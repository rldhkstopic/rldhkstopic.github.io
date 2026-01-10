# 다국어 블로그 설정 가이드

블로그의 자동 영문 번역 기능과 다국어 지원 설정 방법입니다.

## 개요

이 블로그는 한글 포스트를 자동으로 영어로 번역하여 다국어 블로그를 지원합니다.

### 주요 기능

1. **자동 번역**: 한글 포스트 생성 시 자동으로 영어 버전 생성
2. **SEO 최적화**: hreflang 태그로 검색 엔진에 언어별 페이지 정보 제공
3. **언어 선택 버튼**: 포스트 페이지에서 다른 언어 버전으로 쉽게 전환
4. **필터링**: 메인 페이지는 한국어 글만 표시, 영어 글은 `/en/` 페이지에서 확인

## 구조

### 파일 구조

```
_posts/
├── YYYY-MM-DD-title.md          # 한글 포스트 (기본)
└── en/
    └── YYYY-MM-DD-title-en.md   # 영어 포스트 (자동 생성)
```

### Front Matter 속성

#### 한글 포스트
```yaml
---
layout: post
title: "포스트 제목"
date: 2026-01-10 12:00:00 +0900
author: rldhkstopic
category: document
tags: [태그1, 태그2]
lang: ko  # 기본값 (생략 가능)
ref: post-abc123def456  # 영어 버전과 연결하는 고유 ID
views: 0
---
```

#### 영어 포스트
```yaml
---
layout: post
title: "Post Title"
date: 2026-01-10 12:00:00 +0900
author: rldhkstopic
category: document
tags: [Tag1, Tag2]
lang: en  # 영어 표시
ref: post-abc123def456  # 한글 버전과 동일한 ref 값
views: 0
---
```

## 번역 기능 활성화

### GitHub Actions 워크플로우

번역 기능은 이미 워크플로우에 활성화되어 있습니다:

- `auto-post.yml`: 자동 포스트 생성 시 번역
- `daily-diary.yml`: 일기 생성 시 번역

환경 변수 `ENABLE_TRANSLATION: "true"`가 설정되어 있으면 자동으로 영어 번역이 생성됩니다.

### 수동으로 번역 비활성화

번역을 일시적으로 비활성화하려면 워크플로우 파일에서 다음 줄을 주석 처리하거나 제거:

```yaml
ENABLE_TRANSLATION: "true"  # 이 줄 제거 또는 주석 처리
```

## 사용자 경험

### 메인 페이지 (`/`)

- 기본적으로 한국어 글만 표시 (`lang != 'en'` 필터 적용)
- 상단에 "English Blog" 링크로 영어 글 페이지로 이동

### 영어 블로그 페이지 (`/en/`)

- 영어 글만 모아서 표시
- 상단에 "한국어 블로그" 링크로 메인 페이지로 이동

### 포스트 페이지

- 포스트 제목 옆에 언어 선택 버튼 표시
  - 한국어 포스트: "Read in English" 버튼
  - 영어 포스트: "한국어로 읽기" 버튼
- 같은 `ref` 값을 가진 다른 언어 버전으로 이동

## SEO 최적화

### hreflang 태그

각 포스트의 `<head>` 섹션에 자동으로 hreflang 태그가 추가됩니다:

```html
<link rel="alternate" hreflang="ko" href="https://rldhkstopic.github.io/.../korean-post.html">
<link rel="alternate" hreflang="en" href="https://rldhkstopic.github.io/.../english-post.html">
```

이 태그는 검색 엔진에게 같은 내용의 다른 언어 버전이 있다는 것을 알려줍니다.

## 번역 품질

### 번역 에이전트 (TranslatorAgent)

- **모델**: Google Gemini 2.5 Flash (폴백 체인 지원)
- **특징**:
  - 코드 블록 보존 (번역하지 않음)
  - 기술 용어 유지 (VHDL, FPGA, Vivado 등)
  - 마크다운 형식 유지
  - 자연스러운 영어 문체

### 카테고리/태그 매핑

일부 카테고리와 태그는 자동으로 영어로 매핑됩니다:

- `dev` → `dev`
- `study` → `study`
- `daily` → `daily`
- `document` → `document`
- `VHDL` → `VHDL`
- `FPGA` → `FPGA`
- `오류` → `Error`
- `문법` → `Syntax`
- `레퍼런스` → `Reference`

## 문제 해결

### 번역이 생성되지 않는 경우

1. **환경 변수 확인**
   - `ENABLE_TRANSLATION: "true"`가 워크플로우에 설정되어 있는지 확인
   - `GEMINI_API_KEY`가 GitHub Secrets에 설정되어 있는지 확인

2. **로그 확인**
   - GitHub Actions 로그에서 "[7단계] 영어 번역 생성 중..." 메시지 확인
   - 오류 메시지가 있으면 확인

3. **파일 확인**
   - `_posts/en/` 디렉토리에 영어 포스트가 생성되었는지 확인

### 번역 품질이 낮은 경우

- 번역 프롬프트는 `.github/scripts/agents/translator.py`에 정의되어 있습니다
- 필요시 프롬프트를 수정하여 번역 품질을 개선할 수 있습니다

## 향후 확장

현재는 한국어/영어만 지원하지만, 향후 다른 언어를 추가할 수 있습니다:

1. `TranslatorAgent`에 다른 언어 지원 추가
2. `_posts/` 하위에 해당 언어 디렉토리 생성 (예: `_posts/ja/` 일본어)
3. 언어 선택 버튼 로직 확장
4. hreflang 태그에 해당 언어 추가
