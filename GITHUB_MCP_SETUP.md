# GitHub MCP 서버 설정 가이드

이 가이드는 Cursor에 GitHub MCP 서버를 추가하는 방법을 설명합니다.

## 사전 준비

1. **Cursor IDE** (최신 버전, v0.48.0 이상 권장)
2. **GitHub Personal Access Token** 생성 필요

## 단계별 설정

### 1단계: GitHub Personal Access Token 생성

1. GitHub에 로그인
2. [Personal Access Tokens 페이지](https://github.com/settings/personal-access-tokens/new)로 이동
3. "Generate new token" → "Generate new token (classic)" 클릭
4. 토큰 이름 입력 (예: "Cursor MCP")
5. 필요한 권한(Scopes) 선택:
   - `repo` (전체 리포지토리 접근)
   - `read:org` (조직 읽기, 선택사항)
6. "Generate token" 클릭
7. **토큰을 복사하여 안전한 곳에 보관** (한 번만 표시됨!)

### 2단계: MCP 설정 파일 생성/수정

Windows에서 Cursor의 글로벌 MCP 설정 파일 경로:
```
C:\Users\rldhkstopic\.cursor\mcp.json
```

**현재 설정 파일에 GitHub MCP 서버를 추가해야 합니다.**

#### 방법 1: 파일 탐색기 사용 (권장)

1. Windows 탐색기 열기
2. 주소창에 `%USERPROFILE%\.cursor` 입력 후 Enter (또는 `C:\Users\rldhkstopic\.cursor`)
3. `mcp.json` 파일 열기
4. 기존 설정에 다음 내용을 추가:

기존 `mcpServers` 객체 안에 다음을 추가:
```json
"github": {
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "Authorization": "Bearer YOUR_GITHUB_PAT"
  }
}
```

**전체 파일 예시** (프로젝트 루트의 `mcp.json.updated` 파일 참고):
- 기존 firecrawl, playwright, pixellab 설정은 그대로 유지
- github 항목만 추가

5. `YOUR_GITHUB_PAT`를 1단계에서 생성한 GitHub Personal Access Token으로 교체
6. JSON 형식이 올바른지 확인 (쉼표, 중괄호 등)
7. 파일 저장

#### 방법 2: Cursor 설정에서 직접 수정

1. Cursor 열기
2. Settings (설정) → Tools & Integrations → MCP tools
3. "github" 옆 연필 아이콘 클릭
4. 위의 JSON 내용 입력 (토큰 포함)
5. 저장

### 3단계: Cursor 재시작

1. Cursor 완전히 종료
2. Cursor 다시 실행

### 4단계: 설치 확인

1. Settings → Tools & Integrations → MCP Tools에서 "github" 옆에 **초록색 점**이 표시되는지 확인
2. 채팅/컴포저에서 "Available Tools" 확인
3. 테스트: "내 GitHub 리포지토리 목록 보여줘"라고 요청

## 문제 해결

### Remote Server 문제

- **Streamable HTTP 작동 안 함**: Cursor v0.48.0 이상인지 확인
- **인증 실패**: PAT에 올바른 권한(scope)이 있는지 확인
- **연결 오류**: 방화벽/프록시 설정 확인

### 일반 문제

- **MCP가 로드되지 않음**: Cursor를 완전히 재시작
- **잘못된 JSON**: JSON 형식이 올바른지 확인
- **도구가 나타나지 않음**: MCP 설정에서 서버에 초록색 점이 있는지 확인
- **로그 확인**: Cursor 로그에서 MCP 관련 오류 확인

## 참고 자료

- [공식 설치 가이드](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-cursor.md)
- [GitHub Personal Access Token 생성](https://github.com/settings/personal-access-tokens/new)

