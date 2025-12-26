# GitHub OAuth 로그인 구현 가이드

GitHub OAuth를 이용하여 블로그 관리자 로그인을 구현하는 방법을 정리한다. 참고: [GitHub 로그인 구현? 생각보다 너무 쉽다!](https://dev-watnu.tistory.com/58)

## 01. GitHub OAuth App 등록하기

### 1. 설정 메뉴로 이동하기

GitHub에 로그인한 후, **Settings > Developer settings > OAuth Apps**로 이동한다.

직접 링크: https://github.com/settings/developers

### 2. 앱 정보 입력하기

"New OAuth App" 버튼을 클릭하고 다음 정보를 입력한다.

**필수 정보:**
- **Application name**: `Blog Admin Editor` (또는 원하는 이름)
- **Homepage URL**: `https://rldhkstopic.github.io`
- **Application description**: `블로그 포스트 작성 및 관리` (선택 사항)
- **Authorization callback URL**: `https://rldhkstopic.github.io/admin/`

**중요:** Authorization callback URL은 반드시 정확하게 입력해야 한다. GitHub에서 인증 완료 후 이 URL로 리다이렉트된다.

모든 정보를 입력한 뒤 **Register application** 버튼을 클릭하면 앱이 생성된다.

### 3. 앱 생성 완료 확인하기

앱이 성공적으로 생성되면, 다음 정보를 확인할 수 있다.

- **Client ID**: 생성된 앱의 세부 정보에서 바로 확인 가능 (공개 가능)
- **Client Secret**: **Generate a new Client secret** 버튼을 클릭하면 발급 가능 (절대 공개 금지)

⚠️ **보안 주의사항:**
- Client ID는 공개해도 되지만, Client Secret은 절대 외부에 공개하면 안 된다.
- Client Secret이 노출되면 보안 취약점이 발생할 수 있으니, GitHub나 공개 저장소에 업로드하지 않도록 주의한다.
- Client Secret은 서버 사이드에서만 사용한다.

## 02. 로그인 흐름 이해하기

GitHub OAuth 로그인의 기본 흐름은 다음과 같다.

1. **사용자 요청**: 사용자가 "github로 로그인하기" 버튼 클릭
2. **GitHub 인증**: 사용자는 GitHub 인증 화면으로 리다이렉트됨
3. **권한 승인**: 사용자가 GitHub에서 로그인 및 권한 승인
4. **코드 수신**: GitHub이 Authorization callback URL로 리다이렉트하며 `code` 파라미터 전달
5. **토큰 교환**: 서버에서 `code`를 `access_token`으로 교환 (Client Secret 필요)
6. **API 사용**: Access Token을 사용하여 GitHub API에 접근

## 03. _config.yml 설정

생성한 Client ID를 `_config.yml`에 추가한다.

```yaml
admin:
  enabled: true
  github_oauth:
    client_id: "your_client_id_here"  # GitHub OAuth App Client ID
```

⚠️ **주의:** Client Secret은 절대 `_config.yml`에 저장하지 않는다. 서버 사이드에서만 사용한다.

## 04. OAuth 인증 URL 구성

GitHub OAuth 인증 URL은 다음과 같이 구성된다.

```
https://github.com/login/oauth/authorize?
  client_id=${CLIENT_ID}&
  redirect_uri=${REDIRECT_URI}&
  scope=${SCOPE}&
  state=${STATE}
```

**쿼리 매개변수:**

| 매개변수 | 유형 | 설명 | 필수 |
|---------|------|------|------|
| `client_id` | string | GitHub OAuth App의 Client ID | 필수 |
| `redirect_uri` | string | 승인 후 사용자가 리다이렉트될 URL | 강력 추천 |
| `scope` | string | 애플리케이션에서 요청하는 권한 범위 (예: `repo`) | 문맥에 따라 다름 |
| `state` | string | CSRF 공격 방지를 위한 랜덤 문자열 | 강력 추천 |

**권한 범위 (Scope):**
- `repo`: 전체 저장소 접근 (포스트 작성에 필요)
- `user:email`: 사용자 이메일 정보 접근
- `read:user`: 사용자 정보 읽기

## 05. 코드를 Access Token으로 교환하기

### 문제점

GitHub Pages는 정적 사이트이므로 서버 사이드 처리가 불가능하다. `code`를 `access_token`으로 교환하려면 `client_secret`이 필요한데, 이를 클라이언트 사이드에 노출할 수 없다.

### 해결 방법

#### 방법 1: 서버리스 함수 사용 (권장)

Netlify Functions나 Vercel Functions를 사용하여 code를 token으로 교환한다.

**Netlify Functions 예시:**

1. `netlify/functions/github-oauth.js` 파일 생성:

```javascript
exports.handler = async (event, context) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  const { code } = JSON.parse(event.body);
  const clientId = process.env.GITHUB_CLIENT_ID;
  const clientSecret = process.env.GITHUB_CLIENT_SECRET;

  try {
    const response = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        client_id: clientId,
        client_secret: clientSecret,
        code: code
      })
    });

    const data = await response.json();
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify(data)
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
```

2. Netlify 환경 변수 설정:
   - `GITHUB_CLIENT_ID`: OAuth App Client ID
   - `GITHUB_CLIENT_SECRET`: OAuth App Client Secret

#### 방법 2: Personal Access Token 사용 (대체)

서버리스 함수를 설정하지 않는 경우, Personal Access Token을 직접 사용할 수 있다.

1. [GitHub Settings → Personal access tokens](https://github.com/settings/tokens/new)에서 토큰 생성
2. 필요한 권한: `repo` (전체 저장소 접근)
3. 생성된 토큰을 로그인 페이지에서 직접 입력

## 06. 구현 코드

### OAuth 인증 시작

```javascript
function startGitHubOAuth() {
  const clientId = 'your_client_id';
  const redirectUri = 'https://rldhkstopic.github.io/admin/';
  const scope = 'repo';
  const state = generateRandomState(); // CSRF 방지
  
  sessionStorage.setItem('oauth_state', state);
  
  const authUrl = `https://github.com/login/oauth/authorize?` +
    `client_id=${clientId}&` +
    `redirect_uri=${encodeURIComponent(redirectUri)}&` +
    `scope=${scope}&` +
    `state=${state}`;
  
  window.location.href = authUrl;
}
```

### Callback 처리

```javascript
function handleOAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const error = urlParams.get('error');
  
  // 에러 처리
  if (error) {
    console.error('OAuth error:', error);
    return;
  }
  
  // State 검증 (CSRF 방지)
  const savedState = sessionStorage.getItem('oauth_state');
  if (state !== savedState) {
    console.error('State mismatch');
    return;
  }
  
  // Code를 Access Token으로 교환
  if (code) {
    exchangeCodeForToken(code);
  }
}
```

### Code를 Token으로 교환

```javascript
async function exchangeCodeForToken(code) {
  try {
    // 서버리스 함수 호출
    const response = await fetch('/.netlify/functions/github-oauth', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code })
    });
    
    const data = await response.json();
    
    if (data.access_token) {
      // 토큰 저장 및 인증 완료
      saveToken(data.access_token);
      window.location.href = '/editor/';
    }
  } catch (error) {
    console.error('Token exchange failed:', error);
    // 대체 방법 안내
  }
}
```

## 07. 보안 고려사항

### State 파라미터 사용

CSRF 공격을 방지하기 위해 `state` 파라미터를 사용한다. 랜덤 문자열을 생성하여 세션에 저장하고, callback에서 검증한다.

### Client Secret 보호

- Client Secret은 절대 클라이언트 사이드 코드에 포함하지 않는다.
- 환경 변수나 서버 사이드에서만 사용한다.
- 공개 저장소에 업로드하지 않는다.

### HTTPS 사용

프로덕션 환경에서는 반드시 HTTPS를 사용한다. GitHub Pages는 기본적으로 HTTPS를 제공한다.

### 토큰 저장

- Access Token은 브라우저의 로컬스토리지 또는 세션스토리지에 저장한다.
- 공용 컴퓨터에서는 저장하지 않는다.
- 토큰이 유출되면 즉시 GitHub에서 삭제한다.

## 08. 테스트

1. `/admin/` 페이지 접속
2. "github로 로그인하기" 버튼 클릭
3. GitHub 인증 페이지에서 권한 승인
4. Callback 페이지로 리다이렉트
5. Code를 받아서 Token으로 교환
6. 에디터 페이지로 이동

## 09. 문제 해결

### OAuth App이 작동하지 않는 경우

- Client ID가 올바른지 확인
- Authorization callback URL이 정확한지 확인
- OAuth App이 활성화되어 있는지 확인

### Code를 Token으로 교환하지 못하는 경우

- 서버리스 함수가 올바르게 설정되었는지 확인
- 환경 변수(GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET)가 설정되었는지 확인
- 서버리스 함수 로그 확인

### 대체 방법

서버리스 함수를 설정하지 않는 경우, Personal Access Token을 직접 사용할 수 있다. 이 경우 OAuth 플로우를 건너뛰고 토큰 입력 방식으로 로그인한다.

## 참고 자료

- [GitHub OAuth 공식 문서](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
- [GitHub 로그인 구현 가이드](https://dev-watnu.tistory.com/58)
- [OAuth 2.0 스펙](https://oauth.net/2/)

