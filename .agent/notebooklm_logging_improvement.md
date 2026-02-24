# NotebookLM 쿼리 로깅 개선안 — 검토 완료

> **작성일**: 2026-02-24  
> **run_id**: run_20260224_204705  
> **상태**: ✅ 구현 완료, 적용 대기

---

## 1. 문제 정의

### 현재 상황
- NotebookLM 쿼리 실행 시 **에이전트 단위로만 로깅** (START/END)
- 개별 NotebookLM 쿼리의 실행 이력, 소요시간, 응답 크기 등이 **누락**
- 트러블슈팅 시 "어떤 쿼리가 실패했는가?" 파악 어려움

### 목표
- **모든 NotebookLM 쿼리**를 별도 로그 이벤트로 기록
- 쿼리별 **소요시간, 응답 크기, 성공/실패 상태** 추적
- **Notebook ID별** 실행 이력 집계 가능

---

## 2. 개선 내용

### 2.1 로깅 프로토콜 확장 (logging-protocol.md)

#### 새로운 이벤트 유형 추가
| 이벤트 | 설명 | 발생 시점 |
|--------|------|----------|
| `EXTERNAL_TOOL_START` | 외부 도구/API 호출 시작 | 도구 호출 직전 |
| `EXTERNAL_TOOL_END` | 외부 도구/API 호출 완료 | 도구 응답 수신 후 |

#### 새로운 필드 정의 (§3.5)
| 필드 | 타입 | 설명 |
|------|------|------|
| `tool_name` | string | 도구/서비스명 ("notebooklm", "tavily-web" 등) |
| `tool_action` | string | 도구 내 액션 ("ask_question", "search" 등) |
| `tool_input_bytes` | number | 입력 데이터 크기 (bytes) |
| `tool_output_bytes` | number | 응답 데이터 크기 (bytes) |
| `tool_duration_sec` | number | 도구 호출 소요 시간 |
| `tool_status` | string | "success" / "timeout" / "error" |
| `tool_error` | string | 오류 메시지 (실패 시) |
| `notebook_id` | string | NotebookLM 사용 시 노트북 ID |

#### 구현 가이드 추가 (§9.7)
- 외부 도구 호출 로깅 타이밍 및 예시 코드
- jq 분석 쿼리 예시 (NotebookLM 쿼리별 소요시간, 성공률 등)

### 2.2 A1_Trend_Researcher 에이전트 업데이트

#### 새로운 섹션 추가: "NotebookLM 쿼리 로깅 (MANDATORY)"

**START 로그 (쿼리 실행 전)**:
```bash
echo '{"run_id":"[run_id]","ts":"[ISO8601]","status":"EXTERNAL_TOOL_START",
  "workflow":"01_Lecture_Planning","step_id":"step_1_trend_analysis",
  "agent":"A1_Trend_Researcher","category":"deep","model":"[model]",
  "action":"notebooklm_query","tool_name":"notebooklm",
  "tool_action":"ask_question","tool_input_bytes":0,
  "notebook_id":"[notebook_id]","retry":0}' >> ".agent/logs/[DATE]_01_Lecture_Planning.jsonl"
```

**END 로그 (쿼리 완료 후)**:
```bash
echo '{"run_id":"[run_id]","ts":"[ISO8601]","status":"EXTERNAL_TOOL_END",
  ...,
  "tool_output_bytes":0,"tool_duration_sec":0,"tool_status":"success",
  "notebook_id":"[notebook_id]","retry":0}' >> ".agent/logs/[DATE]_01_Lecture_Planning.jsonl"
```

**검증 체크포인트**:
| # | 검증 항목 |
|---|----------|
| 1 | EXTERNAL_TOOL_START 각 쿼리 직전에 기록 |
| 2 | EXTERNAL_TOOL_END 각 쿼리 완료 후 기록 |
| 3 | notebook_id 필드 포함 |
| 4 | tool_status 정확히 기록 |

**미준수 시**: A0가 "NotebookLM 쿼리 로깅 누락"으로 반려

### 2.3 워크플로우 YAML 업데이트

`01_Lecture_Planning.yaml`의 step_1_trend_analysis notes에 추가:
```yaml
📊 External Tool Logging: A1 must log each NotebookLM query to 
    .agent/logs/{DATE}_01_Lecture_Planning.jsonl using 
    EXTERNAL_TOOL_START/END events (see logging-protocol.md §9.7)
```

---

## 3. 예상 로그 출력 예시

### 단일 NotebookLM 쿼리 실행 시
```jsonl
{"run_id":"run_20260224_204705","ts":"2026-02-24T20:50:01","status":"EXTERNAL_TOOL_START","workflow":"01_Lecture_Planning","step_id":"step_1_trend_analysis","agent":"A1_Trend_Researcher","category":"deep","model":"anthropic/claude-opus-4-6","action":"notebooklm_query","tool_name":"notebooklm","tool_action":"ask_question","tool_input_bytes":45,"notebook_id":"28d70970-864a-485b-82e9-ebdd7c233c9a","retry":0}
{"run_id":"run_20260224_204705","ts":"2026-02-24T20:50:15","status":"EXTERNAL_TOOL_END","workflow":"01_Lecture_Planning","step_id":"step_1_trend_analysis","agent":"A1_Trend_Researcher","category":"deep","model":"anthropic/claude-opus-4-6","action":"notebooklm_query","tool_name":"notebooklm","tool_action":"ask_question","tool_input_bytes":45,"tool_output_bytes":3200,"tool_duration_sec":14.2,"tool_status":"success","notebook_id":"28d70970-864a-485b-82e9-ebdd7c233c9a","retry":0}
```

---

## 4. 분석 쿼리 예시

### NotebookLM 쿼리별 소요시간 TOP 5
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END" and .tool_name=="notebooklm"))
  | sort_by(-.tool_duration_sec)
  | .[0:5]
  | .[] | {notebook_id, tool_action, tool_duration_sec, tool_output_bytes}
'
```

### NotebookLM 쿼리 성공률
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END" and .tool_name=="notebooklm"))
  | {total: length, success: map(select(.tool_status=="success")) | length}
'
```

---

## 5. 수정된 파일 목록

| 파일 | 변경 유형 | 설명 |
|------|----------|------|
| `.agent/logging-protocol.md` | 추가 | EXTERNAL_TOOL 이벤트 유형, 필드 정의, 구현 가이드 |
| `.agent/agents/01_planner/A1_Trend_Researcher.md` | 추가 | NotebookLM 쿼리 로깅 섹션 |
| `.agent/workflows/01_Lecture_Planning.yaml` | 추가 | External Tool Logging note |

---

## 6. 다음 단계 (적용 방법)

### 6.1 즉시 적용 (신규 실행부터)
- 변경사항은 이미 파일에 반영됨
- 다음 01_Lecture_Planning 실행부터 자동 적용

### 6.2 기존 A1_Trend_Researcher 에이전트에게 알림
- 이미 위임된 작업이 있다면 세션 ID로 재실행 권장
- 또는 다음 실행부터 자동 적용

### 6.3 확장 적용 (다른 에이전트)
다음 에이전트들에도 동일한 패턴 적용 권장:
- `tavily-web` 사용 에이전트
- `pdf-official` 사용 에이전트  
- `deep-research` 사용 에이전트
- API 호출이 있는 모든 에이전트

---

## 7. 검증 체크리스트

- [x] 로깅 프로토콜에 EXTERNAL_TOOL 이벤트 유형 추가
- [x] EXTERNAL_TOOL 전용 필드 정의 (§3.5)
- [x] 외부 도구 로깅 구현 가이드 추가 (§9.7)
- [x] A1_Trend_Researcher 에이전트에 로깅 섹션 추가
- [x] 워크플로우 YAML에 로깅 note 추가
- [x] 분석 쿼리 예시 제공

---

**결론**: NotebookLM 쿼리별 상세 로깅 체계가 구축되었습니다. 각 쿼리의 소요시간, 응답 크기, 성공/실패 상태를 추적하여 트러블슈팅 및 비용 분석이 가능해집니다.
