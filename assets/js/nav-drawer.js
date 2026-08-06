/**
 * 모바일 네비게이션 드로어
 *
 * 768px 이하에서 상단 네비 링크가 CSS 로 숨겨지므로, 햄버거 버튼으로 여는
 * 드로어가 유일한 메뉴 접근 경로다. 열림/닫힘 상태를 aria 속성과 함께 관리한다.
 */
(function () {
  'use strict';

  var toggle = document.getElementById('navMenuToggle');
  var drawer = document.getElementById('navDrawer');
  var backdrop = document.getElementById('navDrawerBackdrop');
  var closeBtn = document.getElementById('navDrawerClose');

  if (!toggle || !drawer || !backdrop) return;

  var DESKTOP_MIN_WIDTH = 769; // main.css 의 max-width:768px 미디어쿼리와 맞춘 값
  var lastFocused = null;

  function isOpen() {
    return drawer.classList.contains('is-open');
  }

  function open() {
    if (isOpen()) return;
    lastFocused = document.activeElement;

    drawer.classList.add('is-open');
    backdrop.classList.add('is-open');
    document.body.classList.add('nav-drawer-open');

    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', '메뉴 닫기');
    drawer.setAttribute('aria-hidden', 'false');

    // 열리자마자 드로어 안으로 포커스를 옮겨 키보드 사용자가 바로 이동할 수 있게 한다.
    var first = drawer.querySelector('.nav-drawer-close, .nav-drawer-link');
    if (first) first.focus();
  }

  function close(restoreFocus) {
    if (!isOpen()) return;

    drawer.classList.remove('is-open');
    backdrop.classList.remove('is-open');
    document.body.classList.remove('nav-drawer-open');

    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', '메뉴 열기');
    drawer.setAttribute('aria-hidden', 'true');

    if (restoreFocus !== false) {
      (lastFocused && lastFocused.focus ? lastFocused : toggle).focus();
    }
    lastFocused = null;
  }

  toggle.addEventListener('click', function () {
    isOpen() ? close() : open();
  });

  backdrop.addEventListener('click', function () {
    close();
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', function () {
      close();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) close();
  });

  // 드로어 안에서 탭이 밖으로 새어나가지 않도록 가둔다.
  drawer.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab' || !isOpen()) return;

    var items = drawer.querySelectorAll('.nav-drawer-close, .nav-drawer-link');
    if (!items.length) return;

    var first = items[0];
    var last = items[items.length - 1];

    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });

  // 링크를 눌러 페이지를 이동할 때는 포커스를 되돌리지 않는다(이동해 버리므로).
  drawer.addEventListener('click', function (e) {
    if (e.target.closest('.nav-drawer-link')) close(false);
  });

  // 드로어를 열어둔 채 가로 모드로 돌리면 데스크톱 네비가 다시 보이므로 닫아준다.
  window.addEventListener('resize', function () {
    if (window.innerWidth >= DESKTOP_MIN_WIDTH && isOpen()) close(false);
  });
})();
