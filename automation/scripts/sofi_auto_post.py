#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoFi 자동 포스팅 Agent
stock_feed.json에서 SoFi 관련 최신 뉴스를 수집하여 Gemini API로 분석 후 블로그 포스트를 자동 생성한다.
"""

import os
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from zoneinfo import ZoneInfo

# .env 파일 지원
try:
    from dotenv import load_dotenv
    # 프로젝트 루트와 local_bot 디렉토리에서 .env 파일 찾기
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
    from google.genai import types
except ImportError:
    print("[ERROR] google-genai 패키지가 설치되지 않았습니다.")
    print("pip install google-genai 를 실행하세요.")
    exit(1)

# 환경 설정
PROJECT_ROOT = Path(__file__).parent.parent.parent
STOCK_FEED_PATH = PROJECT_ROOT / "assets" / "data" / "stock_feed.json"
POSTS_DIR = PROJECT_ROOT / "_posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

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
        # SoFi 관련 아이템만
        if "SOFI" not in item.get("related_tickers", []):
            continue
        
        # 최근 N시간 이내 아이템만
        try:
            item_time = datetime.fromisoformat(item["timestamp"])
            if item_time < cutoff_time:
                continue
        except Exception:
            continue
        
        sofi_items.append(item)
    
    # 최신순 정렬
    sofi_items.sort(key=lambda x: x["timestamp"], reverse=True)
    return sofi_items


def check_existing_post(date_str: str) -> bool:
    """해당 날짜의 SoFi 포스트가 이미 존재하는지 확인"""
    pattern = f"{date_str}-SOFI-*"
    existing = list(POSTS_DIR.glob(pattern))
    return len(existing) > 0


def create_slug(title: str) -> str:
    """제목을 슬러그로 변환"""
    import re
    slug = re.sub(r'[^\w\s가-힣-]', '', title)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def fetch_article_content(url: str, timeout: int = 10) -> Optional[str]:
    """URL에서 실제 기사 내용을 추출"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            tag.decompose()
        
        # 기사 본문 추출 (일반적인 기사 사이트 구조)
        article_content = None
        
        # 다양한 기사 본문 선택자 시도
        selectors = [
            'article',
            '[class*="article"]',
            '[class*="content"]',
            '[class*="post"]',
            '[id*="article"]',
            '[id*="content"]',
            'main',
            '.entry-content',
            '.article-body',
            '.post-content'
        ]
        
        for selector in selectors:
            article = soup.select_one(selector)
            if article:
                article_content = article
                break
        
        # 선택자가 없으면 body 전체 사용
        if not article_content:
            article_content = soup.find('body') or soup
        
        # 텍스트 추출 및 정리
        text = article_content.get_text(separator='\n', strip=True)
        # 연속된 공백/줄바꿈 정리
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # 너무 짧으면 실패로 간주
        if len(text) < 100:
            return None
        
        # 최대 5000자로 제한
        return text[:5000] if len(text) > 5000 else text
    
    except Exception as e:
        print(f"[WARN] 기사 내용 추출 실패 ({url}): {e}")
        return None


def prepare_news_summary(items: List[Dict]) -> str:
    """뉴스 아이템을 요약 텍스트로 변환 (실제 기사 내용 포함)"""
    summary = f"총 {len(items)}개의 SOFI 관련 뉴스\n\n"
    
    for idx, item in enumerate(items, 1):
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
        
        # 실제 기사 내용 가져오기
        print(f"[INFO] 기사 내용 추출 중: {url}")
        article_content = fetch_article_content(url)
        
        if article_content:
            summary += f"\n기사 내용:\n{article_content}\n"
        else:
            # 기사 내용을 가져오지 못한 경우 원본 요약만 사용
            summary += f"\n(기사 내용 추출 실패 - 제목/요약만 사용)\n"
        
        summary += "\n" + "="*80 + "\n\n"
        
        # API 호출 제한을 위한 딜레이
        time.sleep(1)
    
    return summary


def generate_post_with_gemini(items: List[Dict], date_str: str) -> Optional[str]:
    """Gemini API를 사용하여 포스트 생성"""
    if not items:
        return None
    
    # 뉴스 요약 준비
    news_summary = prepare_news_summary(items)
    
    # Gemini 클라이언트 초기화
    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.0-flash-exp"
    
    # 프롬프트 작성
    prompt = f"""당신은 주식 투자 분석가이자 테크니컬 라이터입니다.
아래 SoFi(SOFI) 관련 최신 뉴스들의 **실제 기사 내용**을 분석하여 투자자들이 이해하기 쉬운 블로그 포스트를 작성하세요.

**날짜**: {date_str}

**수집된 뉴스 (제목, URL, 실제 기사 내용 포함)**:
{news_summary}

**작성 규칙**:
1. **기사 내용 분석**: 각 뉴스의 제목과 URL만이 아니라, 제공된 **실제 기사 내용**을 읽고 분석하여 작성한다.
2. 모든 문장은 "~다."로 끝나는 건조한 평서문을 사용한다.
3. 뉴스를 주제별로 그룹화하여 분석한다 (예: 실적, 제품, 규제, 시장 반응 등).
4. 각 주제마다 기사에서 언급된 **구체적인 사실과 데이터**를 인용하고, 그 의미와 투자자 관점을 간결하게 서술한다.
5. 단순히 링크를 나열하는 것이 아니라, 기사 내용을 읽고 **요약 및 분석**한 내용을 작성한다.
6. 이모지는 사용하지 않는다.
7. 최소 1500자 이상 작성한다.
8. 출처는 각주 형식 [^n]으로 표기하고, 마지막에 ## References 섹션에 정리한다.

**구조**:
### 주요 뉴스 요약
- 3~5개 핵심 주제를 간단히 요약 (기사 내용 기반)

### 상세 분석
각 주제별로:
- 기사에서 언급된 구체적인 사실과 데이터
- 왜 중요한가
- 투자자 관점

### 주가 추세 분석
- 최근 SoFi 주가 동향 (가능한 경우)
- 뉴스가 주가에 미칠 수 있는 영향
- 기술적 분석 (지지선/저항선 등, 데이터가 있는 경우)

### 종합 의견
- 전반적인 시장 분위기
- 주목할 포인트

## References
- [^1]: [출처](URL)
- [^2]: [출처](URL)

**⚠️ 중요**: 
- Front Matter 없이 본문만 작성하세요. 제목(###)부터 시작하세요.
- 링크만 나열하지 말고, 실제 기사 내용을 읽고 분석한 내용을 작성하세요."""

    try:
        print("[INFO] Gemini API로 글 작성 중...")
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        
        content = (response.text or "").strip()
        
        if not content or len(content) < 100:
            print(f"[ERROR] Gemini 응답이 너무 짧습니다: {len(content)}자")
            return None
        
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
        
        # Footer 추가
        footer = f"\n\n---\n\n*이 포스트는 AI가 분석하여 자동으로 생성되었습니다. (생성 시간: {now.strftime('%Y-%m-%d %H:%M:%S KST')})*\n"
        
        return front_matter + content + footer
    
    except Exception as e:
        print(f"[ERROR] Gemini API 호출 실패: {e}")
        return None


def main():
    """메인 함수"""
    print("[INFO] SoFi 자동 포스팅 시작...")
    
    # 1. 주식 피드 로드
    feed_data = load_stock_feed()
    items = feed_data.get("items", [])
    print(f"[INFO] 전체 피드 아이템: {len(items)}개")
    
    # 2. SoFi 관련 최신 아이템 필터링 (최근 24시간)
    sofi_items = filter_sofi_items(items, hours=24)
    print(f"[INFO] SoFi 관련 최신 아이템: {len(sofi_items)}개")
    
    if not sofi_items:
        print("[INFO] 새로운 SoFi 뉴스가 없습니다.")
        return
    
    # 3. 오늘 날짜 포스트가 이미 존재하는지 확인
    tz = ZoneInfo("Asia/Seoul")
    today = datetime.now(tz).strftime("%Y-%m-%d")
    
    if check_existing_post(today):
        print(f"[INFO] {today} SOFI 포스트가 이미 존재합니다. 스킵.")
        return
    
    # 4. Gemini로 포스트 생성
    content = generate_post_with_gemini(sofi_items, today)
    if not content:
        print("[WARN] 포스트 생성 실패")
        return
    
    # 5. 파일 저장
    filename = f"{today}-SOFI-소식-분석.md"
    filepath = POSTS_DIR / filename
    
    filepath.write_text(content, encoding="utf-8")
    print(f"[OK] 포스트 생성 완료: {filename}")
    print(f"[OK] 경로: {filepath}")
    print(f"[OK] 글 길이: {len(content)}자")


if __name__ == "__main__":
    main()
