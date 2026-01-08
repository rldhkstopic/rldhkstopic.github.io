# Discord 알림 설정 가이드

이 문서는 GitHub Actions 워크플로우와 커밋에 대한 Discord 알림 설정을 설명합니다.

## 개요

현재 프로젝트에서는 다음 이벤트에 대해 Discord 알림을 받을 수 있습니다:

1. **GitHub Actions 워크플로우 알림**: 워크플로우 시작, 성공, 실패 시 알림
2. **커밋 알림**: GitHub Webhook을 통한 커밋 알림 (선택 사항)

## GitHub Actions 워크플로우 알림

### 설정된 워크플로우

다음 워크플로우들이 Discord 알림을 전송합니다:

1. **Auto Post Daily** (`.github/workflows/auto-post.yml`)
   - 트리거: 스케줄(매일 오전 7시 KST), push, workflow_dispatch
   - 알림: started, success, failure

2. **Daily Diary Generator** (`.github/workflows/daily-diary.yml`)
   - 트리거: 스케줄(매일 자정 KST), workflow_dispatch
   - 알림: started, success, failure

3. **Update Analytics Data** (`.github/workflows/update-analytics.yml`)
   - 트리거: 스케줄(매시간), workflow_dispatch
   - 알림: started, success, failure

### 알림 내용

각 워크플로우 알림에는 다음 정보가 포함됩니다:

- 워크플로우 이름
- 상태 (시작/성공/실패)
- 실행자 (GitHub 사용자)
- 브랜치
- 커밋 메시지
- 워크플로우 실행 링크
- 오류 메시지 (실패 시)

### 알림 스크립트

알림은 `.github/scripts/workflow_notifier.py` 스크립트를 통해 전송됩니다.

### 환경 변수 설정

GitHub Secrets에 다음 변수를 설정해야 합니다:

- `DISCORD_WEBHOOK_URL`: Discord 웹훅 URL

**설정 방법:**
1. Discord 서버에서 웹훅 생성
2. GitHub 리포지토리 → Settings → Secrets and variables → Actions
3. `DISCORD_WEBHOOK_URL` 추가

## 커밋 알림 (선택 사항)

### GitHub Webhook 설정

커밋 시 Discord 알림을 받으려면 GitHub Webhook을 설정해야 합니다.

**설정 방법:**

1. **Discord 웹훅 생성**
   - Discord 서버 → 채널 설정 → 연동 → 웹후크
   - 새 웹후크 생성 또는 기존 웹후크 URL 복사

2. **GitHub Webhook 설정**
   - GitHub 리포지토리 → Settings → Webhooks
   - Add webhook 클릭
   - Payload URL: Discord 웹훅 URL 입력
   - Content type: `application/json`
   - Which events: `Just the push event` 선택 (또는 필요한 이벤트 선택)
   - Active 체크
   - Add webhook 클릭

3. **Webhook 페이로드 처리**

   GitHub Webhook은 Discord 웹훅과 직접 호환되지 않으므로, 중간 서버나 서비스가 필요합니다.

   **옵션 1: GitHub Actions 사용**
   - 커밋 시 워크플로우가 트리거되면 자동으로 알림 전송 (현재 구현됨)

   **옵션 2: 외부 서비스 사용**
   - Zapier, IFTTT, n8n 등 사용
   - GitHub Webhook → Discord Webhook 변환

   **옵션 3: 자체 서버 구축**
   - GitHub Webhook을 받아 Discord 형식으로 변환하는 서버 구축

### 현재 상태

현재는 GitHub Actions 워크플로우가 커밋을 수행할 때 워크플로우 알림이 전송되므로, 간접적으로 커밋 알림을 받을 수 있습니다. 하지만 수동 커밋에 대한 알림은 GitHub Webhook을 통해서만 가능합니다.

## 알림 확인 방법

### 1. 워크플로우 알림 확인

워크플로우가 실행되면 Discord 채널에 자동으로 알림이 전송됩니다. 알림이 오지 않는 경우:

1. `DISCORD_WEBHOOK_URL` 시크릿이 올바르게 설정되었는지 확인
2. 웹훅 URL 형식 확인 (공백, 따옴표 제거)
3. GitHub Actions 로그에서 `workflow_notifier.py` 실행 결과 확인

### 2. 커밋 알림 확인

GitHub Webhook이 설정되어 있다면, 커밋 시 Discord 알림을 받을 수 있습니다. 알림이 오지 않는 경우:

1. GitHub Webhook 설정 확인
2. Webhook 페이로드 처리 서비스/서버 확인
3. Discord 웹훅 URL 유효성 확인

## 문제 해결

### 알림이 오지 않는 경우

1. **워크플로우 알림**
   - GitHub Actions 로그 확인
   - `workflow_notifier.py` 실행 결과 확인
   - `DISCORD_WEBHOOK_URL` 시크릿 확인

2. **커밋 알림**
   - GitHub Webhook 설정 확인
   - Webhook 페이로드 처리 확인
   - Discord 웹훅 URL 확인

### 알림 형식 오류

- 웹훅 URL에 공백이나 따옴표가 포함되어 있는지 확인
- `workflow_notifier.py`가 웹훅 URL을 정규화하므로 대부분 자동으로 처리됩니다

## 참고 자료

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Discord Webhooks 가이드](https://discord.com/developers/docs/resources/webhook)
- [GitHub Webhooks 문서](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
