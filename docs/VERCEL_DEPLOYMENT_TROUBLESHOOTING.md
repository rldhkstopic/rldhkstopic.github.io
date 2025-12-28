# Vercel 배포 오류 해결 가이드

Vercel 배포 중 발생하는 일반적인 오류와 해결 방법을 정리한다.

## 배포 오류 확인 방법

1. **Vercel 대시보드 접속**
   - 프로젝트 선택 → **Deployments** 탭
   - 실패한 배포 클릭

2. **빌드 로그 확인**
   - **Build Logs** 섹션 확장
   - 오류 메시지 확인

## 일반적인 오류 및 해결 방법

### 1. 빌드 명령어 오류

**증상:**
```
Error: Command "bundle exec jekyll build" exited with 1
```

**해결:**
- 로컬에서 빌드 테스트: `bundle exec jekyll build`
- `vercel.json`의 `buildCommand` 확인
- Gemfile과 Gemfile.lock이 올바른지 확인

### 2. Ruby 버전 문제

**증상:**
```
Ruby version mismatch
```

**해결:**
- `.ruby-version` 파일 생성 (선택사항):
  ```
  3.3.0
  ```
- 또는 Vercel이 자동으로 Ruby 버전을 감지하도록 둠

### 3. 의존성 설치 실패

**증상:**
```
Error installing gems
```

**해결:**
- `Gemfile.lock`이 최신인지 확인
- 로컬에서 `bundle install` 성공하는지 확인
- `vercel.json`의 `installCommand` 확인

### 4. 출력 디렉토리 누락

**증상:**
```
Error: Output directory "_site" not found
```

**해결:**
- 빌드가 실제로 `_site` 디렉토리를 생성하는지 확인
- `vercel.json`의 `outputDirectory` 확인
- 로컬 빌드 후 `_site` 디렉토리가 생성되는지 확인

### 5. vercel.json 설정 오류

**증상:**
```
Invalid vercel.json configuration
```

**해결:**
- JSON 문법 오류 확인
- `analytics`와 `speedInsights`는 vercel.json에 설정하지 않음 (대시보드에서 활성화)
- 필수 필드만 포함:
  - `buildCommand`
  - `outputDirectory`
  - `installCommand` (선택사항)

### 6. 환경 변수 누락

**증상:**
```
Environment variable not found
```

**해결:**
- Vercel 대시보드 → Settings → Environment Variables 확인
- 필요한 환경 변수가 모두 설정되었는지 확인
- Production, Preview 환경 모두 확인

## 로컬 빌드 테스트

배포 전에 로컬에서 빌드를 테스트한다:

```bash
# 의존성 설치
bundle install

# 빌드 테스트
bundle exec jekyll build

# 빌드 결과 확인
ls _site
```

로컬 빌드가 성공하면 Vercel 배포도 대부분 성공한다.

## vercel.json 최소 설정

문제가 지속되면 최소 설정으로 시작:

```json
{
  "buildCommand": "bundle install && bundle exec jekyll build",
  "outputDirectory": "_site"
}
```

## 추가 리소스

- [Vercel 배포 문제 해결](https://vercel.com/docs/deployments/troubleshoot-a-build)
- [Vercel 오류 목록](https://vercel.com/docs/errors/error-list)
- [Jekyll 배포 가이드](https://jekyllrb.com/docs/deployment/vercel/)

