/**
 * 서비스 워커 등록
 *
 * 로컬(localhost/127.0.0.1)과 https 에서만 동작한다.
 * 새 버전이 배포되면 다음 방문 때 자동으로 갈린다.
 */
(function () {
  'use strict';

  if (!('serviceWorker' in navigator)) return;

  var isSecure =
    window.location.protocol === 'https:' ||
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1';

  if (!isSecure) return;

  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).then(
      function (registration) {
        // 새 서비스 워커가 대기 중이면 다음 새로고침에 적용된다.
        registration.addEventListener('updatefound', function () {
          var installing = registration.installing;
          if (!installing) return;
          installing.addEventListener('statechange', function () {
            if (installing.state === 'installed' && navigator.serviceWorker.controller) {
              // 새 콘텐츠 준비됨. 다음 페이지 이동부터 적용.
              document.dispatchEvent(new CustomEvent('pwa:update-ready'));
            }
          });
        });
      },
      function (err) {
        // 등록 실패해도 사이트는 정상 동작해야 하므로 조용히 넘어간다.
        if (window.console && console.warn) {
          console.warn('서비스 워커 등록 실패:', err);
        }
      }
    );
  });
})();
