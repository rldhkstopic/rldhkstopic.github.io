# GitHub OAuth 설정 가이드

블로그에 GitHub OAuth 로그인을 설정하는 방법을 설명한다.

## GitHub OAuth App 생성

1. [GitHub Settings → Developer settings → OAuth Apps](https://github.com/settings/developers)로 이동
2. "New OAuth App" 클릭
3. 설정 입력:
   - **Application name**: "Blog Admin Editor" (또는 원하는 이름)
   - **Homepage URL**: `https://rldhkstopic.github.io`
   - **Authorization callback URL**: `https://rldhkstopic.github.io/admin/`
4. "Register application" 클릭
5. 생성된 **Client ID** 복사

## _config.yml 설정

`_config.yml` 파일에 Client ID 추가:

```yaml
admin:
  enabled: true
  github_oauth:
    client_id: "your_client_id_here"
```

## 서버리스 함수 설정 (선택사항)

OAuth code를 access token으로 자동 교환하려면 서버리스 함수가 필요하다.

### Netlify Functions 사용

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

3. `oauth.js`에서 함수 URL 수정:
```javascript
const exchangeUrl = '/.netlify/functions/github-oauth';
```

### Vercel Functions 사용

1. `api/github-oauth.js` 파일 생성 (위와 동일한 코드)
2. Vercel 환경 변수 설정
3. `oauth.js`에서 함수 URL 수정:
```javascript
const exchangeUrl = '/api/github-oauth';
```

## 서버리스 함수 없이 사용

서버리스 함수가 없는 경우:
- OAuth 인증 후 Personal Access Token 생성 페이지로 안내
- 또는 수동으로 Personal Access Token 입력

## 보안 주의사항

1. **Client Secret**: 절대 클라이언트 사이드 코드에 포함하지 마세요
2. **환경 변수**: 서버리스 함수에서만 Client Secret 사용
3. **HTTPS**: 프로덕션에서는 반드시 HTTPS 사용

## 테스트

1. `/admin/` 페이지 접속
2. "GitHub로 로그인" 버튼 클릭
3. GitHub 인증 페이지에서 권한 승인
4. Callback으로 돌아와서 자동 로그인 확인

