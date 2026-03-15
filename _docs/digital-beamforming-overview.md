---
title: "디지털 빔포밍 기술 개요 및 FPGA 구현 전략"
description: "AESA 레이더 시스템에서의 디지털 빔포밍 알고리즘 분석과 FPGA 기반 실시간 구현 방법론을 다룬다."
author: "kiwanPark"
date: 2026-03-10
doc_category: "연구 논문"
tags: ["디지털 빔포밍", "FPGA", "AESA", "DSP", "레이더"]
version: "1.2"
github_path: "_docs/digital-beamforming-overview.md"
revisions:
  - version: "1.2"
    date: "2026-03-10"
    summary: "FPGA 리소스 사용량 분석 섹션 추가"
    changes:
      - type: added
        description: "리소스 사용량 테이블 추가"
      - type: modified
        description: "구현 전략 섹션 보완"
  - version: "1.1"
    date: "2026-02-20"
    summary: "Calibration 알고리즘 설명 보강"
    changes:
      - type: modified
        description: "캘리브레이션 섹션 확장"
      - type: added
        description: "수식 오류 수정"
  - version: "1.0"
    date: "2026-01-15"
    summary: "초기 문서 작성"
    changes:
      - type: added
        description: "전체 문서 초안 작성"
---

## 서론

능동 전자 주사 배열(AESA, Active Electronically Scanned Array) 레이더 시스템은 기계적 회전 없이 전자적으로 빔을 조향할 수 있다는 점에서 기존 레이더 대비 월등한 유연성을 제공한다. 디지털 빔포밍(DBF, Digital Beamforming)은 각 안테나 소자에서 수신된 신호를 디지털 영역에서 처리하여 빔 패턴을 형성하는 기술이다.

본 문서에서는 DBF의 핵심 알고리즘을 분석하고, FPGA 기반 실시간 구현 전략을 제시한다. 특히 위상 가중치 계산, 적응형 빔포밍, 그리고 캘리브레이션 기법에 대해 상세히 다룬다.

## 디지털 빔포밍 기본 원리

### 배열 신호 모델

$N$개의 안테나 소자로 구성된 균일 선형 배열(ULA, Uniform Linear Array)에서, $k$번째 소자가 수신하는 신호는 다음과 같이 모델링된다:

$$x_k(t) = s(t) \cdot e^{-j 2\pi f_c \tau_k} + n_k(t)$$

여기서:
- $s(t)$: 입사 신호
- $f_c$: 캐리어 주파수
- $\tau_k$: $k$번째 소자에서의 시간 지연
- $n_k(t)$: 가산 백색 가우시안 잡음(AWGN)

배열 수신 벡터를 $\mathbf{x}(t) = [x_0(t), x_1(t), \ldots, x_{N-1}(t)]^T$로 정의하면, 빔포밍 출력은 가중치 벡터 $\mathbf{w}$와의 내적으로 표현된다:

$$y(t) = \mathbf{w}^H \mathbf{x}(t)$$

### 조향 벡터(Steering Vector)

방위각 $\theta$ 방향에서 입사하는 평면파에 대한 조향 벡터는 다음과 같다:

$$\mathbf{a}(\theta) = \begin{bmatrix} 1 \\ e^{-j 2\pi d \sin\theta / \lambda} \\ \vdots \\ e^{-j 2\pi (N-1) d \sin\theta / \lambda} \end{bmatrix}$$

여기서 $d$는 소자 간격, $\lambda$는 파장이다. 일반적으로 $d = \lambda/2$로 설정하여 공간 앨리어싱을 방지한다.

### 종래 빔포밍(Conventional Beamforming)

가장 기본적인 빔포밍 방식은 지연-합산(Delay-and-Sum) 빔포밍으로, 가중치 벡터를 조향 벡터와 동일하게 설정한다:

$$\mathbf{w}_{CBF} = \frac{1}{N} \mathbf{a}(\theta_0)$$

이 방식의 빔 패턴은 다음과 같이 주어진다:

$$B(\theta) = \frac{1}{N} \sum_{k=0}^{N-1} e^{j 2\pi k d (\sin\theta - \sin\theta_0) / \lambda}$$

## 적응형 빔포밍 알고리즘

### MVDR (Minimum Variance Distortionless Response)

MVDR 빔포머는 원하는 방향의 신호를 왜곡 없이 수신하면서 총 출력 전력을 최소화한다:

$$\min_{\mathbf{w}} \mathbf{w}^H \mathbf{R}_{xx} \mathbf{w} \quad \text{subject to} \quad \mathbf{w}^H \mathbf{a}(\theta_0) = 1$$

최적 가중치는 다음과 같다:

$$\mathbf{w}_{MVDR} = \frac{\mathbf{R}_{xx}^{-1} \mathbf{a}(\theta_0)}{\mathbf{a}^H(\theta_0) \mathbf{R}_{xx}^{-1} \mathbf{a}(\theta_0)}$$

여기서 $\mathbf{R}_{xx} = E[\mathbf{x}(t)\mathbf{x}^H(t)]$는 수신 신호의 공분산 행렬이다.

### LMS 적응형 알고리즘

실시간 구현에 적합한 Least Mean Squares(LMS) 알고리즘은 가중치를 반복적으로 갱신한다:

$$\mathbf{w}(n+1) = \mathbf{w}(n) + \mu \cdot e^*(n) \cdot \mathbf{x}(n)$$

- $\mu$: 스텝 크기 (수렴 속도와 안정성의 트레이드오프)
- $e(n) = d(n) - \mathbf{w}^H(n)\mathbf{x}(n)$: 오차 신호

LMS 알고리즘의 수렴 조건은 $0 < \mu < \frac{2}{\lambda_{max}}$이며, $\lambda_{max}$는 $\mathbf{R}_{xx}$의 최대 고유값이다.

## FPGA 구현 전략

### 아키텍처 설계

FPGA 기반 DBF 시스템의 전체 아키텍처는 다음과 같은 파이프라인 구조로 설계한다:

```
ADC → DDC → Buffer → Weight Multiply → Σ → Output
                          ↑
                    Weight Calculator
                          ↑
                    Calibration Engine
```

각 스테이지의 처리 지연을 최소화하기 위해 완전 파이프라인(fully pipelined) 구조를 채택한다.

### 고정소수점 설계

FPGA에서는 부동소수점 대신 고정소수점 연산을 사용하여 리소스를 절약한다. 각 신호의 비트폭 할당은 다음과 같다:

| 신호 | 비트폭 | 정수부 | 소수부 | 비고 |
|------|--------|--------|--------|------|
| ADC 출력 | 14 bit | 2 | 12 | 14-bit ADC 사용 |
| DDC 출력 (I/Q) | 18 bit | 2 | 16 | CIC + FIR 후 |
| 가중치 | 18 bit | 2 | 16 | sin/cos LUT |
| 곱셈 결과 | 36 bit | 4 | 32 | 18×18 곱셈기 |
| 누적 결과 | 40 bit | 8 | 32 | 16채널 누적 |

### 코드 예시: 빔포밍 코어

```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity beamformer_core is
    generic (
        NUM_CHANNELS : integer := 16;
        DATA_WIDTH   : integer := 18;
        WEIGHT_WIDTH : integer := 18
    );
    port (
        clk       : in  std_logic;
        rst       : in  std_logic;
        data_in   : in  signed(DATA_WIDTH-1 downto 0);
        weight_in : in  signed(WEIGHT_WIDTH-1 downto 0);
        ch_valid  : in  std_logic;
        beam_out  : out signed(DATA_WIDTH+WEIGHT_WIDTH+3 downto 0);
        beam_valid: out std_logic
    );
end entity;

architecture rtl of beamformer_core is
    signal mult_result : signed(DATA_WIDTH+WEIGHT_WIDTH-1 downto 0);
    signal accumulator : signed(DATA_WIDTH+WEIGHT_WIDTH+3 downto 0);
    signal ch_count    : unsigned(3 downto 0);
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if rst = '1' then
                accumulator <= (others => '0');
                ch_count    <= (others => '0');
                beam_valid  <= '0';
            elsif ch_valid = '1' then
                mult_result <= data_in * weight_in;
                if ch_count = 0 then
                    accumulator <= resize(mult_result, accumulator'length);
                else
                    accumulator <= accumulator + resize(mult_result, accumulator'length);
                end if;

                if ch_count = NUM_CHANNELS - 1 then
                    beam_out   <= accumulator + resize(mult_result, accumulator'length);
                    beam_valid <= '1';
                    ch_count   <= (others => '0');
                else
                    beam_valid <= '0';
                    ch_count   <= ch_count + 1;
                end if;
            else
                beam_valid <= '0';
            end if;
        end if;
    end process;
end architecture;
```

### 리소스 사용량 분석

Xilinx Kintex UltraScale+ KU15P 기준, 16채널 DBF 시스템의 예상 리소스 사용량은 다음과 같다:

| 리소스 | 사용량 | 가용량 | 사용률 |
|--------|--------|--------|--------|
| LUT | 45,200 | 522,720 | 8.6% |
| FF | 62,100 | 1,045,440 | 5.9% |
| DSP48E2 | 128 | 1,968 | 6.5% |
| BRAM (36Kb) | 96 | 984 | 9.8% |
| URAM | 16 | 128 | 12.5% |

## 캘리브레이션

### 채널 간 불균형 보정

실제 하드웨어에서는 각 수신 채널의 이득과 위상이 정확히 일치하지 않는다. 이를 보정하기 위해 캘리브레이션 벡터 $\mathbf{c}$를 도입한다:

$$\mathbf{w}_{cal} = \mathbf{w} \odot \mathbf{c}$$

캘리브레이션 벡터의 각 원소는 $c_k = g_k \cdot e^{j\phi_k}$이며, 여기서 $g_k$와 $\phi_k$는 각각 $k$번째 채널의 이득 보정 계수와 위상 보정 값이다.

### 상호 결합 보상

안테나 소자 간 상호 결합(mutual coupling)은 빔 패턴 왜곡의 주요 원인이다. 상호 결합 행렬 $\mathbf{C}$를 측정하여 다음과 같이 보상한다:

$$\mathbf{x}_{comp}(t) = \mathbf{C}^{-1} \mathbf{x}(t)$$

## 성능 평가

### 시뮬레이션 조건

- 배열 구성: 16소자 ULA ($d = \lambda/2$)
- 신호 대 잡음비(SNR): 20 dB
- 간섭 방향: $\theta_{int} = 30°$, INR = 40 dB
- 원하는 신호 방향: $\theta_0 = 0°$

### 결과 요약

MVDR 빔포머는 CBF 대비 간섭 방향에서 약 45 dB의 추가 억제를 달성했으며, 고정소수점 구현(18-bit)에서의 성능 열화는 0.3 dB 이내로 확인되었다. LMS 알고리즘은 약 500회 반복 후 수렴하며, FPGA 클럭 200 MHz 기준 실시간 처리가 가능하다.

## 결론

본 문서에서는 디지털 빔포밍의 기본 원리부터 FPGA 구현 전략까지를 포괄적으로 다루었다. 고정소수점 설계와 파이프라인 아키텍처를 통해 실시간 처리 요구 사항을 만족시킬 수 있으며, 캘리브레이션 기법을 적용하여 실제 하드웨어에서의 빔 패턴 성능을 보장할 수 있다.

향후 과제로는 2D 평면 배열로의 확장, 광대역 빔포밍, 그리고 딥러닝 기반 적응형 빔포밍 알고리즘의 FPGA 구현이 있다.

## References

[^1]: [Van Trees, H.L. "Optimum Array Processing"](https://doi.org/10.1002/0471221104) - 배열 신호 처리의 표준 참고서적.
[^2]: [Xilinx UltraScale+ FPGA Product Tables](https://www.xilinx.com/products/silicon-devices/fpga/kintex-ultrascale-plus.html) - Kintex UltraScale+ FPGA 사양.
[^3]: [Haykin, S. "Adaptive Filter Theory"](https://www.pearson.com/en-us/subject-catalog/p/adaptive-filter-theory/P200000003259) - 적응형 필터 이론의 교과서.
