# Vercel 빌드 스킵 설정 가이드

Vercel이 워크플로우가 생성한 커밋에 대해 불필요하게 빌드를 시도하는 것을 방지하는 방법입니다.

## 문제 상황

- `auto-post.yml`, `daily-diary.yml`, `update-analytics.yml` 워크플로우가 커밋을 생성하고 push
- Vercel이 모든 push에 대해 자동으로 배포를 시도
- 워크플로우가 생성한 커밋도 Vercel 배포를 트리거하여 불필요한 빌드 발생

## 해결 방법

### 방법 1: 커밋 메시지에 `[skip vercel]` 추가 (권장)

워크플로우의 모든 커밋 메시지에 `[skip vercel]` 또는 `[vercel skip]`을 추가합니다.

**현재 적용된 워크플로우:**
- `auto-post.yml`: 모든 커밋 메시지에 `[skip ci] [skip vercel]` 포함
- `daily-diary.yml`: 모든 커밋 메시지에 `[skip ci] [skip vercel]` 포함
- `update-analytics.yml`: 커밋 메시지에 `[skip ci] [skip vercel]` 포함

### 방법 2: Vercel 대시보드에서 Ignore Build Step 설정

1. **Vercel 대시보드 접속**
   - 프로젝트 선택
   - **Settings** → **General** 탭

2. **Build & Development Settings** 섹션
   - **Ignore Build Step** 필드 찾기

3. **스크립트 추가**
   ```bash
   # 커밋 메시지에 [skip vercel]이 포함되어 있으면 빌드 스킵
   if [[ "$VERCEL_GIT_COMMIT_MESSAGE" == *"[skip vercel]"* ]] || [[ "$VERCEL_GIT_COMMIT_MESSAGE" == *"[vercel skip]"* ]]; then
     echo "⏭️ Skipping Vercel build due to [skip vercel] in commit message"
     exit 1
   fi
   
   # analytics 파일만 변경된 경우 빌드 스킵
   git diff --name-only HEAD^ HEAD | grep -E "^(_data/analytics\.json|assets/analytics\.json)$" && exit 1
   
   # 처리된 요청 파일만 변경된 경우 빌드 스킵
   git diff --name-only HEAD^ HEAD | grep -E "^(_auto_post_requests_processed/|_auto_post_results/)" && exit 1
   
   # 그 외의 경우 빌드 진행
   exit 0
   ```

4. **저장**
   - 설정 저장 후 다음 배포부터 적용

### 방법 3: Vercel CLI로 설정 (선택사항)

```bash
vercel env add IGNORE_BUILD_STEP
# 값: 위의 스크립트 내용
```

## 확인 방법

1. **워크플로우 실행 후 확인**
   - `auto-post` 또는 `daily-diary` 워크플로우 실행
   - 생성된 커밋 메시지에 `[skip vercel]` 포함 확인

2. **Vercel 대시보드 확인**
   - **Deployments** 탭에서 해당 커밋의 배포 상태 확인
   - "Skipped" 또는 "Ignored" 상태로 표시되어야 함

## 참고사항

- `[skip ci]`: GitHub Actions 워크플로우 스킵
- `[skip vercel]` 또는 `[vercel skip]`: Vercel 빌드 스킵
- 두 태그를 모두 사용하면 GitHub Actions와 Vercel 모두 스킵됨

## 문제 해결

### 여전히 Vercel이 빌드를 시도하는 경우

1. **커밋 메시지 확인**
   - `[skip vercel]` 또는 `[vercel skip]`이 정확히 포함되어 있는지 확인
   - 대소문자 구분 없음

2. **Vercel 설정 확인**
   - Ignore Build Step 스크립트가 올바르게 설정되었는지 확인
   - 스크립트가 `exit 1`을 반환해야 빌드가 스킵됨

3. **Vercel 캐시 클리어**
   - Settings → General → **Clear Build Cache** 실행

4. **수동 테스트**
   ```bash
   # 테스트 커밋 생성
   git commit --allow-empty -m "Test [skip vercel]"
   git push origin main
   # Vercel 대시보드에서 빌드가 스킵되는지 확인
   ```
