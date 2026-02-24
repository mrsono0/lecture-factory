# Day 3 팩트 패킷 (세션 044-064)
> 3-Source Mandatory | Source A: 로컬 참고자료 | Source B: NotebookLM | Source C: Deep Research

## 세션별 교육 콘텐츠

### 세션 044: 변수의 개념과 이름표 상자 비유
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf, AI 시대의 서사 v3 - Claude.md], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 파이썬에서 변수는 데이터를 담는 '상자'가 아니라, 데이터(객체)에 붙이는 **이름표(Sticky note)**입니다.
  * 메모리에 데이터가 존재하고, 변수는 이를 가리킵니다. 하나의 이름표에 새로운 값을 붙이면 이전 연결은 끊어집니다.
  * AI 시대의 서사: 데이터는 요리의 '재료', 변수는 그 재료를 담는 '그릇' 혹은 '라벨'에 비유할 수 있습니다.
* 💻 **실습 예시**:
  ```python
  x = 10
  x = 20
  print(x)  # 20 — 마지막에 붙인 이름표의 값만 출력됨
  ```
* 🗣️ **강사 스크립트 포인트**:
  "여러분, 변수를 상자라고 생각하면 나중에 헷갈리기 쉽습니다. 포스트잇 이름표라고 생각하세요! 10이라는 데이터에 'x'라는 포스트잇을 붙였다가, 떼서 20에 다시 붙이는 겁니다."

### 세션 045: 기본 데이터 타입 4가지
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 컴퓨터가 데이터를 처리하는 기준이 되는 자료형입니다.
  * 4대 기본 타입: 정수(`int` - 개수), 실수(`float` - 측정값), 문자열(`str` - 텍스트), 논리형(`bool` - 스위치).
  * `type()` 함수를 사용해 데이터가 어떤 종류인지 직접 확인할 수 있습니다.
* 💻 **실습 예시**:
  ```python
  age = 25          # int
  height = 175.5    # float
  name = "홍길동"    # str
  is_student = True # bool
  print(type(age))  # <class 'int'>
  ```
* 🗣️ **강사 스크립트 포인트**:
  "데이터에도 혈액형 같은 타입이 있습니다. 숫자인지, 글자인지에 따라 컴퓨터가 처리하는 방식이 완전히 다릅니다. AI에게 코드를 맡길 때도 이 데이터 타입을 정확히 명시해주는 것이 중요합니다."

### 세션 046: 타입 변환과 f-string
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * **타입 변환 함정**: `input()`으로 받은 데이터는 항상 문자열(str)이므로 연산을 위해선 형변환이 필수입니다.
  * `int(3.9)`는 3으로 소수점을 '버림' 처리합니다. `bool("0")`은 True(비어있지 않은 문자열)가 되는 함정에 주의해야 합니다.
  * **f-string**: 문자열 앞에 `f`를 붙이고 `{}` 안에 변수를 넣어 직관적으로 포매팅합니다 (예: `{score:.1f}`).
* 💻 **실습 예시**:
  ```python
  birth_year = input("출생연도: ")  # 입력값은 무조건 str
  age = 2026 - int(birth_year)      # 정수로 변환하여 계산
  print(f"당신의 나이는 {age}세입니다") # f-string 활용
  print(f"{age=}")  # 디버깅용 (파이썬 3.12+): age=20
  ```
* 🗣️ **강사 스크립트 포인트**:
  "input()으로 받은 20과 10을 더하면 30이 아니라 2010이 됩니다. 문자열끼리 이어붙이기 때문이죠! 계산을 원한다면 반드시 int()라는 변환 마법을 걸어줘야 합니다."

### 세션 047: 기본 연산자와 실습
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 산술, 비교, 논리 연산자. 우선순위: `**` > `*, /, //, %` > `+, -`.
  * 파이썬3에서 나눗셈 `/`는 항상 실수(`float`)를 반환합니다.
  * **단락 평가(Short-circuit)**: `and`나 `or`에서 앞의 조건만으로 결과가 확정되면 뒤는 평가하지 않습니다.
  * `==` (값 비교) vs `is` (객체 주소 비교)의 차이점 인지.
* 💻 **실습 예시**:
  ```python
  print(17 / 5)   # 3.4 (float 반환)
  print(17 // 5)  # 3 (몫)
  
  # 단락 평가 함정 확인
  x = 0
  result = x and (10 / x)
  print(result)   # 0 (ZeroDivisionError가 발생하지 않음!)
  ```
* 🗣️ **강사 스크립트 포인트**:
  "파이썬의 나눗셈은 항상 소수점이 남습니다. 그리고 단락 평가는 똑똑하게 동작해요. x가 0일 때 x and (10/x)에서 에러가 안 나는 이유, 바로 파이썬이 첫 번째가 거짓임을 알고 뒤를 무시하기 때문입니다."

### 세션 048: 리스트의 이해와 기본 조작
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 리스트는 데이터가 순서대로 들어가는 **'번호가 매겨진 서랍장'**입니다.
  * 추가(`append`, `extend`), 삽입(`insert`), 삭제(`remove`, `pop`), 정렬(`sort`) 메서드.
  * **흔한 실수**: `append([4,5])`는 리스트 통째로 넣고, `extend([4,5])`는 요소를 풀어 넣습니다. `sort()`는 원본을 변경하고 `None`을 반환합니다.
* 💻 **실습 예시**:
  ```python
  fruits = ["사과", "바나나"]
  fruits.append("딸기")
  print(fruits)  # ['사과', '바나나', '딸기']
  
  new_fruits = fruits.sort()
  print(new_fruits)  # None! (sort()는 반환값이 없음)
  ```
* 🗣️ **강사 스크립트 포인트**:
  "sort()를 변수에 저장하면 안 됩니다! 리스트의 서랍장 내용물을 스스로 정리할 뿐, 새로운 서랍장을 주지 않아요. 초보자들이 가장 많이 하는 실수 중 하나입니다."

### 세션 049: 리스트 인덱싱과 슬라이싱
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 인덱싱(Indexing): 특정 위치의 데이터를 콕 집어 가져옵니다 (0부터 시작).
  * 슬라이싱(Slicing): `[start:end]` 형태로 리스트의 일부분을 잘라냅니다 (`end`는 포함하지 않음). 음수 인덱스로 뒤에서부터 접근 가능.
* 💻 **실습 예시**:
  ```python
  numbers = [10, 20, 30, 40, 50]
  print(numbers[0])     # 10
  print(numbers[-1])    # 50 (마지막 요소)
  print(numbers[1:4])   # [20, 30, 40]
  ```
* 🗣️ **강사 스크립트 포인트**:
  "컴퓨터의 숫자는 0부터 시작합니다. 첫 번째 칸은 0번, 마지막 칸은 -1번입니다. 슬라이싱 할 때 뒷번호는 '미만'이라는 점을 꼭 기억하세요!"

### 세션 050: 딕셔너리의 이해
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 딕셔너리는 **'실제 사전'** 혹은 **'고객 카드'**와 같습니다. 키(Key)표를 보고 값(Value)을 찾습니다.
  * 없는 키에 `dict["key"]`로 접근하면 `KeyError`가 발생하지만, `dict.get("key")`를 쓰면 `None`이나 기본값을 안전하게 반환합니다.
* 💻 **실습 예시**:
  ```python
  student = {"이름": "이수진", "점수": 95}
  print(student["이름"])  # "이수진"
  
  # 안전한 접근법 (실무 패턴)
  print(student.get("전화번호", "정보 없음"))  # "정보 없음"
  ```
* 🗣️ **강사 스크립트 포인트**:
  "리스트가 순서대로 나열된 서랍장이라면, 딕셔너리는 이름표가 붙어있는 고객 카드입니다. 실무에서는 에러를 방지하기 위해 괄호 대신 get() 메서드를 훨씬 많이 사용합니다."

### 세션 051: 복합 자료구조
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 리스트 안에 딕셔너리를 넣는 **List of Dicts** 구조. 
  * 현대 웹 서비스와 데이터베이스에서 데이터를 주고받는 표준 형태(JSON 스타일)이자 가장 빈번하게 쓰이는 실무 패턴입니다.
* 💻 **실습 예시**:
  ```python
  customers = [
      {"id": 1, "name": "김민준", "purchases": 5},
      {"id": 2, "name": "이수진", "purchases": 23}
  ]
  print(customers[1]["name"])  # 두 번째 고객의 이름: "이수진"
  ```
* 🗣️ **강사 스크립트 포인트**:
  "회원 목록은 리스트로 묶고, 각 회원의 상세 정보는 딕셔너리로 만듭니다. 이 두 가지를 합친 '리스트 안의 딕셔너리'는 실무에서 매일 보게 될 가장 중요한 구조입니다."

### 세션 052: 조건문 if/elif/else
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 프로그램의 흐름을 나누는 분기 제어문. 
  * 파이썬은 중괄호 대신 **들여쓰기(Indentation)**로 블록을 구분합니다.
  * 파이썬 특유의 간결한 문법: 체이닝 비교(`0 <= score <= 100`)와 삼항 연산자(`A if 조건 else B`).
* 💻 **실습 예시**:
  ```python
  score = 85
  if 0 <= score <= 100:  # 체이닝 비교
      if score >= 90:
          print("A등급")
      elif score >= 80:
          print("B등급")
      else:
          print("C등급")
          
  # 삼항 연산자
  status = "합격" if score >= 80 else "불합격"
  ```
* 🗣️ **강사 스크립트 포인트**:
  "파이썬은 수학처럼 0 <= score <= 100 이라고 쓸 수 있는 아주 직관적인 언어입니다. 조건문에서 들여쓰기를 틀리면 프로그램 구조가 무너지니 탭(Tab) 사용에 유의하세요."

### 세션 053: 반복문 for와 range
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 반복 횟수가 정해져 있거나 데이터 군집을 순회할 때 사용합니다.
  * `range()`와 찰떡궁합이며, `enumerate(순회객체)`로 인덱스와 값을 동시에 얻을 수 있습니다.
  * 병렬 순회에는 `zip()` 함수를 활용합니다.
* 💻 **실습 예시**:
  ```python
  names = ["김철수", "이영희"]
  
  # 인덱스와 함께 순회 (실무 패턴)
  for idx, name in enumerate(names, start=1):
      print(f"고객 {idx}번: {name}")
  ```
* 🗣️ **강사 스크립트 포인트**:
  "리스트의 데이터만 필요한 게 아니라 '몇 번째' 데이터인지도 필요할 때가 많죠. 그때는 복잡하게 카운트 변수를 만들지 말고 enumerate()라는 마법의 함수를 쓰면 됩니다."

### 세션 054: 반복문 while과 제어 흐름
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * `while`은 조건이 참인 동안 끝없이 반복합니다.
  * 루프를 즉시 탈출하는 `break`와 현재 반복을 건너뛰고 다음으로 넘어가는 `continue`를 통해 흐름을 정교하게 제어합니다.
* 💻 **실습 예시**:
  ```python
  count = 0
  while True:
      count += 1
      if count == 2:
          continue  # 2는 건너뜀
      if count > 3:
          break     # 3보다 크면 탈출
      print(f"루프: {count}")
  ```
* 🗣️ **강사 스크립트 포인트**:
  "for문이 정해진 트랙을 도는 달리기라면, while문은 멈추라는 신호가 올 때까지 계속 뛰는 러닝머신과 같습니다. 반드시 break라는 비상 정지 버튼을 만들어두어야 무한루프에 빠지지 않아요."

### 세션 055: 예외 처리 try/except
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf, 9 디 버깅, 테스트, 배포.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 예기치 않은 오류로 인한 프로그램 강제 종료를 막는 **안전망(Safety Net)**.
  * 에러의 유형(구문, 논리, 런타임) 중 런타임 에러를 방어합니다.
  * `try`(시도) -> `except`(대처) -> `else`(성공 시) -> `finally`(항상 실행).
* 💻 **실습 예시**:
  ```python
  try:
      num = int(input("숫자 입력: "))
      result = 100 / num
  except ValueError:
      print("숫자만 입력해야 합니다!")
  except ZeroDivisionError:
      print("0으로 나눌 수 없습니다!")
  else:
      print(f"결과는 {result}입니다.")
  finally:
      print("계산 종료.")
  ```
* 🗣️ **강사 스크립트 포인트**:
  "프로그램이 죽어버리는 것보다 '잘못된 입력입니다'라고 알려주는 것이 훨씬 좋은 UX입니다. try/except는 서커스의 안전그물처럼 여러분의 코드가 추락하는 것을 막아줍니다."

### 세션 056: 함수의 개념과 정의
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 반복되는 로직을 묶어 이름을 붙인 **'레시피 카드'** 또는 **'레고 블록'**.
  * `def` 키워드로 선언하며, 파이썬 최신 문법인 **타입 힌트**(Type Hint)를 라벨 스티커처럼 붙여 명확성을 높일 수 있습니다.
* 💻 **실습 예시**:
  ```python
  def greet(name: str) -> str:
      """이름을 받아 인사말을 반환하는 함수"""
      return f"안녕하세요, {name}님!"
      
  print(greet("AI시대"))
  ```
* 🗣️ **강사 스크립트 포인트**:
  "코드를 복사-붙여넣기 하고 있다면, 함수를 만들 때가 된 것입니다! 자주 쓰는 요리법을 레시피 카드에 적어두고 필요할 때 이름만 불러서 꺼내 쓰는 것과 같습니다."

### 세션 057: 함수의 매개변수와 반환값
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf, AI 시대의 서사 v3 - Claude.md], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 매개변수(Parameter)는 입력을 받는 통로, 반환값(Return)은 결과를 내보내는 출구입니다.
  * **핵심 오해 교정**: `print()`는 단순 화면 출력일 뿐, 재사용 가능한 데이터로 내보내려면 반드시 `return`을 사용해야 합니다.
  * 매개변수에 기본값(Default)을 설정해 유연성을 높입니다.
* 💻 **실습 예시**:
  ```python
  def calculate_discount(price: float, rate: float = 0.1) -> float:
      return price * (1 - rate)
      
  final_price = calculate_discount(10000) # rate는 기본값 0.1 적용
  print(f"할인가: {final_price}") # 변수에 저장해서 재사용 가능
  ```
* 🗣️ **강사 스크립트 포인트**:
  "많은 분들이 print와 return을 헷갈립니다. print는 음식 모형을 쇼윈도에 보여주는 것이고, return은 실제 요리를 포장해서 손님에게 건네주는 것입니다. 포장(return)해야 다른 요리에 또 쓸 수 있죠!"

### 세션 058: 내장 함수 활용
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 파이썬 설치 시 기본 제공되는 유용한 도구들. 별도의 `import` 없이 즉시 사용 가능합니다.
  * 리스트나 문자열을 다루는 `len()`, `sum()`, `max()`, `min()` 등이 자주 쓰입니다.
* 💻 **실습 예시**:
  ```python
  scores = [85, 92, 78, 95]
  count = len(scores)        # 요소 개수: 4
  total = sum(scores)        # 합계: 350
  average = total / count    # 평균 계산
  print(f"최고점: {max(scores)}, 평균: {average}")
  ```
* 🗣️ **강사 스크립트 포인트**:
  "합계나 최대값을 구하려고 굳이 for문을 돌릴 필요가 없습니다. 파이썬이 이미 만들어둔 강력한 기본 도구상자인 내장 함수를 먼저 찾아보세요. 코드가 훨씬 짧고 효율적이 됩니다."

### 세션 059: 리스트 컴프리헨션
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 한 줄로 새로운 리스트를 찍어내는 **'컨베이어 벨트'** 문법.
  * `[표현식 for 변수 in 반복객체 if 조건]` 형태를 가집니다.
  * AI가 코드 생성 시 매우 자주 사용하는 파이썬 특유(Pythonic) 문법이므로 해석 능력이 필수적입니다.
* 💻 **실습 예시**:
  ```python
  customers = [{"name": "A", "purchases": 5}, {"name": "B", "purchases": 12}]
  
  # VIP 고객(10회 이상) 이름만 추출
  vip_names = [c["name"] for c in customers if c["purchases"] >= 10]
  print(vip_names)  # ['B']
  ```
* 🗣️ **강사 스크립트 포인트**:
  "처음엔 외계어 같지만, 공장의 컨베이어 벨트를 떠올려보세요. 재료(customers)가 지나가면, 불량품을 걸러내고(if), 원하는 모양으로 가공해서(표현식) 새로운 박스([])에 담는 겁니다. AI 코드를 읽기 위한 필수 교양입니다."

### 세션 060: [종합 실습 1] 학생 성적 관리 데이터 모델링
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 학습한 변수와 복합 자료구조(List of Dicts)를 조합하여 실제 데이터를 모델링(설계)하는 첫 번째 실습 페이즈.
* 💻 **실습 예시**:
  ```python
  # 학생 데이터를 복합 자료구조로 설계
  students = [
      {"name": "김철수", "math": 85, "eng": 92},
      {"name": "이영희", "math": 95, "eng": 98},
      {"name": "박민수", "math": 70, "eng": 65}
  ]
  ```
* 🗣️ **강사 스크립트 포인트**:
  "자, 이제 흩어진 지식들을 하나로 모아볼 시간입니다. 현실의 성적표 데이터를 파이썬이 이해할 수 있는 '리스트 안의 딕셔너리' 형태로 설계해봅시다."

### 세션 061: [종합 실습 2] 제어문과 함수로 로직 구현
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 제어문(if, for)과 함수(def)를 활용하여 데이터에 생명력을 불어넣는 비즈니스 로직 작성 페이즈.
* 💻 **실습 예시**:
  ```python
  def get_grade(score: float) -> str:
      if score >= 90: return "A"
      elif score >= 80: return "B"
      else: return "C"
      
  # 각 학생별 평균과 등급 부여
  for s in students:
      s["avg"] = (s["math"] + s["eng"]) / 2
      s["grade"] = get_grade(s["avg"])
  ```
* 🗣️ **강사 스크립트 포인트**:
  "함수라는 기계 장치와 반복문이라는 컨베이어 벨트를 연결했습니다. 이제 데이터들이 로직을 통과하면서 스스로 평균과 등급이라는 새로운 정보를 갖게 됩니다."

### 세션 062: [종합 실습 3] 통계 분석기 추가
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * 내장 함수와 리스트 컴프리헨션을 결합하여 데이터를 분석하고 통계를 내는 최종 구현 페이즈.
* 💻 **실습 예시**:
  ```python
  # 수학 점수만 모아서 평균 계산 (리스트 컴프리헨션 + 내장함수)
  math_scores = [s["math"] for s in students]
  math_avg = sum(math_scores) / len(math_scores)
  
  print(f"수학 평균: {math_avg:.1f}점")
  print(f"최고 수학 점수: {max(math_scores)}점")
  ```
* 🗣️ **강사 스크립트 포인트**:
  "통계 분석은 길고 복잡할 필요가 없습니다. 앞서 배운 리스트 컴프리헨션과 내장 함수 sum, len, max를 조립하면 단 두 줄만으로도 강력한 통계 엔진이 완성됩니다."

### 세션 063: 생성 코드 리뷰 게임
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * **학습 사이클**: 🔮 예측 → ✅ 검증 → 💡 설명
  * AI가 일부러 비효율적이거나 'Messy'하게 짠 코드를 15분 라운드 형식으로 팀별 리뷰.
  * 로직 정확성, 효율성(내장 함수 미사용 여부 등), 안전성(예외 처리 누락) 검토.
* 💻 **실습 예시**:
  ```text
  [게임 룰]
  1. AI 코드 제시 (2분)
  2. 에러 및 개선점 예측 작성 (3분)
  3. 팀 토론 및 대안 탐색 (2분)
  4. 실제 실행 및 검증 (3분)
  5. 강사 해설 (5분)
  ```
* 🗣️ **강사 스크립트 포인트**:
  "AI가 코드를 짜준다고 끝이 아닙니다. AI는 가끔 나쁜 습관이 밴 코드를 주기도 해요. 여러분이 팀장(Reviewer)이 되어 AI의 코드에서 논리적 구멍과 개선점을 찾아내는 게임을 시작하겠습니다!"

### 세션 064: Day 3 총정리
* 📚 **참고자료 매핑**: [Source A: 8 코딩.pdf], [Source B: NotebookLM], [Source C: Deep Research]
* 🎯 **정의 및 핵심 개념**:
  * Day 3 핵심 문법 구조화: 변수(이름표) → 자료구조(서랍/사전) → 흐름제어(분기/반복/안전망) → 모듈화(함수/레시피).
  * 파이썬의 핵심은 '간결함(Pythonic)'과 '가독성'에 있음을 강조.
* 💻 **실습 예시**:
  ```python
  # 전체 개념을 아우르는 단일 복습
  # 이름표(변수)를 붙이고, 서랍(리스트)에 담아, 
  # 조건(if)과 반복(for)으로 요리(함수)를 합니다!
  ```
* 🗣️ **강사 스크립트 포인트**:
  "오늘 우리는 파이썬의 기초 체력을 모두 다졌습니다. 이름표를 붙이고, 서랍장에 정리하고, 컨베이어 벨트를 돌리고, 안전망을 치고, 요리 레시피를 만들었죠. 내일은 이 도구들을 가지고 코드가 어떻게 '구조'로 진화하는지 보겠습니다."
