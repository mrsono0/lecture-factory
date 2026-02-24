# 세션 089: 데이터를 담는 특별한 그릇, @dataclass

| 항목 | 값 |
|------|-----|
| **세션 ID** | MS-PY101-089 |
| **소요 시간** | 20분 |
| **난이도** | ★★☆ (medium) |
| **청크 타입** | code |
| **선행 세션** | 088 (필수) |
| **학습 목표** | 일반 클래스의 `__init__` 방식과 `@dataclass`를 비교하여, `@dataclass`가 데이터 중심 클래스 작성에 주는 이점을 설명할 수 있다 |
| **출처** | [Source A] 8 코딩.pdf §8.14 @dataclass 활용 · [Source B] day5_notebooklm.md · [Source C] day5_deep_research.md |

---

## ① 도입 — "타이핑이 너무 많지 않았나요?"

🗣️ 강사 대본 (Instructor Script):

여러분, 방금 전 실습에서 Customer 클래스를 직접 만들어 보셨죠? `def __init__(self, name, phone, email):` 적고, 그 아래에 `self.name = name`, `self.phone = phone`, `self.email = email`을 한 줄 한 줄 타이핑하셨을 겁니다. 속성이 세 개일 때는 그럭저럭 참을 만했는데, 만약 속성이 열 개라면 어떨까요? `self.`을 열 번 반복해서 치는 자신의 모습을 상상해 보세요. 손가락이 먼저 파업을 선언할 겁니다. 사실 파이썬을 만든 개발자들도 똑같은 불만을 가지고 있었어요. "데이터만 담을 건데, 이 반복 타이핑 좀 어떻게 안 되나?" 그래서 파이썬 3.7 버전에 아주 기특한 기능이 하나 추가되었습니다. 바로 `@dataclass`라는 마법의 모자입니다.

---

## ② 비유 — 수작업 포장 vs 반자동 포장 기계

🗣️ 강사 대본 (Instructor Script):

비유를 하나 들어 볼게요. 여러분이 택배 회사에서 일한다고 상상해 봅시다 [Source A]. 매일 수백 개의 상품을 포장해야 하는데, 지금까지의 방식은 이랬습니다. 빈 박스를 꺼내고(`class Customer:`), 박스를 접고(`def __init__(self, ...)`), 상품 이름표를 하나하나 손으로 붙이고(`self.name = name`), 가격표도 붙이고(`self.price = price`), 무게 라벨도 붙이고(`self.weight = weight`)... 상품 종류가 바뀔 때마다 이 과정을 처음부터 반복해야 합니다. 하루에 열 종류의 상품을 포장한다면, 라벨 붙이는 것만으로 오전이 다 갑니다.

그런데 어느 날, 사장님이 "반자동 포장 기계"를 들여놓았습니다 [Source B]. 이 기계는 놀랍게도 "이름: 문자열, 가격: 숫자, 무게: 숫자"라고 스펙 목록만 적어서 넣으면, 기계가 알아서 박스를 접고, 라벨을 전부 붙여주고, 심지어 내용물 비교 기능까지 자동으로 장착해 줍니다. 여러분은 스펙만 정의하면 되고, 나머지 반복 작업은 기계가 전부 처리하는 거예요.

프로그래밍에서 이 "반자동 포장 기계"가 바로 `@dataclass`입니다 [Source C]. 클래스 위에 `@dataclass`라는 모자를 씌워주면, 파이썬이 뒤에서 `__init__`도 만들어주고, `__repr__`(객체를 예쁘게 출력하는 기능)도 만들어주고, `__eq__`(두 객체가 같은지 비교하는 기능)까지 자동으로 생성해 줍니다. 여러분은 "이 클래스에 어떤 데이터가 들어가야 하는지" 목록만 적으면 됩니다.

이것은 AI 시대의 철학과도 정확히 맞닿아 있습니다. AI가 우리의 반복 작업을 줄여주듯이, 파이썬 언어 자체도 개발자의 단순 반복 타이핑, 이른바 보일러플레이트(Boilerplate) 코드를 줄이는 방향으로 꾸준히 진화해 왔습니다. "무엇을 담을지"만 결정하면 "어떻게 담을지"는 도구가 알아서 해주는 세상, 바로 지금 우리가 살고 있는 시대입니다.

---

## ③ 개념 설명 — @dataclass의 정체

🗣️ 강사 대본 (Instructor Script):

자, 그러면 `@dataclass`가 정확히 무엇인지 정리해 보겠습니다. `@dataclass`는 파이썬 3.7 버전부터 표준 라이브러리에 포함된 데코레이터(Decorator)입니다 [Source A][Source C]. 데코레이터란 클래스나 함수 위에 `@` 기호와 함께 붙여서, 원래의 코드에 추가 기능을 "장식(decorate)"해 주는 문법입니다. 케이크 위에 생크림을 올리듯, 클래스 위에 `@dataclass`를 올리면 여러 가지 편의 기능이 자동으로 추가됩니다.

구체적으로 `@dataclass`가 자동 생성해 주는 것은 세 가지입니다 [Source B]. 첫째, `__init__` 메서드 — 우리가 일일이 `self.name = name`을 적지 않아도 됩니다. 둘째, `__repr__` 메서드 — `print(customer1)`을 했을 때 `<__main__.Customer object at 0x...>` 같은 암호 대신 `Customer(name='홍길동', email='hong@mail.com', age=30)`처럼 읽기 좋은 형태로 출력됩니다. 셋째, `__eq__` 메서드 — 두 객체의 속성 값이 모두 같으면 `==` 비교 시 `True`를 반환합니다.

한 가지 주의할 점이 있습니다. `@dataclass`를 사용하려면 각 속성에 반드시 타입 힌트(Type Hint)를 적어야 합니다. `name: str`, `age: int`처럼요. 타입 힌트는 파이썬에게 "이 변수에는 이런 종류의 데이터가 들어올 거야"라고 알려주는 표지판 같은 것입니다. `@dataclass`는 이 표지판을 읽고 자동으로 `__init__`의 매개변수를 구성하기 때문에, 타입 힌트가 없으면 동작하지 않습니다.

---

## ④ 코드 비교 — Before vs After

🗣️ 강사 대본 (Instructor Script):

백문이 불여일견, 코드로 직접 비교해 봅시다. 먼저 기존 방식입니다.

```python
# Before: 전통적인 클래스 방식
class Customer:
    def __init__(self, name: str, email: str, age: int, points: int = 0):
        self.name = name
        self.email = email
        self.age = age
        self.points = points

    def __repr__(self) -> str:
        return f"Customer(name='{self.name}', email='{self.email}', age={self.age})"
```

이제 `@dataclass` 버전을 보세요.

```python
# After: @dataclass 방식
from dataclasses import dataclass

@dataclass
class Customer:
    name: str
    email: str
    age: int
    points: int = 0
```

놀랍지 않나요? 코드가 절반 이하로 줄었습니다. `__init__`도 없고, `self.name = name`도 없고, `__repr__`도 없습니다. 그런데 기능은 완전히 동일합니다. 인스턴스를 만들고 출력해 보면 똑같이 동작해요.

🎙️ 실습 가이드 (Lab Guide):

직접 확인해 봅시다. AI에게 "앞서 만든 Customer 클래스를 `@dataclass`를 사용하는 방식으로 바꿔줘"라고 요청해 보세요. 출력된 코드를 Antigravity IDE에 복사해서 실행하고, 기존과 똑같이 `customer1 = Customer("홍길동", "hong@mail.com", 30)` 형태로 인스턴스를 만들 수 있는지 확인합니다. 그리고 `print(customer1)`을 실행해 보세요 — `__repr__`을 따로 안 만들었는데도 깔끔하게 출력되는 마법을 목격하실 겁니다. 마지막으로 `from dataclasses import dataclass` 임포트 줄을 지워보고 실행하면 어떤 에러가 나는지도 확인해 보세요. 이 임포트가 왜 필수인지 몸으로 체감하실 수 있습니다.

---

## ⑤ 정리 — "스펙만 적으면 나머지는 파이썬이"

🗣️ 강사 대본 (Instructor Script):

정리하겠습니다. 데이터를 주로 담는 그릇 역할의 클래스를 만들 때는 `@dataclass`를 쓰면 코드가 훨씬 짧고 명확해집니다. "코드가 짧아진다 = 내가 칠 오타가 줄어든다 = 버그가 줄어든다 = 퇴근이 빨라진다"는 공식을 기억해 주세요. 자, 이제 클래스의 기초 문법과 최신 트렌드인 `@dataclass`까지 모두 익히셨습니다. 무기를 잘 갈고 닦았으니, 이제 실전에 투입해야죠? 다음 세션에서는 어제 만든 "절차적" 고객관리 프로그램을 "객체지향"으로 완전히 뒤엎는 리팩토링의 서막을 열어 보겠습니다!
