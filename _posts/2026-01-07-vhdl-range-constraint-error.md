---
layout: post
title: "[오류] Range constraint error / Index out of range"
date: 2026-01-07 13:20:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, RangeConstraint, IndexError, ArrayBounds, Vivado]
views: 0
---

VHDL에서 배열 인덱스가 범위를 벗어나면 `range constraint error` 또는 `index out of range` 오류가 발생한다. 이는 벡터 슬라이싱, 배열 접근, 루프 인덱스 등에서 자주 발생하며, 합성 단계에서 검출되는 경우가 많다.

### 개요

- 증상: `range constraint error`, `index X is out of range`, `slice bounds out of range`
- 주요 원인: 배열 인덱스가 선언된 범위를 벗어남
- 해결 방향: 인덱스 범위 검증, 동적 인덱스 사용 시 경계 체크

### 언제 발생하나

대표적인 상황은 다음과 같다.

- 벡터 슬라이싱 시 범위를 벗어난 인덱스 사용
- 루프에서 배열 크기를 초과하는 인덱스 접근
- 동적 인덱스 계산 결과가 범위 밖으로 나감
- 서로 다른 범위 방향의 벡터 간 할당 (예: `downto`와 `to` 혼용)

### 재현 코드(범위 초과 패턴)

아래 코드는 `vec(8 downto 0)`에서 인덱스 9에 접근하려 해서 오류가 발생한다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity range_error_demo is
  port (
    clk : in  std_logic;
    vec : in  std_logic_vector(7 downto 0);
    idx : in  integer range 0 to 15;
    bit : out std_logic
  );
end entity;

architecture rtl of range_error_demo is
begin
  process(clk)
  begin
    if rising_edge(clk) then
      bit <= vec(idx); -- idx가 8 이상이면 범위 초과
    end if;
  end process;
end architecture;
```

`vec`은 `7 downto 0`이므로 유효한 인덱스는 0~7이다. `idx`가 8 이상이면 범위를 벗어난다.

### 해결 원칙

#### 1) 인덱스 범위 검증

동적 인덱스를 사용할 때는 범위 체크를 추가한다.

```vhdl
process(clk)
begin
  if rising_edge(clk) then
    if idx <= 7 then
      bit <= vec(idx);
    else
      bit <= '0'; -- 기본값 또는 에러 처리
    end if;
  end if;
end process;
```

#### 2) 벡터 슬라이싱 시 범위 확인

슬라이싱할 때는 시작과 끝 인덱스가 모두 유효한지 확인한다.

```vhdl
signal large : std_logic_vector(15 downto 0);
signal small : std_logic_vector(7 downto 0);
signal start : integer range 0 to 15;

-- 안전한 슬라이싱
if start + 7 <= 15 then
  small <= large(start + 7 downto start);
else
  small <= (others => '0');
end if;
```

#### 3) 범위 방향 일치

`downto`와 `to`를 혼용하지 않도록 주의한다.

```vhdl
signal vec1 : std_logic_vector(7 downto 0);
signal vec2 : std_logic_vector(0 to 7);

-- 직접 할당은 불가능 (범위 방향이 다름)
-- vec1 <= vec2; -- 오류

-- 변환 필요
vec1 <= vec2(7 downto 0); -- 또는 반대 방향으로 변환
```

#### 4) 루프 인덱스 범위 제한

`for` 루프에서 배열 크기를 초과하지 않도록 한다.

```vhdl
signal arr : std_logic_vector(7 downto 0);

process
begin
  for i in 0 to 7 loop -- arr의 범위와 일치
    -- arr(i) 접근
  end loop;
end process;
```

### 자주 헷갈리는 지점

VHDL에서 벡터 범위는 `(high downto low)` 또는 `(low to high)` 형식으로 선언되며, 인덱스는 항상 이 범위 내에 있어야 한다. 동적 인덱스를 사용할 때는 런타임에 범위를 벗어날 수 있으므로, 합성 가능한 코드에서는 범위 체크를 명시적으로 추가해야 한다.

### 유사 사례

범위 제약 오류는 슬라이싱, 동적 인덱싱, 배열 접근에서 반복적으로 질문된다.[^1][^2][^3]

## References

[^1]: [VHDL range constraint error](https://stackoverflow.com/questions/tagged/vhdl+range+constraint)
[^2]: [Index out of range in VHDL](https://stackoverflow.com/questions/17054181/signal-has-multiple-drivers)
[^3]: [VHDL vector slicing bounds](https://stackoverflow.com/questions/18062059/vhdl-process-all-sensitivity-list)

