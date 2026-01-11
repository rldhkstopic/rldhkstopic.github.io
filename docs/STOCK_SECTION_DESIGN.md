# 주식 섹션 디자인 및 구현 계획

## 📋 개요

주식 섹션을 개발(Dev) 섹션과 유사한 구조로 구현하여, 관심 종목 소식과 경제 뉴스를 실시간으로 정리하고 업데이트할 수 있도록 설계한다.

---

## 🎯 목표

1. **관심 종목 소식**: 특정 종목에 대한 뉴스와 분석을 체계적으로 정리
2. **경제 뉴스 정리**: 전일/당일 경제 뉴스를 주제별로 분류하여 종합
3. **실시간 업데이트**: 자동화 시스템을 통해 지속적으로 콘텐츠 업데이트
4. **개발 섹션과의 일관성**: 동일한 UI/UX 패턴으로 사용자 경험 통일

---

## 🏗️ 구조 설계

### 1. 하위 카테고리 구성

```
주식 (Stock)
├── 관심 종목 (Watchlist)
│   ├── 종목별 하위 페이지 (예: 삼성전자, SK하이닉스 등)
│   └── 각 종목별 최신 뉴스 및 분석
├── 경제 뉴스 (Economic News)
│   ├── 일일 뉴스 종합 (Daily Digest)
│   └── 주제별 분류 (정책, 시장, 기업 등)
└── 시장 분석 (Market Analysis)
    ├── 섹터별 분석
    └── 기술적 분석
```

### 2. 데이터 구조

#### `_data/stock_structure.yml`

```yaml
subcategories:
  - id: watchlist
    title: "관심 종목"
    icon: "star" # Lucide icon
    description: "관심 종목별 뉴스 및 분석"
    stocks:
      - id: samsung
        name: "삼성전자"
        ticker: "005930"
        icon: "chip" # Lucide icon
      - id: skhynix
        name: "SK하이닉스"
        ticker: "000660"
        icon: "database"
      # 추가 종목...

  - id: economic-news
    title: "경제 뉴스"
    icon: "newspaper"
    description: "일일 경제 뉴스 종합"
    sections:
      - id: daily-digest
        title: "일일 뉴스 종합"
        description: "전일/당일 주요 경제 뉴스"
      - id: policy
        title: "정책"
        description: "정부 정책 및 규제 관련 뉴스"
      - id: market
        title: "시장"
        description: "시장 동향 및 전망"

  - id: market-analysis
    title: "시장 분석"
    icon: "trending-up"
    description: "시장 및 섹터 분석"
```

### 3. 페이지 구조

```
pages/stock/
├── index.html          # 주식 섹션 메인 (개발 섹션과 유사)
├── watchlist/
│   ├── index.html       # 관심 종목 목록
│   ├── samsung.html    # 삼성전자 전용 페이지
│   └── skhynix.html    # SK하이닉스 전용 페이지
├── economic-news/
│   ├── index.html      # 경제 뉴스 메인
│   └── daily-digest.html  # 일일 뉴스 종합
└── market-analysis/
    └── index.html      # 시장 분석 메인
```

---

## 🎨 UI/UX 디자인

### 메인 화면 (index.html)

**개발 섹션과 동일한 구조:**

```html
<div class="content-section">
  <div class="section-header">
    <h2 class="section-title">
      <span class="category-icon-wrapper icon-stock">
        <i data-lucide="trending-up" class="category-icon"></i>
      </span>
      주식
    </h2>
    <a href="/stock/" class="section-more">더보기</a>
  </div>
  <div class="stock-subcategories">
    <!-- 관심 종목 -->
    <a href="/stock/watchlist/" class="stock-subcategory-link">
      <span class="stock-subcategory-icon-wrapper">
        <i data-lucide="star" class="stock-subcategory-icon"></i>
      </span>
      <span class="stock-subcategory-title">관심 종목</span>
      <span class="stock-subcategory-count">5</span>
    </a>
    <!-- 경제 뉴스 -->
    <a href="/stock/economic-news/" class="stock-subcategory-link">
      <span class="stock-subcategory-icon-wrapper">
        <i data-lucide="newspaper" class="stock-subcategory-icon"></i>
      </span>
      <span class="stock-subcategory-title">경제 뉴스</span>
      <span class="stock-subcategory-count">12</span>
    </a>
  </div>
</div>
```

### 관심 종목 페이지

**종목별 카드 형태:**

```html
<div class="stock-list">
  <div class="stock-item">
    <div class="stock-header">
      <span class="stock-icon-wrapper">
        <i data-lucide="chip" class="stock-icon"></i>
      </span>
      <div class="stock-info">
        <h3>삼성전자 (005930)</h3>
        <p>최근 뉴스 3건</p>
      </div>
    </div>
    <div class="stock-news-preview">
      <!-- 최근 뉴스 3개 미리보기 -->
    </div>
  </div>
</div>
```

---

## 🔄 자동화 전략

### 1. 뉴스 수집

**소스:**

- Bloomberg RSS (이미 구현됨)
- 네이버 증권 뉴스
- 한국경제, 매일경제 RSS
- Yahoo Finance API

**수집 주기:**

- **전날 뉴스**: 매일 오전 7시 (KST)
- **당일 뉴스**: 매일 오후 6시 (KST)
- **실시간 알림**: Discord 봇을 통한 중요 뉴스 즉시 알림

### 2. 관심 종목 필터링

**구현 방식:**

1. `_data/stock_structure.yml`에 관심 종목 목록 정의
2. 수집된 뉴스에서 종목명/티커 매칭
3. 종목별로 뉴스 자동 분류
4. 각 종목 페이지에 자동 업데이트

### 3. 뉴스 종합 및 분석

**처리 로직:**

1. 뉴스 그룹핑 (종목별, 섹터별, 이슈별)
2. 중요도 평가 (출처, 스크랩 여부, 조회수)
3. AI 분석 (요약, 시장 영향, 리스크)
4. 블로그 포스트 자동 생성

---

## 📁 파일 구조

### 신규 생성 파일

```
_data/
  └── stock_structure.yml          # 주식 섹션 구조 정의

pages/stock/
  ├── index.html                   # 주식 섹션 메인
  ├── watchlist/
  │   ├── index.html               # 관심 종목 목록
  │   └── [종목].html              # 종목별 페이지 (동적 생성 가능)
  ├── economic-news/
  │   ├── index.html               # 경제 뉴스 메인
  │   └── daily-digest.html        # 일일 뉴스 종합
  └── market-analysis/
      └── index.html               # 시장 분석 메인

.github/scripts/
  └── stock_news_agent.py          # 주식 뉴스 수집 및 분석 Agent

.github/workflows/
  └── stock-news.yml               # 주식 뉴스 자동화 워크플로우
```

### 수정 파일

```
index.html                          # 주식 섹션 UI 추가
assets/css/main.css                 # 주식 섹션 스타일 추가
_layouts/dev-wiki.html              # stock-wiki.html으로 복사하여 활용 가능
```

---

## 🎯 구현 단계

### Phase 1: 기본 구조 구축 (1주)

1. **데이터 구조 정의**

   - `_data/stock_structure.yml` 생성
   - 관심 종목 목록 정의

2. **페이지 구조 생성**

   - `pages/stock/index.html` 생성
   - `pages/stock/watchlist/index.html` 생성
   - `pages/stock/economic-news/index.html` 생성

3. **UI 구현**
   - 메인 화면 주식 섹션 수정
   - 개발 섹션과 유사한 하위 카테고리 표시
   - CSS 스타일 추가

### Phase 2: 뉴스 수집 및 분류 (1-2주)

1. **뉴스 수집 Agent 개발**

   - RSS 피드 수집
   - 웹 스크래핑 유틸리티
   - 관심 종목 필터링

2. **뉴스 분류 시스템**
   - 종목별 자동 분류
   - 주제별 분류
   - 중요도 평가

### Phase 3: 자동화 워크플로우 (1주)

1. **GitHub Actions 워크플로우**

   - `stock-news.yml` 생성
   - 스케줄 설정 (오전 7시, 오후 6시)
   - Discord 알림 연동

2. **Discord 봇 확장**
   - 실시간 뉴스 알림
   - 관심 종목 뉴스 필터링

---

## 💡 개선 사항 및 고려사항

### 1. 실시간 업데이트

**현재 계획:**

- GitHub Actions 스케줄 실행 (오전 7시, 오후 6시)

**향후 개선:**

- Discord 봇을 통한 실시간 뉴스 수집
- 중요 뉴스 즉시 알림 및 포스팅

### 2. 관심 종목 관리

**초기 구현:**

- `_data/stock_structure.yml`에 수동으로 종목 추가

**향후 개선:**

- Discord 명령어로 관심 종목 추가/제거
- 자동으로 종목별 페이지 생성

### 3. 뉴스 분석 품질

**AI 프롬프트 최적화:**

- Bloomberg 다이제스트 프롬프트 확장
- 종목별 맞춤 분석
- 시장 영향도 평가

### 4. 성능 최적화

**대량 뉴스 처리:**

- 뉴스 중복 제거
- 중요 뉴스 우선순위 처리
- 캐싱 전략

---

## 🔧 기술 스택

### 기존 사용

- Jekyll (정적 사이트 생성)
- GitHub Actions (자동화)
- Discord Bot API
- Google Gemini API

### 신규 필요

- `beautifulsoup4`: 웹 스크래핑
- `feedparser`: RSS 파싱
- `newspaper3k` 또는 `readability-lxml`: 기사 본문 추출
- `yfinance` (선택): Yahoo Finance API

---

## 📊 예상 결과

### 사용자 경험

- 개발 섹션과 일관된 UI/UX
- 관심 종목별로 체계적인 뉴스 정리
- 실시간 업데이트로 최신 정보 제공

### 콘텐츠 품질

- AI 분석을 통한 인사이트 제공
- 주제별 분류로 가독성 향상
- 자동화로 지속적인 콘텐츠 업데이트

---

## ⚠️ 주의사항

1. **뉴스 저작권**: 기사 전문 재현 금지, 요약 및 링크만 제공
2. **투자 조언 금지**: 정보 제공 목적만, 투자 조언은 하지 않음
3. **데이터 정확성**: 뉴스 출처 명시 및 검증 필요
4. **API 제한**: RSS/API 호출 빈도 제한 고려

---

## 📰 Live News Feed 구축

### 개요

정적 사이트의 한계를 극복하기 위해 JSON 파일을 DB처럼 활용하고, 1시간마다 GitHub Actions로 업데이트하는 실시간 주식 뉴스 피드 시스템을 구축한다.

### 1. 데이터 구조 설계

#### `assets/data/stock_feed.json`

```json
{
  "last_updated": "2026-01-10T15:30:00+09:00",
  "items": [
    {
      "id": "unique_hash",
      "timestamp": "2026-01-10T15:25:00+09:00",
      "source_type": "NEWS",
      "source_name": "Bloomberg",
      "category": "WATCHLIST",
      "related_tickers": ["005930", "NVDA"],
      "content": "뉴스 요약 또는 SNS 내용 본문",
      "url": "https://example.com/news/article",
      "sentiment": "POSITIVE"
    }
  ]
}
```

**제약 사항:**
- 최신 200개 아이템만 유지
- 오래된 항목 자동 삭제
- 중복 체크 (ID 기준)

**데이터 타입:**
- `source_type`: `"NEWS"` | `"SNS"` | `"REPORT"`
- `category`: `"WATCHLIST"` | `"MAJOR"` | `"MARKET"`
- `sentiment`: `"POSITIVE"` | `"NEGATIVE"` | `"NEUTRAL"` (선택)

### 2. 백엔드 로직

#### `.github/scripts/stock_feed_agent.py`

**주요 기능:**

1. **뉴스 수집**
   - RSS 피드 (Bloomberg, 한경, 매경 등)
   - 기존 `topic_collector.py` 로직 활용

2. **SNS 수집 (신규)**
   - StockTwits: 관심 종목 티커별 인기 포스트
   - Reddit: r/stocks, r/koreastock 'Hot' 게시물
   - (선택) X(Twitter), 토스 주식 토론방

3. **데이터 병합 로직**
   - 기존 `stock_feed.json` 로드
   - 중복 체크 (ID 기준)
   - 최신순으로 병합
   - 상위 200개만 유지

**구현 예시:**

```python
def collect_stock_feed():
    # 1. 기존 데이터 로드
    existing_items = load_existing_feed()
    
    # 2. 새 데이터 수집
    news_items = collect_rss_news()
    sns_items = collect_sns_posts()
    
    # 3. 중복 제거 및 병합
    all_items = merge_items(existing_items, news_items, sns_items)
    
    # 4. 상위 200개만 유지
    latest_items = sorted(all_items, key=lambda x: x['timestamp'], reverse=True)[:200]
    
    # 5. 저장
    save_feed(latest_items)
```

### 3. 프론트엔드 UI

#### `pages/stock/index.html`

**레이아웃:**

```
┌─────────────────────────────────────────┐
│  필터 메뉴 (좌측)  │  타임라인 (우측)    │
│  - 전체            │  [최신순 위로]     │
│  - ⭐️ 관심종목    │  ┌─────────────┐  │
│  - 🚨 주요속보    │  │ 뉴스 카드 1  │  │
│  - 호재/악재       │  └─────────────┘  │
│                    │  ┌─────────────┐  │
│                    │  │ SNS 카드 2   │  │
│                    │  └─────────────┘  │
└─────────────────────────────────────────┘
```

**기능:**

1. **페이지 로드 시**
   - JavaScript로 `stock_feed.json` fetch
   - 캐싱 방지: `?t={timestamp}` 쿼리 파라미터 추가

2. **필터링**
   - 전체 / 관심종목 / 주요속보 / 호재/악재
   - 실시간 필터링 (클라이언트 사이드)

3. **스타일**
   - NEWS: 헤드라인 스타일 카드
   - SNS: 트위터/채팅 느낌 말풍선
   - 상대 시간 표시: "방금 전", "10분 전"

**JavaScript 예시:**

```javascript
async function loadStockFeed() {
    const timestamp = new Date().getTime();
    const response = await fetch(`/assets/data/stock_feed.json?t=${timestamp}`);
    const data = await response.json();
    
    renderTimeline(data.items);
    updateRelativeTime();
}

function renderTimeline(items) {
    const container = document.getElementById('timeline-container');
    items.forEach(item => {
        const card = createFeedCard(item);
        container.appendChild(card);
    });
}

function createFeedCard(item) {
    const card = document.createElement('div');
    card.className = `feed-item feed-${item.source_type.toLowerCase()}`;
    
    // 카드 내용 구성
    card.innerHTML = `
        <div class="feed-header">
            <span class="feed-source">${item.source_name}</span>
            <span class="feed-time" data-timestamp="${item.timestamp}"></span>
        </div>
        <div class="feed-content">${item.content}</div>
        <div class="feed-footer">
            <a href="${item.url}" target="_blank">원문 보기</a>
        </div>
    `;
    
    return card;
}
```

### 4. 자동화 워크플로우

#### `.github/workflows/stock-feed.yml`

**스케줄:**
- 매시 정각 실행 (`cron: '0 * * * *'`)

**권한:**
- 리포지토리에 JSON 파일 push 권한

**구현:**

```yaml
name: Stock Feed Update

on:
  schedule:
    - cron: '0 * * * *'  # 매시 정각
  workflow_dispatch:  # 수동 실행 가능

jobs:
  update-feed:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install requests feedparser beautifulsoup4
      - name: Run stock feed agent
        env:
          ECONOMIC_NEWS_RSS_FEEDS: ${{ secrets.ECONOMIC_NEWS_RSS_FEEDS }}
        run: |
          python .github/scripts/stock_feed_agent.py
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add assets/data/stock_feed.json
          git diff --staged --quiet || git commit -m "Update stock feed [skip ci]"
          git push
```

### 5. 파일 구조

```
assets/data/
  └── stock_feed.json              # 타임라인 데이터 (자동 업데이트)

.github/scripts/
  └── stock_feed_agent.py           # 뉴스/SNS 수집 Agent

.github/workflows/
  └── stock-feed.yml                # 1시간마다 실행

pages/stock/
  └── index.html                    # Live Feed UI

assets/css/
  └── stock-feed.css                # 피드 스타일 (신규 또는 main.css에 추가)
```

### 6. 구현 단계

#### Phase 1: 기본 구조 (1-2일)
1. `stock_feed.json` 초기 파일 생성
2. `stock_feed_agent.py` 기본 구조 구현
3. RSS 뉴스 수집 로직 구현

#### Phase 2: SNS 수집 (2-3일)
1. StockTwits API 연동
2. Reddit API 연동
3. 데이터 병합 로직 구현

#### Phase 3: 프론트엔드 (2일)
1. 타임라인 UI 구현
2. 필터링 기능
3. 상대 시간 표시

#### Phase 4: 자동화 (1일)
1. GitHub Actions 워크플로우 생성
2. 테스트 및 배포

### 7. 기술 스택

**기존:**
- `requests`: HTTP 요청
- `feedparser`: RSS 파싱
- GitHub Actions

**신규:**
- `beautifulsoup4`: 웹 스크래핑 (SNS)
- `praw`: Reddit API (선택)
- JavaScript (Fetch API): 프론트엔드

### 8. 고려사항

1. **API 제한**
   - StockTwits, Reddit API rate limit 고려
   - 에러 핸들링 및 재시도 로직

2. **데이터 크기**
   - JSON 파일 크기 모니터링
   - 200개 제한으로 약 100KB 이하 유지

3. **캐싱**
   - 브라우저 캐싱 방지 (`?t={timestamp}`)
   - CDN 캐싱 고려 (Vercel)

4. **성능**
   - 대량 아이템 렌더링 최적화 (가상 스크롤)
   - 필터링 성능 최적화
