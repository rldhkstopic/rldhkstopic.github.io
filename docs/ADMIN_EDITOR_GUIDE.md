# 관리자 에디터 사용 가이드

블로그에 내장된 관리자 전용 포스트 에디터 사용 방법을 정리한다.

## 접근 방법

1. **로그인 페이지**: `/admin/` 또는 `/admin.html`
2. **에디터 페이지**: `/editor/` 또는 `/editor.html` (로그인 후 자동 리다이렉트)

## 초기 설정

### 1. GitHub Personal Access Token 생성

1. [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens/new)로 이동
2. "Generate new token (classic)" 클릭
3. 설정:
   - **Note**: "Blog Admin Editor" (또는 원하는 이름)
   - **Expiration**: 원하는 기간 선택 (90일, 1년 등)
   - **Select scopes**: `repo` 체크 (전체 저장소 접근)
4. "Generate token" 클릭
5. 생성된 토큰 복사 (한 번만 표시되므로 안전한 곳에 저장)

### 2. 로그인

1. `/admin/` 페이지 접속
2. GitHub Personal Access Token 입력
3. (선택) 관리자 비밀번호 입력 (추가 보안)
4. "토큰 저장" 체크박스 선택 (선택사항)
5. "로그인" 클릭

## 에디터 사용법

### 기본 기능

**포스트 정보 입력:**
- **제목**: 포스트 제목 (필수)
- **카테고리**: daily/dev/document/study 중 선택 (필수)
- **하위 카테고리**: 선택사항
- **태그**: 쉼표로 구분하여 입력
- **날짜**: 기본값은 현재 날짜/시간

**파일명:**
- 제목과 날짜를 기반으로 자동 생성
- 형식: `YYYY-MM-DD-제목.md`
- 수동 수정 불가 (자동 생성)

### 마크다운 작성

**툴바 단축키:**
- **B**: 굵게 (`**텍스트**`)
- **I**: 기울임 (`*텍스트*`)
- **H**: 제목 (`### 제목`)
- **🔗**: 링크 (`[텍스트](URL)`)
- **</>**: 코드 블록 (```)
- **"**: 인용 (`> 텍스트`)
- **• 목록**: 목록 (`- 항목`)
- **🖼️**: 이미지 (`![alt](URL)`)

**키보드 단축키:**
- `Ctrl+B`: 굵게
- `Ctrl+I`: 기울임
- `Ctrl+K`: 링크 삽입

### 미리보기

"미리보기" 버튼을 클릭하면 작성한 마크다운이 HTML로 렌더링되어 표시된다. 다시 "편집" 버튼을 클릭하면 편집 모드로 돌아간다.

### 저장 및 게시

**임시저장:**
- 브라우저 로컬스토리지에 저장
- GitHub에 업로드되지 않음
- 페이지를 새로고침해도 복원 가능

**게시:**
- GitHub 저장소의 `_posts/` 폴더에 파일 생성/업데이트
- 게시 후 블로그 페이지로 자동 리다이렉트
- 기존 파일이 있으면 업데이트, 없으면 생성

## Front Matter 자동 생성

에디터는 입력한 정보를 바탕으로 Jekyll Front Matter를 자동으로 생성한다:

```yaml
---
layout: post
title: "제목"
date: 2025-12-13 14:30:00 +0900
author: rldhkstopic
category: document
subcategory: "하위 카테고리"  # 선택사항
tags: [태그1, 태그2, 태그3]  # 선택사항
views: 0
---
```

## 보안 주의사항

1. **토큰 관리:**
   - 토큰은 절대 공유하지 마세요
   - 공용 컴퓨터에서는 "토큰 저장"을 사용하지 마세요
   - 토큰이 유출되면 즉시 GitHub에서 삭제하세요

2. **비밀번호 설정 (선택):**
   - `_config.yml`에 `admin_password` 설정 가능
   - SHA-256 해시로 저장 (직접 평문 저장하지 않음)
   - 추가 보안 레이어 제공

3. **로그아웃:**
   - 에디터 페이지에서 "로그아웃" 버튼 클릭
   - 또는 브라우저에서 세션/로컬스토리지 삭제

## 문제 해결

### 토큰 검증 실패

- 토큰이 올바른지 확인
- `repo` 스코프가 있는지 확인
- 토큰이 만료되지 않았는지 확인
- 저장소 접근 권한이 있는지 확인

### 파일 생성 실패

- GitHub API Rate Limit 확인 (시간당 5,000 요청)
- 네트워크 연결 확인
- 브라우저 콘솔에서 에러 메시지 확인

### 미리보기 작동 안 함

- Marked.js 라이브러리가 로드되었는지 확인
- 브라우저 콘솔에서 에러 확인

## 고급 기능

### 기존 포스트 수정

1. GitHub에서 직접 파일을 수정하거나
2. 에디터에서 같은 파일명으로 게시하면 자동으로 업데이트됨

### 다중 포스트 작성

- 여러 탭에서 에디터를 열어 동시에 작성 가능
- 각 탭은 독립적으로 작동

## 참고 자료

- [GitHub Personal Access Tokens 문서](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub REST API 문서](https://docs.github.com/en/rest)
- [Jekyll Front Matter 가이드](https://jekyllrb.com/docs/front-matter/)
- [Markdown 가이드](https://www.markdownguide.org/)


