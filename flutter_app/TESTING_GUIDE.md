# Flutter 앱 테스트 및 디버깅 가이드

## 🚀 빠른 시작

### 1. JSON 직렬화 코드 생성

```bash
cd flutter_app
dart run build_runner build --delete-conflicting-outputs
```

또는 (watch 모드로 자동 재생성):
```bash
dart run build_runner watch
```

### 2. GitHub Token 설정 (선택)

`lib/config/config.dart` 파일을 열고 GitHub Token을 입력하세요:

```dart
static const String githubToken = 'ghp_your_token_here';
```

⚠️ **테스트용**: Token 없이도 앱은 실행되지만, GitHub API 호출은 실패합니다.

### 3. 앱 실행

#### 기본 실행
```bash
flutter run
```

#### 특정 디바이스에서 실행
```bash
# 연결된 디바이스 목록 확인
flutter devices

# 특정 디바이스에서 실행
flutter run -d <device_id>
```

#### 웹에서 실행 (개발용)
```bash
flutter run -d chrome
```

#### 안드로이드 에뮬레이터
```bash
# 에뮬레이터 목록 확인
flutter emulators

# 에뮬레이터 실행
flutter emulators --launch <emulator_id>

# 에뮬레이터에서 앱 실행
flutter run
```

#### iOS 시뮬레이터 (Mac만 가능)
```bash
open -a Simulator
flutter run
```

---

## 🐛 디버깅 방법

### 1. Hot Reload (핫 리로드)

앱이 실행 중일 때:
- `r` 키: Hot Reload (빠른 재시작)
- `R` 키: Hot Restart (완전 재시작)
- `q` 키: 종료

### 2. 디버그 모드 실행

```bash
flutter run --debug
```

**디버그 기능:**
- Breakpoint 설정 가능
- 변수 값 확인
- 콘솔 로그 출력 (`print()`)
- Flutter DevTools 사용 가능

### 3. Flutter DevTools 사용

```bash
# DevTools 자동 실행
flutter run --debug

# 또는 별도로 실행
flutter pub global activate devtools
flutter pub global run devtools
```

**DevTools 기능:**
- 위젯 트리 탐색
- 성능 프로파일링
- 메모리 분석
- 네트워크 모니터링

### 4. 로그 확인

코드에서 `print()` 사용:
```dart
print('디버그 메시지: $variable');
```

콘솔에서 확인:
```bash
flutter run
# 또는
flutter logs
```

### 5. 에러 확인

```bash
# 상세한 에러 정보
flutter run --verbose

# 릴리즈 모드에서 테스트
flutter run --release
```

---

## 🧪 테스트 방법

### 1. 단위 테스트

```bash
flutter test
```

### 2. 위젯 테스트

```bash
flutter test test/widget_test.dart
```

### 3. 통합 테스트

```bash
flutter test integration_test/
```

---

## 📱 실제 디바이스 연결

### Android

1. USB 디버깅 활성화 (설정 > 개발자 옵션)
2. USB로 연결
3. `flutter devices`로 확인
4. `flutter run` 실행

### iOS (Mac만 가능)

1. Xcode에서 시뮬레이터 실행 또는 실제 기기 연결
2. `flutter devices`로 확인
3. `flutter run` 실행

---

## 🔧 문제 해결

### 앱이 실행되지 않음

```bash
# Flutter 정리
flutter clean
flutter pub get

# 다시 실행
flutter run
```

### 빌드 오류

```bash
# 캐시 삭제
flutter clean

# 의존성 재설치
flutter pub get

# JSON 직렬화 코드 재생성
dart run build_runner build --delete-conflicting-outputs
```

### GitHub API 오류

1. `lib/config/config.dart`에서 Token 확인
2. Token에 `repo` 권한이 있는지 확인
3. 네트워크 연결 확인
4. 콘솔 로그에서 에러 메시지 확인

### Hot Reload가 작동하지 않음

- `R` 키로 Hot Restart 시도
- 앱을 완전히 종료하고 다시 실행

---

## 💡 개발 팁

### 1. 개발 중 빠른 반복

```bash
# Watch 모드로 실행 (파일 변경 시 자동 재시작)
dart run build_runner watch
```

### 2. 릴리즈 빌드 테스트

```bash
# Android APK 생성
flutter build apk --release

# iOS 빌드 (Mac만)
flutter build ios --release
```

### 3. 성능 프로파일링

```bash
flutter run --profile
```

### 4. 코드 분석

```bash
flutter analyze
```

---

## 📝 테스트 시나리오

### 기본 기능 테스트

1. **앱 실행 확인**
   ```bash
   flutter run
   ```

2. **기록 추가 테스트**
   - "새 기록" 버튼 클릭
   - 내용 입력
   - 저장 확인

3. **기록 목록 확인**
   - 홈 화면에서 기록 목록 표시 확인
   - 시간순 정렬 확인

4. **GitHub 동기화 테스트**
   - 기록 저장 후 GitHub 리포지토리 확인
   - `_daily_logs/YYYY-MM-DD/` 폴더에 JSON 파일 생성 확인

### 에러 케이스 테스트

1. **네트워크 오류**
   - 인터넷 연결 끊기
   - 기록 저장 시도
   - 에러 메시지 확인

2. **GitHub Token 오류**
   - 잘못된 Token 입력
   - 기록 저장 시도
   - 에러 메시지 확인

---

## 🎯 다음 단계

1. ✅ `dart run build_runner build` 실행
2. ✅ `lib/config/config.dart`에 GitHub Token 설정
3. ✅ `flutter run`으로 앱 실행
4. ✅ 기본 기능 테스트
5. ✅ 실제 디바이스에서 테스트

