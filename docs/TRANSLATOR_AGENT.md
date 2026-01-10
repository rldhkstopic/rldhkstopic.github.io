# TranslatorAgent 문서

자동 번역 에이전트 (TranslatorAgent)는 한글 블로그 포스트를 영어로 자동 번역하여 다국어 블로그를 지원합니다.

## 개요

**파일 위치**: `.github/scripts/agents/translator.py`

**주요 기능**:
- 한글 마크다운 포스트를 영어로 번역
- Front Matter 자동 수정 (title, description, lang, ref)
- 카테고리/태그 영어 매핑
- 코드 블록 보존 (번역하지 않음)
- 기술 용어 유지 (VHDL, FPGA, Vivado 등)

## 클래스 구조

### TranslatorAgent

#### 초기화

```python
translator_agent = TranslatorAgent(api_key=gemini_key)
```

**매개변수**:
- `api_key` (str): Google Gemini API 키

**특징**:
- 모델 폴백 체인 지원 (gemini-2.5-flash → gemini-2.0-flash → ...)
- 카테고리/태그 영어 매핑 테이블 내장

#### 주요 메서드

##### `translate_post(korean_post_path: Path, ref_id: str) -> Optional[Dict]`

한글 마크다운 포스트를 영어로 번역합니다.

**매개변수**:
- `korean_post_path` (Path): 한글 포스트 파일 경로
- `ref_id` (str): 한글/영문 글을 연결하는 고유 ID

**반환값**:
- `Dict`: 번역된 콘텐츠 딕셔너리
  - `title`: 영어 제목
  - `content`: 영어 본문
  - `front_matter`: 영어 Front Matter 딕셔너리
  - `category`: 영어 카테고리
  - `tags`: 영어 태그 리스트
  - `date`: 날짜
  - `author`: 작성자
- `None`: 번역 실패 시

**작동 과정**:
1. 한글 포스트 파일 읽기
2. Front Matter와 본문 분리
3. Gemini API로 번역 요청
4. 번역된 텍스트 파싱
5. 영어 Front Matter 생성
6. 번역된 콘텐츠 반환

### 유틸리티 함수

#### `generate_ref_id(post_path: Path) -> str`

포스트 파일명에서 고유 ref ID를 생성합니다.

**매개변수**:
- `post_path` (Path): 포스트 파일 경로

**반환값**:
- `str`: `post-{12자리 해시}` 형식의 고유 ID

**예시**:
```python
ref_id = generate_ref_id(Path("_posts/2026-01-10-title.md"))
# 반환: "post-abc123def456"
```

## 사용 예시

### auto_post.py에서 사용

```python
from agents.translator import TranslatorAgent, generate_ref_id

# 번역 기능 활성화 확인
if os.getenv("ENABLE_TRANSLATION", "false").lower() == "true":
    translator_agent = TranslatorAgent(api_key=gemini_key)
    korean_post_path = project_root / post_path
    ref_id = generate_ref_id(korean_post_path)
    
    # 한글 포스트에 ref 추가
    _add_ref_to_post(korean_post_path, ref_id)
    
    # 영어 번역 생성
    translated_content = translator_agent.translate_post(korean_post_path, ref_id)
    if translated_content:
        # 영어 포스트 저장
        english_post_path = _create_english_post(
            translated_content, 
            korean_post_path, 
            ref_id, 
            post_creator
        )
```

### daily_diary_agent.py에서 사용

일기 생성 시에도 동일한 방식으로 번역 기능을 사용할 수 있습니다.

## 번역 프롬프트

TranslatorAgent는 다음 지침을 따라 번역합니다:

1. **코드 블록 보존**: 모든 코드 블록 (```...```)과 인라인 코드 (`...`)는 번역하지 않음
2. **기술 용어 유지**: VHDL, FPGA, Vivado, BRAM 등 표준 영어 기술 용어는 그대로 유지
3. **마크다운 형식 유지**: 헤더, 리스트, 링크 등 마크다운 형식 보존
4. **자연스러운 영어**: 기술 블로그에 적합한 전문적이고 자연스러운 영어 사용

## 카테고리/태그 매핑

### 카테고리 매핑

```python
category_map = {
    'dev': 'dev',
    'study': 'study',
    'daily': 'daily',
    'document': 'document',
}
```

### 태그 매핑

```python
tag_map = {
    'VHDL': 'VHDL',
    'FPGA': 'FPGA',
    'Vivado': 'Vivado',
    'Synthesis': 'Synthesis',
    '오류': 'Error',
    '문법': 'Syntax',
    '레퍼런스': 'Reference',
    '설계': 'Design',
    '아키텍처': 'Architecture',
    '회고': 'Retrospective',
    '일상': 'Daily Life',
    '일기': 'Diary',
}
```

매핑되지 않은 한글 태그는 Gemini API를 사용하여 자동으로 번역을 시도합니다.

## Front Matter 처리

### 한글 포스트 Front Matter

```yaml
---
layout: post
title: "포스트 제목"
date: 2026-01-10 12:00:00 +0900
author: rldhkstopic
category: document
tags: [태그1, 태그2]
ref: post-abc123def456  # 자동 추가
views: 0
---
```

### 영어 포스트 Front Matter (자동 생성)

```yaml
---
layout: post
title: "Post Title"
date: 2026-01-10 12:00:00 +0900
author: rldhkstopic
category: document
tags: [Tag1, Tag2]
lang: en  # 자동 추가
ref: post-abc123def456  # 한글 버전과 동일
views: 0
---
```

## 파일 저장 구조

### 한글 포스트
- 경로: `_posts/YYYY-MM-DD-title.md`
- 예시: `_posts/2026-01-10-블룸버그-뉴스-다이제스트.md`

### 영어 포스트
- 경로: `_posts/en/YYYY-MM-DD-title-en.md`
- 예시: `_posts/en/2026-01-10-bloomberg-news-digest-en.md`

## 에러 처리

TranslatorAgent는 다음과 같은 경우 `None`을 반환합니다:

1. Front Matter를 찾을 수 없는 경우
2. Gemini API 응답이 비어있는 경우
3. 번역 중 예외가 발생한 경우

에러가 발생해도 한글 포스트 생성은 계속 진행되며, 번역 실패는 경고 메시지로만 표시됩니다.

## 환경 변수

### 필수
- `GEMINI_API_KEY`: Google Gemini API 키

### 선택
- `ENABLE_TRANSLATION`: `"true"`로 설정 시 번역 기능 활성화 (기본값: `"false"`)
- `GEMINI_TRANSLATOR_MODEL`: 사용할 Gemini 모델 지정 (기본값: 자동 선택)

## 모델 폴백 체인

TranslatorAgent는 다음 순서로 모델을 시도합니다:

1. `GEMINI_TRANSLATOR_MODEL` 환경 변수에 지정된 모델
2. `models/gemini-2.5-flash`
3. `models/gemini-2.0-flash-exp`
4. `models/gemini-2.0-flash`
5. `models/gemini-flash-latest`

첫 번째로 사용 가능한 모델을 선택합니다.

## 통합된 워크플로우

TranslatorAgent는 다음 워크플로우에 통합되어 있습니다:

1. **auto-post.yml**: 자동 포스트 생성 시 번역
2. **daily-diary.yml**: 일기 생성 시 번역

두 워크플로우 모두 `ENABLE_TRANSLATION: "true"` 환경 변수가 설정되어 있습니다.

## 향후 개선 사항

- [ ] 번역 품질 개선을 위한 프롬프트 최적화
- [ ] 다른 언어 지원 (일본어, 중국어 등)
- [ ] 번역 캐싱 (같은 내용 재번역 방지)
- [ ] 번역 품질 검증 로직 추가
