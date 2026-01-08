const { BetaAnalyticsDataClient } = require('@google-analytics/data');
const fs = require('fs');
const path = require('path');

// 환경 변수에서 설정 가져오기
const propertyId = process.env.GA4_PROPERTY_ID || 'YOUR_PROPERTY_ID';
const credentialsJson = process.env.GA4_CREDENTIALS;

if (!credentialsJson) {
  console.error('GA4_CREDENTIALS 환경 변수가 설정되지 않았습니다.');
  process.exit(1);
}

// 서비스 계정 인증 정보 파싱
let credentials;
try {
  credentials = JSON.parse(credentialsJson);
} catch (e) {
  console.error('GA4_CREDENTIALS JSON 파싱 오류:', e);
  process.exit(1);
}

// Analytics Data API 클라이언트 초기화
const analyticsDataClient = new BetaAnalyticsDataClient({
  credentials: credentials
});

async function fetchAnalyticsData() {
  try {
    // KST(Asia/Seoul) 기준 날짜 문자열 생성 (YYYY-MM-DD)
    const kstFormatter = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Seoul',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
    const today = new Date();
    const todayStr = kstFormatter.format(today);
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const yesterdayStr = kstFormatter.format(yesterday);
    
    // 전체 지표 (시작일부터 오늘까지)
    const [totalResponse] = await analyticsDataClient.runReport({
      property: `properties/${propertyId}`,
      dateRanges: [
        {
          startDate: '2024-01-01', // 블로그 시작일로 변경
          endDate: 'today',
        },
      ],
      metrics: [
        {
          name: 'totalUsers',
        },
        {
          // 방문 "횟수"에 가까운 지표 (고유 사용자 합산과 달라 혼동 방지용)
          name: 'sessions',
        },
        {
          // 페이지 조회수(참고용)
          name: 'screenPageViews',
        },
      ],
    });

    // 오늘 지표 (KST 날짜 기준)
    const [todayResponse] = await analyticsDataClient.runReport({
      property: `properties/${propertyId}`,
      dateRanges: [
        {
          startDate: todayStr,
          endDate: todayStr,
        },
      ],
      metrics: [
        {
          name: 'totalUsers',
        },
        {
          name: 'sessions',
        },
        {
          name: 'screenPageViews',
        },
      ],
    });

    // 어제 지표 (KST 날짜 기준)
    const [yesterdayResponse] = await analyticsDataClient.runReport({
      property: `properties/${propertyId}`,
      dateRanges: [
        {
          startDate: yesterdayStr,
          endDate: yesterdayStr,
        },
      ],
      metrics: [
        {
          name: 'totalUsers',
        },
        {
          name: 'sessions',
        },
        {
          name: 'screenPageViews',
        },
      ],
    });

    // 데이터 추출
    const totalUsers = totalResponse.rows?.[0]?.metricValues?.[0]?.value || '0';
    const totalSessions = totalResponse.rows?.[0]?.metricValues?.[1]?.value || '0';
    const totalPageViews = totalResponse.rows?.[0]?.metricValues?.[2]?.value || '0';

    const todayUsers = todayResponse.rows?.[0]?.metricValues?.[0]?.value || '0';
    const todaySessions = todayResponse.rows?.[0]?.metricValues?.[1]?.value || '0';
    const todayPageViews = todayResponse.rows?.[0]?.metricValues?.[2]?.value || '0';

    const yesterdayUsers = yesterdayResponse.rows?.[0]?.metricValues?.[0]?.value || '0';
    const yesterdaySessions = yesterdayResponse.rows?.[0]?.metricValues?.[1]?.value || '0';
    const yesterdayPageViews = yesterdayResponse.rows?.[0]?.metricValues?.[2]?.value || '0';

    // JSON 파일로 저장
    const data = {
      // 기존 UI 호환: 직관적인 "방문(세션)" 기준으로 노출
      total: parseInt(totalSessions),
      today: parseInt(todaySessions),
      yesterday: parseInt(yesterdaySessions),

      // 추가 지표(정확성/확장성)
      totalUsers: parseInt(totalUsers),
      todayUsers: parseInt(todayUsers),
      yesterdayUsers: parseInt(yesterdayUsers),
      totalSessions: parseInt(totalSessions),
      todaySessions: parseInt(todaySessions),
      yesterdaySessions: parseInt(yesterdaySessions),
      totalPageViews: parseInt(totalPageViews),
      todayPageViews: parseInt(todayPageViews),
      yesterdayPageViews: parseInt(yesterdayPageViews),

      timezone: "Asia/Seoul",
      kstToday: todayStr,
      kstYesterday: yesterdayStr,
      lastUpdated: new Date().toISOString()
    };

    // _data 폴더에 저장 (Jekyll 데이터용)
    const dataPath = path.join(__dirname, '../../_data/analytics.json');
    fs.writeFileSync(dataPath, JSON.stringify(data, null, 2));
    
    // assets 폴더에도 저장 (직접 접근용)
    const assetsPath = path.join(__dirname, '../../assets/analytics.json');
    fs.writeFileSync(assetsPath, JSON.stringify(data, null, 2));
    
    console.log('Analytics 데이터 업데이트 완료:', data);
  } catch (error) {
    console.error('Analytics 데이터 가져오기 오류:', error);
    process.exit(1);
  }
}

fetchAnalyticsData();

