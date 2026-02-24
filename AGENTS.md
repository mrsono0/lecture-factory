# AGENTS.md

This file defines the operating rules and workflows for the Lecture Factory agent team.
All agents MUST follow these instructions when executing tasks.
> **관련 문서**: 사용법은 각 인터페이스의 `Lecture_Creation_Guide.md`를, 시스템 구조 상세는 `Developer_Guide.md`를 참조하세요. (`.claude/` 또는 `.agent/` 디렉토리)

## Essential Rule: Context Analysis (MANDATORY)

**When the user provides a local folder path for any task:**
1.  **Stop** immediately before proceeding with the main workflow.
2.  **Analyze** the contents of the provided folder.
    -   Use `list_dir` to see the file structure.
    -   Use `read_file` (or similar tools) to read **ALL** files within that folder (recursive if necessary, but prioritize root and relevant subdirectories).
3.  **Understand** the context, project status, existing content, and style guides from these files.
4.  **Proceed** with the requested task only AFTER this analysis is complete.
5.  **Confirm** to the user that you have analyzed the folder contents.

### STOP & Replan Triggers

**Stop immediately and re-plan if:**
- Task scope changes mid-implementation
- Discovery of conflicting existing patterns
- 2+ consecutive failed fix attempts
- User's design seems flawed or suboptimal

**Then**: Raise concern concisely → Propose alternative → Wait for confirmation

---

## Plan Node Default (MANDATORY for Complex Tasks)

**Before starting any task with 3+ steps or architectural decisions:**
1. **Stop** and enter Plan Mode - write detailed spec first
2. **Break down** into atomic, verifiable steps
3. **Identify** dependencies, risks, and required tools
4. **Get confirmation** on approach before implementation

**DO NOT proceed to implementation until plan is approved.**

When to plan:
- 3+ steps required
- Cross-module changes
- New patterns or unfamiliar code
- User explicitly asks for plan

---

## Task Management Protocol (MANDATORY)

**Every multi-step task (2+ steps) MUST:**

1. **Create todos IMMEDIATELY** upon receiving request
   - Use atomic, actionable items
   - Maximum ONE task `in_progress` at any time

2. **Mark `in_progress`** before starting each step

3. **Mark `completed`** immediately after finishing
   - NEVER batch completions
   - Real-time tracking is mandatory

4. **Update on scope change** before proceeding

### Anti-patterns (BLOCKING violations)
- Skipping todos on multi-step tasks
- Batch-completing multiple todos
- Proceeding without marking `in_progress`
- Finishing without completing todos


---

## Workflow Overview

The Lecture Factory system consists of **eight** main pipelines과 **1개의 E2E 통합 실행** 명령을 제공합니다:

| # | Pipeline | Workflow File | Goal | Output |
|---|---|---|---|---|
| 1 | **Lecture Planning** | `01_Lecture_Planning.yaml` | Create a structured curriculum from raw ideas | `01_Planning/강의구성안.md` |
| 2 | **Material Writing** | `02_Material_Writing.yaml` | Write detailed lecture material (text + code) | `02_Material/강의교안_v1.0.md` |
| 3 | **Slide Generation** | `03_Slide_Generation.yaml` | Create presentation slide storyboard | `03_Slides/{session}/슬라이드기획안.md` |
| 4 | **Slide Prompt Generation** | `04_SlidePrompt_Generation.yaml` | Generate one-shot slide generation prompts from lecture materials | `04_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개) |
| 5 | **PPTX Conversion** | `05_PPTX_Conversion.yaml` | Convert slide storyboard to PowerPoint file | `05_PPTX/최종_프레젠테이션.pptx` |
| 6 | **NanoBanana PPTX** | `06_NanoBanana_PPTX.yaml` | AI image-based high-quality slide generation | `06_NanoPPTX/최종_프레젠테이션.pptx` |
| 7 | **Manus Slide Generation** | `07_Manus_Slide.yaml` | Send slide prompts to Manus AI (Nano Banana Pro) with session-based chunking and download PPTX | `07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개) |
| 8 | **Log Analysis** | `08_Log_Analysis.yaml` | Analyze pipeline execution logs for bottlenecks, cost, and optimization | `.agent/dashboard/log_analysis_{date}.md` |
| E2E | **End-to-End** | — (마스터 오케스트레이터) | 1, 2, 3, 4단계 순차 자동 실행 | 기획안→교안→슬라이드→프롬프트 |

> **Note**: Pipelines 5, 6, 7 are alternative PPTX generation methods:
> - **05**: HTML-based (faster, code-heavy slides)
> - **06**: Gemini AI image (higher visual quality, design-heavy)
> - **07**: Manus AI cloud (requires Manus Pro plan)

---

## Execution Methods

Lecture Factory 파이프라인은 사용 중인 AI 에이전트 인터페이스(Gemini CLI 또는 Claude Code)에 따라 실행 명령어가 다릅니다.

- **Gemini CLI 환경**: `/skill lecture-plan` 등 스킬 기반 실행. 상세 가이드는 `.gemini/Lecture_Creation_Guide.md` 참조.
- **Claude Code 환경**: `/project:lecture-plan` 등 슬래시 커맨드 기반 실행. E2E 통합 실행은 `/project:lecture-factory`. 상세 가이드는 `.claude/Lecture_Creation_Guide.md` 참조.

두 환경 모두 입력 파일 생략 시 이전 단계 결과물을 자동 탐색합니다. Claude Code에서는 `/project:lecture-factory` 커맨드로 1, 2, 3, 4단계를 순차 자동 실행할 수 있습니다. (5·6·7단계 PPTX 생성은 별도 실행)

---

## Project Folder Structure

All outputs are organized under a date-prefixed project folder:

```text
YYYY-MM-DD_강의제목/
├── 01_Planning/강의구성안.md
├── 02_Material/강의교안_v1.0.md, src/, images/
├── 03_Slides/{session}/슬라이드기획안.md (Phase별 산출물)
├── 04_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md (×N개)
├── 05_PPTX/ | 06_NanoPPTX/ | 07_ManusSlides/ (택1)
└── 참고자료/원본_기획안.md
```

---

## Model Configuration

> **모델 상세 설정**: `.opencode/oh-my-opencode.jsonc` — 에이전트별 모델 배정, 카테고리별 prompt_append, 품질 variant 설정

에이전트 모델 라우팅은 oh-my-opencode 설정 파일이 담당합니다. AGENTS.md는 워크플로우 규칙만 다룹니다.

---

## Continuous Improvement System

### lessons.md (Project Memory)

**위치**: 프로젝트 루트 또는 `.agent/lessons.md`

**기록 내용**:
- 수정받은 실수 및 피드백
- 스타일 가이드 위반 사례
- 반복되는 패턴과 교훈

**사용 방법**:
1. 세션 시작 시 `lessons.md` 자동 로드
2. 이전 교훈을 현재 작업에 적용
3. 새로운 교훈 지속적 추가

### Self-Review Checklist

완료 표시 전 반드시 자문:
- [ ] 이 코드를 Staff Engineer가 승인할 수 있는가?
- [ ] 남겨진 TODO나 임시방편이 있는가?
- [ ] 최소한의 변경으로 목표를 달성했는가?
- [ ] 근본 원인을 찾아 수정했는가?

---

## Verification Before Done

**작업은 다음 조건을 만족할 때까지 완료되지 않음:**

1. **모든 계획된 todo 항목**이 `[completed]`로 표시됨
2. **변경된 파일에서 LSP diagnostics**가 깨끗함
3. **빌드/테스트**가 통과함 (해당 시)
4. **사용자의 원래 요청**이 완전히 충족됨
5. **자체 검증**: "내가 Staff Engineer라면 이걸 승인할까?"

**검증 실패 시:**
1. 즉시 실패 원인 수정
2. 사전 존재하던 문제는 수정하지 않음 (사용자 요청 시에만)
3. 보고: "완료. 참고: N개의 사전 존재 문제는 이번 변경과 무관함"

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
| `GEMINI_API_KEY` | Pipeline 1, 6 | Google AI API Key |
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
- **Pipeline 5 vs 6 vs 7**: 코드 중심 → 05, 로컬 AI 이미지 → 06, 클라우드 AI → 07.

---

## Git Branching Rule (MANDATORY)

**`.agent/` 또는 `.claude/` 디렉토리 내 파일을 수정하는 모든 작업에 적용됩니다.**

에이전트 설정, 워크플로, 커맨드, 프롬프트 등 프로젝트 인프라 파일은 반드시 브랜치 워크플로를 따릅니다.

### Workflow

1. **브랜치 생성**: 작업 시작 전 `main`에서 feature 브랜치를 생성합니다.
   - 네이밍: `feat/<간단한-설명>` (예: `feat/update-writer-agent`, `feat/add-slide-command`)
   - 버그 수정: `fix/<간단한-설명>`
   - 구조 변경: `refactor/<간단한-설명>`
2. **작업 수행**: 브랜치에서 파일 수정 및 커밋합니다.
3. **머지**: 작업 완료 후 `main`으로 머지합니다. (`--no-ff` 권장)
4. **푸시**: `main` 브랜치를 원격에 푸시합니다.
5. **정리**: 머지 완료된 feature 브랜치를 삭제합니다.

### Scope

| 대상 경로 | 브랜치 필수 |
|-----------|:-----------:|
| `.agent/agents/` | O |
| `.agent/workflows/` | O |
| `.agent/scripts/` | O |
| `.agent/skills/` | O |
| `.claude/agents/` | O |
| `.claude/commands/` | O |
| `.claude/Lecture_Creation_Guide.md` | O |
| `.Claude/oh-my-Claude.jsonc` | O |
| `AGENTS.md` | O |
| 그 외 파일 (`.gitignore` 등) | X (main 직접 커밋 가능) |

### Example

```bash
# 1. 브랜치 생성
git checkout -b feat/update-writer-agent

# 2. 작업 & 커밋
git add .agent/agents/02_writer/A4_Technical_Writer.md
git commit -m "feat: A4 Technical Writer 대본 스타일 가이드 추가"

# 3. main 머지 & 푸시
git checkout main
git merge --no-ff feat/update-writer-agent
git push

# 4. 브랜치 정리
git branch -d feat/update-writer-agent
```

> **Note**: 별도 지시 없어도 AI 에이전트는 위 경로 수정 시 이 워크플로를 자동으로 수행합니다.
