# Day 5 심층 연구 자료: OOP와 소프트웨어 아키텍처 (Python 3.12+)
*Sessions: 086-106 | 객체지향 프로그래밍 ~ 수료*

---

## 1. OOP for Absolute Beginners: 클래스와 인스턴스

### 1.1 핵심 개념

| 용어 | 정의 | 비유 |
|------|------|------|
| 클래스 (Class) | 객체를 만드는 설계도/틀 | 붕어빵 틀 🐟 |
| 인스턴스 (Instance) | 클래스로 만들어진 실제 객체 | 붕어빵 한 개 |
| 속성 (Attribute) | 객체가 가진 데이터 | 붕어빵의 팥 종류, 크기 |
| 메서드 (Method) | 객체가 할 수 있는 행동 | 붕어빵을 먹는 행위 |
| `__init__` | 초기화 메서드 | 붕어빵 틀에 반죽 붓기 |
| `self` | 현재 인스턴스 자신 | "나 자신" |

### 1.2 절차적 vs OOP 비교

```python
# ❌ 절차적: 함수 + 딕셔너리
def create_customer(name, email, age):
    return {"name": name, "email": email, "age": age}

# ✅ OOP: 클래스 — 데이터와 행동이 하나로 묶임
class Customer:
    def __init__(self, name, email, age):
        self.name = name
        self.email = email
        self.age = age
    def introduce(self):
        return f"안녕하세요! 저는 {self.name}입니다."
```

---

## 2. Python @dataclass

### 2.1 일반 클래스 vs dataclass

```python
# ✅ dataclass: __init__, __repr__, __eq__ 자동 생성
from dataclasses import dataclass, field

@dataclass
class Customer:
    name: str
    email: str
    age: int
    points: int = 0
    purchase_history: list[str] = field(default_factory=list)
```

### 2.2 핵심 기능

- `field(default_factory=list)`: 리스트/딕셔너리 기본값
- `@dataclass(frozen=True)`: 불변 객체
- `__post_init__`: 초기화 후 검증

---

## 3. 캡슐화와 OOP 리팩토링

### 3.1 Python 접근 제어 관례

```python
self.name = name          # 공개 (public)
self._email = email       # 보호 (protected, 관례)
self.__age = age          # 비공개 (private, 이름 맹글링)
```

### 3.2 @property — Pythonic한 캡슐화

```python
@property
def age(self) -> int:
    return self._age

@age.setter
def age(self, value: int) -> None:
    if value < 0:
        raise ValueError("나이는 0 이상")
    self._age = value
```

### 3.3 고객관리 v2(함수) → v3(클래스) 진화

```python
# v3: 클래스 기반
@dataclass
class Customer:
    name: str
    email: str
    age: int
    points: int = 0

class CustomerManager:
    def __init__(self):
        self._customers: list[Customer] = []
    def add(self, name, email, age) -> Customer: ...
    def find(self, name) -> Customer | None: ...
    @property
    def count(self) -> int: ...
```

---

## 4. 상속과 다형성

### 4.1 상속

```python
@dataclass
class VIPCustomer(Customer):
    grade: str = "GOLD"
    
    def add_points(self, amount: int) -> None:
        super().add_points(amount * 2)  # 2배!
    
    def get_discount(self) -> float:
        return {"GOLD": 0.1, "PLATINUM": 0.2}.get(self.grade, 0.0)
```

### 4.2 다형성

```python
def process_customer(customer: Customer) -> None:
    """같은 함수로 다른 타입 처리"""
    customer.add_points(100)
    discount = customer.get_discount()
    print(f"{customer} | 할인율: {discount:.0%}")
```

### 4.3 Duck Typing

"오리처럼 걷고 오리처럼 꽥꽥거리면 오리다" — 상속 없이도 같은 메서드만 있으면 동작.

---

## 5. 의존성 주입 (DI)

### 5.1 핵심 개념

❌ 바리스타가 직접 원두를 재배 (의존성 직접 생성)
✅ 바리스타가 원두를 공급받아 사용 (의존성 주입)

### 5.2 Storage 인터페이스 패턴

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def save(self, customers: list[Customer]) -> None: ...
    @abstractmethod
    def load(self) -> list[Customer]: ...

class InMemoryStorage(Storage): ...   # 테스트용
class JsonFileStorage(Storage): ...   # JSON 파일
class SQLiteStorage(Storage): ...     # SQLite DB

# DI: 저장소를 외부에서 주입
class CustomerManager:
    def __init__(self, storage: Storage):
        self._storage = storage
```

### 5.3 DI의 장점

- 테스트 용이성: 실제 파일/DB 없이 테스트
- 유연성: 저장소만 바꾸면 됨 (코드 변경 없음)
- 관심사 분리: 비즈니스 로직 ↔ 저장소 로직

---

## 6. 파일과 데이터베이스 저장

### 6.1 JSON 파일 저장

```python
import json
from dataclasses import asdict

# 저장: dataclass → dict → JSON
data = [asdict(c) for c in customers]
with open("customers.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 불러오기: JSON → dict → dataclass
with open("customers.json", "r", encoding="utf-8") as f:
    data = json.load(f)
customers = [Customer(**item) for item in data]
```

### 6.2 SQLite 기초

```python
import sqlite3

# 테이블 생성
conn.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER NOT NULL,
        points INTEGER DEFAULT 0
    )
""")

# INSERT
conn.execute("INSERT INTO customers (name, email, age) VALUES (?, ?, ?)",
             (name, email, age))

# SELECT
rows = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
```

---

## 7. 최종 프로젝트와 수료

### 7.1 고객관리 프로그램 진화 총정리

```
v1 (절차적) → v2 (구조적) → v3 (OOP) → v4 (DI + 저장소)
전역 변수      함수 분리      클래스화      인터페이스 분리
스파게티 코드  모듈화 시작    캡슐화 적용   테스트 가능
```

### 7.2 심화 학습 로드맵

```
📌 웹 개발: FastAPI, Django, Streamlit
📌 데이터 분석: pandas, matplotlib, Jupyter
📌 자동화: requests, BeautifulSoup, schedule
📌 AI/ML 통합: OpenAI API, LangChain, scikit-learn
```

---

## 세션별 배분 (86-106)

```
세션 86-88: Customer 클래스 기초 (붕어빵 틀)
세션 89-91: @dataclass로 리팩토링
세션 92-94: 캡슐화 + @property (v2→v3)
세션 95-97: VIPCustomer 상속 + 다형성
세션 98-100: DI 패턴 + Storage 인터페이스
세션 101-103: JSON/SQLite 저장소 구현
세션 104-106: 최종 프로젝트 + 코드 리뷰 + 수료
```

*리포트 작성: 2026-02-25*
