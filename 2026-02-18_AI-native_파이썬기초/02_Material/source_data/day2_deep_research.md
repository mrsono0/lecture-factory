# Day 2 Deep Research Report: AI-Native Python Course
## 프롬프트 엔지니어링 심화 · 요구사항 정의 · SDD · PRD · 미니 스펙 프로젝트
*Sessions: 023-043*

---

## TOPIC 1: 프롬프트 엔지니어링 심화

### 1.1 프롬프트 구성 4요소

| 요소 | 영어 | 설명 | 예시 (고객 관리 프로그램) |
|------|------|------|--------------------------|
| **지시** | Instruction | 수행할 구체적 작업 | "고객 목록을 출력하는 Python 함수를 작성해라" |
| **맥락** | Context | 배경 정보 | "소규모 카페의 고객 관리용" |
| **입력 데이터** | Input Data | 처리할 실제 데이터 | "고객 데이터: {'이름': '김철수', '방문횟수': 5}" |
| **출력 형식** | Output Indicator | 원하는 출력 형태 | "Python 코드 블록으로만 답해라" |

### 1.2 Chain-of-Thought (CoT) 프롬프팅

| 방식 | 설명 | 프롬프트 예시 |
|------|------|--------------|
| **Zero-shot CoT** | "단계별로 생각해라" 지시 | "Let's think step by step" |
| **Few-shot CoT** | 추론 과정이 포함된 예시 제공 | 예시에 추론 단계 포함 |

### 1.3 Few-shot Learning for Code Generation

핵심 원칙: 예시의 품질이 출력의 품질을 결정한다. 좋은 예시 = 좋은 코드.

### 1.4 Iterative Refinement (반복적 개선)

```
1단계: 초안 생성 (Draft)
2단계: 평가 및 피드백 (Evaluate & Feedback)
3단계: 개선 요청 (Refine)
```

### 1.5 코드 생성 프롬프트의 5가지 핵심 요소

1. 역할/페르소나 (Role/Persona)
2. 기술 스택 명시 (Tech Stack)
3. 구체적 요구사항 (Specific Requirements)
4. 입출력 예시 (Input/Output Examples)
5. 제약 조건 및 출력 형식 (Constraints & Format)

---

## TOPIC 2: 요구사항 정의

### 2.1 요구사항이란?

소프트웨어가 **무엇을 해야 하는지(기능)** 와 **어떻게 동작해야 하는지(품질)** 를 명확하게 기술한 것.

### 2.2 5W1H 요구사항 추출 체크리스트

| 질문 | 의미 | 고객 관리 프로그램 예시 |
|------|------|----------------------|
| WHO | 누가 사용? | 카페 직원 (비개발자) |
| WHAT | 무엇을 하나? | 고객 추가/조회/수정/삭제 |
| WHEN | 언제 사용? | 고객 방문 시, 하루 10~50회 |
| WHERE | 어디서? | 카페 카운터 PC |
| WHY | 왜 필요? | 단골 고객 관리, 방문 횟수 추적 |
| HOW | 어떻게 동작? | 콘솔 메뉴 방식, 키보드 입력 |

### 2.3 기능 요구사항 vs 비기능 요구사항

```
기능 요구사항 (FR):
FR-01: 사용자는 고객 이름, 전화번호를 입력하여 새 고객을 등록할 수 있다
FR-02: 사용자는 이름으로 고객을 검색할 수 있다
FR-03~06: 수정, 삭제, 목록, 방문 기록

비기능 요구사항 (NFR):
NFR-01: [성능] 검색 결과는 1초 이내
NFR-02: [사용성] 메뉴는 번호로 선택
NFR-03: [신뢰성] 프로그램 종료 시 데이터 저장
NFR-04: [유지보수성] 한국어 주석 포함
```

---

## TOPIC 3: SDD (Specification-Driven Development)

### 3.1 SDD란?

명세(Specification)를 소프트웨어의 유일한 진실의 원천(Single Source of Truth)으로 삼는 개발 방법론.

### 3.2 SDD vs TDD 비교

| 비교 항목 | TDD | SDD |
|----------|-----|-----|
| 핵심 산출물 | 단위 테스트 | 실행 가능한 명세 |
| 범위 | 개별 함수/클래스 | 시스템 전체 아키텍처 |
| 검증 방식 | 테스트 통과 여부 | 명세와 구현의 일치 여부 |
| AI 거버넌스 | 없음 | 명세가 AI 코드 생성을 제어 |

### 3.3 바이브 코딩의 5가지 문제

1. **맥락 증발**: AI 대화가 끝나면 결정 이유가 사라짐
2. **파편화된 구현**: 계획 없이 조각조각 생성
3. **기술 부채**: "작동하는 것처럼 보임"
4. **아키텍처 표류**: 일관성 없는 구조
5. **테스트 불가**: 무엇을 테스트해야 하는지 불명확

### 3.4 초급자를 위한 SDD 4단계 프로세스

```
1단계: 명세 (Specification) → spec.md
2단계: 계획 (Plan) → plan.md
3단계: 태스크 (Tasks) → tasks.md
4단계: 구현 (Implementation) → 실제 코드
```

---

## TOPIC 4: PRD (Product Requirements Document)

### 4.1 PRD 구조 (초급자용 7섹션)

1. 개요 (Overview)
2. 문제 정의 (Problem Statement)
3. 기능 명세 (Functional Requirements)
4. 비기능 요구사항 (Non-Functional Requirements)
5. 사용자 시나리오 (User Scenarios)
6. 성공 지표 (Success Metrics)
7. 범위 외 (Out of Scope)

### 4.2 고객 관리 프로그램 PRD 완성 예시

```markdown
# PRD: 카페 고객 관리 프로그램 v1.0

## 1. 개요
- 콘솔 기반 카페 고객 관리 시스템
- 대상: 카페 직원 (비개발자)
- Python 3.11, 표준 라이브러리만

## 3. 기능 명세
| ID | 기능 | 상세 |
|----|------|------|
| FR-01 | 고객 추가 | 이름, 전화번호 입력 → 방문횟수 0으로 등록 |
| FR-02 | 고객 조회 | 이름으로 검색 |
| FR-03 | 전체 목록 | 모든 고객 출력 |
| FR-04 | 방문 기록 | 방문횟수 +1 |
| FR-05 | 고객 수정 | 전화번호 변경 |
| FR-06 | 고객 삭제 | 확인 메시지 포함 |

## 6. 성공 지표
- 6가지 기능 모두 작동
- 잘못된 입력에도 프로그램 종료 안 됨
- 비개발자가 사용법 이해 가능
```

### 4.3 PRD → Plan → Todo 워크플로우

```
PRD (무엇을 만드는가?) → Plan (어떻게?) → Todo (구체적 태스크) → Implementation
```

---

## TOPIC 5: 미니 스펙 프로젝트 방법론

### 5.1 6단계 가이드

1. **Phase 1: 주제 선택** (30분) — 콘솔 기반, CRUD 포함, 실생활 연결
2. **Phase 2: 요구사항 작성** (45분) — 브레인스토밍 → 5W1H → FR/NFR 분류
3. **Phase 3: PRD 작성** (60분) — 7섹션 템플릿 활용
4. **Phase 4: 코드 생성** (90분) — PRD → 프롬프트 변환 → 기능별 분할 생성
5. **Phase 5: 테스트** (30분) — 정상/빈 입력/잘못된 입력/경계값/중복
6. **Phase 6: 팀 발표** (15분/팀) — 소개→PRD→데모→배운점→Q&A

### 5.2 발표 평가 기준

| 평가 항목 | 배점 |
|----------|------|
| PRD 완성도 | 20점 |
| 기능 구현 | 30점 |
| 코드 품질 | 20점 |
| 발표 명확성 | 20점 |
| 팀 협업 | 10점 |

---

## 핵심 용어 사전

| 한국어 | 영어 | 설명 |
|--------|------|------|
| 연쇄 사고 | Chain-of-Thought (CoT) | AI가 단계별로 추론하도록 유도 |
| 소수 예시 학습 | Few-shot Learning | 예시를 보여주어 패턴 학습 |
| 반복적 개선 | Iterative Refinement | 점진적 개선 |
| 기능 요구사항 | Functional Requirements (FR) | 시스템이 무엇을 해야 하는가 |
| 명세 주도 개발 | Spec-Driven Development (SDD) | 명세를 진실의 원천으로 삼는 개발 |
| 바이브 코딩 | Vibe Coding | 명세 없이 AI에게 즉흥적으로 요청 |
| 범위 이탈 | Scope Creep | 계획에 없던 기능이 추가되는 현상 |

---

## 참고 자료

| 자료 | URL |
|------|-----|
| Prompt Engineering Guide | promptingguide.ai |
| Anthropic Interactive Tutorial | github.com/anthropics/prompt-eng-interactive-tutorial |
| Augment Code - SDD Guide | augmentcode.com/guides/what-is-spec-driven-development |
| SpecWeave - Vibe Coding Problem | spec-weave.com |

*리포트 작성: 2026-02-25*
