---
layout: post
title: "⚠️ Type mismatch / Type conversion error"
date: 2026-01-07 13:00:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, TypeConversion, TypeMismatch, Vivado, Synthesis]
views: 0
permalink: /dev/9/
---

VHDL에서 타입 불일치 오류는 합성 단계에서 자주 발생한다. `std_logic`과 `std_logic_vector` 사이, 또는 서로 다른 크기의 벡터 간 할당 시 타입 변환이 필요하다. 명시적 변환 없이 할당하면 `type mismatch` 또는 `no feasible entries` 오류가 발생한다.

### 개요

- 증상: `type mismatch`, `no feasible entries`, `type conversion error`
- 주요 원인: 서로 다른 타입 간 할당 시 명시적 변환 누락
- 해결 방향: 타입 변환 함수 사용 또는 적절한 타입 캐스팅

### 언제 발생하나

대표적인 상황은 다음과 같다.

- `std_logic`과 `std_logic_vector` 간 직접 할당
- 서로 다른 크기의 `std_logic_vector` 간 할당
- `integer`와 `std_logic_vector` 간 변환 누락
- `unsigned`/`signed` 타입과 `std_logic_vector` 간 변환 누락

### 재현 코드(타입 불일치 패턴)

아래 코드는 `std_logic`을 `std_logic_vector`에 직접 할당하려 해서 오류가 발생한다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity type_mismatch_demo is
  port (
    clk    : in  std_logic;
    data   : in  std_logic;
    result : out std_logic_vector(7 downto 0)
  );
end entity;

architecture rtl of type_mismatch_demo is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      result <= data; -- 타입 불일치: std_logic을 std_logic_vector에 할당
    end if;
  end process;
end architecture;
```

이 경우 `data`는 `std_logic`이고 `result`는 `std_logic_vector(7 downto 0)`이므로 직접 할당할 수 없다.

### 해결 원칙

#### 1) 명시적 타입 변환 사용

`std_logic`을 `std_logic_vector`로 변환하려면 벡터 리터럴을 사용하거나 확장 함수를 쓴다.

```vhdl
process(clk)
begin
  if rising_edge(clk) then
    result <= (others => data); -- 모든 비트에 data 할당
    -- 또는
    result <= (0 => data, others => '0'); -- LSB에만 할당
  end if;
end process;
```

#### 2) 크기가 다른 벡터 간 변환

작은 벡터를 큰 벡터에 할당할 때는 확장을 명시한다.

```vhdl
signal small : std_logic_vector(3 downto 0);
signal large : std_logic_vector(7 downto 0);

-- 방법 1: 확장 후 할당
large <= (7 downto 4 => '0', 3 downto 0 => small);

-- 방법 2: 리사이즈 함수 사용 (numeric_std 필요)
large <= std_logic_vector(resize(unsigned(small), 8));
```

#### 3) integer와 std_logic_vector 간 변환

`numeric_std` 패키지를 사용해 변환한다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

signal int_val : integer range 0 to 255;
signal vec_val : std_logic_vector(7 downto 0);

-- integer to vector
vec_val <= std_logic_vector(to_unsigned(int_val, 8));

-- vector to integer
int_val <= to_integer(unsigned(vec_val));
```

### 자주 헷갈리는 지점

VHDL은 강타입 언어이므로, C나 Python처럼 암묵적 타입 변환이 거의 없다. `std_logic`과 `std_logic_vector`는 완전히 다른 타입이며, `std_logic_vector`의 크기만 달라도 다른 타입으로 취급된다. 따라서 변환이 필요할 때는 항상 명시적으로 처리해야 한다.

### 유사 사례

타입 변환 문제는 벡터 크기 불일치, signed/unsigned 변환, integer 변환 등에서 반복적으로 질문된다.[^1][^2][^3]

## References

[^1]: [VHDL type conversion](https://stackoverflow.com/questions/tagged/vhdl+type-conversion)
[^2]: [Converting between std_logic_vector and integer](https://stackoverflow.com/questions/13954193/converting-between-std-logic-vector-and-integer)
[^3]: [VHDL std_logic to std_logic_vector conversion](https://stackoverflow.com/questions/10654485/vhdl-std-logic-to-std-logic-vector-conversion)

