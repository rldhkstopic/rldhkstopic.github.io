# GitHub OAuth Callback URL 수정 가이드

현재 GitHub OAuth App의 Callback URL이 `/oauth/github/callback`으로 설정되어 있지만, 프로젝트 코드는 `/admin/`으로 리다이렉트하도록 설정되어 있다.

## 해결 방법

### 옵션 1: GitHub OAuth App Callback URL 변경 (권장)

1. [GitHub Settings → Developer settings → OAuth Apps](https://github.com/settings/developers) 접속
2. 생성한 OAuth App (`rldhkstopic`) 클릭
3. **Authorization callback URL** 필드 수정:
   ```
   https://rldhkstopic.github.io/admin/
   ```
4. **Update application** 버튼 클릭

**Vercel 배포를 사용하는 경우:**
- Vercel 도메인도 추가:
  ```
  https://your-project.vercel.app/admin/
  ```
- 또는 Vercel 도메인만 사용:
  ```
  https://your-project.vercel.app/admin/
  ```

### 옵션 2: 코드 수정 (고급)

현재 Callback URL을 유지하려면 코드를 수정해야 한다:

1. `assets/js/oauth.js`의 `redirectUri` 변경
2. `/oauth/github/callback` 경로를 처리하는 페이지 생성
3. 해당 페이지에서 OAuth callback 처리

**권장:** 옵션 1이 더 간단하고 현재 코드와 일치한다.

## 현재 설정 확인

- **Client ID:** `Ov23lisMUemA9EpUyk3Q` (이미 `_config.yml`에 추가됨)
- **Callback URL:** `/admin/`으로 변경 필요
- **Vercel 환경 변수:** `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` 설정 필요

## 다음 단계

1. GitHub OAuth App의 Callback URL을 `/admin/`으로 변경
2. Vercel 환경 변수 설정 (Client Secret 포함)
3. 배포 후 테스트

