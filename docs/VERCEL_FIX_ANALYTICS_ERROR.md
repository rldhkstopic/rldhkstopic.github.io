# Vercel Analytics 오류 해결 방법

`vercel.json` schema validation 오류: "should NOT have additional property `analytics`" 해결 방법

## 문제 원인

`vercel.json`에 `analytics`와 `speedInsights` 속성이 포함되어 있었지만, 이 속성들은 Vercel의 vercel.json 스키마에서 지원하지 않습니다.

## 해결 방법

### 방법 1: Vercel 대시보드에서 수동 재배포 (권장)

1. **Vercel 대시보드 접속**
   - 프로젝트 선택
   - **Deployments** 탭으로 이동

2. **최신 배포 확인**
   - 최신 배포의 커밋 해시 확인
   - `2dbd258` 또는 그 이후 커밋인지 확인

3. **수동 재배포**
   - 최신 배포의 **...** 메뉴 클릭
   - **Redeploy** 선택
   - 또는 **Deployments** 탭에서 **Redeploy** 버튼 클릭

### 방법 2: 빈 커밋으로 재배포 트리거

최신 커밋이 배포되지 않았다면, 빈 커밋을 만들어 재배포를 트리거할 수 있습니다:

```bash
git commit --allow-empty -m "Trigger Vercel redeploy"
git push origin main
```

### 방법 3: Vercel 프로젝트 설정 확인

1. **Settings** → **General** 탭
2. **Build & Development Settings** 확인
3. **Override** 설정이 있는지 확인
4. 필요시 **Clear Build Cache** 실행

## 확인 사항

### 현재 vercel.json 상태

최신 커밋의 `vercel.json`에는 다음만 포함되어야 합니다:

```json
{
  "buildCommand": "bundle install && bundle exec jekyll build",
  "outputDirectory": "_site",
  "installCommand": "gem install bundler && bundle install",
  "framework": null,
  "headers": [...]
}
```

**포함되면 안 되는 것:**
- `analytics`
- `speedInsights`

### Analytics & Speed Insights 활성화

이 기능들은 **Vercel 대시보드**에서 활성화해야 합니다:

1. **Analytics**: 대시보드 → Analytics 탭 → Enable Web Analytics
2. **Speed Insights**: 대시보드 → Speed Insights 탭 → Enable Speed Insights

`vercel.json`에 설정하지 않습니다.

## 배포 상태 확인

배포가 성공했는지 확인:

1. Vercel 대시보드 → **Deployments** 탭
2. 최신 배포의 상태 확인
3. **Ready** 상태면 성공
4. 빌드 로그에서 오류가 없는지 확인

## 문제가 지속되는 경우

1. **빌드 캐시 삭제**
   - Settings → General → Clear Build Cache

2. **프로젝트 재연결**
   - Settings → General → Disconnect
   - GitHub 저장소 다시 연결

3. **Vercel CLI로 배포 테스트**
   ```bash
   npm i -g vercel
   vercel --prod
   ```

