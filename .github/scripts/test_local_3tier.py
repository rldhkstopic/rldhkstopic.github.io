#!/usr/bin/env python3
"""
3-Tier Agent Pipeline 로컬 테스트 스크립트

사용법:
1. 환경 변수 설정:
   Windows: set GEMINI_API_KEY=your_key
   Linux/Mac: export GEMINI_API_KEY=your_key

2. 실행:
   python test_local_3tier.py

3. 메모 입력:
   스크립트 실행 후 메모를 입력하면 3단계 파이프라인을 통해 글을 생성합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / '.github' / 'scripts'))

from agents.writer import WriterAgent

def main():
    # API 키 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ 오류: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("\n설정 방법:")
        print("  Windows: set GEMINI_API_KEY=your_key")
        print("  Linux/Mac: export GEMINI_API_KEY=your_key")
        sys.exit(1)
    
    # WriterAgent 초기화
    print("🔧 WriterAgent 초기화 중...")
    writer = WriterAgent(api_key=api_key)
    print("✅ 초기화 완료\n")
    
    # 사용자 입력 받기
    print("=" * 60)
    print("3-Tier Agent Pipeline 로컬 테스트")
    print("=" * 60)
    print("\n작성할 글에 대한 메모를 입력하세요.")
    print("(여러 줄 입력 가능, 빈 줄 두 번 입력하면 종료)\n")
    
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
            if not line.strip():
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\n❌ 사용자에 의해 중단되었습니다.")
            sys.exit(0)
    
    memo = '\n'.join(lines)
    
    if not memo.strip():
        print("\n❌ 메모가 입력되지 않았습니다.")
        sys.exit(1)
    
    # 제목 입력 (선택사항)
    print("\n제목을 입력하세요 (선택사항, Enter로 건너뛰기):")
    try:
        title = input().strip()
    except (EOFError, KeyboardInterrupt):
        title = ""
    
    # 카테고리 입력 (선택사항)
    print("\n카테고리를 입력하세요 (기본값: dev, Enter로 건너뛰기):")
    try:
        category = input().strip() or "dev"
    except (EOFError, KeyboardInterrupt):
        category = "dev"
    
    print("\n" + "=" * 60)
    print("입력된 정보:")
    print(f"  메모 길이: {len(memo)}자")
    print(f"  제목: {title if title else '(없음)'}")
    print(f"  카테고리: {category}")
    print("=" * 60 + "\n")
    
    # 3-Tier Pipeline 실행
    try:
        result = writer.write_with_3tier_pipeline(
            memo=memo,
            title=title if title else None,
            category=category
        )
        
        if not result:
            print("\n❌ 글 작성 실패")
            sys.exit(1)
        
        # 결과 출력
        print("\n" + "=" * 60)
        print("생성된 글:")
        print("=" * 60)
        print(result)
        print("=" * 60)
        
        # 파일로 저장할지 물어보기
        print("\n파일로 저장하시겠습니까? (y/n):")
        try:
            save = input().strip().lower()
            if save == 'y' or save == 'yes':
                # _posts 디렉토리에 저장
                posts_dir = project_root / '_posts'
                posts_dir.mkdir(exist_ok=True)
                
                # 파일명 생성
                from datetime import datetime
                import re
                now = datetime.now()
                date_str = now.strftime("%Y-%m-%d")
                
                if title:
                    filename = re.sub(r'[^\w\s-]', '', title)
                    filename = re.sub(r'[-\s]+', '-', filename)
                    filename = f"{date_str}-{filename}.md"
                else:
                    filename = f"{date_str}-test-post.md"
                
                filepath = posts_dir / filename
                filepath.write_text(result, encoding='utf-8')
                print(f"\n✅ 파일 저장 완료: {filepath}")
        except (EOFError, KeyboardInterrupt):
            print("\n파일 저장을 건너뜁니다.")
        
        print("\n✅ 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
