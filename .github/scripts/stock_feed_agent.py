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


def main():
    """메인 함수"""
    print("[INFO] 주식 뉴스 피드 수집 시작...")
    
    # 1. 기존 데이터 로드
    existing_items = load_existing_feed()
    print(f"[INFO] 기존 아이템: {len(existing_items)}개")
    
    # 2. 새 데이터 수집
    print("[INFO] RSS 뉴스 수집 중...")
    news_items = collect_rss_news()
    print(f"[INFO] RSS 뉴스: {len(news_items)}개")
    
    print("[INFO] Reddit 게시물 수집 중...")
    reddit_items = collect_reddit_posts()
    print(f"[INFO] Reddit 게시물: {len(reddit_items)}개")
    
    # 3. 병합
    all_new_items = news_items + reddit_items
    merged_items = merge_items(existing_items, all_new_items)
    print(f"[INFO] 병합 후 총 아이템: {len(merged_items)}개")
    
    # 4. 저장
    save_feed(merged_items)
    print("[OK] 완료!")


if __name__ == "__main__":
    main()
