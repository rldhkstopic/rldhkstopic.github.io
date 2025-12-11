# Google Analytics 4 (GA4) Reporting API 연동 가이드

이 가이드는 GitHub Actions를 사용하여 GA4 데이터를 자동으로 가져와 블로그에 표시하는 방법을 설명합니다.

## 사전 준비

1. **Google Cloud 프로젝트** 생성
2. **GA4 속성 ID** 확인
3. **서비스 계정** 생성 및 키 다운로드
4. **GitHub Secrets** 설정

## 단계별 설정

### 1단계: Google Cloud 프로젝트 생성 및 API 활성화

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스** → **라이브러리**로 이동
4. "Google Analytics Data API" 검색 후 **활성화**

### 2단계: GA4 속성 ID 확인

1. [Google Analytics](https://analytics.google.com/) 접속
2. 관리(톱니바퀴 아이콘) → 속성 설정
3. **속성 ID** 복사 (예: `123456789`)

### 3단계: 서비스 계정 생성

1. Google Cloud Console → **IAM 및 관리자** → **서비스 계정**
2. **서비스 계정 만들기** 클릭
3. 서비스 계정 이름 입력 (예: "ga4-blog-reader")
4. **만들기** 클릭
5. 역할은 비워두고 **완료** 클릭

### 4단계: 서비스 계정 키 생성

1. 생성한 서비스 계정 클릭
2. **키** 탭 → **키 추가** → **새 키 만들기**
3. JSON 형식 선택 → **만들기**
4. 다운로드된 JSON 파일을 안전하게 보관

### 5단계: GA4 속성에 서비스 계정 권한 부여

1. Google Analytics → 관리 → 속성 액세스 관리
2. **+** 버튼 클릭 → **사용자 추가**
3. 서비스 계정 이메일 주소 입력 (예: `ga4-blog-reader@project-id.iam.gserviceaccount.com`)
4. **뷰어** 역할 선택
5. **추가** 클릭

### 6단계: GitHub Secrets 설정

1. GitHub 리포지토리 → **Settings** → **Secrets and variables** → **Actions**
2. 다음 Secrets 추가:

   - **`GA4_PROPERTY_ID`**: GA4 속성 ID (예: `123456789`)
   - **`GA4_CREDENTIALS`**: 서비스 계정 JSON 파일의 전체 내용 (한 줄로)

   `GA4_CREDENTIALS` 예시:
   ```json
   {"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
   ```

### 7단계: 워크플로우 수정 (선택사항)

`.github/workflows/update-analytics.yml` 파일에서 다음을 수정할 수 있습니다:

- **스케줄**: `cron: '0 * * * *'` (매 시간) → 원하는 주기로 변경
- **시작일**: `fetch-analytics.js`의 `startDate: '2024-01-01'`를 블로그 시작일로 변경

### 8단계: 수동 실행 테스트

1. GitHub 리포지토리 → **Actions** 탭
2. "Update Analytics Data" 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. 실행 로그 확인

## 문제 해결

### "GA4_CREDENTIALS 환경 변수가 설정되지 않았습니다"
- GitHub Secrets에 `GA4_CREDENTIALS`가 올바르게 설정되었는지 확인
- JSON 형식이 올바른지 확인 (한 줄로, 이스케이프 문자 포함)

### "Analytics 데이터를 불러올 수 없습니다"
- GitHub Actions가 성공적으로 실행되었는지 확인
- `_data/analytics.json` 파일이 생성되었는지 확인
- 브라우저 콘솔에서 네트워크 오류 확인

### 데이터가 업데이트되지 않음
- GitHub Actions 실행 로그 확인
- GA4 속성에 서비스 계정 권한이 올바르게 부여되었는지 확인
- 속성 ID가 올바른지 확인

## 참고 자료

- [Google Analytics Data API 문서](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [GitHub Actions 문서](https://docs.github.com/en/actions)

