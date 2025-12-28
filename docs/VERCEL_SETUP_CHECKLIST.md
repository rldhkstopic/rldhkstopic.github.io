# Vercel 설정 체크리스트

Vercel 기능 가이드의 모든 기능을 적용하기 위한 단계별 체크리스트다.

## ✅ 코드로 자동 적용된 항목

다음 항목들은 이미 코드에 적용되어 있다:

1. **Custom Headers (보안 헤더)**
   - `vercel.json`에 보안 헤더 설정 완료
   - XSS 방지, 클릭재킹 방지 등

2. **Vercel Analytics 스크립트**
   - `_layouts/default.html`에 스크립트 추가 완료
   - 로컬 환경에서는 비활성화, 프로덕션에서만 작동

3. **Vercel Speed Insights 스크립트**
   - `_layouts/default.html`에 스크립트 추가 완료
   - 로컬 환경에서는 비활성화, 프로덕션에서만 작동

4. **서버리스 함수**
   - `api/github-oauth.js` 이미 구현됨

5. **vercel.json 설정**
   - Analytics 및 Speed Insights 자동 주입 설정 추가

## 📋 Vercel 대시보드에서 설정해야 할 항목

다음 항목들은 Vercel 대시보드에서 직접 설정해야 한다:

### 1. Analytics 활성화

1. Vercel 대시보드 로그인
2. 프로젝트 선택
3. **Analytics** 탭 클릭
4. **Enable Web Analytics** 토글 활성화
5. 저장

**확인 방법:** Analytics 탭에서 방문자 통계가 표시되는지 확인

### 2. Speed Insights 활성화

1. Vercel 대시보드 로그인
2. 프로젝트 선택
3. **Speed Insights** 탭 클릭
4. **Enable Speed Insights** 토글 활성화
5. 저장

**확인 방법:** Speed Insights 탭에서 Core Web Vitals 지표가 표시되는지 확인

### 3. Deployment Regions 설정 (한국 최적화)

1. Vercel 대시보드 로그인
2. 프로젝트 선택
3. **Settings** → **General** 탭
4. **Region** 섹션에서 **Seoul, South Korea (icn1)** 선택
5. 저장

**효과:** 한국 사용자 기준 응답 시간 단축

### 4. Environment Variables 설정 (GitHub OAuth 사용 시)

1. Vercel 대시보드 로그인
2. 프로젝트 선택
3. **Settings** → **Environment Variables** 탭
4. 다음 변수 추가:
   - `GITHUB_CLIENT_ID`: GitHub OAuth App의 Client ID
   - `GITHUB_CLIENT_SECRET`: GitHub OAuth App의 Client Secret
5. 각 변수에 대해 **Production**, **Preview**, **Development** 환경 선택
6. 저장

**확인 방법:** `api/github-oauth.js` 함수가 정상 작동하는지 테스트

### 5. Custom Domain 설정 (선택사항)

1. Vercel 대시보드 로그인
2. 프로젝트 선택
3. **Settings** → **Domains** 탭
4. **Add Domain** 클릭
5. 도메인 입력 (예: `blog.example.com`)
6. DNS 설정 안내에 따라 도메인 제공업체에서 설정
   - A 레코드 또는 CNAME 레코드 추가
7. DNS 전파 대기 (보통 몇 분~몇 시간)
8. SSL 인증서 자동 발급 확인

**확인 방법:** 커스텀 도메인으로 접속하여 정상 작동 확인

## 🔄 자동으로 작동하는 기능

다음 기능들은 별도 설정 없이 자동으로 작동한다:

1. **Preview Deployments**
   - GitHub PR 생성 시 자동으로 미리보기 URL 생성
   - Vercel 대시보드의 **Deployments** 탭에서 확인 가능

2. **Edge Functions**
   - `api/` 디렉토리의 서버리스 함수는 자동으로 엣지에서 실행됨
   - 전 세계 엣지 서버에서 최적의 위치에서 실행

3. **CDN 및 캐싱**
   - 자동으로 전 세계 CDN에 배포
   - 정적 파일 자동 캐싱

## ✅ 설정 완료 확인

모든 설정이 완료되었는지 확인:

1. **Analytics 확인**
   - Vercel 대시보드 → Analytics 탭
   - 방문자 통계가 표시되는지 확인

2. **Speed Insights 확인**
   - Vercel 대시보드 → Speed Insights 탭
   - Core Web Vitals 지표가 표시되는지 확인

3. **서버리스 함수 확인**
   - 배포된 사이트에서 `/api/github-oauth` 엔드포인트 테스트
   - (환경 변수 설정 후)

4. **보안 헤더 확인**
   - 브라우저 개발자 도구 → Network 탭
   - 응답 헤더에 보안 헤더가 포함되어 있는지 확인

5. **배포 확인**
   - Vercel 대시보드 → Deployments 탭
   - 최신 배포가 성공 상태인지 확인

## 📝 참고

- 모든 대시보드 설정은 배포 후에도 변경 가능하다
- 설정 변경 후 즉시 반영되거나 다음 배포 시 반영된다
- Analytics와 Speed Insights는 배포 후 몇 시간 후부터 데이터가 수집되기 시작한다

## 문제 해결

### Analytics가 작동하지 않는 경우

1. Vercel 대시보드에서 Analytics가 활성화되어 있는지 확인
2. 배포가 완료되었는지 확인
3. 브라우저 콘솔에서 오류 확인
4. `vercel.json`의 `analytics` 설정 확인

### Speed Insights가 작동하지 않는 경우

1. Vercel 대시보드에서 Speed Insights가 활성화되어 있는지 확인
2. 배포가 완료되었는지 확인
3. 브라우저 콘솔에서 오류 확인
4. `vercel.json`의 `speedInsights` 설정 확인

### 서버리스 함수가 작동하지 않는 경우

1. 환경 변수가 올바르게 설정되었는지 확인
2. 함수 파일이 `api/` 디렉토리에 있는지 확인
3. Vercel 대시보드 → Functions 탭에서 함수 로그 확인

