// Vercel Function: GitHub OAuth code를 access token으로 교환
// 참고: https://dev-watnu.tistory.com/58

export default async function handler(req, res) {
  // CORS 헤더 설정
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // OPTIONS 요청 처리 (CORS preflight)
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // POST 요청만 허용
  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method Not Allowed' });
    return;
  }

  try {
    const { code } = req.body;
    
    if (!code) {
      res.status(400).json({ error: 'Code parameter is required' });
      return;
    }

    // 환경 변수에서 Client ID와 Secret 가져오기
    const clientId = process.env.GITHUB_CLIENT_ID;
    const clientSecret = process.env.GITHUB_CLIENT_SECRET;

    if (!clientId || !clientSecret) {
      res.status(500).json({ 
        error: 'GitHub OAuth credentials not configured',
        message: 'GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set in Vercel environment variables'
      });
      return;
    }

    // GitHub OAuth API로 code를 access token으로 교환
    const response = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        client_id: clientId,
        client_secret: clientSecret,
        code: code
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      res.status(response.status).json({ 
        error: 'GitHub OAuth token exchange failed',
        details: errorText
      });
      return;
    }

    const data = await response.json();
    
    // Access token 반환
    res.status(200).json({
      access_token: data.access_token,
      token_type: data.token_type,
      scope: data.scope
    });
  } catch (error) {
    console.error('OAuth token exchange error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message
    });
  }
}

