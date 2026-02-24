# Day 1 Deep Research Report: AI-Native Python Course
**강의 1일차 심층 리서치 리포트**
*Generated: 2026-02-25 | Sources: Official docs, Google Cloud Blog, Astral docs, arXiv, community sources*
*Sessions: 001-022*

---

## TOPIC 1: Google Antigravity IDE (2025–2026)

### 1.1 개요 (What Is It?)

**Google Antigravity**는 2025년 11월 18일 Gemini 3 모델과 함께 발표된 Google의 **에이전트 우선(Agent-First) 개발 플랫폼**이다. VS Code 포크 기반으로 구축되었으며, 기존 AI 코딩 도구(자동완성 방식)와 근본적으로 다른 패러다임을 제시한다.

| 항목 | 내용 |
|------|------|
| 개발사 | Google (Windsurf 팀 인수 후 개발, 2025년 7월 $2.4B 인수) |
| 출시일 | 2025년 11월 18일 |
| 가격 | **무료** (개인 개발자) |
| 플랫폼 | Windows 10/11, macOS 12+, Linux |
| 기반 | VS Code 포크 |
| 주요 AI 모델 | Gemini 3 Pro (기본), Claude Sonnet 4.5, GPT-OSS-120B |
| 최신 버전 | 1.18.4 (2026년 2월 21일) |
| 공식 사이트 | [antigravity.google](https://antigravity.google) |
| 변경 이력 | [antigravity.google/changelog](https://antigravity.google/changelog) |

**패러다임 전환:**
```
[기존 방식] 개발자가 코드 작성 → AI가 다음 줄 제안 → 개발자 수락/수정
[Antigravity] 개발자가 목표 설명 → 에이전트가 계획 수립 → 에이전트가 자율 실행 → 개발자가 결과 검토
```

### 1.2 핵심 기능 (Key Features)

#### 🖥️ 이중 인터페이스 (Dual Interface)

**Editor View (에디터 뷰)**
- VS Code와 동일한 친숙한 환경
- 구문 강조, IntelliSense, 통합 터미널
- 에이전트 사이드바로 빠른 상호작용
- 사용 시점: 수동 코드 검토, 복잡한 로직 디버깅

**Agent Manager View (에이전트 매니저 뷰)**
- 다중 에이전트를 위한 "미션 컨트롤"
- 여러 에이전트를 동시에 생성·모니터링
- 병렬 개발 작업 관리
- 사용 시점: 대규모 기능 개발, 자율 작업 위임

> 🗣️ **강사 설명 포인트**: "에디터는 여러분이 직접 코드를 쓰는 공간이고, 에이전트 매니저는 AI 직원들에게 일을 시키는 관리자 대시보드입니다. 여러분은 이제 코더가 아니라 팀 리더입니다."

#### 🤖 Agent Manager (에이전트 매니저)

에이전트가 수행할 수 있는 작업:
- **Plan (계획)**: 복잡한 작업을 단계별로 분해
- **Execute (실행)**: 코드 작성, 편집, 삭제
- **Validate (검증)**: 테스트 실행 및 변경사항 확인
- **Iterate (반복)**: 피드백 기반 수정 및 개선
- **Document (문서화)**: 문서 및 주석 자동 생성

**에이전트 특화 패턴 (Agent Specialization Patterns):**

| 에이전트 유형 | 역할 | 예시 작업 |
|-------------|------|---------|
| Architect Agent | 시스템 설계, 스캐폴딩 | "마이크로서비스 아키텍처 설계" |
| Feature Agent | 기능 구현 | "장바구니 기능 구현" |
| Test Agent | QA, 테스트 생성 | "결제 플로우 통합 테스트 작성" |
| Refactor Agent | 코드 최적화 | "인증 모듈 성능 리팩토링" |
| Documentation Agent | 문서화 | "OpenAPI 스펙에서 API 문서 생성" |

**병렬화의 핵심 이점:**
> 💡 "5배 빠른 이유는 AI가 코드를 더 빨리 생성해서가 아닙니다. **5개의 에이전트가 시스템의 서로 다른 부분에서 동시에 작업**하기 때문입니다."

#### 🍌 Nano Banana (나노 바나나)

- **정식 명칭**: Gemini 3 Pro Image Model
- **기능**: 코드베이스를 분석하여 시스템 다이어그램, 아키텍처 다이어그램, UI 목업 등 **시각적 자산을 자동 생성**
- **특징**: 생성 전에 "생각"하는 능력 보유; Google Search 그라운딩으로 실시간 데이터 통합
- **Nano Banana Pro**: 2026년 1월 업그레이드 버전 출시

#### 📦 Artifacts (아티팩트)

에이전트가 생성하는 **인간이 읽을 수 있는 결과물**:
1. **Task Lists (작업 목록)**: 에이전트가 수행한 단계별 목록
2. **Implementation Plans (구현 계획)**: 아키텍처 결정 이유 설명
3. **Screenshots & Browser Recordings (스크린샷 및 브라우저 녹화)**: 내장 Chrome 인스턴스로 앱을 실행하고 상호작용을 녹화
4. **Progress Reports (진행 보고서)**: 작업 완료 요약

#### 🛠️ Agent Skills (에이전트 스킬)

2026년 1월 출시된 **오픈 스탠다드** 확장 시스템.
- `SKILL.md` 파일 기반의 폴더 구조
- **3단계 로딩 아키텍처 (Progressive Disclosure)**
- 호환성: Antigravity, Claude Code, Gemini CLI, OpenCode 등

### 1.3 Windows 11 설치 방법

**시스템 요구사항:**
- Windows 10 또는 11 (64비트)
- 최소 4GB RAM (권장 16GB)
- 인터넷 연결 필수
- Google 계정 필수

**설치 단계:**
```
1단계: antigravity.google/download 방문
2단계: 다운로드된 .exe 파일 실행
3단계: 설치 위치 선택 (기본: C:\Program Files\Google\Antigravity)
4단계: 시작 메뉴 또는 바탕화면 바로가기로 실행 → Google 계정 로그인
```

### 1.4 경쟁 도구 비교

| 기능 | Google Antigravity | Cursor | GitHub Copilot | Windsurf |
|------|-------------------|--------|----------------|---------|
| **가격** | **무료** | $20/월 | $10-19/월 | (인수됨) |
| **접근 방식** | 에이전트 우선 | 증강 코딩 | 자동완성 | 단일 에이전트 |
| **컨텍스트 창** | **1M+ 토큰** | 제한적 | 128K 토큰 | 향상됨 |
| **에이전트 조율** | **다중 에이전트** | 단일 | 없음 | 단일 |

### 1.5 교육 활용 포인트

**초보자를 위한 Antigravity 사용 흐름:**
```
1. 목표 설명 (자연어로)
2. 에이전트 계획 검토
3. 자율 실행 관찰
4. 결과 검증
```

---

## TOPIC 2: uv 패키지 매니저 (by Astral)

### 2.1 개요

| 항목 | 내용 |
|------|------|
| 개발사 | Astral (Ruff 개발팀) |
| 언어 | Rust |
| 최신 버전 | **0.10.4** (2026년 2월 17일) |
| GitHub | [astral-sh/uv](https://github.com/astral-sh/uv) (⭐ 79,641) |
| 핵심 가치 | pip, pip-tools, pipx, pyenv, virtualenv, poetry를 **하나의 도구**로 대체 |

### 2.2 pip/conda 대비 장점

| 작업 | uv | Poetry | pip-tools |
|------|-----|--------|-----------|
| 콜드 설치 | **~3초** | ~11초 | ~33초 |
| Lock 파일 생성 | **~8초** | ~22초 | ~35초 |
| 단일 패키지 추가 | **<1초** | ~3초 | ~6초 |

### 2.3 Windows 설치

```powershell
# PowerShell (권장)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2.4 핵심 명령어 (교육용 치트시트)

```bash
# 프로젝트 초기화
uv init my-project && cd my-project

# 가상환경
uv venv
.venv\Scripts\activate  # Windows

# 패키지 설치
uv pip install flask
uv add flask  # pyproject.toml 업데이트

# Python 버전 관리
uv python install 3.12
uv python list

# 실행
uv run python script.py
```

---

## TOPIC 3: AI-First Python 학습 방법론

### 3.1 패러다임 전환

```
[전통] 문법 학습 → 코드 작성 → 실행 → 오류 수정
[AI-First] 목표 설정 → AI 코드 생성 → 코드 읽기/이해 → 설명 → 수정
```

### 3.2 예측-검증-설명 학습법 (Predict-Verify-Explain Cycle)

```
1. 예측 (Predict): "이 코드가 어떤 결과를 출력할까?"
2. 검증 (Verify): "실제로 실행해서 확인하자"
3. 설명 (Explain): "왜 이런 결과가 나왔는가?"
```

### 3.3 SDD (Specification-Driven Development) for Beginners

**SDD란?** 사양(Specification)을 소프트웨어 개발의 **주요 진실 원천**으로 취급하는 개발 패러다임.

**"Vibe Coding" vs SDD:**
| | Vibe Coding | SDD |
|--|-------------|-----|
| 접근 | "뭔가 만들어줘" | "이런 사양으로 만들어줘" |
| 결과 | 예측 불가 | 예측 가능 |
| 반복 | 어려움 | 쉬움 |
| 초보자 적합성 | 낮음 | **높음** |

### 3.4 AI-First 학습의 핵심 원칙

1. **코드 읽기 > 코드 쓰기**
2. **이해 없는 복사 금지**
3. **오류는 학습 기회**
4. **점진적 복잡성 증가**

---

## TOPIC 4: 코드 생성을 위한 프롬프트 엔지니어링 기초

### 4.1 PTCF 프레임워크

```
P - Persona (페르소나): "AI가 어떤 역할을 해야 하는가?"
T - Task (작업): "무엇을 해야 하는가?"
C - Context (컨텍스트): "어떤 상황/제약 조건인가?"
F - Format (형식): "어떤 형태로 출력해야 하는가?"
```

### 4.2 Zero-Shot vs Few-Shot

- **Zero-Shot**: 예시 없이 직접 작업 지시 → 명확하고 단순한 작업에 적합
- **Few-Shot**: 1-3개의 예시를 제공하여 원하는 패턴 학습 → 특정 스타일 중요할 때

### 4.3 Python 코드 생성 특화 팁

1. 구체적인 요구사항 명시
2. 제약 조건 명시
3. 출력 형식 지정
4. 단계별 분해 (복잡한 작업)
5. 검증 기준 포함

---

## TOPIC 5: 멀티 에이전트 오케스트레이션 기초

### 5.1 단일 에이전트 vs 멀티 에이전트

**비유 1: 레스토랑 주방**
- 수셰프 (오케스트레이터): 전체 조율
- 파스타 요리사: 파스타 담당
- 소스 요리사: 소스 담당

**비유 2: 소프트웨어 개발팀**
- PM 에이전트: 요구사항 분석, 작업 분배
- 백엔드 에이전트: API 개발
- QA 에이전트: 테스트 작성

### 5.2 멀티 에이전트 패턴

1. **순차 파이프라인**: 에이전트 A → 결과 → 에이전트 B → 결과 → 에이전트 C
2. **병렬 실행**: 독립적인 작업을 동시에 처리
3. **계층 구조**: 매니저 → 팀 리더 → 워커

---

## 핵심 요약 (강사용 치트시트)

### Day 1 핵심 메시지
1. **AI 시대의 개발자** = 코드 작성자 → 에이전트 관리자
2. **Antigravity** = 무료, VS Code 기반, 멀티 에이전트 오케스트레이션
3. **uv** = pip 대체, 10-100배 빠름, 하나의 도구로 모든 것
4. **예측-검증-설명** = AI 코드를 수동적으로 받지 말고 능동적으로 이해
5. **PTCF 프레임워크** = 좋은 프롬프트의 4요소
6. **멀티 에이전트** = AI 팀을 관리하는 것

### 수업 흐름 제안
```
세션 1-2: AI 시대 서사 → "왜 이 강의인가?"
세션 3-8: 개발환경 구축 → Antigravity + uv 설치 실습
세션 9-14: 첫 코드 생성 → PTCF 프롬프트로 Python 코드 생성
세션 15-22: 예측-검증-설명 → AI 코드 이해 훈련
```

---

## 부록: 교육 자료 링크 모음

| 도구 | 문서 URL |
|------|---------|
| Google Antigravity | https://antigravity.google |
| uv 공식 문서 | https://docs.astral.sh/uv |
| SDD with AI (GitHub) | https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai |
| 프롬프트 엔지니어링 가이드 | https://www.promptingguide.ai |

### 연구 논문
| 논문 | URL |
|------|-----|
| AI 보조 Python 교육 향상 (2025) | https://arxiv.org/abs/2509.20518 |
| 메타인지 이론 기반 AI 프로그래밍 교육 (2025) | https://arxiv.org/abs/2509.03171 |

*리포트 작성: 2026-02-25 | 데이터 기준일: 2026년 2월*
