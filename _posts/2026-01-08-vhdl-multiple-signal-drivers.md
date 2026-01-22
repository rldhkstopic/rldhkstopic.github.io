---
layout: post
title: "⚠️ Multiple signal drivers / Signal has multiple drivers"
date: 2026-01-08 11:30:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Driver, Process, Signal, Conflict]
views: 0
permalink: /dev/17/
---

VHDL에서 하나의 신호에 여러 프로세스나 할당문이 동시에 값을 할당하려 할 때 "multiple drivers" 오류가 발생한다. 신호는 하나의 소스(드라이버)만 가져야 하므로, 여러 프로세스에서 같은 신호를 할당하면 충돌이 발생한다.

### 개요

- 증상: `signal has multiple drivers`, `multiple drivers for signal`, `resolution function required`
- 주요 원인: 여러 프로세스에서 같은 신호 할당, 중복 할당문
- 해결 방향: 신호 할당을 단일 프로세스로 통합, 중간 신호 사용, 조건부 할당 통합

### 언제 발생하나

대표적인 상황은 다음과 같다.

- 여러 프로세스에서 같은 신호에 할당
- 같은 프로세스 내에서 조건 없이 여러 번 할당
- 여러 컴포넌트 인스턴스에서 같은 신호에 출력 연결
- 조합 논리와 순차 논리가 같은 신호에 할당

### 재현 코드(여러 프로세스에서 할당)

아래 코드는 `y` 신호를 두 프로세스에서 할당해 오류가 발생한다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity multiple_drivers_demo is
  port (
    a, b, c : in  std_logic;
    y       : out std_logic
  );
end entity;

architecture rtl of multiple_drivers_demo is
begin
  -- 첫 번째 프로세스
  process(a, b)
  begin
    y <= a and b;  -- y에 할당
  end process;
  
  -- 두 번째 프로세스 (같은 신호에 할당)
  process(c)
  begin
    y <= c;  -- 오류: y에 또 할당
  end process;
end architecture;
```

이 경우 `y` 신호가 두 프로세스에서 동시에 드라이브되어 "multiple drivers" 오류가 발생한다.

### 해결 원칙

#### 1) 단일 프로세스로 통합

여러 프로세스에서 할당하는 대신, 하나의 프로세스에서 모든 조건을 처리한다.

```vhdl
architecture rtl of multiple_drivers_demo is
begin
  process(a, b, c)
  begin
    if c = '1' then
      y <= c;
    else
      y <= a and b;
    end if;
  end process;
end architecture;
```

#### 2) 중간 신호 사용

각 프로세스에서 중간 신호에 할당한 후, 최종 출력 신호에 조합한다.

```vhdl
architecture rtl of multiple_drivers_demo is
  signal y1, y2 : std_logic;
begin
  process(a, b)
  begin
    y1 <= a and b;
  end process;
  
  process(c)
  begin
    y2 <= c;
  end process;
  
  -- 최종 출력 조합
  y <= y1 when c = '0' else y2;
end architecture;
```

#### 3) 조건부 할당 통합

조건에 따라 다른 값을 할당해야 하는 경우, 하나의 할당문에서 처리한다.

```vhdl
architecture rtl of multiple_drivers_demo is
begin
  y <= c when c = '1' else (a and b);
end architecture;
```

#### 4) std_logic_vector의 경우

`std_logic_vector`의 경우 각 비트별로 드라이버가 분리되므로, 비트별로 다른 프로세스에서 할당할 수 있다. 하지만 같은 비트에 여러 드라이버가 있으면 안 된다.

```vhdl
architecture rtl of multiple_drivers_demo is
  signal y : std_logic_vector(7 downto 0);
begin
  -- 비트별로 다른 프로세스에서 할당 가능
  process(a)
  begin
    y(0) <= a;
  end process;
  
  process(b)
  begin
    y(1) <= b;
  end process;
end architecture;
```

### 자주 헷갈리는 지점

포트 출력(`out`)은 내부에서 읽을 수 없으므로, 여러 프로세스에서 할당할 때는 내부 신호를 사용한 후 포트에 연결해야 한다. 또한 `inout` 포트는 여러 드라이버를 가질 수 있지만, 일반적으로 권장되지 않는다.

### 유사 사례

여러 드라이버 오류는 프로세스 분리와 조건부 할당 시 자주 발생하며, 단일 프로세스 통합이 일반적인 해결책이다.[^1][^2][^3]

## References

[^1]: [VHDL multiple drivers error](https://stackoverflow.com/questions/tagged/vhdl+multiple+drivers)
[^2]: [Signal has multiple drivers in VHDL](https://stackoverflow.com/questions/17054181/signal-has-multiple-drivers)
[^3]: [How to fix multiple drivers in VHDL](https://stackoverflow.com/questions/46791502/object-is-used-but-not-declared)
