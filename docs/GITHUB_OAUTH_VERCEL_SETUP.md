# GitHub OAuth 설정 가이드 (Vercel 배포용)

Vercel에 배포된 블로그에 GitHub OAuth 로그인을 설정하는 방법이다.

## 1. GitHub OAuth App 생성

### 단계 1: GitHub Developer Settings 접속

1. GitHub에 로그인
2. 우측 상단 프로필 아이콘 클릭 → **Settings**
3. 왼쪽 사이드바에서 **Developer settings** 클릭
4. **OAuth Apps** 클릭

**직접 링크:** https://github.com/settings/developers

### 단계 2: 새 OAuth App 생성

1. **New OAuth App** 버튼 클릭

2. 다음 정보 입력:

   **Application name:**
   ```
   Blog Admin Editor
   ```
   (원하는 이름으로 변경 가능)

   **Homepage URL:**
   ```
   https://your-project.vercel.app
   ```
   또는 커스텀 도메인 사용 시:
   ```
   https://your-custom-domain.com
   ```

   **Application description (선택사항):**
   ```
   블로그 포스트 작성 및 관리
   ```

   **Authorization callback URL:**
   ```
   https://your-project.vercel.app/admin/
   ```
   또는 커스텀 도메인 사용 시:
   ```
   https://your-custom-domain.com/admin/
   ```

   ⚠️ **중요:** 
   - Callback URL은 반드시 `/admin/`으로 끝나야 한다
   - Vercel 도메인을 사용하는 경우: `https://your-project.vercel.app/admin/`
   - GitHub Pages와 동시 사용 시: `https://rldhkstopic.github.io/admin/`도 추가 가능

3. **Register application** 버튼 클릭

### 단계 3: Client ID와 Client Secret 확인

앱이 생성되면 다음 정보를 확인할 수 있다:

1. **Client ID**
   - 페이지 상단에 표시됨
   - 복사하여 저장 (공개 가능)

2. **Client Secret**
   - **Generate a new client secret** 버튼 클릭
   - 생성된 Secret 복사하여 안전하게 저장
   - ⚠️ **절대 공개하지 마세요!** 한 번만 표시되므로 즉시 저장

## 2. Vercel 환경 변수 설정

### 단계 1: Vercel 대시보드 접속

1. [Vercel](https://vercel.com)에 로그인
2. 프로젝트 선택

### 단계 2: Environment Variables 추가

1. **Settings** 탭 클릭
2. **Environment Variables** 섹션으로 이동
3. 다음 변수 추가:

   **변수 1:**
   - **Key:** `GITHUB_CLIENT_ID`
   - **Value:** GitHub에서 복사한 Client ID
   - **Environment:** Production, Preview, Development 모두 선택

   **변수 2:**
   - **Key:** `GITHUB_CLIENT_SECRET`
   - **Value:** GitHub에서 복사한 Client Secret
   - **Environment:** Production, Preview, Development 모두 선택

4. **Save** 클릭

### 단계 3: 배포 재실행 (선택사항)

환경 변수를 추가한 후, 다음 배포부터 적용된다. 즉시 적용하려면:
1. **Deployments** 탭으로 이동
2. 최신 배포의 **...** 메뉴 클릭
3. **Redeploy** 선택

## 3. _config.yml 설정 (선택사항)

프론트엔드에서 Client ID를 사용하려면 `_config.yml`에 추가할 수 있다:

```yaml
admin:
  enabled: true
  github_oauth:
    client_id: "your_client_id_here"  # GitHub에서 복사한 Client ID
```

⚠️ **주의:** Client ID만 추가하고, Client Secret은 절대 추가하지 마세요.

## 4. 다중 도메인 지원 (GitHub Pages + Vercel)

GitHub Pages와 Vercel을 동시에 사용하는 경우, GitHub OAuth App에 여러 Callback URL을 추가할 수 있다:

1. GitHub → Settings → Developer settings → OAuth Apps
2. 생성한 OAuth App 클릭
3. **Authorization callback URL** 필드에 여러 URL 추가:
   ```
   https://rldhkstopic.github.io/admin/
   https://your-project.vercel.app/admin/
   ```

⚠️ **참고:** GitHub OAuth App은 하나의 Callback URL만 지원하므로, 두 도메인을 모두 사용하려면:
- 방법 1: 두 개의 OAuth App 생성 (각 도메인별)
- 방법 2: 하나의 도메인만 사용 (권장: Vercel 도메인)

## 5. 테스트

### 단계 1: 배포 확인

1. Vercel 대시보드에서 배포가 완료되었는지 확인
2. 배포된 사이트 URL 확인

### 단계 2: 로그인 테스트

1. 배포된 사이트에서 `/admin/` 페이지 접속
   - 예: `https://your-project.vercel.app/admin/`
2. **GitHub로 로그인** 버튼 클릭
3. GitHub 인증 페이지에서 권한 승인
4. Callback으로 돌아와서 자동 로그인 확인

### 단계 3: 서버리스 함수 확인

브라우저 개발자 도구 → Network 탭에서:
- `/api/github-oauth` 요청이 성공하는지 확인
- 응답에 `access_token`이 포함되어 있는지 확인

## 6. 문제 해결

### 문제: "GitHub OAuth credentials not configured" 오류

**원인:** Vercel 환경 변수가 설정되지 않음

**해결:**
1. Vercel 대시보드 → Settings → Environment Variables 확인
2. `GITHUB_CLIENT_ID`와 `GITHUB_CLIENT_SECRET`이 올바르게 설정되었는지 확인
3. 환경 변수 추가 후 배포 재실행

### 문제: "redirect_uri_mismatch" 오류

**원인:** Callback URL이 OAuth App 설정과 일치하지 않음

**해결:**
1. GitHub OAuth App의 **Authorization callback URL** 확인
2. 실제 사이트 URL과 정확히 일치하는지 확인
3. URL 끝에 `/`가 있는지 확인 (`/admin/`)

### 문제: 서버리스 함수가 작동하지 않음

**원인:** `api/github-oauth.js` 파일이 없거나 경로가 잘못됨

**해결:**
1. 프로젝트 루트에 `api/github-oauth.js` 파일이 있는지 확인
2. Vercel 대시보드 → Functions 탭에서 함수가 등록되었는지 확인
3. 함수 로그에서 오류 메시지 확인

## 7. 보안 주의사항

1. **Client Secret 보호**
   - 절대 GitHub 저장소에 커밋하지 마세요
   - Vercel 환경 변수에만 저장
   - `.env` 파일을 `.gitignore`에 추가

2. **HTTPS 사용**
   - 프로덕션에서는 반드시 HTTPS 사용
   - Vercel은 자동으로 HTTPS 제공

3. **환경 변수 관리**
   - Production, Preview, Development 환경별로 다른 값 사용 가능
   - 테스트용 OAuth App과 프로덕션용 OAuth App 분리 권장

## 8. 완료 확인 체크리스트

- [ ] GitHub OAuth App 생성 완료
- [ ] Client ID와 Client Secret 확인 및 저장
- [ ] Vercel 환경 변수 설정 완료
- [ ] `_config.yml`에 Client ID 추가 (선택사항)
- [ ] 배포 완료 및 사이트 접속 확인
- [ ] `/admin/` 페이지에서 로그인 테스트 성공
- [ ] 서버리스 함수 정상 작동 확인

## 참고 자료

- [GitHub OAuth Apps 문서](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
- [Vercel Environment Variables 문서](https://vercel.com/docs/concepts/projects/environment-variables)
- [프로젝트 OAuth 가이드](docs/GITHUB_OAUTH_GUIDE.md)

