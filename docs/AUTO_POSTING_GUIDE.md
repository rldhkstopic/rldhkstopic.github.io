# 자동 포스팅 시스템 가이드

매일 오전 7시에 자동으로 블로그 포스트를 생성하고 게시하는 시스템이다.

## 시스템 개요

이 시스템은 여러 에이전트를 사용하여 다음 작업을 수행한다:

1. **주제 수집 에이전트**: 뉴스, 기술 트렌드, 최신 정보를 수집
2. **콘텐츠 생성 에이전트**: Google Gemini API를 사용하여 블로그 포스트 작성
3. **검증 에이전트**: 스타일 가이드 준수 여부 확인
4. **포스트 생성 에이전트**: Jekyll 포스트 파일 생성

## 설정 방법

### 1. Gemini API 키 설정

GitHub 저장소의 Settings → Secrets and variables → Actions에서 다음 시크릿을 추가한다:

- **Name**: `GEMINI_API_KEY`
- **Value**: Google Gemini API 키 (https://makersuite.google.com/app/apikey 에서 생성)

### 2. GitHub Actions 권한 확인

워크플로우는 자동으로 저장소에 커밋하고 푸시할 수 있어야 한다. 
`GITHUB_TOKEN`은 자동으로 제공되므로 별도 설정이 필요 없다.

### 3. 스케줄 확인

워크플로우는 매일 오전 7시 (KST)에 실행된다. 
`.github/workflows/auto-post.yml` 파일에서 스케줄을 확인할 수 있다:

```yaml
schedule:
  - cron: '0 22 * * *'  # UTC 22:00 = KST 07:00 (다음날)
```

## 에이전트 상세 설명

### TopicCollectorAgent (주제 수집)

여러 소스에서 주제를 수집한다:

- **기술 뉴스**: 기술 동향 및 최신 소식
- **Hacker News**: 인기 기술 글 수집
- **트렌딩 주제**: 현재 날짜 기반 주제 생성

각 주제는 다음 정보를 포함한다:
- `title`: 제목
- `description`: 설명
- `category`: 카테고리 (daily/dev/document/study)
- `tags`: 태그 배열
- `source`: 출처

### ContentGeneratorAgent (콘텐츠 생성)

Google Gemini API를 사용하여 블로그 포스트를 생성한다.

**사용 모델**: `gemini-1.5-flash` (빠르고 비용 효율적)

**프롬프트 특징**:
- 스타일 가이드 준수 강제
- 건조하고 분석적인 문체
- 데이터 기반 분석 강조
- 참조 링크 자동 처리

### ValidatorAgent (검증)

생성된 콘텐츠가 다음 규칙을 준수하는지 검증한다:

**필수 검증 항목**:
- 제목 존재 여부
- 본문 최소 길이 (800자 이상)
- 유효한 카테고리

**경고 항목**:
- 금지어 사용 여부
- 이모지 포함 여부
- 문체 일관성
- References 섹션 존재 여부

### PostCreatorAgent (포스트 생성)

검증된 콘텐츠를 Jekyll 포스트 파일로 변환한다.

**파일명 형식**: `YYYY-MM-DD-제목.md`

**Front Matter 자동 생성**:
- layout, title, date, author
- category, tags
- views (초기값: 0)

## 워크플로우 실행

### 자동 실행

매일 오전 7시 (KST)에 자동으로 실행된다.

### 수동 실행

GitHub Actions 탭에서 워크플로우를 선택하고 "Run workflow" 버튼을 클릭한다.

## 로그 확인

GitHub Actions 탭에서 각 실행의 로그를 확인할 수 있다:

1. **Actions** 탭 클릭
2. **Auto Post Daily** 워크플로우 선택
3. 최근 실행 클릭
4. 각 단계의 로그 확인

## 문제 해결

### Gemini API 키 오류

```
❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.
```

**해결**: GitHub Secrets에 `GEMINI_API_KEY`를 추가한다.

### 콘텐츠 생성 실패

```
❌ 콘텐츠 생성에 실패했습니다.
```

**원인**:
- Gemini API 키가 유효하지 않음
- API 할당량 초과
- 네트워크 오류

**해결**: 
- API 키 확인
- Google AI Studio에서 사용량 확인
- 재시도

### 검증 실패

```
⚠️  검증 실패:
   - 본문이 너무 짧습니다 (최소 800자 필요).
```

**해결**: 
- 검증 에이전트가 자동으로 필터링하므로, 다른 주제가 선택된다.
- 계속 실패하면 주제 수집 로직을 개선한다.

### 파일 중복

```
⚠️  파일이 이미 존재합니다: 2025-12-29-제목.md
```

**해결**: 
- 자동으로 타임스탬프를 추가하여 고유한 파일명을 생성한다.
- 중복 체크 로직이 개선될 수 있다.

## 커스터마이징

### 주제 수집 소스 추가

`.github/scripts/agents/topic_collector.py` 파일을 수정하여 새로운 소스를 추가할 수 있다:

```python
def _collect_custom_source(self) -> List[Dict]:
    """커스텀 소스 수집"""
    topics = []
    # 여기에 수집 로직 추가
    return topics
```

그리고 `__init__` 메서드의 `self.sources` 리스트에 추가한다.

### 스타일 가이드 수정

`.github/scripts/agents/content_generator.py`의 `_get_system_prompt()` 메서드를 수정하여 프롬프트를 변경할 수 있다.

### 검증 규칙 수정

`.github/scripts/agents/validator.py` 파일을 수정하여 검증 규칙을 추가하거나 변경할 수 있다.

## 비용 관리

Gemini API 사용량을 모니터링하여 비용을 관리한다:

1. Google AI Studio (https://aistudio.google.com/) 접속
2. 사용량 확인
3. 필요시 모델을 `gemini-1.5-flash`에서 `gemini-1.5-pro`로 변경 (더 고품질)

**예상 비용** (gemini-1.5-flash 기준):
- 매일 1개 포스트 생성
- 무료 할당량 내에서 사용 가능 (일일 제한 확인 필요)
- 유료 플랜 사용 시 매우 저렴한 가격

## 보안 주의사항

1. **API 키 보호**: 절대 코드에 API 키를 하드코딩하지 않는다.
2. **시크릿 관리**: GitHub Secrets만 사용한다.
3. **권한 최소화**: 워크플로우는 `contents: write` 권한만 필요하다.

## 참고 자료

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Google Gemini API 문서](https://ai.google.dev/docs)
- [WRITING_STYLE_GUIDE.md](./WRITING_STYLE_GUIDE.md) - 글쓰기 스타일 가이드

