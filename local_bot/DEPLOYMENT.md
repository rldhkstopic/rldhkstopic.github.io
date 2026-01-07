# Discord 봇 배포 가이드

디스코드 봇을 항상 실행되도록 클라우드에 배포하는 방법입니다.

## 🚀 Railway 배포 (권장)

Railway는 무료 티어가 있고 디스코드 봇 배포에 최적화되어 있습니다.

### 1. Railway 계정 생성

1. [Railway](https://railway.app)에 접속
2. GitHub 계정으로 로그인
3. "Start a New Project" 클릭

### 2. 프로젝트 배포

#### 방법 1: GitHub 리포지토리에서 배포 (권장)

1. Railway 대시보드에서 **"New Project"** 클릭
2. **"Deploy from GitHub repo"** 선택
3. GitHub 저장소 선택 (또는 이 저장소의 `local_bot` 폴더만 배포)
4. **"Deploy Now"** 클릭

#### 방법 2: 직접 파일 업로드

1. Railway 대시보드에서 **"New Project"** 클릭
2. **"Empty Project"** 선택
3. **"Add Service"** → **"GitHub Repo"** 선택
4. 저장소 선택 후 `local_bot` 폴더를 루트로 설정

### 3. 환경 변수 설정

Railway 대시보드에서 프로젝트 → **Variables** 탭에서 다음 환경 변수 추가:

```
DISCORD_BOT_TOKEN=여기에_디스코드_봇_토큰
GITHUB_TOKEN=여기에_GitHub_PAT
GITHUB_REPO=rldhkstopic/rldhkstopic.github.io
DISCORD_GUILD_ID=여기에_디스코드_서버_ID (선택사항)
```

### 4. 배포 설정

1. 프로젝트 → **Settings** → **Deploy**
2. **Root Directory**를 `local_bot`으로 설정 (전체 저장소를 배포하는 경우)
3. **Start Command**가 `python discord_interface.py`인지 확인

### 5. 배포 확인

1. **Deployments** 탭에서 배포 상태 확인
2. 로그에서 "봇이 준비되었습니다!" 메시지 확인
3. Discord에서 봇이 온라인 상태인지 확인

## 🔄 Render 배포 (대안)

Render도 무료 티어를 제공합니다.

### 1. Render 계정 생성

1. [Render](https://render.com)에 접속
2. GitHub 계정으로 로그인

### 2. 새 Web Service 생성

1. **"New +"** → **"Web Service"** 선택
2. GitHub 저장소 연결
3. 설정:
   - **Name**: `discord-bot` (원하는 이름)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r local_bot/requirements.txt`
   - **Start Command**: `cd local_bot && python discord_interface.py`
   - **Root Directory**: `local_bot` (또는 전체 저장소)

### 3. 환경 변수 설정

**Environment** 탭에서 다음 변수 추가:

```
DISCORD_BOT_TOKEN=여기에_디스코드_봇_토큰
GITHUB_TOKEN=여기에_GitHub_PAT
GITHUB_REPO=rldhkstopic/rldhkstopic.github.io
DISCORD_GUILD_ID=여기에_디스코드_서버_ID (선택사항)
```

### 4. 배포

**"Create Web Service"** 클릭하여 배포 시작

## 🎯 Fly.io 배포 (대안)

Fly.io도 무료 티어를 제공합니다.

### 1. Fly.io CLI 설치

```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### 2. 로그인

```bash
fly auth login
```

### 3. 앱 생성

```bash
cd local_bot
fly launch
```

### 4. 환경 변수 설정

```bash
fly secrets set DISCORD_BOT_TOKEN=여기에_디스코드_봇_토큰
fly secrets set GITHUB_TOKEN=여기에_GitHub_PAT
fly secrets set GITHUB_REPO=rldhkstopic/rldhkstopic.github.io
fly secrets set DISCORD_GUILD_ID=여기에_디스코드_서버_ID
```

### 5. 배포

```bash
fly deploy
```

## 📝 주의사항

1. **무료 티어 제한**:
   - Railway: 월 500시간 무료 (충분함)
   - Render: 무료 티어는 15분 비활성 시 슬리프 모드 (웹훅으로 깨울 수 있음)
   - Fly.io: 월 3개 VM 무료

2. **비용**:
   - Railway: 무료 티어로 충분하지만, 사용량이 많으면 유료 플랜 필요
   - Render: 무료 티어 사용 가능
   - Fly.io: 무료 티어 사용 가능

3. **안정성**:
   - Railway가 가장 안정적이고 디스코드 봇 배포에 최적화됨
   - Render는 무료 티어에서 슬리프 모드로 전환될 수 있음

## 🔧 문제 해결

### 봇이 오프라인 상태

1. Railway/Render/Fly.io 로그 확인
2. 환경 변수가 올바르게 설정되었는지 확인
3. 봇 토큰이 유효한지 확인

### 재시작

- **Railway**: 대시보드에서 **"Restart"** 버튼 클릭
- **Render**: 대시보드에서 **"Manual Deploy"** → **"Deploy latest commit"**
- **Fly.io**: `fly restart` 명령어 실행

### 로그 확인

- **Railway**: 프로젝트 → **Deployments** → 로그 확인
- **Render**: 서비스 → **Logs** 탭
- **Fly.io**: `fly logs` 명령어

## 🎉 완료

배포가 완료되면 봇이 항상 온라인 상태로 유지됩니다!

