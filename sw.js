---
layout: null
sitemap: false
---
/**
 * 서비스 워커 — 오프라인 열람 지원
 *
 * 이 파일은 Jekyll 이 처리한다(front matter 있음). 캐시 이름에 빌드 시각을
 * 박아두므로 새로 배포할 때마다 캐시가 갈리고, 이전 캐시는 activate 에서
 * 지워진다. 따라서 배포 후 사용자가 낡은 CSS 를 보는 문제가 생기지 않는다.
 *
 * 전략
 *   - 페이지 이동: 네트워크 우선 → 실패 시 캐시 → 그래도 없으면 /offline.html
 *   - 같은 출처 정적 파일: stale-while-revalidate (즉시 캐시 응답 + 뒤에서 갱신)
 *   - 외부 CDN(폰트·Prism·MathJax): 캐시 우선 (버전이 URL 에 박힌 불변 자원)
 *   - 애널리틱스: 캐시하지 않음
 */

const BUILD = '{{ site.time | date: "%Y%m%d%H%M%S" }}';
const SHELL_CACHE = `devlogs-shell-${BUILD}`;
const PAGES_CACHE = `devlogs-pages-${BUILD}`;
const ASSETS_CACHE = `devlogs-assets-${BUILD}`;
const VENDOR_CACHE = `devlogs-vendor-${BUILD}`;

const OFFLINE_URL = '/offline.html';

/** 설치 시 미리 받아두는 최소 셸. 실패해도 설치는 진행한다. */
const PRECACHE_URLS = [
  '/',
  '/dev/',
  OFFLINE_URL,
  '/assets/css/main.css',
  '/assets/js/nav-drawer.js',
  '/assets/icons/icon-192.png',
  '/manifest.webmanifest',
];

/** 캐시하면 안 되는 요청 (수집·계측) */
const NEVER_CACHE = [
  'google-analytics.com',
  'googletagmanager.com',
  'analytics.google.com',
  'vercel-insights.com',
  'vitals.vercel-insights.com',
];

self.addEventListener('install', event => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(SHELL_CACHE);
      // 하나라도 실패하면 전체가 실패하는 addAll 대신 개별 처리한다.
      // (오프라인 셸은 없어도 사이트가 동작해야 한다)
      await Promise.all(
        PRECACHE_URLS.map(url =>
          cache.add(new Request(url, { cache: 'reload' })).catch(() => {})
        )
      );
      await self.skipWaiting();
    })()
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    (async () => {
      const keep = new Set([SHELL_CACHE, PAGES_CACHE, ASSETS_CACHE, VENDOR_CACHE]);
      const names = await caches.keys();
      await Promise.all(
        names
          .filter(n => n.startsWith('devlogs-') && !keep.has(n))
          .map(n => caches.delete(n))
      );
      await self.clients.claim();
    })()
  );
});

/** 캐시에 넣어도 되는 응답인지 */
function isCacheable(response) {
  return response && response.status === 200 && response.type === 'basic';
}

/** 페이지 이동: 네트워크 우선 */
async function handleNavigation(request) {
  const cache = await caches.open(PAGES_CACHE);
  try {
    const fresh = await fetch(request);
    if (isCacheable(fresh)) cache.put(request, fresh.clone());
    return fresh;
  } catch (err) {
    // start_url 의 ?source=pwa 같은 쿼리 때문에 어긋나지 않도록 검색어를 무시한다.
    const cached =
      (await cache.match(request, { ignoreSearch: true })) ||
      (await caches.match(request, { ignoreSearch: true }));
    if (cached) return cached;

    const offline = await caches.match(OFFLINE_URL);
    if (offline) return offline;

    return new Response('오프라인입니다.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  }
}

/** 같은 출처 정적 파일: 캐시 즉시 응답 + 뒤에서 갱신 */
async function handleAsset(request) {
  const cache = await caches.open(ASSETS_CACHE);
  // CSS/JS 는 ?v=타임스탬프가 붙으므로 검색어를 무시하고 찾는다.
  const cached = await cache.match(request, { ignoreSearch: true });

  const network = fetch(request)
    .then(response => {
      if (isCacheable(response)) cache.put(request, response.clone());
      return response;
    })
    .catch(() => null);

  return cached || (await network) || Response.error();
}

/** 외부 CDN: 캐시 우선 */
async function handleVendor(request) {
  const cache = await caches.open(VENDOR_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    // CDN 응답은 opaque(type: 'cors'/'opaque')일 수 있어 isCacheable 을 쓰지 않는다.
    if (response && (response.ok || response.type === 'opaque')) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (err) {
    return Response.error();
  }
}

self.addEventListener('fetch', event => {
  const { request } = event;

  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;
  if (NEVER_CACHE.some(host => url.hostname.includes(host))) return;

  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }

  if (url.origin === self.location.origin) {
    event.respondWith(handleAsset(request));
    return;
  }

  event.respondWith(handleVendor(request));
});
