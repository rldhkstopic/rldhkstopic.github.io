#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoFi 자동 포스팅 Agent
stock_feed.json에서 SoFi 관련 최신 뉴스를 수집하여 블로그 포스트를 자동 생성한다.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from zoneinfo import ZoneInfo

# 환경 설정
PROJECT_ROOT = Path(__file__).parent.parent.parent
STOCK_FEED_PATH = PROJECT_ROOT / "assets" / "data" / "stock_feed.json"
POSTS_DIR = PROJECT_ROOT / "_posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)


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


def generate_post_content(items: List[Dict], date_str: str) -> Optional[str]:
    """포스트 콘텐츠 생성"""
    if not items:
        return None
    
    # 카테고리별로 그룹화
    by_source = {}
    for item in items:
        source = item.get("source_name", "기타")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(item)
    
    # Front Matter 생성
    tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(tz)
    title = f"[{date_str}] SOFI 소식 정리"
    
    front_matter = f"""---
layout: post
title: "{title}"
date: {now.strftime('%Y-%m-%d %H:%M:%S')} +0900
author: rldhkstopic
category: stock
tags: ["SOFI", "주식", "뉴스"]
views: 0
---

"""
    
    # 본문 생성
    content = f"### {title}\n\n"
    content += f"**총 {len(items)}개의 SOFI 관련 소식**\n\n"
    
    # 소스별로 정리
    for source, source_items in sorted(by_source.items()):
        content += f"#### {source} ({len(source_items)}개)\n\n"
        
        for item in source_items[:10]:  # 소스당 최대 10개
            timestamp = item.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%m/%d %H:%M")
            except Exception:
                time_str = "N/A"
            
            content_text = item.get("content", "").strip()
            url = item.get("url", "")
            sentiment = item.get("sentiment", "NEUTRAL")
            
            # 감정 이모티콘 (텍스트)
            sentiment_icon = {
                "POSITIVE": "📈",
                "NEGATIVE": "📉",
                "NEUTRAL": "➖"
            }.get(sentiment, "➖")
            
            content += f"**{time_str}** {sentiment_icon} {content_text}\n"
            if url:
                content += f"  - [링크]({url})\n"
            content += "\n"
        
        content += "\n"
    
    # Footer
    content += "---\n\n"
    content += f"*이 포스트는 자동으로 생성되었습니다. (생성 시간: {now.strftime('%Y-%m-%d %H:%M:%S KST')})*\n"
    
    return front_matter + content


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
    
    # 4. 포스트 생성
    content = generate_post_content(sofi_items, today)
    if not content:
        print("[WARN] 포스트 생성 실패")
        return
    
    # 5. 파일 저장
    filename = f"{today}-SOFI-소식-정리.md"
    filepath = POSTS_DIR / filename
    
    filepath.write_text(content, encoding="utf-8")
    print(f"[OK] 포스트 생성 완료: {filename}")
    print(f"[OK] 경로: {filepath}")


if __name__ == "__main__":
    main()
