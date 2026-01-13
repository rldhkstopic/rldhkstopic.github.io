#!/usr/bin/env python3
"""
GitHub Pages 블로그 포스트 자동 생성 스크립트
Google Gemini API를 사용하여 3단계 연쇄 호출로 고품질 블로그 글 생성
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Gemini API 키 확인 및 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ 오류: GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# 모델 설정
MODEL_NAME = "gemini-1.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

# 프로젝트 경로 설정
PROJECT_ROOT = Path(__file__).parent
POSTS_DIR = PROJECT_ROOT / "_posts"


def step1_drafter(topic: str) -> str:
    """
    Step 1: 구성 작가 (The Drafter)
    입력받은 메모를 바탕으로 논리적인 글의 뼈대와 초안 작성
    """
    system_instruction = """너는 구성 작가야. 팩트와 정보 전달 위주로 서론-본론-결론 구조를 잡아줘.
다음 원칙을 지켜줘:
- 거창한 정의로 시작하지 말고, 상황/동기 -> 액션 -> 환경/제약사항 순서로 작성
- 소제목은 간결한 명사형으로 작성 (### 레벨 사용)
- 줄글(Paragraph) 우선, 번호 매기기 리스트는 최소화
- "~다."로 끝나는 건조한 평어체 사용
- 감정적 형용사("매우", "획기적인", "놀라운") 사용 금지
- 이모지 사용 금지
- "안녕하세요", "반갑습니다", "오늘은 ~를 알아보겠습니다" 같은 인사 멘트 삭제
- "결론적으로", "요약하자면", "마지막으로" 같은 접속사 생략
- Front Matter는 작성하지 말고 본문만 작성해줘"""

    prompt = f"""다음 주제나 메모를 바탕으로 기술 블로그 글의 초안을 작성해줘:

주제/메모:
{topic}

위 주제를 바탕으로 논리적이고 구조화된 블로그 글 초안을 작성해줘. 팩트와 정보 전달에 집중하고, 서론-본론-결론 구조를 명확히 해줘."""

    try:
        print("📝 Step 1: 구성 작가가 글의 뼈대를 작성 중...")
        response = model.generate_content(
            f"{system_instruction}\n\n{prompt}",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        draft = response.text
        print("✅ Step 1 완료")
        return draft
    except Exception as e:
        print(f"❌ Step 1 오류: {e}")
        sys.exit(1)


def step2_persona(draft: str) -> str:
    """
    Step 2: 페르소나 에디터 (The Persona)
    Step 1의 글을 특정 말투로 리라이팅
    """
    system_instruction = """너는 10년 차 임베디드 시스템 엔지니어이자 시니컬한 기술 블로거다.

다음 규칙을 엄격히 지켜줘:
- 절대 '습니다/합니다' 체를 쓰지 마. '음/함' 체나 자연스러운 구어체를 섞어 써.
  예: "이건 좀 아닌 듯.", "결국 해결함.", "이렇게 하면 됨."
- "소개합니다", "알아보겠습니다", "설명드리겠습니다" 같은 전형적인 블로그 멘트 완전 삭제
- 개발자의 '냉소적인 위트'를 섞어서 문장 호흡을 짧게 끊어쳐
- "~다."로 끝나는 건조한 평어체를 기본으로 하되, 구어체를 자연스럽게 섞어줘
- 감정 배제, 이모지 금지
- 기술적 정확성은 유지하면서 말투만 바꿔줘
- Front Matter는 그대로 유지해줘"""

    prompt = f"""다음 초안을 위의 페르소나로 리라이팅해줘. 말투만 바꾸고 내용의 논리 구조와 기술적 정보는 그대로 유지해줘:

초안:
{draft}"""

    try:
        print("✏️  Step 2: 페르소나 에디터가 말투를 적용 중...")
        response = model.generate_content(
            f"{system_instruction}\n\n{prompt}",
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        rewritten = response.text
        print("✅ Step 2 완료")
        return rewritten
    except Exception as e:
        print(f"❌ Step 2 오류: {e}")
        sys.exit(1)


def step3_polisher(content: str, topic: str) -> str:
    """
    Step 3: 교정 및 포맷팅 (The Polisher)
    최종 문법 검수 및 Jekyll Front Matter 추가
    """
    system_instruction = """너는 최종 교정 및 포맷팅 전문가야.

다음 작업을 수행해줘:
1. Jekyll Front Matter를 상단에 추가:
   - layout: post
   - title: "제목" (따옴표 필수)
   - date: YYYY-MM-DD HH:MM:SS +0900 (오늘 날짜, 한국 시간대)
   - author: rldhkstopic
   - category: dev (또는 daily/document/study, 내용에 맞게 판단)
   - tags: [태그1, 태그2, 태그3] (3~7개, 내용에 맞는 태그 추천)
   - views: 0

2. 현업 개발 용어로 단어 교정
3. 마크다운 포맷 정리 (코드 블록, H2/H3 헤딩, 리스트 등)
4. 문법 및 맞춤법 검수
5. 전체적인 가독성 향상

Front Matter와 본문 사이에 빈 줄 하나를 두고, 본문은 그대로 유지해줘."""

    # 오늘 날짜 생성
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d %H:%M:%S +0900")

    prompt = f"""다음 글에 Jekyll Front Matter를 추가하고 최종 교정을 해줘:

원본 글:
{content}

주제: {topic}

오늘 날짜: {date_str}

위 정보를 바탕으로 Front Matter를 생성하고, 본문을 교정해줘. 카테고리와 태그는 내용에 맞게 추천해줘."""

    try:
        print("✨ Step 3: 교정 및 포맷팅 중...")
        response = model.generate_content(
            f"{system_instruction}\n\n{prompt}",
            generation_config={
                "temperature": 0.5,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        polished = response.text
        print("✅ Step 3 완료")
        return polished
    except Exception as e:
        print(f"❌ Step 3 오류: {e}")
        sys.exit(1)


def extract_filename_from_content(content: str, topic: str) -> str:
    """
    Front Matter에서 title을 추출하거나 주제에서 파일명 생성
    """
    # Front Matter에서 title 추출 시도
    title_match = re.search(r'title:\s*"([^"]+)"', content)
    if title_match:
        title = title_match.group(1)
    else:
        # title이 없으면 주제에서 추출
        title = topic[:50]  # 최대 50자

    # 한글을 영문으로 변환 (간단한 키워드 추출)
    # 실제로는 Gemini에게 파일명 추천을 받는 것이 좋지만, 여기서는 간단히 처리
    filename_keywords = re.sub(r'[^\w\s-]', '', title)
    filename_keywords = re.sub(r'\s+', '-', filename_keywords)
    filename_keywords = filename_keywords.lower()

    # 날짜 추가
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    
    filename = f"{date_str}-{filename_keywords}.md"
    
    # 파일명이 너무 길면 자르기
    if len(filename) > 100:
        filename = f"{date_str}-{filename_keywords[:80]}.md"
    
    return filename


def save_post(content: str, filename: str) -> Path:
    """
    포스트를 _posts 디렉토리에 저장
    """
    # _posts 디렉토리 확인 및 생성
    POSTS_DIR.mkdir(exist_ok=True)
    
    filepath = POSTS_DIR / filename
    
    # 파일이 이미 존재하면 번호 추가
    counter = 1
    original_filepath = filepath
    while filepath.exists():
        name_part = original_filepath.stem
        filepath = POSTS_DIR / f"{name_part}-{counter}.md"
        counter += 1
    
    # 파일 저장
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filepath


def main():
    """
    메인 실행 함수
    """
    print("=" * 60)
    print("🚀 GitHub Pages 블로그 포스트 자동 생성기")
    print("=" * 60)
    print()
    
    # 사용자 입력 받기
    print("📝 주제나 메모를 입력해주세요 (여러 줄 입력 가능, 빈 줄 입력 시 종료):")
    print("   (Ctrl+Z + Enter 또는 Ctrl+D로 입력 종료)")
    print()
    
    lines = []
    try:
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
    except EOFError:
        pass
    
    if not lines:
        print("❌ 입력이 없습니다. 프로그램을 종료합니다.")
        sys.exit(1)
    
    topic = "\n".join(lines)
    print()
    print(f"📌 입력된 주제/메모:")
    print("-" * 60)
    print(topic)
    print("-" * 60)
    print()
    
    # 3단계 연쇄 호출
    draft = step1_drafter(topic)
    rewritten = step2_persona(draft)
    final_content = step3_polisher(rewritten, topic)
    
    # 파일명 생성
    filename = extract_filename_from_content(final_content, topic)
    
    # 파일 저장
    filepath = save_post(final_content, filename)
    
    print()
    print("=" * 60)
    print("✅ 포스트 생성 완료!")
    print("=" * 60)
    print(f"📁 저장 위치: {filepath}")
    print()
    print("💡 다음 단계:")
    print("   1. 생성된 파일을 확인하고 필요시 수정하세요")
    print("   2. git add, commit, push로 GitHub에 업로드하세요")
    print("   3. GitHub Pages가 자동으로 빌드하여 블로그에 반영합니다")
    print()


if __name__ == "__main__":
    main()
