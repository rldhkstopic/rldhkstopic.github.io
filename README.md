# AI 대화 기록 블로그

GitHub Pages를 사용한 개인 블로그입니다. AI와의 대화 내용을 정리하고 지식을 보존하는 것이 목적입니다.

## 기능

- 📝 마크다운 기반 블로그 포스트 작성
- 🏷️ 태그 시스템
- 📱 반응형 디자인
- 🔍 SEO 최적화
- ⚡ GitHub Pages 자동 배포

## 시작하기

### 1. GitHub 리포지토리 생성

1. GitHub에서 새 리포지토리를 생성합니다
2. 리포지토리 이름을 `yourusername.github.io` 형식으로 설정합니다 (예: `johndoe.github.io`)
3. 이 프로젝트의 모든 파일을 리포지토리에 푸시합니다

### 2. GitHub Pages 활성화

1. 리포지토리 Settings → Pages로 이동
2. Source를 "Deploy from a branch"로 선택
3. Branch를 `main` (또는 `master`)로 선택
4. Save 버튼 클릭

### 3. 설정 파일 수정

`_config.yml` 파일을 열어 다음 내용을 수정하세요:

```yaml
title: "AI 대화 기록 블로그"  # 블로그 제목
description: "AI와의 대화를 정리하고 지식을 보존하는 블로그"  # 설명
author: "Your Name"  # 본인 이름
url: "https://yourusername.github.io"  # GitHub Pages URL
```

### 4. 로컬에서 테스트 (선택사항)

로컬에서 Jekyll을 실행하려면:

```bash
# Ruby와 Bundler 설치 필요
bundle install
bundle exec jekyll serve
```

브라우저에서 `http://localhost:4000`으로 접속하여 확인할 수 있습니다.

## 새 포스트 작성하기

### 방법 1: GitHub 웹 인터페이스

1. `_posts/` 폴더로 이동
2. "Add file" → "Create new file" 클릭
3. 파일명을 `YYYY-MM-DD-제목.md` 형식으로 작성 (예: `2024-01-15-파이썬-기초.md`)
4. 아래 템플릿을 참고하여 작성:

```markdown
---
layout: post
title: "포스트 제목"
date: 2024-01-15
tags: [태그1, 태그2, 태그3]
author: Your Name
---

포스트 내용을 마크다운 형식으로 작성합니다.
```

### 방법 2: 로컬에서 작성 후 푸시

1. `_posts/` 폴더에 새 마크다운 파일 생성
2. 위 템플릿 형식으로 작성
3. Git으로 커밋하고 푸시

## 포스트 작성 팁

### Front Matter (파일 상단)

```yaml
---
layout: post          # 항상 "post"로 설정
title: "제목"         # 포스트 제목
date: 2024-01-15      # 날짜 (YYYY-MM-DD 형식)
tags: [AI, Python]    # 태그 (배열 형식)
author: Your Name     # 작성자 (선택사항)
---
```

### 마크다운 사용법

- **굵게**: `**텍스트**`
- *기울임*: `*텍스트*`
- 코드: `` `코드` ``
- 코드 블록: ` ```언어 `로 감싸기
- 링크: `[텍스트](URL)`
- 이미지: `![대체텍스트](이미지URL)`

## 디렉토리 구조

```
.
├── _config.yml          # Jekyll 설정 파일
├── _layouts/            # 레이아웃 템플릿
│   ├── default.html
│   └── post.html
├── _posts/              # 블로그 포스트 (여기에 작성!)
│   └── YYYY-MM-DD-제목.md
├── assets/              # CSS, JS, 이미지
│   └── css/
│       └── main.css
├── index.html           # 홈페이지
├── blog.html            # 블로그 목록 페이지
├── about.md             # 소개 페이지
├── Gemfile              # Ruby 의존성
└── README.md            # 이 파일
```

## 커스터마이징

### 스타일 변경

`assets/css/main.css` 파일을 수정하여 색상, 폰트, 레이아웃을 변경할 수 있습니다.

### 레이아웃 수정

`_layouts/` 폴더의 HTML 파일을 수정하여 레이아웃을 변경할 수 있습니다.

## 문제 해결

### 포스트가 보이지 않을 때

- 파일명이 `YYYY-MM-DD-제목.md` 형식인지 확인
- Front Matter가 올바른지 확인
- GitHub Pages가 배포되었는지 확인 (Settings → Pages에서 확인)

### 스타일이 적용되지 않을 때

- `_config.yml`의 설정이 올바른지 확인
- 브라우저 캐시를 지우고 다시 로드

## 라이선스

이 프로젝트는 자유롭게 사용하고 수정할 수 있습니다.

## 참고 자료

- [Jekyll 공식 문서](https://jekyllrb.com/docs/)
- [GitHub Pages 가이드](https://pages.github.com/)
- [마크다운 가이드](https://www.markdownguide.org/)

