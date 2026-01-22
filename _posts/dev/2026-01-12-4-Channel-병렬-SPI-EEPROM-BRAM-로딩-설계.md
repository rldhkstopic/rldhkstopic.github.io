---
layout: post
title: "4-Channel 병렬 SPI EEPROM에서 BRAM 로딩 설계"
date: 2026-01-12 12:00:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [FPGA, EEPROM, BRAM, SPI, Parallel, VHDL, XC7A200T]
views: 0
---

4개의 EEPROM을 동시에 읽어 4개의 BRAM에 병렬로 로딩하는 설계를 정리한다. 기존의 순차 처리 방식과 달리 완전 병렬 처리 방식을 채택하여 로딩 시간을 1/4로 단축한다. RS232 트리거 인터페이스와 4-Channel SPI 로더, FSM 기반 제어 로직을 포함한다.

## 1. 전체 시스템 개요

### 1.1 설계 목표

- **병렬 처리**: 4개의 EEPROM을 동시에 읽어 4개의 BRAM에 병렬로 저장
- **로딩 시간 단축**: 순차 처리 대비 1/4 시간으로 단축
- **트리거 기반 시작**: RS232 UART를 통한 명령 수신으로 로딩 시작
- **완전 자동화**: FSM 기반 자동 제어로 최소한의 외부 개입

### 1.2 시스템 구성

```
[PC/메인 제어기] --UART--> [RS232 트리거 모듈] --LOAD_START_TG--> [Main FSM]
                                                                    |
                                                                    v
[EEPROM 1] --SPI--> [4-Channel SPI 로더] --DATA--> [BRAM 1]
[EEPROM 2] --SPI--> [4-Channel SPI 로더] --DATA--> [BRAM 2]
[EEPROM 3] --SPI--> [4-Channel SPI 로더] --DATA--> [BRAM 3]
[EEPROM 4] --SPI--> [4-Channel SPI 로더] --DATA--> [BRAM 4]
```

## 2. 상세 설계 (Detailed Design)

### 2.1 RS232 트리거 모듈 (Command Interface)

**기능**: PC 또는 메인 제어기로부터 로딩 시작 명령을 수신한다.

**프로토콜**: UART, 115200 bps (8-N-1)

**동작 로직**:
- Rx 라인을 통해 특정 커맨드 바이트(예: `0xA5` 또는 `0x55`) 수신 대기
- 정해진 커맨드가 수신되면 `LOAD_START_TG` 신호를 High로 1 Clock Cycle 펄스 발생
- 이 신호가 전체 로딩 FSM을 깨우는(Wake-up) 역할 수행

**VHDL 구현 예시**:

```vhdl
entity rs232_trigger is
  port (
    clk         : in  std_logic;
    rst         : in  std_logic;
    uart_rx     : in  std_logic;
    load_start  : out std_logic
  );
end entity;

architecture rtl of rs232_trigger is
  signal rx_data    : std_logic_vector(7 downto 0);
  signal rx_valid   : std_logic;
  signal cmd_match  : std_logic;
begin
  -- UART 수신 모듈 (예: Xilinx UART IP 또는 직접 구현)
  uart_rx_inst : entity work.uart_rx
    generic map (
      BAUD_RATE => 115200,
      CLK_FREQ  => 100_000_000
    )
    port map (
      clk      => clk,
      rst      => rst,
      rx       => uart_rx,
      data_out => rx_data,
      valid    => rx_valid
    );
  
  -- 커맨드 매칭 및 트리거 생성
  process(clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        load_start <= '0';
        cmd_match  <= '0';
      else
        load_start <= '0'; -- 기본값
        
        if rx_valid = '1' then
          if rx_data = x"A5" or rx_data = x"55" then
            cmd_match <= '1';
          else
            cmd_match <= '0';
          end if;
        end if;
        
        -- 1 Clock Cycle 펄스 생성
        if cmd_match = '1' and rx_valid = '1' then
          load_start <= '1';
        end if;
      end if;
    end if;
  end process;
end architecture;
```

### 2.2 4-Channel SPI 로더 (Parallel Loader)

4개의 EEPROM을 동시에 읽어 4개의 BRAM에 집어넣는 완전 병렬 처리 방식을 채택하여 로딩 시간을 1/4로 단축한다.

**EEPROM 동작 모드**: Sequential Read (명령어 `0x03` + 주소 `0x000000` 1회 전송 후 연속 데이터 수신)

**제어 신호**:
- `SPI_CS_N[3:0]`: 4개의 칩 셀렉트 (Active Low). 로딩 중 계속 0 유지
- `SPI_CLK`: 4개 EEPROM에 공통 공급 (예: 10MHz ~ 20MHz)
- `SPI_MOSI`: 4개 EEPROM에 공통 연결 (명령/주소 전송용)
- `SPI_MISO[3:0]`: 개별 연결. 4개의 EEPROM이 동시에 데이터를 뱉어냄

**VHDL 구현 예시**:

```vhdl
entity spi_4ch_loader is
  port (
    clk           : in  std_logic;
    rst           : in  std_logic;
    start         : in  std_logic;
    
    -- SPI 인터페이스
    spi_clk       : out std_logic;
    spi_mosi      : out std_logic;
    spi_cs_n      : out std_logic_vector(3 downto 0);
    spi_miso      : in  std_logic_vector(3 downto 0);
    
    -- BRAM 인터페이스
    bram_we       : out std_logic_vector(3 downto 0);
    bram_addr     : out std_logic_vector(18 downto 0);
    bram_din      : out std_logic_vector(31 downto 0); -- 4바이트 병렬
    
    -- 상태 신호
    load_done     : out std_logic;
    data_valid    : out std_logic
  );
end entity;

architecture rtl of spi_4ch_loader is
  type state_type is (IDLE, CMD_SEND, ADDR_SEND, DATA_LOAD, DONE);
  signal state      : state_type;
  signal bit_cnt    : integer range 0 to 31;
  signal byte_cnt   : integer range 0 to 2;
  signal addr_cnt   : unsigned(18 downto 0);
  signal spi_clk_en : std_logic;
  signal spi_clk_int: std_logic;
  
  constant CMD_READ  : std_logic_vector(7 downto 0) := x"03";
  constant ADDR_START: std_logic_vector(23 downto 0) := x"000000";
  constant MAX_ADDR  : unsigned(18 downto 0) := to_unsigned(524287, 19);
begin
  -- SPI 클럭 생성 (예: 10MHz)
  spi_clk_gen : process(clk)
    variable clk_div : integer range 0 to 4 := 0;
  begin
    if rising_edge(clk) then
      if rst = '1' or spi_clk_en = '0' then
        spi_clk_int <= '0';
        clk_div := 0;
      else
        if clk_div = 4 then
          spi_clk_int <= not spi_clk_int;
          clk_div := 0;
        else
          clk_div := clk_div + 1;
        end if;
      end if;
    end if;
  end process;
  
  spi_clk <= spi_clk_int;
  
  -- Main FSM
  process(clk)
  begin
    if rising_edge(clk) then
      if rst = '1' then
        state       <= IDLE;
        spi_cs_n    <= (others => '1');
        spi_mosi    <= '0';
        bram_we     <= (others => '0');
        bram_addr   <= (others => '0');
        bram_din    <= (others => '0');
        addr_cnt    <= (others => '0');
        bit_cnt     <= 0;
        byte_cnt    <= 0;
        spi_clk_en  <= '0';
        load_done   <= '0';
        data_valid  <= '0';
      else
        data_valid <= '0';
        
        case state is
          when IDLE =>
            if start = '1' then
              state      <= CMD_SEND;
              spi_cs_n   <= (others => '0');
              spi_clk_en <= '1';
              bit_cnt    <= 7;
              byte_cnt   <= 0;
            end if;
            
          when CMD_SEND =>
            -- Read Command (0x03) 전송
            if falling_edge(spi_clk_int) then
              spi_mosi <= CMD_READ(bit_cnt);
              if bit_cnt = 0 then
                state    <= ADDR_SEND;
                bit_cnt  <= 23;
              else
                bit_cnt <= bit_cnt - 1;
              end if;
            end if;
            
          when ADDR_SEND =>
            -- Start Address (0x000000) 24-bit 전송
            if falling_edge(spi_clk_int) then
              spi_mosi <= ADDR_START(bit_cnt);
              if bit_cnt = 0 then
                state    <= DATA_LOAD;
                bit_cnt  <= 7;
              else
                bit_cnt <= bit_cnt - 1;
              end if;
            end if;
            
          when DATA_LOAD =>
            -- 연속 데이터 수신
            if falling_edge(spi_clk_int) then
              -- 4개의 MISO에서 동시에 데이터 수신
              bram_din(7 downto 0)   <= spi_miso(0) & bram_din(6 downto 0);
              bram_din(15 downto 8)  <= spi_miso(1) & bram_din(14 downto 8);
              bram_din(23 downto 16) <= spi_miso(2) & bram_din(22 downto 16);
              bram_din(31 downto 24) <= spi_miso(3) & bram_din(30 downto 24);
              
              if bit_cnt = 0 then
                -- 1바이트 수신 완료
                bram_we     <= "1111";
                bram_addr   <= std_logic_vector(addr_cnt);
                data_valid  <= '1';
                addr_cnt    <= addr_cnt + 1;
                bit_cnt     <= 7;
                
                if addr_cnt = MAX_ADDR then
                  state     <= DONE;
                  spi_cs_n  <= (others => '1');
                  spi_clk_en <= '0';
                end if;
              else
                bit_cnt <= bit_cnt - 1;
              end if;
            end if;
            
          when DONE =>
            load_done <= '1';
            if start = '0' then
              state <= IDLE;
            end if;
        end case;
      end if;
    end if;
  end process;
end architecture;
```

### 2.3 BRAM 구성 (Internal Memory)

**구조**: 독립된 4개의 Block RAM (True Dual Port 또는 Simple Dual Port)

**크기**: EEPROM 용량(4Mb)에 1:1 대응
- **Depth**: 524,288 ($2^{19}$)
- **Width**: 8-bit (EEPROM Raw Data) 또는 16-bit (2바이트 병합 시)

**참고**: 16-bit로 저장할 경우 Depth는 절반($2^{18}$)이 됨

**VHDL BRAM 인스턴스 예시**:

```vhdl
-- BRAM 1
bram_inst_1 : entity work.bram_simple_dual_port
  generic map (
    DATA_WIDTH => 8,
    ADDR_WIDTH => 19
  )
  port map (
    clk     => clk,
    we      => bram_we(0),
    addr_wr => bram_addr,
    addr_rd => read_addr,
    din     => bram_din(7 downto 0),
    dout    => bram_dout(7 downto 0)
  );

-- BRAM 2, 3, 4도 동일한 방식으로 인스턴스화
```

## 3. FSM 및 데이터 흐름 (Logic Flow)

전체 시스템을 제어하는 Main FSM의 상태 천이도이다.

### State 1: IDLE (대기)

**동작**: `LOAD_START_TG` (RS232 트리거) 신호 감시

**초기화**:
- BRAM Write Enable (`we`) = 0 (비활성)
- BRAM Address Counter (`addr_cnt`) = 0
- SPI CS = 1 (High)

### State 2: CMD_SEND (명령 전송)

**트리거 발생 시 진입**

**동작**:
- `SPI_CS_N[3:0]`를 모두 0으로 내림
- `SPI_MOSI`를 통해 Read Command (`0x03`) 전송 (8 clock)
- 이어서 Start Address (`0x000000`) 24-bit 전송 (24 clock)
- 이 과정은 4개 EEPROM에 동시에 적용됨

### State 3: DATA_LOAD (연속 로딩)

**동작**: 더 이상 주소를 보내지 않고 `SPI_CLK`만 지속적으로 공급

**데이터 획득 및 저장 (Pipeline)**:

1. **Read**: 매 8 Clock마다 4개의 MISO 핀에서 데이터 바이트(D1, D2, D3, D4)가 동시에 도착
2. **Valid Check**: SPI 모듈에서 `data_valid` 펄스 발생
3. **Write BRAM**: `data_valid`가 1일 때:
   - `bram_we[3:0] <= "1111"` (모든 BRAM 쓰기 활성화)
   - `bram_addr <= addr_cnt` (현재 카운터 값을 주소로)
   - `bram_din1 <= D1, bram_din2 <= D2 ...` (각 데이터 매핑)
4. **Counter Update**: 쓰기 수행 직후 `addr_cnt <= addr_cnt + 1`

**종료 조건**: `addr_cnt`가 EEPROM 끝 주소(524,287)에 도달하면 CS를 올리고 DONE 상태로 이동

### State 4: DONE (완료)

**동작**: 로딩 완료 신호(`load_done`) 출력 (LED 점등 등)

**복귀**: 리셋 신호나 재시작 명령 전까지 대기

## 4. 핀 맵핑 계획 (Pin Planning Strategy)

XC7A200T FPGA 핀 할당 시 고려사항이다.

### RS232

- `UART_RX`: 입력 핀 (필수)
- `UART_TX`: 디버깅용 (선택)

### SPI Interface (총 7핀 + @)

- `SPI_CLK` (Output): 1개 (4개 칩 공통)
- `SPI_MOSI` (Output): 1개 (4개 칩 공통)
- `SPI_CS_N` (Output): 4개 (개별 제어 권장, 혹은 동시 제어 시 1개로 묶음 가능)
- `SPI_MISO` (Input): 4개 (필수). 병렬 로딩을 위해 반드시 개별 핀 할당
  - `MISO_1` -> BRAM 1
  - `MISO_2` -> BRAM 2
  - `MISO_3` -> BRAM 3
  - `MISO_4` -> BRAM 4

### 핀 할당 제약 (XDC 예시)

```tcl
# UART
set_property PACKAGE_PIN Y23 [get_ports uart_rx]
set_property IOSTANDARD LVCMOS33 [get_ports uart_rx]

# SPI 공통 신호
set_property PACKAGE_PIN AB22 [get_ports spi_clk]
set_property PACKAGE_PIN AC22 [get_ports spi_mosi]
set_property IOSTANDARD LVCMOS33 [get_ports {spi_clk spi_mosi}]

# SPI CS (개별 제어)
set_property PACKAGE_PIN AD22 [get_ports {spi_cs_n[0]}]
set_property PACKAGE_PIN AE22 [get_ports {spi_cs_n[1]}]
set_property PACKAGE_PIN AF22 [get_ports {spi_cs_n[2]}]
set_property PACKAGE_PIN AG22 [get_ports {spi_cs_n[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {spi_cs_n[*]}]

# SPI MISO (개별 입력, 병렬 처리 필수)
set_property PACKAGE_PIN AH22 [get_ports {spi_miso[0]}]
set_property PACKAGE_PIN AJ22 [get_ports {spi_miso[1]}]
set_property PACKAGE_PIN AK22 [get_ports {spi_miso[2]}]
set_property PACKAGE_PIN AL22 [get_ports {spi_miso[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {spi_miso[*]}]
```

## 5. 타이밍 고려사항

### 5.1 SPI 클럭 속도

- **권장 범위**: 10MHz ~ 20MHz
- **EEPROM 사양 확인**: 최대 SPI 클럭 속도 확인 필요
- **설정 시간(Setup Time)**: MISO 데이터의 유효 시간 보장

### 5.2 BRAM 쓰기 타이밍

- **파이프라인 구조**: SPI 데이터 수신과 BRAM 쓰기를 파이프라인으로 처리
- **주소 카운터**: BRAM 쓰기 직후 주소 증가
- **동기화**: 모든 BRAM에 동시에 쓰기 수행

### 5.3 전체 로딩 시간 계산

**가정**:
- EEPROM 용량: 4Mb = 524,288 바이트
- SPI 클럭: 10MHz
- 명령/주소 전송: 32 clock (8 + 24)
- 데이터 전송: 524,288 × 8 clock = 4,194,304 clock

**총 시간**:
- 순차 처리: (32 + 4,194,304) × 4 × 100ns ≈ 1.68초
- 병렬 처리: (32 + 4,194,304) × 100ns ≈ 0.42초

**단축 효과**: 약 1/4 시간으로 단축

## 6. 디버깅 및 검증

### 6.1 시뮬레이션 체크리스트

- RS232 트리거 신호 수신 확인
- SPI 명령/주소 전송 시퀀스 검증
- 4개 채널 동시 데이터 수신 확인
- BRAM 쓰기 주소 및 데이터 검증
- 종료 조건 및 완료 신호 확인

### 6.2 하드웨어 디버깅

- **ILA (Integrated Logic Analyzer)**: SPI 신호 및 FSM 상태 모니터링
- **UART 출력**: 로딩 진행 상태 및 에러 메시지 출력
- **LED 표시**: 각 상태별 LED 점등으로 시각적 확인

## 7. 결론

4-Channel 병렬 SPI EEPROM에서 BRAM 로딩 설계는 순차 처리 방식 대비 로딩 시간을 1/4로 단축할 수 있다. RS232 트리거 인터페이스와 FSM 기반 자동 제어를 통해 최소한의 외부 개입으로 완전 자동화된 로딩 프로세스를 구현할 수 있다. 핵심은 4개의 MISO 신호를 개별 핀으로 할당하여 진정한 병렬 처리를 보장하는 것이다.
