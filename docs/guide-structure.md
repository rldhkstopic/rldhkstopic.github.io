# 문서 작성 가이드 구조

이 문서는 블로그 포스트 작성 시 참조해야 하는 문서들의 관계와 사용 순서를 설명합니다.

## 📚 문서 구조

### 1. GUIDE_WRITING_STYLE.md (기본 가이드) - 먼저 읽기

**역할**: 모든 카테고리에 공통으로 적용되는 기본 규칙

**포함 내용**:
- 문체 및 어조 규칙 ("~다." 평어체)
- Front Matter 필수 필드
- 글의 구조 (도입부, 본문, 결말)
- 코드 설명 방식
- 참조 표기 방법
- 전문가 인용 형식
- 카테고리별 기본 가이드 (11번 섹션)

**사용 시점**: 글을 작성하기 전에 먼저 읽어야 하는 기본 가이드

### 2. GUIDE_CATEGORY_WRITING.md (카테고리별 상세 가이드) - 선택적 참조

**역할**: 각 카테고리별 특화된 상세 가이드

**포함 내용**:
- Daily: 구어체 허용, 1인칭 시점, 감정 묘사
- Dev: 기술 블로그 작성 방법론, 소재 의식
- Study: 학습 내용 정리 방법
- Document: 데이터 분석 글 작성

**사용 시점**: 카테고리를 선택한 후, 해당 카테고리의 특수 규칙을 확인할 때

## ⚠️ 중요: Daily 카테고리 문체 충돌

현재 두 문서에서 Daily 카테고리에 대해 서로 다른 문체 규칙을 제시하고 있습니다:

### GUIDE_WRITING_STYLE.md (11번 섹션)
- "~다." 평어체 사용
- 건조하고 분석적인 문체

### GUIDE_CATEGORY_WRITING.md
- "~했다", "~였다" 구어체 허용
- 자연스러운 일기 형식
- 감정 묘사 필수

**해결 방법**: Daily 카테고리 작성 시에는 **GUIDE_CATEGORY_WRITING.md의 규칙을 우선** 적용합니다.

## 📝 작성 순서

### 1단계: 기본 가이드 읽기
```
GUIDE_WRITING_STYLE.md 읽기
→ 공통 규칙 이해 (Front Matter, 참조 형식, 코드 설명 등)
```

### 2단계: 카테고리 선택
```
카테고리 결정 (daily, dev, study, document)
```

### 3단계: 카테고리별 가이드 확인
```
GUIDE_CATEGORY_WRITING.md에서 해당 카테고리 섹션 읽기
→ 카테고리별 특수 규칙 확인
```

### 4단계: 작성 시작
```
기본 규칙 + 카테고리별 규칙을 모두 적용하여 작성
```

## 🔄 규칙 우선순위

1. **GUIDE_CATEGORY_WRITING.md의 카테고리별 규칙** (최우선)
   - 카테고리별 특수 규칙이 있으면 이를 우선 적용
   - 예: Daily 카테고리의 구어체 허용

2. **GUIDE_WRITING_STYLE.md의 공통 규칙**
   - 카테고리별 규칙이 없는 경우 기본 규칙 적용
   - Front Matter, 참조 형식 등은 모든 카테고리에서 동일

## 💡 권장 사용법

### Daily 카테고리 작성 시
1. GUIDE_WRITING_STYLE.md: Front Matter, 참조 형식 등 기본 규칙 확인
2. GUIDE_CATEGORY_WRITING.md의 Daily 섹션: 구어체, 감정 묘사 등 특수 규칙 확인
3. Daily 규칙 우선 적용 (구어체 허용)

### Dev 카테고리 작성 시
1. GUIDE_WRITING_STYLE.md: 기본 규칙 확인
2. GUIDE_CATEGORY_WRITING.md의 Dev 섹션: 소재 의식, 기술 블로그 작성법 확인
3. 기본 규칙 + Dev 특수 규칙 모두 적용

### Study/Document 카테고리 작성 시
1. GUIDE_WRITING_STYLE.md: 기본 규칙 확인
2. GUIDE_CATEGORY_WRITING.md에서 해당 섹션 확인 (선택)
3. 기본 규칙 우선 적용

## 📌 요약

- **GUIDE_WRITING_STYLE.md**: 모든 글의 기본 규칙 (필수)
- **GUIDE_CATEGORY_WRITING.md**: 카테고리별 특수 규칙 (선택, Daily는 권장)
- **우선순위**: 카테고리별 규칙 > 기본 규칙 (충돌 시)
