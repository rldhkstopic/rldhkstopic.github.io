# 서버리스 함수 설정 가이드

GitHub OAuth code를 access token으로 교환하기 위한 서버리스 함수 설정 방법을 정리한다.

## Netlify Functions 설정

### 1. 함수 파일 생성

프로젝트 루트에 `netlify/functions/github-oauth.js` 파일을 생성한다. (이미 생성됨)

### 2. Netlify 환경 변수 설정

1. Netlify 대시보드에 로그인
2. 프로젝트 선택 → **Site settings** → **Environment variables**
3. 다음 변수 추가:
   - `GITHUB_CLIENT_ID`: GitHub OAuth App의 Client ID
   - `GITHUB_CLIENT_SECRET`: GitHub OAuth App의 Client Secret

### 3. 배포

Netlify에 배포하면 자동으로 함수가 활성화된다.

**함수 엔드포인트:** `https://your-site.netlify.app/.netlify/functions/github-oauth`

## Vercel Functions 설정

### 1. 함수 파일 생성

프로젝트 루트에 `api/github-oauth.js` 파일을 생성한다. (이미 생성됨)

### 2. Vercel 환경 변수 설정

1. Vercel 대시보드에 로그인
2. 프로젝트 선택 → **Settings** → **Environment Variables**
3. 다음 변수 추가:
   - `GITHUB_CLIENT_ID`: GitHub OAuth App의 Client ID
   - `GITHUB_CLIENT_SECRET`: GitHub OAuth App의 Client Secret

### 3. 배포

Vercel에 배포하면 자동으로 함수가 활성화된다.

**함수 엔드포인트:** `https://your-site.vercel.app/api/github-oauth`

## GitHub Pages에서 사용

GitHub Pages는 서버리스 함수를 직접 지원하지 않는다. 다음 방법 중 하나를 선택한다.

### 방법 1: Netlify로 배포

1. GitHub 저장소를 Netlify에 연결
2. Netlify Functions 설정
3. Netlify 도메인 사용 또는 GitHub Pages와 동기화

### 방법 2: Vercel로 배포

1. GitHub 저장소를 Vercel에 연결
2. Vercel Functions 설정
3. Vercel 도메인 사용

### 방법 3: 별도 API 서버

별도의 서버를 운영하여 OAuth 토큰 교환을 처리한다.

### 방법 4: Personal Access Token 사용

서버리스 함수 없이 Personal Access Token을 직접 사용한다. (현재 구현된 방식)

## 테스트

서버리스 함수가 제대로 작동하는지 테스트:

```bash
curl -X POST https://your-site.netlify.app/.netlify/functions/github-oauth \
  -H "Content-Type: application/json" \
  -d '{"code":"test_code"}'
```

## 보안 주의사항

1. **Client Secret 보호**: 절대 클라이언트 사이드에 노출하지 않는다.
2. **환경 변수**: 서버리스 플랫폼의 환경 변수 기능을 사용한다.
3. **HTTPS**: 프로덕션에서는 반드시 HTTPS를 사용한다.
4. **CORS**: 필요한 경우 CORS 설정을 제한한다.

## 참고 자료

- [Netlify Functions 문서](https://docs.netlify.com/functions/overview/)
- [Vercel Functions 문서](https://vercel.com/docs/functions)
- [GitHub OAuth 문서](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)

