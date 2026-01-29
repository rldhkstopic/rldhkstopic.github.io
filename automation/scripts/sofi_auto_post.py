#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoFi 자동 포스팅 Agent (고도화 버전)
거시경제 데이터, 기술적 지표, 이전 분석 맥락을 통합하여 전문가 수준의 분석 글을 생성한다.
"""

import os
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from zoneinfo import ZoneInfo

# .env 파일 지원
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent.parent
    load_dotenv(project_root / ".env")
    load_dotenv(project_root / "local_bot" / ".env")
except ImportError:
    pass

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[ERROR] requests 또는 beautifulsoup4 패키지가 설치되지 않았습니다.")
    print("pip install requests beautifulsoup4 를 실행하세요.")
    exit(1)

try:
    from google import genai
except ImportError:
    print("[ERROR] google-genai 패키지가 설치되지 않았습니다.")
    print("pip install google-genai 를 실행하세요.")
    exit(1)

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    YFINANCE_AVAILABLE = True
except ImportError:
    print("[WARN] yfinance, pandas, numpy가 설치되지 않았습니다. 기술적 지표 수집이 제한됩니다.")
    print("pip install yfinance pandas numpy 를 실행하세요.")
    YFINANCE_AVAILABLE = False

# 환경 설정
PROJECT_ROOT = Path(__file__).parent.parent.parent
STOCK_FEED_PATH = PROJECT_ROOT / "assets" / "data" / "stock_feed.json"
# _posts 디렉터리 사용 (카테고리별 폴더 구조)
POSTS_DIR = PROJECT_ROOT / "_posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)
# 하위 호환성을 위한 이전 경로 (확인용)
POSTS_DIR_FALLBACK = PROJECT_ROOT / "_posts_stock"

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[ERROR] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
    exit(1)


def load_stock_feed() -> Dict:
    """주식 피드 데이터 로드"""
    if not STOCK_FEED_PATH.exists():
        return {"items": []}
    
    with open(STOCK_FEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_sofi_items(items: List[Dict], hours: int = 24) -> List[Dict]:
    """SoFi 관련 최신 아이템 필터링"""
    tz = ZoneInfo("Asia/Seoul")
    cutoff_time = datetime.now(tz) - timedelta(hours=hours)
    
    sofi_items = []
    for item in items:
        if "SOFI" not in item.get("related_tickers", []):
            continue
        
        try:
            item_time = datetime.fromisoformat(item["timestamp"])
            if item_time < cutoff_time:
                continue
        except Exception:
            continue
        
        sofi_items.append(item)
    
    sofi_items.sort(key=lambda x: x["timestamp"], reverse=True)
    return sofi_items


def collect_macro_data() -> Dict:
    """거시경제 데이터 수집 (국채 금리, 나스닥 지수, 경쟁사 주가)"""
    macro_data = {
        "tnx": None,  # 10년물 국채 금리
        "nasdaq_fintech": None,  # 나스닥 핀테크 지수 (대체 지표)
        "competitors": {}  # 경쟁사 주가
    }
    
    if not YFINANCE_AVAILABLE:
        print("[WARN] yfinance 미설치로 거시경제 데이터 수집 건너뜀")
        return macro_data
    
    try:
        # 10년물 국채 금리 (^TNX)
        tnx = yf.Ticker("^TNX")
        tnx_info = tnx.history(period="5d")
        if not tnx_info.empty:
            current_rate = tnx_info['Close'].iloc[-1]
            prev_rate = tnx_info['Close'].iloc[-2] if len(tnx_info) > 1 else current_rate
            change = current_rate - prev_rate
            macro_data["tnx"] = {
                "current": round(current_rate, 2),
                "change": round(change, 2),
                "change_pct": round((change / prev_rate * 100) if prev_rate > 0 else 0, 2)
            }
            print(f"[INFO] 국채 금리: {current_rate:.2f}% (전일 대비 {change:+.2f}%p)")
    except Exception as e:
        print(f"[WARN] 국채 금리 수집 실패: {e}")
    
    try:
        # 나스닥 지수 (대체 지표)
        nasdaq = yf.Ticker("^IXIC")
        nasdaq_info = nasdaq.history(period="5d")
        if not nasdaq_info.empty:
            current = nasdaq_info['Close'].iloc[-1]
            prev = nasdaq_info['Close'].iloc[-2] if len(nasdaq_info) > 1 else current
            change_pct = ((current - prev) / prev * 100) if prev > 0 else 0
            macro_data["nasdaq_fintech"] = {
                "current": round(current, 2),
                "change_pct": round(change_pct, 2)
            }
            print(f"[INFO] 나스닥 지수: {current:.2f} (전일 대비 {change_pct:+.2f}%)")
    except Exception as e:
        print(f"[WARN] 나스닥 지수 수집 실패: {e}")
    
    # 경쟁사 주가 (UPST, AFRM)
    competitors = ["UPST", "AFRM"]
    for ticker in competitors:
        try:
            stock = yf.Ticker(ticker)
            info = stock.history(period="5d")
            if not info.empty:
                current = info['Close'].iloc[-1]
                prev = info['Close'].iloc[-2] if len(info) > 1 else current
                change_pct = ((current - prev) / prev * 100) if prev > 0 else 0
                macro_data["competitors"][ticker] = {
                    "current": round(current, 2),
                    "change_pct": round(change_pct, 2)
                }
                print(f"[INFO] {ticker}: ${current:.2f} (전일 대비 {change_pct:+.2f}%)")
        except Exception as e:
            print(f"[WARN] {ticker} 주가 수집 실패: {e}")
    
    return macro_data


def fetch_technical_data() -> Dict:
    """SoFi 주가의 기술적 지표 수집 (OHLCV, RSI, 이동평균선)"""
    technical_data = {
        "ohlcv": None,
        "rsi": None,
        "moving_averages": {},
        "volume_analysis": None
    }
    
    if not YFINANCE_AVAILABLE:
        print("[WARN] yfinance 미설치로 기술적 지표 수집 건너뜀")
        return technical_data
    
    try:
        sofi = yf.Ticker("SOFI")
        hist = sofi.history(period="60d")  # 60일 데이터로 RSI 계산
        
        if hist.empty:
            return technical_data
        
        # 최근 5일 OHLCV
        recent = hist.tail(5)
        latest = recent.iloc[-1]
        prev = recent.iloc[-2] if len(recent) > 1 else latest
        
        technical_data["ohlcv"] = {
            "open": round(latest['Open'], 2),
            "high": round(latest['High'], 2),
            "low": round(latest['Low'], 2),
            "close": round(latest['Close'], 2),
            "volume": int(latest['Volume']),
            "change": round(latest['Close'] - prev['Close'], 2),
            "change_pct": round(((latest['Close'] - prev['Close']) / prev['Close'] * 100) if prev['Close'] > 0 else 0, 2)
        }
        
        # RSI 계산 (14일 기준)
        if len(hist) >= 14:
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            technical_data["rsi"] = round(current_rsi, 2)
        
        # 이동평균선 (20일, 60일)
        if len(hist) >= 20:
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            technical_data["moving_averages"]["ma20"] = round(ma20, 2)
            technical_data["moving_averages"]["above_ma20"] = latest['Close'] > ma20
        
        if len(hist) >= 60:
            ma60 = hist['Close'].rolling(window=60).mean().iloc[-1]
            technical_data["moving_averages"]["ma60"] = round(ma60, 2)
            technical_data["moving_averages"]["above_ma60"] = latest['Close'] > ma60
        
        # 거래량 분석
        avg_volume = hist['Volume'].tail(20).mean()
        current_volume = latest['Volume']
        volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1
        technical_data["volume_analysis"] = {
            "current": int(current_volume),
            "average_20d": int(avg_volume),
            "ratio": round(volume_ratio, 2)
        }
        
        print(f"[INFO] SoFi 기술적 지표 수집 완료: ${latest['Close']:.2f}, RSI: {technical_data.get('rsi', 'N/A')}")
        
    except Exception as e:
        print(f"[WARN] 기술적 지표 수집 실패: {e}")
    
    return technical_data


def load_previous_summary(date_str: str) -> Optional[str]:
    """이전 날짜의 SoFi 분석 글 요약 로드 (연속성 확보)"""
    tz = ZoneInfo("Asia/Seoul")
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        prev_date = target_date - timedelta(days=1)
        prev_date_str = prev_date.strftime("%Y-%m-%d")
        
        # 이전 날짜의 SoFi 포스트 찾기 (stock 카테고리 폴더에서)
        stock_dir = POSTS_DIR / "stock"
        pattern = f"{prev_date_str}-SOFI-*"
        if stock_dir.exists():
            prev_posts = list(stock_dir.glob(pattern))
        else:
            # 하위 호환성: 루트에서도 확인
            prev_posts = list(POSTS_DIR.glob(pattern))
        
        if not prev_posts:
            return None
        
        # 가장 최근 포스트 읽기
        prev_post = prev_posts[0]
        content = prev_post.read_text(encoding="utf-8")
        
        # Front Matter 제거하고 본문만 추출
        if "---" in content:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()
            else:
                body = content
        else:
            body = content
        
        # Gemini로 요약 생성 (간단한 추출)
        # 실제로는 Gemini API를 호출해서 요약하는 것이 좋지만, 여기서는 간단히 핵심만 추출
        lines = body.split('\n')
        summary_lines = []
        for line in lines[:30]:  # 처음 30줄만
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip()[:200])  # 각 줄 최대 200자
        
        summary = '\n'.join(summary_lines[:10])  # 최대 10줄
        if len(summary) > 1000:
            summary = summary[:1000] + "..."
        
        print(f"[INFO] 이전 분석 로드: {prev_date_str}")
        return summary
        
    except Exception as e:
        print(f"[WARN] 이전 분석 로드 실패: {e}")
        return None


def check_existing_post(date_str: str) -> Optional[Path]:
    """해당 날짜의 SoFi 포스트가 이미 존재하는지 확인 (stock 카테고리 폴더에서)"""
    stock_dir = POSTS_DIR / "stock"
    pattern = f"{date_str}-SOFI-*"
    
    # stock 카테고리 폴더에서 먼저 확인
    if stock_dir.exists():
        existing = list(stock_dir.glob(pattern))
        if existing:
            return existing[0]
    
    # 하위 호환성: 루트에서도 확인
    existing = list(POSTS_DIR.glob(pattern))
    if existing:
        return existing[0]
    
    # 하위 호환성: 이전 경로에서도 확인
    if POSTS_DIR_FALLBACK.exists():
        existing = list(POSTS_DIR_FALLBACK.glob(pattern))
        if existing:
            return existing[0]
    
    return None


def should_update_post(existing_post_path: Path, sofi_items: List[Dict]) -> bool:
    """기존 포스트를 업데이트해야 하는지 판단"""
    if not sofi_items:
        return False  # 새 뉴스가 없으면 업데이트 불필요
    
    # 기존 포스트의 수정 시간 확인
    try:
        post_mtime = datetime.fromtimestamp(existing_post_path.stat().st_mtime, tz=ZoneInfo("Asia/Seoul"))
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        hours_since_update = (now - post_mtime).total_seconds() / 3600
        
        # 2시간 이상 지났거나, 새 뉴스가 많으면 업데이트
        if hours_since_update >= 2 or len(sofi_items) >= 5:
            return True
    except Exception:
        # 파일 정보를 읽을 수 없으면 업데이트
        return True
    
    return False


def clean_html_tags(content: str) -> str:
    """MathJax 및 기타 HTML 태그 제거, 마크다운 서식 정리, 프롬프트 내용 제거"""
    # MathJax 태그 제거 (모든 변형)
    content = re.sub(r'<mjx-container[^>]*>.*?</mjx-container>', '', content, flags=re.DOTALL)
    content = re.sub(r'<mjx-[^>]*>.*?</mjx-[^>]*>', '', content, flags=re.DOTALL)
    content = re.sub(r'<mjx-[^>]*/?>', '', content)
    content = re.sub(r'\$[^$]+\$', '', content)  # LaTeX 수식 제거 ($...$)
    content = re.sub(r'\$\$[^$]+\$\$', '', content)  # LaTeX 수식 제거 ($$...$$)
    
    # 기타 HTML 태그 제거
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 프롬프트 내용 제거 (본문에 포함된 경우)
    content = re.sub(r'당신은.*?작성하세요\.?\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'월스트리트의.*?블로그 포스트를 작성한다?\.?\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'AI로 작성.*?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'자동.*?생성.*?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'이 포스트는.*?생성되었습니다.*?', '', content, flags=re.IGNORECASE | re.DOTALL)
    
    # 마크다운 서식 정리: 헤더 앞에 빈 줄 추가
    content = re.sub(r'([^\n])\n(#{1,6}\s)', r'\1\n\n\2', content)
    
    # 리스트 앞에 빈 줄 추가
    content = re.sub(r'([^\n])\n([-*+]|\d+\.)\s', r'\1\n\n\2', content)
    
    # 연속된 공백 정리 (단, 헤더와 리스트는 유지)
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = re.sub(r'[ \t]+', ' ', content)  # 탭과 연속 공백을 단일 공백으로
    
    # 문단 끝에 줄바꿈 추가 (헤더/리스트가 아닌 경우)
    content = re.sub(r'([^\n])\n([^\n#\-\*\+])', r'\1\n\n\2', content)
    
    # References 섹션 정리: 각주 형식 수정
    # [^n]: 형식을 - [^n]: 형식으로 변경
    content = re.sub(r'^(\[)\^(\d+)\]:', r'- [^\2]:', content, flags=re.MULTILINE)
    
    return content.strip()


def fetch_article_content(url: str, timeout: int = 10) -> Optional[str]:
    """URL에서 실제 기사 내용을 추출 (Seeking Alpha 제외)"""
    # Seeking Alpha는 스캠 글들이 많고 추출도 실패하므로 제외
    if "seekingalpha.com" in url.lower():
        return None
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            tag.decompose()
        
        article_content = None
        selectors = [
            'article', '[class*="article"]', '[class*="content"]', '[class*="post"]',
            '[id*="article"]', '[id*="content"]', 'main', '.entry-content',
            '.article-body', '.post-content'
        ]
        
        for selector in selectors:
            article = soup.select_one(selector)
            if article:
                article_content = article
                break
        
        if not article_content:
            article_content = soup.find('body') or soup
        
        text = article_content.get_text(separator='\n', strip=True)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        if len(text) < 100:
            return None
        
        return text[:5000] if len(text) > 5000 else text
    
    except Exception as e:
        print(f"[WARN] 기사 내용 추출 실패 ({url}): {e}")
        return None


def prepare_news_summary(items: List[Dict]) -> str:
    """뉴스 아이템을 요약 텍스트로 변환 (실제 기사 내용 포함, Seeking Alpha 제외)"""
    # Seeking Alpha 기사 필터링
    filtered_items = [item for item in items if "seekingalpha.com" not in item.get("url", "").lower()]
    summary = f"총 {len(filtered_items)}개의 SOFI 관련 뉴스 (Seeking Alpha 제외: {len(items) - len(filtered_items)}개)\n\n"
    
    for idx, item in enumerate(filtered_items, 1):
        timestamp = item.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            time_str = "N/A"
        
        source = item.get("source_name", "Unknown")
        title = item.get("content", "").strip()
        url = item.get("url", "")
        sentiment = item.get("sentiment", "NEUTRAL")
        
        summary += f"[{idx}] {time_str} | {source} | {sentiment}\n"
        summary += f"제목: {title}\n"
        summary += f"URL: {url}\n"
        
        print(f"[INFO] 기사 내용 추출 중: {url}")
        article_content = fetch_article_content(url)
        
        if article_content:
            summary += f"\n기사 내용:\n{article_content}\n"
        else:
            summary += f"\n(기사 내용 추출 실패 - 제목/요약만 사용)\n"
        
        summary += "\n" + "="*80 + "\n\n"
        time.sleep(1)
    
    return summary


def format_macro_context(macro_data: Dict) -> str:
    """거시경제 데이터를 프롬프트 형식으로 포맷팅"""
    context = "**시장 환경 (Macro Context)**:\n\n"
    
    if macro_data.get("tnx"):
        tnx = macro_data["tnx"]
        context += f"- **미국 10년물 국채 금리 (TNX)**: {tnx['current']}% (전일 대비 {tnx['change']:+.2f}%p, {tnx['change_pct']:+.2f}%)\n"
        if tnx['change'] > 0:
            context += "  → 국채 금리 상승은 핀테크 기업의 대출 마진에 압박을 줄 수 있음.\n"
        elif tnx['change'] < 0:
            context += "  → 국채 금리 하락은 핀테크 기업의 대출 마진 확대에 유리함.\n"
    
    if macro_data.get("nasdaq_fintech"):
        nasdaq = macro_data["nasdaq_fintech"]
        context += f"- **나스닥 지수**: {nasdaq['current']:.2f} (전일 대비 {nasdaq['change_pct']:+.2f}%)\n"
    
    if macro_data.get("competitors"):
        context += "- **경쟁사 주가**:\n"
        for ticker, data in macro_data["competitors"].items():
            context += f"  - {ticker}: ${data['current']:.2f} (전일 대비 {data['change_pct']:+.2f}%)\n"
    
    context += "\n이 맥락에서 SoFi 뉴스를 해석하세요. 개별 호재/악재보다 전체 시장 환경이 SoFi 주가에 미치는 영향을 먼저 고려하세요.\n\n"
    
    return context


def format_technical_context(technical_data: Dict) -> str:
    """기술적 지표를 프롬프트 형식으로 포맷팅"""
    if not technical_data.get("ohlcv"):
        return ""
    
    context = "**기술적 지표 (Technical Data)**:\n\n"
    ohlcv = technical_data["ohlcv"]
    
    context += f"- **가격**: ${ohlcv['close']:.2f} (전일 대비 {ohlcv['change']:+.2f}, {ohlcv['change_pct']:+.2f}%)\n"
    context += f"- **고가/저가**: ${ohlcv['high']:.2f} / ${ohlcv['low']:.2f}\n"
    
    if technical_data.get("rsi"):
        rsi = technical_data["rsi"]
        context += f"- **RSI (14일)**: {rsi:.2f}"
        if rsi > 70:
            context += " (과매수 구간 - 조정 가능성)\n"
        elif rsi < 30:
            context += " (과매도 구간 - 반등 가능성)\n"
        else:
            context += " (중립 구간)\n"
    
    if technical_data.get("moving_averages"):
        ma = technical_data["moving_averages"]
        if "ma20" in ma:
            above = "위" if ma.get("above_ma20") else "아래"
            context += f"- **20일 이동평균**: ${ma['ma20']:.2f} (현재가 {above})\n"
        if "ma60" in ma:
            above = "위" if ma.get("above_ma60") else "아래"
            context += f"- **60일 이동평균**: ${ma['ma60']:.2f} (현재가 {above})\n"
    
    if technical_data.get("volume_analysis"):
        vol = technical_data["volume_analysis"]
        context += f"- **거래량**: {vol['current']:,}주 (20일 평균 대비 {vol['ratio']:.2f}배)\n"
        if vol['ratio'] > 1.5:
            context += "  → 거래량 급증은 큰 움직임의 신호일 수 있음.\n"
    
    context += "\n이 기술적 데이터와 뉴스를 결합하여 분석하세요. 예: RSI가 70을 넘은 상태에서 호재 뉴스가 나왔으면 '뉴스에 팔기(Sell the news)' 심리가 작용할 수 있음.\n\n"
    
    return context


def get_deep_dive_prompt(date_str: str, macro_data: Dict, technical_data: Dict) -> str:
    """뉴스가 부족할 때 사용하는 Deep Dive 모드 프롬프트"""
    return f"""당신은 월스트리트의 20년 차 핀테크 전문 헤지펀드 매니저입니다.

**날짜**: {date_str}

**상황**: 오늘 SoFi 관련 주요 뉴스가 거의 없습니다. 이 경우 단순히 뉴스를 요약하는 것이 아니라, SoFi의 펀더멘털이나 특정 주제에 대한 심층 분석을 제공하세요.

{format_macro_context(macro_data) if macro_data.get("tnx") or macro_data.get("competitors") else ""}

{format_technical_context(technical_data) if technical_data.get("ohlcv") else ""}

**작성 규칙**:
1. SoFi의 핵심 비즈니스 모델, 기술력(Galileo 플랫폼), 뱅킹 라이선스의 의미 등에 대해 교육적으로 설명하세요.
2. 최근 재무제표의 특정 항목이나 트렌드를 분석하세요.
3. 현재 시장 환경에서 SoFi가 직면한 기회와 리스크를 분석하세요.
4. 모든 문장은 "~다."로 끝나는 건조한 평서문을 사용하세요.
5. 최소 2000자 이상 작성하세요.

**구조**:
### 핵심 주제 (1개 선택)
- SoFi의 특정 비즈니스 영역이나 기술력에 대한 심층 분석

### 펀더멘털 분석
- 선택한 주제가 SoFi의 장기 가치에 미치는 영향
- 재무 지표와의 연관성

### 시장 환경과의 연관성
- 현재 거시경제 환경에서의 의미
- 기술적 지표와의 연관성

### 투자자 관점
- Bull Case (상승 시나리오)
- Bear Case (하락 시나리오)

**⚠️ 중요**: Front Matter 없이 본문만 작성하세요. 제목(###)부터 시작하세요."""


def generate_post_with_gemini(items: List[Dict], date_str: str, macro_data: Dict, technical_data: Dict, previous_summary: Optional[str]) -> Optional[str]:
    """Gemini API를 사용하여 포스트 생성 (고도화 버전)"""
    
    # 뉴스 개수에 따라 모드 결정
    if len(items) < 2:
        print("[INFO] 뉴스가 부족하여 Deep Dive 모드로 전환")
        mode = "deep_dive"
        news_summary = ""
    else:
        mode = "daily_news"
        news_summary = prepare_news_summary(items)
    
    client = genai.Client(api_key=GEMINI_API_KEY)
    # 모델 폴백 체인 (사용 가능한 모델 순서대로 시도)
    model_candidates = [
        "models/gemini-2.5-flash",
        "models/gemini-2.0-flash",
        "models/gemini-flash-latest",
    ]
    
    if mode == "deep_dive":
        prompt = get_deep_dive_prompt(date_str, macro_data, technical_data)
    else:
        # Daily News 모드 - 고도화된 프롬프트
        # f-string 내부에서 백슬래시 사용을 피하기 위해 먼저 변수에 저장
        macro_context = format_macro_context(macro_data) if (macro_data.get("tnx") or macro_data.get("competitors")) else ""
        technical_context = format_technical_context(technical_data) if technical_data.get("ohlcv") else ""
        previous_context = ""
        if previous_summary:
            previous_context = f"**이전 분석 맥락 (어제)**:\n{previous_summary}\n\n이전 전망과 비교하여 뷰를 수정하거나 강화하세요. 연속성을 유지하면서 오늘의 새로운 정보를 반영하세요.\n\n"
        
        prompt = f"""당신은 월스트리트의 20년 차 핀테크 전문 헤지펀드 매니저입니다.
아래 SoFi(SOFI) 관련 최신 뉴스들의 **실제 기사 내용**을 분석하여 투자자들이 이해하기 쉬운 블로그 포스트를 작성하세요.

**⚠️ 절대 금지 사항**:
- 프롬프트 내용을 본문에 포함하지 마세요
- "AI로 작성되었습니다", "자동 생성" 같은 메타 정보를 본문에 포함하지 마세요
- "당신은...", "작성하세요" 같은 지시문을 본문에 포함하지 마세요
- 본문은 바로 제목(###)부터 시작하세요

**날짜**: {date_str}

{macro_context}

{technical_context}

{previous_context}

**수집된 뉴스 (제목, URL, 실제 기사 내용 포함)**:
{news_summary}

**작성 규칙**:
1. **기사 내용 분석**: 각 뉴스의 제목과 URL만이 아니라, 제공된 **실제 기사 내용**을 읽고 분석하여 작성한다.
2. 모든 문장은 "~다."로 끝나는 건조한 평서문을 사용한다.
3. 단순히 뉴스를 요약하지 말고, 다음 3가지 관점에서 분석한다:
   - **Fundamental (펀더멘털)**: 이 뉴스가 SoFi의 EPS(주당순이익), 가이던스, 장기 성장성에 어떤 영향을 주는가?
   - **Sentiment (심리)**: 레딧(Reddit)의 반응과 뉴스 톤을 볼 때 개미 투자자들의 심리는 탐욕인가 공포인가?
   - **Policy/Risk (정세/리스크)**: 현재 정책 환경(트럼프 행정부 등)과 이 뉴스는 상충하는가, 부합하는가?
4. 거시경제 데이터와 기술적 지표를 뉴스와 결합하여 분석한다.
5. 이모지는 사용하지 않는다.
6. 최소 2000자 이상 작성한다.
7. 출처는 각주 형식 [^n]으로 표기하고, 마지막에 ## References 섹션에 정리한다.
8. **MathJax/LaTeX 수식 사용 금지**: 수식이나 수학 표현은 절대 사용하지 않는다. 모든 숫자와 퍼센트는 일반 텍스트로 작성한다 (예: "32.9%", "$24.60", "70.95배").
9. **마크다운 서식 필수**: 
   - 헤더는 ### 또는 ####를 사용하고, 헤더 앞뒤에 빈 줄을 반드시 추가한다.
   - 리스트는 `-` 또는 `*`를 사용하고, 리스트 앞뒤에 빈 줄을 추가한다.
   - 문단 사이에는 반드시 빈 줄을 하나 추가한다.
   - 숫자나 통계는 **굵게** 처리하여 강조한다.

**구조**:
### 주요 뉴스 요약
- 3~5개 핵심 주제를 간단히 요약 (기사 내용 기반)

### 상세 분석
각 주제별로:
- 기사에서 언급된 구체적인 사실과 데이터
- Fundamental 관점: EPS/가이던스 영향
- Sentiment 관점: 시장 심리 분석
- Policy/Risk 관점: 정책 환경과의 부합 여부
- 기술적 지표와의 연관성 (RSI, 거래량 등)

### 투자 시나리오
**Bull Case (상승 시나리오)**:
- 이 뉴스들이 긍정적으로 전개될 경우의 시나리오
- 목표가 및 상승 근거

**Bear Case (하락 시나리오)**:
- 이 뉴스들이 부정적으로 전개될 경우의 시나리오
- 하락 리스크 및 지지선

### 종합 의견
- 전반적인 시장 분위기
- 주목할 포인트
- 투자자 행동 가이드

## References
- [^1]: [출처](URL)
- [^2]: [출처](URL)

**⚠️ 중요**: 
- Front Matter 없이 본문만 작성하세요. 제목(###)부터 시작하세요.
- 링크만 나열하지 말고, 실제 기사 내용을 읽고 분석한 내용을 작성하세요.
- 반드시 Bull Case와 Bear Case를 나누어 작성하세요.
- 프롬프트의 지시문이나 설명을 본문에 포함하지 마세요. 순수한 분석 내용만 작성하세요.
- 각주는 [^1], [^2] 형식으로 사용하고, References 섹션에는 `- [^1]: [출처명](URL)` 형식으로 작성하세요."""

    # 모델 폴백: 첫 번째 모델이 실패하면 다음 모델 시도
    content = None
    last_error = None
    
    for model_name in model_candidates:
        try:
            print(f"[INFO] Gemini API로 글 작성 중... (모드: {mode}, 모델: {model_name})")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            
            content = (response.text or "").strip()
            
            if not content or len(content) < 100:
                print(f"[WARN] Gemini 응답이 너무 짧습니다: {len(content)}자")
                if model_name != model_candidates[-1]:
                    print(f"[INFO] 다음 모델 시도: {model_candidates[model_candidates.index(model_name) + 1]}")
                    continue
                else:
                    print(f"[ERROR] 모든 모델에서 응답이 너무 짧습니다")
                    return None
            
            # 성공하면 루프 종료
            print(f"[OK] 모델 {model_name}로 포스트 생성 성공")
            break
            
        except Exception as e:
            last_error = e
            print(f"[WARN] 모델 {model_name} 실패: {e}")
            if model_name != model_candidates[-1]:
                print(f"[INFO] 다음 모델 시도: {model_candidates[model_candidates.index(model_name) + 1]}")
                continue
            else:
                # 모든 모델 실패
                print(f"[ERROR] 모든 모델 시도 실패: {last_error}")
                return None
    
    # 최종 검증
    if not content or len(content) < 100:
        print(f"[ERROR] Gemini 응답이 비어있거나 너무 짧습니다: {len(content) if content else 0}자")
        return None
    
    # MathJax 태그 및 기타 HTML 태그 제거 (서식 깨짐 방지)
    content = clean_html_tags(content)
    
    # Front Matter 생성
    tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(tz)
    title = f"[{date_str}] SOFI 소식 분석"
    
    front_matter = f"""---
layout: post
title: "{title}"
date: {now.strftime('%Y-%m-%d %H:%M:%S')} +0900
author: rldhkstopic
category: stock
tags: ["SOFI", "주식", "투자", "분석"]
views: 0
---

"""
    
    footer = f"\n\n---\n\n*이 포스트는 AI가 분석하여 자동으로 생성되었습니다. (생성 시간: {now.strftime('%Y-%m-%d %H:%M:%S KST')})*\n"
    
    return front_matter + content + footer


def main():
    """메인 함수"""
    print("[INFO] SoFi 자동 포스팅 시작 (고도화 버전)...")
    
    tz = ZoneInfo("Asia/Seoul")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    
    # 1. 오늘 날짜 포스트가 이미 존재하는지 확인
    existing_post = check_existing_post(today)
    
    # 2. 주식 피드 로드 (업데이트 여부 판단을 위해 먼저 로드)
    feed_data = load_stock_feed()
    items = feed_data.get("items", [])
    print(f"[INFO] 전체 피드 아이템: {len(items)}개")
    
    # 3. SoFi 관련 최신 아이템 필터링 (최근 24시간)
    sofi_items = filter_sofi_items(items, hours=24)
    print(f"[INFO] SoFi 관련 최신 아이템: {len(sofi_items)}개")
    
    # 4. 기존 포스트가 있으면 업데이트 여부 판단
    if existing_post:
        print(f"[INFO] {today} SOFI 포스트가 이미 존재합니다: {existing_post.name}")
        if should_update_post(existing_post, sofi_items):
            print(f"[INFO] 새 뉴스가 있거나 시간이 지나서 포스트를 업데이트합니다.")
            # 기존 파일 삭제 (덮어쓰기)
            existing_post.unlink()
            print(f"[INFO] 기존 포스트 삭제 완료")
        else:
            print(f"[INFO] 업데이트 불필요 (새 뉴스 부족 또는 최근 업데이트됨). 스킵.")
            return
    
    # 2. 주식 피드 로드
    feed_data = load_stock_feed()
    items = feed_data.get("items", [])
    print(f"[INFO] 전체 피드 아이템: {len(items)}개")
    
    # 3. SoFi 관련 최신 아이템 필터링 (최근 24시간)
    sofi_items = filter_sofi_items(items, hours=24)
    print(f"[INFO] SoFi 관련 최신 아이템: {len(sofi_items)}개")
    
    # 4. 거시경제 데이터 수집
    print("[INFO] 거시경제 데이터 수집 중...")
    macro_data = collect_macro_data()
    
    # 6. 기술적 지표 수집
    print("[INFO] 기술적 지표 수집 중...")
    technical_data = fetch_technical_data()
    
    # 7. 이전 분석 로드 (연속성)
    print("[INFO] 이전 분석 맥락 로드 중...")
    previous_summary = load_previous_summary(today)
    
    # 8. 뉴스가 없어도 Deep Dive 모드로 진행
    if not sofi_items:
        print("[INFO] 새로운 SoFi 뉴스가 없습니다. Deep Dive 모드로 진행합니다.")
    else:
        print(f"[INFO] {len(sofi_items)}개의 SoFi 뉴스를 발견했습니다. Daily News 모드로 진행합니다.")
    
    # 9. Gemini로 포스트 생성
    print("[INFO] Gemini API로 포스트 생성 시작...")
    content = generate_post_with_gemini(sofi_items, today, macro_data, technical_data, previous_summary)
    if not content:
        print("[ERROR] 포스트 생성 실패")
        return
    
    # 10. 파일 저장 (stock 카테고리 폴더에 저장)
    stock_dir = POSTS_DIR / "stock"
    stock_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{today}-SOFI-소식-분석.md"
    filepath = stock_dir / filename
    
    filepath.write_text(content, encoding="utf-8")
    print(f"[OK] 포스트 생성 완료: {filename}")
    print(f"[OK] 경로: {filepath}")
    print(f"[OK] 글 길이: {len(content)}자")


if __name__ == "__main__":
    main()
