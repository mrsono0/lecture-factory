# 세션 095: 기존 클래스 확장하기 — VIPCustomer와 super

| 항목 | 값 |
|------|-----|
| **세션 ID** | MS-PY101-095 |
| **소요 시간** | 20분 |
| **난이도** | ★★☆ (medium) |
| **청크 타입** | code |
| **선행 세션** | 094 (필수) |
| **학습 목표** | `super()` 함수를 사용해 부모 클래스의 `__init__`을 호출하고, 자식 클래스에 새로운 속성을 추가하여 VIPCustomer를 구현할 수 있다 |
| **출처** | [Source A] 8 코딩.pdf §8.14 상속 · [Source B] day5_notebooklm.md · [Source C] day5_deep_research.md |

---

## ① 도입 — "부모님 찬스를 쓰겠습니다"

🗣️ 강사 대본 (Instructor Script):

여러분, 지난 세션에서 `VIPCustomer(Customer)`라고 한 줄만 적으면 부모의 모든 기능을 물려받는다는 것을 확인했습니다. 그런데 `pass`만 적어놓은 빈 VIP 클래스는 일반 고객과 다를 게 없잖아요? VIP라면 할인율이 있어야 하고, 적립 포인트도 있어야 합니다. 문제는 이겁니다 — 자식 클래스에 새로운 속성을 추가하려면 `__init__`을 새로 작성해야 하는데, 그러면 부모의 `__init__`이 실행되지 않습니다. 이름, 전화번호, 이메일 초기화가 통째로 날아가는 거예요. 이때 등장하는 것이 바로 `super()` — "부모님 찬스"입니다.

---

## ② 비유 — 가업 리브랜딩

🗣️ 강사 대본 (Instructor Script):

비유를 들어 볼게요 [Source A][Source B]. 부모님이 30년간 운영해 온 빵집이 있습니다. 레시피, 단골 고객 명단, 매장 인테리어 — 이 모든 것이 부모님의 자산입니다. 여러분이 이 빵집을 물려받아 "프리미엄 베이커리"로 리브랜딩하려고 합니다. 기존의 레시피와 단골 명단은 그대로 유지하면서, 새로운 메뉴(마카롱, 크루아상)와 멤버십 프로그램을 추가하는 거죠.

이때 가장 중요한 첫 단계는 뭘까요? 부모님의 기존 자산을 먼저 인수인계 받는 것입니다 [Source C]. 레시피도 안 받고, 단골 명단도 안 받고, 갑자기 마카롱만 만들기 시작하면 빵집이 돌아가지 않겠죠. `super().__init__()`이 바로 이 "인수인계" 과정입니다. 부모가 해놓은 초기 셋팅(이름, 전화번호, 이메일)을 먼저 그대로 가져온 다음, 그 위에 VIP만의 특별한 속성(할인율)을 얹는 겁니다.

오버라이딩(Overriding)은 "가업 리브랜딩"과 같습니다. 부모님의 `display()` 메서드가 "[고객] 홍길동"이라고 출력했다면, VIP에서는 이것을 "[VIP] 홍길동 (할인율: 10%)"로 바꿀 수 있습니다. 같은 이름의 메서드를 자식 클래스에서 다시 정의하면, 자식의 버전이 우선 적용됩니다. 부모의 간판을 새 간판으로 교체하는 것과 같아요.

---

## ③ 개념 설명 — super()와 오버라이딩

🗣️ 강사 대본 (Instructor Script):

핵심 개념 두 가지를 정리합니다 [Source A][Source C]. 첫째, `super()`는 부모 클래스의 메서드를 호출하는 내장 함수입니다. 자식 클래스의 `__init__` 안에서 `super().__init__(name, phone, email)`이라고 적으면, 부모의 `__init__`이 먼저 실행되어 이름, 전화번호, 이메일이 세팅됩니다. 그 다음 줄에서 `self.discount_rate = discount_rate`를 추가하면 VIP만의 속성이 얹어집니다.

둘째, 오버라이딩(Overriding)은 부모의 메서드를 자식에서 같은 이름으로 다시 정의하는 것입니다 [Source B]. 부모의 `display()`가 일반 고객 정보를 출력했다면, 자식의 `display()`는 VIP 정보를 출력하도록 재정의할 수 있습니다. 파이썬은 항상 자식의 메서드를 먼저 찾고, 없으면 부모로 올라갑니다.

---

## ④ 코드 — VIPCustomer 구현

🗣️ 강사 대본 (Instructor Script):

코드로 확인해 봅시다.

```python
class VIPCustomer(Customer):
    def __init__(self, name: str, email: str, age: int,
                 discount_rate: float = 0.1):
        super().__init__(name, email, age)  # 부모 초기화 호출
        self.discount_rate = discount_rate  # VIP만의 속성

    def display(self) -> None:  # 오버라이딩
        print(f"[VIP] {self.name} | {self.email} | 할인율: {self.discount_rate:.0%}")

    def get_discount(self) -> float:
        return self.discount_rate
```

`super().__init__(name, email, age)`가 부모님 찬스입니다. 이 한 줄로 부모의 초기화가 완료되고, 그 아래에서 `self.discount_rate`만 추가하면 됩니다. `display()`는 오버라이딩되어 VIP 전용 출력 형식을 사용합니다.

🎙️ 실습 가이드 (Lab Guide):

AI에게 이렇게 요청해 보세요. "Customer 클래스를 상속받아 VIPCustomer 클래스를 만들어줘. 할인율(discount_rate) 속성을 추가하고, display() 메서드를 오버라이딩해서 VIP 정보를 출력하게 해줘." 생성된 코드를 실행하고, 일반 고객과 VIP 고객을 각각 만들어서 `display()`를 호출해 보세요. 같은 메서드 이름인데 출력이 다른 것을 확인하면 성공입니다.

---

## ⑤ 정리 — "물려받고, 덧붙이고, 바꾸고"

🗣️ 강사 대본 (Instructor Script):

오늘 배운 세 가지를 정리합니다. 첫째, `super().__init__()`으로 부모의 초기화를 먼저 호출합니다(인수인계). 둘째, 자식만의 새 속성을 추가합니다(확장). 셋째, 필요하면 부모의 메서드를 같은 이름으로 다시 정의합니다(오버라이딩). 그런데 재미있는 질문이 하나 있습니다. 일반 고객과 VIP 고객을 섞어서 리스트에 넣고, 똑같이 `get_discount()`를 호출하면 어떻게 될까요? 다음 세션에서 "다형성"이라는 놀라운 현상을 체험해 보겠습니다!
