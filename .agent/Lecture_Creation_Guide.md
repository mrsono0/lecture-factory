# 강의 생성 시스템 사용자 가이드

이 문서는 Lecture Factory 에이전트 팀을 사용하여 강의 기획부터 교안, 슬라이드, PPTX 파일까지 생성하는 절차를 안내합니다.

> 에이전트 파이프라인 내부 구조, 실행 흐름 등 기술적 상세는 [`Developer_Guide.md`](./Developer_Guide.md)를 참조하세요.

---

## 전체 프로세스 요약

| 단계 | 목표 | 실행 워크플로우 | 주요 산출물 |
|---|---|---|---|
| **1. 기획 (Planning)** | 주제 분석 및 커리큘럼 확정 | `01_Lecture_Planning.yaml` | `01_Planning/강의구성안.md` |
| **2. 집필 (Writing)** | 상세 교안 및 코드 작성 | `02_Material_Writing.yaml` | `02_Material/강의교안_v1.0.md` |
| **3. 시각화 (Visualizing)** | 발표용 슬라이드 기획 | `03_Slide_Generation.yaml` | `03_Slides/{session}/슬라이드기획안.md` |
| **4. 슬라이드 프롬프트 생성** | 교안에서 원샷 슬라이드 생성 프롬프트 생성 | `04_SlidePrompt_Generation.yaml` | `04_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개) |
| **5. PPTX 변환** | HTML 기반 PPTX 생성 | `05_PPTX_Conversion.yaml` | `05_PPTX/최종_프레젠테이션.pptx` |
| **6. NanoBanana PPTX** | AI 이미지 기반 고품질 PPTX | `06_NanoBanana_PPTX.yaml` | `06_NanoPPTX/최종_프레젠테이션.pptx` |
| **7. Manus 슬라이드** | Manus AI로 PPTX 생성 | `.agent/scripts/manus_slide.py` | `07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개) |
| **E2E 통합 실행** | 1, 2, 3, 4단계 순차 자동 실행 | — (마스터 오케스트레이터) | 기획안→교안→슬라이드→프롬프트 |

> **5, 6, 7단계는 택 1**: 코드 중심 → 05(HTML 기반, 빠름) / 로컬 AI 이미지 → 06(Gemini API) / 클라우드 AI 생성 → 07(Manus API, 최고 품질)
>
> **4 → 7 연계**: 4단계에서 프롬프트 생성 후 7단계에서 PPTX 자동 생성. 교안에서 최종 PPTX까지 자동화됩니다.

---

## 단계별 상세 가이드

### 1단계: 강의 구성안 작성 (Planning)

**목표**: 모호한 아이디어를 구체적인 커리큘럼으로 구조화합니다.

#### 입력 파일 준비

강의 주제, 대상, 목표가 담긴 초안 문서(예: `AI-native_파이썬기초.md`)를 준비합니다.
(선택) NotebookLM URL을 준비하면 더 정확한 분석이 가능합니다.

**필수 항목 (6개)** — 반드시 작성

| # | 항목 | 설명 | 예시 |
|---|------|------|------|
| 1 | **주제/스택** | 강의 제목, 핵심 철학, 기술 스택, 파트별 개요 | `AI-native 파이썬 기초 과정` |
| 2 | **대상 수준** | 수강생 배경, 선행 학습, 기술 수준 | `비전공 취업준비생` |
| 3 | **총 시간/회차** | 전체 강의 시간과 일정 구조 | `40시간 (8h × 5일)` |
| 4 | **산출 범위** | 기획 단계에서 어디까지 만들지 | `커리큘럼 + 세션 상세표` |
| 5 | **실습 환경 제약** | OS, IDE, AI 도구 등 | `Windows 11, Antigravity, Gemini 3 Pro` |
| 6 | **"반드시 할 수 있어야 하는 것"** | 핵심 성과 2~3가지 | `① 기초문법 이해 ② AI 코드 생성·리뷰` |

**선택 항목 (2개)** — 생략 시 기본값 자동 적용

| # | 항목 | 기본값 |
|---|------|--------|
| 7 | **톤·수준** | 상세 대본 기반 구어체 (~해요, ~입니다), 비유 중심 설명 + 'AI 시대의 서사' 톤, 실습 비율 60%↑, AI-first 학습 |
| 8 | **전제 조건** | 프로그래밍 경험 없음, IT 리터러시 있음, AI 프롬프트 코딩 |

> 기본값 적용 시 강의구성안에 `[기본값 적용]`으로 표기됩니다.

#### 입력 파일 템플릿 (복사해서 사용)

```markdown
## 1. 주제/스택
- 강의 제목: [제목]
- [핵심 철학이나 교육 관점 한 줄]
- 파트별 개요:
  - 파트1: ...
  - 파트2: ...

## 2. 대상 수준
- [수강생 배경 및 선행 학습]

## 3. 총 시간/회차
- [예: 40시간 (8시간 × 5일)]

## 4. 산출 범위
- [예: 커리큘럼 + 세션 상세표]

## 5. 실습 환경 제약
- [OS, IDE, AI 도구 등]

## 6. "반드시 할 수 있어야 하는 것"
- ① ...
- ② ...
- ③ ...

## 7. 톤·수준 ← 생략 가능
- [커스터마이징이 필요한 경우에만 작성]

## 8. 전제 조건 ← 생략 가능
- [커스터마이징이 필요한 경우에만 작성]
```

#### 실행 방법

```
# 기본 명령
"01_Lecture_Planning 워크플로우를 실행해줘. 입력 파일은 AI-native_파이썬기초.md야."

# NotebookLM URL 포함 시
"01_Lecture_Planning 워크플로우를 실행해줘. 입력 파일은 AI-native_파이썬기초.md이고, 참고할 NotebookLM 주소는 https://notebooklm.google.com/... 야."

# 로컬 프로젝트 폴더 지정 시
"01_Lecture_Planning 워크플로우 실행해줘. 참고할 로컬 폴더는 /Users/.../Python_Project 야. 이 폴더의 모든 파일을 먼저 분석해줘."
```

#### 결과물

`YYYY-MM-DD_강의제목/01_Planning/강의구성안.md`

> 💡 **E2E 자동화**: 1, 2, 3, 4단계를 한 번에 실행하려면 "전체 파이프라인 실행해줘"라고 지시하세요. (5·6·7단계 PPTX 생성은 별도 실행)

---

### 2단계: 강의 교안 작성 (Writing)

**목표**: 확정된 구성안을 바탕으로 실제 수업이 가능한 상세 교안을 작성합니다.

#### 입력 준비

- 1단계에서 생성된 `강의구성안.md` (미지정 시 자동 탐색)
- (선택) NotebookLM URL, 로컬 참고자료 폴더

#### 실행 방법

```
# 기본 명령
"02_Material_Writing 워크플로우를 실행해서 교안을 작성해줘."

# NotebookLM URL 포함 시
"02_Material_Writing 워크플로우 실행해줘. 입력 파일은 강의구성안.md이고, 참고할 NotebookLM URL은 https://notebooklm.google.com/... 야."

# 로컬 프로젝트 폴더 지정 시
"02_Material_Writing 워크플로우 실행해줘. 프로젝트 폴더 /Users/.../Python_Project의 내용을 분석해서 스타일과 기존 내용을 반영해줘."
```

#### 결과물

`YYYY-MM-DD_강의제목/02_Material/강의교안_v1.0.md`

> 💡 **E2E 자동화**: "전체 파이프라인 실행해줘"를 사용하면 1단계 산출물이 자동으로 입력됩니다.

---

### 3단계: 슬라이드 생성 (Visualizing)

**목표**: 완성된 교안을 발표용 장표 구조로 변환합니다.

**지원 모드**: 단일 파일 / 배치 (N개 파일 순차 처리)

#### 실행 방법

```
# 기본 명령 (최근 교안 자동 탐색)
"03_Slide_Generation 워크플로우를 실행해줘."

# 파일 지정 시 (세션 자동 추출)
"03_Slide_Generation 워크플로우 실행해줘. 입력 파일은 02_Material/Day1_AM_환경구축_Antigravity_Python.md 야."

# 배치 모드 (폴더 지정 → N개 파일 순차 처리)
"03_Slide_Generation 워크플로우 실행해줘. 교안 폴더는 /Users/.../ADsP/강의 교안/ 이야."
```

> **배치 모드**: 폴더 내 `*.md` 파일을 자동 스캔하여 N개를 순차 처리합니다. 파일 수는 가변(1~수십 개).

#### 결과물

`YYYY-MM-DD_강의제목/03_Slides/{session}/슬라이드기획안.md`

---

### 4단계: 슬라이드 생성 프롬프트 생성 (Slide Prompt Generation)

**목표**: 교안을 분석하여 AI 이미지 생성 도구에서 원샷으로 실행 가능한 프롬프트를 생성합니다.

#### 실행 방법

```
# 기본 명령 (02_Material/ 자동 탐색)
"04_SlidePrompt_Generation 워크플로우를 실행해줘."

# 외부 폴더 지정 시
"04_SlidePrompt_Generation 워크플로우 실행해줘. 교안 폴더는 /Users/.../ADsP/강의 교안/ 이야."

# 03 산출물 참조 시
"04_SlidePrompt_Generation 워크플로우 실행해줘. 교안 폴더는 /Users/.../강의 교안/ 이고, 03_Slides 산출물도 참조해줘."
```

#### 결과물

`{project_folder}/04_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (교안별 개별 파일 ×N개)

> **Note**: 입력 파일 수는 고정값이 아닙니다. 교안 폴더에서 발견된 `*.md` 파일 수에 따라 동적으로 처리합니다.

---

### 5단계: PPTX 변환 (HTML 기반)

**목표**: 3단계 슬라이드 기획안을 실제 PowerPoint 파일로 변환합니다.

#### 실행 방법

```
"05_PPTX_Conversion 워크플로우를 실행해줘."
```

> `03_Slides/` 내 세션 서브폴더를 자동 탐색합니다. 1개면 자동 선택, 복수면 확인합니다.

#### 결과물

`YYYY-MM-DD_강의제목/05_PPTX/최종_프레젠테이션.pptx`, `변환리포트.md`

---

### 6단계: NanoBanana PPTX (AI 이미지 기반)

**목표**: Nano Banana Pro AI로 고품질 이미지 슬라이드를 생성하고 PPTX로 조립합니다.

**필수 환경변수**: `GEMINI_API_KEY`

#### 실행 방법

```
"06_NanoBanana_PPTX 워크플로우를 실행해줘."
```

#### 결과물

`YYYY-MM-DD_강의제목/06_NanoPPTX/최종_프레젠테이션.pptx`, `변환리포트.md`, `index.html`

---

### 7단계: Manus AI 슬라이드 생성

**목표**: 4단계에서 생성된 프롬프트 파일을 Manus AI에 전송하여 PPTX를 다운로드합니다.

**필수 환경변수**: `MANUS_API_KEY`
**필수 요건**: Manus Pro 또는 Team 플랜 (유료)

#### 사전 설정

1. [manus.im](https://manus.im)에서 Pro/Team 플랜 가입
2. `.agent/.env`에 `MANUS_API_KEY="sk-..."` 추가

#### 실행 방법

```bash
# 전체 파일 처리
python .agent/scripts/manus_slide.py {프로젝트폴더경로}

# 단일 파일 처리
python .agent/scripts/manus_slide.py {프로젝트폴더경로} --file Day1_AM

# 드라이런 (API 호출 없이 파일 탐색만)
python .agent/scripts/manus_slide.py {프로젝트폴더경로} --dry-run
```

#### CLI 옵션 레퍼런스

| 옵션 | 설명 |
|------|------|
| `--file PATTERN` / `-f` | 특정 파일/세션ID만 처리 (부분 매칭 지원) |
| `--no-split` | 교시 분할 없이 원본 전체 제출 |
| `--resume` | 이전 실행에서 완료된 파일 자동 스킵 |
| `--dry-run` | API 호출 없이 파일 탐색/분할 판정만 확인 |
| `--quiet` / `-q` | 경고·에러만 출력 |
| `--verbose` / `-v` | DEBUG 레벨 상세 로그 |

#### 결과물

`07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개), `generation_report.json`, `manus_task_log.json`

#### 주의사항

- 10개 파일 기준 예상 소요 시간: **30분~2시간**
- Manus 파일은 **48시간 후 자동 삭제** — 생성 즉시 다운로드 필요
- 중단 시 `manus_task_log.json`에 중간 결과 저장되어 복구 가능

#### 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| API Key 오류 | 환경변수 미설정 | `.agent/.env`에 `MANUS_API_KEY` 추가 |
| 타임아웃 (30분 초과) | Manus 서버 부하 | `manus_task_log.json`의 task_id로 웹에서 확인 |
| 다운로드 실패 | 파일 URL 미반환 | shareable_link로 웹에서 수동 다운로드 |
| 중단 복구 | 비정상 종료 | `--resume` 플래그로 재실행 |
| Lock File 충돌 | 이전 프로세스 잔존 | PID 확인 후 `.manus_slide.lock` 삭제 |

---

## 폴더 구조 예시 (자동 생성됨)

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
│   └── {session}/           (세션별 서브폴더)
│       └── 슬라이드기획안.md
├── 04_SlidePrompt/
│   └── {세션ID}_{세션제목}_슬라이드 생성 프롬프트.md  (×N개)
├── 05_PPTX/                 (Pipeline 5 사용 시)
│   ├── 최종_프레젠테이션.pptx
│   └── 변환리포트.md
├── 06_NanoPPTX/             (Pipeline 6 사용 시)
│   ├── 최종_프레젠테이션.pptx
│   ├── 변환리포트.md
│   └── index.html
├── 07_ManusSlides/          (Pipeline 7 사용 시)
│   ├── {세션ID}_{세션제목}.pptx  (×N개)
│   ├── manus_task_log.json
│   └── generation_report.json
└── 참고자료/
    └── 원본_기획안.md
```

> 상세 폴더 구조(Phase 중간 산출물 포함)는 [`Developer_Guide.md`](./Developer_Guide.md)를 참조하세요.

---

## Flowith Knowledge Garden 활용

Flowith Knowledge Garden에 업로드한 참고자료를 **RAG 기반으로 검색**하여 활용할 수 있습니다.

### 사전 설정

1. [Flowith.io](https://flowith.io) 로그인 → Knowledge Garden → API Settings에서 토큰 발급
2. 사용할 지식 정원의 **KB ID** (UUID 형식) 확인 (웹 대시보드에서 수동 확인)
3. `.agent/.env`에 `FLOWITH_API_TOKEN`, `FLOWITH_KB_LIST` 설정

### 추천 모델

| 용도 | 모델 | 특징 |
|------|------|------|
| 빠른 팩트 수집 | `gemini-3-pro-preview` | ~33초, 안정적 |
| 심층 분석 | `claude-opus-4.6` | ~100초, 구조화 탁월 |
| 비용 효율 | `gpt-4.1-mini` | 가장 저렴, 간단한 팩트 확인용 |

---

## 팁

- **자동 입력 감지**: 2단계 이후 입력 파일을 생략하면 이전 단계 결과물을 자동 탐색합니다.
- **수정 요청**: "A4 에이전트에게 어조를 좀 더 친근하게 바꾸라고 해줘"처럼 구체적으로 피드백 가능합니다.
- **NotebookLM 활용**: 자료가 많을수록 A1 에이전트의 성능이 좋아집니다.
- **Flowith KB 활용**: NotebookLM 대안으로, Flowith Knowledge Garden에 참고자료를 업로드하면 API 검색 가능합니다.
- **Pipeline 5 vs 6 vs 7**: 코드 중심 → 05, 로컬 AI 이미지 → 06, 클라우드 AI → 07.
- **Pipeline 4 → 7 연계**: 4단계 프롬프트 → 7단계 PPTX. 교안에서 최종 PPTX까지 자동화됩니다.
- **E2E 통합 실행**: "전체 파이프라인 실행해줘"로 1, 2, 3, 4단계 순차 자동 실행. (5·6·7단계는 별도 실행)
- **Manus 파일 보존**: Manus에 업로드된 파일은 48시간 후 자동 삭제됩니다. 생성 즉시 다운로드하세요.
