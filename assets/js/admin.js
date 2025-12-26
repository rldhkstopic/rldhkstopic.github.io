// 관리자 인증 및 GitHub API 연동

const ADMIN_CONFIG = {
  repoOwner: 'rldhkstopic',
  repoName: 'rldhkstopic.github.io',
  branch: 'main',
  postsPath: '_posts',
  adminPassword: (window.ADMIN_CONFIG_OVERRIDE && window.ADMIN_CONFIG_OVERRIDE.adminPassword) || null
};

// GitHub API 기본 URL
const GITHUB_API_BASE = 'https://api.github.com';

// 인증 상태 관리
class AuthManager {
  constructor() {
    this.tokenKey = 'admin_github_token';
    this.passwordKey = 'admin_password_hash';
    this.authKey = 'admin_authenticated';
  }

  // 토큰 저장
  saveToken(token, remember = false) {
    if (remember) {
      localStorage.setItem(this.tokenKey, token);
    } else {
      sessionStorage.setItem(this.tokenKey, token);
    }
  }

  // 토큰 가져오기
  getToken() {
    return localStorage.getItem(this.tokenKey) || sessionStorage.getItem(this.tokenKey);
  }

  // 토큰 삭제
  clearToken() {
    localStorage.removeItem(this.tokenKey);
    sessionStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.authKey);
    sessionStorage.removeItem(this.authKey);
  }

  // 인증 상태 확인
  isAuthenticated() {
    const token = this.getToken();
    if (!token) return false;
    
    // 세션 또는 로컬스토리지에 인증 상태 확인
    return sessionStorage.getItem(this.authKey) === 'true' || 
           localStorage.getItem(this.authKey) === 'true';
  }

  // 인증 상태 설정
  setAuthenticated(value, remember = false) {
    if (remember) {
      localStorage.setItem(this.authKey, value.toString());
    } else {
      sessionStorage.setItem(this.authKey, value.toString());
    }
  }

  // GitHub API로 토큰 검증
  async validateToken(token) {
    try {
      const response = await fetch(`${GITHUB_API_BASE}/user`, {
        method: 'GET',
        headers: {
          'Authorization': `token ${token}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        mode: 'cors', // CORS 명시적 설정
        credentials: 'omit' // 쿠키 전송 안 함
      });

      if (!response.ok) {
        throw new Error('Invalid token');
      }

      const user = await response.json();
      
      // 저장소 접근 권한 확인
      const repoResponse = await fetch(
        `${GITHUB_API_BASE}/repos/${ADMIN_CONFIG.repoOwner}/${ADMIN_CONFIG.repoName}`,
        {
          method: 'GET',
          headers: {
            'Authorization': `token ${token}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
          },
          mode: 'cors',
          credentials: 'omit'
        }
      );

      if (!repoResponse.ok) {
        throw new Error('No repository access');
      }

      return {
        valid: true,
        user: user.login,
        avatar: user.avatar_url
      };
    } catch (error) {
      return {
        valid: false,
        error: error.message
      };
    }
  }
}

// GitHub API 클라이언트
class GitHubClient {
  constructor(token) {
    this.token = token;
    this.baseURL = `${GITHUB_API_BASE}/repos/${ADMIN_CONFIG.repoOwner}/${ADMIN_CONFIG.repoName}`;
  }

  // API 요청 헤더
  getHeaders() {
    return {
      'Authorization': `token ${this.token}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    };
  }

  // API 요청 옵션
  getRequestOptions(method = 'GET', body = null) {
    const options = {
      method: method,
      headers: this.getHeaders(),
      mode: 'cors', // CORS 명시적 설정
      credentials: 'omit' // 쿠키 전송 안 함
    };
    if (body) {
      options.body = typeof body === 'string' ? body : JSON.stringify(body);
    }
    return options;
  }

  // 파일 존재 여부 확인
  async checkFileExists(path) {
    try {
      const response = await fetch(
        `${this.baseURL}/contents/${path}?ref=${ADMIN_CONFIG.branch}`,
        this.getRequestOptions('GET')
      );
      return response.ok;
    } catch (error) {
      console.error('Check file exists error:', error);
      return false;
    }
  }

  // 파일 정보 가져오기 (SHA 포함)
  async getFileInfo(path) {
    try {
      const response = await fetch(
        `${this.baseURL}/contents/${path}?ref=${ADMIN_CONFIG.branch}`,
        this.getRequestOptions('GET')
      );
      if (!response.ok) return null;
      return await response.json();
    } catch (error) {
      console.error('Get file info error:', error);
      return null;
    }
  }

  // 파일 생성 또는 업데이트
  async createOrUpdateFile(path, content, message, sha = null) {
    const body = {
      message: message,
      content: btoa(unescape(encodeURIComponent(content))), // Base64 인코딩
      branch: ADMIN_CONFIG.branch
    };

    if (sha) {
      body.sha = sha; // 업데이트 시 SHA 필요
    }

    const response = await fetch(
      `${this.baseURL}/contents/${path}`,
      this.getRequestOptions('PUT', body)
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to create/update file');
    }

    return await response.json();
  }

  // 파일 목록 가져오기
  async listFiles(path) {
    try {
      const response = await fetch(
        `${this.baseURL}/contents/${path}?ref=${ADMIN_CONFIG.branch}`,
        this.getRequestOptions('GET')
      );
      if (!response.ok) return [];
      const data = await response.json();
      return Array.isArray(data) ? data : [];
    } catch (error) {
      console.error('List files error:', error);
      return [];
    }
  }
}

// 전역 인스턴스
const authManager = new AuthManager();

// 로그인 폼 처리
if (document.getElementById('admin-login-form')) {
  document.getElementById('admin-login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const token = document.getElementById('github-token').value.trim();
    const password = document.getElementById('admin-password').value;
    const remember = document.getElementById('remember-token').checked;
    const errorDiv = document.getElementById('login-error');
    
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';

    if (!token) {
      errorDiv.textContent = 'GitHub 토큰을 입력하세요.';
      errorDiv.style.display = 'block';
      return;
    }

    // 토큰 검증
    const validation = await authManager.validateToken(token);
    
    if (!validation.valid) {
      errorDiv.textContent = `토큰 검증 실패: ${validation.error}`;
      errorDiv.style.display = 'block';
      return;
    }

    // 비밀번호 확인 (선택사항)
    if (password && ADMIN_CONFIG.adminPassword) {
      // 간단한 해시 비교 (실제로는 더 안전한 방법 사용)
      const passwordHash = await hashPassword(password);
      if (passwordHash !== ADMIN_CONFIG.adminPassword) {
        errorDiv.textContent = '비밀번호가 올바르지 않습니다.';
        errorDiv.style.display = 'block';
        return;
      }
    }

    // 인증 성공
    authManager.saveToken(token, remember);
    authManager.setAuthenticated(true, remember);
    
    // 에디터 페이지로 리다이렉트
    window.location.href = '/editor/';
  });
}

// 비밀번호 해시 (간단한 예시)
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

// 에디터 페이지 인증 확인
if (document.getElementById('editor-container')) {
  window.addEventListener('DOMContentLoaded', async () => {
    const token = authManager.getToken();
    
    if (!token || !authManager.isAuthenticated()) {
      document.getElementById('editor-container').style.display = 'none';
      document.getElementById('editor-login-required').style.display = 'block';
      return;
    }

    // 토큰 재검증
    const validation = await authManager.validateToken(token);
    if (!validation.valid) {
      authManager.clearToken();
      document.getElementById('editor-container').style.display = 'none';
      document.getElementById('editor-login-required').style.display = 'block';
      return;
    }

    // 인증 성공 - 에디터 표시
    document.getElementById('editor-container').style.display = 'block';
    document.getElementById('editor-login-required').style.display = 'none';
    
    // GitHub 클라이언트 초기화
    window.githubClient = new GitHubClient(token);
  });
}

// 로그아웃
if (document.getElementById('logout-btn')) {
  document.getElementById('logout-btn').addEventListener('click', () => {
    if (confirm('로그아웃하시겠습니까?')) {
      authManager.clearToken();
      window.location.href = '/admin/';
    }
  });
}

// 전역으로 export
window.authManager = authManager;
window.GitHubClient = GitHubClient;
window.ADMIN_CONFIG = ADMIN_CONFIG;

