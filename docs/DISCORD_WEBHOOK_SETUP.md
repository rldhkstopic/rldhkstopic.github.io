# Discord 웹훅 설정 가이드

GitHub Actions 워크플로우에서 Discord 알림을 받으려면 Discord 웹훅을 설정해야 합니다.

## 1. Discord 웹훅 생성

### 1.1 Discord 서버에서 웹훅 생성

1. Discord 서버에서 알림을 받을 채널 선택
2. 채널 설정 (톱니바퀴 아이콘) 클릭
3. **연동** → **웹후크** 클릭
4. **새 웹후크** 클릭
5. 웹후크 이름 설정 (예: "GitHub Actions 알림")
6. **웹후크 URL 복사** 클릭
   - 형식: `https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz1234567890`

### 1.2 웹훅 URL 형식 확인

올바른 웹훅 URL 형식:
```
https://discord.com/api/webhooks/<ID>/<TOKEN>
```

예시:
```
https://discord.com/api/webhooks/123456789012345678/abcdefghijklmnopqrstuvwxyz1234567890
```

## 2. GitHub Secrets에 웹훅 URL 추가

### 2.1 GitHub 리포지토리 설정

1. GitHub 리포지토리 페이지 접속
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. **New repository secret** 버튼 클릭
5. 다음 정보 입력:
   - **Name**: `DISCORD_WEBHOOK_URL`
   - **Secret**: Discord 웹훅 URL (복사한 전체 URL)
6. **Add secret** 클릭

### 2.2 웹훅 URL 확인 사항

- ✅ 전체 URL을 복사했는지 확인 (https://로 시작)
- ✅ 공백이나 줄바꿈이 포함되지 않았는지 확인
- ✅ 따옴표로 감싸지 않았는지 확인
- ❌ 숫자 ID만 복사하지 않았는지 확인
- ❌ 웹훅 이름만 입력하지 않았는지 확인

## 3. 웹훅 테스트

### 3.1 수동 테스트

GitHub Actions에서 워크플로우를 수동 실행하여 테스트할 수 있습니다:

1. GitHub 리포지토리 → **Actions** 탭
2. **Auto Post Daily** 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. 워크플로우 실행 후 Discord 채널에서 알림 확인

### 3.2 알림이 오지 않는 경우

1. **GitHub Secrets 확인**
   - Settings → Secrets and variables → Actions
   - `DISCORD_WEBHOOK_URL`이 올바르게 설정되었는지 확인

2. **워크플로우 로그 확인**
   - Actions 탭 → 최근 실행 → 로그 확인
   - `workflow_notifier.py` 실행 결과 확인
   - 오류 메시지 확인

3. **웹훅 URL 유효성 확인**
   - 웹훅 URL을 브라우저에 직접 입력하여 테스트
   - 또는 curl 명령어로 테스트:
     ```bash
     curl -X POST "YOUR_WEBHOOK_URL" \
       -H "Content-Type: application/json" \
       -d '{"content": "테스트 메시지"}'
     ```

4. **Discord 웹훅 상태 확인**
   - Discord 채널 설정 → 연동 → 웹후크
   - 웹후크가 활성화되어 있는지 확인
   - 웹후크가 삭제되지 않았는지 확인

## 4. 여러 채널에 알림 보내기

여러 채널에 알림을 보내려면 각 채널마다 웹훅을 생성하고, GitHub Secrets에 여러 개를 추가할 수 있습니다:

- `DISCORD_WEBHOOK_URL`: 기본 알림 채널
- `DISCORD_WEBHOOK_URL_2`: 추가 알림 채널 (선택사항)

워크플로우 파일을 수정하여 여러 웹훅을 사용할 수 있습니다.

## 5. 문제 해결

### 알림이 오지 않는 경우

1. **웹훅 URL 형식 오류**
   - 로그에서 `[WARN] DISCORD_WEBHOOK_URL 형식이 잘못되었습니다` 메시지 확인
   - 전체 URL이 올바르게 입력되었는지 확인

2. **웹훅이 삭제됨**
   - Discord 채널에서 웹훅이 삭제되었는지 확인
   - 필요시 새 웹훅 생성 후 GitHub Secrets 업데이트

3. **권한 문제**
   - 웹훅이 해당 채널에 메시지를 보낼 권한이 있는지 확인
   - 봇이 채널에 접근할 수 있는지 확인

4. **네트워크 문제**
   - GitHub Actions에서 Discord API에 접근할 수 있는지 확인
   - 방화벽이나 네트워크 제한이 없는지 확인

## 참고 자료

- [Discord 웹훅 가이드](https://discord.com/developers/docs/resources/webhook)
- [GitHub Secrets 문서](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
