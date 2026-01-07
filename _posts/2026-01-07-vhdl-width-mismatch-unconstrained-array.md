---
layout: post
title: "[오류] width mismatch"
date: 2026-01-07 12:30:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Vivado, WidthMismatch, std_logic_vector, Array]
views: 0
permalink: /dev/7/
---

VHDL에서 폭 불일치 오류는 거의 모든 설계에서 한 번은 만난다. Vivado에서는 “width mismatch”, “cannot match”, “range mismatch” 같은 형태로 보이는데, 실질적으로는 **좌변과 우변의 비트 폭이 다르다**는 의미다.

### 개요

- 증상: `width mismatch`/`range mismatch` 류의 폭 불일치
- 주요 원인: 슬라이스 범위 오류, 패딩/확장 누락, unconstrained array 연결 실수
- 해결 방향: 의도에 맞는 패딩/확장/슬라이스로 폭을 명시적으로 일치

### 언제 발생하나

자주 나오는 패턴은 다음과 같다.

- 상수/리터럴 폭 미지정으로 기본 폭과 기대 폭 불일치
- `std_logic_vector` 슬라이스 범위 지정 오류
- unconstrained array 포트 연결 시 실제 폭 불일치

### 재현 코드(슬라이스 폭 불일치)

아래는 `a(7 downto 0)` 8비트에 `b(3 downto 0)` 4비트를 그대로 할당해 폭 불일치를 만드는 예다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity width_demo is
  port (
    a : out std_logic_vector(7 downto 0);
    b : in  std_logic_vector(3 downto 0)
  );
end entity;

architecture rtl of width_demo is
begin
  a <= b; -- 폭 불일치
end architecture;
```

### 해결 패턴

#### 1) 의도를 명확히 해서 확장/패딩한다

아래는 상위 비트를 0으로 패딩하는 방식이다.

```vhdl
a <= (7 downto 4 => '0') & b;
```

#### 2) 슬라이스로 정확히 맞춰 넣는다

```vhdl
a(3 downto 0) <= b;
a(7 downto 4) <= (others => '0');
```

프로젝트 규모가 커질수록 “한 줄로 끝내려는 습관”이 오히려 오류를 숨긴다. 분해해서 쓰는 편이 디버깅 비용이 낮다.

### unconstrained array 포트에서 특히 조심할 점

VHDL-2008에서 unconstrained array를 포트로 쓰는 경우, 컴포넌트 인스턴스에서 실제 폭을 결정하는 지점이 많아진다. 이때는 “타입/서브타입”을 통일해서 폭이 한 군데에서만 결정되도록 구성하는 편이 안전하다.

### 유사 사례

폭 불일치 관련 질문은 VHDL-2008의 width mismatch 형태로 반복된다.[^1]

## References

[^1]: [VHDL 2008 Width mismatch](https://stackoverflow.com/questions/64466777/vhdl-2008-width-mismatch)

