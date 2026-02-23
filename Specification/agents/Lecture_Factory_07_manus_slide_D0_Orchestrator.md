# D0_Orchestrator — 에이전트 상세 설계 명세서 (SDD)

> **문서 버전**: 1.1
> **작성일**: 2026-02-23
> **상위 문서**: `Lecture_Factory_Specification.md`
> **소스 프롬프트**: `.agent/agents/07_manus_slide/D0_Orchestrator.md` (117 lines)
> **바운디드 컨텍스트**: Pipeline 07 — Manus Slide Generation

---

## 1. 에이전트 개요

| 항목 | 값 |
|---|---|
| **에이전트 ID** | `D0_Orchestrator` |
| **역할명** | Manus Slide 오케스트레이터 |
| **소속 팀** | `07_manus_slide` (Manus Slide 생성 팀) |
| **LLM 카테고리** | `unspecified-low` (config.json 오버라이드) |
| **기대 모델 등급** | Haiku급 |
| **워크플로우 스텝** | `step_1_input_discovery`, `step_7_approval`, `step_8_finalize` (3개 스텝 담당) |
| **실행 모델** | Step-by-Step (순차 실행) |
| **핵심 한줄 요약** | P04 슬라이드 프롬프트를 입력으로 받아 파일 업로드 모드(Project instruction + Files API)로 공통 헤더 중복을 제거하고, D1→D2→D3→D4→D5 파이프라인을 지휘하며, QA 게이트(승인/재제출/반려) 판단 및 최종 산출물을 확정하는 프로젝트 관리자 |

---

## 2. 파이프라인 내 위치

```
       ┌──────────────────────────────────────────────────────────┐
       │              ★ D0_Orchestrator                           │
       │        (진입점 + QA 게이트 + 최종 확정)                    │
       └──────┬──────────────────────────────────────┬────────────┘
              │ step_1                                │ step_7/8
              ▼                                       │
     [D1_Prompt_Validator] ─ step_2                   │
              │                                       │
              ▼                                       │
     [D2_Chunk_Splitter] ─ step_3                     │
              │                                       │
              ▼                                       │
     [D3_Submission_Manager] ─ step_4  ◄──────────────┤ (재제출)
              │                                       │
              ▼                                       │
     [D4_Post_Processor] ─ step_5                     │
              │                                       │
              ▼                                       │
     [D5_Visual_QA] ─ step_6 ─────────────────────────┘
```

**위치 특성**: 듀얼 진입/종료점 오케스트레이터. step_1에서 입력을 탐색하고 파이프라인을 시작, step_7에서 QA 결과를 판정(3-outcome gate), step_8에서 최종 산출물을 확정한다.

---

## 3. 인터페이스 설계

### 3.1 입력 (Input)

| # | 입력 항목 | 소스 | 형식 | 필수 여부 |
|---|---|---|---|---|
| 1 | P04 슬라이드 프롬프트 파일(N개) | Pipeline 04 산출물 | `04_SlidePrompt/*슬라이드 생성 프롬프트.md` | 필수 |
| 2 | `MANUS_API_KEY` | 환경변수 | API Key 문자열 | 필수 |
| 3 | 프로젝트 폴더 경로 | 사용자 또는 자동 탐색 | 파일 시스템 경로 | 필수 |
| 4 | 교안 원문 (선택) | Pipeline 02 산출물 | `02_Material/*.md` | 선택 (D5 대조 검증용) |
| 5 | `--no-upload` CLI 옵션 | CLI 파라미터 | boolean 플래그 | 선택 (파일 업로드 모드 비활성화) |

### 3.2 출력 (Output)

| # | 산출물 | 경로 | 형식 | 설명 |
|---|---|---|---|---|
| 1 | **최종 PPTX 파일(N개)** | `07_ManusSlides/{세션ID}_{세션제목}.pptx` | `.pptx` | 프롬프트 파일당 1개 |
| 2 | **실행 로그** | `07_ManusSlides/manus_task_log.json` | JSON | task_id, 상태, 소요 시간 |
| 3 | **생성 리포트** | `07_ManusSlides/generation_report.json` | JSON | 성공/실패/재시도 현황 + `upload_mode`, `project_id` 필드 |
| 4 | **발표자 노트** | `07_ManusSlides/slide_notes.md` | Markdown | Manus 생성 노트 (선택) |
| 5 | **입력 매니페스트** | 내부 전달 | Markdown | 파일 목록 + 줄 수 + 슬라이드 수 |

### 3.3 하류 전파

| 하류 에이전트 | 전달 내용 | 용도 |
|---|---|---|
| `D1_Prompt_Validator` | 입력 매니페스트 + 프롬프트 파일 | 6-섹션 구조 검증 |
| `D2_Chunk_Splitter` | 검증 통과 파일 목록 | 교시 단위 분할 |
| `D3_Submission_Manager` | 재제출 지시 (step_7 partial_resubmit) + `project_id`, `file_ids` | 특정 청크 재제출 (파일 업로드 모드 시 프로젝트 컨텍스트 전달) |

---

## 4. 처리 로직

### 4.1 전체 흐름도

```
┌──────────────────────────────────────────────────────┐
│                D0_Orchestrator                        │
│                                                      │
│  Phase 1: 입력 탐색 (step_1_input_discovery)          │
│     ├─ 04_SlidePrompt/ 폴더 스캔                      │
│     ├─ *슬라이드 생성 프롬프트.md 파일 목록 수집          │
│     ├─ 파일명에서 세션 ID 추출 (Day{N}_{AM|PM})         │
│     ├─ Day→AM/PM→교시 순 정렬                          │
│     ├─ 파일별 줄 수 + 슬라이드 수 집계                   │
│     ├─ MANUS_API_KEY 유효성 확인                       │
│     └─ 매니페스트 생성 → D1 전달                        │
│                                                      │
│  Phase 1.5: 파일 업로드 설정 (기본 활성)                │
│     ├─ setup_project_with_files() 호출                 │
│     ├─ SLIDE_GENERATION_PREFIX → Project instruction   │
│     ├─ 공통 헤더(①②④⑤) → Files API 업로드            │
│     ├─ project_id + file_ids 획득                      │
│     └─ 실패 시 → 기존 인라인 방식으로 자동 폴백          │
│                                                      │
│  (D1→D2→D3→D4→D5 순차 실행)                           │
│                                                      │
│  Phase 4: QA 게이트 (step_7_approval)                 │
│     ├─ D5 QA 리포트 수신                               │
│     ├─ FAIL/WARN 카운트 분석                           │
│     └─ 판정:                                          │
│         ├─ PASS → step_8_finalize                     │
│         ├─ PARTIAL_REDO → step_4 (해당 청크 재제출)     │
│         └─ REJECT → step_3 (분할 전략 재실행, ≤2회)     │
│                                                      │
│  Phase 5: 최종 확정 (step_8_finalize)                  │
│     ├─ PPTX 파일명 규칙 적용                            │
│     ├─ generation_report.json 작성                     │
│     ├─ manus_task_log.json 정리                        │
│     └─ 프로젝트 폴더 정리                               │
└──────────────────────────────────────────────────────┘
```

### 4.2 의사코드 — 동적 입력 탐색

```
FUNCTION discover_inputs(project_folder):
  // ① 프롬프트 파일 탐색
  prompt_dir ← "{project_folder}/04_SlidePrompt/"
  files ← glob("{prompt_dir}/*슬라이드 생성 프롬프트.md")
  
  IF files.length == 0:
    ABORT "04_SlidePrompt/에 프롬프트 파일이 없습니다."
  END IF
  
  // ② 파일별 메타데이터 수집
  manifest ← []
  FOR each file IN files:
    session_id ← extract_session_id(file.name)  // Day{N}_{AM|PM}
    line_count ← count_lines(file)
    slide_count ← count_pattern(file, "[슬라이드 NN]")
    needs_split ← (line_count > 1000) OR (slide_count > 35)
    
    manifest.add({
      file: file.name,
      session_id: session_id,
      lines: line_count,
      slides: slide_count,
      split_required: needs_split
    })
  END FOR
  
  // ③ 정렬: Day → AM/PM → 교시 순
  manifest.sort_by(session_id)
  
  // ④ MANUS_API_KEY 확인
  ASSERT env("MANUS_API_KEY") != null, "MANUS_API_KEY 미설정"
  
  // ⑤ 사용자 확인
  PRESENT manifest TO user
  AWAIT user confirmation
  
  RETURN manifest
END FUNCTION
```

### 4.3 의사코드 — QA 게이트

```
FUNCTION review_and_decide(qa_report, post_report):
  fail_count ← qa_report.total_fails
  warn_count ← qa_report.total_warns
  
  IF fail_count == 0 AND warn_count <= 3:
    RETURN "approved" → step_8_finalize
  ELSE IF fail_count <= 2:
    // 특정 청크만 문제 → 해당 청크 재제출
    failed_chunks ← qa_report.get_failed_chunks()
    RETURN "partial_resubmit" → step_4 (failed_chunks)
  ELSE:
    // 전체 문제 → 분할 전략 재실행 (최대 2회)
    IF retry_count < 2:
      RETURN "rejected" → step_3
    ELSE:
      ESCALATE to user "재시도 한도 초과. 수동 확인 필요."
    END IF
  END IF
END FUNCTION
```

### 4.4 비용 관리 로직

```
FUNCTION estimate_cost(manifest):
  total_chunks ← 0
  FOR each entry IN manifest:
    IF entry.split_required:
      IF entry.lines <= 1500:
        total_chunks += 2
      ELSE:
        total_chunks += ceiling(entry.lines / 500)  // 3~4분할
      END IF
    ELSE:
      total_chunks += 1
    END IF
  END FOR
  
  estimated_api_calls ← total_chunks
  estimated_time_min ← total_chunks × 8  // 평균 8분/청크
  
  LOG "예상 API 호출: {estimated_api_calls}회"
  LOG "예상 소요 시간: {estimated_time_min}분"
  LOG "일일 Nano Banana Pro 이미지 한도 고려: ~35장/세션"
  
  RETURN { calls: total_chunks, time: estimated_time_min }
END FUNCTION
```

### 4.5 의사코드 — 파일 업로드 설정

```
FUNCTION setup_file_upload(project_folder, prompts, use_upload):
  IF NOT use_upload:
    LOG "파일 업로드 모드 비활성 (--no-upload)"
    RETURN { project_id: null, file_ids: null, use_upload: false }
  END IF

  TRY:
    // ① 프로젝트 생성 (SLIDE_GENERATION_PREFIX를 instruction으로)
    project_id ← create_project(session, "slide_gen_{timestamp}", SLIDE_GENERATION_PREFIX)
    
    // ② 공통 헤더(①②④⑤) 추출 + 임시 파일 저장
    common_header ← extract_common_header(prompts[0])
    header_file ← save_temp_file(project_folder, "common_header.md", common_header)
    
    // ③ Files API로 업로드
    file_id ← upload_file(session, header_file)
    file_ids_map ← { "common_header": file_id }
    
    LOG "파일 업로드 모드 활성: project_id={project_id}"
    RETURN { project_id, file_ids: file_ids_map, use_upload: true }
    
  CATCH Error:
    WARN "파일 업로드 실패, 기존 방식으로 폴백: {error}"
    RETURN { project_id: null, file_ids: null, use_upload: false }
  END TRY
END FUNCTION
```

---

## 5. 의존성

### 5.1 업스트림 의존성

| 소스 | 제공 데이터 | 의존 강도 |
|---|---|---|
| Pipeline 04 (04_prompt_generator) | 슬라이드 프롬프트 파일(N개) | **강** — 입력 없으면 파이프라인 불가 |
| Pipeline 02 (02_writer) | 교안 원문(선택) | **약** — D5 대조 검증용 |
| 환경변수 `MANUS_API_KEY` | Manus AI API 인증 | **강** — 필수 |

### 5.2 다운스트림 의존성

| 대상 에이전트 | 전달 데이터 | 의존 강도 |
|---|---|---|
| `D1_Prompt_Validator` | 입력 매니페스트 | **강** — 첫 번째 하류 |
| `D3_Submission_Manager` | 재제출 지시 + `project_id`, `file_ids` | **조건부** — partial_resubmit 시 |

### 5.3 스킬 의존성

해당 없음 (D0는 조율 역할, 도구 직접 사용 없음).

### 5.4 시스템 의존성

| 시스템 | 용도 | 필수 여부 |
|---|---|---|
| `MANUS_API_KEY` | Manus AI API 인증 | 필수 |
| 파일 시스템 | 04_SlidePrompt/ 탐색, 07_ManusSlides/ 생성 | 필수 |
| Manus Projects API | 프로젝트 생성 + instruction 설정 | 선택 (파일 업로드 모드) |
| Manus Files API | 공통 헤더 파일 업로드 | 선택 (파일 업로드 모드) |

---

## 6. 도메인 모델

### 6.1 엔티티 (Entities)

```
┌──────────────────────────────┐
│      PipelineExecution        │
├──────────────────────────────┤
│ project_folder: string        │
│ manifest: InputManifest       │
│ phase: Phase                  │
│ retry_count: number           │
│ qa_verdict: Verdict           │
│ start_time: ISO8601           │
│ end_time: ISO8601             │
│ upload_mode: boolean          │
│ project_id: string?           │
│ file_ids_map: Map<string,string>? │
└──────────┬───────────────────┘
           │ 1:N
           ▼
┌──────────────────────────────┐
│      ManifestEntry            │
├──────────────────────────────┤
│ file_name: string             │
│ session_id: string            │
│ line_count: number            │
│ slide_count: number           │
│ split_required: boolean       │
│ chunk_count: number           │
│ status: EntryStatus           │
└──────────────────────────────┘
```

### 6.2 값 객체 (Value Objects)

```
┌──────────────────────────────┐
│         Phase                 │
├──────────────────────────────┤
│ DISCOVERY: 입력 탐색           │
│ FILE_UPLOAD: 파일 업로드 설정   │
│ VALIDATION: D1 검증            │
│ SPLITTING: D2 분할             │
│ SUBMISSION: D3 제출            │
│ POST_PROCESSING: D4 후처리     │
│ QA: D5 품질 검증               │
│ APPROVAL: QA 게이트            │
│ FINALIZE: 최종 확정            │
└──────────────────────────────┘

┌──────────────────────────────┐
│         Verdict               │
├──────────────────────────────┤
│ approved: 최종 승인            │
│ partial_resubmit: 부분 재제출  │
│ rejected: 전체 반려            │
└──────────────────────────────┘

┌──────────────────────────────┐
│       GenerationReport        │
├──────────────────────────────┤
│ total_files: number           │
│ total_chunks: number          │
│ success_count: number         │
│ failure_count: number         │
│ retry_count: number           │
│ total_elapsed_min: number     │
│ split_merge_history: object[] │
│ upload_mode: boolean          │
│ project_id: string?           │
└──────────────────────────────┘
```

---

## 7. 상태 전이

```
     ┌────────────────┐
     │   IDLE          │
     └───────┬────────┘
             │ 입력 폴더 지정
             ▼
     ┌────────────────┐
     │  DISCOVERY      │ ← step_1
     └───────┬────────┘
             │ 매니페스트 생성
             ▼
     ┌────────────────┐
     │  FILE_UPLOAD    │ ← Phase 1.5 (기본 활성)
     └───────┬────────┘
             │ project_id + file_ids 획득 (또는 폴백)
             ▼
     ┌────────────────┐
     │  VALIDATION     │ ← D1 실행
     └───────┬────────┘
             │
     ┌───────┴────────┐
     │                │
   PASS            REJECT (⑥ 누락)
     │                │
     ▼                ▼
  ┌──────────┐   ┌──────────┐
  │ SPLITTING │   │ ABORTED  │
  └─────┬────┘   └──────────┘
        │ D2 완료
        ▼
  ┌──────────┐
  │SUBMISSION│ ← D3 실행
  └─────┬────┘
        │ 다운로드 완료
        ▼
  ┌──────────────┐
  │POST_PROCESS  │ ← D4 실행
  └─────┬────────┘
        │ 병합 완료
        ▼
  ┌──────────┐
  │ QA       │ ← D5 실행
  └─────┬────┘
        │ 리포트 수신
        ▼
  ┌──────────┐
  │ APPROVAL │ ← step_7
  └─────┬────┘
     ┌──┼──────────┐
     │  │          │
  approved partial  rejected
     │  resubmit   │
     ▼     │       ▼
  ┌──────┐ │  ┌──────────┐
  │FINAL │ │  │SPLITTING │ (≤2회)
  └──────┘ │  └──────────┘
           ▼
     ┌──────────┐
     │SUBMISSION│ (해당 청크만)
     └──────────┘
```

---

## 8. 오류 처리

| # | 오류 상황 | 감지 방법 | 처리 전략 | 에스컬레이션 |
|---|---|---|---|---|
| E1 | 04_SlidePrompt/ 폴더 없음 | 디렉토리 존재 확인 | 프로젝트 루트 최신 날짜 폴더 자동 탐색 | 사용자에게 경로 확인 |
| E2 | 프롬프트 파일 0개 | glob 결과 확인 | ABORT + 에러 메시지 | 사용자 알림 |
| E3 | MANUS_API_KEY 미설정 | env 확인 | `.claude/.env` 대체 확인 → 실패 시 ABORT | 사용자 알림 |
| E4 | D1 REJECT (⑥ 교안 원문 누락) | 검증 리포트 | 해당 파일 제외, 사용자 알림 | P04 재실행 안내 |
| E5 | 재제출 한도 초과 (2회) | retry_count 추적 | 사용자 에스컬레이션 | 수동 확인 안내 |
| E6 | 전체 파일 실패 | 성공 카운트 0 | ABORT + 전체 실패 보고 | 사용자 에스컬레이션 |
| E7 | 파일 업로드 모드 실패 | `setup_project_with_files()` 예외 | 경고 로그 + 기존 인라인 방식으로 자동 폴백 | 폴백 성공 시 없음 |

---

## 9. 품질 기준

### 9.1 파이프라인 관리 품질

| 기준 | 충족 조건 | 검증 방법 |
|---|---|---|
| **입력 완전성** | 모든 프롬프트 파일 탐색 완료 | 매니페스트 파일 수 = 실제 파일 수 |
| **순서 정확** | Day→AM/PM→교시 순 정렬 | 매니페스트 순서 확인 |
| **비용 최소화** | 1,000줄 이하 원샷, 분할 최소화 | 분할 매니페스트 검토 |
| **QA 게이트 정확** | FAIL/WARN 기반 판정 정확 | QA 리포트 vs 판정 일치 |
| **진행 보고** | 각 Phase 완료 시 사용자 보고 | 보고 로그 확인 |
| **파일 업로드 폴백** | 업로드 실패 시 기존 방식 자동 전환 | 폴백 경고 로그 확인 |

### 9.2 산출물 품질

| 기준 | 충족 조건 |
|---|---|
| **파일명 규칙** | `{세션ID}_{세션제목}.pptx` 형식 준수 |
| **리포트 완전성** | generation_report.json에 성공/실패/재시도 현황 + `upload_mode`, `project_id` 포함 |
| **로그 완전성** | manus_task_log.json에 모든 task_id 기록 |

---

## 10. 로깅

### 10.1 이벤트 목록

| 이벤트 | 시점 | 필수 필드 |
|---|---|---|
| `START` | step_1/7/8 시작 | `agent_id`, `step_id`, `timestamp`, `input_summary` |
| `DECISION` | step_7 판정 | `decision_type: "qa_gate"`, `verdict`, `fail_count`, `warn_count` |
| `END` | step_1/7/8 완료 | `agent_id`, `step_id`, `timestamp`, `output_summary`, `est_tokens` |
| `FAIL` | 파이프라인 실패 | `agent_id`, `step_id`, `error_type`, `error_message` |
| `SESSION_START` | 세션 병렬 위임 시 | `session_id`, `session_name` |
| `SESSION_END` | 세션 처리 완료 | `duration_sec`, `output_files`, `total_slides` |

### 10.2 비용 산정 공식

D0는 `unspecified-low` 카테고리 (Haiku급):

```
est_tokens = round(bytes ÷ 3.3)
cost_input  = est_tokens × $0.003 / 1000
cost_output = est_tokens × $0.015 / 1000
```

---

## 11. 설정

### 11.1 config.json 매핑

```jsonc
{
    "name": "07_manus_slide",
    "default_category": "quick",
    "agent_models": {
        "D0_Orchestrator": { "category": "unspecified-low", "note": "조율·입력 탐색·승인/반려 — 절차적 작업" }
    }
}
```

### 11.2 워크플로우 YAML 매핑

```yaml
# step_1_input_discovery
- id: step_1_input_discovery
  agent: "07_manus_slide/D0_Orchestrator"
  action: "discover_inputs"

# step_7_approval
- id: step_7_approval
  agent: "07_manus_slide/D0_Orchestrator"
  action: "review_and_decide"
  decision:
    approved: "step_8_finalize"
    partial_resubmit: "step_4_manus_submission (해당 청크만 재제출)"
    rejected: "step_3_chunk_splitting (최대 2회)"

# step_8_finalize
- id: step_8_finalize
  agent: "07_manus_slide/D0_Orchestrator"
  action: "finalize_output"
```

---

## 12. 확장 포인트

| # | 확장 영역 | 설명 | 구현 난이도 |
|---|---|---|---|
| EP1 | **병렬 세션 처리** | 세션별 독립 파이프라인 병렬 실행 | 보통 |
| EP2 | **비용 예산 관리** | API 호출 비용 누적 추적 + 예산 한도 설정 | 낮음 |
| EP3 | **자동 재시도 정책** | FAIL 유형별 자동 재시도 전략 세분화 | 보통 |
| EP4 | **Manus API 상태 모니터링** | API 가용성 사전 확인 + 대기열 관리 | 보통 |
| EP5 | **Pipeline 06과 통합** | NanoBanana 로컬 vs Manus 클라우드 하이브리드 | 높음 |
| EP6 | **파일 업로드 모드 (구현 완료)** | `--no-upload` 옵션으로 기존 방식 폴백 가능. 프로젝트 instruction + Files API + attachments file_id 조합으로 공통 헤더 중복 제거 | 완료 |
