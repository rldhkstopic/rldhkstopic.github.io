#!/usr/bin/env python3
"""
디스코드 글 작성 기능 로컬 테스트 스크립트

이 스크립트는 디스코드 봇 없이 로컬에서 글 작성 기능을 테스트할 수 있게 해줍니다.
사용자 입력을 받아서 JSON 요청 파일을 생성하고, auto_post.py를 실행합니다.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# .env 파일 지원 (python-dotenv 설치 필요)
try:
    from dotenv import load_dotenv
    # 프로젝트 루트와 bots/discord 디렉토리의 .env 파일 로드
    project_root = Path(__file__).parent.parent.parent
    load_dotenv(project_root / "bots" / "discord" / ".env")  # bots/discord/.env 파일 로드
    load_dotenv(project_root / ".env")  # 프로젝트 루트의 .env 파일도 로드 (있는 경우)
except ImportError:
    pass  # python-dotenv가 없어도 환경 변수로 동작

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'automation' / 'scripts'))

REQUEST_DIR = project_root / "automation" / "requests"


def create_request_file(category: str, topic: str, situation: str = "", action: str = "", memo: str = "") -> Path:
    """요청 JSON 파일 생성"""
    REQUEST_DIR.mkdir(parents=True, exist_ok=True)
    
    # 파일명 생성: request_YYYYMMDD_HHMMSS.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"request_{timestamp}.json"
    filepath = REQUEST_DIR / filename
    
    # JSON 페이로드 생성
    payload = {
        "Category": category,
        "Topic": topic,
        "Situation": situation,
        "Action": action,
        "Memo": memo,
        "source": "local_test",
        "requested_at": datetime.utcnow().isoformat() + "Z",
        "user": "local_test_user"
    }
    
    # 파일 저장
    filepath.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    
    print(f"\n[OK] 요청 파일 생성 완료: {filepath}")
    print(f"[INFO] 요청 내용:")
    print(f"  - 카테고리: {category}")
    print(f"  - 제목: {topic}")
    if situation:
        print(f"  - 상황: {situation[:100]}...")
    if action:
        print(f"  - 액션: {action[:100]}...")
    if memo:
        print(f"  - 메모: {memo[:100]}...")
    
    return filepath


def get_user_input() -> dict:
    """사용자 입력 받기"""
    print("=" * 60)
    print("디스코드 글 작성 기능 로컬 테스트")
    print("=" * 60)
    print()
    
    # 카테고리 선택
    print("카테고리를 선택하세요:")
    print("  1. dev (개발 관련)")
    print("  2. study (학습 내용)")
    print("  3. daily (일상 기록)")
    print("  4. document (문서화/분석)")
    
    while True:
        choice = input("\n선택 (1-4): ").strip()
        category_map = {
            "1": "dev",
            "2": "study",
            "3": "daily",
            "4": "document"
        }
        if choice in category_map:
            category = category_map[choice]
            break
        print("잘못된 선택입니다. 1-4 중에서 선택하세요.")
    
    # 제목 입력
    print("\n" + "-" * 60)
    topic = input("제목/주제를 입력하세요 (필수): ").strip()
    if not topic:
        print("[ERROR] 제목은 필수입니다.")
        sys.exit(1)
    
    # 상황 입력 (선택)
    print("\n" + "-" * 60)
    print("상황/문제 설명을 입력하세요 (선택, Enter로 건너뛰기):")
    situation = input().strip()
    
    # 액션 입력 (선택)
    print("\n" + "-" * 60)
    print("해결 방법/시도한 내용을 입력하세요 (선택, Enter로 건너뛰기):")
    action = input().strip()
    
    # 메모 입력 (선택)
    print("\n" + "-" * 60)
    print("기타 메모나 참고 링크를 입력하세요 (선택, Enter로 건너뛰기):")
    memo = input().strip()
    
    return {
        "category": category,
        "topic": topic,
        "situation": situation,
        "action": action,
        "memo": memo
    }


def main():
    """메인 실행 함수"""
    # 환경 변수 확인 (.env 파일에서도 로드됨)
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("[ERROR] GEMINI_API_KEY를 찾을 수 없습니다.")
        print("\n다음 방법 중 하나로 API 키를 설정하세요:")
        print("  1. bots/discord/.env 파일에 GEMINI_API_KEY=your_key 추가")
        print("  2. 환경 변수로 설정:")
        print("     Windows: $env:GEMINI_API_KEY = \"<YOUR_KEY>\"")
        print("     Linux/Mac: export GEMINI_API_KEY=\"<YOUR_KEY>\"")
        print("\n참고: bots/discord/.env 파일이 있다면 자동으로 로드됩니다.")
        sys.exit(1)
    
    # API 키가 .env 파일에서 로드되었는지 확인
    env_file = project_root / "bots" / "discord" / ".env"
    if env_file.exists():
        print(f"[INFO] bots/discord/.env 파일에서 API 키를 로드했습니다.")
    else:
        print(f"[INFO] 환경 변수에서 API 키를 사용합니다.")
    
    try:
        # 사용자 입력 받기
        user_input = get_user_input()
        
        # 요청 파일 생성
        request_file = create_request_file(
            category=user_input["category"],
            topic=user_input["topic"],
            situation=user_input["situation"],
            action=user_input["action"],
            memo=user_input["memo"]
        )
        
        # auto_post.py 실행
        print("\n" + "=" * 60)
        print("글 작성 프로세스 시작...")
        print("=" * 60)
        print()
        
        from auto_post import main as auto_post_main
        auto_post_main()
        
    except KeyboardInterrupt:
        print("\n\n[INFO] 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
