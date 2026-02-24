# 세션 098: 파일 저장 모듈(FileStorage) 구현

| 항목 | 값 |
|------|-----|
| **세션 ID** | MS-PY101-098 |
| **소요 시간** | 25분 |
| **난이도** | ★★☆ (medium) |
| **청크 타입** | code |
| **선행 세션** | 097 (필수) |
| **학습 목표** | `json` 모듈을 활용하여 고객 데이터를 JSON 파일로 저장하고 불러오는 `JsonFileStorage` 클래스를 구현할 수 있다 |
| **출처** | [Source A] 8 코딩.pdf §8.14 데이터 영속화 · [Source B] day5_notebooklm.md · [Source C] day5_deep_research.md |

---

## ① 도입 — "프로그램을 끄면 데이터가 사라집니다"

🗣️ 강사 대본 (Instructor Script):

여러분, 지금까지 열심히 고객을 등록하고 수정하고 삭제했는데, 프로그램을 한 번 껐다 켜면 어떻게 되나요? 모든 데이터가 증발합니다. 메모리(RAM)는 휘발성이기 때문이에요. 전원이 꺼지면 내용물이 전부 날아갑니다. 실제 서비스에서 이런 일이 벌어지면 고객들이 폭동을 일으키겠죠. 오늘은 이 문제를 해결합니다. 메모리에만 존재하던 데이터를 물리적인 파일로 영구 보존하는 첫 번째 저장소, `JsonFileStorage`를 만들어 보겠습니다.

---

## ② 비유 — 서류함 전담 직원

🗣️ 강사 대본 (Instructor Script):

비유를 들어 볼게요 [Source A][Source B]. 지금까지 우리 회사(프로그램)의 고객 데이터는 화이트보드(메모리)에 적혀 있었습니다. 퇴근할 때 누군가 화이트보드를 지우면 끝이에요. 이제 "서류함 전담 직원(JsonFileStorage)"을 고용합니다. 이 직원의 역할은 딱 두 가지입니다. 첫째, 화이트보드의 내용을 종이 서류(JSON 파일)에 옮겨 적어서 서류함(하드디스크)에 보관합니다(`save`). 둘째, 다음 날 출근하면 서류함에서 종이를 꺼내 화이트보드에 다시 옮겨 적습니다(`load`).

JSON(JavaScript Object Notation)은 데이터를 텍스트로 표현하는 국제 표준 형식입니다 [Source C]. 사람이 읽을 수 있고, 거의 모든 프로그래밍 언어가 지원합니다. 파이썬에서는 `json` 모듈 하나면 딕셔너리를 JSON 텍스트로 변환하거나, JSON 텍스트를 딕셔너리로 복원할 수 있습니다. 그리고 `@dataclass`로 만든 객체는 `dataclasses.asdict()` 함수로 딕셔너리로 변환할 수 있으니, 객체 → 딕셔너리 → JSON 파일이라는 변환 체인이 완성됩니다.

---

## ③ 개념 설명 — 직렬화와 역직렬화

🗣️ 강사 대본 (Instructor Script):

두 가지 핵심 용어를 알아 두세요 [Source A][Source C]. 직렬화(Serialization)는 메모리 속 객체를 파일에 저장할 수 있는 형태(텍스트, 바이트)로 변환하는 과정입니다. 우리의 경우 `Customer` 객체를 JSON 문자열로 바꾸는 것이 직렬화입니다. 역직렬화(Deserialization)는 그 반대 — 파일에서 읽어온 텍스트를 다시 객체로 복원하는 과정입니다.

파이썬의 `json.dump()`는 딕셔너리를 파일에 JSON 형태로 쓰고, `json.load()`는 파일에서 JSON을 읽어 딕셔너리로 복원합니다. 이 두 함수만 알면 파일 저장소를 만들 수 있습니다.

---

## ④ 코드 — JsonFileStorage 구현

🗣️ 강사 대본 (Instructor Script):

코드를 봅시다.

```python
import json
from dataclasses import asdict

class JsonFileStorage(Storage):
    def __init__(self, filepath: str = "customers.json"):
        self._filepath = filepath

    def save(self, customers: list[Customer]) -> None:
        data = [asdict(c) for c in customers]
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {len(customers)}명의 고객 데이터를 {self._filepath}에 저장했습니다.")

    def load(self) -> list[Customer]:
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Customer(**item) for item in data]
        except FileNotFoundError:
            return []
```

핵심을 짚겠습니다. `save()`에서 `asdict(c)`는 `@dataclass` 객체를 딕셔너리로 변환합니다. `json.dump()`가 이 딕셔너리 리스트를 파일에 씁니다. `load()`에서는 `json.load()`로 파일을 읽고, `Customer(**item)`으로 딕셔너리를 다시 객체로 복원합니다. `**item`은 딕셔너리의 키-값 쌍을 매개변수로 풀어주는 문법입니다.

🎙️ 실습 가이드 (Lab Guide):

AI에게 이렇게 요청하세요. "Storage 클래스를 상속받아 JsonFileStorage를 구현해줘. json 모듈과 dataclasses.asdict를 사용해서 Customer 객체 리스트를 JSON 파일로 저장하고 불러오는 기능을 만들어줘." 생성된 코드를 실행하고, 고객 3명을 등록한 뒤 `save()`를 호출해 보세요. 프로젝트 폴더에 `customers.json` 파일이 생성되었는지 확인하고, 프로그램을 껐다 켠 뒤 `load()`로 데이터가 복원되는지 테스트합니다.

---

## ⑤ 정리 — "데이터가 영원히 살아남습니다"

🗣️ 강사 대본 (Instructor Script):

축하합니다! 이제 프로그램을 꺼도 데이터가 사라지지 않습니다. `JsonFileStorage`라는 서류함 전담 직원이 퇴근 전에 모든 데이터를 종이(JSON 파일)에 옮겨 적어 두니까요. 그런데 고객이 수백만 명이 되면 텍스트 파일로는 감당이 안 됩니다. 검색도 느리고, 동시 접근도 어렵죠. 다음 세션에서는 이 한계를 극복하는 두 번째 저장소, `SQLiteStorage`를 만들어 보겠습니다!
