# AGENTS.md

This file defines the operating rules and workflows for the Lecture Factory agent team.
All agents MUST follow these instructions when executing tasks.

## Essential Rule: Context Analysis (MANDATORY)

**When the user provides a local folder path for any task:**
1.  **Stop** immediately before proceeding with the main workflow.
2.  **Analyze** the contents of the provided folder.
    -   Use `list_dir` to see the file structure.
    -   Use `read_file` (or similar tools) to read **ALL** files within that folder (recursive if necessary, but prioritize root and relevant subdirectories).
3.  **Understand** the context, project status, existing content, and style guides from these files.
4.  **Proceed** with the requested task only AFTER this analysis is complete.
5.  **Confirm** to the user that you have analyzed the folder contents.

---

## Workflow Overview

The Lecture Factory system consists of **seven** main pipelines과 **1개의 E2E 통합 실행** 명령을 제공합니다:

| # | Pipeline | Workflow File | Goal | Output |
|---|---|---|---|---|
| 1 | **Lecture Planning** | `01_Lecture_Planning.yaml` | Create a structured curriculum from raw ideas | `01_Planning/강의구성안.md` |
| 2 | **Material Writing** | `02_Material_Writing.yaml` | Write detailed lecture material (text + code) | `02_Material/강의교안_v1.0.md` |
| 3 | **Slide Generation** | `03_Slide_Generation.yaml` | Create presentation slide storyboard | `03_Slides/{session}/슬라이드기획안.md` |
| 4 | **PPTX Conversion** | `04_PPTX_Conversion.yaml` | Convert slide storyboard to PowerPoint file | `04_PPTX/최종_프레젠테이션.pptx` |
| 5 | **NanoBanana PPTX** | `05_NanoBanana_PPTX.yaml` | AI image-based high-quality slide generation | `05_NanoPPTX/최종_프레젠테이션.pptx` |
| 6 | **Slide Prompt Generation** | `06_SlidePrompt_Generation.yaml` | Generate one-shot slide generation prompts from lecture materials | `06_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개) |
| 7 | **Manus Slide Generation** | `.agent/scripts/manus_slide.py` | Send slide prompts to Manus AI (Nano Banana Pro) and download PPTX | `07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개) |
| E2E | **End-to-End** | — (마스터 오케스트레이터) | 1, 2, 3, 6단계 순차 자동 실행 | 기획안→교안→슬라이드→프롬프트 |

> **Note**: Pipelines 4, 5, 7 are alternative PPTX generation methods:
> - **04**: HTML-based (faster, code-heavy slides)
> - **05**: Gemini AI image (higher visual quality, design-heavy)
> - **07**: Manus AI cloud (requires Manus Pro plan)

---

## Execution Methods

Lecture Factory 파이프라인은 사용 중인 AI 에이전트 인터페이스(Gemini CLI 또는 Claude Code)에 따라 실행 명령어가 다릅니다.

- **Gemini CLI 환경**: `/skill lecture-plan` 등 스킬 기반 실행. 상세 가이드는 `.gemini/Lecture_Creation_Guide.md` 참조.
- **Claude Code 환경**: `/project:lecture-plan` 등 슬래시 커맨드 기반 실행. E2E 통합 실행은 `/project:lecture-factory`. 상세 가이드는 `.claude/Lecture_Creation_Guide.md` 참조.

두 환경 모두 입력 파일 생략 시 이전 단계 결과물을 자동 탐색합니다. Claude Code에서는 `/project:lecture-factory` 커맨드로 1, 2, 3, 6단계를 순차 자동 실행할 수 있습니다. (4·5·7단계 PPTX 생성은 별도 실행)

---

## Project Folder Structure

All outputs are organized under a date-prefixed project folder:

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
│   └── Day1_PM/ (동일 구조)
├── 04_PPTX/                 (Pipeline 4)
├── 05_NanoPPTX/             (Pipeline 5)
├── 06_SlidePrompt/          (Pipeline 6)
│   └── {세션ID}_{세션제목}_슬라이드 생성 프롬프트.md  (×N개)
├── 07_ManusSlides/          (Pipeline 7)
│   ├── {세션ID}_{세션제목}.pptx  (×N개)
│   ├── manus_task_log.json
│   └── generation_report.json
└── 참고자료/
    └── 원본_기획안.md
```

---

## Agent Teams

각 에이전트의 상세 역할은 `.agent/agents/{team}/` 프롬프트 파일에 정의되어 있습니다.

### Team 1: Planner (01_planner) — 7 agents
**팀 공통 원칙**: 기획 산출물(강의구성안)만으로 교안 작성 팀이 막힘 없이 집필을 시작할 수 있어야 합니다.
**Flow**: A0 → A1 → A5B → A3 → A2 → A7 → A5A → A0 (승인/반려)
- A5B(학습자 분석) → A3(커리큘럼 설계): A5B 산출물을 A3의 입력으로 참조
- 1일 4시간 초과 시 AM/PM 분할 설계, 60~90분 단위 하위 세션 세분화

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

### Team 4: PPTX Converter (04_pptx_converter) — 6 agents
**Flow**: B0 → B1 → B3 → B2 → B4 → B5 → B0 (승인/반려)
**Tech**: html2pptx.js (Playwright + PptxGenJS), Sharp, react-icons

### Team 5: NanoBanana (05_nanopptx) — 6 agents
**Flow**: C0 → C1 → C2 → C3 → C4 → C5 → C0 (승인/부분 재생성/반려)
**Required**: `GEMINI_API_KEY`

### Team 6: Slide Prompt Generator (06_prompt_generator) — 5 agents
**Flow**:
- Phase A: P0 (입력 탐색, N개 스캐폴딩)
- Phase B: P1 (교육 구조 ×N) ∥ P3 (비주얼 스펙) [병렬]
- Phase C: P2 (슬라이드 명세 ×N)
- Phase D: P0 (조립) → P4 (QA)

> **Pipeline 6 정책**: §⑥ 교안 원문 섹션에 교안 마크다운 전문을 삽입합니다. 상세 규칙은 P0/P2 에이전트 명세 참조.

---

## Integrated Quality Perspective

All review and decision-making applies these **3 expert perspectives simultaneously**:

1.  **Senior Fullstack Developer**: 코드 정확성, 실행 가능성, 파일 경로 명확성
2.  **Technical Education Content Designer**: 교육 흐름 논리성, 용어 설명, 슬라이드당 핵심 개념 1개
3.  **Presentation Designer**: 시각적 일관성, 레이아웃 균형, 가독성, 디자인 토큰 준수

---

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Pipeline 1, 5 | Google AI API Key |
| `TAVILY_API_KEY` | Pipeline 1 | Tavily 검색 API Key |
| `MANUS_API_KEY` | Pipeline 7 | Manus AI API Key (각 환경의 `.env`에 설정) |

> 전체 환경변수 목록 및 설정 방법은 각 인터페이스의 `Lecture_Creation_Guide.md` (예: `.gemini/` 또는 `.claude/`) 가이드 문서를 참조하세요.

---

## Output Standards

-   **Language**: All outputs must be in **Korean** unless specified otherwise (기술 용어 제외).
-   **Format**: Markdown with clear headers and code blocks.
-   **Code**: Python code must be executable and follow PEP 8.
-   **Tone**: 상세 대본 기반 구어체 (~해요, ~입니다). 교안에는 🗣️ 강사 대본과 🎙️ 실습 대본을 포함하며, 'AI 시대의 서사'와 같은 비유적 톤을 유지합니다.

---

## Tips

- **Auto Input Detection**: 2단계 이후 입력 파일 생략 시 이전 단계 결과물을 자동 탐색합니다.
- **Agent-specific Feedback**: "A4 에이전트에게 어조를 좀 더 친근하게 바꿔줘"와 같이 특정 에이전트에 지시 가능합니다.
- **Pipeline 4 vs 5 vs 7**: 코드 중심 → 04, 로컬 AI 이미지 → 05, 클라우드 AI → 07.
