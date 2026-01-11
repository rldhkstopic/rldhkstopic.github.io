"""
주제 수집 에이전트
뉴스, 기술 트렌드, 최신 정보를 수집하여 블로그 포스트 주제를 생성한다.
"""

import requests
import random
from datetime import datetime, timedelta
from typing import List, Dict
import os
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo


class TopicCollectorAgent:
    """주제 수집 에이전트"""
    
    def __init__(self):
        self.sources = [
            self._collect_bloomberg_yesterday_digest,
            self._collect_tech_news,
            self._collect_hackernews,
            self._generate_trending_topic,
        ]
    
    def collect_topics(self) -> List[Dict]:
        """
        여러 소스에서 주제를 수집한다.
        
        Returns:
            List[Dict]: 주제 리스트 (각 항목은 title, description, category, tags 포함)
        """
        all_topics = []
        
        for source_func in self.sources:
            try:
                topics = source_func()
                if topics:
                    all_topics.extend(topics)
            except Exception as e:
                print(f"⚠️  주제 수집 중 오류 ({source_func.__name__}): {str(e)}")
                continue
        
        # 중복 제거 및 정렬
        unique_topics = self._deduplicate_topics(all_topics)
        
        return unique_topics[:5]  # 상위 5개만 반환
    
    def _collect_tech_news(self) -> List[Dict]:
        """기술 뉴스 수집 (예시: RSS 피드 또는 API)"""
        topics = []
        
        # 예시: 간단한 주제 생성 (실제로는 뉴스 API나 RSS 피드를 사용)
        tech_topics = [
            {
                'title': '최신 AI 기술 동향 분석',
                'description': '최근 발표된 AI 기술과 연구 동향을 분석한다.',
                'category': 'document',
                'tags': ['AI', '기술동향', '분석'],
                'source': 'tech_news'
            },
            {
                'title': '오픈소스 프로젝트 리뷰',
                'description': '주목할 만한 오픈소스 프로젝트를 리뷰한다.',
                'category': 'dev',
                'tags': ['오픈소스', '개발'],
                'source': 'tech_news'
            }
        ]
        
        return tech_topics

    def _collect_bloomberg_yesterday_digest(self) -> List[Dict]:
        """
        여러 경제 뉴스 소스 RSS를 사용해 전일(Asia/Seoul 기준) 뉴스 항목을 모아 다이제스트 주제로 만든다.

        - RSS는 제목/요약/링크만 사용한다(원문 전문 수집 금지).
        - 전일 범위는 KST 00:00:00 ~ 23:59:59 로 필터링한다.
        - 수집 소스: 블룸버그, 다음경제, investing, 한국경제, 미국 경제뉴스 등
        """
        # 사용자가 RSS 피드를 커스터마이징할 수 있도록 환경 변수로 받는다.
        # 예: ECONOMIC_NEWS_RSS_FEEDS="https://feeds.bloomberg.com/markets/news.rss,https://..."
        feeds_env = os.getenv("ECONOMIC_NEWS_RSS_FEEDS", "").strip()
        if feeds_env:
            feed_urls = [u.strip() for u in feeds_env.split(",") if u.strip()]
        else:
            # 기본값: 여러 경제 뉴스 소스
            feed_urls = [
                # Bloomberg
                "https://feeds.bloomberg.com/markets/news.rss",
                "https://feeds.bloomberg.com/technology/news.rss",
                "https://feeds.bloomberg.com/politics/news.rss",
                # 다음경제 (RSS URL 확인 필요)
                # "https://news.daum.net/rss/economic",
                # investing.com (RSS URL 확인 필요)
                # "https://www.investing.com/rss/news.rss",
                # 한국경제 (RSS URL 확인 필요)
                # "https://www.hankyung.com/rss/economy",
                # 미국 경제뉴스 (예: Reuters, WSJ 등)
                # "https://feeds.reuters.com/reuters/businessNews",
            ]

        # 전일 범위(Asia/Seoul)
        tz = ZoneInfo("Asia/Seoul")
        now_kst = datetime.now(tz=tz)
        today_start = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59, microsecond=999999)

        items: List[Dict] = []
        seen_links = set()

        for url in feed_urls:
            try:
                resp = requests.get(url, timeout=8, headers={"User-Agent": "rldhkstopic-auto-post/1.0"})
                if resp.status_code != 200:
                    continue
                root = ET.fromstring(resp.text)

                # RSS 2.0: rss/channel/item
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

                    if not title or not link or not pub:
                        continue
                    if link in seen_links:
                        continue

                    try:
                        dt = parsedate_to_datetime(pub)
                        if dt.tzinfo is None:
                            # tz가 없으면 UTC로 가정
                            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
                        dt_kst = dt.astimezone(tz)
                    except Exception:
                        continue

                    if not (yesterday_start <= dt_kst <= yesterday_end):
                        continue

                    seen_links.add(link)
                    items.append(
                        {
                            "title": title,
                            "link": link,
                            "published_at": dt_kst.isoformat(),
                            "summary": desc,
                        }
                    )
            except Exception:
                continue

        if not items:
            return []

        # 너무 길면 상위 N개로 제한(대략 최신순)
        items.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        items = items[:25]

        ymd = yesterday_start.strftime("%Y-%m-%d")
        topic = {
            "title": f"{ymd} 전일 경제 뉴스 정리",
            "description": f"여러 경제 뉴스 소스에서 전일(한국시간) 뉴스 {len(items)}건을 묶어 요약하고 관찰 포인트를 정리한다.",
            "category": "document",
            "tags": ["경제뉴스", "뉴스요약", "시장", "전일"],
            "source": "bloomberg_rss",  # 기존 코드 호환성을 위해 유지
            "source_url": feed_urls[0] if feed_urls else "",
            "digest_items": items,
        }
        return [topic]
    
    def _collect_hackernews(self) -> List[Dict]:
        """Hacker News 인기 글 수집"""
        topics = []
        
        try:
            # Hacker News API
            response = requests.get(
                'https://hacker-news.firebaseio.com/v0/topstories.json',
                timeout=5
            )
            if response.status_code == 200:
                top_story_ids = response.json()[:5]  # 상위 5개
                
                for story_id in top_story_ids:
                    story_response = requests.get(
                        f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json',
                        timeout=5
                    )
                    if story_response.status_code == 200:
                        story = story_response.json()
                        if story.get('title') and story.get('url'):
                            topics.append({
                                'title': f"{story['title']} 분석",
                                'description': story.get('title', ''),
                                'category': 'document',
                                'tags': ['기술', '분석'],
                                'source': 'hackernews',
                                'source_url': story.get('url', '')
                            })
        except Exception as e:
            print(f"Hacker News 수집 실패: {str(e)}")
        
        return topics
    
    def _generate_trending_topic(self) -> List[Dict]:
        """트렌딩 주제 생성 (키워드 기반)"""
        # 현재 날짜 기반 주제 생성
        today = datetime.now()
        
        trending_topics = [
            {
                'title': f'{today.strftime("%Y년 %m월")} 기술 트렌드 정리',
                'description': f'{today.strftime("%Y년 %m월")}에 주목받은 기술 트렌드를 정리한다.',
                'category': 'document',
                'tags': ['트렌드', '기술동향'],
                'source': 'trending'
            },
            {
                'title': '개발 환경 설정 가이드',
                'description': '최신 개발 도구와 환경 설정 방법을 정리한다.',
                'category': 'dev',
                'tags': ['개발환경', '가이드'],
                'source': 'trending'
            }
        ]
        
        return trending_topics
    
    def _deduplicate_topics(self, topics: List[Dict]) -> List[Dict]:
        """중복 주제 제거"""
        seen_titles = set()
        unique_topics = []
        
        for topic in topics:
            title = topic.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_topics.append(topic)
        
        return unique_topics

