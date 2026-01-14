# Windows 자동 시작 설정 (가장 경제적)

PC가 항상 켜져있다면, Windows 작업 스케줄러를 사용하여 가장 경제적으로 봇을 항상 실행할 수 있습니다.

## 🎯 장점

- **완전 무료** (클라우드 비용 없음)
- **항상 켜놓기 가능** (PC가 켜져있는 한)
- **로컬 실행** (빠른 응답 속도)

## 📋 설정 방법

### 1. 배치 파일 생성

`local_bot/start_bot.bat` 파일 생성:

```batch
@echo off
cd /d "%~dp0"
python discord_interface.py
pause
```

### 2. 작업 스케줄러 설정

1. **작업 스케줄러 열기**
   - Windows 검색에서 "작업 스케줄러" 입력
   - 또는 `Win + R` → `taskschd.msc` 입력

2. **기본 작업 만들기**
   - 오른쪽 "기본 작업 만들기" 클릭
   - 이름: `Discord Bot Auto Start`
   - 설명: `Discord 봇 자동 시작`

3. **트리거 설정**
   - "작업 시작 시점": **"로그온할 때"** 선택
   - 또는 **"컴퓨터 시작 시"** 선택 (PC 부팅 시 자동 실행)

4. **동작 설정**
   - "동작": **"프로그램 시작"** 선택
   - 프로그램/스크립트: `C:\Users\사용자명\AppData\Local\Programs\Python\Python311\python.exe` (Python 경로)
   - 인수 추가: `"D:\cursor\GithubPage_rldhkstopic\local_bot\discord_interface.py"`
   - 시작 위치: `D:\cursor\GithubPage_rldhkstopic\local_bot`

5. **조건 설정**
   - "작업이 실행 중이 아닐 때만 새 인스턴스 시작" 체크 해제
   - "다음 시간 동안 실행 중이면 작업 중지" 체크 해제

6. **설정**
   - "작업이 요청된 경우 즉시 실행" 체크
   - "작업이 실행 중이면 다음 규칙 적용": **"새 인스턴스 병렬 실행"** 선택

### 3. 환경 변수 설정

작업 스케줄러에서 환경 변수를 설정하려면:

1. 작업 스케줄러에서 생성한 작업 선택
2. **속성** → **일반** 탭
3. **"가장 높은 수준의 권한으로 실행"** 체크 (선택사항)
4. **동작** 탭 → 작업 편집
5. **"새로 만들기"** → **"환경 변수 추가"** 클릭
6. 다음 변수 추가:
   - `DISCORD_BOT_TOKEN`: 디스코드 봇 토큰
   - `GITHUB_TOKEN`: GitHub PAT
   - `GITHUB_REPO`: `rldhkstopic/rldhkstopic.github.io`
   - `DISCORD_GUILD_ID`: 디스코드 서버 ID (선택사항)

또는 `.env` 파일 사용 (더 간단):

1. `local_bot/.env` 파일 생성 (이미 있다면 스킵)
2. 환경 변수 대신 `.env` 파일 사용

### 4. 봇 재시작 스크립트 (선택사항)

봇이 크래시되면 자동으로 재시작하는 스크립트:

`local_bot/auto_restart_bot.bat`:

```batch
@echo off
:loop
cd /d "%~dp0"
python discord_interface.py
echo 봇이 종료되었습니다. 5초 후 재시작합니다...
timeout /t 5 /nobreak >nul
goto loop
```

이 스크립트를 작업 스케줄러에 등록하면 봇이 종료되어도 자동으로 재시작됩니다.

## 🔧 문제 해결

### 봇이 시작되지 않음

1. Python 경로 확인:
   ```powershell
   where python
   ```

2. 작업 스케줄러 → 작업 실행 기록 확인
3. 로그 파일 확인 (봇에 로깅 기능 추가 필요)

### 봇이 자동으로 종료됨

1. 작업 스케줄러 → 작업 속성 → **"작업이 실행 중이면 다음 규칙 적용"** 확인
2. PC 절전 모드 해제
3. Windows 업데이트로 인한 재부팅 확인

### 환경 변수가 적용되지 않음

1. `.env` 파일 사용 (더 안정적)
2. 또는 작업 스케줄러에서 환경 변수 직접 설정

## 💡 추가 팁

### PC 절전 모드 방지

1. **전원 옵션** 설정:
   - Windows 설정 → 시스템 → 전원 및 절전
   - "화면 끄기": **"안 함"**
   - "절전 모드": **"안 함"**

2. **절전 모드 해제** (명령어):
   ```powershell
   powercfg /change standby-timeout-ac 0
   powercfg /change standby-timeout-dc 0
   ```

### 봇 상태 모니터링

작업 스케줄러에서 작업 실행 기록을 확인하여 봇이 정상 실행 중인지 확인할 수 있습니다.

## 🎉 완료

설정이 완료되면:
- PC 부팅 시 자동으로 봇이 시작됩니다
- PC가 켜져있는 한 봇이 항상 실행됩니다
- 완전 무료로 사용 가능합니다!

