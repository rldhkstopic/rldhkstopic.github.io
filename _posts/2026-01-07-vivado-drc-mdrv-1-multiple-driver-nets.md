---
layout: post
title: "[오류] [DRC MDRV-1] Multiple Driver Nets"
date: 2026-01-07 12:00:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Vivado, DRC, MDRV-1, MultipleDrivers]
views: 0
---

Vivado에서 합성/구현 단계로 넘어갈 때 `[DRC MDRV-1] Multiple Driver Nets`가 발생하는 경우가 있다. 이 오류는 특정 네트가 **둘 이상의 드라이버에 의해 구동**된다는 의미다. RTL 시뮬레이션에서는 의도치 않게 통과하는 경우가 있어, 빌드 단계에서 처음 드러나는 편이다.

### 개요

- 증상: `[DRC MDRV-1] Multiple Driver Nets` DRC 발생
- 주요 원인: 동일 네트를 둘 이상의 드라이버가 구동
- 해결 방향: 단일 드라이버 구조로 정규화(프로세스/할당 지점 통합)

### 언제 발생하나

대표적인 패턴은 다음과 같다.

- 하나의 `signal`을 **서로 다른 프로세스**에서 동시에 할당하는 경우다.
- 조합 논리와 순차 논리(클럭드 프로세스)가 같은 신호를 동시에 구동하는 경우다.
- `inout`/트라이스테이트를 의도했지만, FPGA 내부 로직에서 트라이스테이트가 합성 불가인 구간에 걸린 경우다.

### 재현 코드(의도치 않은 다중 드라이버)

아래 예제는 `a`를 두 개의 프로세스에서 각각 할당해 다중 드라이버를 만든다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity mdrv_demo is
  port (
    clk : in  std_logic;
    en  : in  std_logic;
    a   : out std_logic
  );
end entity;

architecture rtl of mdrv_demo is
  signal a_i : std_logic;
begin
  a <= a_i;

  p1 : process(clk)
  begin
    if rising_edge(clk) then
      if en = '1' then
        a_i <= '1';
      end if;
    end if;
  end process;

  p2 : process(clk)
  begin
    if rising_edge(clk) then
      a_i <= '0';
    end if;
  end process;
end architecture;
```

이 경우 `a_i`는 `p1`, `p2` 두 프로세스에 의해 구동된다. VHDL 언어 자체는 다중 드라이버를 허용할 수 있으나, 합성 관점에서는 보통 단일 드라이버 네트로 정규화해야 한다.

### 해결 원칙

해결 방향은 “한 신호는 한 군데에서만 할당한다”로 귀결된다. 실제로는 아래 중 하나로 정리하는 경우가 많다.

#### 1) 단일 프로세스에서 우선순위를 명확히 합치기

```vhdl
process(clk)
begin
  if rising_edge(clk) then
    if en = '1' then
      a_i <= '1';
    else
      a_i <= '0';
    end if;
  end if;
end process;
```

여기서 중요한 점은 **모든 분기에서 `a_i`가 정확히 1회 할당**되도록 만드는 것이다. “조건에 따라 어떤 프로세스가 쓰도록 한다”는 발상은 합성에서 그대로 성립하지 않는 경우가 많다.

#### 2) 여러 조건을 다루는 경우, next-state 방식으로 분리하기

조합 논리에서 `a_next`를 계산하고, 클럭드 프로세스에서 `a_i <= a_next`로 단일 할당을 유지하는 방식이다. 이 방식은 코드가 길어지더라도 “드라이버 1개”라는 구조를 유지하기 쉽다.

### 유사 사례

동일한 문제는 “signal has multiple drivers”, “net has multiple drivers” 같은 형태로 반복된다.[^1][^2]

## References

[^1]: [Vivado Error: [DRC MDRV-1] Multiple Driver Nets](https://stackoverflow.com/questions/78379796/vivado-error-drc-mdrv-1-multiple-driver-nets)
[^2]: [Signal has multiple drivers](https://stackoverflow.com/questions/17054181/signal-has-multiple-drivers)

