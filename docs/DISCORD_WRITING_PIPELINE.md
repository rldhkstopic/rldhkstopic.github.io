# Discord - 글쓰기 파이프라인 전체 가이드

이 문서는 Discord 봇을 통한 블로그 글 작성 파이프라인의 전체 흐름과 구조를 설명합니다.

---

## 📋 전체 아키텍처

```
[사용자] 
  ↓ Discord 슬래시 명령어
[Discord 봇 (로컬 PC)]
  ↓ GitHub API로 JSON 파일 커밋
[GitHub 리포지토리]
  ↓ 파일 변경 감지
[GitHub Actions 워크플로우]
  ↓ AI 에이전트 파이프라인 실행
[글 생성 및 검증]
  ↓ Discord 웹훅 알림
[Discord "포스팅-현황" 채널]
  ↓ 자동 커밋/푸시
[블로그 게시]
```

---

## 🔄 상세 파이프라인 흐름

### Phase 1: Discord 봇 (로컬 PC)

**파일:** `local_bot/discord_interface.py`

#### 1.1 사용자 입력 (`/write` 명령어)

**슬래시 명령어:**
- `/write` - 새 글 요청
- `/list` - 대기 중인 요청 목록
- `/status` - 최근 워크플로우 상태
- `/help` - 사용 가이드

**입력 필드 (Modal):**
- **Category**: dev, study, daily, essay 중 선택
- **Topic**: 글 제목/주제 (필수, 최대 120자)
- **Situation**: 상황/문제 설명 (선택, 최대 2000자)
- **Action**: 해결 방법/시도한 내용 (선택, 최대 2000자)
- **Memo**: 기타 메모나 참고 링크 (선택, 최대 2000자)

#### 1.2 요청 파일 생성 및 커밋

**함수:** `commit_request_to_github(payload: dict)`

**동작:**
1. JSON 페이로드 생성:
   ```json
   {
     "Category": "daily",
     "Topic": "임팩트 팩터",
     "Situation": "상황 설명...",
     "Action": "액션 설명...",
     "Memo": "메모...",
     "source": "discord",
     "requested_at": "2026-01-03T12:00:00Z",
     "user": "사용자명#1234"
   }
   ```

2. GitHub에 파일 커밋:
   - 경로: `_auto_post_requests/request_YYYYMMDD_HHMMSS.json`
   - 커밋 메시지: `[REQUEST] {Topic}`

3. 워크플로우 트리거 파일 업데이트:
   - 파일: `.github/force-auto-post-run`
   - 내용: 요청 시간 및 파일명

#### 1.3 실시간 워크플로우 모니터링

**함수:** `monitor_workflow_status(interaction, request_filename)`

**동작:**
- 10초마다 GitHub Actions 워크플로우 상태 확인
- Discord 메시지 실시간 업데이트
- 최대 10분(600초) 모니터링
- 상태: `queued` → `in_progress` → `completed` (success/failure)

**Discord Embed 업데이트:**
- 현재 상태 (큐 대기 중 / 실행 중 / 완료)
- 경과 시간
- GitHub Actions 로그 링크
- 성공 시 생성된 포스트 링크

---

### Phase 2: GitHub Actions 워크플로우

**파일:** `.github/workflows/auto-post.yml`

#### 2.1 트리거 조건

**자동 실행:**
- 스케줄: 매일 오전 7시 (KST, UTC 22:00)
- 파일 변경 감지:
  - `.github/force-auto-post-run` 파일 변경
  - `_auto_post_requests/**` 폴더에 새 파일 추가

**수동 실행:**
- `workflow_dispatch` (GitHub Actions UI에서)

#### 2.2 실행 환경

- **OS**: Ubuntu Latest
- **Python**: 3.11
- **의존성:**
  - `.github/scripts/requirements.txt` 패키지
  - `requests` (Discord 알림용)

**환경 변수:**
- `GEMINI_API_KEY`: Gemini API 키
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `DISCORD_WEBHOOK_URL`: Discord 웹훅 URL

#### 2.3 스크립트 실행

```bash
python .github/scripts/auto_post.py
```

---

### Phase 3: AI 에이전트 파이프라인

**파일:** `.github/scripts/auto_post.py`

#### 3.1 요청 큐 처리

**함수:** `_load_request()`

**동작:**
1. `_auto_post_requests/` 폴더에서 JSON 파일 검색
2. 파일명 기준 오름차순 정렬 (가장 오래된 요청 우선)
3. 첫 번째 파일 읽기 및 파싱
4. 요청 정보 로깅:
   - 발견된 요청 파일 수
   - 처리할 요청 파일명
   - 주제, 카테고리

**요청 모드 vs 자동 모드:**
- **요청 모드**: `_auto_post_requests/`에 파일이 있으면 우선 처리
- **자동 모드**: 요청이 없으면 `TopicCollectorAgent`로 주제 자동 수집

#### 3.2 에이전트 파이프라인

**에이전트 순서:**

1. **TopicCollectorAgent** (자동 모드만)
   - 외부 소스에서 주제 수집
   - 중복 제목 필터링

2. **ResearcherAgent**
   - 요청 모드: Situation/Action/Memo를 조사 데이터로 사용
   - 자동 모드: 주제에 대한 심층 조사 수행
   - 출력: `raw_research`, `sources`

3. **AnalystAgent**
   - 조사 데이터 분석
   - 인사이트 도출
   - 출력: `insights`

4. **WriterAgent**
   - 카테고리별 프롬프트 적용
   - Daily: 1인칭 시점, 감정 묘사, 현장감
   - Dev/Study/Document: 건조하고 분석적인 문체
   - 한글 검증 (150자 이상, 20% 비율, 종결어미 검사)
   - 출력: 초안 본문

5. **ReviewerAgent**
   - 문체 통일 ("~다."로 끝나는 문장)
   - 금지어 제거 ("결론적으로", "마지막으로" 등)
   - 이모지 제거
   - 카테고리별 검토 규칙 적용
   - 출력: 교정된 본문

6. **ValidatorAgent**
   - 스타일 가이드 준수 여부 검증
   - 경고 및 오류 수집
   - 출력: 검증 결과

7. **PostCreatorAgent**
   - Front Matter 생성
   - 마크다운 파일 저장
   - 경로: `_posts/YYYY-MM-DD-title.md`
   - 출력: 파일 경로

#### 3.3 후처리

1. **요청 파일 이동**
   - `_auto_post_requests/request_*.json`
   - → `_auto_post_requests_processed/request_*.json`
   - 중복 처리 방지

2. **처리 결과 저장**
   - `_auto_post_results/result_{request_id}.json`
   - 상태, 주제, 파일 경로, 오류 정보 저장

---

### Phase 4: Discord 알림

**파일:** `.github/scripts/discord_notifier.py`

#### 4.1 성공 알림

**함수:** `notify_post_success()`

**전송 내용:**
- **제목**: "✅ 포스트 생성 완료"
- **설명**: 주제명 + 블로그 링크
- **필드:**
  - 요청 출처 (Discord 등)
  - 카테고리
  - 파일명
  - 블로그 링크 (자동 생성)
  - **글 내용** (최대 1500자, Front Matter 제거, 코드 블록/이미지 간소화)

**블로그 URL 생성:**
```
파일명: 2026-01-03-임팩트-팩터.md
→ URL: https://rldhkstopic.github.io/blog/2026/01/03/임팩트-팩터/
```

#### 4.2 실패 알림

**함수:** `notify_post_failure()`

**전송 내용:**
- **제목**: "❌ 포스트 생성 실패"
- **설명**: 주제명 + 오류 안내
- **필드:**
  - 요청 출처
  - 오류 메시지 (최대 1000자)

---

### Phase 5: Git 커밋 및 푸시

**워크플로우 단계:** "Commit and push"

**동작 순서:**
1. 원격 변경사항 fetch
2. 로컬 변경사항 모두 커밋 (`git add -A`)
3. 원격 변경사항 pull (merge 전략)
4. 충돌 시 자동 생성 포스트 우선 (`--ours`)
5. 생성된 포스트 및 처리 파일 추가
6. 커밋 및 push

**커밋 메시지:**
- `Add auto-generated post for YYYY-MM-DD`

---

## 📁 디렉토리 구조

```
프로젝트 루트/
├── local_bot/                    # Discord 봇 (로컬 PC)
│   ├── discord_interface.py     # 봇 메인 스크립트
│   ├── .env                      # 환경 변수 (gitignore)
│   └── README.md                 # 봇 사용 가이드
│
├── _auto_post_requests/          # 요청 큐 (대기 중)
│   └── request_YYYYMMDD_HHMMSS.json
│
├── _auto_post_requests_processed/ # 처리 완료된 요청
│   └── request_YYYYMMDD_HHMMSS.json
│
├── _auto_post_results/           # 처리 결과
│   └── result_request_YYYYMMDD_HHMMSS.json
│
├── _posts/                       # 생성된 포스트
│   └── YYYY-MM-DD-title.md
│
└── .github/
    ├── workflows/
    │   └── auto-post.yml         # GitHub Actions 워크플로우
    └── scripts/
        ├── auto_post.py          # 메인 파이프라인
        ├── discord_notifier.py   # Discord 알림
        ├── reviewer_agent.py     # 검토 에이전트
        └── agents/
            ├── writer.py         # 작성 에이전트
            ├── researcher.py     # 조사 에이전트
            ├── analyst.py        # 분석 에이전트
            ├── validator.py      # 검증 에이전트
            └── post_creator.py  # 포스트 생성 에이전트
```

---

## 🔑 환경 변수 및 시크릿

### Discord 봇 (로컬 PC)

**필수:**
- `DISCORD_BOT_TOKEN`: Discord 봇 토큰
- `GITHUB_TOKEN`: GitHub Personal Access Token (repo 권한)

**선택:**
- `DISCORD_GUILD_ID`: Discord 서버 ID (빠른 슬래시 명령 등록용)
- `GITHUB_REPO`: 리포지토리 (기본: `rldhkstopic/rldhkstopic.github.io`)

### GitHub Actions

**GitHub Secrets:**
- `GEMINI_API_KEY`: Gemini API 키
- `GITHUB_TOKEN`: 자동 생성 (워크플로우용)
- `DISCORD_WEBHOOK_URL`: Discord 웹훅 URL ("포스팅-현황" 채널)

---

## 📊 카테고리별 처리 방식

### Daily (일상/회고)

**특징:**
- 1인칭 시점 ('나', '내가', '나는')
- 감정 묘사 필수
- 구체적인 현장감 묘사
- 구조: [상황] → [행동] → [회고]

**프롬프트:**
- `WriterAgent._get_daily_prompt()` 사용
- `ReviewerAgent`에서 Daily 전용 검토 규칙 적용

### Dev (개발)

**특징:**
- 기술 중심, 논리적 흐름
- 코드/트러블슈팅 단계별 정리
- 건조하고 분석적인 문체

### Study (학습)

**특징:**
- 개념 설명 중심
- 체계적 정리
- 명확한 단계/예시 포함

### Document/Essay (분석/에세이)

**특징:**
- 데이터/근거 기반
- 비판적 분석
- 참조 형식 ([^n])
- 전문가 의견 인용 (blockquote)

---

## 🔍 한글 검증 로직

**파일:** `.github/scripts/agents/writer.py`

**검증 항목:**

1. **기본 한글 비율 검사**
   - 최소 150자 이상
   - 한글 비율 20% 이상 (코드 블록 제외)

2. **종결어미 검사**
   - 문장의 50% 이상이 '~다.'로 끝나야 함
   - 제목/헤더/리스트는 제외

3. **앞/뒤 분할 검사**
   - 뒷부분 25%에도 한글 20자 이상 필요
   - Language Switching 방지

**디버깅 로그:**
- 생성된 내용 미리보기
- 한글 수 (전체/코드 제외)
- 한글 비율
- 검증 실패 시 샘플 출력

---

## 🚨 오류 처리

### Discord 봇 오류

- **토큰 오류**: `discord.LoginFailure` 예외 처리
- **GitHub API 오류**: Discord에 오류 메시지 전송
- **워크플로우 모니터링 타임아웃**: 10분 후 타임아웃 메시지

### GitHub Actions 오류

- **한글 생성 실패**: 최대 3회 재시도, 모델 폴백 체인
- **검증 실패**: 상세 디버깅 로그 출력, 임시 파일 저장
- **Merge 충돌**: 자동 생성 포스트 우선 (`--ours`)
- **Push 실패**: 재시도 로직

### Discord 알림 오류

- **웹훅 전송 실패**: 경고 로그만 출력, 프로세스는 계속 진행

---

## 📈 모니터링 및 로깅

### Discord 봇 로그

- 요청 파일 커밋 성공/실패
- 워크플로우 상태 실시간 업데이트
- 오류 발생 시 상세 메시지

### GitHub Actions 로그

- 각 에이전트 단계별 진행 상황
- 한글 검증 상세 통계
- 요청 파일 처리 정보
- 오류 발생 시 스택 트레이스

### Discord 알림

- 포스트 생성 성공/실패
- 글 내용 미리보기
- 블로그 링크
- 처리 시간 및 상태

---

## 🔧 설정 및 커스터마이징

### 카테고리별 프롬프트 수정

**파일:** `.github/scripts/agents/writer.py`

- `_get_daily_prompt()`: Daily 카테고리 프롬프트
- `_get_system_prompt(category)`: 카테고리별 시스템 프롬프트

### 검토 규칙 수정

**파일:** `.github/scripts/reviewer_agent.py`

- `review()` 메서드의 카테고리별 규칙 수정
- 금지어 목록 추가/수정

### 한글 검증 기준 조정

**파일:** `.github/scripts/agents/writer.py`

- `_is_korean_output()` 메서드의 검증 기준 수정
- 한글 최소 수, 비율, 종결어미 비율 조정

---

## 📝 사용 예시

### 1. Discord에서 글 요청

```
/write category:daily
```

**Modal 입력:**
- Topic: "임팩트 팩터"
- Situation: "학술지의 영향력을 평가하는 지표에 대해 알아보고 싶다"
- Action: "논문 검색 및 관련 자료 조사"
- Memo: "https://example.com/impact-factor"

### 2. 처리 과정

1. Discord 봇이 `_auto_post_requests/request_20260103_120000.json` 생성
2. GitHub Actions가 파일 변경 감지하여 워크플로우 실행
3. `auto_post.py`가 요청 파일 읽기
4. AI 에이전트 파이프라인 실행 (Writer → Reviewer → Validator)
5. `_posts/2026-01-03-임팩트-팩터.md` 생성
6. Discord "포스팅-현황" 채널에 알림 전송 (글 내용 포함)
7. GitHub에 자동 커밋/푸시
8. 블로그에 게시

### 3. Discord에서 확인

**"포스팅-현황" 채널에서:**
- ✅ 포스트 생성 완료 알림
- 제목, 카테고리, 블로그 링크
- **글 내용 (최대 1500자)**
- 요청 출처 (Discord)

---

## 🎯 주요 특징

1. **완전 자동화**: Discord 입력 → 블로그 게시까지 자동
2. **실시간 모니터링**: Discord에서 워크플로우 상태 실시간 확인
3. **카테고리별 최적화**: 각 카테고리에 맞는 프롬프트 및 검토 규칙
4. **품질 보장**: 한글 검증, 문체 통일, 금지어 제거
5. **오류 복구**: 자동 재시도, 모델 폴백, 충돌 해결

---

## 📚 관련 문서

- [카테고리별 작성 가이드](./CATEGORY_WRITING_GUIDES.md)
- [자동 포스팅 가이드](./AUTO_POSTING_GUIDE.md)
- [Discord 봇 사용 가이드](../local_bot/README.md)

