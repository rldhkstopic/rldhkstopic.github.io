---
layout: post
title: "⚠️ Generic parameter error"
date: 2026-01-08 11:00:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Generic, Parameter, Instantiation, Configuration]
views: 0
permalink: /dev/16/
---

VHDL에서 제네릭(generic) 파라미터 오류가 발생하는 경우가 있다. `generic map`에서 타입 불일치, 범위 초과, 필수 제네릭 누락 등이 원인이 될 수 있다. 제네릭은 엔티티의 재사용성을 높이기 위한 파라미터이므로 올바르게 전달해야 한다.

### 개요

- 증상: `generic type mismatch`, `generic value out of range`, `generic not found`
- 주요 원인: 제네릭 타입 불일치, 범위 초과, 필수 제네릭 누락
- 해결 방향: 제네릭 선언과 전달 값 일치 확인, 범위 검증

### 언제 발생하나

대표적인 상황은 다음과 같다.

- 제네릭 타입 불일치 (예: `integer` vs `natural`)
- 제네릭 값이 선언된 범위를 벗어남
- 필수 제네릭 파라미터 누락
- 제네릭 기본값이 없는 경우 값을 전달하지 않음
- 제네릭 이름 오타

### 재현 코드(제네릭 타입 불일치)

아래 코드는 제네릭으로 `natural`을 선언했지만 음수 값을 전달해 오류가 발생한다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- 제네릭을 사용하는 엔티티
entity shift_register is
  generic (
    WIDTH : natural := 8;  -- natural은 0 이상의 정수
    DEPTH : positive := 4  -- positive는 1 이상의 정수
  );
  port (
    clk   : in  std_logic;
    rst   : in  std_logic;
    din   : in  std_logic_vector(WIDTH-1 downto 0);
    dout  : out std_logic_vector(WIDTH-1 downto 0)
  );
end entity;

architecture rtl of shift_register is
  type reg_array is array (0 to DEPTH-1) of std_logic_vector(WIDTH-1 downto 0);
  signal regs : reg_array;
begin
  process(clk, rst)
  begin
    if rst = '1' then
      regs <= (others => (others => '0'));
    elsif rising_edge(clk) then
      regs(0) <= din;
      for i in 1 to DEPTH-1 loop
        regs(i) <= regs(i-1);
      end loop;
    end if;
  end process;
  dout <= regs(DEPTH-1);
end architecture;
```

```vhdl
-- 잘못된 인스턴스화 (제네릭 값 오류)
library ieee;
use ieee.std_logic_1164.all;

entity top is
  port (
    clk  : in  std_logic;
    rst  : in  std_logic;
    data : in  std_logic_vector(7 downto 0);
    out  : out std_logic_vector(7 downto 0)
  );
end entity;

architecture rtl of top is
  component shift_register is
    generic (
      WIDTH : natural;
      DEPTH : positive
    );
    port (
      clk  : in  std_logic;
      rst  : in  std_logic;
      din  : in  std_logic_vector(WIDTH-1 downto 0);
      dout : out std_logic_vector(WIDTH-1 downto 0)
    );
  end component;
begin
  inst_shift : shift_register
    generic map (
      WIDTH => -8,  -- 오류: natural은 음수 불가
      DEPTH => 0    -- 오류: positive는 0 불가
    )
    port map (
      clk  => clk,
      rst  => rst,
      din  => data,
      dout => out
    );
end architecture;
```

### 해결 원칙

#### 1) 제네릭 타입과 값 일치

제네릭 선언의 타입과 전달하는 값의 타입이 일치해야 한다. `natural`은 0 이상, `positive`는 1 이상의 정수만 가능하다.

```vhdl
inst_shift : shift_register
  generic map (
    WIDTH => 8,   -- 올바른 값
    DEPTH => 4    -- 올바른 값
  )
  port map (
    clk  => clk,
    rst  => rst,
    din  => data,
    dout => out
  );
```

#### 2) 제네릭 기본값 활용

제네릭에 기본값이 있으면 인스턴스화 시 생략할 수 있다. 기본값이 없으면 반드시 값을 전달해야 한다.

```vhdl
-- 기본값이 있는 경우 생략 가능
inst_shift : shift_register
  generic map (
    DEPTH => 8  -- WIDTH는 기본값 8 사용
  )
  port map (
    clk  => clk,
    rst  => rst,
    din  => data,
    dout => out
  );
```

#### 3) 제네릭 범위 확인

제네릭 값이 실제 사용되는 범위를 벗어나지 않도록 확인한다. 예를 들어, `WIDTH-1`을 인덱스로 사용한다면 `WIDTH >= 1`이어야 한다.

#### 4) 제네릭 이름 정확히 일치

제네릭 이름이 엔티티 선언과 정확히 일치해야 한다. 대소문자를 구분하므로 주의해야 한다.

### 자주 헷갈리는 지점

제네릭은 컴파일 타임 상수이므로, 런타임에 변경할 수 없다. 동적으로 크기를 변경하려면 제네릭이 아닌 다른 방법(예: 최대 크기로 설계 후 사용 시 제한)을 사용해야 한다.

### 유사 사례

제네릭 파라미터 오류는 타입 불일치와 범위 초과가 주요 원인으로 자주 질문된다.[^1][^2][^3]

## References

[^1]: [VHDL generic parameter error](https://stackoverflow.com/questions/tagged/vhdl+generic)
[^2]: [Generic type mismatch in VHDL](https://stackoverflow.com/questions/18062059/vhdl-process-all-sensitivity-list)
[^3]: [VHDL generic value out of range](https://stackoverflow.com/questions/46791502/object-is-used-but-not-declared)
