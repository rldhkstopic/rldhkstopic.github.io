# 일기 자동화 워크플로우 문제 해결 가이드

## 문제: 일기 글이 생성되지 않음

### 1. GitHub Secrets 확인

일기 수집 워크플로우가 작동하려면 다음 Secrets가 설정되어 있어야 합니다:

#### 필수 Secrets

1. **DISCORD_BOT_TOKEN**
   - Discord 봇 토큰
   - Discord Developer Portal에서 생성한 봇의 토큰
   - 설정 위치: GitHub 리포지토리 → Settings → Secrets and variables → Actions

2. **DISCORD_CHANNEL_ID**
   - 일기 메시지를 수집할 Discord 채널 ID
   - 채널 ID 확인 방법:
     1. Discord 개발자 모드 활성화 (설정 → 고급 → 개발자 모드)
     2. 채널 우클릭 → ID 복사
   - 설정 위치: GitHub 리포지토리 → Settings → Secrets and variables → Actions

3. **GEMINI_API_KEY**
   - Google Gemini API 키
   - 일기 생성에 사용

4. **GITHUB_TOKEN**
   - 자동으로 제공되지만 확인 필요

5. **DISCORD_WEBHOOK_URL** (선택)
   - 알림 전송용 웹훅 URL

#### Secrets 설정 방법

1. GitHub 리포지토리 페이지 접속
2. **Settings** 탭 클릭
3. 왼쪽 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. **New repository secret** 버튼 클릭
5. Name과 Secret 값 입력 후 **Add secret** 클릭

### 2. Discord 봇 권한 확인

Discord 봇이 다음 권한을 가지고 있어야 합니다:

#### 필수 권한

- **메시지 읽기** (Read Message History)
- **채널 보기** (View Channels)
- **채널 접근** (해당 채널에 봇이 초대되어 있어야 함)

#### 권한 설정 방법

1. Discord Developer Portal 접속
2. 봇 선택 → **Bot** 탭
3. **Privileged Gateway Intents** 활성화:
   - MESSAGE CONTENT INTENT (메시지 내용 읽기)
4. **OAuth2** → **URL Generator**에서:
   - Scopes: `bot`
   - Bot Permissions: `Read Message History`, `View Channels`
5. 생성된 URL로 봇을 서버에 초대

### 3. 워크플로우 실행 확인

#### 수동 실행 테스트

1. GitHub 리포지토리 → **Actions** 탭
2. **Daily Diary Generator** 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. `target_date` 입력 (예: `2026-01-03`)
5. 실행 후 로그 확인

#### 로그 확인 포인트

1. **"Collect Discord daily logs (polling)"** 단계:
   - `[ERROR] DISCORD_BOT_TOKEN is not set` → Secrets 미설정
   - `[ERROR] DISCORD_CHANNEL_ID is not set` → Secrets 미설정
   - `[OK] Collected=X written=Y skipped=Z` → 정상 수집

2. **"Run daily diary agent"** 단계:
   - `[INFO] {날짜}에 기록된 일이 없습니다` → 해당 날짜에 메시지 없음
   - `[OK] {N}개의 기록을 찾았습니다` → 정상 로드

### 4. 일반적인 문제와 해결 방법

#### 문제 1: "기록된 일이 없습니다"

**원인:**
- 해당 날짜에 Discord 채널에 메시지가 없음
- 봇이 메시지를 읽을 수 없음
- 채널 ID가 잘못됨

**해결:**
1. Discord 채널에 실제로 메시지가 있는지 확인
2. 봇이 해당 채널에 접근 가능한지 확인
3. 채널 ID가 올바른지 확인 (개발자 모드로 재확인)

#### 문제 2: "DISCORD_BOT_TOKEN is not set"

**원인:**
- GitHub Secrets에 토큰이 설정되지 않음
- 토큰 이름이 잘못됨 (대소문자 구분)

**해결:**
1. Settings → Secrets and variables → Actions 확인
2. `DISCORD_BOT_TOKEN` 이름이 정확한지 확인 (대문자)
3. 토큰 값이 올바른지 확인 (공백 없이)

#### 문제 3: "DISCORD_CHANNEL_ID is not set"

**원인:**
- GitHub Secrets에 채널 ID가 설정되지 않음

**해결:**
1. Settings → Secrets and variables → Actions 확인
2. `DISCORD_CHANNEL_ID` 이름이 정확한지 확인
3. 채널 ID가 숫자로만 구성되어 있는지 확인

#### 문제 4: 봇이 메시지를 읽지 못함

**원인:**
- MESSAGE CONTENT INTENT가 활성화되지 않음
- 봇이 채널에 접근할 수 없음
- 봇 메시지는 자동으로 제외됨 (정상 동작)

**해결:**
1. Discord Developer Portal → Bot → Privileged Gateway Intents
2. **MESSAGE CONTENT INTENT** 활성화
3. 봇을 서버에서 제거 후 다시 초대

### 5. 디버깅 방법

#### 로컬 테스트

```bash
# 환경 변수 설정
export DISCORD_BOT_TOKEN="your_token"
export DISCORD_CHANNEL_ID="your_channel_id"

# 스크립트 실행
python .github/scripts/discord_daily_log_collector.py 2026-01-03

# 결과 확인
ls _daily_logs/2026-01-03/
```

#### 워크플로우 로그 확인

1. GitHub Actions → 최근 실행 선택
2. **"Collect Discord daily logs (polling)"** 단계 클릭
3. 출력 로그 확인:
   - `[INFO] Target date (KST): ...`
   - `[OK] Collected=... written=... skipped=...`

### 6. 예상 동작 흐름

```
1. 자정 (KST 00:00) 워크플로우 실행
   ↓
2. Discord 채널에서 전일 메시지 수집
   → _daily_logs/YYYY-MM-DD/{message_id}.json 저장
   ↓
3. 수집된 메시지 로드
   ↓
4. AI로 일기 생성
   ↓
5. _posts/YYYY-MM-DD-{날짜}-일기.md 생성
   ↓
6. GitHub에 커밋 및 푸시
```

### 7. 체크리스트

- [ ] `DISCORD_BOT_TOKEN` GitHub Secret 설정됨
- [ ] `DISCORD_CHANNEL_ID` GitHub Secret 설정됨
- [ ] `GEMINI_API_KEY` GitHub Secret 설정됨
- [ ] Discord 봇이 서버에 초대됨
- [ ] Discord 봇이 해당 채널에 접근 가능
- [ ] MESSAGE CONTENT INTENT 활성화됨
- [ ] 워크플로우가 정상 실행됨
- [ ] `_daily_logs/` 폴더에 JSON 파일 생성됨
- [ ] `_posts/` 폴더에 일기 파일 생성됨

### 8. 추가 도움말

문제가 지속되면:
1. GitHub Actions 로그 전체 확인
2. Discord Developer Portal에서 봇 상태 확인
3. Discord 채널에서 봇이 메시지를 볼 수 있는지 수동 테스트
