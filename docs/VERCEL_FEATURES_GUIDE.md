# Vercel 기능 활용 가이드

Jekyll 블로그에 Vercel의 기능을 활용하는 방법을 정리한다.

## 1. Vercel Analytics (웹 분석)

GA4 외에 Vercel의 무료 분석 도구를 추가로 사용할 수 있다.

### 설정 방법

1. Vercel 대시보드 → 프로젝트 → **Analytics** 탭
2. **Enable Web Analytics** 활성화
3. HTML에 스크립트 추가 (선택사항, 자동 주입도 가능)

### 장점

- GA4와 별도로 Vercel 전용 통계 확인
- 실시간 방문자 수, 페이지뷰, 세션 시간 등
- 무료 플랜에서도 사용 가능

## 2. Speed Insights (성능 모니터링)

웹사이트의 Core Web Vitals를 측정하고 개선할 수 있다.

### 설정 방법

1. Vercel 대시보드 → 프로젝트 → **Speed Insights** 탭
2. **Enable Speed Insights** 활성화
3. `_layouts/default.html`에 스크립트 추가:

```html
<script>
  if (window.va) {
    window.va('send', 'pageview');
  }
</script>
```

### 측정 지표

- **LCP (Largest Contentful Paint)**: 로딩 성능
- **FID (First Input Delay)**: 상호작용 반응성
- **CLS (Cumulative Layout Shift)**: 시각적 안정성

## 3. Preview Deployments (미리보기 배포)

Pull Request나 브랜치마다 자동으로 미리보기 URL이 생성된다.

### 활용 방법

1. GitHub에서 PR 생성
2. Vercel이 자동으로 미리보기 배포 생성
3. PR 댓글로 미리보기 URL 공유
4. 실제 배포 전 변경사항 검토

### 장점

- 실제 사이트에 영향 없이 테스트 가능
- 팀원과 변경사항 공유 용이
- 각 PR별로 독립적인 환경 제공

## 4. Image Optimization (이미지 최적화)

Vercel의 이미지 최적화 API를 사용하여 이미지 로딩 속도를 개선할 수 있다.

### 사용 방법

Jekyll에서는 직접 사용하기 어렵지만, 서버리스 함수를 통해 활용 가능:

```javascript
// api/optimize-image.js
export default async function handler(req, res) {
  const { url } = req.query;
  // Vercel Image Optimization API 사용
  // 또는 외부 이미지 최적화 서비스 연동
}
```

## 5. Custom Headers (보안 헤더)

보안을 강화하기 위한 HTTP 헤더를 추가할 수 있다.

### vercel.json 설정 예시

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ]
}
```

## 6. Redirects & Rewrites (URL 리다이렉트)

이전 URL을 새 URL로 리다이렉트하거나 URL을 재작성할 수 있다.

### vercel.json 설정 예시

```json
{
  "redirects": [
    {
      "source": "/old-post",
      "destination": "/new-post",
      "permanent": true
    }
  ],
  "rewrites": [
    {
      "source": "/blog/:slug",
      "destination": "/posts/:slug"
    }
  ]
}
```

## 7. Environment Variables (환경 변수)

빌드 시점이나 런타임에 환경 변수를 사용할 수 있다.

### 활용 예시

- GitHub OAuth 클라이언트 ID/Secret
- API 키
- 빌드 시점 설정값

### 설정 방법

1. Vercel 대시보드 → Settings → Environment Variables
2. 변수 추가 (Production, Preview, Development별로 설정 가능)

## 8. Edge Functions (엣지 함수)

전 세계 엣지 서버에서 실행되는 서버리스 함수로, 더 빠른 응답 속도를 제공한다.

### 활용 예시

- 댓글 시스템
- 좋아요 기능 (현재 localStorage 사용 중, 서버 연동 시)
- 실시간 통계
- API 프록시

### 현재 프로젝트 적용

`api/github-oauth.js`는 이미 서버리스 함수로 구현되어 있다. Edge Functions로 전환하면 더 빠른 응답이 가능하다.

## 9. Custom Domain (커스텀 도메인)

무료로 커스텀 도메인을 연결할 수 있다.

### 설정 방법

1. Vercel 대시보드 → Settings → Domains
2. 도메인 추가
3. DNS 설정 (A 레코드 또는 CNAME)

### 장점

- GitHub Pages와 별도 도메인 사용 가능
- SSL 인증서 자동 발급
- 무료 HTTPS 제공

## 10. Deployment Regions (배포 지역 설정)

한국 사용자를 위한 경우 서울 리전(`icn1`)으로 설정하여 속도 개선 가능.

### 설정 방법

1. Vercel 대시보드 → Settings → General
2. **Region** 설정에서 `Seoul, South Korea (icn1)` 선택

### 성능 영향

- 한국 사용자 기준 응답 시간 단축
- CDN 캐시 효율 향상

## 권장 설정 우선순위

1. **Speed Insights** - 성능 모니터링 (무료, 즉시 적용)
2. **Analytics** - 웹 분석 (GA4 보완)
3. **Custom Headers** - 보안 강화
4. **Preview Deployments** - 개발 워크플로우 개선
5. **Deployment Regions** - 한국 사용자 최적화

## 참고 자료

- [Vercel Analytics 문서](https://vercel.com/docs/analytics)
- [Vercel Speed Insights 문서](https://vercel.com/docs/speed-insights)
- [Vercel Edge Functions 문서](https://vercel.com/docs/functions/edge-functions)

