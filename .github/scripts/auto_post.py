#!/usr/bin/env python3
"""
자동 블로그 포스팅 메인 스크립트
여러 에이전트를 오케스트레이션하여 매일 포스트를 생성한다.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / '.github' / 'scripts'))

from agents.topic_collector import TopicCollectorAgent
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.writer import WriterAgent
from agents.validator import ValidatorAgent
from agents.post_creator import PostCreatorAgent


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("자동 포스팅 시스템 시작")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 환경 변수 확인
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("[ERROR] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 에이전트 초기화 (역할별)
    topic_agent = TopicCollectorAgent()
    researcher_agent = ResearcherAgent(gemini_key)
    analyst_agent = AnalystAgent(gemini_key)
    writer_agent = WriterAgent(gemini_key)
    validator_agent = ValidatorAgent()
    post_creator = PostCreatorAgent()
    
    try:
        # 1. 주제 수집
        print("\n[1단계] 주제 수집 중...")
        topics = topic_agent.collect_topics()
        if not topics:
            print("[WARN] 수집된 주제가 없습니다. 종료합니다.")
            return
        
        print(f"[OK] {len(topics)}개의 주제를 수집했습니다.")
        for i, topic in enumerate(topics[:3], 1):
            print(f"   {i}. {topic.get('title', 'N/A')}")
        
        # 첫 번째 주제 선택 (또는 랜덤 선택)
        selected_topic = topics[0]
        print(f"\n[선택] 주제: {selected_topic.get('title', 'N/A')}")
        
        # 2. 심층 조사 (ResearcherAgent)
        print("\n[2단계] 심층 조사 중...")
        research_data = researcher_agent.research_topic(selected_topic)
        if not research_data or not research_data.get('raw_research'):
            print("[WARN] 조사 데이터가 부족합니다. 계속 진행합니다.")
        
        print(f"[OK] 조사 완료 (출처: {len(research_data.get('sources', []))}개)")
        
        # 3. 데이터 분석 (AnalystAgent)
        print("\n[3단계] 데이터 분석 중...")
        analysis_data = analyst_agent.analyze(research_data, selected_topic)
        if not analysis_data or not analysis_data.get('insights'):
            print("[WARN] 분석 데이터가 부족합니다. 계속 진행합니다.")
        
        print("[OK] 분석 완료")
        
        # 4. 글 작성 (WriterAgent)
        print("\n[4단계] 글 작성 중...")
        content_text = writer_agent.write(selected_topic, research_data, analysis_data)
        if not content_text:
            print("[ERROR] 글 작성에 실패했습니다.")
            return
        
        # 콘텐츠 구조화
        content = {
            'title': selected_topic.get('title', ''),
            'content': content_text,
            'category': selected_topic.get('category', 'document'),
            'tags': selected_topic.get('tags', []),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'author': 'rldhkstopic',
            'source': selected_topic.get('source', 'auto'),
            'source_url': selected_topic.get('source_url', '')
        }
        
        print(f"[OK] 작성 완료 ({len(content_text)}자)")
        
        # 5. 검증
        print("\n[5단계] 콘텐츠 검증 중...")
        validation_result = validator_agent.validate(content)
        if not validation_result['valid']:
            print("[WARN] 검증 실패:")
            for error in validation_result.get('errors', []):
                print(f"   - {error}")
            # 경고만 있으면 계속 진행
            if validation_result.get('errors'):
                print("[ERROR] 치명적 오류로 인해 중단합니다.")
                return
        
        if validation_result.get('warnings'):
            print("[WARN] 경고:")
            for warning in validation_result['warnings']:
                print(f"   - {warning}")
        
        print("[OK] 검증 완료")
        
        # 6. 포스트 생성
        print("\n[6단계] 포스트 파일 생성 중...")
        post_path = post_creator.create_post(content, selected_topic)
        if not post_path:
            print("[ERROR] 포스트 생성에 실패했습니다.")
            return
        
        print(f"[OK] 포스트 생성 완료: {post_path}")
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 자동 포스팅 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

