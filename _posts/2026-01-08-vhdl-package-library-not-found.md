---
layout: post
title: "[오류] Package/Library not found"
date: 2026-01-08 10:00:00 +0900
author: rldhkstopic
category: dev
subcategory: "VHDL"
tags: [VHDL, Package, Library, Compile, Vivado]
views: 0
permalink: /dev/14/
---

VHDL 컴파일에서 사용자 정의 패키지나 라이브러리를 찾을 수 없다는 오류가 발생하는 경우가 있다. `package not found` 또는 `library not found` 오류는 패키지 파일이 컴파일되지 않았거나, 라이브러리 경로가 잘못 설정되었을 때 발생한다.

### 개요

- 증상: `package not found`, `library not found`, `unit not found`
- 주요 원인: 패키지 파일 미컴파일, 라이브러리 경로 오류, 컴파일 순서 문제
- 해결 방향: 패키지 파일 먼저 컴파일, 라이브러리 경로 확인, 컴파일 순서 조정

### 언제 발생하나

대표적인 상황은 다음과 같다.

- 사용자 정의 패키지를 `use` 했지만 패키지 파일이 컴파일되지 않음
- 패키지 파일이 프로젝트에 포함되지 않음
- Vivado에서 컴파일 순서가 잘못되어 패키지가 나중에 컴파일됨
- 라이브러리 이름이 일치하지 않음

### 재현 코드(패키지 미컴파일)

아래 코드는 `my_pkg` 패키지를 사용하지만, 패키지 파일이 컴파일되지 않아 오류가 발생한다.

```vhdl
-- my_pkg.vhd (패키지 파일)
library ieee;
use ieee.std_logic_1164.all;

package my_pkg is
  constant DATA_WIDTH : integer := 8;
  function parity(data : std_logic_vector) return std_logic;
end package my_pkg;

package body my_pkg is
  function parity(data : std_logic_vector) return std_logic is
    variable result : std_logic := '0';
  begin
    for i in data'range loop
      result := result xor data(i);
    end loop;
    return result;
  end function;
end package body;
```

```vhdl
-- main.vhd (패키지를 사용하는 파일)
library ieee;
use ieee.std_logic_1164.all;
use work.my_pkg.all; -- 패키지 사용

entity main is
  port (
    data : in  std_logic_vector(DATA_WIDTH-1 downto 0);
    par  : out std_logic
  );
end entity;

architecture rtl of main is
begin
  par <= parity(data);
end architecture;
```

만약 `my_pkg.vhd`가 프로젝트에 포함되지 않았거나 컴파일되지 않았다면 `package my_pkg is not found` 오류가 발생한다.

### 해결 원칙

#### 1) 패키지 파일을 프로젝트에 포함

Vivado나 다른 툴에서 패키지 파일을 프로젝트에 추가하고, 사용하는 파일보다 먼저 컴파일되도록 설정한다.

#### 2) 컴파일 순서 확인

패키지는 이를 사용하는 파일보다 먼저 컴파일되어야 한다. Vivado에서는 "Compile Order"를 확인하여 패키지 파일이 상위에 오도록 조정한다.

#### 3) 라이브러리 이름 확인

패키지가 `library work;`에 컴파일되면 `use work.package_name.all;`로 사용한다. 다른 라이브러리에 컴파일했다면 해당 라이브러리 이름을 사용해야 한다.

```vhdl
-- 패키지가 mylib 라이브러리에 컴파일된 경우
library mylib;
use mylib.my_pkg.all;
```

#### 4) 패키지 파일 경로 확인

패키지 파일이 프로젝트 디렉토리 외부에 있다면, 라이브러리 경로를 추가하거나 파일을 프로젝트로 복사해야 한다.

### 자주 헷갈리는 지점

`library` 선언과 `use` 선언은 다르다. `library work;`는 `work` 라이브러리를 사용하겠다는 선언이고, `use work.my_pkg.all;`은 해당 라이브러리의 패키지를 가져오는 것이다. 패키지가 컴파일되지 않으면 `use` 선언에서 오류가 발생한다.

### 유사 사례

패키지/라이브러리 찾기 실패는 컴파일 순서와 프로젝트 설정 문제로 자주 질문된다.[^1][^2][^3]

## References

[^1]: [VHDL package not found](https://stackoverflow.com/questions/tagged/vhdl+package)
[^2]: [How to use custom package in VHDL](https://stackoverflow.com/questions/18062059/vhdl-process-all-sensitivity-list)
[^3]: [VHDL library and package compilation order](https://stackoverflow.com/questions/46791502/object-is-used-but-not-declared)
