#!/usr/bin/env python3
"""
자동 블로그 포스팅 메인 스크립트
여러 에이전트를 오케스트레이션하여 매일 포스트를 생성한다.
"""

import os
import sys
import json
import random
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / '.github' / 'scripts'))

from agents.topic_collector import TopicCollectorAgent
from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.writer import WriterAgent
from agents.validator import ValidatorAgent
from agents.post_creator import PostCreatorAgent
from reviewer_agent import ReviewerAgent

try:
    from discord_notifier import notify_post_success, notify_post_failure, save_processing_result
    DISCORD_NOTIFIER_AVAILABLE = True
except ImportError:
    DISCORD_NOTIFIER_AVAILABLE = False
REQUEST_DIR = project_root / "_auto_post_requests"
PROCESSED_DIR = project_root / "_auto_post_requests_processed"
RESULTS_DIR = project_root / "_auto_post_results"



def _load_existing_post_titles(posts_dir: Path) -> Set[str]:
    """이미 발행된 포스트의 제목(Front Matter title)을 수집한다."""
    titles: Set[str] = set()
    if not posts_dir.exists():
        return titles

    for post_path in posts_dir.glob("*.md"):
        try:
            text = post_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Front Matter의 title 라인 파싱 (따옴표 유무 모두 대응)
        m = re.search(r'(?m)^title:\s*"?(.+?)"?\s*$', text)
        if m:
            title = m.group(1).strip().lower()
            if title:
                titles.add(title)

    return titles


def _select_topic(topics: List[Dict], existing_titles: Set[str]) -> Dict:
    """
    반복 포스팅 방지를 위해, 이미 존재하는 제목은 우선 제외하고 주제를 선택한다.
    - source_url이 있는(=외부 링크 기반) 주제를 우선
    - 정적 예시(tech_news)보다 동적 소스를 우선
    """
    def score(topic: Dict) -> int:
        s = 0
        if topic.get("source_url"):
            s += 10
        if topic.get("source") and topic.get("source") != "tech_news":
            s += 3
        return s

    # 같은 날에도 변동이 생기도록 약한 랜덤성 추가
    random.shuffle(topics)
    ranked = sorted(topics, key=score, reverse=True)

    for t in ranked:
        title = (t.get("title") or "").strip().lower()
        if title and title not in existing_titles:
            return t

    # 전부 중복이면 최선의 후보를 그대로 사용 (단, 이후 검증/생성 단계에서 걸러질 수 있음)
    return ranked[0]


def _load_request() -> Dict:
    """요청 큐에서 JSON 요청을 하나 불러온다."""
    if not REQUEST_DIR.exists():
        print("[INFO] 요청 디렉토리가 존재하지 않습니다.")
        return {}
    request_files = sorted(REQUEST_DIR.glob("*.json"))
    if not request_files:
        print("[INFO] 대기 중인 요청이 없습니다.")
        return {}

    print(f"[INFO] 발견된 요청 파일 수: {len(request_files)}")
    for i, f in enumerate(request_files[:5], 1):  # 최대 5개만 출력
        print(f"  {i}. {f.name}")

    req_file = request_files[0]
    print(f"[INFO] 처리할 요청 파일: {req_file.name}")
    try:
        data = json.loads(req_file.read_text(encoding="utf-8"))
        topic = data.get("Topic") or data.get("title") or "N/A"
        category = data.get("Category") or "N/A"
        print(f"[INFO] 요청 내용 - 주제: {topic}, 카테고리: {category}")
    except Exception as e:
        print(f"[ERROR] 요청 파일 파싱 실패: {e}")
        return {}

    data["_request_file"] = req_file
    return data


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
    
    # Discord 웹훅 URL (선택 사항)
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    
    # 에이전트 초기화 (역할별)
    topic_agent = TopicCollectorAgent()
    researcher_agent = ResearcherAgent(gemini_key)
    analyst_agent = AnalystAgent(gemini_key)
    writer_agent = WriterAgent(gemini_key)
    reviewer_agent = ReviewerAgent(gemini_key)
    validator_agent = ValidatorAgent()
    post_creator = PostCreatorAgent()
    
    try:
        # 0. 요청 큐 우선 처리
        request_data = _load_request()
        request_mode = bool(request_data)
        request_file = request_data.get("_request_file") if request_mode else None
        request_id = request_data.get("request_id") or (request_file.stem if request_file else None) if request_mode else None
        request_source = request_data.get("source", "discord") if request_mode else None

        # 1. 주제 수집
        if request_mode:
            print("\n[1단계] 디스코드 요청 처리 중...")
            print(f"[INFO] 요청 파일: {request_file.name if request_file else 'N/A'}")
            req_title = request_data.get("Topic") or request_data.get("title") or "Untitled"
            req_category = (request_data.get("Category") or "document").lower()
            req_situation = request_data.get("Situation") or ""
            req_action = request_data.get("Action") or ""
            req_memo = request_data.get("Memo") or ""
            mapped_category = req_category if req_category in ["dev", "study", "daily", "document"] else "document"
            selected_topic = {
                "title": req_title,
                "description": req_situation,
                "category": mapped_category,
                "tags": [],
                "source": "discord",
                "source_url": "",
            }
            print(f"[OK] 요청 주제: {selected_topic.get('title')}")
            print(f"[OK] 카테고리: {mapped_category}")
            print(f"[OK] 요청 출처: {request_source}")
        else:
            print("\n[1단계] 주제 수집 중...")
            topics = topic_agent.collect_topics()
            if not topics:
                print("[WARN] 수집된 주제가 없습니다. 종료합니다.")
                return  # 주제가 없으면 정상 종료
            
            print(f"[OK] {len(topics)}개의 주제를 수집했습니다.")
            for i, topic in enumerate(topics[:3], 1):
                print(f"   {i}. {topic.get('title', 'N/A')}")
            
            # 이미 발행된 글과 동일한 제목은 우선 제외하여 선택
            existing_titles = _load_existing_post_titles(project_root / "_posts")
            selected_topic = _select_topic(topics, existing_titles)
            print(f"\n[선택] 주제: {selected_topic.get('title', 'N/A')}")
        
        # 2. 심층 조사 (ResearcherAgent)
        print("\n[2단계] 심층 조사 중...")
        if request_mode:
            # 요청 기반: 메모/상황/액션을 조사 데이터로 간주
            memo_text = f"상황: {selected_topic.get('description','')}\n" \
                        f"액션: {request_data.get('Action','')}\n" \
                        f"메모: {request_data.get('Memo','')}"
            research_data = {
                "raw_research": memo_text,
                "sources": []
            }
            print("[OK] 요청 기반 조사 데이터 사용")
        else:
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
            sys.exit(1)
        
        # 4-1. 작성 후 검토 (ReviewerAgent)
        print("\n[4-1단계] 작성물 검토/교정 중...")
        final_content_text = reviewer_agent.review(content_text, selected_topic.get("category", "document"))
        if not final_content_text:
            print("[ERROR] 검토 결과가 비었습니다.")
            sys.exit(1)

        # 콘텐츠 구조화
        content = {
            'title': selected_topic.get('title', ''),
            'content': final_content_text,
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
            if validation_result.get('errors'):
                print("[ERROR] 치명적 오류로 인해 중단합니다.")
                sys.exit(1)
        
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
            sys.exit(1)
        
        print(f"[OK] 포스트 생성 완료: {post_path}")

        # 요청 처리 완료 시 파일 이동
        if request_mode and request_file:
            PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
            dest = PROCESSED_DIR / request_file.name
            try:
                shutil.move(str(request_file), dest)
                print(f"[INFO] 요청 파일 이동: {request_file.name} -> {dest}")
            except Exception as e:
                print(f"[WARN] 요청 파일 이동 실패: {e}")
        
        # Discord 알림 전송 (성공)
        if DISCORD_NOTIFIER_AVAILABLE and discord_webhook:
            topic_title = selected_topic.get('title', 'N/A')
            category = selected_topic.get('category', 'document')
            # 포스트 내용 읽기
            try:
                post_content = Path(post_path).read_text(encoding="utf-8")
            except Exception:
                post_content = content_text  # 파일 읽기 실패 시 메모리의 내용 사용
            notify_post_success(
                discord_webhook,
                topic_title,
                category,
                str(post_path),
                request_source,
                post_content,
            )
        
        # 처리 결과 저장
        if request_id and DISCORD_NOTIFIER_AVAILABLE:
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            save_processing_result(
                str(RESULTS_DIR),
                request_id,
                "success",
                selected_topic.get('title', 'N/A'),
                str(post_path),
            )
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 자동 포스팅 완료!")
        print("=" * 60)
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n[ERROR] 오류 발생: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Discord 알림 전송 (실패)
        if DISCORD_NOTIFIER_AVAILABLE and discord_webhook:
            topic_title = request_data.get('Topic', '알 수 없음') if request_data else '알 수 없음'
            notify_post_failure(
                discord_webhook,
                topic_title,
                error_msg,
                request_source,
            )
        
        # 처리 결과 저장 (실패)
        if request_id and DISCORD_NOTIFIER_AVAILABLE:
            RESULTS_DIR.mkdir(parents=True, exist_ok=True)
            topic_title = request_data.get('Topic', '알 수 없음') if request_data else '알 수 없음'
            save_processing_result(
                str(RESULTS_DIR),
                request_id,
                "failure",
                topic_title,
                None,
                error_msg,
            )
        
        sys.exit(1)


if __name__ == '__main__':
    main()

