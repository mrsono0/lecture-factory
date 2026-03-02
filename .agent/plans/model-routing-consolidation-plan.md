# 모델 라우팅 통합 작업 계획서

> **작성일**: 2026-03-02
> **상태**: 검토 대기 (사용자 승인 후 실행)
> **범위**: 모든 파이프라인 (P01–P08)의 모델 라우팅 정보를 `oh-my-opencode.jsonc` 1곳으로 집중화

---

## 1. 문제 정의

### 1.1 현황: 동일 정보가 4곳에 분산

| # | 위치 | 역할 | 문제 |
|---|------|------|------|
| ① | `config.json` ×8개 | 에이전트→카테고리 매핑 | **사문화** — Python/bash에서 파싱 0건, A0도 실제로는 인라인 테이블 사용 |
| ② | `oh-my-opencode.jsonc` | 카테고리→모델 매핑 (정본) | 19개 카테고리 중 고유 모델 설정은 9개뿐 — 10개 중복 |
| ③ | `A0_Orchestrator.md` ×3개 | 에이전트→카테고리→모델 인라인 테이블 | config.json 복사본 — 수정 시 동기화 누락 위험 |
| ④ | `.agent/AGENTS.md` | 전체 파이프라인 매핑 표 (70줄) | ①②③의 종합 요약 — 역시 수동 동기화 필요 |

### 1.2 확인된 문제

- **불일치 발생**: dashboard 분석 리포트 2건이 이미 config.json ↔ AGENTS.md 간 불일치를 문제로 지적
- **유지보수 비용**: 모델 변경 시 4곳을 수동으로 동기화해야 함
- **관심사 혼재**: `prompt_append`(도메인 컨텍스트)가 카테고리(모델 라우팅)에 혼재

### 1.3 워크플로우 YAML — 변경 불필요

grep 결과: 9개 YAML 파일에 `model_routing`, `category`, `model` 관련 내용 **0건**. YAML은 수정 대상에서 제외.

---

## 2. 목표

1. **Single Source of Truth**: `oh-my-opencode.jsonc`를 모델 라우팅의 유일한 정본으로 확립
2. **카테고리 통합**: 19개 → 9개 (동일 모델 설정을 공유하는 카테고리 병합)
3. **config.json 삭제**: 8개 파일 제거 (런타임 영향 없음 확인됨)
4. **prompt_append 분리**: 카테고리에서 제거 → 에이전트 `.md` 파일로 이동
5. **인라인 테이블 제거**: A0_Orchestrator.md의 중복 매핑 테이블을 `.agent/AGENTS.md` 포인터로 대체

---

## 3. 스키마 호환성 검증 결과 ✅

| 검증 항목 | 결과 |
|-----------|------|
| 스키마 루트 `additionalProperties` | **미설정** (draft-07 기본값 = 추가 키 허용) |
| `config-manager.ts` 런타임 파싱 | `parseJsonc()` → 객체 변환만 수행, **스키마 검증 없음** |
| `deepMerge()` 동작 | unknown 키도 보존 (무시하지 않음) |
| `categories` 섹션 커스텀 키 | 공식 문서에서 커스텀 카테고리 자유 추가 가능 명시 |
| **결론** | 커스텀 카테고리 추가 및 커스텀 최상위 키 추가 모두 **문제 없음** |

---

## 4. 카테고리 통합안 (19 → 9)

### 4.1 통합 카테고리 정의

| # | 새 카테고리 | 모델 | 흡수 대상 (기존 카테고리) | 용도 |
|---|------------|------|--------------------------|------|
| 1 | `orchestration` | `opencode/claude-sonnet-4-6` | `unspecified-low` | A0 오케스트레이터 전용 |
| 2 | `deep-writing` | `anthropic/claude-opus-4-6` variant=max | `deep`, `micro-writing`, `unspecified-high` | 장문 교안 집필 (최고 품질) |
| 3 | `fast-task` | `anthropic/claude-haiku-4-5` | `quick` | 기계적 작업 (검증, 실행, 변환) |
| 4 | `visual-creative` | `google/antigravity-gemini-3.1-pro` variant=high | `visual-engineering`, `artistry`, `research`, `writing`, `curriculum-chunking` | 시각 설계, 리서치, 창의적 작업, 1M 컨텍스트 활용 |
| 5 | `fast-extraction` | `google/antigravity-gemini-3-flash` | `gemini-flash` | 빠른 구조화 추출 (1M 컨텍스트) |
| 6 | `structural` | `opencode/glm-5` | `glm5`, `curriculum-architecture`, `material-aggregation` | 구조적 분석/설계 (GLM-5) |
| 7 | `quality-gate` | `openai/gpt-5.3-codex` variant=xhigh | `ultrabrain`, `reasoning-high`, `reasoning-xhigh` | QA/최종 방어선 (최고 추론) |
| 8 | `codex-support` | `openai/gpt-5.3-codex` | `instructor-support-codex` | 강사 지원 콘텐츠 생성 |
| 9 | `korean-editing` | `google/antigravity-claude-sonnet-4-6` | `antigravity-sonnet` | 한국어 카피/톤 편집 |

### 4.2 파이프라인별 에이전트 → 새 카테고리 매핑

#### P01 Planner (기본: `deep-writing`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| A0 Orchestrator | `unspecified-low` | `orchestration` |
| A1 Trend Researcher | `research` | `visual-creative` |
| A2 Instructional Designer | `deep` | `deep-writing` (기본) |
| A3 Curriculum Architect | `curriculum-architecture` | `structural` |
| A5A QA Manager | `ultrabrain` | `quality-gate` |
| A5B Learner Analyst | `glm5` | `structural` |
| A7 Differentiation Advisor | `artistry` | `visual-creative` |

#### P02 Writer (기본: `deep-writing`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| A0 Orchestrator | `unspecified-low` | `orchestration` |
| A1 Source Miner | `glm5` | `structural` |
| A2 Traceability Curator | `gemini-flash` | `fast-extraction` |
| A3 Curriculum Architect | `glm5` | `structural` |
| A4B Session Writer | `micro-writing` | `deep-writing` (기본) |
| A4C Material Aggregator | `material-aggregation` | `structural` |
| A5 Code Validator | `glm5` | `structural` |
| A6 Visualization Designer | `visual-engineering` | `visual-creative` |
| A7 Learner Experience Designer | `glm5` | `structural` |
| A8 QA Editor | `ultrabrain` | `quality-gate` |
| A9 Instructor Support Designer | `instructor-support-codex` | `codex-support` |
| A10 Differentiation Strategist | `artistry` | `visual-creative` |
| A11 Chart Specifier | `visual-engineering` | `visual-creative` |

#### P03 Visualizer (기본: `visual-creative`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| A0 Orchestrator | `unspecified-low` | `orchestration` |
| A1 Content Analyst | `visual-engineering` (기본) | `visual-creative` (기본) |
| A2 Terminology Manager | `gemini-flash` | `fast-extraction` |
| A3 Slide Architect | `visual-engineering` (기본) | `visual-creative` (기본) |
| A4 Layout Designer | `visual-engineering` (기본) | `visual-creative` (기본) |
| A5 Code Validator | `quick` | `fast-task` |
| A6 Lab Reproducibility Eng. | `gemini-flash` | `fast-extraction` |
| A7 Visual Design Director | `visual-engineering` (기본) | `visual-creative` (기본) |
| A8 Copy Tone Editor | `antigravity-sonnet` | `korean-editing` |
| A9 QA Auditor | `ultrabrain` | `quality-gate` |
| A10 Trace Citation Keeper | `gemini-flash` | `fast-extraction` |

#### P04 Prompt Generator (기본: `visual-creative`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| P0 Orchestrator | `gemini-flash` | `fast-extraction` |
| P1 Education Structurer | `gemini-flash` | `fast-extraction` |
| P2 Slide Prompt Architect | `gemini-flash` | `fast-extraction` |
| P3 Visual Spec Curator | `visual-engineering` | `visual-creative` |
| P4 QA Auditor | `ultrabrain` | `quality-gate` |

> **P04 기본 카테고리 변경**: `writing` → `visual-creative`
> 이유: P04의 기본 카테고리 `writing`은 `visual-creative`에 흡수됨. 단, P04의 대부분 에이전트(P0/P1/P2)는 개별 오버라이드로 `fast-extraction`을 사용하므로 기본값의 실제 영향은 P3만 해당.

#### P05 PPTX Converter (기본: `fast-task`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| B0 Orchestrator | `unspecified-low` | `orchestration` |
| B1 Slide Parser | `unspecified-low` | `orchestration` |
| B2 HTML Renderer | `visual-engineering` | `visual-creative` |
| B3–B4 (기본) | `quick` | `fast-task` (기본) |
| B5 Visual QA | `visual-engineering` | `visual-creative` |

#### P06 NanoBanana (기본: `visual-creative`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| C0 Orchestrator | `unspecified-low` | `orchestration` |
| C1 (기본) | `visual-engineering` (기본) | `visual-creative` (기본) |
| C2 Prompt Engineer | `writing` | `visual-creative` |
| C3–C5 (기본) | `visual-engineering` (기본) | `visual-creative` (기본) |

> **C2 변경**: `writing` → `visual-creative` (동일 모델, 카테고리명만 변경)

#### P07 Manus Slide (기본: `fast-task`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| D0 Orchestrator | `unspecified-low` | `orchestration` |
| D1 Prompt Validator | `quick` (기본) | `fast-task` (기본) |
| D2 Chunk Splitter | `unspecified-low` | `orchestration` |
| D3 Submission Manager | `quick` (기본) | `fast-task` (기본) |
| D4 Post Processor | `quick` (기본) | `fast-task` (기본) |
| D5 Visual QA | `ultrabrain` | `quality-gate` |

#### P08 Log Analyzer (기본: `deep-writing`)

| 에이전트 | 기존 카테고리 | → 새 카테고리 |
|---------|-------------|-------------|
| L0 Orchestrator | `unspecified-low` | `orchestration` |
| L1 Data Collector | `quick` | `fast-task` |
| L2 Insight Analyst | `reasoning-high` | `quality-gate` |
| L3 Optimizer | `ultrabrain` | `quality-gate` |
| L4 Report Writer | `reasoning-high` | `quality-gate` |
| L5 QA Auditor | `ultrabrain` | `quality-gate` |

### 4.3 파이프라인 간 동일 역할 카테고리 통일 (기존 불일치 해소)

| 역할 | 기존 (불일치) | → 통합 후 |
|------|-------------|-----------|
| Orchestration | P01–P03 `unspecified-low`, P04 `gemini-flash` | **P04만 예외** — P04의 P0은 오케스트레이션보다 파일 조립 작업이 중심이라 `fast-extraction` 유지 |
| QA/방어선 | 전체 `ultrabrain` | `quality-gate` (통일) |
| 구조 설계 | P01 `curriculum-architecture`, P02 `glm5` | `structural` (통일) |
| 코드 검증 | P02 `glm5`, P03 `quick` | **P02 `structural`, P03 `fast-task`** — 검증 깊이가 다르므로 의도적 차이 유지 |

---

## 5. prompt_append 마이그레이션

### 5.1 현재 상태: 카테고리에 5개 prompt_append 존재

| 카테고리 | prompt_append 내용 | → 이동 대상 |
|---------|-------------------|------------|
| `deep` | 한국어 교안 작성 규칙 (강사 대본/실습 가이드) | 02_writer 소속 에이전트 .md (A4B 등) |
| `visual-engineering` | Bento Grid/Sketch Note 슬라이드 규칙 | 03_visualizer 소속 에이전트 .md (A1/A3/A4/A7) |
| `writing` | Pipeline 06 슬라이드 프롬프트 생성 규칙 | 04_prompt_generator 소속 에이전트 .md (P2) |
| `curriculum-chunking` | 마이크로세션 15-25분 설계 규칙 | 01_planner 소속 에이전트 .md (A3) |
| `micro-writing` | 마이크로세션 교안 집필 규칙 | 02_writer 소속 에이전트 .md (A4B) |

### 5.2 마이그레이션 방식

1. 각 에이전트 `.md` 파일 상단에 `## 도메인 컨텍스트` 섹션을 추가
2. 해당 prompt_append 내용을 그대로 복사
3. `oh-my-opencode.jsonc`의 통합 카테고리에서는 prompt_append 제거 (순수 모델 라우팅만 담당)

### 5.3 영향받는 에이전트 .md 파일 목록

정확한 파일 목록은 실행 단계에서 확인 필요. 대상 후보:
- `.agent/agents/01_planner/A3_Curriculum_Architect.md`
- `.agent/agents/02_writer/A4B_Session_Writer.md`
- `.agent/agents/03_visualizer/A1_Content_Analyst.md` (및 A3, A4, A7)
- `.agent/agents/04_prompt_generator/P2_Slide_Prompt_Architect.md`

---

## 6. 단계별 실행 계획

### Phase 1: oh-my-opencode.jsonc 수정 (핵심)

**파일**: `.opencode/oh-my-opencode.jsonc`

**변경 내용**:
- 19개 카테고리 → 9개로 통합
- prompt_append 5개 제거 (Phase 3에서 에이전트 .md로 이동)
- JSONC 주석으로 카테고리 용도 설명 유지

**Before** (19개):
```
deep, micro-writing, unspecified-high, quick, visual-engineering, artistry,
research, writing, curriculum-chunking, gemini-flash, glm5, curriculum-architecture,
material-aggregation, ultrabrain, reasoning-high, reasoning-xhigh,
instructor-support-codex, unspecified-low, antigravity-sonnet
```

**After** (9개):
```
orchestration, deep-writing, fast-task, visual-creative, fast-extraction,
structural, quality-gate, codex-support, korean-editing
```

### Phase 2: config.json 삭제

**파일 삭제 (8개)**:
```
.agent/agents/01_planner/config.json
.agent/agents/02_writer/config.json
.agent/agents/03_visualizer/config.json
.agent/agents/04_prompt_generator/config.json
.agent/agents/05_pptx_converter/config.json
.agent/agents/06_nanopptx/config.json
.agent/agents/07_manus_slide/config.json
.agent/agents/08_log_analyzer/config.json
```

**사전 검증 완료**: Python/bash 스크립트에서 config.json 파싱 0건, 워크플로우 YAML에서 참조 0건.

**보존할 정보**: config.json의 비-라우팅 메타데이터 (name, description, tools_reference, input_policy, output_policy, chunking_policy 등)는 각 팀의 A0/P0/B0 등 오케스트레이터 .md 파일이나 워크플로우 YAML에 이미 존재하거나, 해당 .md 파일로 이전.

### Phase 3: prompt_append 이동

**5개 prompt_append를 에이전트 .md 파일로 이동** (§5 참조)

각 대상 에이전트 .md에 `## 도메인 컨텍스트` 섹션 추가.

### Phase 4: A0_Orchestrator.md 수정 (3개)

**파일**:
```
.agent/agents/01_planner/A0_Orchestrator.md
.agent/agents/02_writer/A0_Orchestrator.md
.agent/agents/03_visualizer/A0_Orchestrator.md
```

**변경 내용**:

1. **인라인 매핑 테이블 제거** (03_visualizer A0 lines 164-181 등)
2. **config.json 로드 절차 삭제** (02_writer A0 line 193 등의 "config.json 로드" 단계)
3. **새 참조 방식 삽입**: `.agent/AGENTS.md`의 §Per-Agent Model Routing 참조 포인터로 대체
4. **로깅 초기화 절차에서 카테고리 결정 방식 갱신**: config.json 대신 `.agent/AGENTS.md` 매핑 테이블 참조

**수정 후 로깅 초기화 (예시)**:
```markdown
### 로깅 초기화
1. `run_id` 확인 (기존과 동일)
2. 로그 파일 경로 확인 (기존과 동일)
3. **카테고리 결정**: `.agent/AGENTS.md` §Per-Agent Model Routing 표에서
   자신의 파이프라인과 에이전트명으로 카테고리를 조회합니다.
4. **model 매핑**: `.opencode/oh-my-opencode.jsonc`의 `categories` 섹션에서
   해당 카테고리의 model 값을 참조합니다.
```

### Phase 5: .agent/AGENTS.md 수정

**파일**: `.agent/AGENTS.md`

**변경 내용**:

1. **§Per-Agent Model Routing** 섹션 전면 개편:
   - "해석 규칙"에서 config.json 참조 삭제
   - config.json 스키마 예시 제거
   - 파이프라인별 매핑 표를 **새 9개 카테고리**로 갱신
   - 표에서 "기존 카테고리" 열 제거 → 새 카테고리만 표시

2. **해석 규칙 갱신**:
   ```
   Before: "오케스트레이터가 config.json을 읽어 카테고리를 결정"
   After:  "오케스트레이터가 이 테이블에서 카테고리를 결정하고,
            oh-my-opencode.jsonc에서 모델을 조회"
   ```

3. **표 축소**: 기본 카테고리와 다른 오버라이드만 기재 (동일한 건 생략)

---

## 7. 수정 대상 파일 요약

| # | 작업 | 파일 | 종류 |
|---|------|------|------|
| 1 | 카테고리 19→9 통합 | `.opencode/oh-my-opencode.jsonc` | 수정 |
| 2 | 삭제 | `.agent/agents/01_planner/config.json` | 삭제 |
| 3 | 삭제 | `.agent/agents/02_writer/config.json` | 삭제 |
| 4 | 삭제 | `.agent/agents/03_visualizer/config.json` | 삭제 |
| 5 | 삭제 | `.agent/agents/04_prompt_generator/config.json` | 삭제 |
| 6 | 삭제 | `.agent/agents/05_pptx_converter/config.json` | 삭제 |
| 7 | 삭제 | `.agent/agents/06_nanopptx/config.json` | 삭제 |
| 8 | 삭제 | `.agent/agents/07_manus_slide/config.json` | 삭제 |
| 9 | 삭제 | `.agent/agents/08_log_analyzer/config.json` | 삭제 |
| 10 | prompt_append 이동 | 대상 에이전트 .md (4-8개) | 수정 |
| 11 | 인라인 테이블/config.json 참조 제거 | `.agent/agents/01_planner/A0_Orchestrator.md` | 수정 |
| 12 | 인라인 테이블/config.json 참조 제거 | `.agent/agents/02_writer/A0_Orchestrator.md` | 수정 |
| 13 | 인라인 테이블/config.json 참조 제거 | `.agent/agents/03_visualizer/A0_Orchestrator.md` | 수정 |
| 14 | 매핑 표 갱신 | `.agent/AGENTS.md` | 수정 |

**총 14개 파일** (삭제 8 + 수정 6 + prompt_append 이동 대상 별도)

---

## 8. 리스크 평가

### 8.1 저위험 (검증 완료)

| 리스크 | 완화 |
|--------|------|
| config.json 삭제 시 런타임 에러 | ✅ grep으로 확인: 소스코드 참조 0건 |
| oh-my-opencode.jsonc 커스텀 키 | ✅ 스키마/파싱 로직 검증: 문제 없음 |
| 워크플로우 YAML 변경 누락 | ✅ grep으로 확인: model 관련 내용 0건 — 수정 불필요 |

### 8.2 중위험 (주의 필요)

| 리스크 | 완화 |
|--------|------|
| 카테고리명 변경 시 A0의 task() 호출 불일치 | A0 .md에 "이 카테고리 사용" 지시를 명시. 그러나 A0는 .md 내용을 참조하여 task()를 호출하므로 .md 수정이 동기화됨 |
| prompt_append 이동 시 누락 | 이동 전후 diff 비교로 100% 동일 확인 |
| 로깅 비용 추정 정확도 변화 | 카테고리→모델 매핑이 변경되므로 logging-protocol.md의 비용 테이블도 갱신 필요 (향후 작업) |

### 8.3 고위험 — 없음

기존 시스템의 실질적 런타임 변경은 0건. 모든 변경은 **문서/설정 레벨**이며, 실제 모델 호출 경로(`task(category=X)` → `oh-my-opencode.jsonc` → 모델)는 동일하게 유지됨.

---

## 9. Git 브랜치 전략

AGENTS.md의 Git Branching Rule에 따라:

```bash
# 1. 브랜치 생성 (파일 수정 전)
git checkout -b feat/model-routing-consolidation

# 2. Phase 1-5 수정 작업 수행

# 3. 커밋
git add -A && git commit -m "refactor: consolidate model routing to oh-my-opencode.jsonc (19→9 categories)"

# 4. main 머지 & 정리
git checkout main && git merge --no-ff feat/model-routing-consolidation
git push && git branch -d feat/model-routing-consolidation
```

---

## 10. 롤백 계획

모든 변경이 Git으로 추적되므로:
```bash
git revert HEAD  # 머지 커밋 롤백
```

config.json 파일은 git history에 보존됨.

---

## 11. 실행 순서 요약

```
Phase 1: oh-my-opencode.jsonc 수정 (카테고리 19→9, prompt_append 제거)
    ↓
Phase 2: config.json ×8 삭제
    ↓
Phase 3: prompt_append를 에이전트 .md로 이동 (4-8개 파일)
    ↓
Phase 4: A0_Orchestrator.md ×3 수정 (인라인 테이블 제거, 참조 갱신)
    ↓
Phase 5: .agent/AGENTS.md 수정 (매핑 표를 새 카테고리로 갱신)
    ↓
검증: 모든 수정 파일 일관성 확인
    ↓
Git: feat 브랜치 → commit → merge → push
```
