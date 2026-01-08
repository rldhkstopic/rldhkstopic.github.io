---
layout: post
title: "[오류] Port mismatch / Port connection error"
date: 2026-01-08 10:30:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Port, Component, Instantiation, Connection]
views: 0
permalink: /dev/15/
---

VHDL에서 컴포넌트 인스턴스화 시 포트 연결 오류가 발생하는 경우가 있다. `port mismatch`, `no feasible entries`, `association element not found` 등의 오류는 엔티티 선언과 인스턴스화 시 포트 이름이나 타입이 일치하지 않을 때 발생한다.

### 개요

- 증상: `port mismatch`, `no feasible entries`, `association element not found`
- 주요 원인: 포트 이름 불일치, 포트 타입/방향 불일치, 포트 개수 불일치
- 해결 방향: 엔티티 선언과 인스턴스화 일치 확인, 포트 매핑 검증

### 언제 발생하나

대표적인 상황은 다음과 같다.

- 포트 이름 오타 (예: `clk` vs `clock`)
- 포트 방향 불일치 (예: `in` vs `out`)
- 포트 타입 불일치 (예: `std_logic` vs `std_logic_vector`)
- 포트 개수 불일치 (필수 포트 누락 또는 추가 포트)
- 포트 매핑 문법 오류

### 재현 코드(포트 이름 불일치)

아래 코드는 엔티티에서 `clk`로 선언했지만 인스턴스화에서 `clock`으로 연결해 오류가 발생한다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

-- 엔티티 선언
entity counter is
  port (
    clk   : in  std_logic;
    rst   : in  std_logic;
    count : out std_logic_vector(7 downto 0)
  );
end entity;

architecture rtl of counter is
  signal cnt : unsigned(7 downto 0);
begin
  process(clk, rst)
  begin
    if rst = '1' then
      cnt <= (others => '0');
    elsif rising_edge(clk) then
      cnt <= cnt + 1;
    end if;
  end process;
  count <= std_logic_vector(cnt);
end architecture;
```

```vhdl
-- 잘못된 인스턴스화 (포트 이름 불일치)
library ieee;
use ieee.std_logic_1164.all;

entity top is
  port (
    clock : in  std_logic;
    reset : in  std_logic;
    q     : out std_logic_vector(7 downto 0)
  );
end entity;

architecture rtl of top is
  component counter is
    port (
      clk   : in  std_logic;
      rst   : in  std_logic;
      count : out std_logic_vector(7 downto 0)
    );
  end component;
begin
  inst_counter : counter
    port map (
      clock => clock,  -- 오류: clk가 아니라 clock
      rst   => reset,
      count => q
    );
end architecture;
```

### 해결 원칙

#### 1) 포트 이름 정확히 일치

엔티티 선언의 포트 이름과 인스턴스화 시 포트 이름이 정확히 일치해야 한다.

```vhdl
inst_counter : counter
  port map (
    clk   => clock,  -- 올바른 매핑
    rst   => reset,
    count => q
  );
```

#### 2) 위치 기반 매핑 사용

포트 순서가 일치하면 이름 없이 위치로 매핑할 수 있다. 다만 가독성과 유지보수성을 위해 이름 기반 매핑을 권장한다.

```vhdl
inst_counter : counter
  port map (
    clock,  -- 첫 번째 포트 (clk)
    reset,  -- 두 번째 포트 (rst)
    q       -- 세 번째 포트 (count)
  );
```

#### 3) 포트 타입과 방향 확인

포트의 타입(`std_logic`, `std_logic_vector` 등)과 방향(`in`, `out`, `inout`)이 엔티티 선언과 일치해야 한다.

#### 4) 선택적 포트 처리

VHDL-2008에서는 선택적 포트를 지원하지만, 대부분의 경우 모든 포트를 연결해야 한다. 사용하지 않는 포트는 `open`으로 연결할 수 있다.

```vhdl
inst_counter : counter
  port map (
    clk   => clock,
    rst   => reset,
    count => open  -- 출력 포트를 사용하지 않는 경우
  );
```

### 자주 헷갈리는 지점

포트 매핑에서 `=>`는 "연결"을 의미한다. 왼쪽은 컴포넌트의 포트 이름이고, 오른쪽은 상위 레벨의 신호 이름이다. `포트이름 => 신호이름` 형식으로 작성한다.

### 유사 사례

포트 연결 오류는 인스턴스화 시 자주 발생하며, 이름 오타와 타입 불일치가 주요 원인이다.[^1][^2][^3]

## References

[^1]: [VHDL port mapping error](https://stackoverflow.com/questions/tagged/vhdl+port+map)
[^2]: [Port mismatch in VHDL component instantiation](https://stackoverflow.com/questions/18062059/vhdl-process-all-sensitivity-list)
[^3]: [VHDL association element not found](https://stackoverflow.com/questions/46791502/object-is-used-but-not-declared)
