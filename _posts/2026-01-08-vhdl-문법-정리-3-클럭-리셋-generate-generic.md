---
layout: post
title: "VHDL 문법 정리 (3): 클럭/리셋 템플릿, generate/generic, 구조 확장"
date: 2026-01-08 10:55:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, VHDL-2008, reset, clock, generate, generic, RTL]
views: 0
permalink: /dev/14/
series: "VHDL 문법 정리"
series_order: 3
---

1~2편에서 문법 블록의 경계와 타입/시간 모델을 잡았다. 남는 실전 문제는 “회로는 나왔는데 방식이 제각각이라 유지보수 비용이 커지는 문제”다. 이 문제는 문법 이해 부족보다, **클럭/리셋 템플릿과 구조 확장 패턴을 팀 단위로 합의하지 못한 것**에서 시작되는 경우가 많다. 이 글에서는 합성 가능한 RTL의 관점에서, 가장 자주 쓰는 템플릿을 명시적으로 적어둔다.

### 클럭 프로세스 템플릿(동기 리셋 기준)

동기 리셋은 `rising_edge(clk)` 내부에서 리셋을 처리한다. 합성기 입장에서는 레지스터의 `CE/RESET` 매핑이 단순해지고, 타이밍/CDC 측면에서도 일관성이 생긴다. 다만 보드/시스템 요구사항(전원 인가 직후 초기화 등)에 따라 비동기 리셋이 필요한 경우도 있다.

아래는 동기 리셋의 최소 템플릿이다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity sync_reset_reg is
  generic ( WIDTH : natural := 8 );
  port (
    clk   : in  std_logic;
    rst_n : in  std_logic;
    d     : in  std_logic_vector(WIDTH-1 downto 0);
    q     : out std_logic_vector(WIDTH-1 downto 0)
  );
end entity;

architecture rtl of sync_reset_reg is
  signal r : std_logic_vector(WIDTH-1 downto 0);
begin
  process(clk)
  begin
    if rising_edge(clk) then
      if rst_n = '0' then
        r <= (others => '0');
      else
        r <= d;
      end if;
    end if;
  end process;

  q <= r;
end architecture;
```

핵심은 다음 두 줄로 요약된다.

```vhdl
process(clk)
...
if rising_edge(clk) then
```

순차 논리의 기준을 “클럭 에지”로 고정한다. 이 패턴이 흔들리기 시작하면, 레지스터 추론이 아니라 래치/조합 경로가 섞이기 시작한다.

### 비동기 리셋 템플릿(필요할 때만)

비동기 리셋은 민감도 리스트에 리셋을 포함하고, 리셋 분기가 `rising_edge` 바깥에 위치한다. 도메인 경계에서 리셋이 비동기로 들어오면 해제 시점에서 메타안정성이 생길 수 있어, 실무에서는 “비동기 assert + 동기 deassert” 같은 정책을 함께 쓰는 편이다[^1].

```vhdl
process(clk, rst_n)
begin
  if rst_n = '0' then
    r <= (others => '0');
  elsif rising_edge(clk) then
    r <= d;
  end if;
end process;
```

이 템플릿은 문법적으로는 단순하지만, 시스템 수준 정책이 없으면 오히려 문제를 만든다. 그래서 “기본은 동기 리셋, 필요할 때만 비동기 리셋”이라는 룰이 보통은 안전하다.

### generate: 복제(Replication)와 조건 분기(Elaboration)

`generate`는 런타임이 아니라 **엘라보레이션(elaboration) 시점에 구조를 생성**하는 문법이다. 이 관점이 잡히지 않으면, `if generate`를 런타임 if처럼 착각하는 문제가 생긴다.

자주 쓰는 두 가지 패턴만 정리한다.

- `for generate`: 반복 인스턴스 생성
- `if generate`: 파라미터에 따른 구조 선택

### 예제: WIDTH에 따른 2-way 구현 선택(if generate)

아래 코드는 `WIDTH`가 작을 때는 단순 리플 캐리, 클 때는 파이프라인 구조로 “구현 선택지”를 나누는 예시다. 실제로는 더 복잡한 구조가 되지만, 문법 구조만 보려는 목적이다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity add_select is
  generic (
    WIDTH : natural := 8
  );
  port (
    a : in  std_logic_vector(WIDTH-1 downto 0);
    b : in  std_logic_vector(WIDTH-1 downto 0);
    y : out std_logic_vector(WIDTH-1 downto 0)
  );
end entity;

architecture rtl of add_select is
begin
  gen_small: if WIDTH <= 8 generate
    y <= std_logic_vector(unsigned(a) + unsigned(b));
  end generate;

  gen_large: if WIDTH > 8 generate
    -- 예시용: 여기서는 동일 연산을 쓰지만, 실제로는 파이프라인/캐리 체인 등으로 분기 가능하다.
    y <= std_logic_vector(unsigned(a) + unsigned(b));
  end generate;
end architecture;
```

핵심은 `if WIDTH <= 8 generate` 자체가 “회로 생성 단계에서 분기”라는 점이다. 이 분기는 시뮬레이션 시간 축에서 변하지 않는다.

### 예제: 비트 단위 로직 복제(for generate)

다음은 비트 단위 논리를 반복 생성하는 예시다. 실제 합성에서는 이런 구조를 굳이 generate로 쓰지 않아도 되지만, “구조 복제”를 확실히 보여준다.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity bit_mask is
  generic ( WIDTH : natural := 8 );
  port (
    en : in  std_logic;
    x  : in  std_logic_vector(WIDTH-1 downto 0);
    y  : out std_logic_vector(WIDTH-1 downto 0)
  );
end entity;

architecture rtl of bit_mask is
begin
  gen_bits: for i in 0 to WIDTH-1 generate
    y(i) <= x(i) and en;
  end generate;
end architecture;
```

여기서 `i`는 런타임 변수처럼 증가하는 값이 아니라, 회로를 N개 찍어내기 위한 인덱스다. 즉 “동작이 반복된다”가 아니라 “구조가 반복된다”로 이해해야 한다.

### generic: 파라미터는 “인터페이스의 일부”로 다루기

`generic`은 그냥 상수 전달 통로가 아니라, 설계 블록의 인터페이스를 결정한다. 그래서 다음 관례를 추천한다.

- 타입을 `natural/positive`로 제한
- 의미 단위 이름 사용(`WIDTH`, `DEPTH`, `PIPE_STAGES`)
- 변환 최소화(타입 경계에서만 변환)

이 관례를 지키면, generate와 결합했을 때 “구조 선택”을 안전하게 만들 수 있다.

### 마무리 메모

이 시리즈는 VHDL의 모든 문법을 열거하지 않았다. 대신 RTL 작성에서 반복적으로 쓰는 문법을 “시간 모델/구조 모델” 관점에서 고정했다. 이후에는 오류 포스트(합성 불가 구문, 타입 미스매치, 민감도 리스트 누락 등)와 연결하면 학습 루프가 닫힌다.

작성자: rldhkstopic

## References

[^1]: [Xilinx UG901 Vivado Synthesis](https://docs.xilinx.com/r/en-US/ug901-vivado-synthesis) - 리셋 추론 및 합성 관점의 일반 가이드를 제공한다.

