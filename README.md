# rldhkstopic 블로그

GitHub Pages를 사용한 개인 블로그입니다.

## 기능

- Jekyll 기반 정적 사이트
- 카테고리별 포스트 분류
- Hits API를 통한 방문자 수 카운팅
- 반응형 디자인

## 방문자 수 카운팅

이 블로그는 [Hits API](https://hits.seeyoufarm.com)를 사용하여 방문자 수를 카운팅합니다.

### Hits API 사용법

Hits는 특정 URL이 얼마나 많이 새로고침 되었는지를 알려주는 API입니다. 

사이드바의 "전체 방문자" 섹션에서 실시간 방문자 수를 확인할 수 있습니다.

### 커스터마이징

Hits Badge는 `index.html`의 방문자 통계 섹션에서 설정할 수 있습니다.

```html
<img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url={{ site.url | url_encode }}&count_bg=%23FFFFFF&title_bg=%23FFFFFF&icon=&icon_color=%23E7E7E7&title=Visitors&edge_flat=false"/>
```

더 많은 커스터마이징 옵션은 [Hits 사이트](https://hits.seeyoufarm.com)에서 확인할 수 있습니다.

## 포스트 작성

`_posts/` 폴더에 `YYYY-MM-DD-제목.md` 형식으로 파일을 생성하세요.

```markdown
---
layout: post
title: "포스트 제목"
date: 2024-01-15
category: study
tags: [태그1, 태그2]
views: 0
---

포스트 내용...
```

## 참고 자료

- [Jekyll 공식 문서](https://jekyllrb.com/docs/)
- [GitHub Pages 가이드](https://pages.github.com/)
- [Hits API](https://hits.seeyoufarm.com)


