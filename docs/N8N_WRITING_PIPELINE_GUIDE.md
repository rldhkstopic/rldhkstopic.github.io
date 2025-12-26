# n8n 글 자동화 파이프라인 가이드

n8n 워크플로우를 통해 블로그 포스트를 자동으로 생성하고 게시하는 전체 파이프라인 설계 가이드다. 글쓰기 가이드라인부터 데이터 수집, 변환, 검증, 푸시까지의 전체 프로세스를 다룬다.

## 1. 글쓰기 가이드라인

### 1.1 스타일 원칙

**문체:**
- "~다."로 끝나는 건조하고 분석적인 문체 사용
- 감정 배제, 이모지 금지
- "AI가 말했다"가 아니라 "데이터를 분석해 본 결과 ~임이 확인되었다"와 같이 주도적 연구 시점 유지

**흐름 구조:**
1. [현상/문제 인식] → 2. [데이터/근거 분석] → 3. [전문가 의견 대조] → 4. [인사이트 도출]

**도입부 작성:**
- 거창한 정의로 시작하지 않음
- 패턴: [상황/동기] -> [액션] -> [환경/제약사항]
- 예시: "연구실 과제로 TurtleBot3를 쓰는데 파이썬이 필요해서 rospy를 찾아보게 되었다. 나중을 위해 정리해둔다. 실습 환경은 Desktop이다."

**본문 작성:**
- 소제목은 간결하게(명사형) 작성
- 1, 2, 3 번호 매기기 리스트보다는 줄글(Paragraph) 우선
- 섹션 간 연결: 각 섹션이 끝나기 전에 다음 섹션으로 자연스럽게 이어지는 전환 문장 추가

**결말:**
- "결론" 섹션을 따로 만들지 않음
- 작업이 끝난 상태나, 다음 단계에 대한 짧은 메모로 툭 던지듯 마무리

### 1.2 Front Matter 필수 필드

```yaml
---
layout: post
title: "제목 (따옴표 필수)"
date: YYYY-MM-DD HH:MM:SS +0900
author: rldhkstopic
category: daily  # daily/dev/document/study 중 하나
subcategory: "하위 카테고리 (선택)"
tags: [태그1, 태그2, 태그3]
views: 0
---
```

**카테고리 선택 기준:**
- **daily**: 일상, 회고, 생각
- **dev**: 개발 과정, 문제 해결, 프로젝트
- **document**: 문서화, 가이드, 참고 자료, 시장 분석
- **study**: 학습 내용, 개념 정리, 튜토리얼

### 1.3 참조 및 인용 규칙

**Reference Linking System:**
- 본문 내에서 외부 자료나 데이터의 출처를 언급할 때는 반드시 **대괄호 숫자 인덱스 `[^n]`** 사용
- 글의 맨 마지막에 `## References` 섹션을 만들고, 모든 링크를 정리
- 형식: `[^1]: [문서 제목/웹사이트명](URL) - 간단한 설명`

**전문가 의견 추출:**
- 입력 데이터에 전문가, 기관, 리포트의 구체적인 발언이 포함되어 있다면, 요약하지 말고 **직접 인용(Direct Quote)** 한다
- 인용문은 반드시 **Markdown Blockquote (`>`)** 구문 사용
- 인용문 아래에는 반드시 발언의 주체(사람/기관)를 명시

**작성 예시:**
```markdown
> "현재 시장의 연체율 11.2%는 단순한 오류가 아니라 시스템의 붕괴를 의미할 수 있다."
> — *M.V. Cunha (Financial Analyst)*
```

### 1.4 코드 설명 방식

코드가 포함될 경우, 반드시 아래 **[분할 설명 방식]**을 따른다:

1. 먼저 전체 코드 블록을 보여준다
2. 그 아래에 **설명이 필요한 주요 라인만 따로 떼어내어** 다시 적고, 그 밑에 줄글로 설명을 덧붙인다
3. 코드 내 주석(#)보다는 본문 텍스트 설명을 선호한다

**작성 예시:**
```python
rospy.init_node('listener', anonymous=True)
```
'listener'라는 노드를 초기화 생성한다. anonymous=True로 설정하면 노드 이름 뒤에 임의 숫자가 붙어 중복을 방지한다.

### 1.5 금지어 및 주의사항

**금지어:**
- "안녕하세요", "반갑습니다", "오늘은 ~를 알아보겠습니다" (인사 생략)
- "결론적으로", "요약하자면", "마지막으로" (접속사 생략)
- "매우", "획기적인", "놀라운" (감정적 형용사 생략)
- 이모지 사용 금지

**입력 데이터 처리:**
- 입력된 대화 로그나 텍스트에서 **잡담, 인삿말, 불필요한 추임새는 모두 제거**
- 오직 **기술적 사실, 분석 데이터, 전문가 견해**만 추출하여 재구성

## 2. n8n 파이프라인 설계

### 2.1 전체 파이프라인 구조

```
[Trigger] 
  → [데이터 수집] 
  → [데이터 전처리] 
  → [AI 변환 (선택)] 
  → [마크다운 변환] 
  → [Front Matter 생성] 
  → [내용 검증] 
  → [중복 체크] 
  → [GitHub 푸시] 
  → [알림]
```

### 2.2 단계별 상세 설계

#### Step 1: Trigger (트리거)

**Schedule Trigger:**
- Interval: `Every Hour` 또는 `Every 6 Hours`
- Timezone: `Asia/Seoul`
- Start Time: `00:00`

**Webhook Trigger (선택):**
- 외부 시스템에서 직접 호출 가능
- 예: AI 대화 완료 시 웹훅으로 전송

**Manual Trigger:**
- 테스트 및 수동 실행용

#### Step 2: 데이터 수집

**소스별 수집 방법:**

**A. RSS 피드:**
```javascript
// HTTP Request 노드
Method: GET
URL: https://example.com/feed.xml

// XML Parse 노드
XPath: /rss/channel/item
```

**B. API 호출:**
```javascript
// HTTP Request 노드
Method: GET
URL: https://api.example.com/posts
Authentication: OAuth2 또는 API Key
```

**C. 데이터베이스:**
```sql
-- MySQL/PostgreSQL 노드
SELECT * FROM posts 
WHERE created_at > DATE_SUB(NOW(), INTERVAL 1 HOUR)
AND status = 'published'
```

**D. 파일 시스템:**
```javascript
// Read Binary File 노드
File Path: /path/to/source/data.json
```

**수집 데이터 구조:**
```json
{
  "title": "제목",
  "content": "본문 내용 (HTML 또는 마크다운)",
  "date": "2025-12-13T14:30:00+09:00",
  "source_url": "https://example.com/article",
  "author": "원본 작성자",
  "category": "document",
  "tags": ["태그1", "태그2"],
  "metadata": {
    "source": "rss",
    "id": "unique-id"
  }
}
```

#### Step 3: 데이터 전처리

**Code 노드 - 데이터 정규화:**
```javascript
const items = $input.all();

return items.map(item => {
  const data = item.json;
  
  // 날짜 정규화
  const date = new Date(data.date || Date.now());
  const dateStr = date.toISOString().split('T')[0];
  const timeStr = date.toTimeString().split(' ')[0];
  
  // 제목 정리 (특수문자 제거, 공백 정리)
  const title = (data.title || '').trim()
    .replace(/\s+/g, ' ')
    .replace(/[""]/g, '"')
    .replace(/['']/g, "'");
  
  // 카테고리 검증
  const validCategories = ['daily', 'dev', 'document', 'study'];
  const category = validCategories.includes(data.category) 
    ? data.category 
    : 'daily';
  
  // 태그 정리
  const tags = Array.isArray(data.tags) 
    ? data.tags.filter(t => t && t.trim()).map(t => t.trim())
    : [];
  
  // 본문 정리 (HTML 태그 제거, 마크다운 변환 등)
  let content = data.content || '';
  // HTML 태그 제거 (필요시)
  // content = content.replace(/<[^>]*>/g, '');
  
  return {
    json: {
      title,
      content,
      date: dateStr,
      time: timeStr,
      category,
      tags,
      source_url: data.source_url || '',
      author: data.author || 'rldhkstopic',
      metadata: data.metadata || {}
    }
  };
});
```

#### Step 4: AI 변환 (선택)

**OpenAI 노드 또는 HTTP Request:**
```javascript
// OpenAI API 호출
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "당신은 현업 수석 엔지니어이자, 팩트와 논리를 중시하는 테크니컬 라이터입니다. 주어지는 입력 데이터를 바탕으로 웹페이지에 게시할 고품질의 기술 블로그 포스트를 Markdown 형식으로 작성하십시오.\n\n문체: '~다.'로 끝나는 건조하고 분석적인 문체. 감정 배제, 이모지 금지.\n\n구조: [현상/문제 인식] -> [데이터/근거 분석] -> [전문가 의견 대조] -> [인사이트 도출]"
    },
    {
      "role": "user",
      "content": `다음 내용을 블로그 포스트로 변환해주세요:\n\n제목: {{ $json.title }}\n카테고리: {{ $json.category }}\n\n내용:\n{{ $json.content }}`
    }
  ],
  "temperature": 0.7,
  "max_tokens": 4000
}
```

**AI 응답 파싱:**
```javascript
// Code 노드
const response = $input.first().json;
const aiContent = response.choices[0].message.content;

// 마크다운에서 Front Matter와 본문 분리
const frontMatterMatch = aiContent.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
if (frontMatterMatch) {
  return {
    json: {
      ...$input.first().json,
      ai_content: frontMatterMatch[2],
      ai_frontmatter: frontMatterMatch[1]
    }
  };
}

return {
  json: {
    ...$input.first().json,
    ai_content: aiContent
  }
};
```

#### Step 5: 마크다운 변환

**Code 노드 - Jekyll 포스트 형식 생성:**
```javascript
const items = $input.all();

return items.map(item => {
  const data = item.json;
  
  // 파일명 생성
  const titleSlug = data.title
    .replace(/[^\w\s가-힣-]/g, '')  // 특수문자 제거 (하이픈 제외)
    .replace(/\s+/g, '-')            // 공백을 하이픈으로
    .replace(/-+/g, '-')              // 연속된 하이픈 제거
    .toLowerCase();
  
  const filename = `${data.date}-${titleSlug}.md`;
  
  // Front Matter 생성
  const frontMatter = `---
layout: post
title: "${data.title.replace(/"/g, '\\"')}"
date: ${data.date} ${data.time} +0900
author: ${data.author}
category: ${data.category}${data.subcategory ? `\nsubcategory: "${data.subcategory}"` : ''}
tags: [${data.tags.map(t => `"${t}"`).join(', ')}]
views: 0
---

`;
  
  // 본문 처리
  let content = data.ai_content || data.content;
  
  // 참조 링크 처리 (URL을 [^n] 형식으로 변환)
  const urlRegex = /(https?:\/\/[^\s\)]+)/g;
  let refIndex = 1;
  const references = [];
  const urlMap = new Map();
  
  content = content.replace(urlRegex, (url) => {
    if (!urlMap.has(url)) {
      urlMap.set(url, refIndex);
      references.push({
        index: refIndex,
        url: url
      });
      refIndex++;
    }
    return `[^${urlMap.get(url)}]`;
  });
  
  // References 섹션 추가
  if (references.length > 0) {
    content += '\n\n## References\n\n';
    references.forEach(ref => {
      content += `[^${ref.index}]: ${ref.url}\n`;
    });
  }
  
  // 최종 마크다운 생성
  const markdown = frontMatter + content;
  
  return {
    json: {
      filename,
      path: `_posts/${filename}`,
      content: markdown,
      title: data.title,
      category: data.category,
      date: data.date,
      metadata: data.metadata
    }
  };
});
```

#### Step 6: 내용 검증

**Code 노드 - 검증 로직:**
```javascript
const items = $input.all();

return items.map(item => {
  const data = item.json;
  const errors = [];
  const warnings = [];
  
  // 필수 필드 검증
  if (!data.title || data.title.trim().length === 0) {
    errors.push('제목이 없습니다.');
  }
  
  if (!data.content || data.content.length < 100) {
    warnings.push('본문이 너무 짧습니다 (100자 미만).');
  }
  
  // Front Matter 검증
  if (!data.content.includes('layout: post')) {
    errors.push('Front Matter에 layout: post가 없습니다.');
  }
  
  if (!data.content.includes('category:')) {
    errors.push('Front Matter에 category가 없습니다.');
  }
  
  // 금지어 검증
  const forbiddenWords = ['안녕하세요', '반갑습니다', '오늘은', '매우', '획기적인', '놀라운'];
  forbiddenWords.forEach(word => {
    if (data.content.includes(word)) {
      warnings.push(`금지어 "${word}"가 포함되어 있습니다.`);
    }
  });
  
  // 이모지 검증
  const emojiRegex = /[\u{1F300}-\u{1F9FF}]/u;
  if (emojiRegex.test(data.content)) {
    warnings.push('이모지가 포함되어 있습니다.');
  }
  
  return {
    json: {
      ...data,
      validation: {
        valid: errors.length === 0,
        errors,
        warnings
      }
    }
  };
});
```

**IF 노드 - 검증 결과 필터링:**
```
Condition: {{ $json.validation.valid }} === true
```

#### Step 7: 중복 체크

**HTTP Request 노드 - GitHub API로 파일 목록 조회:**
```javascript
// GET /repos/{owner}/{repo}/contents/{path}
Method: GET
URL: https://api.github.com/repos/rldhkstopic/rldhkstopic.github.io/contents/_posts
Authentication: GitHub API Token
```

**Code 노드 - 중복 체크:**
```javascript
const items = $input.all();
const existingFiles = $('HTTP Request').first().json; // GitHub API 응답

const existingFilenames = existingFiles
  .map(file => file.name)
  .filter(name => name.endsWith('.md'));

return items
  .map(item => {
    const data = item.json;
    const isDuplicate = existingFilenames.includes(data.filename);
    
    return {
      json: {
        ...data,
        is_duplicate: isDuplicate
      }
    };
  })
  .filter(item => !item.json.is_duplicate); // 중복 제거
```

#### Step 8: GitHub 푸시

**HTTP Request 노드 - 파일 생성/업데이트:**
```javascript
// 먼저 파일 존재 여부 확인
Method: GET
URL: https://api.github.com/repos/rldhkstopic/rldhkstopic.github.io/contents/{{ $json.path }}
Authentication: GitHub API Token

// 파일이 없으면 생성, 있으면 업데이트
Method: PUT
URL: https://api.github.com/repos/rldhkstopic/rldhkstopic.github.io/contents/{{ $json.path }}
Authentication: GitHub API Token
Body:
{
  "message": "Auto-post: {{ $json.title }}",
  "content": "{{ $json.content | base64 }}",
  "branch": "main",
  "sha": "{{ $('GET File Info').json.sha }}" // 업데이트 시에만 필요
}
```

**에러 처리:**
```javascript
// IF 노드로 HTTP 상태 코드 확인
Condition: {{ $json.statusCode }} === 200 || {{ $json.statusCode }} === 201

// 실패 시 재시도 로직 (선택)
// Delay 노드 + 재시도
```

#### Step 9: 알림

**성공 알림:**
```javascript
// Slack 노드 또는 Email 노드
{
  "channel": "#blog-automation",
  "text": `✅ 새 포스트 게시 완료: {{ $json.title }}\n카테고리: {{ $json.category }}\n파일: {{ $json.filename }}`
}
```

**실패 알림:**
```javascript
{
  "channel": "#blog-automation",
  "text": `❌ 포스트 게시 실패: {{ $json.title }}\n에러: {{ $json.error }}`
}
```

## 3. 실제 구현 예시

### 3.1 RSS 피드 자동화 워크플로우

**전체 노드 구성:**
1. Schedule Trigger (매 시간)
2. HTTP Request (RSS 피드)
3. XML Parse
4. Code (데이터 정규화)
5. Code (마크다운 변환)
6. Code (검증)
7. HTTP Request (GitHub - 파일 목록)
8. Code (중복 체크)
9. HTTP Request (GitHub - 파일 생성)
10. IF (성공/실패 분기)
11. Slack (알림)

**RSS 파싱 예시:**
```javascript
// XML Parse 노드 후 Code 노드
const items = $input.all();

return items.map(item => {
  const entry = item.json;
  
  return {
    json: {
      title: entry.title || entry['title']['#text'],
      content: entry.description || entry.content || entry['content']['#text'],
      date: entry.pubDate || entry.published,
      source_url: entry.link || entry['link']['#text'],
      category: 'document', // RSS별로 고정 또는 키워드 분석
      tags: extractTags(entry.title + ' ' + entry.description),
      metadata: {
        source: 'rss',
        id: entry.guid || entry.id
      }
    }
  };
});
```

### 3.2 AI 대화 로그 자동화 워크플로우

**전체 노드 구성:**
1. Webhook Trigger (AI 대화 완료 시)
2. Code (대화 로그 파싱)
3. OpenAI (마크다운 변환)
4. Code (Front Matter 생성)
5. Code (검증)
6. HTTP Request (GitHub - 중복 체크)
7. Code (중복 필터링)
8. HTTP Request (GitHub - 파일 생성)
9. Slack (알림)

**대화 로그 파싱:**
```javascript
// Webhook에서 받은 데이터 처리
const conversation = $input.first().json;

// 대화에서 핵심 내용 추출
const title = conversation.title || extractTitle(conversation.messages);
const category = conversation.category || detectCategory(conversation.messages);
const content = conversation.messages
  .map(msg => msg.content)
  .join('\n\n');

return {
  json: {
    title,
    content,
    category,
    tags: conversation.tags || [],
    date: new Date().toISOString().split('T')[0],
    metadata: {
      source: 'ai_conversation',
      conversation_id: conversation.id
    }
  }
};
```

## 4. 고급 기능

### 4.1 다중 소스 통합

**Merge 노드 사용:**
- 여러 소스(RSS, API, DB)에서 데이터 수집
- Merge 노드로 통합
- 중복 제거 (제목 + 날짜 기준)

### 4.2 태그 자동 생성

**키워드 분석:**
```javascript
// Code 노드
const content = $json.content + ' ' + $json.title;
const keywords = {
  '연준': '금리정책',
  'QT': '금리정책',
  '레포': '금융시장',
  '업스타트': '핀테크',
  // ... 더 많은 키워드 매핑
};

const detectedTags = [];
Object.keys(keywords).forEach(keyword => {
  if (content.includes(keyword)) {
    detectedTags.push(keywords[keyword]);
  }
});

return {
  json: {
    ...$json,
    tags: [...new Set([...$json.tags, ...detectedTags])]
  }
};
```

### 4.3 POSTS_OVERVIEW.md 자동 업데이트

**Code 노드:**
```javascript
// 기존 POSTS_OVERVIEW.md 읽기
const overview = $('Read Overview').json.content;

// 새 포스트 정보 추가
const newEntry = `- [${$json.title}](/${$json.category}/${$json.date}-${$json.filename.replace('.md', '')}/) - ${$json.date}`;

// 적절한 카테고리 섹션에 추가
const updatedOverview = addToCategory(overview, $json.category, newEntry);

// GitHub에 업데이트
return {
  json: {
    path: 'docs/POSTS_OVERVIEW.md',
    content: updatedOverview,
    message: 'Update POSTS_OVERVIEW.md'
  }
};
```

## 5. 보안 및 모니터링

### 5.1 GitHub Personal Access Token 관리

- n8n Credentials에 저장
- 최소 권한 원칙: `repo` 스코프만 부여
- 정기적으로 토큰 갱신

### 5.2 Rate Limit 관리

**Delay 노드 추가:**
- GitHub API 호출 사이에 1초 지연
- 여러 파일 처리 시 배치 처리

### 5.3 에러 핸들링

**Try-Catch 패턴:**
```javascript
// Code 노드
try {
  // 처리 로직
  return { json: { success: true, data: result } };
} catch (error) {
  return { 
    json: { 
      success: false, 
      error: error.message,
      stack: error.stack
    } 
  };
}
```

**재시도 로직:**
- IF 노드로 에러 감지
- Loop 노드로 최대 3회 재시도
- 실패 시 알림 전송

## 6. 테스트 및 디버깅

### 6.1 로컬 테스트

1. Manual Trigger로 즉시 실행
2. 각 노드의 출력 데이터 확인
3. Code 노드에 `console.log()` 추가하여 디버깅

### 6.2 스테이징 브랜치 활용

- 프로덕션(`main`) 대신 `auto-posts` 브랜치에 먼저 푸시
- 검증 후 수동으로 `main`으로 먼지

### 6.3 검증 체크리스트

- [ ] Front Matter 형식 올바른가?
- [ ] 파일명 형식 올바른가? (`YYYY-MM-DD-제목.md`)
- [ ] 카테고리가 유효한가? (`daily/dev/document/study`)
- [ ] 금지어가 포함되지 않았는가?
- [ ] 이모지가 포함되지 않았는가?
- [ ] 참조 링크가 올바르게 형식화되었는가?
- [ ] 본문이 최소 길이를 만족하는가? (100자 이상)

## 7. 배포 및 운영

### 7.1 n8n 클라우드 vs Self-hosted

**n8n 클라우드:**
- 별도 서버 관리 불필요
- 무료 플랜: 월 2,000 실행
- 유료 플랜: 더 많은 실행 및 고급 기능

**Self-hosted:**
- 더 많은 제어권
- 무제한 실행
- 서버 관리 필요

### 7.2 백업 및 복구

- 워크플로우 설정을 정기적으로 Export
- GitHub에 워크플로우 JSON 파일 저장
- 문제 발생 시 백업에서 복구

### 7.3 모니터링 알림

- 워크플로우 실행 실패 시 Slack/Email 알림
- 주간 요약 리포트 (생성된 포스트 수, 실패 건수 등)

## 참고 자료

- [n8n 공식 문서](https://docs.n8n.io/)
- [GitHub REST API 문서](https://docs.github.com/en/rest)
- [Jekyll Front Matter 가이드](https://jekyllrb.com/docs/front-matter/)
- [스타일 가이드](/_posts/2024-01-25-스타일-가이드.md)



