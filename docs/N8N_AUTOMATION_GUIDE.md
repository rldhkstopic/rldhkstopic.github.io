# n8n을 이용한 블로그 자동화 가이드라인

이 문서는 n8n 워크플로우를 통해 블로그 포스트를 자동으로 생성하고 GitHub에 푸시하는 프로세스를 정리한다. 매 시간마다 실행되는 스케줄 워크플로우를 구성하는 방법을 단계별로 설명한다.

## 전체 아키텍처 개요

워크플로우는 크게 세 단계로 나뉜다. 첫째, 외부 소스(예: RSS 피드, API, 데이터베이스)에서 새 콘텐츠를 수집한다. 둘째, 수집한 데이터를 Jekyll 포스트 형식의 마크다운으로 변환한다. 셋째, 변환된 파일을 GitHub 저장소에 커밋하고 푸시한다.

이 구조는 소스가 바뀌어도 변환과 푸시 단계는 재사용할 수 있도록 분리되어 있다. 각 단계는 독립적으로 테스트하고 수정할 수 있다.

## 1. n8n 워크플로우 구성

### 기본 워크플로우 구조

```
[Schedule Trigger] → [데이터 수집] → [마크다운 변환] → [GitHub API] → [알림]
```

### Schedule Trigger 설정

n8n의 Schedule Trigger 노드를 사용하여 매 시간마다 워크플로우를 실행한다.

**설정 파라미터:**
- Trigger Interval: `Every Hour`
- Timezone: `Asia/Seoul` (또는 사용자 환경에 맞게)
- Start Time: 워크플로우를 시작할 시간 (예: `00:00`)

이 트리거는 매 시간 정각에 워크플로우를 실행한다. 필요에 따라 `Every 6 Hours`, `Every Day` 등으로 조정할 수 있다.

### 데이터 수집 단계

외부 소스에서 데이터를 가져오는 방법은 소스 타입에 따라 다르다. 몇 가지 일반적인 패턴을 정리한다.

**RSS 피드에서 수집:**
- HTTP Request 노드를 사용하여 RSS 피드 URL을 호출
- XML Parse 노드로 피드 항목 추출
- Filter 노드로 중복 제거 (이미 처리한 항목은 제외)

**API에서 수집:**
- HTTP Request 노드로 API 엔드포인트 호출
- 인증이 필요한 경우 OAuth2 또는 API Key를 Credentials에 저장
- 응답 데이터를 JSON Parse 노드로 파싱

**데이터베이스에서 수집:**
- MySQL, PostgreSQL 등 데이터베이스 노드 사용
- 쿼리로 최근 업데이트된 레코드만 조회
- 타임스탬프 기반으로 중복 처리 방지

수집 단계의 출력은 다음 단계에서 사용할 수 있도록 구조화된 JSON 형식으로 정리한다. 각 항목은 최소한 `title`, `content`, `date`, `category`, `tags` 필드를 포함해야 한다.

### 마크다운 변환 단계

수집한 데이터를 Jekyll 포스트 형식의 마크다운으로 변환한다. Code 노드나 Function 노드를 사용하여 템플릿을 적용한다.

**필수 Front Matter 필드:**
- `layout: post`
- `title`: 포스트 제목
- `date`: YYYY-MM-DD 형식
- `author`: 작성자 (예: `rldhkstopic`)
- `category`: 카테고리 (daily, dev, document, study 중 하나)
- `tags`: 태그 배열

**파일명 규칙:**
- 형식: `YYYY-MM-DD-제목.md`
- 제목에서 특수문자는 하이픈으로 변환
- 한글은 그대로 유지 (UTF-8 인코딩)

**변환 예시 (Code 노드):**

```javascript
const items = $input.all();

return items.map(item => {
  const data = item.json;
  const date = new Date(data.date || Date.now());
  const dateStr = date.toISOString().split('T')[0];
  const titleSlug = data.title
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .toLowerCase();
  
  const frontMatter = `---
layout: post
title: "${data.title}"
date: ${dateStr}
author: rldhkstopic
category: ${data.category || 'daily'}
tags: [${data.tags ? data.tags.map(t => `"${t}"`).join(', ') : ''}]
views: 0
---

${data.content}
`;

  return {
    json: {
      filename: `${dateStr}-${titleSlug}.md`,
      content: frontMatter,
      path: `_posts/${dateStr}-${titleSlug}.md`
    }
  };
});
```

이 코드는 각 입력 항목을 Jekyll 포스트 형식으로 변환하고, 파일명과 경로를 생성한다.

### GitHub API 연동

변환된 마크다운 파일을 GitHub 저장소에 커밋하고 푸시한다. GitHub API 노드를 사용하거나 HTTP Request 노드로 직접 API를 호출할 수 있다.

**필수 설정:**
- Repository: `rldhkstopic/rldhkstopic.github.io`
- Branch: `main`
- Authentication: Personal Access Token (PAT)

**워크플로우:**
1. 기존 파일 존재 여부 확인 (GET `/repos/{owner}/{repo}/contents/{path}`)
2. 파일이 없으면 생성, 있으면 업데이트 (PUT `/repos/{owner}/{repo}/contents/{path}`)
3. 커밋 메시지: `Auto-post: {title}` 형식

**HTTP Request 노드 설정 예시:**

```json
{
  "method": "PUT",
  "url": "https://api.github.com/repos/rldhkstopic/rldhkstopic.github.io/contents/_posts/{{ $json.path }}",
  "authentication": "predefinedCredentialType",
  "nodeCredentialType": "githubApi",
  "sendHeaders": true,
  "headerParameters": {
    "Accept": "application/vnd.github.v3+json"
  },
  "sendBody": true,
  "bodyParameters": {
    "message": "Auto-post: {{ $json.filename }}",
    "content": "{{ $json.content | base64 }}",
    "branch": "main"
  }
}
```

파일이 이미 존재하는 경우, `sha` 파라미터를 추가해야 한다. 따라서 먼저 GET 요청으로 파일 정보를 확인하고, 존재하면 `sha`를 포함하여 업데이트한다.

### 중복 방지 로직

같은 포스트를 여러 번 생성하지 않도록 중복 체크가 필요하다. 몇 가지 방법이 있다.

**방법 1: 파일명 기반 체크**
- GitHub API로 `_posts/` 디렉토리 목록 조회
- 새 파일명이 이미 존재하면 스킵

**방법 2: 제목 해시 기반 체크**
- 제목을 해시하여 별도 메타데이터 파일에 저장
- n8n의 Set 노드나 외부 데이터베이스에 처리된 항목 기록

**방법 3: 날짜+제목 조합 체크**
- 같은 날짜에 같은 제목의 포스트가 있으면 스킵

실제 구현에서는 방법 1과 방법 3을 조합하는 것이 가장 단순하다. GitHub API로 파일 목록을 가져와서, 새 파일명과 비교하여 중복을 걸러낸다.

## 2. 실제 구현 예시: RSS 피드 자동화

RSS 피드를 읽어서 새 항목을 블로그 포스트로 변환하는 완전한 워크플로우 예시를 정리한다.

### 노드 구성

1. **Schedule Trigger**: 매 시간 실행
2. **HTTP Request**: RSS 피드 URL 호출
3. **XML Parse**: RSS XML 파싱
4. **Code**: 마크다운 변환
5. **HTTP Request (GitHub)**: 파일 생성/업데이트
6. **IF**: 에러 체크
7. **Slack/Email**: 알림 (선택)

### RSS 파싱 로직

RSS 피드의 각 항목에서 다음 정보를 추출한다:
- `title`: 제목
- `description` 또는 `content`: 본문
- `pubDate`: 발행일
- `link`: 원본 링크 (References 섹션에 추가)

카테고리는 피드별로 고정하거나, 제목/태그를 분석하여 자동 분류할 수 있다. 자동 분류가 필요한 경우 Code 노드에서 키워드 매칭 로직을 추가한다.

### 에러 처리

GitHub API 호출이 실패할 경우를 대비하여 에러 핸들링을 추가한다. IF 노드로 HTTP 상태 코드를 확인하고, 4xx/5xx 응답이면 알림을 보내거나 재시도 로직을 실행한다.

## 3. 고급 기능

### POSTS_OVERVIEW.md 자동 업데이트

새 포스트가 추가될 때마다 `POSTS_OVERVIEW.md` 파일도 함께 업데이트한다. Code 노드에서 기존 파일 내용을 읽고, 새 항목을 적절한 카테고리 섹션에 추가한다.

### 다중 소스 통합

여러 소스(RSS 피드, API, 데이터베이스)에서 데이터를 수집하여 하나의 워크플로우로 처리할 수 있다. Merge 노드나 Function 노드로 여러 입력을 합치고, 중복을 제거한 뒤 변환 단계로 전달한다.

### 태그 자동 생성

본문 내용을 분석하여 자동으로 태그를 생성할 수 있다. 간단한 키워드 추출부터, 외부 NLP API를 활용한 고급 분류까지 선택할 수 있다.

## 4. 보안 및 모니터링

### GitHub Personal Access Token 관리

n8n의 Credentials에 GitHub PAT를 저장하고, 워크플로우에서만 사용한다. 토큰은 최소 권한 원칙에 따라 `repo` 스코프만 부여한다.

### 워크플로우 실행 로그

n8n의 Execution History에서 각 실행 결과를 확인할 수 있다. 실패한 실행은 자동으로 알림을 보내도록 설정한다.

### Rate Limit 고려

GitHub API는 시간당 요청 수에 제한이 있다. 여러 포스트를 한 번에 처리할 경우, HTTP Request 노드 사이에 Delay 노드를 추가하여 Rate Limit을 피한다.

## 5. 테스트 및 디버깅

### 로컬 테스트

n8n을 로컬에서 실행하여 워크플로우를 테스트한다. Schedule Trigger 대신 Manual Trigger를 사용하여 즉시 실행할 수 있다.

### 스테이징 브랜치 활용

프로덕션 브랜치(`main`)에 직접 푸시하기 전에, 스테이징 브랜치(예: `auto-posts`)에 먼저 푸시하여 검증한다. 검증이 완료되면 수동으로 `main`으로 머지한다.

### 로그 확인

각 노드의 출력 데이터를 확인하여 변환 결과가 올바른지 검증한다. 특히 마크다운 변환 단계와 GitHub API 호출 단계의 출력을 자세히 확인한다.

## 6. 배포 및 운영

### n8n 클라우드 vs Self-hosted

n8n 클라우드를 사용하면 별도의 서버 관리 없이 워크플로우를 실행할 수 있다. Self-hosted 버전은 더 많은 제어권을 제공하지만, 서버 관리 부담이 있다.

### 백업 및 복구

워크플로우 설정을 정기적으로 내보내기(Export)하여 백업한다. 문제가 발생하면 백업에서 복구할 수 있다.

### 모니터링 알림

워크플로우 실행 실패 시 Slack, Email, Discord 등으로 알림을 보내도록 설정한다. 정상 실행 시에도 요약 리포트를 주기적으로 받을 수 있다.

## 참고 자료

- [n8n 공식 문서](https://docs.n8n.io/)
- [GitHub REST API 문서](https://docs.github.com/en/rest)
- [Jekyll Front Matter 가이드](https://jekyllrb.com/docs/front-matter/)

