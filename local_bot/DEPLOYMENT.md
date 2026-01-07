# Discord 봇 배포 가이드

디스코드 봇을 항상 실행되도록 클라우드에 배포하는 방법입니다.

## 🎯 Fly.io 배포 (가장 추천 - 무료로 항상 켜놓기 가능)

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

## 🔄 Render 배포 (무료 티어 제한 있음)

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

## 🚀 Railway 배포 (유료 플랜 필요)

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

## 📝 주의사항 및 무료 티어 제한

### ⚠️ 중요: 무료 티어의 현실

**Railway 무료 티어:**
- 월 $1 크레딧 = 약 **62.5시간** 실행 시간
- 24시간 × 30일 = 720시간이 필요하므로 **한 달 내내 켜놓을 수 없음**
- 약 **8.7일** 정도만 실행 가능
- **10분간 아웃바운드 트래픽이 없으면 슬립 모드** (디스코드 봇은 WebSocket 연결로 인해 슬립되지 않을 수 있음)

**Render 무료 티어:**
- **15분 비활성 시 슬립 모드**로 전환
- 디스코드 봇은 WebSocket 연결이 있어서 슬립되지 않을 수 있음
- 하지만 무료 티어는 **항상 켜놓기 어려움**

**Fly.io 무료 티어:**
- 월 3개 VM (shared-cpu-1x)
- 각 VM은 256MB RAM
- **실제로는 항상 켜놓기 가능**하지만 리소스 제한 있음

### 💡 실제 사용 패턴 고려

디스코드 봇의 특성:
- **WebSocket 연결 유지 필요** → 항상 실행되어야 함
- **실제 CPU/메모리 사용량은 매우 낮음** (대기 상태)
- 명령이 들어올 때만 실제 작업 수행

**문제점:**
- Railway 62.5시간 = 약 8.7일만 실행 가능 → **한 달 내내 켜놓기 불가능**
- Render 슬립 모드 = 디스코드 봇 특성상 슬립되지 않을 수 있지만, 무료 티어 제한 있음

### 🎯 추천 솔루션

1. **Fly.io (가장 추천)**
   - 무료 티어로 **항상 켜놓기 가능**
   - 디스코드 봇에 충분한 리소스
   - 슬립 모드 없음

2. **Render (대안)**
   - 무료 티어 사용 가능하지만 제한 있음
   - 유료 플랜($7/월)으로 업그레이드 시 항상 켜놓기 가능

3. **Railway (비추천 - 무료 티어)**
   - 62.5시간만 가능 → 한 달 내내 켜놓기 불가능
   - 유료 플랜($5/월)으로 업그레이드 필요

4. **로컬 실행 + 자동 재시작**
   - Windows 작업 스케줄러로 PC 켜질 때 자동 실행
   - PC가 항상 켜져있다면 가장 경제적

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

## 💻 Windows 자동 시작 (가장 경제적)

PC가 항상 켜져있다면, Windows 작업 스케줄러를 사용하여 **완전 무료**로 봇을 항상 실행할 수 있습니다.

**자세한 가이드**: [WINDOWS_AUTO_START.md](./WINDOWS_AUTO_START.md)

### 빠른 설정

1. 작업 스케줄러 열기 (`Win + R` → `taskschd.msc`)
2. "기본 작업 만들기" → "로그온할 때" 또는 "컴퓨터 시작 시"
3. Python으로 `discord_interface.py` 실행하도록 설정
4. 환경 변수 설정 또는 `.env` 파일 사용

**장점:**
- 완전 무료
- 항상 켜놓기 가능 (PC가 켜져있는 한)
- 빠른 응답 속도

## 🎉 완료

배포가 완료되면 봇이 항상 온라인 상태로 유지됩니다!

## 📊 플랫폼 비교 요약

| 플랫폼 | 무료 티어 | 항상 켜놓기 | 추천도 |
|--------|----------|------------|--------|
| **Fly.io** | ✅ (월 3개 VM) | ✅ 가능 | ⭐⭐⭐⭐⭐ |
| **Windows 자동 시작** | ✅ 완전 무료 | ✅ 가능 (PC 켜져있는 한) | ⭐⭐⭐⭐⭐ |
| **Render** | ⚠️ 제한 있음 | ⚠️ 슬립 모드 가능 | ⭐⭐⭐ |
| **Railway** | ❌ 62.5시간만 | ❌ 불가능 | ⭐⭐ (유료 필요) |

