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
    // 오늘 날짜
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    
    // 어제 날짜
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split('T')[0];
    
    // 전체 방문자 수 (시작일부터 오늘까지)
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
      ],
    });

    // 오늘 방문자 수
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
      ],
    });

    // 어제 방문자 수
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
      ],
    });

    // 데이터 추출
    const totalVisitors = totalResponse.rows?.[0]?.metricValues?.[0]?.value || '0';
    const todayVisitors = todayResponse.rows?.[0]?.metricValues?.[0]?.value || '0';
    const yesterdayVisitors = yesterdayResponse.rows?.[0]?.metricValues?.[0]?.value || '0';

    // JSON 파일로 저장
    const data = {
      total: parseInt(totalVisitors),
      today: parseInt(todayVisitors),
      yesterday: parseInt(yesterdayVisitors),
      lastUpdated: new Date().toISOString()
    };

    const outputPath = path.join(__dirname, '../../_data/analytics.json');
    fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
    
    console.log('Analytics 데이터 업데이트 완료:', data);
  } catch (error) {
    console.error('Analytics 데이터 가져오기 오류:', error);
    process.exit(1);
  }
}

fetchAnalyticsData();

