---
layout: post
title: "[오류] wait statement not supported for synthesis"
date: 2026-01-07 12:40:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Vivado, Synthesis, wait, Testbench]
views: 0
permalink: /dev/8/
---

VHDL에서 `wait` 문은 시뮬레이션에서는 매우 편하지만, 합성에서는 제한이 크다. Vivado 합성에서 `wait statement not supported for synthesis`류의 메시지가 나오면, 대부분 “테스트벤치용 문법을 RTL에 섞어 넣었다”는 의미다.

### 개요

- 증상: `wait statement not supported for synthesis` 류의 합성 불가
- 주요 원인: RTL(합성 대상)에 `wait`/시간 지연 문법 혼입
- 해결 방향: 테스트벤치/RTL 분리, 지연은 클럭+카운터/상태기계로 치환

### 언제 발생하나

대표적인 상황은 다음과 같다.

- RTL(합성 대상) 파일에 `wait for 10 ns;` 같은 시간 지연 포함
- 조합/순차 프로세스 안에 `wait until ...`로 이벤트 대기 구현
- 클럭 생성/stimulus 생성 코드를 RTL에 혼입

### 재현 코드(합성 불가 패턴)

```vhdl
process
begin
  a <= '0';
  wait for 10 ns; -- 합성 불가
  a <= '1';
  wait;
end process;
```

이 코드는 테스트벤치에서는 자연스럽지만, 하드웨어로 변환할 수 있는 구조가 아니다. 시간 지연은 실제 회로에서는 “클럭과 카운터”로 구현해야 한다.

### 해결 원칙

#### 1) 테스트벤치와 RTL을 분리한다

`wait`는 테스트벤치 파일에서만 쓰고, RTL에는 클럭드 프로세스와 상태기계로 동작을 표현한다.

#### 2) “시간 지연”을 “카운터 기반”으로 변환한다

예를 들어 100MHz에서 10ns는 1클럭에 해당하므로, 실제로는 다음처럼 표현한다.

```vhdl
process(clk)
begin
  if rising_edge(clk) then
    a <= '1';
  end if;
end process;
```

지연이 여러 클럭이라면 카운터를 두고, `if count = N then ...` 형태로 상태 전이를 만든다.

### 유사 사례

합성 가능한 `wait`의 제한(예: 특정 형태의 `wait until rising_edge(clk)`만 허용되는 툴 체인)이 자주 논의된다.[^1][^2][^3]

## References

[^1]: [Synthesizable wait statement in VHDL](https://stackoverflow.com/questions/25924909/synthesizable-wait-statement-in-vhdl)
[^2]: [Wait statement to be synthesizable](https://stackoverflow.com/questions/43964745/wait-statement-to-be-synthesizable)
[^3]: [How to wait for a signal to be assigned new value within a process without using wait statement in vhdl](https://stackoverflow.com/questions/51697633/how-to-wait-for-a-signal-to-be-assigned-new-value-within-a-process-without-using)

