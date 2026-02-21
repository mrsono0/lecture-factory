# 강의 생성 시스템 사용자 가이드

이 문서는 구축된 **Planner, Writer, Visualizer, PPTX Converter, NanoBanana PPTX, Slide Prompt Generator, Manus Slide Generator 에이전트 팀**을 사용하여 강의 기획부터 교안, 슬라이드, PPTX 파일까지 생성하는 절차를 안내합니다.

---

## 전체 프로세스 요약

| 단계 | 목표 | 실행 워크플로우 | 주요 산출물 |
|---|---|---|---|
| **1. 기획 (Planning)** | 주제 분석 및 커리큘럼 확정 | `01_Lecture_Planning.yaml` | `01_Planning/강의구성안.md` |
| **2. 집필 (Writing)** | 상세 교안 및 코드 작성 | `02_Material_Writing.yaml` | `02_Material/강의교안_v1.0.md` |
| **3. 시각화 (Visualizing)** | 발표용 슬라이드 기획 | `03_Slide_Generation.yaml` | `03_Slides/{session}/슬라이드기획안.md` |
| **4. PPTX 변환** | HTML 기반 PPTX 생성 | `04_PPTX_Conversion.yaml` | `04_PPTX/최종_프레젠테이션.pptx` |
| **5. NanoBanana PPTX** | AI 이미지 기반 고품질 PPTX | `05_NanoBanana_PPTX.yaml` | `05_NanoPPTX/최종_프레젠테이션.pptx` |
| **6. 슬라이드 프롬프트 생성** | 교안에서 원샷 슬라이드 생성 프롬프트 생성 | `06_SlidePrompt_Generation.yaml` | `06_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개) |
| **7. Manus 슬라이드** | Manus AI로 PPTX 생성 | `.agent/scripts/manus_slide.py` | `07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개) |
| **E2E 통합 실행** | 1단계부터 6단계까지 자동 연결 실행 | — (마스터 오케스트레이터) | 전체 산출물 |

> **Note**: Pipelines 4, 5, 7 are alternative PPTX generation methods:
> - **04**: HTML 기반 변환 (빠름, 코드 중심 슬라이드에 적합)
> - **05**: AI 이미지 생성 via Nano Banana Pro (높은 시각 품질, 디자인 중심 슬라이드에 적합)
> - **07**: Manus AI 클라우드 (Manus Pro plan 필요, 최고 품질)
>
> **6 → 7 연계**: 6단계에서 프롬프트 생성 후 7단계에서 PPTX 자동 생성. 교안에서 최종 PPTX까지 자동화됩니다.

---

## 단계별 상세 가이드

### 1단계: 강의 구성안 작성 (Planning)

**목표**: 모호한 아이디어를 구체적인 커리큘럼으로 구조화합니다.

1.  **입력 파일 준비**:
    -   강의 주제, 대상, 목표가 담긴 초안 문서(예: `AI-native_파이썬기초.md`)를 준비합니다.
    -   *팁: `AI-native_파이썬기초.md`가 좋은 입력 예시입니다.*
    -   (선택) **NotebookLM URL 확보**: 관련 자료를 업로드한 NotebookLM의 공유 링크(URL)를 준비하면 더 정확한 분석이 가능합니다.

    #### 📋 입력 파일 항목 (필수 6개 + 선택 2개)

    입력 파일에는 **6개 필수 항목**을 반드시 포함해야 합니다. 나머지 2개(톤·수준, 전제 조건)는 생략하면 시스템 기본값이 자동 적용됩니다.

    **필수 항목 (6개)** — 반드시 작성

    | # | 항목 | 설명 | 예시 |
    |---|------|------|------|
    | 1 | **주제/스택** | 강의 제목, 핵심 철학, 다루는 기술 스택, 파트별 개요. 단순 제목이 아닌 "무엇을 어떤 관점으로 가르칠 것인지"가 핵심입니다. | `AI-native 파이썬 기초 과정` / `문제를 정의하고 AI와 협업하는 사람 양성` |
    | 2 | **대상 수준** | 수강생의 배경, 선행 학습, 기술 수준. 구체적일수록 커리큘럼 난이도 조절이 정확해집니다. | `"AI 시대의 서사" 이수한 비전공 취업준비생` |
    | 3 | **총 시간/회차** | 전체 강의 시간과 일정 구조. 시간에 따라 커리큘럼 깊이와 실습 비율이 결정됩니다. | `40시간 (8h × 5일)` 또는 `16시간 (4h × 4주)` |
    | 4 | **산출 범위** | 기획 단계에서 어디까지 만들지 정의합니다. | `커리큘럼 + 세션 상세표` 또는 `커리큘럼 목차만` |
    | 5 | **실습 환경 제약** | 수강생이 사용할 OS, IDE, AI 도구 등 물리적 환경. 실습 설계에 직접 영향을 줍니다. | `Windows 11, Antigravity, Gemini 3 Pro` |
    | 6 | **"반드시 할 수 있어야 하는 것"** | 수강 후 **반드시** 달성해야 하는 핵심 성과 2~3가지. 학습 목표(LO)의 근간이 됩니다. | `① 기초문법 이해` / `② AI로 코드 생성·리뷰` / `③ 간단한 프로그램 작성` |

    **선택 항목 (2개)** — 생략 시 기본값 자동 적용

    | # | 항목 | 기본값 (생략 시 자동 적용) |
    |---|------|--------------------------|
    | 7 | **톤·수준** | 상세 대본 기반 구어체 (~해요, ~입니다), 비유 중심 설명 + 'AI 시대의 서사' 톤, 모든 주요 개념에 🗣️ 강사 대본 / 실습에 🎙️ 실습 가이드 대본 포함, 실습 비율 60%↑, AI-first 학습 |
    | 8 | **전제 조건** | 프로그래밍 경험 없음 전제, IT 리터러시는 있음, 모든 코드는 AI 프롬프트로 생성, 빈 에디터 직접 코딩 요구 안 함 |

    > **기본값 적용 표시**: 강의구성안에서 기본값이 적용된 항목은 `[기본값 적용]`으로 표기됩니다. 사용자가 직접 지정한 항목은 `[사용자 지정]`으로 구분됩니다. 이 정보는 02_Material_Writing 워크플로우에서 교안 작성 기준으로 그대로 전달됩니다.

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

    ## 7. 톤·수준 ← 생략 가능 (기본값: 비유 중심, 실습 60%↑, AI-first, 구어체)
    - [커스터마이징이 필요한 경우에만 작성]

    ## 8. 전제 조건 ← 생략 가능 (기본값: 비전공·무경험, AI 프롬프트 코딩)
    - [커스터마이징이 필요한 경우에만 작성]
    ```

2.  **실행 방법**:
    -   **기본 명령**:
        > "01_Lecture_Planning 워크플로우를 실행해줘. 입력 파일은 `AI-native_파이썬기초.md`야."
    -   **NotebookLM URL 포함 시**:
        > "01_Lecture_Planning 워크플로우를 실행해줘. 입력 파일은 `AI-native_파이썬기초.md`이고, 참고할 NotebookLM 주소는 `https://notebooklm.google.com/...` 야."
    -   **로컬 프로젝트 폴더 지정 시 (강력 권장)**:
        > "01_Lecture_Planning 워크플로우 실행해줘. 참고할 로컬 폴더는 `/Users/.../Python_Project` 야. 이 폴더의 모든 파일을 먼저 분석해줘."

3.  **내부 프로세스 (자동)**:
    -   **팀 공통 원칙**: 기획 산출물(강의구성안)만으로 교안 작성 팀이 막힘 없이 집필을 시작할 수 있어야 합니다.
    -   **A0 (Orchestrator)**: 요청 분석 및 업무 분배
    -   **A1 (Trend Researcher)**: 관련 트렌드 및 자료 조사 (NotebookLM/Web)
    -   **A5B (Learner Analyst)**: 학습자 페르소나, 선수 지식, 이탈 예상 지점 분석
    -   **A3 (Curriculum Architect)**: A5B 산출물을 입력으로 받아 커리큘럼 구조 설계. 1일 4시간 초과 시 AM/PM 분할, 60~90분 단위 하위 세션 세분화
    -   **A2 (Instructional Designer)** ∥ **A7 (Differentiation Advisor)**: 학습 활동 설계 + USP 식별 (병렬)
    -   **A5A (QA Manager)**: 기획안 검증

4.  **결과물**: `YYYY-MM-DD_강의제목/01_Planning/강의구성안.md`

> 💡 **E2E 자동화**: 1~6단계를 한 번에 실행하려면 "전체 파이프라인 실행해줘"라고 지시하세요. 각 단계의 입력 파일과 URL이 자동으로 전달됩니다.

---

### 2단계: 강의 교안 작성 & 프롬프트 향상 (Writing)

**목표**: 확정된 구성안을 바탕으로 실제 수업이 가능한 상세 교안(텍스트+코드)을 작성합니다.

1.  **입력 준비**:
    -   1단계에서 생성된 `강의구성안.md`를 사용합니다.
    -   필요한 참고 자료(PDF, 영상 등)가 있다면 `참고자료/` 폴더에 넣고 NotebookLM에 업로드합니다.
    -   (선택) **NotebookLM URL**: 업로드 완료된 NotebookLM의 공유 링크를 준비합니다.

2.  **실행 방법**:
    -   **기본 명령**:
        > "02_Material_Writing 워크플로우를 실행해서 교안을 작성해줘."
    -   **NotebookLM URL 포함 시**:
        > "02_Material_Writing 워크플로우 실행해줘. 입력 파일은 `강의구성안.md`이고, 참고할 NotebookLM URL은 `https://notebooklm.google.com/...` 야."
        > *(A1 Source Miner가 해당 URL을 참조하여 팩트를 추출합니다)*
    -   **로컬 프로젝트 폴더 지정 시**:
        > "02_Material_Writing 워크플로우 실행해줘. 프로젝트 폴더 `/Users/.../Python_Project`의 내용을 분석해서 스타일과 기존 내용을 반영해줘."

3.  **내부 프로세스 (자동)**:
    -   **팀 공통 원칙**: 초보 강사가 교안만 읽고 막힘 없이 설명할 수 있어야 합니다.
    -   **대본 시스템**: 모든 주요 개념에 🗣️ 강사 대본, 실습에 🎙️ 실습 가이드 대본을 포함합니다.
    -   **Phase 1**: A1 (Source Miner) → A2 (Traceability Curator) — 소스 분석 및 추적성
    -   **Phase 2**: A3 (Curriculum Architect) → A4 (Technical Writer) — 골격 및 초안
    -   **Phase 3**: A5(기술 검증) + A6(시각화) + A7(학습 경험 설계) + A9(강사 지원) + A10(차별화) — 5개 병렬. A5는 코드 정확성 검증, A7은 실습 교육 설계를 각각 전담
    -   **Phase 4**: A4 (통합) → A8 (QA Editor) — 최종 검수 (대본 존재 여부 포함, 승인/반려)

4.  **결과물**: `YYYY-MM-DD_강의제목/02_Material/강의교안_v1.0.md`

> 💡 **E2E 자동화**: "전체 파이프라인 실행해줘"를 사용하면 1단계 산출물이 자동으로 입력됩니다.

---

### 3단계: 슬라이드 생성 (Visualizing)

**목표**: 완성된 교안을 발표용 장표 구조로 변환합니다.

1.  **입력 준비**: 2단계에서 완성된 `강의교안_v1.0.md` 또는 교안이 포함된 폴더
2.  **실행 방법**:
    -   **기본 명령** (단일 파일 — 최근 교안 자동 탐색):
        > "03_Slide_Generation 워크플로우를 실행해줘."
    -   **파일 지정 시** (세션 자동 추출):
        > "03_Slide_Generation 워크플로우 실행해줘. 입력 파일은 `02_Material/Day1_AM_환경구축_Antigravity_Python.md` 야." → 출력: `03_Slides/Day1_AM/`
    -   **파일 지정 시** (일반):
        > "03_Slide_Generation 워크플로우 실행해줘. 입력 파일은 `02_Material/강의교안_v1.0.md` 야."
    -   **배치 모드** (폴더 지정 → N개 파일 동적 탐색·순차 처리):
        > "03_Slide_Generation 워크플로우 실행해줘. 교안 폴더는 `/Users/.../ADsP/강의 교안/` 이야."
    -   **로컬 폴더 컨텍스트 반영 시**:
        > "03_Slide_Generation 실행해줘. `/Users/.../Python_Project` 폴더의 이미지 스타일 가이드를 확인하고 적용해줘."

    > **배치 모드**: 폴더 내 `*.md` 파일을 자동 스캔하여 발견된 N개를 순차 처리합니다. 파일 수는 가변(1개~수십 개)이며, 파일당 전체 파이프라인(Phase 1~4)을 1회 실행합니다.

3.  **내부 프로세스 (자동)**:
    -   **Phase 1**: A1 (Content Analyst) → A2 (Terminology Manager) — 분석 및 정규화
    -   **Phase 2**: A3 (Slide Architect) → A7 (Visual Design Director) — 설계
    -   **Phase 3**: A4 (Layout) + A5 (Code Validator) + A8 (Copy Tone) — 병렬 생성/검증, A5 완료 후 → A6 (Lab 카드)
    -   **Phase 4**: A10 (Trace Citation) → A9 (QA Auditor) — 최종 품질 감사 (승인/반려)
    -   *(배치 모드 시)* N개 파일 완료 후 세션 간 교차 검증 (T-BRIDGE 연결성, 용어 일관성)

4.  **결과물**: `YYYY-MM-DD_강의제목/03_Slides/{session}/슬라이드기획안.md` (예: `03_Slides/Day1_AM/슬라이드기획안.md`)

---

### 4단계: PPTX 변환 (HTML 기반)

**목표**: 3단계 슬라이드 기획안을 실제 PowerPoint 파일로 변환합니다.

1.  **입력 준비**: 3단계에서 생성된 `03_Slides/{session}/` 디렉토리의 슬라이드 산출물 (시퀀스 맵, 레이아웃 명세, 디자인 토큰). 세션 서브폴더가 복수인 경우 처리할 세션을 지정합니다.
2.  **실행 방법**:
    -   **기본 명령**:
        > "04_PPTX_Conversion 워크플로우를 실행해줘." (`03_Slides/` 내 세션 서브폴더 자동 탐색 — 1개면 자동 선택, 복수면 확인)

3.  **내부 프로세스 (자동)**:
    -   **B0 (Orchestrator)**: 입력 검증 및 스킬 로드 (`pptx-official`)
    -   **B1 (Slide Parser)**: 마크다운 → 구조화된 JSON 파싱
    -   **B3 (Asset Generator)**: 아이콘/그래디언트/다이어그램 PNG 생성
    -   **B2 (HTML Renderer)**: JSON → html2pptx.js 호환 HTML 변환
    -   **B4 (PPTX Assembler)**: HTML → PPTX 변환, 차트/표/이미지 삽입
    -   **B5 (Visual QA)**: 썸네일 검증, 시각적 결함 검사
    -   **B0**: 승인/반려/재작업 결정

4.  **결과물**: `YYYY-MM-DD_강의제목/04_PPTX/최종_프레젠테이션.pptx`, `변환리포트.md`

---

### 5단계: NanoBanana PPTX (AI 이미지 기반)

**목표**: 3단계 슬라이드 기획안을 Nano Banana Pro AI로 고품질 이미지 슬라이드를 생성하고 PPTX로 조립합니다.

1.  **입력 준비**:
    -   3단계에서 생성된 `03_Slides/{session}/` 디렉토리의 슬라이드 산출물. 세션 서브폴더가 복수인 경우 처리할 세션을 지정합니다.
    -   `GEMINI_API_KEY` 환경변수 설정 필수
2.  **실행 방법**:
    -   **기본 명령**:
        > "05_NanoBanana_PPTX 워크플로우를 실행해줘." (`03_Slides/` 내 세션 서브폴더 자동 탐색 — 1개면 자동 선택, 복수면 확인)

3.  **내부 프로세스 (자동)**:
    -   **C0 (Orchestrator)**: 입력 검증, 스타일/해상도 결정
    -   **C1 (Content Planner)**: 슬라이드 마크다운 → slides_plan.json 구조화
    -   **C2 (Prompt Engineer)**: 슬라이드별 이미지 생성 프롬프트 작성
    -   **C3 (Image Generator)**: Nano Banana Pro 호출, 16:9 PNG 생성
    -   **C4 (PPTX Builder)**: 이미지 삽입 + Speaker Notes → PPTX 조립
    -   **C5 (Visual QA)**: 텍스트 정확성, 스타일 일관성 검사
    -   **C0**: 승인/부분 재생성/전체 반려 결정

4.  **결과물**: `YYYY-MM-DD_강의제목/05_NanoPPTX/최종_프레젠테이션.pptx`, `변환리포트.md`, `index.html` (인터랙티브 뷰어)

---

### 6단계: 슬라이드 생성 프롬프트 생성 (Slide Prompt Generation)

**목표**: 교안을 분석하여 Nano Banana Pro 등 AI 이미지 생성 도구에서 원샷으로 실행 가능한 '슬라이드 생성 프롬프트.md'를 생성합니다.

1.  **입력 준비**:
    -   2단계에서 생성된 `02_Material/` 내 교안 파일(*.md)을 사용합니다.
    -   또는 사용자가 지정한 외부 교안 폴더를 사용합니다.
    -   (선택) 3단계 산출물(`03_Slides/`)이 있으면 IR/Glossary/DesignTokens를 참조하여 품질을 향상시킵니다.
2.  **실행 방법**:
    -   **기본 명령**:
        > "06_SlidePrompt_Generation 워크플로우를 실행해줘." (`02_Material/` 내 `*.md` 파일 자동 탐색)
    -   **외부 폴더 지정 시**:
        > "06_SlidePrompt_Generation 워크플로우 실행해줘. 교안 폴더는 `/Users/.../ADsP/강의 교안/` 이야."
    -   **03 산출물 참조 시**:
        > "06_SlidePrompt_Generation 워크플로우 실행해줘. 교안 폴더는 `/Users/.../강의 교안/` 이고, 03_Slides 산출물도 참조해줘."

3.  **내부 프로세스 (자동)**:
    -   **Phase A**: P0 (Orchestrator) — 교안 폴더 스캔, N개 파일 발견 및 순서 결정
    -   **Phase B**: P1 (Education Structurer, ×N) ∥ P3 (Visual Spec Curator) — 교육 구조 추출 + 비주얼 스펙 준비 [병렬]
    -   **Phase C**: P2 (Slide Prompt Architect, ×N) — 교시별 슬라이드 단위 명세 생성
    -   **Phase D**: P0 (교안별 개별 조립) → P4 (QA Auditor) — 파일별 검증 및 승인/반려

4.  **결과물**: `{project_folder}/06_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (교안별 개별 파일 ×N개)

> **Note**: 입력 파일 수는 고정값이 아닙니다. 교안 폴더에서 발견된 `*.md` 파일 수에 따라 1개~수십 개까지 동적으로 처리합니다.

---

### 7단계: Manus AI 슬라이드 생성

**목표**: 6단계에서 생성된 프롬프트 파일을 Manus AI에 전송하여 Nano Banana Pro로 슬라이드를 생성하고 PPTX를 다운로드합니다.

> **참고**: 이 파이프라인은 별도의 워크플로우 YAML 없이 Python 스크립트(`.agent/scripts/manus_slide.py`)로 직접 실행됩니다.

1.  **사전 설정**:
    -   [manus.im](https://manus.im)에서 Pro/Team 플랜 가입
    -   `.agent/.env`에 `MANUS_API_KEY="sk-..."` 추가

2.  **실행 방법**:
    -   **전체 파일 처리**:
        ```bash
        python .agent/scripts/manus_slide.py {프로젝트폴더경로}
        ```
    -   **단일 파일 처리**:
        ```bash
        python .agent/scripts/manus_slide.py {프로젝트폴더경로} --file Day1_AM
        ```
    -   **드라이런 (API 호출 없이 파일 탐색만)**:
        ```bash
        python .agent/scripts/manus_slide.py {프로젝트폴더경로} --dry-run
        ```

3.  **실행 흐름**:
    -   `06_SlidePrompt/*.md` (N개 프롬프트) → Manus AI POST → 30초 간격 폴링 → PPTX 다운로드

4.  **결과물**: `07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개), `generation_report.json`, `manus_task_log.json`

5.  **주의사항**:
    -   10개 파일 기준 예상 소요 시간: **30분~2시간**
    -   Manus 파일은 **48시간 후 자동 삭제** — 생성 즉시 다운로드 필요
    -   중단 시 `manus_task_log.json`에 중간 결과 저장되어 복구 가능

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
├── 04_PPTX/                 (Pipeline 4 사용 시)
│   ├── 최종_프레젠테이션.pptx
│   ├── 변환리포트.md
│   ├── html/                (슬라이드별 HTML)
│   ├── assets/              (아이콘/그래디언트 PNG)
│   └── thumbnails/          (QA 썸네일)
├── 05_NanoPPTX/             (Pipeline 5 사용 시)
│   ├── 최종_프레젠테이션.pptx
│   ├── 변환리포트.md
│   ├── images/              (슬라이드 PNG)
│   ├── prompts/             (이미지 생성 프롬프트)
│   └── index.html           (인터랙티브 뷰어)
├── 06_SlidePrompt/          (Pipeline 6 사용 시)
│   ├── {세션ID}_{세션제목}_슬라이드 생성 프롬프트.md  (교안별 개별 파일 ×N개)
│   ├── Day1_AM_환경구축_슬라이드 생성 프롬프트.md      (예시)
│   └── Day1_PM_변수와자료형_슬라이드 생성 프롬프트.md  (예시)
├── 07_ManusSlides/          (Pipeline 7 사용 시)
│   ├── {세션ID}_{세션제목}.pptx  (Manus AI 생성 PPTX ×N개)
│   ├── manus_task_log.json      (task_id 로그, 중단 복구용)
│   └── generation_report.json   (생성 결과 리포트)
└── 참고자료/
    └── 원본_기획안.md
```

## Flowith Knowledge Garden 활용 (flowith-kb 스킬)

Flowith Knowledge Garden에 업로드한 참고자료를 **RAG 기반으로 검색**하여 강의 기획 및 교안 작성에 활용할 수 있습니다.

### 사전 설정

#### 1) API 토큰 발급

1. [Flowith.io](https://flowith.io) 로그인
2. Knowledge Garden 메뉴 진입
3. API Settings에서 토큰 발급 (복사)

#### 2) Knowledge Base(KB) ID 확인

> **주의**: KB 목록을 조회하는 API는 제공되지 않습니다. KB ID는 반드시 웹 대시보드에서 수동 확인해야 합니다.

1. [Flowith.io](https://flowith.io) 로그인
2. 좌측 메뉴에서 **Knowledge Garden** 클릭
3. 사용할 지식 정원 선택
4. 상단 URL 또는 설정/공유 화면에서 **KB ID** (UUID 형식) 복사
   - 예시: `ad055591-34bf-4fb8-a5ab-c1ca19e93a6b`
5. 복수의 지식 정원을 사용할 경우 쉼표로 구분하여 등록

#### 3) 사용 가능 모델 확인

다음 API로 현재 지원 모델 목록(32개+)을 조회할 수 있습니다:

```bash
curl -s -X GET "https://edge.flowith.net/external/use/knowledge-base/models" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Host: edge.flowith.net"
```

> **참고**: 공식 문서의 경로(`/seek-knowledge/models`)는 404를 반환합니다. 실제 작동 경로는 위의 `/knowledge-base/models`입니다.

#### 4) `.agent/.env` 설정

```bash
# Flowith API 토큰
FLOWITH_API_TOKEN="your_flowith_api_token_here"

# 지식 베이스 ID (복수 시 쉼표 구분)
FLOWITH_KB_LIST="your_kb_id_here"

# 사용 모델 (기본값: claude-opus-4.6)
FLOWITH_MODEL="claude-opus-4.6"
```

### 사용 가능 모델

| 용도 | 추천 모델 | 특징 |
|------|----------|------|
| **빠른 팩트 수집** (다수 질의) | `gemini-3-pro-preview` | 평균 ~33초, 안정적 |
| **심층 분석** (교안 품질 자료) | `claude-opus-4.6` | 평균 ~100초, 구조화·비유·시각화 탁월 |
| **비용 효율** | `gpt-4.1-mini` | 가장 저렴, 간단한 팩트 확인용 |

> **전체 지원 모델**: `claude-opus-4.6`, `claude-opus-4.5`, `claude-4.1-opus`, `claude-4-sonnet`, `gemini-3-pro-preview`, `gemini-2.5-pro`, `gpt-5`, `gpt-4.1-mini`, `deepseek-reasoner` 등 60+ 모델

---

## 팁
- **자동 입력 감지**: 2단계 이후 워크플로우 실행 시 입력 파일을 생략하면, 에이전트가 자동으로 이전 단계의 결과물을 찾아서 작업을 수행합니다.
- **수정 요청**: 각 단계가 끝날 때마다 에이전트가 결과물을 보여줍니다. 마음에 들지 않는 부분은 "A4 에이전트에게 어조를 좀 더 친근하게 바꾸라고 해줘"와 같이 구체적으로 피드백하면 수정해줍니다.
- **NotebookLM 활용**: 자료가 많을수록 `A1` 에이전트의 성능이 좋아집니다. 관련 PDF나 문서를 미리 NotebookLM에 올려두세요.
- **Flowith KB 활용**: NotebookLM 대안 또는 보완으로, Flowith Knowledge Garden에 참고자료를 업로드하면 API를 통한 자동 검색이 가능합니다. 특히 A1 Source Miner 단계에서 효과적입니다.
- **Pipeline 4 vs 5 vs 7**: 코드 중심 → 04(HTML 기반), 로컬 AI 이미지 → 05(Gemini API), 클라우드 AI 생성 → 07(Manus API).
- **Pipeline 6 → 7 연계**: 6단계에서 프롬프트 생성 후 7단계에서 PPTX 자동 생성. 교안에서 최종 PPTX까지 자동화됩니다.
- **E2E 통합 실행**: "전체 파이프라인 실행해줘"로 1~6단계를 순차 자동 실행할 수 있습니다.
- **Manus 파일 보존**: Manus에 업로드된 파일은 48시간 후 자동 삭제됩니다. 생성 즉시 다운로드하세요.
