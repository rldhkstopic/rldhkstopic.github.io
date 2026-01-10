# Dev 카테고리 GitBook 스타일 위키 설계

## 목표

Dev 카테고리를 GitBook 스타일의 문서 위키로 전환하여 기술 문서를 체계적으로 정리하고 탐색할 수 있도록 한다.

## 구조 설계

### 1. 레이아웃 구조

```
┌─────────────────────────────────────────────────┐
│  [헤더]                                          │
├──────────┬───────────────────────────────────────┤
│          │                                       │
│ 사이드바 │  메인 콘텐츠 영역                      │
│ (고정)   │  (스크롤 가능)                        │
│          │                                       │
│ - VHDL   │  - 문서 목차                          │
│   - 오류 │  - 문서 내용                          │
│   - 문법 │  - 코드 예제                         │
│   - 예제 │  - 관련 링크                         │
│ - Vivado │                                       │
│   - 기본 │                                       │
│   - 고급 │                                       │
│ - 기타   │                                       │
│          │                                       │
└──────────┴───────────────────────────────────────┘
```

### 2. 하위 카테고리 구조

#### VHDL
- **오류 해결 가이드**
  - 중요도/빈도별 정렬
  - 카테고리별 분류 (문법 오류, 합성 오류, 시뮬레이션 오류 등)
  - 검색 기능
- **문법 레퍼런스**
  - 설계 단위와 기본 구조
  - 타입, 신호, 프로세스
  - 클럭, 리셋, Generate, Generic
  - 기타 문법 요소
- **예제 코드**
  - 실전 예제
  - 베스트 프랙티스
- **FAQ**

#### Vivado
- **기본 사용법**
  - 프로젝트 생성
  - 시뮬레이션
  - 합성 및 구현
- **고급 기능**
  - IP 코어 사용
  - 제약 조건
  - 타이밍 분석
- **트러블슈팅**
  - DRC 오류
  - 타이밍 위반
  - 리소스 부족

#### 기타 (향후 확장)
- Verilog
- SystemVerilog
- 기타 EDA 툴

### 3. 데이터 구조

#### 오류 문서 분류

**카테고리별:**
- 문법 오류 (Syntax Errors)
- 타입 오류 (Type Errors)
- 합성 오류 (Synthesis Errors)
- 시뮬레이션 오류 (Simulation Errors)
- DRC 오류 (Design Rule Check Errors)

**중요도별:**
- Critical (즉시 수정 필요)
- High (빠른 수정 권장)
- Medium (수정 권장)
- Low (참고)

**빈도별:**
- Very Common (매우 흔함)
- Common (흔함)
- Uncommon (드묾)
- Rare (매우 드묾)

### 4. 페이지 구조

#### 메인 페이지 (`/dev/`)
- 하위 카테고리 선택 (VHDL, Vivado 등)
- 최근 업데이트 문서
- 인기 문서 (조회수 기준)
- 빠른 검색

#### 하위 카테고리 페이지 (`/dev/vhdl/`)
- 사이드바: 문서 목차
- 메인: 선택된 문서 내용
- 관련 문서 링크
- 이전/다음 문서 네비게이션

#### 문서 페이지 (`/dev/vhdl/errors/wait-statement/`)
- 문서 내용
- 관련 오류 목록
- 해결 방법
- 예제 코드
- 참고 자료

### 5. 기능 요구사항

#### 필수 기능
1. 사이드바 네비게이션 (고정, 스크롤 가능)
2. 문서 목차 자동 생성
3. 검색 기능
4. 관련 문서 링크
5. 코드 하이라이팅
6. 반응형 디자인

#### 선택 기능
1. 다크 모드 지원
2. 인쇄 최적화
3. PDF 내보내기
4. 북마크 기능
5. 댓글 시스템

### 6. 파일 구조

```
pages/
  dev.html                    # Dev 메인 페이지
  dev/
    vhdl.html                 # VHDL 메인 페이지
    vhdl/
      errors.html             # 오류 해결 가이드 목록
      syntax.html             # 문법 레퍼런스 목록
      examples.html           # 예제 목록
    vivado.html               # Vivado 메인 페이지
    vivado/
      basics.html             # 기본 사용법 목록
      advanced.html           # 고급 기능 목록
      troubleshooting.html    # 트러블슈팅 목록

_data/
  dev_structure.yml           # Dev 카테고리 구조 정의
  vhdl_errors.yml            # VHDL 오류 분류 및 메타데이터
  vhdl_syntax.yml            # VHDL 문법 구조
  vivado_guides.yml          # Vivado 가이드 구조

assets/css/
  dev-wiki.css               # Dev 위키 전용 스타일

assets/js/
  dev-wiki.js                # Dev 위키 전용 스크립트
```

### 7. 메타데이터 구조

#### 포스트 Front Matter 확장

```yaml
---
layout: dev-doc
title: "VHDL Wait Statement Not Synthesizable"
category: dev
subcategory: vhdl
doc_type: error
error_category: synthesis
error_severity: high
error_frequency: common
tags: [vhdl, synthesis, wait, error]
related_errors:
  - vhdl-inferred-latch-warning
  - vhdl-sensitivity-list-incomplete
syntax_topics:
  - process-statement
  - clock-synchronization
---
```

#### 데이터 파일 구조 (`_data/vhdl_errors.yml`)

```yaml
errors:
  - id: vhdl-wait-statement-not-synthesizable
    title: "Wait Statement Not Synthesizable"
    category: synthesis
    severity: high
    frequency: common
    tags: [wait, synthesis, process]
    related: [vhdl-inferred-latch-warning]
    post_path: "2026-01-07-vhdl-wait-statement-not-synthesizable.md"
    
  - id: vhdl-inferred-latch-warning
    title: "Inferred Latch Warning"
    category: synthesis
    severity: medium
    frequency: very_common
    tags: [latch, synthesis, process]
    related: [vhdl-wait-statement-not-synthesizable]
    post_path: "2026-01-07-vhdl-inferred-latch-warning.md"
```

### 8. UI/UX 설계

#### 사이드바
- 고정 위치 (sticky)
- 계층적 구조 표시
- 현재 위치 하이라이트
- 접기/펼치기 기능
- 검색 기능

#### 메인 콘텐츠
- 문서 제목
- 목차 (자동 생성)
- 문서 본문
- 관련 문서 섹션
- 이전/다음 네비게이션
- 댓글/피드백

#### 반응형
- 모바일: 사이드바 숨김, 햄버거 메뉴
- 태블릿: 사이드바 축소
- 데스크톱: 전체 레이아웃

### 9. 구현 단계

#### Phase 1: 기본 구조
1. Dev 메인 페이지 레이아웃 변경
2. 사이드바 네비게이션 구현
3. 하위 카테고리 페이지 생성

#### Phase 2: VHDL 섹션
1. 오류 해결 가이드 페이지
2. 오류 분류 및 정렬 기능
3. 문법 레퍼런스 통합

#### Phase 3: Vivado 섹션
1. Vivado 가이드 페이지
2. 사용법 문서 정리
3. 트러블슈팅 가이드

#### Phase 4: 고급 기능
1. 검색 기능
2. 관련 문서 자동 링크
3. 조회수 기반 인기 문서

### 10. 스타일 가이드

#### GitBook 스타일 특징
- 깔끔한 타이포그래피
- 넓은 여백
- 명확한 계층 구조
- 코드 블록 강조
- 사이드바 네비게이션

#### 색상 팔레트
- Primary: 기존 accent-color 유지
- Background: 기존 bg-primary/bg-secondary 유지
- Code: 기존 code 스타일 유지
- Border: 기존 border-color 유지

### 11. SEO 최적화

- 구조화된 데이터 (Schema.org)
- 시맨틱 HTML
- 메타 태그 최적화
- 사이트맵 업데이트

## 다음 단계

1. 설계 검토 및 승인
2. 기본 레이아웃 구현
3. VHDL 섹션 구현
4. Vivado 섹션 구현
5. 테스트 및 최적화
