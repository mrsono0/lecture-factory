# .agent/AGENTS.md — Agent Teams & Model Routing

> 이 파일은 파이프라인 실행 시 에이전트 팀 구조, 모델 라우팅, 로깅 규칙의 상세 참조 문서입니다.
> 전체 시스템 운영 규칙은 루트 `AGENTS.md`를 참조하세요.

---

## Agent Teams

각 에이전트의 상세 역할은 `.agent/agents/{team}/` 프롬프트 파일에 정의되어 있습니다.

### Team 1: Planner (01_planner) — 7 agents
**팀 공통 원칙**: 기획 산출물(강의구성안)만으로 교안 작성 팀이 막힘 없이 집필을 시작할 수 있어야 합니다.
**Flow**: A0 → A1 → A5B → A3 → A2 ∥ A7 → A3(통합) → A5A → A0 (승인/반려)
 A5B(학습자 분석) → A3(커리큐럼 설계): A5B 산출물을 A3의 입력으로 참조
 A2∥A7 병렬 완료 후 A3가 양쪽 산출물을 커리큐럼에 통합 (Integration Hub)
 1일 4시간 초과 시 AM/PM 분할 설계, 60~90분 단위 하위 세션 세분화

### Team 2: Writer (02_writer) — 11 agents
**팀 공통 원칙**: 초보 강사가 교안만 읽고 막힘 없이 설명할 수 있어야 합니다.
**대본 시스템**: 모든 주요 개념에 🗣️ 강사 대본, 실습에 🎙️ 실습 가이드 대본을 포함합니다.
**Flow**:
- Phase 1: A1 → A2 (소스 분석)
- Phase 2: A3 → A4 (골격 및 초안)
- Phase 3: A5(기술 검증) + A6 + A7(학습 경험 설계) + A9 + A10 (병렬)
- Phase 4: A4 (통합) → A8 (최종 QA)

### Team 3: Visualizer (03_visualizer) — 11 agents
**Flow**:
- Phase 1: A1 → A2 (분석)
- Phase 2: A3 → A7 (설계)
- Phase 3: A4 + A5 + A8 (병렬), A5 → A6 (Lab 카드)
- Phase 4: A10 → A9 (최종 QA)

### Team 4: Slide Prompt Generator (04_prompt_generator) — 5 agents
**Flow**:
 Phase A: P0 (입력 탐색, N개 스캐폴딩)
 Phase B: P1 (교육 구조 ×N) ∥ P3 (비주얼 스펙) [병렬]
 Phase C: P2 (슬라이드 명세 ×N)
 Phase D: P0 (조립) → P4 (QA)
 Phase E: P0 (최종 산출물 저장)

> **Pipeline 4 정책**: §⑥ 교안 원문 섹션에 교안 마크다운 전문을 삽입합니다. 상세 규칙은 P0/P2 에이전트 명세 참조.

### Team 5: PPTX Converter (05_pptx_converter) — 6 agents
**Flow**: B0 → B1 → B3 → B2 → B4 → B5 → B0 (승인/반려)
**Tech**: html2pptx.js (Playwright + PptxGenJS), Sharp, react-icons

### Team 6: NanoBanana (06_nanopptx) — 6 agents
**Flow**: C0 → C1 → C2 → C3 → C4 → C5 → C0 (승인/부분 재생성/반려)
**Required**: `GEMINI_API_KEY`

### Team 7: Manus Slide (07_manus_slide) — 6 agents
**Flow**: D0 → D1 → D2 → D3 → D4 → D5 → D0 (승인/재제출/반려)
**Tech**: Manus AI API (manus-1.6-max), Nano Banana Pro, python-pptx
**Required**: `MANUS_API_KEY`
**분할 전략**: 교시 단위 순차 분할 (≤1,000줄 원샷 / 1,000+ 교시 분할)
- D2(Chunk Splitter): ③⑥ 교시 경계 감지 → 공통 헤더 + 교시별 청크 생성
- D3(Submission Manager): 청크별 순차 제출 → PPTX 다운로드
- D4(Post Processor): 청크 PPTX 병합 (python-pptx, 슬라이드 노트 보존)

### Team 8: Log Analyzer (08_log_analyzer) — 6 agents
**팀 공통 원칙**: 모든 인사이트에 정량적 근거를 포함하고, 최적화 제안은 실행 가능한 구체적 내용이어야 합니다.
**도구**: `.agent/scripts/analyze_logs.sh` (jq 기반 11개 서브커맨드)
**Flow**:
 Phase 1: L0 → L1 (범위 결정 → 데이터 수집 + 스키마 검증)
 Phase 2: L2(인사이트 분석) ∥ L3(최적화 제안) [병렬]
 Phase 3: L4 (리포트 작성) → L5 (QA 검증)
 Phase 4: L0 (최종 승인/반려)

---

## Per-Agent Model Routing

각 파이프라인의 `config.json`에서 에이전트별 LLM 카테고리를 지정합니다.

### 해석 규칙

1. 오케스트레이터가 파이프라인 실행 시 `.agent/agents/{team}/config.json`을 읽습니다.
2. 에이전트가 `agent_models`에 **있으면** → 지정된 카테고리의 모델 사용
3. 에이전트가 `agent_models`에 **없으면** → `default_category`의 모델 사용
4. 카테고리 → 모델 매핑은 `.Claude/oh-my-Claude.jsonc`의 `categories` 섹션 참조

### config.json 스키마

```jsonc
{
    "name": "팀명",
    "default_category": "deep",           // 팀 기본 카테고리
    "agent_models": {                      // 에이전트별 오버라이드 (선택)
        "A5_Code_Validator": {
            "category": "quick",           // 이 에이전트만 다른 카테고리 사용
            "note": "코드 검증 — 정확성만 필요"
        }
    }
}
```

### 파이프라인별 에이전트 모델 매핑

| Pipeline | 기본 카테고리 | 오버라이드 에이전트 | 오버라이드 카테고리 |
|----------|:---:|---|:---:|
| **P01** Planner | `deep` | A0 Orchestrator | `unspecified-low` |
| | | A3 Curriculum Architect, A5A QA Manager | `ultrabrain` |
| | | A7 Differentiation Advisor | `artistry` |
| **P02** Writer | `deep` | A2 Traceability Curator, A5 Code Validator | `quick` |
| | | A6 Visualization Designer | `visual-engineering` |
| | | A8 QA Editor | `ultrabrain` |
| | | A10 Differentiation Strategist | `artistry` |
| **P03** Visualizer | `visual-engineering` | A2 Terminology, A5 Code, A6 Lab, A10 Trace | `quick` |
| | | A8 Copy Tone Editor | `writing` |
| | | A9 QA Auditor | `ultrabrain` |
| **P04** Prompt Generator | `writing` | P0 Orchestrator | `unspecified-low` |
| | | P1 Education Structurer | `deep` |
| | | P2 Slide Prompt Architect | `deep` |
| | | P3 Visual Spec Curator | `visual-engineering` |
| | | P4 QA Auditor | `ultrabrain` |
| **P05** PPTX Converter | `quick` | B0 Orchestrator, B1 Slide Parser | `unspecified-low` |
| | | B2 HTML Renderer | `visual-engineering` |
| | | B5 Visual QA | `visual-engineering` |
| **P06** NanoBanana | `visual-engineering` | C2 Prompt Engineer | `writing` |
| **P07** Manus Slide | `quick` | D0 Orchestrator | `unspecified-low` |
| | | D2 Chunk Splitter | `writing` |
| | | D5 Visual QA | `ultrabrain` |
| **P08** Log Analyzer | `deep` | L0 Orchestrator | `unspecified-low` |
| | | L1 Data Collector | `quick` |
| | | L3 Optimizer, L5 QA Auditor | `ultrabrain` |

---

## Agent Execution Logging

모든 파이프라인 실행 시 에이전트별 구조화된 로그를 기록합니다.

 **프로토콜 정의**: `.agent/logging-protocol.md` (JSONL 포맷, 20+ 필드 스키마, 토큰/비용 추정 공식, model 매핑)
 **로그 위치**: `.agent/logs/{YYYY-MM-DD}_{pipeline_name}.jsonl`
 **워크플로우 설정**: 각 `.agent/workflows/*.yaml`의 `logging:` 섹션
 **이벤트 유형**: `START`, `END`, `FAIL`, `RETRY`, `DECISION`, `SESSION_START`, `SESSION_END`
 **실행 모델**: Step-by-Step (순차 실행) 또는 Session-Parallel (세션 병렬 위임), 파이프라인별 기본 모델은 `logging-protocol.md` §11 참조
 **토큰 추정**: `est_tokens = round(bytes ÷ 3.3)` (input_bytes + output_bytes 기반, 정확도 ~85-90%)
 **비용 추정**: 에이전트 카테고리별 단가 테이블 적용 (quick=Haiku급, deep=Sonnet급, ultrabrain=Opus급)
오케스트레이터는 실행 모델에 따라 step 또는 session 단위로 `logging-protocol.md`를 참조하여 JSONL 로그를 기록합니다.
- **Step-by-Step**: 각 step 실행 전후로 START/END 이벤트 기록 (Pipeline 01, 02, 05, 06, 07, 08)
- **Session-Parallel**: 세션 단위 병렬 위임 시 SESSION_START/SESSION_END 이벤트 기록 (Pipeline 03, 04)
로그 파일(`.jsonl`)은 `.gitignore`에 의해 Git 추적에서 제외됩니다.
