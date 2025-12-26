// GitHub OAuth 인증 처리

const GITHUB_OAUTH_CONFIG = {
  clientId: (window.ADMIN_CONFIG_OVERRIDE && window.ADMIN_CONFIG_OVERRIDE.githubOAuth && window.ADMIN_CONFIG_OVERRIDE.githubOAuth.clientId) || '',
  redirectUri: window.location.origin + '/admin/',
  scope: 'repo',
  state: generateRandomState()
};

// 랜덤 state 생성 (CSRF 방지)
function generateRandomState() {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

// GitHub OAuth 로그인 시작
function startGitHubOAuth() {
  if (!GITHUB_OAUTH_CONFIG.clientId) {
    // OAuth App이 설정되지 않은 경우, 기존 토큰 입력 방식으로 폴백
    window.location.href = '/admin/';
    return;
  }

  // state를 세션스토리지에 저장
  sessionStorage.setItem('oauth_state', GITHUB_OAUTH_CONFIG.state);

  // GitHub OAuth 인증 페이지로 리다이렉트
  const authUrl = `https://github.com/login/oauth/authorize?` +
    `client_id=${GITHUB_OAUTH_CONFIG.clientId}&` +
    `redirect_uri=${encodeURIComponent(GITHUB_OAUTH_CONFIG.redirectUri)}&` +
    `scope=${GITHUB_OAUTH_CONFIG.scope}&` +
    `state=${GITHUB_OAUTH_CONFIG.state}`;

  window.location.href = authUrl;
}

// OAuth callback 처리
function handleOAuthCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const error = urlParams.get('error');

  // 에러 처리
  if (error) {
    const errorDiv = document.getElementById('login-error');
    if (errorDiv) {
      errorDiv.textContent = `인증 실패: ${error}`;
      errorDiv.style.display = 'block';
    }
    // URL에서 code와 state 제거
    window.history.replaceState({}, document.title, '/admin/');
    return;
  }

  // state 검증
  const savedState = sessionStorage.getItem('oauth_state');
  if (!state || state !== savedState) {
    const errorDiv = document.getElementById('login-error');
    if (errorDiv) {
      errorDiv.textContent = '보안 검증 실패. 다시 시도해주세요.';
      errorDiv.style.display = 'block';
    }
    window.history.replaceState({}, document.title, '/admin/');
    return;
  }

  sessionStorage.removeItem('oauth_state');

  // code가 있으면 서버리스 함수로 토큰 교환 시도
  if (code) {
    exchangeCodeForToken(code);
  }
}

// code를 access token으로 교환
// 주의: 이 함수는 서버 사이드에서 실행되어야 합니다.
// GitHub Pages는 정적 사이트이므로, Netlify Functions나 Vercel Functions 같은 서버리스 함수가 필요합니다.
async function exchangeCodeForToken(code) {
  // 서버리스 함수 엔드포인트 (예: Netlify Functions)
  // 실제 구현 시 이 URL을 서버리스 함수 엔드포인트로 변경해야 합니다.
  const exchangeUrl = '/.netlify/functions/github-oauth'; // 예시

  try {
    const response = await fetch(exchangeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ code })
    });

    if (!response.ok) {
      throw new Error('Token exchange failed');
    }

    const data = await response.json();
    
    if (data.access_token) {
      // 토큰 저장 및 인증 완료
      if (window.authManager) {
        window.authManager.saveToken(data.access_token, true);
        window.authManager.setAuthenticated(true, true);
        window.location.href = '/editor/';
      }
    } else {
      throw new Error('No access token in response');
    }
  } catch (error) {
    console.error('Token exchange error:', error);
    
    // 서버리스 함수가 없는 경우, 사용자에게 Personal Access Token 생성 안내
    const errorDiv = document.getElementById('login-error');
    if (errorDiv) {
      errorDiv.innerHTML = `
        <strong>OAuth 토큰 교환 실패</strong><br>
        서버리스 함수가 설정되지 않았습니다.<br>
        <a href="https://github.com/settings/tokens/new" target="_blank">GitHub에서 Personal Access Token을 생성</a>하여 직접 입력하거나,<br>
        Netlify Functions나 Vercel Functions를 설정하여 OAuth를 완전히 자동화할 수 있습니다.
      `;
      errorDiv.style.display = 'block';
    }
    
    // URL 정리
    window.history.replaceState({}, document.title, '/admin/');
  }
}

// 글쓰기 버튼 표시/숨김 (인증 상태에 따라)
function updateWriteButtonVisibility() {
  const writeBtn = document.getElementById('write-btn');
  if (!writeBtn) return;

  // 항상 표시하되, 인증 상태에 따라 링크 변경
  writeBtn.style.display = 'inline-flex';
  
  // 인증 상태 확인
  if (window.authManager && window.authManager.isAuthenticated()) {
    writeBtn.href = '/editor/';
    writeBtn.title = '글쓰기';
  } else {
    writeBtn.href = '/admin/';
    writeBtn.title = '로그인';
  }
}

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
  // OAuth callback 처리
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('code') || urlParams.get('error')) {
    handleOAuthCallback();
  }

  // 글쓰기 버튼 표시 업데이트
  updateWriteButtonVisibility();
  
  // 인증 상태 변경 감지 (다른 탭에서 로그인/로그아웃 시)
  window.addEventListener('storage', (e) => {
    if (e.key === 'admin_github_token' || e.key === 'admin_authenticated') {
      updateWriteButtonVisibility();
    }
  });
});

// 전역으로 export
window.startGitHubOAuth = startGitHubOAuth;
window.handleOAuthCallback = handleOAuthCallback;

