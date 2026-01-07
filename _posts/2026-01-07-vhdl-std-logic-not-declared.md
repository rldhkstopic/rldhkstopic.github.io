---
layout: post
title: "[오류] std_logic is not declared"
date: 2026-01-07 12:20:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Vivado, IEEE, std_logic_1164, Compile]
views: 0
---

VHDL 컴파일에서 `std_logic` 또는 `std_logic_vector`가 “선언되지 않았다”는 오류가 발생하는 경우가 있다. 메시지는 툴/버전에 따라 다르지만, 본질은 `std_logic` 타입 정의가 들어있는 패키지를 가져오지 않았다는 뜻이다.

### 개요

- 증상: `std_logic`/`std_logic_vector` 미선언(컴파일 실패)
- 주요 원인: `ieee.std_logic_1164` 패키지 import 누락 또는 라이브러리 설정 꼬임
- 해결 방향: `library ieee; use ieee.std_logic_1164.all;` 추가 및 컴파일 순서/라이브러리 확인

### 언제 발생하나

대표적으로 다음 상황에서 발생한다.

- 파일 상단 `library ieee; use ieee.std_logic_1164.all;` 누락
- `use` 선언은 존재하지만 `library ieee;` 누락
- Vivado 프로젝트에서 라이브러리/컴파일 순서 꼬임으로 패키지 참조 실패

### 재현 코드(패키지 누락)

아래 코드는 `std_logic`을 쓰면서 IEEE 패키지를 가져오지 않아 컴파일 오류가 난다.

```vhdl
entity missing_pkg is
  port (
    clk : in  std_logic;
    q   : out std_logic
  );
end entity;

architecture rtl of missing_pkg is
begin
  q <= clk;
end architecture;
```

### 해결 코드(IEEE std_logic_1164 추가)

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity missing_pkg is
  port (
    clk : in  std_logic;
    q   : out std_logic
  );
end entity;

architecture rtl of missing_pkg is
begin
  q <= clk;
end architecture;
```

이 패턴은 모든 파일에 반복되기 때문에, 템플릿을 만들어 두고 새 파일 생성 시 자동으로 포함시키는 편이 실수 비용을 줄인다.

### 추가로 확인할 것(Vivado 프로젝트)

Vivado에서는 파일별로 “Libraries”나 컴파일 순서가 얽히면, 동일한 패키지 이름이더라도 다른 라이브러리로 인식되어 문제가 생기는 경우가 있다. 이 경우에는 “Compile Order”를 재정렬하고, 패키지 파일이 먼저 컴파일되도록 고정하는 것이 우선이다.

### 유사 사례

`object is used but not declared` 유형으로도 자주 나타난다.[^1][^2]

## References

[^1]: [How to use an entity inside an architecture in VHDL](https://stackoverflow.com/questions/40505882/how-to-use-an-entity-inside-an-architecture-in-vhdl)
[^2]: [Object is used but not declared](https://stackoverflow.com/questions/46791502/object-is-used-but-not-declared)

