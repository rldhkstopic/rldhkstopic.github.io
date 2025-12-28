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
from agents.content_generator import ContentGeneratorAgent
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
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # 에이전트 초기화
    topic_agent = TopicCollectorAgent()
    content_agent = ContentGeneratorAgent(gemini_key)
    validator_agent = ValidatorAgent()
    post_creator = PostCreatorAgent()
    
    try:
        # 1. 주제 수집
        print("\n[1단계] 주제 수집 중...")
        topics = topic_agent.collect_topics()
        if not topics:
            print("⚠️  수집된 주제가 없습니다. 종료합니다.")
            return
        
        print(f"✅ {len(topics)}개의 주제를 수집했습니다.")
        for i, topic in enumerate(topics[:3], 1):
            print(f"   {i}. {topic.get('title', 'N/A')}")
        
        # 첫 번째 주제 선택 (또는 랜덤 선택)
        selected_topic = topics[0]
        print(f"\n📌 선택된 주제: {selected_topic.get('title', 'N/A')}")
        
        # 2. 콘텐츠 생성
        print("\n[2단계] 콘텐츠 생성 중...")
        content = content_agent.generate_content(selected_topic)
        if not content:
            print("❌ 콘텐츠 생성에 실패했습니다.")
            return
        
        print("✅ 콘텐츠 생성 완료")
        
        # 3. 검증
        print("\n[3단계] 콘텐츠 검증 중...")
        validation_result = validator_agent.validate(content)
        if not validation_result['valid']:
            print("⚠️  검증 실패:")
            for error in validation_result.get('errors', []):
                print(f"   - {error}")
            # 경고만 있으면 계속 진행
            if validation_result.get('errors'):
                print("❌ 치명적 오류로 인해 중단합니다.")
                return
        
        if validation_result.get('warnings'):
            print("⚠️  경고:")
            for warning in validation_result['warnings']:
                print(f"   - {warning}")
        
        print("✅ 검증 완료")
        
        # 4. 포스트 생성
        print("\n[4단계] 포스트 파일 생성 중...")
        post_path = post_creator.create_post(content, selected_topic)
        if not post_path:
            print("❌ 포스트 생성에 실패했습니다.")
            return
        
        print(f"✅ 포스트 생성 완료: {post_path}")
        
        print("\n" + "=" * 60)
        print("✅ 자동 포스팅 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

