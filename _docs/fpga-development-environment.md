---
title: "FPGA 개발 환경 구축 가이드"
description: "Xilinx Vivado 기반 FPGA 개발 환경 설정부터 합성, 시뮬레이션, 디버깅까지의 워크플로우를 정리한다."
author: "kiwanPark"
date: 2026-02-28
doc_category: "기술 가이드"
tags: ["FPGA", "Vivado", "VHDL", "개발환경"]
version: "1.0"
github_path: "_docs/fpga-development-environment.md"
revisions:
  - version: "1.0"
    date: "2026-02-28"
    summary: "초기 문서 작성"
    changes:
      - type: added
        description: "전체 가이드 초안 작성"
---

## 개요

FPGA(Field-Programmable Gate Array) 개발은 HDL(Hardware Description Language) 설계, 합성(Synthesis), 구현(Implementation), 시뮬레이션, 디버깅의 단계로 구성된다. 본 문서에서는 Xilinx Vivado Design Suite를 중심으로 개발 환경 구축과 기본 워크플로우를 정리한다.

## 개발 환경 설정

### Vivado 설치 요구 사항

| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| OS | Windows 10/11, Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| RAM | 16 GB | 32 GB 이상 |
| 디스크 | 100 GB (설치) | SSD 500 GB 이상 |
| CPU | 4코어 | 8코어 이상 (합성 속도) |
| 디스플레이 | 1920×1080 | 듀얼 모니터 권장 |

### Linux 환경 설정

Ubuntu에서 Vivado를 실행하기 위한 의존성 패키지를 설치한다:

```bash
sudo apt-get update
sudo apt-get install -y \
    libncurses5 \
    libncursesw5 \
    libtinfo5 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libfreetype6 \
    libfontconfig1 \
    locales \
    gcc \
    g++ \
    make
```

환경 변수 설정:

```bash
source /opt/Xilinx/Vivado/2024.1/settings64.sh
export XILINX_VIVADO=/opt/Xilinx/Vivado/2024.1
```

## 프로젝트 구조

권장 프로젝트 디렉토리 구조:

```
project_root/
├── src/
│   ├── hdl/          # VHDL/Verilog 소스
│   ├── ip/           # IP 코어
│   └── constraints/  # XDC 제약 조건 파일
├── sim/
│   ├── tb/           # 테스트벤치
│   └── scripts/      # 시뮬레이션 스크립트
├── docs/             # 설계 문서
├── scripts/
│   ├── tcl/          # Vivado TCL 스크립트
│   └── python/       # 유틸리티 스크립트
└── output/           # 빌드 결과물
```

### TCL 기반 비프로젝트 모드

GUI 없이 TCL 스크립트로 빌드를 자동화할 수 있다:

```tcl
# build.tcl
read_vhdl [glob src/hdl/*.vhd]
read_xdc  [glob src/constraints/*.xdc]

synth_design -top top_module -part xcu15p-fsvb2104-2-e
opt_design
place_design
route_design

write_bitstream -force output/top_module.bit
write_debug_probes -force output/top_module.ltx
```

실행:

```bash
vivado -mode batch -source scripts/tcl/build.tcl
```

## 시뮬레이션

### 테스트벤치 작성 패턴

```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity tb_beamformer is
end entity;

architecture sim of tb_beamformer is
    constant CLK_PERIOD : time := 5 ns;  -- 200 MHz
    signal clk   : std_logic := '0';
    signal rst   : std_logic := '1';
    signal done  : boolean   := false;
begin
    clk <= not clk after CLK_PERIOD/2 when not done;

    -- DUT 인스턴스
    uut: entity work.beamformer_core
        port map (
            clk       => clk,
            rst       => rst,
            data_in   => (others => '0'),
            weight_in => (others => '0'),
            ch_valid  => '0',
            beam_out  => open,
            beam_valid => open
        );

    -- 스티뮬러스 프로세스
    stim: process
    begin
        rst <= '1';
        wait for CLK_PERIOD * 10;
        rst <= '0';
        wait for CLK_PERIOD * 100;

        report "Simulation complete" severity note;
        done <= true;
        wait;
    end process;
end architecture;
```

### 파형 분석

Vivado 시뮬레이터 또는 GHDL + GTKWave 조합을 사용한다:

```bash
# GHDL 분석 및 시뮬레이션
ghdl -a --std=08 src/hdl/beamformer_core.vhd
ghdl -a --std=08 sim/tb/tb_beamformer.vhd
ghdl -e --std=08 tb_beamformer
ghdl -r --std=08 tb_beamformer --wave=sim/output/waveform.ghw

# GTKWave로 파형 확인
gtkwave sim/output/waveform.ghw
```

## 디버깅

### ILA (Integrated Logic Analyzer)

실시간 하드웨어 디버깅을 위해 ILA IP를 삽입한다. 관찰하려는 신호에 `MARK_DEBUG` 속성을 설정한다:

```vhdl
attribute MARK_DEBUG : string;
attribute MARK_DEBUG of accumulator : signal is "true";
attribute MARK_DEBUG of beam_valid  : signal is "true";
```

### VIO (Virtual Input/Output)

실시간으로 레지스터 값을 읽거나 쓸 수 있는 VIO IP를 활용한다. 캘리브레이션 계수나 빔 각도를 런타임에 변경할 때 유용하다.

## 버전 관리

FPGA 프로젝트에서 Git 사용 시 `.gitignore` 설정:

```
# Vivado 프로젝트 파일 (대부분 재생성 가능)
*.jou
*.log
*.str
*.runs/
*.cache/
*.hw/
*.ip_user_files/
*.sim/

# 빌드 결과물
output/*.bit
output/*.ltx

# 대용량 IP 코어는 별도 관리
!src/ip/*.xci
```

## 결론

FPGA 개발은 소프트웨어 개발과 달리 하드웨어 타이밍, 리소스 제약, 물리적 배치 등을 고려해야 한다. 체계적인 프로젝트 구조, TCL 기반 자동화, 그리고 적절한 디버깅 도구 활용이 생산성 향상의 핵심이다.
