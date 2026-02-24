# Day 3 Python 기초 — AI-Native 강의 팩트 패킷
*Sessions: 044-064 | 학습 사이클: 🔮 예측 → ✅ 검증 → 💡 설명*

---

## 1. 변수와 자료형 (Variables & Data Types)

### 1.1 변수 = 이름표 (Label), 상자(Box)가 아님

Python에서 변수는 **이름표(label/sticky note)** — 객체가 메모리에 존재하고 변수는 그 객체를 가리키는 이름표.

### 1.2 기본 자료형 4종

| 자료형 | 영문 | 예시 | 비유 |
|--------|------|------|------|
| 정수 | `int` | `42`, `-7` | 개수 |
| 실수 | `float` | `3.14` | 측정값 |
| 문자열 | `str` | `"안녕"` | 텍스트 |
| 불리언 | `bool` | `True`, `False` | 스위치 |

### 1.3 타입 변환 함정

- `int(3.9)` → `3` (버림, 반올림 아님!)
- `bool("0")` → `True` (비어있지 않은 문자열)
- `int("3.14")` → `ValueError`

### 1.4 f-string 포매팅

```python
name = "이수진"
score = 95.7
print(f"점수: {score:.1f}점")  # 소수점 1자리
print(f"{name=}")  # Python 3.12+ 디버깅용
```

---

## 2. 연산자와 표현식

### 2.1 주요 함정

- `17 / 5` → `3.4` (Python 3에서 `/`는 항상 float)
- `10 == 10.0` → `True` (값 비교)
- `10 is 10.0` → `False` (객체 동일성 비교)
- 단락 평가: `x = 0; result = x and (10/x)` → `0` (에러 없음)

### 2.2 연산자 우선순위

`**` > `*/ // %` > `+-` > `비교` > `not` > `and` > `or`

---

## 3. 자료구조

### 3.1 리스트 (List) — 번호가 매겨진 서랍장

핵심 메서드: `append`, `extend`, `insert`, `remove`, `pop`, `sort`, `sorted`

**흔한 실수:**
- `append([4,5])` → `[1,2,3,[4,5]]` vs `extend([4,5])` → `[1,2,3,4,5]`
- `new = lst.sort()` → `None` (sort는 반환값 없음!)

### 3.2 딕셔너리 (Dictionary) — 실제 사전/고객 카드

```python
customer["phone"]       # KeyError (없는 키)
customer.get("phone")   # None (에러 없음)
customer.get("phone", "없음")  # "없음"
```

### 3.3 복합 자료구조 (List of Dicts) — 고객 데이터베이스

```python
customers = [
    {"id": 1, "name": "김민준", "age": 28, "purchases": 5},
    {"id": 2, "name": "이수진", "age": 35, "purchases": 23},
]
vip = [c for c in customers if c["purchases"] >= 10]
```

---

## 4. 제어 흐름

### 4.1 조건문 — Python 특유 문법

```python
status = "VIP" if purchases >= 10 else "일반"  # 삼항
if 0 <= score <= 100:  # 체이닝 비교 (Python만!)
```

### 4.2 반복문

```python
for idx, name in enumerate(customers, start=1):  # 인덱스+값
for name, score in zip(names, scores):  # 병렬 순회
```

### 4.3 예외처리 — 안전망(Safety Net)

```python
try:
    number = int(input("숫자 입력: "))
except ValueError:
    print("숫자가 아닙니다!")
except ZeroDivisionError:
    print("0으로 나눌 수 없습니다!")
else:
    print("성공")  # 예외 없을 때만
finally:
    print("항상 실행")
```

---

## 5. 함수 — 레시피 카드

### 5.1 기본 구조

```python
def calculate_discount(price: float, discount_rate: float = 0.1) -> float:
    """할인 가격 계산"""
    return price * (1 - discount_rate)
```

### 5.2 내장 함수 vs 리스트 컴프리헨션

```python
# map/filter는 이해용, 실무에서는 리스트 컴프리헨션이 더 Pythonic
names = [c["name"] for c in customers]  # ✅ Pythonic
vip = [c for c in customers if c["purchases"] >= 10]
```

### 5.3 리스트 컴프리헨션 — 컨베이어 벨트

```python
[표현식 for 변수 in 이터러블 if 조건]
squares = [x ** 2 for x in range(1, 6)]  # [1, 4, 9, 16, 25]
```

---

## 6. 종합실습 — 생성 코드 리뷰 게임

### 6.1 3단계 구조

```
Phase 1: 데이터 모델링 (변수 + 자료구조)
Phase 2: 로직 구현 (조건문 + 반복문 + 함수)
Phase 3: 통계 분석 (내장함수 + 리스트 컴프리헨션)
```

### 6.2 게임 형식 (15분/라운드)

1. [2분] AI 생성 코드 제시
2. [3분] 개인 예측 작성
3. [2분] 팀 토론
4. [3분] 실제 실행 + 검증
5. [5분] 강사 설명 + 핵심 개념 정리

### 6.3 핵심 비유 모음

| 개념 | 비유 |
|------|------|
| 변수 | 이름표 (sticky note) |
| 리스트 | 번호 서랍장 |
| 딕셔너리 | 실제 사전 / 고객 카드 |
| 함수 | 레시피 카드 |
| try/except | 안전망 |
| 리스트 컴프리헨션 | 컨베이어 벨트 |
| 타입 힌트 | 라벨 스티커 |

---

## 세션별 배분

```
세션 44-46: 변수와 자료형 (이름표 비유 → 4가지 타입 → 타입 변환 함정)
세션 47-49: 연산자 (산술 → 비교 → 논리 → 우선순위 예측 게임)
세션 50-54: 자료구조 (리스트 → 딕셔너리 → 복합구조)
세션 55-58: 제어 흐름 (if/elif/else → for+range → while → try/except)
세션 59-61: 함수 (def → 기본값 → 내장함수 → 컴프리헨션)
세션 62-64: 종합실습 (데이터모델 → 로직 → 통계 → 리뷰 게임)
```

*리포트 작성: 2026-02-25*
