---
layout: post
title: "⚠️ inferred latch"
date: 2026-01-07 12:10:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Vivado, Latch, Synthesis, Combinational]
views: 0
permalink: /dev/5/
---

합성 로그에서 `inferred latch` 또는 “래치가 추론되었다”는 경고를 보는 경우가 있다. 이는 조합 논리로 의도한 프로세스가 모든 입력 조합에서 값을 결정하지 못해, 합성기가 **상태를 기억해야 하는 소자(래치)**로 구현했다고 판단한 상황이다.

### 개요

- 증상: `inferred latch` 경고/래치 추론
- 주요 원인: 조합 프로세스에서 일부 분기 할당 누락
- 해결 방향: 기본값 할당 또는 모든 분기에서 1회 할당 보장

### 언제 발생하나

대부분의 원인은 단순하다.

- 조합 프로세스에서 일부 분기 할당 누락
- `if/elsif` 체인에서 `else`/기본값 누락(값 유지 요구)
- `case` 문에서 `when others` 또는 일부 가지 할당 누락

### 재현 코드(조합 프로세스에서 할당 누락)

아래 코드는 `en='0'`일 때 `y`가 할당되지 않는다. 이 경우 `y`는 이전 값을 유지해야 하므로 래치가 추론된다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity latch_demo is
  port (
    en : in  std_logic;
    a  : in  std_logic;
    y  : out std_logic
  );
end entity;

architecture rtl of latch_demo is
  signal y_i : std_logic;
begin
  y <= y_i;

  process(en, a)
  begin
    if en = '1' then
      y_i <= a;
    end if;
  end process;
end architecture;
```

### 해결 원칙

의도적으로 래치를 쓰는 것이 아니라면, 조합 프로세스는 다음을 만족해야 한다.

- 프로세스 시작에서 기본값 선할당
- 모든 분기에서 신호 1회 할당 보장

#### 기본값을 둔 안전한 패턴

```vhdl
process(en, a)
begin
  y_i <= '0'; -- 기본값
  if en = '1' then
    y_i <= a;
  end if;
end process;
```

이 방식은 `en='0'`일 때 `y_i`가 명확히 `'0'`이 되므로 래치가 생기지 않는다. 기본값을 어떤 값으로 둘지는 설계 의도에 따라 달라진다.

### 자주 헷갈리는 지점

“조건이 아닐 때 값을 유지”가 스펙이면 래치가 맞을 수 있다. 하지만 FPGA 설계에서는 대부분 **플립플롭 기반 상태기계**로 의도를 구현하는 경우가 많다. 따라서 유지가 필요하면 조합이 아니라 클럭드 프로세스로 옮기는 편이 일반적으로 안전하다.

### 유사 사례

래치 추론은 FSM/리셋/중첩 if 구문에서 특히 자주 질문으로 반복된다.[^1][^2][^3]

## References

[^1]: [VHDL inferring latches](https://stackoverflow.com/questions/34088925/vhdl-inferring-latches)
[^2]: [Inferring Latch in a nested If-Else statement (VHDL)](https://stackoverflow.com/questions/54817633/inferring-latch-in-a-nested-if-else-statement-vhdl)
[^3]: [VHDL - Inferred Latch With Reset - FSM](https://stackoverflow.com/questions/58868525/vhdl-inferred-latch-with-reset-fsm)

