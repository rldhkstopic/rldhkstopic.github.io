"""
주제 수집 에이전트
뉴스, 기술 트렌드, 최신 정보를 수집하여 블로그 포스트 주제를 생성한다.
"""

import requests
import random
from datetime import datetime
from typing import List, Dict


class TopicCollectorAgent:
    """주제 수집 에이전트"""
    
    def __init__(self):
        self.sources = [
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

