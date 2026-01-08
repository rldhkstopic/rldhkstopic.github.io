# 버전/커밋 메시지/변경 이력 관리 규칙

이 문서는 이 저장소의 **버전 관리 방식**, **커밋 메시지 형식**, **변경 이력 기록 방법**을 정의한다.  
목표는 “배포에 반영된 변경사항을 버전 단위로 추적 가능하게 만드는 것”이다.

## 버전 문자열(`VERSION` 파일)

- **파일**: `VERSION`
- **형식**: `vMAJOR.MINOR.PATCH` (예: `v0.0.3`)
- **의미**
  - **MAJOR**: 호환성 파괴 변경(레이아웃/URL/빌드 파이프라인 변경 등)
  - **MINOR**: 기능 추가(호환성 유지)
  - **PATCH**: 버그 수정/스타일 수정/문서 보강

## 언제 버전을 올리나

- **사용자 화면/동작이 바뀌는 변경**: 최소 PATCH 증가
- **새 기능 추가**: MINOR 증가
- **URL 구조/카테고리 구조/자동화 파이프라인의 출력 형태가 바뀌는 변경**: MAJOR 또는 MINOR(영향 범위에 따라)
- **순수 CI 로그/주석/오타 정도**: 보통 버전 유지(필요 시 PATCH)

## 커밋 메시지 규칙(필수)

> 이 저장소는 커밋 메시지를 **영어**로 작성한다.

### 기본 형식

`[vMAJOR.MINOR.PATCH] Verb: brief description`

- **Verb**: imperative mood (Add/Update/Fix/Refactor/Remove/Document 등)
- **brief description**: “왜(의도)” 중심으로 1줄 요약

예시:

- `[v0.0.3] Fix: show today visitors in mobile profile bar`
- `[v0.0.3] Update: simplify mobile header layout`
- `[v0.0.3] Document: add versioning and changelog policy`

### 자동화(GitHub Actions) 커밋 형식

워크플로에서 생성되는 커밋도 동일하게 `VERSION`을 prefix로 사용한다.

- **Analytics 갱신**: `[vX.Y.Z] Update analytics data [skip ci]`
- **Auto-post**: `[vX.Y.Z] Auto-post: <short reason>`
- **Daily diary**: `[vX.Y.Z] Auto-diary: <short reason>`

## 변경 이력(CHANGELOG) 기록 규칙

- **파일**: `CHANGELOG.md`
- **단위**: 버전 섹션 기준(`## [vX.Y.Z] - YYYY-MM-DD`)
- **형식**
  - **Added / Changed / Fixed / Removed** 중 해당되는 항목만 사용
  - 항목은 간결한 명사구/구문으로 작성
  - “배포 시 사용자가 체감하는 변화” 위주로 기록

## “반영이 안 된다” 체크리스트

- **원격 반영 여부**: `origin/main`에 커밋이 올라갔는지 확인
- **모바일 전용 UI 여부**: 화면 폭 조건/미디어쿼리 조건에서만 보이는 요소인지 확인
- **캐시**: CSS/JS 캐시로 인해 즉시 안 보일 수 있음(캐시 버스팅 적용 여부 확인)

