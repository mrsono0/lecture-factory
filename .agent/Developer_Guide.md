# Lecture Factory 개발자 가이드

이 문서는 Lecture Factory 시스템의 **에이전트 파이프라인 내부 구조, 실행 흐름, 확장 방법** 등 기술적 구조를 설명합니다.
사용법(실행 명령, 입력/결과물)은 [`Lecture_Creation_Guide.md`](./Lecture_Creation_Guide.md)를, AI 에이전트 런타임 규칙은 [`../AGENTS.md`](../AGENTS.md)를 참조하세요.

> Claude Code 환경의 커맨드/에이전트 매핑, 아키텍처 다이어그램은 [`.claude/Developer_Guide.md`](../.claude/Developer_Guide.md)를 참조하세요.

---

## 단계별 에이전트 파이프라인 상세

### 1단계: Planning (01_planner)

**팀 공통 원칙**: 기획 산출물(강의구성안)만으로 교안 작성 팀이 막힘 없이 집필을 시작할 수 있어야 합니다.

**에이전트 플로우**: A0 → A1 → A5B → A3 → A2∥A7 → A5A → A0 (승인/반려)

| 에이전트 | 역할 |
|---|---|
| A0 (Orchestrator) | 요청 분석 및 업무 분배 |
| A1 (Trend Researcher) | 관련 트렌드 및 자료 조사 (NotebookLM/Web) |
| A5B (Learner Analyst) | 학습자 페르소나, 선수 지식, 이탈 예상 지점 분석 |
| A3 (Curriculum Architect) | A5B 산출물을 입력으로 받아 커리큘럼 구조 설계 |
| A2 (Instructional Designer) | 학습 활동 설계 (A7과 병렬) |
| A7 (Differentiation Advisor) | USP 식별 (A2와 병렬) |
| A5A (QA Manager) | 기획안 검증 |

- A5B → A3: A5B 산출물을 A3의 입력으로 참조
- 1일 4시간 초과 시 AM/PM 분할 설계, 60~90분 단위 하위 세션 세분화

### 2단계: Writing (02_writer)

**팀 공통 원칙**: 초보 강사가 교안만 읽고 막힘 없이 설명할 수 있어야 합니다.

**대본 시스템**: 모든 주요 개념에 🗣️ 강사 대본, 실습에 🎙️ 실습 가이드 대본을 포함합니다.

**에이전트 플로우**:
- Phase 1: A1 (Source Miner) → A2 (Traceability Curator) — 소스 분석 및 추적성
- Phase 2: A3 (Curriculum Architect) → A4 (Technical Writer) — 골격 및 초안
- Phase 3: A5(기술 검증) + A6(시각화) + A7(학습 경험 설계) + A9(강사 지원) + A10(차별화) — **5개 병렬**
  - A5: 코드 정확성 검증, A7: 실습 교육 설계 전담
- Phase 4: A4 (통합) → A8 (QA Editor) — 최종 검수 (대본 존재 여부 포함, 승인/반려)

### 3단계: Visualizing (03_visualizer)

**에이전트 플로우**:
- Phase 1: A1 (Content Analyst) → A2 (Terminology Manager) — 분석 및 정규화
- Phase 2: A3 (Slide Architect) → A7 (Visual Design Director) — 설계
- Phase 3: A4 (Layout) + A5 (Code Validator) + A8 (Copy Tone) — 병렬 생성/검증, A5 완료 후 → A6 (Lab 카드)
- Phase 4: A10 (Trace Citation) → A9 (QA Auditor) — 최종 품질 감사 (승인/반려)
- (배치 모드 시) N개 파일 완료 후 세션 간 교차 검증 (T-BRIDGE 연결성, 용어 일관성)

### 4단계: Slide Prompt Generation (04_prompt_generator)

**에이전트 플로우**: P0→P1∥P3 (병렬)→P2→P0 (조립)→P4 (QA)

- Phase A: P0 (Orchestrator) — 교안 폴더 스캔, N개 파일 발견 및 순서 결정
- Phase B: P1 (Education Structurer, ×N) ∥ P3 (Visual Spec Curator) — 교육 구조 추출 + 비주얼 스펙 준비 [병렬]
- Phase C: P2 (Slide Prompt Architect, ×N) — 교시별 슬라이드 단위 명세 생성
- Phase D: P0 (교안별 개별 조립) → P4 (QA Auditor) — 파일별 검증 및 승인/반려

### 5단계: PPTX Conversion (05_pptx_converter)

**에이전트 플로우**: B0→B1→B3→B2→B4→B5→B0 (승인/반려)

| 에이전트 | 역할 |
|---|---|
| B0 (Orchestrator) | 입력 검증 및 스킬 로드 (`pptx-official`) |
| B1 (Slide Parser) | 마크다운 → 구조화된 JSON 파싱 |
| B3 (Asset Generator) | 아이콘/그래디언트/다이어그램 PNG 생성 |
| B2 (HTML Renderer) | JSON → html2pptx.js 호환 HTML 변환 |
| B4 (PPTX Assembler) | HTML → PPTX 변환, 차트/표/이미지 삽입 |
| B5 (Visual QA) | 썸네일 검증, 시각적 결함 검사 |

### 6단계: NanoBanana PPTX (06_nanopptx)

**에이전트 플로우**: C0→C1→C2→C3→C4→C5→C0 (승인/부분재생성/반려) — 완전 순차

| 에이전트 | 역할 |
|---|---|
| C0 (Orchestrator) | 입력 검증, 스타일/해상도 결정 |
| C1 (Content Planner) | 슬라이드 마크다운 → slides_plan.json 구조화 |
| C2 (Prompt Engineer) | 슬라이드별 이미지 생성 프롬프트 작성 |
| C3 (Image Generator) | Nano Banana Pro 호출, 16:9 PNG 생성 |
| C4 (PPTX Builder) | 이미지 삽입 + Speaker Notes → PPTX 조립 |
| C5 (Visual QA) | 텍스트 정확성, 스타일 일관성 검사 |

### 7단계: Manus AI Slide Generation (07_manus_slide)

**에이전트 플로우**: D0→D1→D2→D3→D4→D5→D0 (승인/재제출/반려)

**실행 흐름**:
```text
04_SlidePrompt/*.md (N개 프롬프트)
    ↓ POST /v1/tasks (순차 제출)
Manus AI (Nano Banana Pro 슬라이드 생성, 3~15분/파일)
    ↓ 30초 간격 폴링
완료 시 output[].fileUrl
    ↓ curl 자동 다운로드
07_ManusSlides/{세션ID}_{세션제목}.pptx
```

---

## 교시 분할 전략 (Chunking) — 7단계

P04 프롬프트 파일이 대용량인 경우, Manus AI의 최적 처리를 위해 교시(세션) 단위로 자동 분할합니다:

| 조건 | 동작 |
|------|------|
| ≤1,000줄 AND ≤35 슬라이드 | 원샷 제출 (분할 없음) |
| >1,000줄 OR >35 슬라이드 | 교시 단위 자동 분할 |

- **분할 기준**: ③ 슬라이드 명세의 `#### N. 세션 X-Y 파트:`, ⑥ 교안 원문의 `## 세션 X-Y:` 경계
- **청크 구성**: ①②④⑤ 공통 헤더 + ③-N번째 교시 슬라이드 + ⑥-N번째 교시 원문
- **병합**: 청크별 PPTX를 python-pptx로 병합 (슬라이드 노트 보존)
- **비활성화**: `--no-split` 플래그로 분할 없이 원본 전체 제출 가능

---

## 교안 원문 전문 삽입 정책 (v1.1)

4단계에서 생성되는 프롬프트 파일의 §④ 교안 원문 섹션에는 **교안 마크다운 전문**이 삽입됩니다. 파일 경로만 참조하는 것은 금지됩니다.

**목적**: 슬라이드 생성 AI(Manus/Nano Banana Pro)가 프롬프트 파일 하나만 받아도 교안의 모든 비유, 코드, 퀴즈, 트러블슈팅 FAQ에 직접 접근할 수 있어, 비전공 초보자가 슬라이드만 보면서 따라할 수 있는 수준의 슬라이드가 생성됩니다.

| 상황 | §④ 삽입 범위 |
|------|------------|
| 교안 1파일 = 1세션 | 교안 전체 마크다운 전문 삽입 |
| 교안 1파일 = Day 전체 (AM+PM) | 해당 세션 교시 섹션만 추출 삽입 |
| 교안 3000줄 초과 | 해당 교시 섹션 + 공통 개요 (실습/코드/FAQ는 절대 생략 금지) |

---

## 에이전트별 모델 라우팅

각 파이프라인의 `.agent/agents/{team}/config.json`에서 에이전트별 LLM 카테고리를 오버라이드할 수 있습니다. 상세 매핑은 `../AGENTS.md`의 "Per-Agent Model Routing" 섹션을 참조하세요.

---

## 개발자 팁

- **Ground Truth**: `.agent/workflows/*.yaml` 7개 워크플로우 YAML이 시스템의 Ground Truth입니다.
- **에이전트 프롬프트**: `.agent/agents/{team}/*.md` 파일에 각 에이전트의 상세 역할이 정의되어 있습니다.
- **병렬 실행**: Writer Phase 3는 5개, Visualizer Phase 3는 3개, Planner Step 4∥5는 2개 에이전트를 동시 실행합니다.
- **대본 시스템**: 교안의 🗣️ 강사 대본은 슬라이드 변환 시 Speaker Notes로 이동하며, 본문의 비유/서사는 압축 보존됩니다.
