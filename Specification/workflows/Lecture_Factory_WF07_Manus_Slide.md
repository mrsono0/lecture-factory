# WF07_Manus_Slide — 워크플로우 상세 설계 명세서 (SDD)

> **문서 버전**: 1.1  
> **작성일**: 2026-02-23  
> **상위 문서**: `Lecture_Factory_Specification.md` (Part IV. SDD)  
> **소스 워크플로우**: `.agent/workflows/07_Manus_Slide.yaml` (88줄, v1.1)  
> **바운디드 컨텍스트**: BC7 — Cloud AI Context (Manus AI 클라우드 렌더링)  
> **서브도메인 분류**: Generic Domain

---

## 1. 워크플로우 개요

| 항목 | 값 |
|------|-----|
| **워크플로우 ID** | `07_Manus_Slide` |
| **정식 명칭** | Manus Slide Generation Pipeline |
| **목적** | 04_SlidePrompt가 생성한 슬라이드 프롬프트를 교시 단위로 분할하여 Manus AI(Nano Banana Pro)에 제출하고, PPTX를 다운로드·병합하는 파이프라인 |
| **팀** | 07_manus_slide (Manus Slide Team — 6 agents) |
| **기본 LLM 카테고리** | `quick` |
| **실행 모델** | Step-by-Step (순차 실행) |
| **총 스텝 수** | 8 (step_1 ~ step_8) |
| **Phase 수** | 6 (Phase 1.5 추가) |
| **최대 재시도** | 2회 (step_7 반려 시 step_3부터) |
| **산출물 경로** | `{YYYY-MM-DD_강의제목}/07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개) |
| **핵심 한줄 요약** | 슬라이드 프롬프트를 교시 단위로 자동 분할하여 Manus AI 클라우드에 순차 제출하고, 다운로드된 PPTX를 병합·후처리하는 클라우드 기반 렌더링 파이프라인. 파일 업로드 모드로 공통 헤더 중복 전송 제거 지원 |

---

## 2. DDD 전략 설계 (Strategic Design)

### 2.1 바운디드 컨텍스트 매핑

```
┌─────────────────────────────────────────────────────────────────┐
│                BC7: Cloud AI Context                              │
│                                                                   │
│  유비쿼터스 언어:                                                 │
│    Prompt Chunk, Chunk Manifest, Submission Log,                  │
│    PPTX Merge, Post-Processing, Visual QA,                       │
│    Session Boundary, Nano Banana Pro, manus_slide.py              │
│                                                                   │
│  서브도메인: Generic Domain (범용 클라우드 API 렌더링)            │
│  투자 전략: 최소 투자, 기존 API 활용                             │
│  구현 전략: 트랜잭션 스크립트, 외부 API 위임                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 컨텍스트 맵 (Context Map)

| 관계 | 패턴 | 상세 |
|------|------|------|
| BC4 → BC7 | **Customer-Supplier** | BC4가 Upstream으로 슬라이드 프롬프트(6-Section 스키마)를 제공, BC7이 Downstream으로 소비 |
| BC7 → External (Manus AI) | **Open Host Service / Published Language** | Manus AI API(manus-1.6-max)에 프롬프트를 제출하고 PPTX를 수신하는 외부 서비스 연동 |
| BC7 → BC9 (Orchestration) | **Conformist** | BC7은 BC9의 워크플로우 YAML 스키마를 그대로 수용 |
| BC7 → BC8 (Observability) | **Published Language** | JSONL 로깅 프로토콜을 통한 실행 데이터 교환 |

### 2.3 서브도메인 근거

| 판별 기준 | 평가 |
|-----------|------|
| 경쟁 우위 제공 여부 | ❌ 클라우드 API 호출 래퍼로, 자체 렌더링 로직 없음 |
| 자체 개발 필요성 | ❌ Manus AI API 위임 — 핵심 렌더링은 외부 서비스 |
| 도메인 전문성 요구 | 낮음 — API 호출, 분할/병합 로직 수준 |
| 복잡도 | 중간 — 교시 분할, 순차 제출, PPTX 병합 등 조정 로직 |

---

## 3. PRD — 제품 요구사항 정의서

### 3.1 기능 요구사항 (Functional Requirements)

| ID | 요구사항 | 우선순위 | 담당 에이전트 |
|----|----------|----------|---------------|
| FR-01 | 04_SlidePrompt/ 폴더에서 프롬프트 파일을 탐색하고 입력 매니페스트를 생성한다 | P0 (필수) | D0_Orchestrator |
| FR-02 | MANUS_API_KEY 유효성을 검증한다 | P0 | D0_Orchestrator |
| FR-03 | 각 프롬프트 파일의 6개 섹션(①~⑥) 구조 완전성을 검증한다 | P0 | D1_Prompt_Validator |
| FR-04 | SLIDE_GENERATION_PREFIX 중복 삽입 여부를 체크한다 | P1 (중요) | D1_Prompt_Validator |
| FR-05 | 1,000줄 이상 또는 35슬라이드 이상인 프롬프트를 교시(세션) 경계에서 분할한다 | P0 | D2_Chunk_Splitter |
| FR-06 | 각 청크에 ①②④⑤ 공통 헤더를 복제하고, ③⑥을 세션 단위로 추출한다 | P0 | D2_Chunk_Splitter |
| FR-07 | manus_slide.py를 실행하여 각 청크를 Manus AI에 순차 제출한다 | P0 | D3_Submission_Manager |
| FR-08 | 30초 간격 폴링으로 완료를 감지하고 PPTX를 다운로드한다 | P0 | D3_Submission_Manager |
| FR-09 | 분할 제출된 청크 PPTX들을 python-pptx로 병합하여 세션별 단일 PPTX를 생성한다 | P0 | D4_Post_Processor |
| FR-10 | 헤더/풋터/페이지번호를 후처리 제거하고 발표자 노트를 추출한다 | P1 | D4_Post_Processor |
| FR-11 | 최종 PPTX의 콘텐츠 보존율, 디자인 규칙 준수, 노트 완전성을 검사한다 | P0 | D5_Visual_QA |
| FR-12 | QA 결과에 따라 승인/재제출/반려를 판정한다 | P0 | D0_Orchestrator |
| FR-13 | 최종 PPTX 파일 명명 규칙 적용 및 생성 리포트를 작성한다 | P0 | D0_Orchestrator |
| FR-14 | 파일 업로드 모드로 공통 헤더(①②④⑤)를 사전 업로드하여 청크별 중복 전송을 제거한다 | P1 (중요) | D0_Orchestrator, D3_Submission_Manager |

### 3.2 비기능 요구사항 (Non-Functional Requirements)

| ID | 카테고리 | 요구사항 | 측정 기준 |
|----|----------|----------|-----------|
| NFR-01 | 언어 | 모든 산출물은 한국어로 작성 (기술 용어 제외) | 한국어 비율 ≥ 95% |
| NFR-02 | 보안 | MANUS_API_KEY는 환경변수로만 참조, 로그에 마스킹 | API 키 노출 0건 |
| NFR-03 | 재시도 | 반려 시 최대 2회 재실행 후 에스컬레이션 | max_retries: 2 |
| NFR-04 | 추적성 | 모든 에이전트 실행을 JSONL 로그로 기록 | 로그 무결성 100% |
| NFR-05 | 안정성 | Manus AI API 제출 실패 시 1회 자동 재시도 | 단일 청크 재시도 1회 |
| NFR-06 | 호환성 | 입력은 04_SlidePrompt 6-Section 스키마를 준수해야 함 | 섹션 완전성 100% |
| NFR-07 | 분할 정책 | ≤1,000줄 원샷 / 1,000+ 교시 분할 | 분할 경계 정확도 100% |
| NFR-08 | 복원력 | 파일 업로드 실패 시 기존 인라인 방식으로 자동 폴백 | 폴백 전환 시 제출 성공률 유지 |

### 3.3 사용자 스토리

```
AS A 강의 제작자
I WANT TO 슬라이드 프롬프트를 Manus AI에 자동 제출하여 고품질 PPTX를 생성
SO THAT 수동으로 AI 도구에 복붙하는 반복 작업 없이 대규모 슬라이드를 효율적으로 생산할 수 있다.

수용 조건:
1. 입력: 04_SlidePrompt/ 폴더 내 N개 프롬프트 파일 + MANUS_API_KEY
2. 출력: 07_ManusSlides/{세션ID}_{세션제목}.pptx (×N개) + generation_report.json
3. 1,000줄 이상 프롬프트는 교시 경계에서 자동 분할되어야 함
4. 분할된 청크 PPTX는 세션별로 자동 병합되어야 함
5. QA 검증을 통과한 산출물만 최종 확정
6. 제출 실패 시 해당 청크만 자동 재시도
7. 파일 업로드 모드로 공통 헤더 중복 전송을 제거하여 비용 절감
```

---

## 4. DDD 전술 설계 (Tactical Design)

### 4.1 Aggregate 설계

#### Aggregate Root: `ManusSlideJob`

```
ManusSlideJob (Aggregate Root)
├── input_manifest: InputManifest (Value Object)
│   ├── prompt_files: List<PromptFileInfo>
│   │   ├── file_path: FilePath
│   │   ├── line_count: int
│   │   ├── slide_count: int
│   │   └── needs_chunking: boolean
│   └── api_key_valid: boolean
├── validation_report: ValidationReport (Value Object)
├── chunk_manifest: ChunkManifest (Entity)
│   ├── chunks: List<Chunk>
│   │   ├── chunk_id: ChunkID
│   │   ├── source_file: FilePath
│   │   ├── session_boundary: SessionRange
│   │   ├── common_header: string (①②④⑤)
│   │   └── content: string (③⑥)
│   └── passthrough_files: List<FilePath>
├── upload_context: UploadContext (Value Object)          ← v1.1 추가
│   ├── project_id: string?
│   ├── file_ids: Dict<string, string>?
│   └── upload_mode: boolean
├── submission_log: SubmissionLog (Entity)
│   ├── entries: List<SubmissionEntry>
│   │   ├── chunk_id: ChunkID
│   │   ├── manus_task_id: string
│   │   ├── status: SubmissionStatus (PENDING | SUBMITTED | POLLING | DOWNLOADED | FAILED)
│   │   ├── retry_count: int
│   │   └── pptx_path: FilePath
│   └── total_duration_ms: long
├── merged_pptx_files: List<MergedPPTX> (Value Object)
│   ├── session_id: SessionID
│   ├── session_title: string
│   ├── pptx_path: FilePath
│   └── slide_count: int
├── qa_report: QAReport (Entity)
└── job_status: JobStatus (Value Object: IDLE | RUNNING | QA | APPROVED | REJECTED | FAILED)
```

#### 불변조건 (Invariants)

1. `ManusSlideJob`은 유효한 `MANUS_API_KEY`가 있어야 실행 가능하다
2. 모든 `prompt_files`는 6-Section 스키마(①~⑥)를 준수해야 한다
3. `line_count ≥ 1000` 또는 `slide_count ≥ 35`인 파일은 반드시 분할해야 한다
4. 각 `Chunk`의 `common_header`에는 ①②④⑤ 섹션이 복제되어야 한다
5. `job_status`가 `APPROVED`이려면 `qa_report.verdict`가 `PASS`여야 한다
6. 파일 업로드 실패 시 `upload_context.upload_mode`가 `false`로 전환되어야 한다 (v1.1)

### 4.2 Entity vs Value Object

| 구분 | 이름 | 식별자 | 생명주기 | 근거 |
|------|------|--------|----------|------|
| **Entity** | ChunkManifest | — (Aggregate 내부) | 분할 후 제출·병합까지 추적 | D2가 생성, D3/D4가 참조하며 상태 변경 |
| **Entity** | SubmissionLog | — (Aggregate 내부) | 제출 시 생성, 폴링·다운로드 시 갱신 | 재시도 시 이전 기록과 비교 필요 |
| **Entity** | QAReport | qa_report_id | 검증 시마다 새로 생성 | 반려-재시도 시 이전 QA 결과와 비교 필요 |
| **VO** | InputManifest | — | step_1에서 1회 생성 | 탐색 결과 불변 |
| **VO** | ValidationReport | — | step_2에서 1회 생성 | 검증 결과 불변 |
| **VO** | UploadContext | — | Phase 1.5에서 1회 생성 | 업로드 결과 불변 (v1.1) |
| **VO** | MergedPPTX | — | 병합 후 변경 불가 | 최종 산출물 참조용 |
| **VO** | JobStatus | — | 열거형 상태 전이 | IDLE→RUNNING→QA→APPROVED/REJECTED/FAILED |

### 4.3 Domain Event

| 이벤트 | 발행 시점 | 발행자 | 소비자 | 페이로드 |
|--------|----------|--------|--------|----------|
| `InputsDiscovered` | step_1 완료 | D0 | D1 | input_manifest, prompt_file_list |
| `PromptsValidated` | step_2 완료 | D1 | D2 | validation_report, validated_files |
| `ChunksSplit` | step_3 완료 | D2 | D3 | chunk_manifest, chunk_files |
| `FilesUploaded` | Phase 1.5 완료 | D0 | D3 | project_id, file_ids_map (v1.1) |
| `PPTXDownloaded` | step_4 완료 | D3 | D4 | submission_log, downloaded_pptx_paths |
| `PPTXMerged` | step_5 완료 | D4 | D5 | merged_pptx_files, post_processing_report |
| `QACompleted` | step_6 완료 | D5 | D0 | qa_report, verdict |
| `JobApproved` | step_7 승인 | D0 | step_8 | approved_pptx_files |
| `JobPartialResubmit` | step_7 재제출 | D0 | D3 | failed_chunk_ids |
| `JobRejected` | step_7 반려 | D0 | D2 | rejection_reasons, retry_count |

### 4.4 Domain Service

| 서비스 | 책임 | 호출 시점 |
|--------|------|----------|
| `ChunkSplittingService` | 교시 경계 감지 및 프롬프트 분할 로직 | Phase 2 (step_3) |
| `FileUploadService` | 프로젝트 생성 + 공통 헤더 파일 업로드 (v1.1) | Phase 1.5 |
| `ManusSubmissionService` | manus_slide.py 실행, 30초 폴링, PPTX 다운로드 | Phase 3 (step_4) |
| `PPTXMergeService` | python-pptx로 청크 PPTX 병합, 후처리 | Phase 4 (step_5) |
| `RetryCoordinator` | 반려/재제출 시 재시도 횟수 관리 및 라우팅 | Phase 5 (step_7) |

---

## 5. 워크플로우 실행 흐름

### 5.1 Phase 구조

```
Phase 1: 입력 탐색 + 검증 — 프롬프트 파일 탐색 → 구조 검증
  step_1 [D0] → step_2 [D1]

Phase 1.5: 파일 업로드 준비 (v1.1 추가)
  D0 main() 내부 — setup_project_with_files() 호출
  - Manus Projects API로 프로젝트 생성 (SLIDE_GENERATION_PREFIX를 instruction으로)
  - Manus Files API로 공통 헤더(①②④⑤) 업로드
  - 실패 시 기존 인라인 모드로 자동 폴백
  ※ 별도 step 없이 main() preflight 직후 실행

Phase 2: 교시 단위 분할
  step_3 [D2] ← depends_on: step_2
  ※ 업로드 모드 시 use_upload=True → 청크에서 공통 헤더 제외

Phase 3: Manus AI 제출 + 다운로드
  step_4 [D3] ← depends_on: step_3
  ※ 업로드 모드 시 project_id + file_ids를 create_task()에 전달

Phase 4: 후처리 + 품질 검증
  step_5 [D4] → step_6 [D5] ← depends_on: step_4

Phase 5: 최종 승인/반려 + 산출물 확정
  step_7 [D0] ← depends_on: step_6
    ├── approved → step_8 [D0] (최종 산출물)
    ├── partial_resubmit → step_4 (해당 청크만)
    └── rejected → step_3 (분할 전략 재실행, max 2회)
  step_8 [D0] ← depends_on: step_7 (approved)
```

### 5.2 스텝 상세

| Step ID | Agent | Action | Input | Output | Phase |
|---------|-------|--------|-------|--------|-------|
| `step_1_input_discovery` | D0_Orchestrator | `discover_inputs` | 04_SlidePrompt/ directory, MANUS_API_KEY | Input Manifest (파일 목록, 크기, 슬라이드 수) | 1 |
| `step_2_prompt_validation` | D1_Prompt_Validator | `validate_prompts` | Input Manifest, Prompt files | Validation Report (구조 검증, PREFIX 중복 체크) | 1 |
| `step_3_chunk_splitting` | D2_Chunk_Splitter | `split_prompts` | Validated Prompt files, Validation Report | Chunk Manifest, Chunk files (임시 디렉토리) | 2 |
| `step_4_manus_submission` | D3_Submission_Manager | `submit_and_download` | Chunk Manifest, Chunk/원본 files, MANUS_API_KEY, `project_id` + `file_ids` (optional, 업로드 모드) | Submission Log, Downloaded PPTX files | 3 |
| `step_5_post_processing` | D4_Post_Processor | `merge_and_cleanup` | Downloaded PPTX files, Chunk Manifest | Merged PPTX files (세션별 1개), Post-processing Report | 4 |
| `step_6_visual_qa` | D5_Visual_QA | `inspect_quality` | Final PPTX files, Chunk Manifest, Prompt files | QA Report (보존율, 디자인, 노트, 경계) | 4 |
| `step_7_approval` | D0_Orchestrator | `review_and_decide` | QA Report, Post-processing Report | Final Decision (승인/재제출/반려) | 5 |
| `step_8_finalize` | D0_Orchestrator | `finalize_output` | Approved PPTX files, QA Report, Submission Log | Final PPTX files, generation_report.json, manus_task_log.json | 5 |

### 5.3 의존성 그래프 (DAG)

```
step_1 ──→ step_2 ──→ [Phase 1.5: File Upload] ──→ step_3 ──→ step_4 ──→ step_5 ──→ step_6 ──→ step_7
                                                       ▲                                           │
                                                       │                              ┌────────────┼────────────┐
                                                       │                              │            │            │
                                                       │                       partial_resubmit  approved   rejected
                                                       │                              │            │            │
                                                       │                              ▼            ▼            │
                                                       │                           step_4       step_8          │
                                                       │                                                        │
                                                       └────────────────────────────────────────────────────────┘
                                                                                (max 2회)
```

---

## 6. 상태 전이 (State Machine)

```
                    ┌──────────────┐
                    │   IDLE       │
                    └──────┬───────┘
                           │ trigger: prompt_files_ready
                           ▼
                    ┌──────────────┐
                    │ DISCOVERING  │  (D0: 입력 탐색)
                    └──────┬───────┘
                           │ InputsDiscovered
                           ▼
                    ┌──────────────┐
                    │ VALIDATING   │  (D1: 구조 검증)
                    └──────┬───────┘
                           │ PromptsValidated
                           ▼
                    ┌──────────────┐
                    │ FILE_UPLOAD  │  (D0: 프로젝트 생성 + 파일 업로드)  ← v1.1 추가
                    └──────┬───────┘
                           │ FilesUploaded (또는 폴백 시 skip)
                           ▼
                    ┌──────────────┐
              ┌────▶│ SPLITTING    │◀─── JobRejected (retry ≤ 2)
              │     └──────┬───────┘
              │            │ ChunksSplit
              │            ▼
              │     ┌──────────────┐
              │  ┌─▶│ SUBMITTING   │◀─── JobPartialResubmit
              │  │  └──────┬───────┘
              │  │         │ PPTXDownloaded
              │  │         ▼
              │  │  ┌──────────────┐
              │  │  │ MERGING      │  (D4: 병합 + 후처리)
              │  │  └──────┬───────┘
              │  │         │ PPTXMerged
              │  │         ▼
              │  │  ┌──────────────┐
              │  │  │ QA_CHECKING  │  (D5: 품질 검증)
              │  │  └──────┬───────┘
              │  │         │ QACompleted
              │  │         ▼
              │  │  ┌──────────────┐
              │  │  │ APPROVING    │  (D0: 판정)
              │  │  └──────┬───────┘
              │  │       ╱  │  ╲
              │  │ partial  approved  rejected
              │  │ resubmit │            │
              │  └──┘       ▼            │
              │      ┌──────────────┐    │
              │      │ FINALIZING   │    │
              │      └──────┬───────┘    │
              │             │            │
              │             ▼            │
              │      ┌──────────────┐    │
              │      │  COMPLETED   │    │
              │      └──────────────┘    │
              │                          │
              └──────────────────────────┘
                                   (retry > 2)
                                        │
                                        ▼
                                 ┌──────────────┐
                                 │   FAILED     │
                                 └──────────────┘
```

---

## 7. 에이전트 모델 라우팅

| Agent | 기본 카테고리 | 오버라이드 | 기대 모델 등급 | 비용 (Input/1K) | 비용 (Output/1K) |
|-------|:---:|:---:|:---:|---:|---:|
| D0_Orchestrator (×3) | `quick` | `unspecified-low` | Sonnet급 | $0.003 | $0.015 |
| D1_Prompt_Validator | `quick` | — | Haiku급 | $0.00025 | $0.00125 |
| D2_Chunk_Splitter | `quick` | `writing` | Sonnet급 | $0.003 | $0.015 |
| D3_Submission_Manager | `quick` | — | Haiku급 | $0.00025 | $0.00125 |
| D4_Post_Processor | `quick` | — | Haiku급 | $0.00025 | $0.00125 |
| D5_Visual_QA | `quick` | `ultrabrain` | Opus급 | $0.015 | $0.075 |

### 비용 추정 공식

```
est_tokens = round(bytes ÷ 3.3)
est_cost = (input_tokens × input_rate + output_tokens × output_rate) ÷ 1000
```

---

## 8. 인터페이스 설계

### 8.1 파이프라인 입력 (Pipeline Input)

| 입력 항목 | 타입 | 필수 | 설명 |
|-----------|------|------|------|
| `prompt_directory` | DirectoryPath | ✅ | `04_SlidePrompt/` 폴더 경로 (N개 프롬프트 파일) |
| `MANUS_API_KEY` | string (env) | ✅ | Manus AI API 인증 키 (환경변수) |
| `output_language` | string | 자동 | 고정값: `"Korean"` |
| `--no-upload` | boolean | ❌ | 파일 업로드 모드 비활성화 (기존 인라인 방식 강제) |

### 8.2 파이프라인 산출물 (Pipeline Output)

| 산출물 | 경로 | 설명 |
|--------|------|------|
| 세션별 PPTX | `07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개) | Manus AI가 생성한 최종 프레젠테이션 파일 |
| 생성 리포트 | `07_ManusSlides/generation_report.json` | 소요 시간, 분할/병합 이력, 재제출 횟수, 업로드 모드 정보 기록 |
| 태스크 로그 | `07_ManusSlides/manus_task_log.json` | Manus AI API 호출 상세 로그 |

### 8.3 하류 전파 (Downstream Propagation)

| 소비자 파이프라인 | 참조하는 산출물 | 사용 목적 |
|-------------------|----------------|-----------|
| WF08 (Log Analysis) | JSONL 실행 로그 | 파이프라인 실행 분석 및 최적화 |
| — (최종 사용자) | 세션별 PPTX 파일 | 강의 프레젠테이션 직접 사용 |

---

## 9. 오류 처리

| 오류 유형 | 발생 스텝 | 처리 전략 | 재시도 |
|-----------|----------|-----------|--------|
| MANUS_API_KEY 미설정/무효 | step_1 | 환경변수 설정 안내 메시지 출력 후 파이프라인 중단 | 0 (즉시 중단) |
| 04_SlidePrompt/ 폴더 비어있음 | step_1 | WF04 선행 실행 안내, 파이프라인 중단 | 0 |
| 프롬프트 6-Section 구조 불완전 | step_2 | 누락 섹션 목록 출력, 해당 파일 skip 또는 전체 중단 | 0 |
| PREFIX 중복 삽입 감지 | step_2 | 중복 PREFIX 자동 제거 후 경고 로그 | 자동 |
| 파일 업로드 실패 (Projects/Files API) | Phase 1.5 | 기존 인라인 방식으로 자동 폴백, 경고 로그 | 0 (폴백) |
| 교시 경계 감지 실패 (분할 불가) | step_3 | 원본 그대로 통과 (원샷 제출) + 경고 로그 | 0 |
| Manus AI API 제출 실패 | step_4 | 해당 청크 1회 자동 재시도, 재실패 시 skip 후 리포트 기록 | 1회 |
| Manus AI 폴링 타임아웃 | step_4 | 10분 초과 시 해당 청크 실패 처리, 재시도 큐에 추가 | 1회 |
| PPTX 다운로드 실패 | step_4 | 다운로드 재시도 1회, 실패 시 해당 청크 skip | 1회 |
| python-pptx 병합 오류 | step_5 | 병합 실패 청크 개별 파일로 유지, 경고 로그 | 0 |
| QA 검증 실패 (콘텐츠 보존율 미달) | step_6 | step_7에서 partial_resubmit 또는 rejected 판정 | step_7 판정 |
| 최대 재시도 초과 (2회) | step_7 | 파이프라인 FAILED 상태 전환, 사용자 에스컬레이션 | 0 (종료) |

---

## 10. 로깅

### 10.1 로깅 설정

```yaml
logging:
  enabled: true
  protocol: ".agent/logging-protocol.md"
  model_config: ".opencode/oh-my-opencode.jsonc"
  path: ".agent/logs/{YYYY-MM-DD}_07_Manus_Slide.jsonl"
  format: "jsonl"
```

### 10.2 이벤트 유형

| 이벤트 | 발생 시점 | 주요 필드 |
|--------|----------|-----------|
| `START` | 각 step 실행 전 | run_id, agent_id, step_id, input_bytes |
| `END` | 각 step 성공 완료 | run_id, agent_id, output_bytes, duration_ms, est_tokens, est_cost |
| `FAIL` | 에이전트 실행 실패 | run_id, agent_id, error_type, error_message |
| `RETRY` | 재시도 발생 | run_id, agent_id, retry_count, max_retries |
| `DECISION` | step_7 판정 | run_id, verdict (approved/partial_resubmit/rejected), reason |
| `DECISION` | Phase 1.5 업로드 결과 | run_id, decision (upload_success/upload_fallback), project_id |

### 10.3 비용 추정

| 에이전트 | 카테고리 | 예상 입력 (tokens) | 예상 출력 (tokens) | 예상 비용 ($) |
|----------|---------|------------------:|------------------:|-------------:|
| D0 (×3) | unspecified-low | 4,000 | 3,000 | $0.057 |
| D1 | quick | 5,000 | 2,000 | $0.004 |
| D2 | writing | 8,000 | 6,000 | $0.114 |
| D3 | quick | 3,000 | 1,500 | $0.003 |
| D4 | quick | 4,000 | 2,000 | $0.004 |
| D5 | ultrabrain | 8,000 | 5,000 | $0.495 |
| **합계** | — | **~36,000** | **~22,500** | **~$0.68** |

> **참고**: Manus AI API 호출 비용은 별도이며, 위 비용은 에이전트 LLM 호출만 포함합니다.

---

## 11. 설정 (Configuration)

### 11.1 config.json 매핑

```jsonc
// .agent/agents/07_manus_slide/config.json
{
  "name": "07_manus_slide",
  "default_category": "quick",
  "agent_models": {
    "D0_Orchestrator": { "category": "unspecified-low", "note": "오케스트레이터 — 판정/조정만" },
    "D2_Chunk_Splitter": { "category": "writing", "note": "교시 경계 감지 — 텍스트 분석 필요" },
    "D5_Visual_QA": { "category": "ultrabrain", "note": "다차원 품질 검증 — 고품질 추론 필요" }
  }
}
```

### 11.2 워크플로우 YAML 핵심 설정

| 설정 키 | 값 | 의미 |
|---------|-----|------|
| `version` | `"1.1"` | 워크플로우 스키마 버전 |
| `max_retries` | `2` | step_7 반려 시 최대 재실행 횟수 |
| `required_env` | `["MANUS_API_KEY"]` | 필수 환경변수 |
| `output_path` | `{YYYY-MM-DD_강의제목}/07_ManusSlides/{세션ID}_{세션제목}.pptx` | 최종 산출물 경로 패턴 |
| `logging.path` | `.agent/logs/{YYYY-MM-DD}_07_Manus_Slide.jsonl` | 로그 파일 경로 |

---

## 12. 품질 게이트 (Quality Gates)

### 12.1 스텝별 품질 기준

| Gate | 위치 | 검증 항목 | 통과 조건 |
|------|------|----------|-----------|
| **G1: API Key Validity** | step_1 → step_2 | MANUS_API_KEY 환경변수 존재 및 유효성 | API 키 인증 성공 |
| **G1.5: File Upload** | Phase 1.5 | Projects/Files API 호출 성공 여부 | 업로드 성공 또는 폴백 전환 완료 |
| **G2: Prompt Structure** | step_2 → step_3 | 6-Section 스키마(①~⑥) 완전성 | 모든 파일 6개 섹션 존재 |
| **G3: Chunk Integrity** | step_3 → step_4 | 분할 청크의 공통 헤더(①②④⑤) 복제 및 ③⑥ 추출 | 청크당 6개 섹션 유지 |
| **G4: Download Completeness** | step_4 → step_5 | 모든 청크/원본에 대한 PPTX 다운로드 | 다운로드 성공률 ≥ 90% |
| **G5: Content Preservation** | step_6 → step_7 | 프롬프트 대비 슬라이드 수, 핵심 키워드 매칭 | 콘텐츠 보존율 ≥ 85% |
| **G6: Design Compliance** | step_6 → step_7 | 헤더/풋터 부재, full bleed 적용 | 디자인 규칙 100% 준수 |
| **G7: Note Completeness** | step_6 → step_7 | 발표자 노트 6개 필수 항목 | 노트 완전성 100% |
| **G8: Boundary Smoothness** | step_6 → step_7 | 병합 슬라이드의 청크 경계 연속성 | 경계 부자연스러움 0건 |

### 12.2 3중 관점 검증

| 관점 | 검증 대상 | 적용 스텝 |
|------|----------|-----------|
| Senior Fullstack Developer | API 호출 안정성, python-pptx 병합 정확성, 파일 경로 규칙 | step_6 |
| Technical Education Content Designer | 콘텐츠 보존율, 교시별 흐름 연속성, 발표자 노트 교육적 적합성 | step_6 |
| Presentation Designer | 디자인 규칙 준수 (full bleed, 헤더/풋터 제거), 슬라이드 시각적 일관성 | step_6 |

---

## 13. 확장 포인트

| 확장 포인트 | 현재 상태 | 확장 방향 |
|-------------|----------|-----------|
| **AI 모델 업그레이드** | manus-1.6-max (Nano Banana Pro) | Manus API 모델 버전 업그레이드 시 설정만 변경 |
| **병렬 제출** | 순차 제출 (30초 폴링) | 동시 3~5개 청크 병렬 제출로 처리 시간 단축 |
| **분할 알고리즘** | 교시(세션) 경계 기반 | 의미 단위 분할 (Topic Segmentation) 도입 |
| **품질 피드백 루프** | 단방향 (프롬프트→PPTX) | QA 실패 시 프롬프트 자동 수정 후 재제출 (BC4←BC7 이벤트) |
| **PPTX 후처리** | 헤더/풋터/페이지번호 제거 | 커스텀 템플릿 적용, 브랜딩 요소 삽입 |
| **다중 AI 백엔드** | Manus AI 단독 | OpenAI, Google Slides API 등 멀티 백엔드 지원 |
| **대시보드 연동** | generation_report.json 파일 | 실시간 제출 상태 모니터링 웹 대시보드 |
| **파일 업로드 모드** | ✅ 구현 완료 (v1.1) | Projects/Files API로 공통 헤더 사전 업로드, 청크별 중복 전송 제거. `--no-upload`로 비활성화 가능. 4분할 시 ~309줄(21KB) 절감 |

---

## 부록 A: 분할 정책 상세

### 분할 임계값

| 기준 | 임계값 | 동작 |
|------|--------|------|
| 줄 수 | ≤ 1,000줄 | 원샷 제출 (분할 불필요) |
| 줄 수 | > 1,000줄 | 교시 경계에서 분할 |
| 슬라이드 수 | ≤ 35개 | 원샷 제출 |
| 슬라이드 수 | > 35개 | 교시 경계에서 분할 |

### 청크 구조

```
[청크 N]
├── ① Role (공통 헤더에서 복제)
├── ② 교안 정보 (공통 헤더에서 복제)
├── ③ 슬라이드 구성 (해당 교시 범위만 추출)
├── ④ 스타일 (공통 헤더에서 복제)
├── ⑤ 품질 (공통 헤더에서 복제)
└── ⑥ 교안 원문 (해당 교시 범위만 추출)
```

> **파일 업로드 모드 시**: ①②④⑤ 공통 헤더는 Files API로 사전 업로드되므로, 각 청크 프롬프트에는 ③⑥ 동적 콘텐츠만 포함됩니다. `create_task()` 호출 시 `projectId` + `attachments(file_id)` 파라미터로 공통 헤더를 참조합니다.

### 병합 규칙

1. 각 청크 PPTX의 슬라이드를 순서대로 병합
2. 슬라이드 노트(발표자 노트) 보존
3. 헤더/풋터/페이지번호 후처리 제거
4. 병합 경계 슬라이드의 연속성 확인

## 부록 B: 기술 스택

| 기술 | 용도 | 버전 |
|------|------|------|
| Manus AI API | 슬라이드 렌더링 (Nano Banana Pro) | manus-1.6-max |
| Manus Projects API | 프로젝트 생성 + instruction 설정 (v1.1) | v1 |
| Manus Files API | 공통 헤더 파일 업로드 + presigned URL (v1.1) | v1 |
| manus_slide.py | API 호출 스크립트 | — |
| python-pptx | PPTX 파일 병합 및 후처리 | — |

## 부록 C: 판정 로직 (Decision Logic)

| 판정 | 조건 | 라우팅 |
|------|------|--------|
| `approved` | QA 보고서 전 항목 PASS | → step_8 (최종 산출물) |
| `partial_resubmit` | 일부 청크만 QA 실패 | → step_4 (해당 청크만 재제출) |
| `rejected` | 분할 전략 자체 문제 또는 다수 청크 실패 | → step_3 (분할부터 재실행, max 2회) |
