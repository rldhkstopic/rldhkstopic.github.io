# 일상 기록 앱 (Daily Logger)

하루 동안 일어난 일들을 기록하고, 자동으로 일기로 변환하는 Flutter 앱입니다.

## 🚀 시작하기

### 1. Flutter PATH 설정

Flutter를 설치한 후, PATH에 Flutter를 추가해야 합니다.

**Windows:**
1. Flutter 설치 경로 확인 (예: `C:\src\flutter\bin`)
2. 시스템 환경 변수에 `Path`에 Flutter bin 경로 추가
3. 새 터미널 열기

**확인:**
```bash
flutter doctor
```

### 2. 프로젝트 설정

```bash
cd flutter_app
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

⚠️ **보안**: `config.dart`는 `.gitignore`에 포함되어 있어 커밋되지 않습니다.

### 4. JSON 직렬화 코드 생성

```bash
flutter pub run build_runner build
```

### 5. 앱 실행

```bash
flutter run
```

## 📱 기능

- 📝 일상 기록 입력 (생각날 때마다 기록)
- 📋 오늘 기록한 일들 목록 보기
- 🔄 GitHub에 자동 동기화
- 📅 매일 자정에 기록들을 취합하여 일기 자동 작성

## 🐛 문제 해결

### Flutter 명령어를 찾을 수 없음

Flutter가 PATH에 추가되지 않았을 수 있습니다.

1. Flutter 설치 경로 확인
2. 시스템 환경 변수에 `Path`에 Flutter bin 경로 추가
3. 터미널 재시작

### `flutter pub get` 오류

```bash
flutter clean
flutter pub get
```

### JSON 직렬화 오류

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## 📚 상세 가이드

전체 가이드는 `docs/DAILY_LOGGER_APP_GUIDE.md`를 참고하세요.
