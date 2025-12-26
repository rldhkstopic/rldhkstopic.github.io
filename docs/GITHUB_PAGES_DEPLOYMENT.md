# GitHub Pages에서 관리자 에디터 사용하기

GitHub Pages에 배포된 사이트에서도 관리자 에디터를 사용할 수 있다. GitHub API는 CORS를 지원하므로 브라우저에서 직접 API를 호출할 수 있다.

## 작동 원리

1. **클라이언트 사이드 인증**: 브라우저에서 GitHub Personal Access Token을 사용하여 인증
2. **GitHub API 직접 호출**: CORS를 지원하므로 브라우저에서 직접 API 호출 가능
3. **로컬스토리지 저장**: 토큰은 브라우저의 로컬스토리지 또는 세션스토리지에 저장

## 사용 방법

### 1. GitHub Personal Access Token 생성

1. [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens/new)로 이동
2. "Generate new token (classic)" 클릭
3. 설정:
   - **Note**: "Blog Admin Editor"
   - **Expiration**: 원하는 기간 선택
   - **Select scopes**: `repo` 체크 (전체 저장소 접근)
4. "Generate token" 클릭 후 토큰 복사

### 2. 배포된 사이트에서 로그인

1. **https://rldhkstopic.github.io/admin/** 접속
2. GitHub Personal Access Token 입력
3. (선택) 관리자 비밀번호 입력
4. "토큰 저장" 체크박스 선택 (선택사항)
5. "로그인" 클릭

### 3. 포스트 작성

1. 로그인 성공 시 자동으로 `/editor/` 페이지로 이동
2. 포스트 정보 입력 (제목, 카테고리, 태그 등)
3. 마크다운으로 본문 작성
4. "게시" 버튼 클릭하여 GitHub에 직접 업로드

## CORS 및 보안

### GitHub API CORS 지원

GitHub API는 CORS를 지원하므로 브라우저에서 직접 호출이 가능하다. 코드에서 `mode: 'cors'`를 명시적으로 설정하여 CORS 요청임을 표시한다.

### 보안 고려사항

1. **토큰 보안**:
   - 토큰은 브라우저의 로컬스토리지에 저장되므로, 공용 컴퓨터에서는 사용하지 마세요
   - 토큰이 유출되면 즉시 GitHub에서 삭제하세요
   - 정기적으로 토큰을 갱신하세요

2. **HTTPS 사용**:
   - GitHub Pages는 기본적으로 HTTPS를 사용하므로 안전합니다
   - 로컬 개발 시에도 가능하면 HTTPS를 사용하세요

3. **추가 보안 (선택)**:
   - `_config.yml`에 `admin.admin_password`를 설정하여 추가 보안 레이어 추가 가능
   - 비밀번호는 SHA-256 해시로 저장

## 문제 해결

### CORS 오류 발생 시

만약 CORS 오류가 발생한다면:

1. **브라우저 콘솔 확인**: 개발자 도구(F12)에서 에러 메시지 확인
2. **토큰 확인**: 토큰이 올바른지, 만료되지 않았는지 확인
3. **권한 확인**: 토큰에 `repo` 스코프가 있는지 확인

### API Rate Limit

GitHub API는 시간당 5,000 요청으로 제한되어 있다. 일반적인 사용에서는 문제가 없지만, 여러 포스트를 연속으로 작성할 경우 주의가 필요하다.

### 네트워크 오류

- 인터넷 연결 확인
- GitHub API 상태 확인: https://www.githubstatus.com/
- 브라우저 캐시 삭제 후 재시도

## 대안: GitHub OAuth App 사용 (고급)

더 안전한 방법으로 GitHub OAuth App을 사용할 수 있다. 이 방법은:

1. GitHub OAuth App 생성
2. OAuth 인증 플로우 구현
3. Access Token을 서버에서 받아서 사용

하지만 이 방법은 서버 사이드 컴포넌트가 필요하므로, GitHub Pages만으로는 구현이 어렵다. Netlify Functions나 Vercel Functions 같은 서버리스 함수를 사용해야 한다.

## 참고 자료

- [GitHub API CORS 문서](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#cors)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)


