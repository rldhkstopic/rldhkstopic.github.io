#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
주식 뉴스 피드 수집 Agent
RSS 피드와 SNS 소스에서 뉴스를 수집하여 stock_feed.json을 업데이트한다.
"""

import os
import json
import hashlib
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
from pathlib import Path

# 환경 변수
ECONOMIC_NEWS_RSS_FEEDS = os.getenv("ECONOMIC_NEWS_RSS_FEEDS", "").strip()
STOCK_FEED_JSON_PATH = Path("assets/data/stock_feed.json")
MAX_ITEMS = 200

# 기본 RSS 피드
DEFAULT_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://feeds.bloomberg.com/technology/news.rss",
    "https://feeds.bloomberg.com/politics/news.rss",
]

# 관심 종목 티커 (한국: 6자리, 미국: 대문자)
WATCHLIST_TICKERS = ["SOFI"]


def generate_item_id(url: str, timestamp: str) -> str:
    """URL과 타임스탬프로 고유 ID 생성"""
    content = f"{url}|{timestamp}"
    return hashlib.md5(content.encode()).hexdigest()


def extract_tickers(text: str) -> List[str]:
    """텍스트에서 티커 추출 (간단한 패턴 매칭)"""
    found = []
    text_upper = text.upper()
    
    for ticker in WATCHLIST_TICKERS:
        if ticker in text_upper:
            found.append(ticker)
    
    return found


def categorize_item(item: Dict) -> str:
    """아이템 카테고리 결정"""
    tickers = item.get("related_tickers", [])
    if tickers:
        return "WATCHLIST"
    
    content_lower = item.get("content", "").lower()
    if any(keyword in content_lower for keyword in ["긴급", "속보", "중요", "breaking"]):
        return "MAJOR"
    
    return "MARKET"


def determine_sentiment(content: str) -> Optional[str]:
    """간단한 감정 분석 (키워드 기반)"""
    content_lower = content.lower()
    
    positive_keywords = ["상승", "증가", "성장", "긍정", "호재", "상향", "개선"]
    negative_keywords = ["하락", "감소", "부정", "악재", "하향", "악화", "우려"]
    
    pos_count = sum(1 for kw in positive_keywords if kw in content_lower)
    neg_count = sum(1 for kw in negative_keywords if kw in content_lower)
    
    if pos_count > neg_count:
        return "POSITIVE"
    elif neg_count > pos_count:
        return "NEGATIVE"
    else:
        return "NEUTRAL"


def collect_rss_news() -> List[Dict]:
    """RSS 피드에서 뉴스 수집"""
    feed_urls = DEFAULT_FEEDS
    if ECONOMIC_NEWS_RSS_FEEDS:
        feed_urls = [u.strip() for u in ECONOMIC_NEWS_RSS_FEEDS.split(",") if u.strip()]
    
    all_items = []
    tz = ZoneInfo("Asia/Seoul")
    cutoff_time = datetime.now(tz) - timedelta(hours=24)
    
    for url in feed_urls:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            
            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if channel is None:
                continue
            
            for item in channel.findall("item"):
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                desc_el = item.find("description")
                
                title = (title_el.text or "").strip() if title_el is not None else ""
                link = (link_el.text or "").strip() if link_el is not None else ""
                pub = (pub_el.text or "").strip() if pub_el is not None else ""
                desc = (desc_el.text or "").strip() if desc_el is not None else ""
                
                if not title or not link:
                    continue
                
                # 시간 파싱
                try:
                    dt = parsedate_to_datetime(pub)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                    dt_kst = dt.astimezone(tz)
                    
                    if dt_kst < cutoff_time:
                        continue
                except Exception:
                    continue
                
                # 출처 추출
                source_name = "Bloomberg"
                if "bloomberg" in url.lower():
                    source_name = "Bloomberg"
                elif "hankyung" in url.lower():
                    source_name = "한국경제"
                elif "mk" in url.lower() or "매경" in url.lower():
                    source_name = "매일경제"
                
                # 티커 추출
                related_tickers = extract_tickers(title + " " + desc)
                
                # 아이템 생성
                feed_item = {
                    "id": generate_item_id(link, dt_kst.isoformat()),
                    "timestamp": dt_kst.isoformat(),
                    "source_type": "NEWS",
                    "source_name": source_name,
                    "category": "MARKET",  # 나중에 categorize_item로 업데이트
                    "related_tickers": related_tickers,
                    "content": title + (" - " + desc[:200] if desc else ""),
                    "url": link,
                    "sentiment": None,
                }
                
                feed_item["category"] = categorize_item(feed_item)
                feed_item["sentiment"] = determine_sentiment(feed_item["content"])
                
                all_items.append(feed_item)
        
        except Exception as e:
            print(f"[WARN] RSS 수집 실패 ({url}): {e}")
            continue
    
    return all_items


def collect_reddit_posts() -> List[Dict]:
    """Reddit에서 주식 관련 게시물 수집 (간단한 웹 스크래핑)"""
    # Reddit RSS 피드 사용 (공개 API)
    reddit_feeds = [
        "https://www.reddit.com/r/stocks/hot/.rss",
        "https://www.reddit.com/r/investing/hot/.rss",
        "https://www.reddit.com/r/koreastock/hot/.rss",
    ]
    
    all_items = []
    tz = ZoneInfo("Asia/Seoul")
    cutoff_time = datetime.now(tz) - timedelta(hours=24)
    
    for url in reddit_feeds:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; StockFeedBot/1.0)"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if channel is None:
                continue
            
            for item in channel.findall("item"):
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("published") or item.find("pubDate")
                desc_el = item.find("description")
                
                title = (title_el.text or "").strip() if title_el is not None else ""
                link = (link_el.text or "").strip() if link_el is not None else ""
                pub = (pub_el.text or "").strip() if pub_el is not None else ""
                desc = (desc_el.text or "").strip() if desc_el is not None else ""
                
                if not title or not link:
                    continue
                
                # 시간 파싱
                try:
                    dt = parsedate_to_datetime(pub)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                    dt_kst = dt.astimezone(tz)
                    
                    if dt_kst < cutoff_time:
                        continue
                except Exception:
                    continue
                
                # 티커 추출
                related_tickers = extract_tickers(title + " " + desc)
                
                # 아이템 생성
                feed_item = {
                    "id": generate_item_id(link, dt_kst.isoformat()),
                    "timestamp": dt_kst.isoformat(),
                    "source_type": "SNS",
                    "source_name": "Reddit",
                    "category": "MARKET",
                    "related_tickers": related_tickers,
                    "content": title + (" - " + desc[:200] if desc else ""),
                    "url": link,
                    "sentiment": None,
                }
                
                feed_item["category"] = categorize_item(feed_item)
                feed_item["sentiment"] = determine_sentiment(feed_item["content"])
                
                all_items.append(feed_item)
        
        except Exception as e:
            print(f"[WARN] Reddit 수집 실패 ({url}): {e}")
            continue
    
    return all_items


def collect_sofi_specific_sources() -> List[Dict]:
    """SoFi 전용 소스에서 콘텐츠 수집 (Seeking Alpha 제외)"""
    all_items = []
    tz = ZoneInfo("Asia/Seoul")
    cutoff_time = datetime.now(tz) - timedelta(hours=24)
    
    # Seeking Alpha는 스캠 글들이 많고 추출도 실패하므로 제외
    
    # 1. Yahoo Finance - SoFi 뉴스
    yahoo_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=SOFI&region=US&lang=en-US"
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; StockFeedBot/1.0)"}
        resp = requests.get(yahoo_url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        root = ET.fromstring(resp.content)
        channel = root.find("channel")
        
        if channel is not None:
            for item in channel.findall("item")[:20]:
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                desc_el = item.find("description")
                
                title = (title_el.text or "").strip() if title_el is not None else ""
                link = (link_el.text or "").strip() if link_el is not None else ""
                pub = (pub_el.text or "").strip() if pub_el is not None else ""
                desc = (desc_el.text or "").strip() if desc_el is not None else ""
                
                if not title or not link:
                    continue
                
                try:
                    dt = parsedate_to_datetime(pub)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                    dt_kst = dt.astimezone(tz)
                    
                    if dt_kst < cutoff_time:
                        continue
                except Exception:
                    dt_kst = datetime.now(tz)
                
                feed_item = {
                    "id": generate_item_id(link, dt_kst.isoformat()),
                    "timestamp": dt_kst.isoformat(),
                    "source_type": "NEWS",
                    "source_name": "Yahoo Finance",
                    "category": "WATCHLIST",
                    "related_tickers": ["SOFI"],
                    "content": title + (" - " + desc[:200] if desc else ""),
                    "url": link,
                    "sentiment": determine_sentiment(title + " " + desc),
                }
                
                all_items.append(feed_item)
    
    except Exception as e:
        print(f"[WARN] Yahoo Finance 수집 실패: {e}")
    
    # 3. Reddit - SoFi 전용 서브레딧
    sofi_reddit_feeds = [
        "https://www.reddit.com/r/sofistock/hot/.rss",
        "https://www.reddit.com/r/sofi/hot/.rss",
    ]
    
    for url in sofi_reddit_feeds:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; StockFeedBot/1.0)"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            
            root = ET.fromstring(resp.content)
            channel = root.find("channel")
            if channel is None:
                continue
            
            for item in channel.findall("item")[:15]:
                title_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("published") or item.find("pubDate")
                desc_el = item.find("description")
                
                title = (title_el.text or "").strip() if title_el is not None else ""
                link = (link_el.text or "").strip() if link_el is not None else ""
                pub = (pub_el.text or "").strip() if pub_el is not None else ""
                desc = (desc_el.text or "").strip() if desc_el is not None else ""
                
                if not title or not link:
                    continue
                
                try:
                    dt = parsedate_to_datetime(pub)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                    dt_kst = dt.astimezone(tz)
                    
                    if dt_kst < cutoff_time:
                        continue
                except Exception:
                    continue
                
                feed_item = {
                    "id": generate_item_id(link, dt_kst.isoformat()),
                    "timestamp": dt_kst.isoformat(),
                    "source_type": "SNS",
                    "source_name": "Reddit",
                    "category": "WATCHLIST",
                    "related_tickers": ["SOFI"],
                    "content": title + (" - " + desc[:200] if desc else ""),
                    "url": link,
                    "sentiment": determine_sentiment(title + " " + desc),
                }
                
                all_items.append(feed_item)
        
        except Exception as e:
            print(f"[WARN] Reddit SoFi 수집 실패 ({url}): {e}")
            continue
    
    return all_items


def load_existing_feed() -> List[Dict]:
    """기존 stock_feed.json 로드"""
    if not STOCK_FEED_JSON_PATH.exists():
        return []
    
    try:
        with open(STOCK_FEED_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("items", [])
    except Exception as e:
        print(f"[WARN] 기존 피드 로드 실패: {e}")
        return []


def merge_items(existing: List[Dict], new_items: List[Dict]) -> List[Dict]:
    """기존 아이템과 새 아이템 병합 (중복 제거)"""
    existing_ids: Set[str] = {item["id"] for item in existing}
    
    # 새 아이템 중 중복 제거
    unique_new = [item for item in new_items if item["id"] not in existing_ids]
    
    # 병합 및 정렬 (최신순)
    all_items = existing + unique_new
    all_items.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # 상위 200개만 유지
    return all_items[:MAX_ITEMS]


def save_feed(items: List[Dict]):
    """stock_feed.json 저장"""
    tz = ZoneInfo("Asia/Seoul")
    data = {
        "last_updated": datetime.now(tz).isoformat(),
        "items": items,
    }
    
    # 디렉토리 생성
    STOCK_FEED_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(STOCK_FEED_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] {len(items)}개 아이템 저장 완료: {STOCK_FEED_JSON_PATH}")


def send_sofi_discord_notification(webhook_url: str, items: List[Dict]) -> int:
    """SOFI 관련 새 뉴스를 Discord로 전송"""
    if not webhook_url:
        return 0
    
    import requests
    from datetime import datetime
    
    sent_count = 0
    
    for item in items:
        # SOFI 관련 아이템만 필터링
        tickers = item.get("related_tickers", [])
        if "SOFI" not in tickers:
            continue
        
        # Discord Embed 생성
        embed = {
            "title": f"📰 SOFI 소식: {item.get('content', '')[:100]}",
            "description": item.get("content", "")[:500],
            "color": 0x00FF00 if item.get("sentiment") == "POSITIVE" else (0xFF0000 if item.get("sentiment") == "NEGATIVE" else 0x5865F2),
            "timestamp": item.get("timestamp", datetime.utcnow().isoformat()),
            "fields": [
                {
                    "name": "출처",
                    "value": f"{item.get('source_name', 'Unknown')} ({item.get('source_type', 'NEWS')})",
                    "inline": True,
                },
                {
                    "name": "카테고리",
                    "value": item.get("category", "MARKET"),
                    "inline": True,
                },
            ],
        }
        
        if item.get("sentiment"):
            embed["fields"].append({
                "name": "감정 분석",
                "value": item.get("sentiment", "NEUTRAL"),
                "inline": True,
            })
        
        if item.get("url"):
            embed["url"] = item["url"]
        
        embed["footer"] = {"text": "Stock Feed Agent"}
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(webhook_url.strip().strip('"').strip("'"), json=payload, timeout=10)
            response.raise_for_status()
            sent_count += 1
            print(f"[OK] Discord 알림 전송: {item.get('content', '')[:50]}...")
        except Exception as e:
            print(f"[WARN] Discord 알림 전송 실패: {e}")
    
    return sent_count


def main():
    """메인 함수"""
    import os
    
    print("[INFO] 주식 뉴스 피드 수집 시작...")
    
    # 1. 기존 데이터 로드
    existing_items = load_existing_feed()
    existing_ids = {item["id"] for item in existing_items}
    print(f"[INFO] 기존 아이템: {len(existing_items)}개")
    
    # 2. 새 데이터 수집
    print("[INFO] RSS 뉴스 수집 중...")
    news_items = collect_rss_news()
    print(f"[INFO] RSS 뉴스: {len(news_items)}개")
    
    print("[INFO] Reddit 게시물 수집 중...")
    reddit_items = collect_reddit_posts()
    print(f"[INFO] Reddit 게시물: {len(reddit_items)}개")
    
    print("[INFO] SoFi 전용 소스 수집 중...")
    sofi_items = collect_sofi_specific_sources()
    print(f"[INFO] SoFi 전용 소스: {len(sofi_items)}개")
    
    # 3. 병합
    all_new_items = news_items + reddit_items + sofi_items
    
    # 4. SOFI 관련 새 뉴스만 필터링 (Discord 알림용)
    sofi_new_items = [
        item for item in all_new_items
        if item["id"] not in existing_ids and "SOFI" in item.get("related_tickers", [])
    ]
    
    # 5. Discord 알림 전송 (SOFI 관련 새 뉴스만, 중요 뉴스만 필터링)
    discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if sofi_new_items and discord_webhook:
        # 중요 뉴스만 필터링 (제목에 특정 키워드가 있거나, 특정 소스인 경우)
        important_keywords = ["earnings", "실적", "분기", "quarter", "guidance", "가이던스", 
                             "acquisition", "인수", "merger", "합병", "partnership", "제휴",
                             "regulation", "규제", "approval", "승인", "launch", "출시"]
        important_sources = ["Yahoo Finance", "Bloomberg"]
        
        important_items = [
            item for item in sofi_new_items
            if any(keyword.lower() in item.get("content", "").lower() for keyword in important_keywords)
            or item.get("source_name") in important_sources
        ]
        
        # 중요 뉴스가 있으면 그것만, 없으면 전체 전송 (최대 5개로 제한)
        items_to_notify = important_items[:5] if important_items else sofi_new_items[:3]
        
        if items_to_notify:
            print(f"[INFO] SOFI 관련 중요 뉴스 {len(items_to_notify)}개 발견, Discord 알림 전송 중...")
            sent_count = send_sofi_discord_notification(discord_webhook, items_to_notify)
            print(f"[OK] Discord 알림 {sent_count}개 전송 완료")
        else:
            print(f"[INFO] SOFI 관련 새 뉴스 {len(sofi_new_items)}개 발견했지만 중요 뉴스는 없습니다.")
    elif sofi_new_items:
        print(f"[INFO] SOFI 관련 새 뉴스 {len(sofi_new_items)}개 발견 (Discord 알림 미설정)")
    
    # 6. 병합 및 저장
    merged_items = merge_items(existing_items, all_new_items)
    print(f"[INFO] 병합 후 총 아이템: {len(merged_items)}개")
    
    # 7. 저장
    save_feed(merged_items)
    print("[OK] 완료!")


if __name__ == "__main__":
    main()
