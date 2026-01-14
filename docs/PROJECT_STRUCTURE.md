# 프로젝트 구조 문서

이 문서는 프로젝트의 파일 구조와 각 디렉토리의 역할을 설명합니다.

## 현재 구조 (리팩토링 전)

```
.
├── _auto_post_requests/          # 자동 포스팅 요청 파일
├── _auto_post_requests_processed/ # 처리된 요청 파일
├── _auto_post_results/            # 처리 결과 파일
├── _config.yml                   # Jekyll 설정
├── _daily_logs/                  # 일일 로그 파일
├── _data/                        # Jekyll 데이터 파일
├── _layouts/                     # Jekyll 레이아웃
├── _posts/                       # 블로그 포스트
├── .github/                      # GitHub Actions 워크플로우
│   └── scripts/                  # 자동화 스크립트
├── api/                          # Vercel 서버리스 함수
├── assets/                       # 정적 자산 (CSS, JS, 이미지)
├── daily_logger_app/             # Flutter 일기 앱
├── docs/                         # 프로젝트 문서
├── flutter_app/                  # Flutter 앱
├── local_bot/                    # Discord 봇
├── pages/                        # Jekyll 페이지
├── scripts/                      # PowerShell 스크립트
├── vercel/                       # Vercel 설정
└── [기타 Jekyll 파일들]
```

## 문제점

1. **루트 디렉토리가 복잡함**: 자동화, 앱, 봇, 스크립트가 모두 루트에 있음
2. **자동화 관련 파일 분산**: `_auto_post_*` 디렉토리들이 루트에 있음
3. **앱들이 루트에 있음**: `daily_logger_app`, `flutter_app`이 루트에 있음
4. **스크립트 분산**: `.github/scripts`와 `scripts/`가 분리되어 있음

## 개선된 구조 (리팩토링 후)

```
.
├── _config.yml                   # Jekyll 설정
├── _data/                        # Jekyll 데이터 파일
├── _layouts/                     # Jekyll 레이아웃
├── _posts/                       # 블로그 포스트
├── api/                          # Vercel 서버리스 함수
├── assets/                       # 정적 자산 (CSS, JS, 이미지)
├── pages/                        # Jekyll 페이지
│
├── automation/                    # 자동화 관련 파일 통합
│   ├── requests/                 # 자동 포스팅 요청 파일
│   ├── processed/                # 처리된 요청 파일
│   ├── results/                 # 처리 결과 파일
│   ├── logs/                     # 일일 로그 파일
│   └── scripts/                  # 자동화 스크립트 (.github/scripts에서 이동)
│
├── apps/                         # 애플리케이션들
│   ├── daily_logger/             # Flutter 일기 앱
│   └── flutter_app/              # Flutter 앱
│
├── bots/                         # 봇 관련
│   └── discord/                  # Discord 봇 (local_bot에서 이동)
│
├── scripts/                      # 유틸리티 스크립트 (통합)
│   ├── test-*.ps1                # 테스트 스크립트
│   └── check-*.ps1               # 체크 스크립트
│
├── docs/                         # 프로젝트 문서
│   └── index.md                  # 문서 인덱스
│
├── .github/                      # GitHub Actions 워크플로우
│   └── workflows/                # 워크플로우 파일만 유지
│
└── vercel/                       # Vercel 설정
```

## 디렉토리 설명

### Jekyll 관련 (루트)
- `_config.yml`: Jekyll 설정 파일
- `_data/`: Jekyll 데이터 파일 (YAML, JSON)
- `_layouts/`: HTML 레이아웃 템플릿
- `_posts/`: 블로그 포스트 (Markdown)
- `pages/`: Jekyll 페이지 (HTML)
- `assets/`: 정적 자산 (CSS, JS, 이미지)
- `api/`: Vercel 서버리스 함수

### automation/ (자동화)
- `requests/`: 자동 포스팅 요청 파일 (JSON)
- `processed/`: 처리된 요청 파일
- `results/`: 처리 결과 파일
- `logs/`: 일일 로그 파일
- `scripts/`: 자동화 스크립트 (Python)

### apps/ (애플리케이션)
- `daily_logger/`: Flutter 일기 앱
- `flutter_app/`: Flutter 앱

### bots/ (봇)
- `discord/`: Discord 봇 (Python)

### scripts/ (유틸리티 스크립트)
- PowerShell/Batch 스크립트들
- 테스트, 체크, 유틸리티 스크립트

### docs/ (문서)
- 프로젝트 문서 (Markdown)
- `index.md`: 문서 인덱스

### .github/ (GitHub)
- `workflows/`: GitHub Actions 워크플로우 파일

## 리팩토링 계획

1. ✅ 구조 분석 및 문서화
2. ⏳ 자동화 파일 이동 (`_auto_post_*` → `automation/`)
3. ⏳ 앱 이동 (`daily_logger_app`, `flutter_app` → `apps/`)
4. ⏳ 봇 이동 (`local_bot` → `bots/discord/`)
5. ⏳ 스크립트 통합 (`.github/scripts` → `automation/scripts/`)
6. ⏳ 경로 참조 업데이트 (워크플로우, 스크립트 등)
7. ⏳ 문서 인덱스 생성

## 주의사항

리팩토링 시 다음 파일들의 경로 참조를 업데이트해야 합니다:

1. **GitHub Actions 워크플로우** (`.github/workflows/*.yml`)
2. **Python 스크립트** (`automation/scripts/*.py`)
3. **PowerShell 스크립트** (`scripts/*.ps1`)
4. **Jekyll 설정** (`_config.yml` - 필요시)
5. **문서** (`docs/*.md` - 경로 참조 업데이트)
