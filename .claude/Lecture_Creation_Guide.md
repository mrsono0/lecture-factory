# 강의 생성 시스템 사용자 가이드 (Claude Code Edition)

이 문서는 Lecture Factory 시스템의 **사용법**을 안내합니다.
7개 파이프라인을 슬래시 커맨드로 실행하여 강의 기획부터 PPTX까지 생성할 수 있습니다.

> 시스템 아키텍처, 에이전트 파이프라인 상세, 커맨드 매핑 등 기술적 내용은 [`Developer_Guide.md`](./Developer_Guide.md)를 참조하세요.

---

## 전체 프로세스 요약

| 단계 | 목표 | 슬래시 커맨드 | 주요 산출물 |
|---|---|---|---|
| **1. 기획** | 주제 분석 → 커리큘럼 확정 | `/project:lecture-plan` | `01_Planning/강의구성안.md` |
| **2. 집필** | 상세 교안 및 코드 작성 | `/project:material-write` | `02_Material/강의교안_v1.0.md` |
| **3. 시각화** | 슬라이드 스토리보드 기획 | `/project:slide-gen` | `03_Slides/{session}/슬라이드기획안.md` |
| **4. 프롬프트 생성** | 원샷 슬라이드 생성 프롬프트 | `/project:slide-prompt` | `04_SlidePrompt/...프롬프트.md` (×N개) |
| **5. PPTX 변환** | HTML 기반 PPTX 생성 | `/project:pptx-convert` | `05_PPTX/최종_프레젠테이션.pptx` |
| **6. AI PPTX** | AI 이미지 기반 고품질 PPTX | `/project:nano-pptx` | `06_NanoPPTX/최종_프레젠테이션.pptx` |
| **7. Manus 슬라이드** | Manus AI로 PPTX 생성 | `/project:manus-slide` | `07_ManusSlides/*.pptx` (×N개) |
| **전체 자동화** | 1, 2, 3, 4단계 자동 연결 실행 | `/project:lecture-factory` | 기획안→교안→슬라이드→프롬프트 |

> **5단계, 6단계, 7단계는 택 1**: 코드 중심 → 05(HTML 기반, 빠름) / 로컬 AI 이미지 → 06(Gemini API) / 클라우드 AI 생성 → 07(Manus API, 고품질)
>
> **4 → 7 연계**: `/project:slide-prompt`로 프롬프트 생성 후 `/project:manus-slide`로 PPTX 생성. 교안에서 최종 PPTX까지 자동화됩니다.

---

## 실행 방법 (2가지)

### 방법 1: 슬래시 커맨드 (권장)

```bash
/project:lecture-plan 입력 파일은 AI-native_파이썬기초.md야.
```

`$ARGUMENTS`에 입력 파일, NotebookLM URL, 로컬 폴더 등을 자유롭게 기술합니다.

```bash
/project:lecture-factory 파이썬기초.md 참고할 로컬 폴더는 참고자료 이고, 참고할 NotebookLM 주소는 https://notebooklm.google.com/notebook/45baed65-b49f-4204-a13a-5a4feda14b0a 야.
```
위와 같이 마스터 명령어 하나로 1단계(기획) → 2단계(집필) → 3단계(시각화) → 4단계(슬라이드 프롬프트) 총 4개 단계를 순차적으로 자동 실행할 수 있습니다. 각 단계가 끝나면 중간 산출물을 검증하고 다음 단계로 알아서 넘어갑니다. (5·6·7단계 PPTX 생성은 별도 실행)

단일 단계만 실행하고 싶을 때는 아래처럼 개별 명령어를 사용합니다:

### 방법 2: 자연어 실행 (기존 호환)

```
01_Lecture_Planning 워크플로우를 실행해줘. 입력 파일은 AI-native_파이썬기초.md야.
```

커스텀 에이전트의 `description`에 의해 자동 위임됩니다.

---

## 단계별 상세 가이드

### 1단계: 강의 구성안 작성 (Planning)

**목표**: 모호한 아이디어를 구체적인 커리큘럼으로 구조화합니다.

#### 입력 파일 준비

강의 주제, 대상, 목표가 담긴 초안 문서를 준비합니다.

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
| 7 | **톤·수준** | 상세 대본 기반 구어체 (~해요, ~입니다), 비유 중심 설명 + 'AI 시대의 서사' 톤, 모든 주요 개념에 🗣️ 강사 대본 / 실습에 🎙️ 실습 가이드 대본 포함, 실습 비율 60%↑, AI-first 학습 |
| 8 | **전제 조건** | 프로그래밍 경험 없음, IT 리터러시 있음, AI 프롬프트 코딩 |

> 기본값 적용 시 강의구성안에 `[기본값 적용]`으로 표기됩니다.

#### 입력 파일 템플릿

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

#### 실행 명령

```bash
# 기본
/project:lecture-plan 입력 파일은 AI-native_파이썬기초.md야.

# NotebookLM 포함
/project:lecture-plan 입력 파일은 AI-native_파이썬기초.md이고, 참고할 NotebookLM 주소는 https://notebooklm.google.com/... 야.

# 로컬 폴더 지정
/project:lecture-plan 참고할 로컬 폴더는 /Users/.../Python_Project 야. 이 폴더의 모든 파일을 먼저 분석해줘.
```

#### 결과물

`{YYYY-MM-DD_강의제목}/01_Planning/강의구성안.md`

> 💡 **E2E 자동화**: 1, 2, 3, 4단계를 한 번에 실행하려면 `/project:lecture-factory`를 사용하세요. 각 단계의 입력 파일과 URL이 자동으로 전달됩니다.

---

### 2단계: 강의 교안 작성 (Writing)

**목표**: 확정된 구성안을 바탕으로 실제 수업이 가능한 상세 교안을 작성합니다.

#### 입력 준비

- 1단계에서 생성된 `강의구성안.md` (미지정 시 자동 탐색)
- (선택) NotebookLM URL, 로컬 참고자료 폴더

#### 실행 명령

```bash
# 기본 (이전 단계 결과물 자동 탐색)
/project:material-write

# NotebookLM 포함
/project:material-write 입력 파일은 강의구성안.md이고, 참고할 NotebookLM URL은 https://notebooklm.google.com/... 야.

# 로컬 폴더 지정
/project:material-write 프로젝트 폴더 /Users/.../Python_Project의 내용을 분석해서 스타일과 기존 내용을 반영해줘.
```

#### 결과물

`{YYYY-MM-DD_강의제목}/02_Material/강의교안_v1.0.md`

> 💡 **E2E 자동화**: `/project:lecture-factory`를 사용하면 1단계 산출물이 자동으로 입력됩니다.

---

### 3단계: 슬라이드 생성 (Visualizing)

**목표**: 완성된 교안을 발표용 슬라이드 구조로 변환합니다.

**지원 모드**: 단일 파일 / 배치 (N개 파일 순차 처리)

#### 실행 명령

```bash
# 기본 (최근 교안 자동 탐색)
/project:slide-gen

# 파일 지정 (세션 자동 추출 — Day1_AM)
/project:slide-gen 입력 파일은 02_Material/Day1_AM_환경구축_Antigravity_Python.md 야.

# 배치 모드 (폴더 내 N개 파일 순차 처리)
/project:slide-gen 교안 폴더는 /Users/.../ADsP/강의 교안/ 이야.
```

> **배치 모드**: 폴더 내 `*.md` 파일을 자동 스캔하여 N개를 순차 처리합니다. 파일 수는 가변(1~수십 개).

#### 결과물 (세션별)

`{YYYY-MM-DD_강의제목}/03_Slides/{session}/슬라이드기획안.md`

> 💡 **E2E 자동화**: `/project:lecture-factory`를 사용하면 2단계 교안이 자동으로 입력됩니다.

---

### 4단계: 슬라이드 생성 프롬프트 생성

**목표**: 교안을 분석하여 AI 이미지 생성 도구용 원샷 프롬프트를 교안별 개별 파일로 생성합니다.

#### 실행 명령

```bash
# 기본 (02_Material/ 자동 탐색)
/project:slide-prompt

# 외부 폴더 지정
/project:slide-prompt 교안 폴더는 /Users/.../ADsP/강의 교안/ 이야.

# 03 산출물 참조 포함
/project:slide-prompt 교안 폴더는 /Users/.../강의 교안/ 이고, 03_Slides 산출물도 참조해줘.
```

#### 결과물

`{project_folder}/04_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개)

---

### 5단계: PPTX 변환 (HTML 기반)

**목표**: 3단계 슬라이드 기획안을 PowerPoint 파일로 변환합니다.

#### 실행 명령

```bash
# 기본 (03_Slides/ 자동 탐색 — 세션 1개면 자동 선택, 복수면 확인)
/project:pptx-convert
```

#### 결과물

- `{YYYY-MM-DD_강의제목}/05_PPTX/최종_프레젠테이션.pptx`
- `05_PPTX/변환리포트.md`

---

### 6단계: NanoBanana PPTX (AI 이미지 기반)

**목표**: Nano Banana Pro AI로 고품질 이미지 슬라이드를 생성하고 PPTX로 조립합니다.

**필수 환경변수**: `GEMINI_API_KEY`

#### 실행 명령

```bash
# 기본 (03_Slides/ 자동 탐색)
/project:nano-pptx
```

#### 결과물

- `{YYYY-MM-DD_강의제목}/06_NanoPPTX/최종_프레젠테이션.pptx`
- `06_NanoPPTX/변환리포트.md`
- `06_NanoPPTX/index.html` (인터랙티브 뷰어)

---

### 7단계: Manus AI 슬라이드 생성

**목표**: 4단계에서 생성된 프롬프트 파일을 Manus AI에 전송하여 Nano Banana Pro로 슬라이드를 생성하고 PPTX를 다운로드합니다.

**필수 환경변수**: `MANUS_API_KEY`
**필수 요건**: Manus Pro 또는 Team 플랜 (유료)

#### 사전 설정

1. [manus.im](https://manus.im) 에서 Pro/Team 플랜 가입
2. 대시보드 → API Integration → API Key 생성
3. `.agent/.env`에 `MANUS_API_KEY="sk-..."` 추가
4. Manus MCP 서버 등록 (1회만):
   ```bash
   claude mcp add manus-mcp -s project -e MANUS_API_KEY="your-key" -- npx manus-mcp
   ```

#### 실행 명령

```bash
# 슬래시 커맨드 (Claude Code 내에서)
/project:manus-slide

# 전체 파일 처리 (04_SlidePrompt/ 내 모든 프롬프트)
python .agent/scripts/manus_slide.py 2026-02-19_AI-native_데이터사이언스기초

# 단일 파일만 처리 (세션ID로 지정)
python .agent/scripts/manus_slide.py 2026-02-19_AI-native_데이터사이언스기초 --file Day1_AM

# 단일 파일만 처리 (한글 키워드로 지정)
python .agent/scripts/manus_slide.py 2026-02-19_AI-native_데이터사이언스기초 --file 환경구축

# 복수 파일 선택 처리
python .agent/scripts/manus_slide.py 2026-02-19_AI-native_데이터사이언스기초 -f Day1_AM Day2_PM Day3_AM

# 드라이런 — API 호출 없이 파일 탐색만 확인
python .agent/scripts/manus_slide.py 2026-02-19_AI-native_데이터사이언스기초 --dry-run

# 프로젝트 폴더 자동 탐색 (최신 날짜 프로젝트 자동 선택)
python .agent/scripts/manus_slide.py
```

> **`--file` / `-f` 옵션**: 부분 매칭을 지원합니다. `Day1_AM`, `환경구축`, `CRISP-DM` 등 파일명의 일부만 입력해도 매칭됩니다.

#### CLI 옵션 레퍼런스

| 옵션 | 설명 |
|------|------|
| `--file PATTERN` / `-f` | 특정 파일/세션ID만 처리 |
| `--no-split` | 교시 분할 없이 원본 전체 제출 |
| `--resume` | 이전 실행에서 완료된 파일 자동 스킵 |
| `--dry-run` | API 호출 없이 파일 탐색/분할 판정만 확인 |
| `--quiet` / `-q` | 경고·에러만 출력 |
| `--verbose` / `-v` | DEBUG 레벨 상세 로그 |

#### 결과물

- `{project_folder}/07_ManusSlides/{세션ID}_{세션제목}.pptx` (×N개)
- `07_ManusSlides/generation_report.json` — 성공/실패 현황 리포트
- `07_ManusSlides/manus_task_log.json` — Manus task_id 로그 (중단 복구용)

#### 주의사항

- 10개 파일 기준 예상 소요 시간: **30분~2시간**
- Manus 파일은 **48시간 후 자동 삭제** — 생성 즉시 다운로드 필요
- 중단 시 `manus_task_log.json`에 중간 결과가 저장되어 복구 가능
- API 호출 비용이 프롬프트 수에 비례하여 발생

#### 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `API Key를 찾을 수 없습니다` | 환경변수 미설정 | `.agent/.env`에 `MANUS_API_KEY` 추가 |
| `401 Unauthorized` | API Key 만료/잘못됨 | Manus 대시보드에서 새 키 발급 |
| `타임아웃 (30분 초과)` | Manus 서버 부하 | `manus_task_log.json`의 task_id로 웹에서 확인 |
| `다운로드 파일 없음` | 파일 URL 미반환 | shareable_link로 웹에서 수동 다운로드 |

---

## 폴더 구조 (자동 생성)

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

> 상세 폴더 구조(중간 산출물 포함)는 [`Developer_Guide.md`](./Developer_Guide.md)를 참조하세요.

---

## 환경 변수

`.agent/.env`에 설정 (`.agent/.env.template` 참조):

| 변수 | 필수 | 용도 |
|---|---|---|
| `GEMINI_API_KEY` | Pipeline 6 필수 | Google AI API Key |
| `TAVILY_API_KEY` | Pipeline 1 필수 | Tavily 검색 API |
| `MANUS_API_KEY` | Pipeline 7 필수 | Manus AI API Key (Pro/Team 플랜) |
| `FLOWITH_API_TOKEN` | 선택 | Flowith Knowledge Garden API |
| `FLOWITH_KB_LIST` | 선택 | 지식 베이스 ID |

> 환경 변수 상세(사용처, 선택 API 키 포함)는 [`Developer_Guide.md`](./Developer_Guide.md)를 참조하세요.

---

## Flowith Knowledge Garden 활용

Flowith Knowledge Garden에 업로드한 참고자료를 **RAG 기반으로 검색**하여 활용할 수 있습니다.

### 사전 설정

1. [Flowith.io](https://flowith.io) 로그인 → Knowledge Garden → API Settings에서 토큰 발급
2. 사용할 지식 정원의 **KB ID** (UUID 형식) 확인
3. `.agent/.env`에 `FLOWITH_API_TOKEN`, `FLOWITH_KB_LIST` 설정

### 추천 모델

| 용도 | 모델 | 특징 |
|------|------|------|
| 빠른 팩트 수집 | `gemini-3-pro-preview` | ~33초, 안정적 |
| 심층 분석 | `claude-opus-4.6` | ~100초, 구조화 탁월 |
| 비용 효율 | `gpt-4.1-mini` | 가장 저렴, 간단한 팩트 확인 |

---

## 팁

- **자동 입력 감지**: 2단계 이후 입력 파일을 생략하면 이전 단계 결과물을 자동 탐색합니다.
- **에이전트별 피드백**: "A4 에이전트에게 어조를 좀 더 친근하게 바꾸라고 해줘"처럼 구체적으로 지시 가능합니다.
- **NotebookLM**: 참고자료를 많이 올릴수록 A1 에이전트의 성능이 향상됩니다.
- **Pipeline 5 vs 6 vs 7**: 코드 중심 → 05(HTML 기반) / 로컬 AI 이미지 → 06(Gemini API) / 클라우드 AI 생성 → 07(Manus API)
- **Pipeline 4 → 7 연계**: `/project:slide-prompt` → `/project:manus-slide` 순서로 실행하면 교안에서 최종 PPTX까지 자동화됩니다.
- **Manus 파일 보존**: Manus에 업로드된 파일은 48시간 후 자동 삭제됩니다. 생성 즉시 다운로드하세요.
- **E2E 통합 실행**: `/project:lecture-factory` 하나로 1, 2, 3, 4단계를 순차 자동 실행할 수 있습니다. (5·6·7단계 PPTX 생성은 별도 실행)
