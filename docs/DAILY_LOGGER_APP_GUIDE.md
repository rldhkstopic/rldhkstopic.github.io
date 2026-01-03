# 일상 기록 앱 (Daily Logger) 가이드

Flutter로 구현된 일상 기록 앱과 자동 일기 작성 시스템 가이드입니다.

## 📱 앱 개요

**목적**: 하루 동안 일어난 일들을 간단히 기록하고, 자동으로 일기로 변환

**특징**:
- 📝 생각날 때마다 간단히 기록
- 📋 오늘 기록한 일들 목록 보기
- 🔄 GitHub에 자동 동기화
- 📅 매일 자정에 기록들을 취합하여 일기 자동 작성

---

## 🚀 시작하기

### 1. Flutter 설치

Flutter가 설치되어 있지 않다면:
- [Flutter 공식 사이트](https://flutter.dev/docs/get-started/install)에서 설치
- `flutter doctor` 명령어로 설치 확인

### 2. 프로젝트 설정

```bash
cd daily_logger_app
flutter pub get
```

### 3. GitHub Token 설정

`lib/config/config.dart` 파일을 수정:

```dart
class Config {
  static const String githubToken = 'YOUR_GITHUB_TOKEN_HERE';
  static const String githubRepo = 'rldhkstopic/rldhkstopic.github.io';
  static const String logsDir = '_daily_logs';
}
```

**GitHub Token 발급:**
1. GitHub Settings > Developer settings > Personal access tokens
2. Generate new token (Classic)
3. `repo` 권한 체크
4. 토큰 복사하여 `config.dart`에 입력

⚠️ **보안**: `config.dart`는 `.gitignore`에 포함되어 있어 커밋되지 않습니다.

### 4. 앱 실행

```bash
flutter run
```

---

## 📖 사용 방법

### 기록 추가

1. 앱 실행 후 "새 기록" 버튼 클릭
2. 내용 입력 (필수)
3. 선택 사항 입력:
   - 기분 (예: 기쁨, 슬픔, 평온)
   - 위치 (예: 집, 회사, 카페)
   - 태그 (쉼표로 구분, 예: 작업, 운동, 독서)
4. "저장하기" 버튼 클릭
5. 기록이 자동으로 GitHub에 저장됨

### 기록 보기

- 홈 화면에서 오늘 기록한 일들을 시간순으로 확인
- 각 기록의 시간, 내용, 기분, 위치, 태그 표시
- 기록 삭제 가능

### 기록 새로고침

- 상단 새로고침 버튼으로 최신 기록 불러오기
- 아래로 당겨서 새로고침 (Pull-to-refresh)

---

## 🔄 자동 일기 작성 시스템

### 작동 원리

1. **기록 저장**: 앱에서 입력한 기록이 `_daily_logs/YYYY-MM-DD/` 폴더에 JSON 파일로 저장
2. **자동 실행**: GitHub Actions가 매일 자정(KST 00:00)에 실행
3. **기록 취합**: 당일 기록들을 시간순으로 정리
4. **일기 작성**: AI 에이전트가 기록들을 바탕으로 Daily 카테고리 일기 작성
5. **자동 게시**: 생성된 일기가 `_posts/` 폴더에 저장되고 블로그에 게시

### 일기 작성 에이전트

**파일**: `.github/scripts/daily_diary_agent.py`

**처리 과정:**
1. `_daily_logs/YYYY-MM-DD/` 폴더에서 기록 로드
2. 기록들을 시간순으로 취합
3. `WriterAgent`로 일기 초안 작성 (Daily 카테고리 프롬프트 사용)
4. `ReviewerAgent`로 문체 통일 및 검토
5. `ValidatorAgent`로 검증
6. `PostCreatorAgent`로 마크다운 파일 생성

### GitHub Actions 워크플로우

**파일**: `.github/workflows/daily-diary.yml`

**실행 시점:**
- 자동: 매일 자정 (KST 00:00, UTC 15:00)
- 수동: GitHub Actions UI에서 `workflow_dispatch`

**수동 실행 시 날짜 지정:**
- Input: `target_date` (YYYY-MM-DD 형식)
- 예: `2026-01-02` → 2026년 1월 2일 기록으로 일기 작성

---

## 📁 데이터 구조

### 기록 파일 형식

**경로**: `_daily_logs/YYYY-MM-DD/{timestamp}.json`

**JSON 구조:**
```json
{
  "id": "1704326400000",
  "content": "오늘 드론쇼를 보러 갔다",
  "timestamp": "2026-01-03T12:00:00Z",
  "mood": "기쁨",
  "location": "부산 광안리",
  "tags": ["여행", "드론쇼"]
}
```

### 일기 파일 형식

**경로**: `_posts/YYYY-MM-DD-{날짜}-일기.md`

**Front Matter:**
```yaml
---
layout: post
title: "2026년 01월 03일 일기"
date: 2026-01-03 00:00:00 +0900
author: rldhkstopic
category: daily
tags: ["일기", "일상"]
views: 0
---
```

---

## 🎨 앱 구조

```
daily_logger_app/
├── lib/
│   ├── main.dart                 # 앱 진입점
│   ├── config/
│   │   └── config.dart           # GitHub 설정
│   ├── models/
│   │   ├── daily_log.dart        # 기록 모델
│   │   └── daily_log.g.dart     # JSON 직렬화 (자동 생성)
│   ├── services/
│   │   └── github_service.dart   # GitHub API 연동
│   ├── providers/
│   │   └── log_provider.dart     # 상태 관리
│   └── screens/
│       ├── home_screen.dart      # 홈 화면 (기록 목록)
│       └── add_log_screen.dart   # 기록 추가 화면
├── pubspec.yaml                  # Flutter 의존성
└── README.md                     # 앱 가이드
```

---

## 🔧 커스터마이징

### 기록 필드 추가

`lib/models/daily_log.dart`에 필드 추가:

```dart
final String? weather; // 날씨

// toJson, fromJson도 업데이트 필요
```

### 일기 프롬프트 수정

`.github/scripts/daily_diary_agent.py`의 `aggregate_logs()` 함수에서 기록 취합 방식 수정

### 일기 제목 형식 변경

`.github/scripts/daily_diary_agent.py`의 `create_diary_topic()` 함수 수정

---

## 🐛 문제 해결

### 기록이 저장되지 않음

1. GitHub Token이 올바른지 확인
2. Token에 `repo` 권한이 있는지 확인
3. 네트워크 연결 확인
4. 앱 로그 확인 (콘솔 출력)

### 일기가 생성되지 않음

1. GitHub Actions 로그 확인
2. `_daily_logs/` 폴더에 기록이 있는지 확인
3. `GEMINI_API_KEY`가 설정되어 있는지 확인

### 앱이 실행되지 않음

```bash
flutter clean
flutter pub get
flutter run
```

---

## 📚 관련 문서

- [카테고리별 작성 가이드](./CATEGORY_WRITING_GUIDES.md)
- [Discord 글쓰기 파이프라인](./DISCORD_WRITING_PIPELINE.md)

