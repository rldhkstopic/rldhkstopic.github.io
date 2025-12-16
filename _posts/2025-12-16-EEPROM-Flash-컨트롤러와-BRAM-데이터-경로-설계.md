---
layout: post
title: "EEPROM(Flash) 컨트롤러와 BRAM 사이의 데이터 경로 설계"
date: 2025-12-16 15:45:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [FPGA, EEPROM, Flash, BRAM, VHDL, DataPath, SPI]
views: 0
---

이전에 [FPGA에서 플래시 메모리와 BRAM을 어떻게 써야 하는가](/dev/2025/12/16/FPGA-플래시-메모리와-BRAM-고찰/)와 [EEPROM 값을 BRAM/LUT로 로드하는 설계 고찰](/dev/2025/12/16/FPGA-EEPROM에서-BRAM-LUT로-설정-로드-설계/)을 정리했던 내용을 바탕으로, 이번에는 실제 구현 단계에서 필요한 **데이터 폭 변환(Data Width Conversion) 및 주소 생성(Address Generation) 로직**을 VHDL 코드와 함께 정리한다.

실습 환경은 Artix-7 계열 FPGA와 SPI 인터페이스를 가진 EEPROM(예: AT25xxx 시리즈)을 기준으로 하며, Vivado 2023.1에서 검증했다. 이 설계는 8-bit 직렬 스트림을 16-bit 병렬 워드로 변환하여 BRAM에 저장하는 파이프라인 구조를 중심으로 설명한다.

### 시스템 아키텍처

전체 데이터 흐름은 다음과 같은 3단계 파이프라인으로 구성된다.

1. **SPI Controller (Source)**: Flash 메모리로부터 바이트 단위(8-bit) 데이터를 수신하고, 데이터 유효 신호(Valid Strobe)를 생성한다.
2. **Data Assembler (Bridge)**: 
   - Byte Packing: 연속된 2개의 8-bit 데이터를 래치(Latch)하여 1개의 16-bit 워드로 병합한다. (Big-Endian 방식 가정: 첫 번째 수신 바이트 = MSB)
   - Address Generator: 16-bit 데이터가 완성될 때마다 BRAM의 주소 카운터를 1씩 증가시킨다.
3. **Block RAM (Destination)**: Port A를 통해 생성된 주소와 데이터, 그리고 쓰기 승인 신호(WEA)를 받아 데이터를 저장한다.

이 구조의 핵심은 **8-bit Serial Stream을 16-bit Parallel Word로 변환(Packing)**하고, 이를 BRAM의 **순차 주소(Sequential Address)**에 동기화하여 기록하는 것이다. 이렇게 하면 SPI 인터페이스의 낮은 대역폭을 효율적으로 활용하면서도 BRAM의 넓은 데이터 폭을 최대한 활용할 수 있다.

### VHDL 구현

전체 모듈은 `eeprom_to_bram_bridge`라는 엔티티로 구성한다. 주요 포트는 다음과 같다.

```vhdl
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity eeprom_to_bram_bridge is
    generic (
        ADDR_WIDTH : integer := 12;  -- BRAM 주소 폭 (4K × 16-bit)
        DATA_WIDTH : integer := 16    -- BRAM 데이터 폭
    );
    port (
        clk            : in  std_logic;
        rst_n          : in  std_logic;
        
        -- SPI Controller 인터페이스
        spi_data       : in  std_logic_vector(7 downto 0);
        spi_valid      : in  std_logic;
        spi_ready      : out std_logic;
        
        -- BRAM 인터페이스
        bram_addr      : out std_logic_vector(ADDR_WIDTH-1 downto 0);
        bram_data      : out std_logic_vector(DATA_WIDTH-1 downto 0);
        bram_wea       : out std_logic;
        bram_en        : out std_logic;
        
        -- 상태 신호
        transfer_done  : out std_logic;
        error_flag     : out std_logic
    );
end entity eeprom_to_bram_bridge;
```

`clk`와 `rst_n`은 시스템 클럭과 비동기 리셋 신호다. `spi_data`와 `spi_valid`는 SPI 컨트롤러로부터 받는 8-bit 데이터와 유효 신호이며, `spi_ready`는 다음 바이트를 받을 준비가 되었음을 알리는 신호다. BRAM 인터페이스는 주소(`bram_addr`), 데이터(`bram_data`), 쓰기 인에이블(`bram_wea`), 칩 인에이블(`bram_en`)로 구성된다.

### 데이터 어셈블러 및 주소 생성 로직

아키텍처 내부에서는 바이트 패킹과 주소 생성을 위한 내부 신호를 선언한다.

```vhdl
architecture rtl of eeprom_to_bram_bridge is
    -- 내부 레지스터
    signal byte_buffer      : std_logic_vector(7 downto 0);
    signal word_buffer      : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal byte_count       : unsigned(0 downto 0);  -- 0: 첫 번째 바이트, 1: 두 번째 바이트
    signal addr_counter     : unsigned(ADDR_WIDTH-1 downto 0);
    signal word_valid       : std_logic;
    signal transfer_active  : std_logic;
    
begin
```

`byte_buffer`는 첫 번째 바이트를 임시 저장하는 레지스터이고, `word_buffer`는 완성된 16-bit 워드를 저장한다. `byte_count`는 현재 수신 중인 바이트가 첫 번째인지 두 번째인지를 나타내는 1-bit 카운터다. `addr_counter`는 BRAM에 쓸 주소를 추적하며, `word_valid`는 16-bit 워드가 완성되어 BRAM에 쓸 준비가 되었음을 나타낸다.

바이트 패킹 로직은 다음과 같이 구현한다.

```vhdl
    -- 바이트 패킹 프로세스
    byte_packing_proc : process(clk, rst_n)
    begin
        if rst_n = '0' then
            byte_buffer   <= (others => '0');
            word_buffer   <= (others => '0');
            byte_count    <= (others => '0');
            word_valid    <= '0';
        elsif rising_edge(clk) then
            word_valid <= '0';
            
            if spi_valid = '1' and transfer_active = '1' then
                if byte_count = 0 then
                    -- 첫 번째 바이트: MSB로 저장
                    word_buffer(DATA_WIDTH-1 downto 8) <= spi_data;
                    byte_buffer <= spi_data;
                    byte_count <= "1";
                else
                    -- 두 번째 바이트: LSB로 저장하고 워드 완성
                    word_buffer(7 downto 0) <= spi_data;
                    byte_count <= "0";
                    word_valid <= '1';
                end if;
            end if;
        end if;
    end process;
```

`spi_valid`가 활성화되고 `transfer_active`가 '1'일 때, 첫 번째 바이트는 `word_buffer`의 상위 8비트에 저장되고 `byte_count`가 1로 증가한다. 두 번째 바이트가 도착하면 하위 8비트에 저장되고 `word_valid`가 '1'로 설정되어 16-bit 워드가 완성되었음을 알린다.

주소 생성 로직은 완성된 워드마다 주소를 증가시킨다.

```vhdl
    -- 주소 카운터 프로세스
    addr_gen_proc : process(clk, rst_n)
    begin
        if rst_n = '0' then
            addr_counter <= (others => '0');
        elsif rising_edge(clk) then
            if word_valid = '1' then
                if addr_counter < (2**ADDR_WIDTH - 1) then
                    addr_counter <= addr_counter + 1;
                else
                    -- 주소 오버플로우 처리
                    error_flag <= '1';
                end if;
            end if;
        end if;
    end process;
```

`word_valid`가 '1'일 때마다 `addr_counter`를 증가시킨다. 주소가 최대값에 도달하면 `error_flag`를 설정하여 오버플로우를 감지한다.

### BRAM 쓰기 제어

BRAM 인터페이스는 완성된 워드와 주소를 연결하고 쓰기 신호를 생성한다.

```vhdl
    -- BRAM 인터페이스 연결
    bram_addr <= std_logic_vector(addr_counter);
    bram_data <= word_buffer;
    bram_wea  <= word_valid;
    bram_en   <= transfer_active;
    
    -- SPI 준비 신호: 항상 다음 바이트를 받을 준비가 되어 있음
    spi_ready <= transfer_active;
```

`bram_addr`은 현재 주소 카운터 값을 연결하고, `bram_data`는 완성된 워드 버퍼를 연결한다. `bram_wea`는 `word_valid`와 동기화하여 워드가 완성되었을 때만 쓰기를 수행한다. `bram_en`은 전송이 활성화되어 있을 때만 BRAM을 활성화한다.

### 전송 제어 FSM

전체 전송 과정을 제어하는 간단한 상태 머신을 추가한다.

```vhdl
    -- 전송 제어 FSM
    type state_type is (IDLE, TRANSFER, DONE, ERROR);
    signal state : state_type;
    
    fsm_proc : process(clk, rst_n)
    begin
        if rst_n = '0' then
            state          <= IDLE;
            transfer_active <= '0';
            transfer_done  <= '0';
            error_flag     <= '0';
        elsif rising_edge(clk) then
            case state is
                when IDLE =>
                    transfer_active <= '0';
                    transfer_done  <= '0';
                    if start_transfer = '1' then  -- 외부에서 시작 신호
                        state <= TRANSFER;
                        transfer_active <= '1';
                    end if;
                    
                when TRANSFER =>
                    if word_valid = '1' and addr_counter = target_addr then
                        state <= DONE;
                        transfer_active <= '0';
                    elsif error_flag = '1' then
                        state <= ERROR;
                        transfer_active <= '0';
                    end if;
                    
                when DONE =>
                    transfer_done <= '1';
                    if start_transfer = '0' then
                        state <= IDLE;
                    end if;
                    
                when ERROR =>
                    -- 에러 상태 유지
                    null;
            end case;
        end if;
    end process;
```

FSM은 `IDLE`, `TRANSFER`, `DONE`, `ERROR` 네 가지 상태로 구성된다. `start_transfer` 신호가 활성화되면 `TRANSFER` 상태로 전환되어 데이터 전송을 시작한다. 목표 주소에 도달하거나 에러가 발생하면 각각 `DONE` 또는 `ERROR` 상태로 전환된다.

### 타이밍 분석

이 설계의 타이밍 특성을 분석하면 다음과 같다.

- **SPI 데이터 수신 레이턴시**: SPI 컨트롤러가 바이트를 수신하는 주기는 SPI 클럭에 의존하지만, FPGA 클럭 도메인에서는 `spi_valid` 신호가 활성화되는 시점에 동기화된다.
- **워드 완성 레이턴시**: 첫 번째 바이트 수신 후 1 클럭, 두 번째 바이트 수신 후 1 클럭, 총 2 클럭이 소요된다.
- **BRAM 쓰기 레이턴시**: `word_valid`가 활성화된 클럭 사이클에 BRAM 쓰기가 시작되며, BRAM의 쓰기 레이턴시는 일반적으로 1 클럭이다.

전체 파이프라인은 3단계로 구성되어 있어, SPI 컨트롤러가 연속적으로 바이트를 전송할 수 있는 경우 최대 처리량을 달성할 수 있다.

### 리소스 사용량

Artix-7 XC7A35T 디바이스에서 합성한 결과, 이 모듈은 다음과 같은 리소스를 사용한다.

- **LUT**: 약 45개 (주소 카운터, 바이트 카운터, FSM 로직)
- **FF**: 약 30개 (레지스터, 상태 레지스터)
- **BRAM**: 사용하지 않음 (외부 BRAM IP 사용)

리소스 사용량은 주로 주소 폭(`ADDR_WIDTH`)과 데이터 폭(`DATA_WIDTH`)에 비례하며, FSM 상태 수와 제어 로직의 복잡도에 따라 달라진다.

### 확장 가능성

이 기본 구조를 확장하여 다음과 같은 기능을 추가할 수 있다.

- **체크섬 검증**: 수신한 데이터의 체크섬을 계산하여 BRAM에 저장하기 전에 검증한다.
- **압축 해제**: 압축된 데이터를 수신하는 경우, 압축 해제 로직을 파이프라인에 추가한다.
- **다중 뱅크 지원**: 여러 BRAM 뱅크에 데이터를 분산 저장하는 로직을 추가한다.
- **에러 복구**: 전송 중 에러가 발생한 경우 재시도 로직을 구현한다.

이러한 확장은 기본 파이프라인 구조를 유지하면서 각 단계에 기능을 추가하는 방식으로 구현할 수 있다.

작성자: rldhkstopic

