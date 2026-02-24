# Day 5 NotebookLM 데이터 (세션 086-106)
> Source: NotebookLM notebook/28d70970-864a-485b-82e9-ebdd7c233c9a
> Collected: 2026-02-25
> Query: Day 5 핵심 교육 콘텐츠 (클래스/인스턴스, __init__, @dataclass, 캡슐화, 상속, 다형성, DI, 파일/DB 저장, 진화 총정리, AI 시대의 서사)

---

## 1. 클래스와 인스턴스 (Classes and Instances)

### 정의
클래스는 객체를 만들기 위한 '설계 도면' 또는 템플릿이며, 인스턴스는 이 도면을 바탕으로 만들어진 '실제 생산품(객체)'[1]

### 핵심 개념
- 붕어빵 틀(클래스)과 붕어빵(인스턴스)으로 비유
- 붕어빵 틀 하나로 철수, 영희 등 여러 명의 학생(인스턴스) 객체를 찍어낼 수 있으며, 하나의 클래스로 만들어진 인스턴스들은 각자 독립적인 데이터 공간을 가짐[2]

### 실습 예시
```python
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade

s1 = Student("철수", "A")
s2 = Student("영희", "B")
# s1과 s2는 각각 독립적인 데이터 공간
```

---

## 2. 속성과 메서드, 그리고 __init__

### 정의
속성(Attribute)은 객체가 가진 데이터(상태)이며, 메서드(Method)는 객체가 수행하는 기능(동작). `__init__`은 인스턴스가 생성될 때 자동으로 호출되는 '매직 메서드(생성자)'[3][4]

### 핵심 개념
- 메서드 안의 `self`는 생성된 인스턴스 객체 자신을 가리킴
- `self.name`과 같이 선언된 인스턴스 변수는 다른 인스턴스와 메모리를 공유하지 않는 고유한 영역[4]

### 실습 예시
```python
class Customer:
    def __init__(self, name, phone):
        self.name = name    # 속성
        self.phone = phone  # 속성
    
    def display(self):      # 메서드
        print(f"{self.name}: {self.phone}")
```

---

## 3. @dataclass 데코레이터

### 정의
파이썬 3.7부터 도입된 기능으로, 데이터를 저장하고 처리하기 위한 클래스를 효율적으로 생성하게 해주는 장식자[5]

### 핵심 개념
- `__init__`, `__repr__`, `__eq__`와 같은 반복적인 보일러플레이트 코드(매직 메서드)를 자동으로 생성하여 코드가 매우 간결해짐
- 딕셔너리의 유연함에서 오는 오타 실수를 방지하고 구조를 명확히 할 수 있음[6][7]

### 실습 예시
```python
from dataclasses import dataclass

@dataclass
class Customer:
    name: str
    phone: str
    email: str = ""  # 기본값

c = Customer("홍길동", "010-1234-5678")
print(c)  # Customer(name='홍길동', phone='010-1234-5678', email='')
```

---

## 4. 객체지향 리팩토링과 캡슐화 (Encapsulation)

### 정의
코드를 객체 중심으로 재설계하는 과정. 캡슐화는 객체의 내부 구조를 숨기고, 외부에는 필요한 인터페이스(메서드)만 공개하는 객체지향의 핵심 원칙[8]

### 핵심 개념
- 자동차 엔진의 원리를 몰라도 핸들과 페달로 운전할 수 있는 것과 같음
- 속성 이름 앞에 두 개의 언더스코어(`__`)를 붙여 비공개 속성으로 만들고, `@property` 데코레이터를 사용하여 안전하게 값에 접근하거나 제한(예: 음수 입력 방지)[8]

### 실습 예시
```python
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # 비공개
    
    @property
    def balance(self):
        return self.__balance
    
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
```

---

## 5. 상속과 super (Inheritance)

### 정의
기존 클래스(부모)의 특성과 기능을 새로운 클래스(자식)가 물려받아 재사용하고 확장하는 기능[8][11]

### 핵심 개념
- 부모의 기능을 그대로 쓰면서 자식만의 고유한 기능을 덧붙일 수 있음
- `super()` 함수를 사용하면 자식 클래스에서 부모 클래스의 메서드(예: `__init__`)를 호출하여 기존 로직을 확장 가능[12]

### 실습 예시
```python
class Customer:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

class VIPCustomer(Customer):
    def __init__(self, name, phone, discount_rate):
        super().__init__(name, phone)  # 부모 호출
        self.discount_rate = discount_rate
```

---

## 6. 다형성 (Polymorphism)

### 정의
"같은 명령, 다른 결과"를 의미. 동일한 메서드를 호출해도 객체의 타입에 따라 다르게 동작하는 성질[13]

### 핵심 개념
- 부모 클래스에서 상속받은 메서드를 자식 클래스에서 필요에 맞게 재정의(메서드 오버라이딩)하여 구현
- TV 리모컨의 전원 버튼이 TV와 에어컨에서 각각 다른 결과를 내는 것과 같음[13][14]

### 실습 예시
```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "멍멍!"

class Cat(Animal):
    def speak(self):
        return "야옹!"

# 같은 메서드, 다른 결과
for animal in [Dog(), Cat()]:
    print(animal.speak())
```

---

## 7. 의존성 주입 (Dependency Injection, DI)

### 정의
객체가 내부에서 사용할 의존성(예: 저장소 객체)을 직접 생성하지 않고, 외부에서 생성자를 통해 주입받는 디자인 패턴[15][16]

### 핵심 개념
- 메인 프로그램(Manager)이 데이터를 어디에 저장할지 구체적인 방식(파일 vs DB)에 얽매이지 않게 결합도를 낮춤
- 테스트와 유지보수가 훨씬 쉬워짐

### 실습 예시
```python
class CustomerManager:
    def __init__(self, storage):  # 외부에서 주입
        self.storage = storage
    
    def save(self, customer):
        self.storage.save(customer)

# 사용 시 부품 교체
manager = CustomerManager(JsonStorage())   # 파일 저장
manager = CustomerManager(SqliteStorage()) # DB 저장
```

---

## 8. 파일/DB 저장 모듈 구현

### 정의
프로그램 종료 시 휘발성 메모리의 데이터가 사라지는 한계를 극복하기 위해 물리적 파일이나 데이터베이스에 영구 저장하는 기능

### 핵심 개념
- Python의 `json` 내장 라이브러리를 활용해 리스트/딕셔너리를 텍스트 파일로 저장(`dump`)[17]
- 대용량 데이터 처리를 위해 `sqlite3`를 사용하여 SQL 쿼리로 DB에 데이터를 저장[18]

### 실습 예시
```python
# 파일 저장
import json
json.dump(data, open("customers.json", "w"))

# DB 저장
import sqlite3
conn = sqlite3.connect("customers.db")
cursor = conn.cursor()
cursor.execute("INSERT INTO customers VALUES (?, ?)", (name, phone))
```

---

## 9. DI 적용 저장소 교체

### 정의
의존성 주입(DI) 아키텍처를 활용하여 비즈니스 로직(CustomerManager) 코드를 단 한 줄도 수정하지 않고 데이터 저장 방식을 교체하는 과정

### 핵심 개념
- 파일 저장 클래스(JsonStorage)와 DB 저장 클래스(SqliteStorage)가 동일한 인터페이스(예: `save()`, `load()`) 약속을 지키기만 하면, 부품을 갈아 끼우듯 쉽게 전환이 가능

### 실습 예시
```python
# 인터페이스 약속
class JsonStorage:
    def save(self, data): ...
    def load(self): ...

class SqliteStorage:
    def save(self, data): ...
    def load(self): ...

# 교체 테스트 — Manager 코드 변경 없음
manager1 = CustomerManager(JsonStorage())
manager2 = CustomerManager(SqliteStorage())
```

---

## 10. 프로그램 진화 총정리 (Total Evolution)

### 정의
1일차부터 5일차까지 고객 정보 관리 프로그램이 패러다임에 따라 어떻게 진화했는지 요약[19]

### 핵심 개념
- **v1. 절차적 (Day 1)**: 변수들이 흩어져 있고 하나의 거대한 while 루프 안에서 덩어리져 돌아감[20][21]
- **v2. 구조적 (Day 3)**: 반복되는 로직을 '함수'로 묶고, 데이터를 리스트와 딕셔너리로 묶음 (`[{"name":...}]`)[21]
- **v3. 객체지향 (Day 5)**: 데이터와 기능을 Customer 클래스로 모델링하여 현실 세계와 가깝게 설계[2]
- **v4. 아키텍처 (Day 5 심화)**: DI 패턴을 통해 비즈니스 로직과 데이터 영속성(파일/DB) 계층을 분리[22][23]

---

## 11. AI 시대의 서사 최종 연결

### 정의
5일간의 교육을 관통하는 "코드를 타이핑하는 사람에서, 문제를 정의하고 설계하는 아키텍트로"라는 메시지의 최종 완성[24][25]

### 핵심 개념
- 과거의 경쟁력이 '얼마나 빨리 코드를 치느냐(How)'였다면, 이제는 **"무엇을(What) 만들지 명확히 정의하는 능력"**[26][27]
- 5일간 스펙을 분석하고 테스트 시나리오를 짰던 이유는 AI(하급 실행자)에게 명확한 '설계도(명세)'를 지시하고, 그들이 가져온 코드를 비판적으로 리뷰(품질 검증)하기 위함
- "말이 되어야 프로그램이 된다"는 명세 주도 개발(SDD)의 가치를 현업에 돌아가 적용[28][29]

### 강사 스크립트 포인트
"앞으로는 구글링해서 복사-붙여넣기 하거나 문법을 통째로 외우는 대신, PRD나 명세서를 꼼꼼히 작성한 뒤 AI 에이전트(Antigravity, codex 등)를 지휘하는 오케스트라 지휘자가 될 것입니다."[30]
