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
    // OAuth App이 설정되지 않은 경우, 토큰 입력 폼 표시
    const showTokenForm = document.getElementById('show-token-form');
    if (showTokenForm) {
      showTokenForm.click();
    }
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
// 참고: https://dev-watnu.tistory.com/58
async function exchangeCodeForToken(code) {
  // 서버리스 함수 엔드포인트 목록 (여러 플랫폼 지원)
  const serverlessEndpoints = [
    '/.netlify/functions/github-oauth',  // Netlify Functions
    '/api/github-oauth',                  // Vercel Functions
    '/api/oauth/github',                  // 일반적인 API 경로
    'https://api.rldhkstopic.github.io/github-oauth' // 외부 API (예시)
  ];

  // 각 엔드포인트를 순차적으로 시도
  for (const endpoint of serverlessEndpoints) {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ code }),
        mode: 'cors',
        credentials: 'omit'
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.access_token) {
          // 토큰 저장 및 인증 완료
          if (window.authManager) {
            window.authManager.saveToken(data.access_token, true);
            window.authManager.setAuthenticated(true, true);
            window.location.href = '/editor/';
            return; // 성공 시 종료
          }
        }
      }
    } catch (error) {
      console.log(`Endpoint ${endpoint} failed, trying next...`, error);
      continue; // 다음 엔드포인트 시도
    }
  }

  // 모든 서버리스 함수가 실패한 경우, 대체 방법 안내
  showTokenExchangeFallback();
}

// 서버리스 함수가 없을 때 대체 방법 안내
function showTokenExchangeFallback() {
  const errorDiv = document.getElementById('login-error');
  if (errorDiv) {
    errorDiv.innerHTML = `
      <div class="oauth-fallback">
        <h3 style="margin-bottom: 1rem; color: var(--text-primary);">OAuth 인증 완료</h3>
        <p style="margin-bottom: 1rem; color: var(--text-secondary);">
          GitHub에서 인증은 완료되었지만, code를 access token으로 교환하려면 서버가 필요합니다.
        </p>
        <p style="margin-bottom: 1rem; color: var(--text-secondary);"><strong>다음 중 하나를 선택하세요:</strong></p>
        <ol style="margin-left: 1.5rem; margin-bottom: 1rem; color: var(--text-secondary); line-height: 1.8;">
          <li style="margin-bottom: 0.5rem;">
            <strong>서버리스 함수 설정 (권장):</strong><br>
            Netlify Functions나 Vercel Functions를 설정하여 자동으로 토큰을 받을 수 있습니다.<br>
            <a href="/docs/GITHUB_OAUTH_GUIDE.md" target="_blank" style="color: var(--accent-color);">설정 가이드 보기</a>
          </li>
          <li>
            <strong>Personal Access Token 사용:</strong><br>
            <a href="https://github.com/settings/tokens/new" target="_blank" style="color: var(--accent-color);">GitHub에서 Personal Access Token 생성</a> 후 아래에 입력하세요.
          </li>
        </ol>
        <div class="token-input-fallback" style="margin-top: 1rem;">
          <input 
            type="password" 
            id="fallback-token-input" 
            class="form-input" 
            placeholder="Personal Access Token 입력 (ghp_...)"
            style="margin-bottom: 0.5rem;"
          />
          <button 
            type="button" 
            class="btn btn-primary btn-block" 
            onclick="window.useFallbackToken && window.useFallbackToken()"
          >
            토큰으로 로그인
          </button>
        </div>
      </div>
    `;
    errorDiv.style.display = 'block';
  }
  
  // URL 정리 (code 파라미터 제거)
  window.history.replaceState({}, document.title, '/admin/');
}

// 대체 토큰 사용 함수
async function useFallbackToken() {
  const tokenInput = document.getElementById('fallback-token-input');
  if (!tokenInput) return;
  
  const token = tokenInput.value.trim();
  if (!token) {
    alert('토큰을 입력하세요.');
    return;
  }

  if (window.authManager) {
    const validation = await window.authManager.validateToken(token);
    if (validation.valid) {
      window.authManager.saveToken(token, true);
      window.authManager.setAuthenticated(true, true);
      window.location.href = '/editor/';
    } else {
      alert(`토큰 검증 실패: ${validation.error}`);
    }
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
window.useFallbackToken = useFallbackToken;

