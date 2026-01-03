# 일상 기록 앱 (Daily Logger)

하루 동안 일어난 일들을 기록하고, 자동으로 일기로 변환하는 Flutter 앱입니다.

## 기능

- 📝 일상 기록 입력 (생각날 때마다 기록)
- 📋 오늘 기록한 일들 목록 보기
- 🔄 GitHub에 자동 동기화
- 📅 매일 자정에 기록들을 취합하여 일기 자동 작성

## 설정

### 1. 환경 변수 설정

`lib/config/config.dart` 파일을 생성하고 다음 내용을 입력:

```dart
class Config {
  static const String githubToken = 'YOUR_GITHUB_TOKEN';
  static const String githubRepo = 'rldhkstopic/rldhkstopic.github.io';
  static const String logsDir = '_daily_logs';
}
```

⚠️ **보안**: GitHub Token은 절대 공개 저장소에 커밋하지 마세요!

### 2. 의존성 설치

```bash
flutter pub get
```

### 3. 앱 실행

```bash
flutter run
```

## 사용 방법

1. 앱을 열고 "새 기록 추가" 버튼 클릭
2. 일어난 일을 간단히 기록
3. 기록이 자동으로 GitHub에 저장됨
4. 매일 자정에 모든 기록이 취합되어 일기로 작성됨

## 작동 원리

1. **기록 저장**: 앱에서 입력한 기록이 `_daily_logs/YYYY-MM-DD/` 폴더에 JSON 파일로 저장
2. **자동 일기 작성**: GitHub Actions가 매일 자정에 실행되어 당일 기록들을 취합
3. **일기 생성**: AI 에이전트가 기록들을 정리하여 Daily 카테고리 일기로 작성

