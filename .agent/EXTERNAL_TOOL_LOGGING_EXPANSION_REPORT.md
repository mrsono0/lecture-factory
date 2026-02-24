# EXTERNAL_TOOL 로깅 확장 적용 완료 보고서

> **작성일**: 2026-02-24  
> **적용 범위**: 01_Lecture_Planning → 07_Manus_Slide (전 파이프라인)  
> **상태**: ✅ 완료

---

## 1. 개요

기존에 01_Lecture_Planning의 A1_Trend_Researcher에만 적용되었던 NotebookLM 쿼리 로깅을 **전체 Lecture Factory 파이프라인으로 확장**했습니다.

### 확장 적용 도구

| 도구 유형 | 도구명 | 사용 파이프라인 |
|-----------|--------|----------------|
| 소스 리서치 | NotebookLM | 01, 02 |
| 소스 리서치 | Deep Research | 01, 02 |
| 소스 리서치 | Context7 | 02 |
| 소스 리서치 | Firecrawl | 02 |
| 파일 처리 | pdf-official | 01, 02 |
| 이미지 생성 | Gemini API | 06 |
| PPTX 생성 | Manus AI API | 07 |

---

## 2. 적용된 에이전트 목록

### 01_Lecture_Planning (Planner)
| 에이전트 | 도구 | 로깅 섹션 추가 |
|----------|------|---------------|
| A0_Orchestrator | pdf-official | ✅ |
| A1_Trend_Researcher | notebooklm, deep-research | ✅ (기존) |

### 02_Material_Writing (Writer)
| 에이전트 | 도구 | 로깅 섹션 추가 |
|----------|------|---------------|
| A0_Orchestrator | pdf-official | ✅ |
| A1_Source_Miner | notebooklm, deep-research, context7, firecrawl, pdf-official | ✅ |

### 06_NanoBanana_PPTX (NanoBanana)
| 에이전트 | 도구 | 로깅 섹션 추가 |
|----------|------|---------------|
| C3_Image_Generator | Gemini API (gemini-3-pro-image-preview) | ✅ |

### 07_Manus_Slide (Manus)
| 에이전트 | 도구 | 로깅 섹션 추가 |
|----------|------|---------------|
| D3_Submission_Manager | Manus AI API (create_project, upload_file, create_task) | ✅ |

---

## 3. 수정된 파일 목록

### 에이전트 문서 (Agent Prompts)
| 파일 경로 | 변경 내용 |
|-----------|----------|
| `.agent/agents/01_planner/A0_Orchestrator.md` | pdf-official 로깅 섹션 추가 |
| `.agent/agents/01_planner/A1_Trend_Researcher.md` | NotebookLM 로깅 섹션 (기존) |
| `.agent/agents/02_writer/A0_Orchestrator.md` | pdf-official 로깅 섹션 추가 |
| `.agent/agents/02_writer/A1_Source_Miner.md` | 5가지 도구 로깅 섹션 추가 |
| `.agent/agents/06_nanopptx/C3_Image_Generator.md` | Gemini API 로깅 섹션 추가 |
| `.agent/agents/07_manus_slide/D3_Submission_Manager.md` | Manus AI API 로깅 섹션 추가 |

### 워크플로우 YAML
| 파일 경로 | 변경 내용 |
|-----------|----------|
| `.agent/workflows/01_Lecture_Planning.yaml` | step_1_trend_analysis에 로깅 note 추가 |
| `.agent/workflows/02_Material_Writing.yaml` | step_1_source_mining에 로깅 note 추가 |
| `.agent/workflows/06_NanoBanana_PPTX.yaml` | step_5_image_generation에 로깅 note 추가 |
| `.agent/workflows/07_Manus_Slide.yaml` | step_4_manus_submission에 로깅 note 추가 |

### 프로토콜 문서
| 파일 경로 | 변경 내용 |
|-----------|----------|
| `.agent/logging-protocol.md` | EXTERNAL_TOOL 이벤트 유형, 필드 정의, 구현 가이드(§9.7) 추가 |

---

## 4. 로깅 이벤트 스키마

### EXTERNAL_TOOL_START
```json
{
  "run_id": "run_YYYYMMDD_HHMMSS",
  "ts": "2026-02-24T20:50:01+09:00",
  "status": "EXTERNAL_TOOL_START",
  "workflow": "01_Lecture_Planning|02_Material_Writing|06_NanoBanana_PPTX|07_Manus_Slide",
  "step_id": "step_X_name",
  "agent": "Agent_Name",
  "category": "deep|unspecified-low|visual-engineering|quick",
  "model": "anthropic/claude-opus-4-6|...",
  "action": "tool_action",
  "tool_name": "notebooklm|deep-research|context7|firecrawl|pdf-official|gemini-api|manus-ai",
  "tool_action": "ask_question|research|auto_research|scrape|extract|generate_image|create_project|upload_file|create_task",
  "tool_input_bytes": 1234,
  "notebook_id": "optional-for-notebooklm",
  "retry": 0
}
```

### EXTERNAL_TOOL_END
```json
{
  "run_id": "run_YYYYMMDD_HHMMSS",
  "ts": "2026-02-24T20:50:15+09:00",
  "status": "EXTERNAL_TOOL_END",
  "workflow": "...",
  "step_id": "...",
  "agent": "...",
  "category": "...",
  "model": "...",
  "action": "...",
  "tool_name": "...",
  "tool_action": "...",
  "tool_input_bytes": 1234,
  "tool_output_bytes": 5678,
  "tool_duration_sec": 14.2,
  "tool_status": "success|timeout|error",
  "tool_error": "optional error message",
  "notebook_id": "optional",
  "retry": 0
}
```

---

## 5. 분석 쿼리 예시

### 5.1 외부 도구별 총 호출 횟수
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({tool: .[0].tool_name, total_calls: length})
  | sort_by(-.total_calls)
'
```

### 5.2 외부 도구별 성공률
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({
      tool: .[0].tool_name,
      total: length,
      success: map(select(.tool_status=="success")) | length,
      timeout: map(select(.tool_status=="timeout")) | length,
      error: map(select(.tool_status=="error")) | length,
      success_rate: (map(select(.tool_status=="success")) | length) / length * 100
    })
'
```

### 5.3 파이프라인별 외부 도구 소요시간
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.workflow)
  | map({
      workflow: .[0].workflow,
      total_duration_sec: map(.tool_duration_sec) | add,
      avg_duration_sec: (map(.tool_duration_sec) | add) / length,
      total_calls: length
    })
  | sort_by(-.total_duration_sec)
'
```

### 5.4 Gemini API 이미지 생성 통계 (NanoBanana)
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END" and .tool_name=="gemini-api"))
  | {
      total_images: length,
      total_generation_time_sec: map(.tool_duration_sec) | add,
      avg_generation_time_sec: (map(.tool_duration_sec) | add) / length,
      total_output_bytes: map(.tool_output_bytes) | add,
      avg_output_bytes: (map(.tool_output_bytes) | add) / length
    }
'
```

### 5.5 Manus AI API 호출 패턴 (Manus Slide)
```bash
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END" and .tool_name=="manus-ai"))
  | group_by(.tool_action)
  | map({
      action: .[0].tool_action,
      total_calls: length,
      avg_duration_sec: (map(.tool_duration_sec) | add) / length,
      total_input_bytes: map(.tool_input_bytes) | add
    })
'
```

---

## 6. 검증 체크리스트

- [x] 01_Lecture_Planning: A0_Orchestrator (pdf-official)
- [x] 01_Lecture_Planning: A1_Trend_Researcher (notebooklm, deep-research)
- [x] 02_Material_Writing: A0_Orchestrator (pdf-official)
- [x] 02_Material_Writing: A1_Source_Miner (5가지 도구)
- [x] 06_NanoBanana_PPTX: C3_Image_Generator (Gemini API)
- [x] 07_Manus_Slide: D3_Submission_Manager (Manus AI API)
- [x] logging-protocol.md: EXTERNAL_TOOL 이벤트/필드/구현가이드 추가
- [x] 워크플로우 YAML: 4개 파일에 로깅 note 추가

---

## 7. 다음 단계 (운영 가이드)

### 7.1 즉시 적용
- 변경사항은 이미 파일에 반영됨
- 다음 파이프라인 실행부터 자동 적용

### 7.2 로그 분석 자동화 권장
`.agent/scripts/`에 다음 분석 스크립트 추가 권장:
- `analyze_external_tools.sh`: 외부 도구별 호출 통계
- `analyze_api_costs.sh`: API 호출 비용 추정
- `detect_tool_failures.sh`: 외부 도구 실패 패턴 감지

### 7.3 모니터링 대시보드
`.agent/dashboard/`에 외부 도구 메트릭 추가:
- 일별 API 호출 횟수 추이
- 도구별 평균 응답 시간
- 에러율 알림 (임계값: >5%)

---

## 8. 요약

**모든 외부 도구 호출이 이제 추적 가능합니다.**

| 파이프라인 | 추적 대상 | 비용 분석 가능 |
|-----------|----------|--------------|
| 01 | NotebookLM, Deep Research, PDF | ✅ |
| 02 | NotebookLM, Deep Research, Context7, Firecrawl, PDF | ✅ |
| 06 | Gemini API 이미지 생성 | ✅ |
| 07 | Manus AI API (프로젝트, 업로드, 태스크) | ✅ |

**기대 효과**:
1. 트러블슈팅: "어느 API 호출이 실패했는가?" 즉시 파악
2. 비용 최적화: 도구별 사용량 및 소요시간 분석
3. 품질 관리: 외부 도구 성공률 모니터링
4. 용량 계획: API 호출 패턴 기반 리소스 예측

---

*작성 완료: 2026-02-24*  
*총 수정 파일: 11개*  
*적용 에이전트: 7개*
