# 빌드 오류 해결 가이드

Jekyll 빌드나 Vercel 배포 중 발생하는 오류를 해결하는 방법입니다.

## 일반적인 빌드 오류

### 1. Liquid 템플릿 오류

**증상:**
```
Liquid Exception: Liquid syntax error
```

**원인:**
- `absolute_url` 필터 사용 시 `site.url`이 설정되지 않음
- 변수 참조 오류
- 조건문 문법 오류

**해결:**
- `site.url`이 `_config.yml`에 설정되어 있는지 확인
- `absolute_url` 대신 `site.url`과 `relative_url` 조합 사용
- 변수 존재 여부 확인 후 사용 (`{% if variable %}`)

### 2. hreflang 태그 오류

**증상:**
```
Error: undefined method `absolute_url' for nil:NilClass
```

**해결:**
```liquid
{% if site.url %}
  <link rel="alternate" hreflang="en" href="{{ site.url }}{{ site.baseurl }}{{ page.url | relative_url }}">
{% endif %}
```

### 3. 파일명 중복 문제

**증상:**
- 파일명에 날짜가 중복됨 (예: `2026-01-09-2026-01-09-일기.md`)

**원인:**
- 제목에 날짜가 포함되어 있고, 파일명 생성 시 날짜를 제거하지 않음

**해결:**
- `_create_slug` 함수에서 `[YYYY-MM-DD]` 형식의 날짜를 제거하도록 수정
- 제목에서 날짜 부분을 제거한 후 슬러그 생성

### 4. Front Matter 파싱 오류

**증상:**
```
YAML Exception: could not find expected ':'
```

**원인:**
- Front Matter에 잘못된 YAML 문법
- 특수문자 이스케이프 누락

**해결:**
- 따옴표로 감싸기: `title: "제목 [특수문자]"` 
- YAML 문법 검증 도구 사용

## Vercel 빌드 오류

### 1. 빌드 타임아웃

**증상:**
```
Build exceeded maximum build time
```

**해결:**
- `vercel.json`에서 빌드 명령어 최적화
- 불필요한 파일 제외 (`.vercelignore` 또는 `_config.yml`의 `exclude`)

### 2. 의존성 설치 실패

**증상:**
```
Error installing gems
```

**해결:**
- `Gemfile.lock`이 최신인지 확인
- Vercel 대시보드에서 Ruby 버전 확인
- `.ruby-version` 파일 추가

### 3. 빌드 스킵 설정

**Vercel 대시보드 설정:**
1. Settings → General → Build & Development Settings
2. "Ignore Build Step" 필드에 다음 추가:

```bash
# 커밋 메시지에 [skip vercel]이 포함되어 있으면 빌드 스킵
if [[ "$VERCEL_GIT_COMMIT_MESSAGE" == *"[skip vercel]"* ]] || [[ "$VERCEL_GIT_COMMIT_MESSAGE" == *"[vercel skip]"* ]]; then
  echo "⏭️ Skipping Vercel build"
  exit 1
fi

# analytics 파일만 변경된 경우 빌드 스킵
git diff --name-only HEAD^ HEAD | grep -E "^(_data/analytics\.json|assets/analytics\.json)$" && exit 1

# 처리된 요청 파일만 변경된 경우 빌드 스킵
git diff --name-only HEAD^ HEAD | grep -E "^(_auto_post_requests_processed/|_auto_post_results/)" && exit 1

# 그 외의 경우 빌드 진행
exit 0
```

## 로컬 빌드 테스트

빌드 오류를 확인하려면 로컬에서 테스트:

```bash
# 의존성 설치
bundle install

# 빌드 테스트
bundle exec jekyll build

# 빌드 결과 확인
ls _site
```

## 디버깅 팁

1. **빌드 로그 확인**
   - GitHub Actions: Actions 탭 → 실패한 워크플로우 → 로그 확인
   - Vercel: Deployments 탭 → 실패한 배포 → Build Logs 확인

2. **단계별 확인**
   - Front Matter 문법 확인
   - Liquid 템플릿 문법 확인
   - 파일 경로 확인

3. **최소 재현 사례**
   - 문제가 되는 파일만 남기고 나머지 제외
   - 점진적으로 파일 추가하며 오류 재현
