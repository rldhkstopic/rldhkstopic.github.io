#!/usr/bin/env python3
"""
일기 작성 에이전트
하루 동안 기록된 일상 로그들을 취합하여 일기로 작성한다.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / '.github' / 'scripts'))

from agents.writer import WriterAgent
from agents.validator import ValidatorAgent
from agents.post_creator import PostCreatorAgent
from agents.translator import TranslatorAgent, generate_ref_id
from reviewer_agent import ReviewerAgent


def load_daily_logs(target_date: str) -> List[Dict]:
    """
    특정 날짜의 일상 기록들을 로드한다.
    
    Args:
        target_date: YYYY-MM-DD 형식의 날짜
        
    Returns:
        기록 리스트
    """
    logs_dir = project_root / "_daily_logs" / target_date
    if not logs_dir.exists():
        return []
    
    logs = []
    for log_file in logs_dir.glob("*.json"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                logs.append(log_data)
        except Exception as e:
            print(f"[WARN] 기록 파일 읽기 실패 ({log_file.name}): {e}")
            continue
    
    # 타임스탬프 기준 정렬
    logs.sort(key=lambda x: x.get('timestamp', ''))
    return logs


def aggregate_logs(logs: List[Dict], target_date: str) -> Dict:
    """
    기록들을 취합하여 조사 데이터 형태로 변환한다.
    
    Args:
        logs: 일상 기록 리스트
        target_date: YYYY-MM-DD 형식의 날짜
        
    Returns:
        조사 데이터 딕셔너리
    """
    if not logs:
        return {
            'raw_research': '오늘 기록된 일이 없습니다.',
            'sources': []
        }
    
    # 기록들을 시간순으로 정리 (target_date 기준)
    try:
        date_obj = datetime.strptime(target_date, '%Y-%m-%d')
        date_str = date_obj.strftime('%Y년 %m월 %d일')
    except Exception:
        # 파싱 실패 시에도 사람이 읽기 쉬운 표기로 유지
        date_str = target_date

    aggregated_text = f"오늘({date_str}) 기록된 일상:\n\n"
    
    for i, log in enumerate(logs, 1):
        timestamp = log.get('timestamp', '')
        content = log.get('content', '')
        mood = log.get('mood')
        location = log.get('location')
        # tags가 null/문자열로 들어오는 케이스를 방어
        raw_tags = log.get('tags')
        if raw_tags is None:
            tags: List[str] = []
        elif isinstance(raw_tags, list):
            tags = [str(t).strip() for t in raw_tags if str(t).strip()]
        else:
            # 단일 문자열이면 쉼표 기반으로 분해
            tags = [t.strip() for t in str(raw_tags).split(',') if t.strip()]
        
        # 시간 파싱
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M')
        except:
            time_str = timestamp[:5] if len(timestamp) >= 5 else ''
        
        aggregated_text += f"[{i}] {time_str}"
        if location:
            aggregated_text += f" @ {location}"
        if mood:
            aggregated_text += f" (기분: {mood})"
        aggregated_text += f"\n{content}\n"
        
        if tags:
            aggregated_text += f"태그: {', '.join(tags)}\n"
        
        aggregated_text += "\n"
    
    return {
        'raw_research': aggregated_text,
        'sources': []
    }


def create_diary_topic(target_date: str, log_count: int) -> Dict:
    """
    일기 주제를 생성한다.
    
    Args:
        target_date: YYYY-MM-DD 형식의 날짜
        log_count: 기록 개수
        
    Returns:
        주제 딕셔너리
    """
    # 허용: YYYY-MM-DD 또는 YYYYMMDD
    if len(target_date) == 8 and target_date.isdigit():
        target_date = f"{target_date[0:4]}-{target_date[4:6]}-{target_date[6:8]}"
    date_obj = datetime.strptime(target_date, '%Y-%m-%d')
    date_str = date_obj.strftime('%Y년 %m월 %d일')
    
    # 제목은 AI가 생성할 때 요약 제목을 포함하도록 하므로, 여기서는 기본 형식만 제공
    # 실제 제목은 WriterAgent가 일기 내용을 바탕으로 "[YYYY-MM-DD] 요약 제목" 형식으로 생성
    return {
        'title': f"[{target_date}] 일기",  # AI가 요약 제목으로 대체할 예정
        'description': f"오늘 하루 동안 기록한 {log_count}개의 일상을 정리한 일기입니다.",
        'category': 'daily',
        'tags': ['일기', '일상'],
        'source': 'daily_logger',
        'source_url': '',
    }


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("일기 작성 에이전트 시작")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 환경 변수 확인
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("[ERROR] GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        sys.exit(1)
    
    # Discord 웹훅 URL (선택 사항)
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    
    # 대상 날짜 (어제 또는 오늘, 기본값: 어제)
    # 새벽 6시에 실행되므로 전날 날짜를 사용
    target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 명령줄 인자로 날짜 지정 가능
    if len(sys.argv) > 1:
        raw = sys.argv[1].strip()
        # 허용: YYYY-MM-DD 또는 YYYYMMDD
        if len(raw) == 8 and raw.isdigit():
            target_date = f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"
        else:
            target_date = raw
    
    print(f"\n[대상 날짜] {target_date}")
    
    # 1. 일상 기록 로드
    print("\n[1단계] 일상 기록 로드 중...")
    logs = load_daily_logs(target_date)
    
    if not logs:
        print(f"[INFO] {target_date}에 기록된 일이 없습니다. 일기 작성을 건너뜁니다.")
        sys.exit(0)
    
    print(f"[OK] {len(logs)}개의 기록을 찾았습니다.")
    
    # 2. 기록 취합
    print("\n[2단계] 기록 취합 중...")
    research_data = aggregate_logs(logs, target_date)
    print(f"[OK] 취합 완료 ({len(research_data['raw_research'])}자)")
    
    # 3. 일기 주제 생성
    topic = create_diary_topic(target_date, len(logs))
    print(f"\n[주제] {topic['title']}")
    
    # 4. 에이전트 초기화
    writer_agent = WriterAgent(gemini_key)
    reviewer_agent = ReviewerAgent(gemini_key)
    validator_agent = ValidatorAgent()
    post_creator = PostCreatorAgent()
    
    # 5. 일기 작성 (WriterAgent - Daily 카테고리)
    print("\n[3단계] 일기 작성 중...")
    # Daily 카테고리는 조사/분석 단계를 생략하고 기록을 직접 사용
    analysis_data = {
        'insights': f"오늘 하루 동안 {len(logs)}개의 일상이 기록되었습니다. 이를 바탕으로 하루를 회고하는 일기를 작성합니다."
    }
    
    content_text = writer_agent.write(topic, research_data, analysis_data)
    if not content_text:
        print("[ERROR] 일기 작성에 실패했습니다.")
        sys.exit(1)
    
    print(f"[OK] 초안 작성 완료 ({len(content_text)}자)")
    
    # 6. 검토 (ReviewerAgent)
    print("\n[4단계] 일기 검토/교정 중...")
    final_content_text = reviewer_agent.review(content_text, 'daily')
    if not final_content_text:
        print("[ERROR] 검토 결과가 비었습니다.")
        sys.exit(1)
    
    print(f"[OK] 검토 완료 ({len(final_content_text)}자)")
    
    # 7. 검증
    print("\n[5단계] 콘텐츠 검증 중...")
    content = {
        'title': topic['title'],
        'content': final_content_text,
        'category': 'daily',
        'tags': topic['tags'],
        'date': target_date,
        'author': 'rldhkstopic',
        'source': 'daily_logger',
        'source_url': '',
    }
    
    validation_result = validator_agent.validate(content)
    if not validation_result['valid']:
        print("[WARN] 검증 실패:")
        for error in validation_result.get('errors', []):
            print(f"   - {error}")
        if validation_result.get('errors'):
            print("[ERROR] 치명적 오류로 인해 중단합니다.")
            sys.exit(1)
    
    if validation_result.get('warnings'):
        print("[WARN] 경고:")
        for warning in validation_result['warnings']:
            print(f"   - {warning}")
    
    print("[OK] 검증 완료")
    
    # 8. 포스트 생성
    print("\n[6단계] 포스트 파일 생성 중...")
    post_path = post_creator.create_post(content, topic)
    if not post_path:
        print("[ERROR] 포스트 생성에 실패했습니다.")
        sys.exit(1)
    
    print(f"[OK] 포스트 생성 완료: {post_path}")
    
    # 9. Discord 알림 (선택)
    if discord_webhook:
        try:
            from discord_notifier import notify_post_success
            notify_post_success(
                discord_webhook,
                topic['title'],
                'daily',
                str(post_path),
                'daily_logger',
            )
            print("[OK] Discord 알림 전송 완료")
        except Exception as e:
            print(f"[WARN] Discord 알림 전송 실패: {e}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 일기 작성 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()

