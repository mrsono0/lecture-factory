# Agent Execution Logging Protocol

> 워크플로우·에이전트 실행 시 구조화된 로그를 기록하여 보틀넥 분석, 토큰/비용 추적, 디버깅을 지원합니다.
> 이 프로토콜은 OpenTelemetry GenAI Semantic Conventions, AgentTrace(AAAI-26), RudderStack Multi-Agent Event Schema를 참고하여 설계되었습니다.

---

## 1. 로그 파일 위치 및 네이밍

```
.agent/logs/{YYYY-MM-DD}_{pipeline_name}.jsonl
```

**예시:**
- `.agent/logs/2026-02-22_01_Lecture_Planning.jsonl`
- `.agent/logs/2026-02-22_02_Material_Writing.jsonl`

**규칙:**
- 같은 날 같은 파이프라인 재실행 시 **append** (덮어쓰기 금지)
- 포맷: **JSONL** (JSON Lines — 한 줄에 하나의 JSON 객체)
- 인코딩: UTF-8

---

## 2. 이벤트 유형

| status | 발생 시점 | 설명 |
|--------|-----------|------|
| `START` | 에이전트 실행 직전 | step 시작 기록 |
| `END` | 에이전트 실행 완료 후 | 소요시간, 데이터 크기, 토큰/비용 추정치 포함 |
| `FAIL` | 에이전트 실행 실패 시 | error_message 포함 |
| `RETRY` | 재시도 시작 시 | retry 카운트 증가 |
| `DECISION` | QA/승인 스텝 판정 시 | decision 필드에 approved/rejected |
| `SESSION_START` | 세션 단위 병렬 실행 시작 | session_id, session_name 포함. Session-Parallel 모델 전용 |
| `SESSION_END` | 세션 단위 병렬 실행 완료 | 세션 전체의 duration/bytes/cost + output_files 포함 |

---

## 3. 필드 정의

### 3.1 공통 필드 (모든 이벤트)

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| `run_id` | string | O | 파이프라인 실행 고유 ID | `"run_20260222_143005"` |
| `parent_run_id` | string | — | E2E 실행 시 마스터 run_id (선택) | `"run_20260222_140000"` / `null` |
| `ts` | string | O | ISO 8601 타임스탬프 | `"2026-02-22T14:30:05"` |
| `status` | string | O | 이벤트 유형 | `"START"` / `"END"` / `"FAIL"` / `"RETRY"` / `"DECISION"` / `"SESSION_START"` / `"SESSION_END"` |
| `workflow` | string | O | 파이프라인명 | `"01_Lecture_Planning"` |
| `step_id` | string | O | 워크플로우 YAML의 step id | `"step_0_scope"` / `"session_Day1_AM"` |
| `agent` | string | O | 에이전트명 | `"A0_Orchestrator"` |
| `category` | string | O | config.json의 LLM 카테고리 | `"deep"` / `"ultrabrain"` |
| `model` | string | O | 실행 시 배정된 LLM 모델명 (model_config에서 category→model 조회) | `"anthropic/claude-opus-4-6"` |
| `action` | string | O | 워크플로우 YAML의 action 필드 | `"analyze_request"` |
| `parallel_group` | string | — | 병렬 실행 그룹 (없으면 null) | `"phase3"` / `"batch_1"` / `null` |
| `retry` | number | O | 재시도 횟수 (0=첫 실행) | `0` |

### 3.2 END 전용 필드

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| `duration_sec` | number | O | 소요 시간 (초) | `40.2` |
| `input_bytes` | number | O | 입력 데이터 크기 (bytes) | `15200` |
| `output_bytes` | number | O | 출력 데이터 크기 (bytes) | `9600` |
| `est_input_tokens` | number | O | 추정 입력 토큰 수 | `4606` |
| `est_output_tokens` | number | O | 추정 출력 토큰 수 | `2909` |
| `est_cost_usd` | number | O | 추정 비용 (USD) | `0.018` |
| `decision` | string | — | QA/승인 판정 (해당 시만) | `"approved"` / `"rejected"` / `null` |

### 3.3 FAIL 전용 필드

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| `error_message` | string | O | 에러 메시지 | `"Timeout after 300s"` |

### 3.4 SESSION 전용 필드 (SESSION_START / SESSION_END)

> Session-Parallel 실행 모델에서 사용됩니다. SESSION_END는 END 전용 필드(§3.2)를 동일하게 포함합니다.

| 필드 | 타입 | 필수 | 설명 | 예시 |
|------|------|:----:|------|------|
| `session_id` | string | O | 세션 식별자 | `"Day1_AM"` |
| `session_name` | string | O | 세션 표시명 | `"환경구축과 첫 API"` |
| `total_slides` | number | — | 생성된 슬라이드 수 (해당 시) | `38` |
| `output_files` | string[] | — | 생성된 파일 목록 (상대 경로) | `["슬라이드기획안.md", "Phase1_IR_Glossary.md"]` |

---

## 4. 토큰 추정 공식

BPE 토크나이저는 바이트 레벨로 동작하므로, **바이트 수**를 기반으로 추정합니다.

```
est_input_tokens  = round(input_bytes  ÷ 3.3)
est_output_tokens = round(output_bytes ÷ 3.3)
```

> **근거**: 영어 ~4 bytes/token, 한국어 ~2.5 bytes/token (UTF-8 3바이트 × ~1.5 token),
> 코드 ~3.5 bytes/token. 한국어+코드 혼합 기준 평균 **3.3 bytes/token**.
> 정확도: ~85-90% (순수 영문 또는 순수 한국어일 때 ±10% 오차).

### 4.1 데이터 크기 측정 방법

| 측정 대상 | 측정 시점 | 측정 방법 |
|-----------|-----------|-----------|
| `input_bytes` | START 시 | 에이전트 프롬프트 파일 + 이전 step 산출물의 UTF-8 바이트 수 합산 |
| `output_bytes` | END 시 | 에이전트가 생성한 산출물의 UTF-8 바이트 수 |

---

## 5. 비용 추정 테이블

카테고리별 예상 모델 및 단가 (2026.02 기준, USD per 1K tokens):

| category | 예상 모델 | input ($/1K) | output ($/1K) |
|----------|-----------|:------------:|:-------------:|
| `quick` | Haiku/Flash | 0.00025 | 0.00125 |
| `unspecified-low` | Sonnet/Flash | 0.003 | 0.015 |
| `deep` | Sonnet/Pro | 0.003 | 0.015 |
| `visual-engineering` | Sonnet/Pro | 0.003 | 0.015 |
| `writing` | Sonnet/Pro | 0.003 | 0.015 |
| `ultrabrain` | Opus/Pro | 0.015 | 0.075 |
| `artistry` | Opus/Pro | 0.015 | 0.075 |
| `unspecified-high` | Opus/Pro | 0.015 | 0.075 |

**비용 계산:**
```
est_cost_usd = (est_input_tokens × input_price / 1000) + (est_output_tokens × output_price / 1000)
```

> **Note**: 이 테이블은 실제 프로바이더 가격 변동에 따라 주기적으로 업데이트해야 합니다.

---

## 6. run_id 생성 규칙

```
run_{YYYYMMDD}_{HHMMSS}
```

- 파이프라인 실행 시작 시 1회 생성
- 해당 파이프라인의 모든 step이 동일한 `run_id`를 공유
- 재시도(retry) 시에도 동일한 `run_id` 유지
- E2E 실행 시 각 하위 파이프라인은 자체 `run_id`를 생성하고, 마스터의 `run_id`는 `parent_run_id`에 기록

**예시**: `run_20260222_143005`

---

## 7. JSONL 예시

### 7.1 Step-by-Step 모델 (기존)

```jsonl
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:30:05","status":"START","workflow":"01_Lecture_Planning","step_id":"step_0_scope","agent":"A0_Orchestrator","category":"unspecified-low","model":"opencode/claude-sonnet-4-6","action":"analyze_request","parallel_group":null,"retry":0}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:30:45","status":"END","workflow":"01_Lecture_Planning","step_id":"step_0_scope","agent":"A0_Orchestrator","category":"unspecified-low","model":"opencode/claude-sonnet-4-6","action":"analyze_request","parallel_group":null,"retry":0,"duration_sec":40,"input_bytes":15200,"output_bytes":9600,"est_input_tokens":4606,"est_output_tokens":2909,"est_cost_usd":0.047,"decision":null}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:30:46","status":"START","workflow":"01_Lecture_Planning","step_id":"step_1_trend","agent":"A1_Trend_Researcher","category":"deep","model":"anthropic/claude-opus-4-6","action":"research_trend","parallel_group":null,"retry":0}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:35:20","status":"END","workflow":"01_Lecture_Planning","step_id":"step_1_trend","agent":"A1_Trend_Researcher","category":"deep","model":"anthropic/claude-opus-4-6","action":"research_trend","parallel_group":null,"retry":0,"duration_sec":274,"input_bytes":9600,"output_bytes":28500,"est_input_tokens":2909,"est_output_tokens":8636,"est_cost_usd":0.138,"decision":null}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:40:00","status":"START","workflow":"01_Lecture_Planning","step_id":"step_4_inst","agent":"A2_Instructional_Designer","category":"deep","model":"anthropic/claude-opus-4-6","action":"design_activities","parallel_group":"phase2_parallel","retry":0}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:40:00","status":"START","workflow":"01_Lecture_Planning","step_id":"step_5_diff","agent":"A7_Differentiation_Advisor","category":"artistry","model":"google/antigravity-gemini-3.1-pro","action":"identify_usp","parallel_group":"phase2_parallel","retry":0}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:48:30","status":"END","workflow":"01_Lecture_Planning","step_id":"step_4_inst","agent":"A2_Instructional_Designer","category":"deep","model":"anthropic/claude-opus-4-6","action":"design_activities","parallel_group":"phase2_parallel","retry":0,"duration_sec":510,"input_bytes":18000,"output_bytes":22000,"est_input_tokens":5454,"est_output_tokens":6666,"est_cost_usd":0.116,"decision":null}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:52:15","status":"FAIL","workflow":"01_Lecture_Planning","step_id":"step_6_qa","agent":"A5A_QA_Manager","category":"ultrabrain","model":"opencode/gpt-5.3-codex","action":"verify_plan","parallel_group":null,"retry":0,"error_message":"QA rejected: 시간 합계 불일치 (40h expected, 38h found)"}
{"run_id":"run_20260222_143005","ts":"2026-02-22T14:52:16","status":"RETRY","workflow":"01_Lecture_Planning","step_id":"step_3_curriculum","agent":"A3_Curriculum_Architect","category":"ultrabrain","model":"opencode/gpt-5.3-codex","action":"design_structure","parallel_group":null,"retry":1}
```

### 7.2 Session-Parallel 모델 (신규)

```jsonl
{"run_id":"run_20260223_230000","ts":"2026-02-23T23:00:00","status":"SESSION_START","workflow":"03_Slide_Generation","step_id":"session_Day1_AM","agent":"A0_Orchestrator","category":"visual-engineering","model":"anthropic/claude-sonnet-4-6","action":"generate_slides","parallel_group":"batch_1","retry":0,"session_id":"Day1_AM","session_name":"환경구축과 첫 API"}
{"run_id":"run_20260223_230000","ts":"2026-02-23T23:00:00","status":"SESSION_START","workflow":"03_Slide_Generation","step_id":"session_Day1_PM","agent":"A0_Orchestrator","category":"visual-engineering","model":"anthropic/claude-sonnet-4-6","action":"generate_slides","parallel_group":"batch_1","retry":0,"session_id":"Day1_PM","session_name":"프롬프트엔지니어링과 SpringBoot 핵심"}
{"run_id":"run_20260223_230000","ts":"2026-02-23T23:08:30","status":"SESSION_END","workflow":"03_Slide_Generation","step_id":"session_Day1_AM","agent":"A0_Orchestrator","category":"visual-engineering","model":"anthropic/claude-sonnet-4-6","action":"generate_slides","parallel_group":"batch_1","retry":0,"session_id":"Day1_AM","session_name":"환경구축과 첫 API","duration_sec":510,"input_bytes":42000,"output_bytes":168000,"est_input_tokens":12727,"est_output_tokens":50909,"est_cost_usd":0.802,"decision":null,"total_slides":38,"output_files":["슬라이드기획안.md","슬라이드기획안_번들.md","Phase1_IR_Glossary.md","Phase2_SequenceMap_DesignTokens.md","Phase3_Layout_Copy_Lab.md","Phase3B_CodeValidation.md","Phase4_Trace_QA.md"]}
{"run_id":"run_20260223_230000","ts":"2026-02-23T23:09:45","status":"SESSION_END","workflow":"03_Slide_Generation","step_id":"session_Day1_PM","agent":"A0_Orchestrator","category":"visual-engineering","model":"anthropic/claude-sonnet-4-6","action":"generate_slides","parallel_group":"batch_1","retry":0,"session_id":"Day1_PM","session_name":"프롬프트엔지니어링과 SpringBoot 핵심","duration_sec":585,"input_bytes":36000,"output_bytes":155000,"est_input_tokens":10909,"est_output_tokens":46970,"est_cost_usd":0.736,"decision":null,"total_slides":55,"output_files":["슬라이드기획안.md","슬라이드기획안_번들.md","Phase1_IR_Glossary.md","Phase2_SequenceMap_DesignTokens.md","Phase3_Layout_Copy_Lab.md","Phase3B_CodeValidation.md","Phase4_Trace_QA.md"]}
{"run_id":"run_20260223_230000","ts":"2026-02-23T23:20:00","status":"END","workflow":"03_Slide_Generation","step_id":"pipeline_summary","agent":"Sisyphus","category":"unspecified-low","model":"anthropic/claude-opus-4-6","action":"orchestrate_pipeline","parallel_group":null,"retry":0,"duration_sec":1200,"input_bytes":0,"output_bytes":0,"est_input_tokens":0,"est_output_tokens":0,"est_cost_usd":8.02,"decision":"approved"}
```

---

## 8. 분석 쿼리 예시 (jq)

### 보틀넥 분석: 소요시간 TOP 5
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="END" or .status=="SESSION_END"))
  | sort_by(-.duration_sec)
  | .[0:5]
  | .[] | {step_id, agent, category, duration_sec}
'
```

### 비용 분석: 파이프라인별 총 비용
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="END" or .status=="SESSION_END"))
  | group_by(.workflow)
  | map({
      workflow: .[0].workflow,
      total_cost_usd: (map(.est_cost_usd) | add),
      total_tokens: (map(.est_input_tokens + .est_output_tokens) | add)
    })
'
```

### 에이전트별 평균 소요시간
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="END" or .status=="SESSION_END"))
  | group_by(.agent)
  | map({
      agent: .[0].agent,
      avg_duration: (map(.duration_sec) | add / length),
      total_cost: (map(.est_cost_usd) | add)
    })
  | sort_by(-.avg_duration)
'
```

### 재시도/실패 빈도
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="FAIL" or .status=="RETRY"))
  | group_by(.agent)
  | map({agent: .[0].agent, fail_count: length, errors: map(.error_message // .step_id)})
'
```

### 병렬 실행 효율 분석
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select((.status=="END" or .status=="SESSION_END") and .parallel_group != null))
  | group_by(.parallel_group)
  | map({
      group: .[0].parallel_group,
      agents: map(.agent),
      max_duration: (map(.duration_sec) | max),
      total_if_sequential: (map(.duration_sec) | add),
      parallelism_gain: ((map(.duration_sec) | add) - (map(.duration_sec) | max))
    })
'
```

### 세션별 산출물 요약 (Session-Parallel)
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="SESSION_END"))
  | map({session_id, session_name, duration_sec, total_slides, est_cost_usd, output_files})
'
```

---

## 9. 오케스트레이터 구현 가이드

### 9.0 실행 모델 분류

Lecture Factory는 두 가지 실행 모델을 지원합니다:

| 실행 모델 | 설명 | 이벤트 패턴 | 대표 파이프라인 |
|-----------|------|------------|---------------|
| **Step-by-Step** | 오케스트레이터가 내부 에이전트를 순차/병렬 호출 | N×(START+END) | 01, 02, 05, 06, 07, 08 |
| **Session-Parallel** | 상위 오케스트레이터가 세션 단위로 병렬 위임 | M×(SESSION_START+SESSION_END) | 03, 04 |

**판단 기준**:
- **Step-by-Step**: 오케스트레이터 자체가 워크플로우 YAML의 각 step을 직접 실행할 때
- **Session-Parallel**: 상위 시스템(Sisyphus 등)이 세션을 병렬 에이전트로 위임하고, 각 에이전트가 전체 파이프라인을 자율 실행할 때

**혼합 모델**: 일부 파이프라인은 상황에 따라 두 모델 모두 사용할 수 있습니다.
- Pipeline 01: 보통 Step-by-Step이지만, 여러 강의를 병렬 기획 시 Session-Parallel 가능
- Pipeline 03/04: 보통 Session-Parallel이지만, 단일 세션 처리 시 Step-by-Step 가능

### 9.1 공통: 파이프라인 시작 시
1. **`run_id` 확인**: 상위에서 전달받은 `run_id`가 있으면 사용, 없으면 `run_{YYYYMMDD}_{HHMMSS}` 형식으로 자체 생성합니다.
2. **`parent_run_id` 확인**: E2E 실행으로 호출된 경우 상위의 마스터 `run_id`를 `parent_run_id`로 기록합니다.
3. 워크플로우 YAML의 `logging:` 섹션을 읽어 로그 파일 경로를 결정합니다.
4. 로그 파일이 없으면 새로 생성, 있으면 append 모드로 엽니다.
5. `config.json`을 읽어 에이전트별 카테고리 매핑을 로드합니다.

### 9.2 Step-by-Step 모델

오케스트레이터가 워크플로우 YAML의 각 step을 직접 실행할 때 사용합니다.

#### 9.2.1 각 step 실행 시
1. **START 로그**: step 시작 직전에 START 이벤트를 기록합니다.
2. **에이전트 실행**: 에이전트의 프롬프트를 읽고 역할을 수행합니다.
3. **END 로그**: step 완료 직후에 END 이벤트를 기록합니다.
   - `duration_sec`: START의 ts와 현재 시간의 차이
   - `input_bytes`: 에이전트에게 전달한 입력의 UTF-8 바이트 수
   - `output_bytes`: 에이전트가 생성한 산출물의 UTF-8 바이트 수
   - `est_input_tokens`, `est_output_tokens`: bytes ÷ 3.3
   - `est_cost_usd`: 토큰 × 카테고리별 단가

#### 9.2.2 실패/재시도 시
1. **FAIL 로그**: 실패 즉시 FAIL 이벤트를 기록합니다 (`error_message` 포함).
2. **RETRY 로그**: 재시도 시작 직전에 RETRY 이벤트를 기록합니다 (`retry` 카운트 증가).

### 9.3 Session-Parallel 모델

상위 시스템이 세션 단위로 병렬 에이전트를 위임하고, 각 에이전트가 전체 파이프라인을 자율 실행할 때 사용합니다.

#### 9.3.1 세션 시작 시
1. 상위 오케스트레이터로부터 `run_id`를 전달받습니다.
   - 전달받지 못한 경우, 자체 `run_id`를 생성합니다.
2. `SESSION_START` 이벤트를 기록합니다:
   - `step_id`: `"session_{session_id}"` (예: `"session_Day1_AM"`)
   - `session_id`: 세션 식별자 (예: `"Day1_AM"`)
   - `session_name`: 세션 표시명 (예: `"환경구축과 첫 API"`)
   - `parallel_group`: 배치 그룹 (예: `"batch_1"`)

#### 9.3.2 세션 완료 시
1. `SESSION_END` 이벤트를 기록합니다:
   - `duration_sec`: SESSION_START부터 현재까지의 경과 시간
   - `input_bytes`: 세션 입력(교안 마크다운 등)의 UTF-8 바이트 수
   - `output_bytes`: 세션 산출물 전체의 UTF-8 바이트 수 합계
   - `est_input_tokens`, `est_output_tokens`: bytes ÷ 3.3
   - `est_cost_usd`: 토큰 × 카테고리별 단가
   - `output_files`: 생성된 파일 목록 (상대 경로)
   - `total_slides`: 슬라이드 수 (해당 시)

#### 9.3.3 세션 실패 시
1. `FAIL` 이벤트를 기록합니다 (기존 FAIL 스키마 동일)
   - `step_id`: `"session_{session_id}"` (예: `"session_Day1_AM"`)
   - `error_message`: 실패 원인

### 9.4 상위 오케스트레이터의 로깅 책임 (Session-Parallel 시)

Sisyphus(또는 E2E 오케스트레이터)가 Session-Parallel 실행을 조율할 때:

1. **파이프라인 시작 전**: `run_id`를 생성하여 모든 세션 에이전트에게 전달합니다.
2. **배치 관리**: 병렬 배치의 `parallel_group`을 지정합니다 (예: `"batch_1"`, `"batch_2"`).
3. **파이프라인 종료 후**: 전체 파이프라인의 요약 `END` 이벤트를 기록합니다:
   - `step_id`: `"pipeline_summary"`
   - `duration_sec`: 전체 파이프라인 소요 시간
   - `est_cost_usd`: 개별 세션 비용의 합산

### 9.5 config.json 카테고리 결정
1. `config.json`의 `agent_models`에서 현재 에이전트를 찾습니다.
2. 있으면 → 해당 `category` 사용
3. 없으면 → `default_category` 사용

### 9.6 model 필드 결정 (category→model 매핑)
1. 파이프라인 시작 시 워크플로우 YAML의 `logging.model_config` 경로를 읽어 모델 설정 파일을 로드합니다.
2. 해당 파일의 `categories` 섹션에서 `category` 키로 `model` 값을 조회합니다.
3. 매 step/session의 START/END/SESSION_START/SESSION_END 로그에 조회된 `model` 값을 기록합니다.
4. 매핑 실패 시(config에 카테고리 없음) `"unknown"`을 기록합니다.

---

## 10. model 필드 하위 호환 정책

2026-02-22 이전에 생성된 로그는 `model` 필드가 포함되어 있지 않을 수 있습니다.

### 10.1 호환성 규칙
 `model` 필드가 없거나 `null`/빈 문자열인 로그 이벤트는 **유효한 레코드로 처리**합니다.
 분석 도구(`analyze_logs.sh`)는 `model` 필드 부재 시 `"unknown"`으로 대체하여 집계합니다.
 QA 감사(L5)는 `model` 필드 누락 로그에 대해 "⚠️ model 필드 누락 (레거시)"로 경고하되 반려하지 않습니다.

### 10.2 적용 기준일
 **2026-02-23 이후** 생성되는 모든 로그는 `model` 필드를 **필수**로 포함해야 합니다.
 기존 로그는 재처리 없이 현재 상태로 유지합니다.
**예시**: `category: "ultrabrain"` → config의 `categories.ultrabrain.model` → `"opencode/gpt-5.3-codex"`

### 10.3 SESSION 이벤트 하위 호환
 `SESSION_START`/`SESSION_END` 이벤트는 2026-02-23부터 도입되었습니다.
 기존 분석 쿼리(`select(.status=="END")`)는 SESSION_END를 자동으로 무시하므로 하위 호환됩니다.
 SESSION 이벤트를 포함한 분석이 필요하면 `select(.status=="END" or .status=="SESSION_END")`로 필터링합니다.

---

## 11. 파이프라인별 기본 실행 모델

| Pipeline | 기본 모델 | 세션 분할 기준 | 이벤트 패턴 |
|----------|----------|---------------|------------|
| 01 Lecture Planning | Step-by-Step | 단일 실행 (세션 없음) | 9 steps × (START+END) |
| 02 Material Writing | Step-by-Step | 일자별 AM/PM 분할 가능 | 11 agents × (START+END) |
| 03 Slide Generation | Session-Parallel | Day{N}_{AM/PM} 세션 단위 | N × (SESSION_START+SESSION_END) |
| 04 SlidePrompt Generation | Session-Parallel | Day{N}_{AM/PM} 세션 단위 | N × (SESSION_START+SESSION_END) |
| 05 PPTX Conversion | Step-by-Step | 세션별 개별 실행 | 6 steps × (START+END) |
| 06 NanoBanana PPTX | Step-by-Step | 세션별 개별 실행 | 6 steps × (START+END) |
| 07 Manus Slide | Step-by-Step | 세션별 순차 처리 | 6 steps × (START+END) |
| 08 Log Analysis | Step-by-Step | 단일 실행 | 6 steps × (START+END) |

> **Note**: 기본 모델은 권장 사항이며, 실행 상황에 따라 다른 모델이 사용될 수 있습니다 (§9.0 혼합 모델 참조).
