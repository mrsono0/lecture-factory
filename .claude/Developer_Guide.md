# Lecture Factory 개발자 가이드 (Claude Code Edition)

이 문서는 Lecture Factory 시스템의 **내부 아키텍처, 에이전트 파이프라인 상세, 커맨드 매핑** 등 기술적 구조를 설명합니다.
사용법(실행 명령, 입력/결과물)은 [`Lecture_Creation_Guide.md`](./Lecture_Creation_Guide.md)를, AI 에이전트 런타임 규칙은 [`AGENTS.md`](../AGENTS.md)를 참조하세요.

---


## 로그 분석 시스템 — 빠른 시작 가이드 (Pipeline 08)

Lecture Factory의 **자기 분석(Self-Observability)** 시스템입니다. 파이프라인 1~7의 실행 로그(JSONL)를 수집하여 보틀넥, 비용, 실패 패턴을 자동 진단하고 최적화 전략을 리포트로 산출합니다.

### 사전 요구사항

- `jq >= 1.6` 설치 필요 (`brew install jq` / `apt install jq`)
- `.agent/logs/` 디렉토리에 JSONL 로그 파일 1개 이상 존재
- 로그는 파이프라인 실행 시 자동 생성됨 (`.agent/logging-protocol.md` 참조)

### 분석 스크립트 직접 사용

터미널에서 `analyze_logs.sh`를 직접 실행하여 빠르게 데이터를 확인할 수 있습니다:

```bash
# 전체 분석 (기본)
.agent/scripts/analyze_logs.sh

# 개별 서브커맨드
.agent/scripts/analyze_logs.sh summary            # 파이프라인별 실행 요약
.agent/scripts/analyze_logs.sh bottleneck 10      # 소요시간 TOP 10
.agent/scripts/analyze_logs.sh cost               # 비용 분석 (파이프라인별 + TOP 5)
.agent/scripts/analyze_logs.sh agent              # 에이전트별 통계
.agent/scripts/analyze_logs.sh failure            # 재시도/실패 분석
.agent/scripts/analyze_logs.sh parallel           # 병렬 실행 효율
.agent/scripts/analyze_logs.sh category           # LLM 카테고리별 비용
.agent/scripts/analyze_logs.sh timeline [run_id]  # 특정 실행의 타임라인
.agent/scripts/analyze_logs.sh validate           # JSONL 스키마 검증
.agent/scripts/analyze_logs.sh report             # 종합 마크다운 리포트 생성
.agent/scripts/analyze_logs.sh all                # 위 모든 분석 한번에 실행
```

### AI 에이전트 파이프라인으로 실행

에이전트 팀(L0~L5)을 통해 심층 분석 리포트를 생성합니다:

```bash
/project:log-analysis                    # 전체 분석 (auto 모드)
/project:log-analysis --mode cost         # 비용 집중 분석
/project:log-analysis --mode performance  # 성능/보틀넥 집중
/project:log-analysis --mode reliability  # 안정성/실패 집중
/project:log-analysis --mode compare      # 실행 간 비교
```

### 분석 모드 요약

| 모드 | 초점 | 실행되는 서브커맨드 |
|------|------|-------------------|
| `auto` (기본) | 전체 분석 | `all` |
| `cost` | 비용 최적화 | `cost`, `category`, `agent` |
| `performance` | 보틀넥 해소 | `bottleneck`, `parallel`, `timeline` |
| `reliability` | 실패 원인 | `failure`, `validate` |
| `compare` | 실행 간 비교 | `summary`, `timeline [run_id1]`, `timeline [run_id2]` |

### 산출물

- **리포트**: `.agent/dashboard/log_analysis_{YYYY-MM-DD}.md`
- **구성**: Executive Summary → 파이프라인 개요 → 인사이트(보틀넥/비용/안정성/토큰효율) → 최적화 제안(ROI 순) → 에이전트 성과 카드(p50/p95/p99) → SLA/SLO 현황 → 트렌드

### 파일 구조

```
.agent/
├── scripts/analyze_logs.sh     ← jq 기반 분석 도구 (599줄, 11 서브커맨드)
├── logging-protocol.md         ← JSONL 스키마 정의 (20필드, 5이벤트, 비용 단가표)
├── logs/*.jsonl                ← 파이프라인 실행 로그 (자동 생성)
├── dashboard/                  ← 분석 리포트 출력 위치
└── agents/08_log_analyzer/     ← 에이전트 프롬프트 (L0~L5, 6명)
    ├── config.json
    ├── L0_Orchestrator.md
    ├── L1_Data_Collector.md
    ├── L2_Insight_Analyst.md
    ├── L3_Optimizer.md
    ├── L4_Report_Writer.md
    └── L5_QA_Auditor.md
```

### 로그 스키마 핵심 (logging-protocol.md)

각 파이프라인 실행 시 에이전트별로 JSONL 이벤트가 기록됩니다:

| 이벤트 | 발생 시점 | 핵심 필드 |
|--------|---------|----------|
| `START` | 에이전트 실행 직전 | `run_id`, `agent`, `category`, `model`, `action` |
| `END` | 실행 완료 후 | + `duration_sec`, `input_bytes`, `output_bytes`, `est_cost_usd` |
| `FAIL` | 실행 실패 시 | + `error_message` |
| `RETRY` | 재시도 시작 | + `retry` 카운트 |
| `DECISION` | QA 판정 시 | + `decision` (approved/rejected) |

**토큰/비용 추정 공식**:
- 토큰: `est_tokens = round(bytes ÷ 3.3)` (정확도 ~85-90%)
- 비용: 카테고리별 단가 적용 — `quick` $0.00025/1K input, `deep` $0.003/1K, `ultrabrain` $0.015/1K

### 확장 가이드

**새 파이프라인의 로그 활성화**:
1. 워크플로우 YAML에 `logging:` 섹션 추가 (기존 YAML 참조)
2. `logging-protocol.md`의 스키마 필드를 준수하여 JSONL 기록
3. `analyze_logs.sh`는 `.agent/logs/*.jsonl`을 자동 탐색하므로 별도 등록 불필요

**분석 스크립트 서브커맨드 추가**:
1. `.agent/scripts/analyze_logs.sh`에 새 함수 정의
2. `case` 문에 서브커맨드 등록
3. `L1_Data_Collector.md`의 서브커맨드 테이블에 문서화

---
## 아키텍처: Subagents 기반 실행 모델

```
사용자
  │
  ├─ /project:lecture-factory 파이썬기초.md (Master Orchestrator)
  │   ├─ 1. /project:lecture-plan 실행 및 대기
  │   ├─ 2. /project:material-write 실행 및 대기
  │   ├─ 3. /project:slide-gen 실행 및 대기
  │   └─ 4. /project:slide-prompt 실행 및 대기
  │
  ├─ /project:lecture-plan $ARGS
  │   └─ Task(subagent_type="lecture-planner")
  │       ├─ AGENTS.md 로드
  │       ├─ 01_Lecture_Planning.yaml 스텝 순서 파악
  │       ├─ .agent/agents/01_planner/*.md 참조하며 순차 실행
  │       ├─ Step 4∥5: run_in_background 병렬
  │       └─ 승인/반려 루프 → 01_Planning/강의구성안.md
  │
  ├─ /project:material-write
  │   └─ Task(subagent_type="material-writer")
  │       ├─ Phase 3: 5개 background subagent 동시 스폰
  │       └─ → 02_Material/강의교안_v1.0.md
  │
  ├─ /project:slide-gen
  │   └─ Task(subagent_type="slide-generator")
  │       ├─ 배치 모드: N파일 순차, 용어집 누적
  │       └─ → 03_Slides/{session}/슬라이드기획안.md
  │
  ├─ /project:pptx-convert  또는  /project:nano-pptx
  │   └─ → 05_PPTX/ 또는 06_NanoPPTX/
  │
  └─ /project:manus-slide
      └─ python .agent/scripts/manus_slide.py
          ├─ 04_SlidePrompt/*.md 탐색
          ├─ Manus API POST /v1/tasks (순차 제출)
          ├─ 30초 폴링 → 완료 감지
          ├─ PPTX 자동 다운로드
          └─ → 07_ManusSlides/*.pptx
```

**핵심**: 각 커맨드는 해당 커스텀 에이전트를 Subagent로 스폰합니다. 에이전트는 내부적으로 `.agent/workflows/` YAML과 `.agent/agents/` 프롬프트 파일을 참조하여 파이프라인을 실행합니다.

---

## 커맨드 ↔ 에이전트 ↔ 워크플로우 매핑

### 슬래시 커맨드 (`/project:*`)

| 커맨드 | 파일 위치 | 대응 워크플로우 YAML |
|---|---|---|
| `/project:lecture-plan` | `.claude/commands/lecture-plan.md` | `01_Lecture_Planning.yaml` |
| `/project:material-write` | `.claude/commands/material-write.md` | `02_Material_Writing.yaml` |
| `/project:slide-gen` | `.claude/commands/slide-gen.md` | `03_Slide_Generation.yaml` |
| `/project:slide-prompt` | `.claude/commands/slide-prompt.md` | `04_SlidePrompt_Generation.yaml` |
| `/project:pptx-convert` | `.claude/commands/pptx-convert.md` | `05_PPTX_Conversion.yaml` |
| `/project:nano-pptx` | `.claude/commands/nano-pptx.md` | `06_NanoBanana_PPTX.yaml` |
| `/project:manus-slide` | `.claude/commands/manus-slide.md` | `.agent/scripts/manus_slide.py` |
| `/project:lecture-factory` | `.claude/commands/lecture-factory.md` | 전체 파이프라인 E2E 통합 오케스트레이션 |
| `/project:log-analysis` | `.claude/commands/log-analysis.md` | `08_Log_Analysis.yaml` |

### 커스텀 에이전트 (`/agents`)

| 에이전트 | 파일 위치 | 모델 | 병렬 실행 |
|---|---|---|---|
| `lecture-planner` | `.claude/agents/lecture-planner.md` | opus | Step 4∥5 (2개) |
| `material-writer` | `.claude/agents/material-writer.md` | opus | Phase 3 (5개 bg) |
| `slide-generator` | `.claude/agents/slide-generator.md` | sonnet | Phase 3 (3개 bg) |
| `slide-prompt-gen` | `.claude/agents/slide-prompt-gen.md` | sonnet | Phase B (2개 bg) |
| `pptx-converter` | `.claude/agents/pptx-converter.md` | sonnet | Step 4∥5 (2개) |
| `nano-pptx` | `.claude/agents/nano-pptx.md` | opus | 없음 (완전 순차) |
| `log-analyzer` | `.claude/agents/log-analyzer.md` | sonnet | Phase 2 (2개 bg) |

---

## 단계별 파이프라인 상세

### 1단계: Planning

**팀 공통 원칙**: 기획 산출물(강의구성안)만으로 교안 작성 팀이 막힘 없이 집필을 시작할 수 있어야 합니다.

**파이프라인 플로우**: A0 → A1 → A5B → A3 → A2∥A7 → A3(통합) → A5A → A0 (승인/반려)

 A5B(학습자 분석) → A3(커리큐럼 설계): A5B 산출물을 A3의 입력으로 참조
 A2∥A7 병렬 완료 후 A3가 양쪽 산출물을 커리큐럼에 통합 (Integration Hub)
 1일 4시간 초과 시 AM/PM 분할 설계, 60~90분 단위 하위 세션 세분화

### 2단계: Writing

**팀 공통 원칙**: 초보 강사가 교안만 읽고 막힘 없이 설명할 수 있어야 합니다.

**대본 시스템**: 모든 주요 개념에 🗣️ 강사 대본, 실습에 🎙️ 실습 가이드 대본을 포함합니다.

**파이프라인 플로우**:
- Phase 1: A1→A2 (소스 분석)
- Phase 2: A3→A4 (골격/초안)
- Phase 3: A5(기술 검증)∥A6∥A7(학습 경험 설계)∥A9∥A10 (**5개 병렬** — `run_in_background`)
- Phase 4: A4 (통합) → A8 (QA — 대본 존재 여부 포함 검증)

### 3단계: Visualizing

**파이프라인 플로우**:
- Phase 1: A1→A2 (분석)
- Phase 2: A3→A7 (설계)
- Phase 3: A4∥A5∥A8 (병렬) → A6 (Lab 카드)
- Phase 4: A10→A9 (QA)

### 4단계: Slide Prompt Generation

**파이프라인 플로우**: P0→P1∥P3 (병렬)→P2→P0 (조립)→P4 (QA)

- Phase A: P0 — 교안 폴더 스캔, N개 파일 발견 및 순서 결정
- Phase B: P1 (×N) ∥ P3 — 교육 구조 추출 + 비주얼 스펙 준비 [병렬]
- Phase C: P2 (×N) — 교시별 슬라이드 단위 명세 생성
- Phase D: P0 (교안별 개별 조립) → P4 (QA)

### 5단계: PPTX Conversion

**파이프라인 플로우**: B0→B1→B3→B2→B4→B5→B0 (승인/반려)

**스킬 의존**: `pptx-official` (html2pptx.js, PptxGenJS)

### 6단계: NanoBanana PPTX

**파이프라인 플로우**: C0→C1→C2→C3→C4→C5→C0 (승인/부분재생성/반려) — 완전 순차

**필수 환경변수**: `GEMINI_API_KEY`

### 7단계: Manus AI Slide Generation

**실행 방식**: Python 스크립트 (`.agent/scripts/manus_slide.py`)

**파이프라인 플로우**: D0→D1→D2→D3→D4→D5→D0 (승인/재제출/반려)


### 8단계: Log Analysis

**팀 공통 원칙**: 모든 인사이트에 정량적 근거를 포함하고, 최적화 제안은 실행 가능한 구체적 내용이어야 합니다.

**파이프라인 플로우**:
- Phase 1: L0 (Orchestrator) → L1 (Data Collector) → L1 (Schema Validate) — 순차
- Phase 2: L2 (Insight Analyst) ∥ L3 (Optimizer) — **병렬** (`run_in_background`)
- Phase 3: L4 (Report Writer) — L2+L3 산출물 통합
- Phase 4: L5 (QA Auditor) → L0 (승인/반려, 반려 시 L4로 루프)

**에이전트 카테고리 라우팅**:
- L0: `unspecified-low` | L1: `quick` | L2, L4: `deep` | L3, L5: `ultrabrain`

**데이터 흐름**:
```text
.agent/logs/*.jsonl
    ↓ L0: 분석 모드 결정 (auto/cost/performance/reliability/compare)
    ↓ L1: analyze_logs.sh 실행 → Data Packet (JSON)
    ↓
  L2 (인사이트) ─┐
  L3 (최적화)   ─┤ 병렬
                 ↓
    L4: 통합 리포트 → L5: QA → L0: 승인
    ↓
.agent/dashboard/log_analysis_{date}.md
```

---

## 교안 원문 전문 삽입 정책 (v1.1)

4단계에서 생성되는 프롬프트 파일의 §⑥ 교안 원문 섹션에는 **교안 마크다운 전문**이 삽입됩니다. 파일 경로만 참조하는 것은 금지됩니다.

**목적**: 슬라이드 생성 AI(Manus/Nano Banana Pro)가 프롬프트 파일 하나만 받아도 교안의 모든 비유, 코드, 퀴즈, 트러블슈팅 FAQ에 직접 접근할 수 있어, 비전공 초보자가 슬라이드만 보면서 따라할 수 있는 수준의 슬라이드가 생성됩니다.

| 상황 | §⑥ 삽입 범위 |
|------|------------|
| 교안 1파일 = 1세션 | 교안 전체 마크다운 전문 삽입 |
| 교안 1파일 = Day 전체 (AM+PM) | 해당 세션 교시 섹션만 추출 삽입 |
| 교안 3000줄 초과 | 해당 교시 섹션 + 공통 개요 (실습/코드/FAQ는 절대 생략 금지) |

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

## 폴더 구조 (상세)

```text
YYYY-MM-DD_강의제목/
├── 01_Planning/
│   ├── 강의구성안.md
│   └── Trend_Report.md
├── 02_Material/
│   ├── 강의교안_v1.0.md
│   ├── src/                 (예제 소스코드)
│   └── images/
├── 03_Slides/
│   ├── Day1_AM/                (세션별 서브폴더)
│   │   ├── 슬라이드기획안.md
│   │   ├── 슬라이드기획안_번들.md  (Phase 통합본)
│   │   ├── Phase1_IR_Glossary.md
│   │   ├── Phase2_SequenceMap_DesignTokens.md
│   │   ├── Phase3_Layout_Copy_Lab.md
│   │   ├── Phase3B_CodeValidation.md
│   │   └── Phase4_Trace_QA.md
│   ├── Day1_PM/
│   │   └── (동일 구조)
│   └── ...
├── 04_SlidePrompt/          (Pipeline 4)
│   ├── {세션ID}_{세션제목}_슬라이드 생성 프롬프트.md  (×N개)
│   ├── Day1_AM_환경구축_슬라이드 생성 프롬프트.md
│   └── Day1_PM_변수와자료형_슬라이드 생성 프롬프트.md
├── 05_PPTX/                 (Pipeline 5)
│   ├── 최종_프레젠테이션.pptx
│   ├── 변환리포트.md
│   ├── html/                (슬라이드별 HTML)
│   ├── assets/              (아이콘/그래디언트 PNG)
│   └── thumbnails/          (QA 썸네일)
├── 06_NanoPPTX/             (Pipeline 6)
│   ├── 최종_프레젠테이션.pptx
│   ├── 변환리포트.md
│   ├── images/              (슬라이드 PNG)
│   ├── prompts/             (이미지 생성 프롬프트)
│   └── index.html           (인터랙티브 뷰어)
├── 07_ManusSlides/          (Pipeline 7)
│   ├── {세션ID}_{세션제목}.pptx  (Manus AI 생성 PPTX ×N개)
│   ├── manus_task_log.json      (task_id 로그, 중단 복구용)
│   └── generation_report.json   (생성 결과 리포트)
└── 참고자료/
    └── 원본_기획안.md
```

> 03_Slides의 `Phase*.md` 파일은 슬라이드 생성 파이프라인의 중간 산출물입니다. 최종 결과물은 `슬라이드기획안.md`이며, `슬라이드기획안_번들.md`는 Phase 통합본입니다.

---

## 환경 변수 (상세)

`.agent/.env`에 설정 (`.agent/.env.template` 참조):

| 변수 | 필수 | 사용처 | 용도 |
|---|---|---|---|
| `GEMINI_API_KEY` | Pipeline 6 필수 | NanoBanana C3, Planner A1 | Google AI API Key |
| `TAVILY_API_KEY` | Pipeline 1 필수 | Planner A1 | Tavily 검색 API |
| `EXA_API_KEY` | 선택 | — | Exa Search API |
| `FIRECRAWL_API_KEY` | 선택 | — | Firecrawl Scraper API |
| `FLOWITH_API_TOKEN` | 선택 | A1 Source Miner | Flowith Knowledge Garden API |
| `FLOWITH_KB_LIST` | 선택 | A1 Source Miner | 지식 베이스 ID |
| `MANUS_API_KEY` | Pipeline 7 필수 | `.agent/scripts/manus_slide.py` | Manus AI API Key (Pro/Team 플랜) |

---

## 개발자 팁

- **비용 절감**: sonnet 모델 에이전트(slide-generator, pptx-converter, slide-prompt-gen)는 opus 대비 비용이 낮습니다.
- **병렬 실행**: material-writer의 Phase 3는 `run_in_background`로 5개 에이전트를 동시 실행하여 시간을 절약합니다.
- **대본 시스템**: 교안의 🗣️ 강사 대본은 슬라이드 변환 시 Speaker Notes로 이동하며, 본문의 비유/서사는 압축 보존됩니다.
- **에이전트별 모델 라우팅**: 각 파이프라인의 `.agent/agents/{team}/config.json`에서 에이전트별 LLM 카테고리를 오버라이드할 수 있습니다. 상세 매핑은 `AGENTS.md`의 "Per-Agent Model Routing" 섹션을 참조하세요.
 **Ground Truth**: `.agent/workflows/*.yaml` 8개 워크플로우 YAML이 시스템의 Ground Truth입니다. `.claude/` 디렉토리는 이 워크플로우를 호출하는 인터페이스 레이어입니다.
