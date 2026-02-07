---
layout: post
title: "⚠️ NullReferenceException: Object reference not set to an instance of an object"
date: 2026-01-10 22:00:00 +0900
author: rldhkstopic
category: dev
subcategory: "C#"
tags: [C#, .NET, NullReferenceException, 오류해결, null체크]
views: 0
permalink: /dev/18/
post_number: 9
---

C#에서 `NullReferenceException`은 가장 흔하게 발생하는 런타임 오류 중 하나다. 객체가 `null`인 상태에서 멤버에 접근하려 할 때 발생한다. 이 오류는 컴파일 타임에 감지되지 않아 런타임에 예기치 못한 크래시를 일으킬 수 있다.

### 개요

- 증상: `NullReferenceException: Object reference not set to an instance of an object`
- 주요 원인: `null`인 객체의 멤버(메서드, 속성, 필드)에 접근
- 해결 방향: null 체크, null 조건부 연산자(`?.`), null 병합 연산자(`??`) 활용

### 언제 발생하나

대표적인 상황은 다음과 같다.

- 초기화되지 않은 참조 변수에 접근
- 메서드가 `null`을 반환하는 경우를 처리하지 않음
- 컬렉션이나 배열이 `null`인 상태에서 요소 접근
- 이벤트 핸들러가 `null`인 상태에서 호출

### 재현 코드(오류 발생 패턴)

```csharp
class Program
{
    static void Main(string[] args)
    {
        Person person = null;
        
        // NullReferenceException 발생
        string name = person.Name; // person이 null이므로 오류
        int age = person.GetAge(); // 마찬가지로 오류
    }
}

class Person
{
    public string Name { get; set; }
    public int GetAge() => 25;
}
```

이 코드는 `person`이 `null`인 상태에서 `Name` 속성과 `GetAge()` 메서드에 접근하려 하므로 런타임에 예외가 발생한다.

### 해결 원칙

#### 1) null 체크를 명시적으로 수행한다

가장 기본적인 방법은 객체가 `null`인지 확인한 후 접근하는 것이다.

```csharp
Person person = GetPerson();

if (person != null)
{
    string name = person.Name;
    int age = person.GetAge();
}
```

#### 2) null 조건부 연산자(`?.`)를 활용한다

C# 6.0부터 도입된 null 조건부 연산자는 객체가 `null`이면 전체 표현식이 `null`을 반환한다.

```csharp
Person person = GetPerson();

// person이 null이면 name도 null이 됨
string name = person?.Name;

// 메서드 호출도 안전하게 처리
int? age = person?.GetAge();
```

#### 3) null 병합 연산자(`??`)로 기본값 제공한다

null 병합 연산자는 왼쪽 피연산자가 `null`이면 오른쪽 값을 반환한다.

```csharp
Person person = GetPerson();

// person이 null이면 "Unknown" 반환
string name = person?.Name ?? "Unknown";

// 숫자 타입에도 적용 가능
int age = person?.GetAge() ?? 0;
```

#### 4) null 병합 할당(`??=`)으로 초기화한다

C# 8.0부터 도입된 null 병합 할당 연산자는 변수가 `null`일 때만 값을 할당한다.

```csharp
Person person = GetPerson();
person ??= new Person { Name = "Default" };
```

### 유사 사례

#### 컬렉션 null 체크

```csharp
List<string> items = GetItems();

// 잘못된 방법: items가 null이면 오류
int count = items.Count;

// 올바른 방법
int count = items?.Count ?? 0;
```

#### 이벤트 핸들러 null 체크

```csharp
public event EventHandler SomethingHappened;

protected virtual void OnSomethingHappened()
{
    // 잘못된 방법
    SomethingHappened(this, EventArgs.Empty); // null이면 오류
    
    // 올바른 방법
    SomethingHappened?.Invoke(this, EventArgs.Empty);
}
```

#### 문자열 null 체크

```csharp
string text = GetText();

// 잘못된 방법
int length = text.Length; // text가 null이면 오류

// 올바른 방법
int length = text?.Length ?? 0;
```

### 추가 고려사항

#### nullable 참조 타입 (C# 8.0+)

C# 8.0부터 nullable 참조 타입을 활성화하면 컴파일 타임에 null 참조 경고를 받을 수 있다.

```csharp
#nullable enable

class Program
{
    static void Main(string[] args)
    {
        Person? person = GetPerson(); // ? 표시로 nullable 명시
        
        // 컴파일러가 null 체크를 요구함
        if (person != null)
        {
            string name = person.Name; // 안전
        }
    }
}
```

#### ArgumentNullException 사용

메서드 파라미터가 `null`인 경우 `NullReferenceException` 대신 `ArgumentNullException`을 던지는 것이 더 명확하다.

```csharp
public void ProcessPerson(Person person)
{
    if (person == null)
        throw new ArgumentNullException(nameof(person));
    
    // 처리 로직
}
```

## References

[^1]: [Microsoft Docs: NullReferenceException Class](https://learn.microsoft.com/en-us/dotnet/api/system.nullreferenceexception)
[^2]: [Microsoft Docs: Null-conditional operators ?. and ?[]](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/member-access-operators#null-conditional-operators--and-)
[^3]: [Microsoft Docs: Null-coalescing operator ??](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/null-coalescing-operator)
