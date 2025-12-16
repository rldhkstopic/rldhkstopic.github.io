# AGENTS.md

이 문서는 이 블로그 프로젝트에서 작업하는 AI 코딩 에이전트를 위한 컨텍스트와 지침을 제공한다.

## 프로젝트 개요

이 프로젝트는 Jekyll 기반의 정적 블로그 사이트다. GitHub Pages를 통해 자동으로 배포되며, 마크다운 포스트를 작성하여 기술 문서와 분석 글을 게시한다.

**주요 기술 스택:**
- Jekyll (정적 사이트 생성기)
- GitHub Pages (호스팅)
- Liquid 템플릿 엔진
- 커스텀 HTML/CSS 레이아웃

## 개발 환경 설정

### 로컬 서버 실행

1. **의존성 설치:**
```bash
bundle install
```

2. **개발 서버 실행:**
```bash
bundle exec jekyll serve
```

서버는 기본적으로 `http://localhost:4000`에서 실행된다. 변경사항은 자동으로 반영되지만, `_config.yml` 수정 시에는 서버를 재시작해야 한다.

3. **서버 중지:**
터미널에서 `Ctrl + C`를 누른다.

### 빌드 산출물

`_site/` 디렉토리는 Jekyll이 생성한 정적 파일이 저장되는 곳이다. 이 디렉토리는 `.gitignore`에 포함되어 있거나 무시해야 한다. 소스 파일만 버전 관리에 포함된다.

## 프로젝트 구조

```
.
├── _config.yml          # Jekyll 설정 파일
├── _layouts/            # 레이아웃 템플릿
│   ├── default.html     # 기본 레이아웃
│   └── post.html        # 포스트 레이아웃
├── _posts/              # 블로그 포스트 (YYYY-MM-DD-제목.md)
├── assets/
│   ├── css/
│   │   └── main.css     # 메인 스타일시트
│   └── analytics.json   # 방문자 통계 데이터
├── index.html           # 홈페이지
├── blog.html            # 전체 글 목록 페이지
├── daily.html           # Daily 카테고리 페이지
├── dev.html             # Dev 카테고리 페이지
├── document.html        # Document 카테고리 페이지
├── study.html           # Study 카테고리 페이지
├── about.md             # 소개 페이지
├── versions.html        # 버전 업데이트 내역
├── WRITING_STYLE_GUIDE.md  # 글쓰기 스타일 가이드 (필수 참조)
├── POSTS_OVERVIEW.md   # 포스트 종합 요약 파일
└── N8N_AUTOMATION_GUIDE.md # n8n 자동화 가이드
```

## 포스트 작성 규칙

### 파일 생성

새 포스트는 `_posts/` 디렉토리에 다음 형식으로 생성한다:
- 파일명: `YYYY-MM-DD-제목.md`
- 예시: `2025-12-16-FPGA-플래시-메모리와-BRAM-고찰.md`

### Front Matter 필수 필드

모든 포스트는 반드시 다음 필드를 포함해야 한다:

```yaml
---
layout: post
title: "포스트 제목"
date: YYYY-MM-DD
author: rldhkstopic
category: [daily|dev|document|study]
tags: [태그1, 태그2, 태그3]
views: 0
---
```

**카테고리 설명:**
- `daily`: 일상 기록, 실험 로그
- `dev`: 개발 관련 (FPGA, VHDL, 프로그래밍 등)
- `document`: 문서화, 분석 글 (금융, 시장 분석 등)
- `study`: 학습 내용 정리

### 글쓰기 스타일

**반드시 `WRITING_STYLE_GUIDE.md`를 참조하여 작성한다.** 주요 규칙:

1. **어조**: "~다."로 끝나는 건조한 평어체
2. **도입부**: 거창한 정의로 시작하지 말고, 상황/동기 → 액션 → 환경/제약사항 순서
3. **본문**: 소제목은 간결한 명사형, 줄글 우선
4. **결말**: "결론" 섹션 없이 작업 상태나 다음 단계 메모로 마무리
5. **참조**: 외부 자료는 `[^n]` 형식으로 각주 처리, 마지막에 `## References` 섹션 추가
6. **작성자 표기**: Front Matter의 `author` 필드와 본문에 "작성자: {author}" 명시

### 코드 설명 방식

코드가 포함될 경우:
1. 전체 코드 블록 먼저 표시
2. 설명이 필요한 주요 라인만 따로 추출하여 설명
3. 코드 내 주석보다는 본문 텍스트 설명 선호

### POSTS_OVERVIEW.md 업데이트

새 포스트를 작성할 때마다 `POSTS_OVERVIEW.md` 파일도 함께 업데이트한다. 해당 카테고리 섹션에 다음 형식으로 추가:

```markdown
- **YYYY-MM-DD · 포스트 제목**  
  한 줄 요약 설명
```

## 파일 수정 규칙

### CSS 수정

- `assets/css/main.css` 파일을 직접 수정한다
- 인라인 스타일은 피하고, 클래스 기반 스타일을 사용한다
- CSS 변수(`--text-primary`, `--accent-color` 등)를 활용하여 테마 일관성 유지

### 레이아웃 수정

- `_layouts/default.html`: 전체 페이지 레이아웃
- `_layouts/post.html`: 포스트 페이지 레이아웃
- Liquid 템플릿 문법을 사용하여 동적 콘텐츠 생성

### 설정 변경

- `_config.yml` 수정 시 Jekyll 서버 재시작 필요
- `future: true` 설정으로 미래 날짜 포스트도 표시됨

## Git 워크플로우

### 커밋 전 체크리스트

1. **포스트 작성 시:**
   - Front Matter 필수 필드 확인
   - `WRITING_STYLE_GUIDE.md` 규칙 준수 여부 확인
   - `POSTS_OVERVIEW.md` 업데이트
   - 작성자 필드 및 본문 작성자 표기 확인

2. **코드 변경 시:**
   - 로컬에서 `bundle exec jekyll serve`로 빌드 확인
   - CSS 변경사항 브라우저에서 확인
   - 레이아웃 변경사항 여러 페이지에서 확인

### 커밋 메시지 규칙

- 간결하고 명확하게 작성
- 예시: `Add FPGA EEPROM configuration post`, `Update header navigation styles`

### 푸시 프로세스

새 포스트나 변경사항이 있을 때:

```bash
git add .
git commit -m "커밋 메시지"
git pull --rebase origin main  # 원격 변경사항 먼저 반영
git push origin main
```

**중요:** 항상 `git pull --rebase`를 먼저 실행하여 원격 변경사항을 반영한 뒤 푸시한다.

## 자동화 관련

### n8n 자동화

`N8N_AUTOMATION_GUIDE.md` 파일에 n8n을 이용한 자동 포스팅 가이드가 정리되어 있다. 매 시간마다 외부 소스에서 데이터를 수집하여 자동으로 포스트를 생성하는 워크플로우를 구성할 수 있다.

## 테스트 및 검증

### 로컬 빌드 확인

변경사항을 커밋하기 전에 반드시 로컬에서 빌드가 성공하는지 확인한다:

```bash
bundle exec jekyll build
```

빌드 오류가 없고 `_site/` 디렉토리에 정상적으로 파일이 생성되는지 확인한다.

### 브라우저 확인

개발 서버를 실행한 상태에서 다음 페이지들을 확인한다:
- 홈페이지 (`/`)
- 카테고리 페이지 (`/dev/`, `/document/` 등)
- 새로 작성한 포스트 페이지
- 전체 글 목록 (`/blog/`)

### GitHub Pages 배포 확인

푸시 후 GitHub Actions에서 빌드가 성공하는지 확인한다. 빌드 실패 시 Actions 탭에서 에러 로그를 확인한다.

## 주의사항

1. **한글 파일명**: 파일명에 한글이 포함되어도 문제없지만, Git에서 인코딩 이슈가 발생할 수 있으므로 주의한다.

2. **미래 날짜 포스트**: `_config.yml`에 `future: true`가 설정되어 있어 미래 날짜 포스트도 표시된다.

3. **스타일 가이드 준수**: 모든 포스트는 `WRITING_STYLE_GUIDE.md`의 규칙을 엄격히 따라야 한다. 특히 어조, 구조, 참조 형식은 반드시 준수한다.

4. **POSTS_OVERVIEW.md 동기화**: 새 포스트 작성 시 반드시 `POSTS_OVERVIEW.md`도 함께 업데이트한다.

5. **작성자 필드**: 모든 포스트의 Front Matter에 `author: rldhkstopic`을 포함하고, 본문에도 작성자를 명시한다.

## 참고 자료

- [Jekyll 공식 문서](https://jekyllrb.com/docs/)
- [Liquid 템플릿 언어](https://shopify.github.io/liquid/)
- [GitHub Pages 문서](https://docs.github.com/en/pages)
- [AGENTS.md 프로젝트](https://github.com/agentsmd/agents.md)

