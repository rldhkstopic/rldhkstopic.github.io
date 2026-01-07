---
layout: post
title: "[오류] Incomplete sensitivity list / Missing signal in sensitivity list"
date: 2026-01-07 13:10:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, SensitivityList, Combinational, Simulation, Synthesis]
views: 0
---

조합 논리 프로세스에서 감지 리스트(sensitivity list)가 불완전하면 시뮬레이션과 합성 결과가 달라질 수 있다. 프로세스 내에서 읽는 모든 신호가 감지 리스트에 포함되지 않으면, 시뮬레이션에서는 해당 신호 변화를 놓칠 수 있다. 합성기는 보통 경고를 내지만, 시뮬레이션 동작 불일치의 주요 원인이 된다.

### 개요

- 증상: 시뮬레이션과 합성 결과 불일치, `missing signal in sensitivity list` 경고
- 주요 원인: 조합 프로세스에서 읽는 신호가 감지 리스트에 누락
- 해결 방향: 모든 읽는 신호를 감지 리스트에 포함 또는 `process(all)` 사용

### 언제 발생하나

대표적인 상황은 다음과 같다.

- `if` 문에서 사용하는 신호가 감지 리스트에 없음
- `case` 문의 선택 신호가 감지 리스트에 누락
- 중첩된 조건문에서 일부 신호만 감지 리스트에 포함
- 조합 프로세스에서 계산에 사용되는 신호 일부 누락

### 재현 코드(불완전한 감지 리스트)

아래 코드는 `b` 신호가 감지 리스트에 없어서 `b`가 변경되어도 프로세스가 재실행되지 않는다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity sensitivity_demo is
  port (
    a : in  std_logic;
    b : in  std_logic;
    y : out std_logic
  );
end entity;

architecture rtl of sensitivity_demo is
begin
  process(a) -- b가 누락됨
  begin
    if a = '1' then
      y <= b; -- b를 읽지만 감지 리스트에 없음
    else
      y <= '0';
    end if;
  end process;
end architecture;
```

이 경우 `b`가 변경되어도 프로세스가 트리거되지 않아 시뮬레이션에서 `y`가 업데이트되지 않을 수 있다.

### 해결 원칙

#### 1) 모든 읽는 신호를 감지 리스트에 포함

조합 프로세스에서는 프로세스 내에서 읽는 모든 신호를 감지 리스트에 명시해야 한다.

```vhdl
process(a, b) -- 모든 읽는 신호 포함
begin
  if a = '1' then
    y <= b;
  else
    y <= '0';
  end if;
end process;
```

#### 2) VHDL-2008의 process(all) 사용

VHDL-2008에서는 `process(all)`을 사용하면 프로세스 내에서 읽는 모든 신호가 자동으로 감지 리스트에 포함된다.

```vhdl
process(all) -- VHDL-2008: 모든 읽는 신호 자동 포함
begin
  if a = '1' then
    y <= b;
  else
    y <= '0';
  end if;
end process;
```

이 방식은 실수로 신호를 누락하는 것을 방지할 수 있어 권장된다.

#### 3) 클럭드 프로세스는 클럭과 리셋만 포함

순차 논리(클럭드 프로세스)에서는 클럭과 리셋 신호만 감지 리스트에 포함한다.

```vhdl
process(clk, rst) -- 클럭과 리셋만
begin
  if rst = '1' then
    y <= '0';
  elsif rising_edge(clk) then
    y <= a and b; -- a, b는 감지 리스트에 불필요
  end if;
end process;
```

### 자주 헷갈리는 지점

조합 프로세스와 순차 프로세스의 감지 리스트 규칙이 다르다. 조합 프로세스는 모든 읽는 신호를 포함해야 하지만, 클럭드 프로세스는 클럭과 비동기 리셋만 포함하면 된다. 클럭드 프로세스에서 데이터 신호를 감지 리스트에 넣으면 불필요한 시뮬레이션 오버헤드가 발생할 수 있다.

### 유사 사례

감지 리스트 누락은 시뮬레이션/합성 불일치의 주요 원인으로 자주 질문된다.[^1][^2][^3]

## References

[^1]: [VHDL incomplete sensitivity list](https://stackoverflow.com/questions/tagged/vhdl+sensitivity-list)
[^2]: [Missing signal in sensitivity list warning](https://stackoverflow.com/questions/17054181/signal-has-multiple-drivers)
[^3]: [VHDL-2008 process(all) usage](https://stackoverflow.com/questions/18062059/vhdl-process-all-sensitivity-list)

