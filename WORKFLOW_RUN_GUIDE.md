# GitHub Actions 워크플로우 실행 가이드

## 워크플로우 수동 실행 방법

### 1단계: GitHub 리포지토리로 이동
1. `https://github.com/rldhkstopic/rldhkstopic.github.io` 접속
2. 상단 메뉴에서 **Actions** 탭 클릭

### 2단계: 워크플로우 선택
1. 왼쪽 사이드바에서 **"Update Analytics Data"** 워크플로우 클릭
2. 또는 워크플로우 목록에서 "Update Analytics Data" 찾기

### 3단계: 워크플로우 실행
1. 오른쪽 상단의 **"Run workflow"** 버튼 클릭
2. 드롭다운에서 **"Run workflow"** 선택
3. **"Run workflow"** 버튼 클릭

### 4단계: 실행 확인
1. 워크플로우 실행 목록에서 가장 최근 실행 클릭
2. 각 단계의 로그 확인:
   - ✅ Checkout repository
   - ✅ Setup Node.js
   - ✅ Install dependencies
   - ✅ Fetch GA4 Data
   - ✅ Commit and push

## 문제 해결

### "This workflow has no runs yet" 메시지
- 이는 정상입니다. 아직 실행하지 않았기 때문입니다.
- 위의 1-3단계를 따라 수동으로 실행하세요.

### "GA4_CREDENTIALS 환경 변수가 설정되지 않았습니다"
- GitHub Secrets에 `GA4_CREDENTIALS`가 올바르게 설정되었는지 확인
- Settings → Secrets and variables → Actions에서 확인

### "GA4_PROPERTY_ID 환경 변수가 설정되지 않았습니다"
- GitHub Secrets에 `GA4_PROPERTY_ID`가 설정되었는지 확인
- Google Analytics에서 속성 ID 확인 (숫자만, 예: `123456789`)

### "Permission denied" 오류
- GitHub Actions가 리포지토리에 쓰기 권한이 있는지 확인
- Settings → Actions → General → Workflow permissions에서 확인

### 데이터가 업데이트되지 않음
- 워크플로우 실행 로그에서 오류 확인
- GA4 속성에 서비스 계정 권한이 올바르게 부여되었는지 확인
- 속성 ID가 올바른지 확인

## 자동 실행

워크플로우는 매 시간마다 자동으로 실행됩니다 (cron: '0 * * * *').
첫 실행은 수동으로 해야 할 수도 있습니다.

## 확인 사항

워크플로우가 성공적으로 실행되면:
1. `_data/analytics.json` 파일이 업데이트됩니다
2. 블로그의 방문자 통계 섹션에 숫자가 표시됩니다
3. GitHub Actions 로그에 "Analytics 데이터 업데이트 완료" 메시지가 표시됩니다

