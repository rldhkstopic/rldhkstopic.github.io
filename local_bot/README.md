# Discord 봇 사용 가이드

## 환경 변수 설정 (Windows)

### 방법 1: PowerShell에서 임시 설정 (봇 실행 중에만 유효)

봇을 실행할 PowerShell 창에서:

```powershell
$env:DISCORD_BOT_TOKEN = "여기에_디스코드_봇_토큰_입력"
$env:GITHUB_TOKEN = "여기에_GitHub_PAT_입력"
$env:GITHUB_REPO = "rldhkstopic/rldhkstopic.github.io"
# 선택사항: 길드 ID (빠른 슬래시 커맨드 등록용)
$env:DISCORD_GUILD_ID = "여기에_디스코드_서버_ID_입력"
```

그 다음 봇 실행:
```powershell
python discord_interface.py
```

### 방법 2: 시스템 환경 변수로 영구 설정 (재부팅 후에도 유지)

1. **Windows 검색**에서 "환경 변수" 입력 → "시스템 환경 변수 편집" 클릭
2. **환경 변수** 버튼 클릭
3. **사용자 변수** 섹션에서 **새로 만들기** 클릭
4. 다음 변수들을 각각 추가:
   - 변수 이름: `DISCORD_BOT_TOKEN`, 값: `디스코드_봇_토큰`
   - 변수 이름: `GITHUB_TOKEN`, 값: `GitHub_PAT`
   - 변수 이름: `GITHUB_REPO`, 값: `rldhkstopic/rldhkstopic.github.io`
   - (선택) 변수 이름: `DISCORD_GUILD_ID`, 값: `디스코드_서버_ID`

5. **확인** 클릭 후 PowerShell 창을 다시 열어야 적용됩니다.

### 방법 3: .env 파일 사용 (권장, 가장 안전)

1. `local_bot/` 폴더에 `.env` 파일 생성:

```env
DISCORD_BOT_TOKEN=여기에_디스코드_봇_토큰_입력
GITHUB_TOKEN=여기에_GitHub_PAT_입력
GITHUB_REPO=rldhkstopic/rldhkstopic.github.io
DISCORD_GUILD_ID=여기에_디스코드_서버_ID_입력
```

2. `.env` 파일을 `.gitignore`에 추가 (절대 커밋하지 마세요!)

3. `discord_interface.py`를 수정하여 `python-dotenv`로 `.env` 파일을 읽도록 변경:

```python
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드
```

## 의존성 설치

```bash
pip install discord.py PyGithub python-dotenv
```

## 봇 실행

```bash
cd local_bot
python discord_interface.py
```

## 작동 방식

1. **Discord 봇 (로컬 PC)**: 
   - `/write` 명령어로 요청 입력
   - GitHub 리포지토리에 `_auto_post_requests/request_*.json` 파일 커밋

2. **GitHub Actions (자동 실행)**:
   - `_auto_post_requests/` 폴더에 새 파일이 생기면 (또는 스케줄 실행 시)
   - `auto_post.py`가 요청을 읽어서 글 생성
   - Writer → Reviewer → Validator → PostCreator 순서로 처리
   - 최종적으로 `_posts/*.md` 파일 생성 및 커밋

## ☁️ 클라우드 배포 (항상 실행)

로컬에서 매번 실행하는 대신, 클라우드에 배포하여 봇을 항상 온라인 상태로 유지할 수 있습니다.

**자세한 배포 가이드**: [DEPLOYMENT.md](./DEPLOYMENT.md)

### 빠른 시작 (Railway 권장)

1. [Railway](https://railway.app)에 GitHub 계정으로 로그인
2. **"New Project"** → **"Deploy from GitHub repo"** 선택
3. 저장소 선택 후 `local_bot` 폴더를 루트로 설정
4. **Variables** 탭에서 환경 변수 설정:
   - `DISCORD_BOT_TOKEN`
   - `GITHUB_TOKEN`
   - `GITHUB_REPO`
   - `DISCORD_GUILD_ID` (선택사항)
5. 배포 완료 후 봇이 자동으로 실행됩니다!

### 다른 배포 옵션

- **Render**: 무료 티어 제공 (슬리프 모드 가능)
- **Fly.io**: 무료 티어 제공
- 자세한 내용은 [DEPLOYMENT.md](./DEPLOYMENT.md) 참고

## 주의사항

⚠️ **토큰은 절대 공개하지 마세요!**
- `.env` 파일은 `.gitignore`에 추가
- GitHub에 커밋하지 마세요
- 다른 사람과 공유하지 마세요
- 클라우드 배포 시 환경 변수로만 설정하세요

