# 마이크로 세션 기능 완전 제거 — 실행 계획서

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 15~25분 마이크로 세션 청킹 로직을 완전히 제거하고, 60~90분 통합 세션 단위로 기획→집필 파이프라인을 단순화한다.

**Architecture:** A3B(MicroSession Specifier), A3C(Session Indexer) 에이전트를 삭제하고, 워크플로우 YAML에서 micro session 관련 step/policy를 제거한다. 02_writer에서는 A4B→A4로 통합, A4C를 유지하되 마이크로 세션 의존성을 제거한다. 모든 문서(AGENTS.md, 가이드)에서 micro_sessions 참조를 정리한다.

**Tech Stack:** YAML, Markdown, JSON (에이전트 설정 파일)

**Git Branching:** 루트 AGENTS.md의 Git Branching Rule에 따라 `feat/remove-micro-sessions` 브랜치에서 작업 후 main에 `--no-ff` 머지.

---

## 영향 범위 전수 조사 결과

### 변경 대상 파일 목록 (총 14개)

| # | 파일 | 조치 | Phase |
|---|------|------|-------|
| 1 | `.agent/agents/01_planner/A3B_MicroSession_Specifier.md` | 🗑️ 삭제 | 1 |
| 2 | `.agent/agents/01_planner/A3C_Session_Indexer.md` | 🗑️ 삭제 | 1 |
| 3 | `.agent/agents/01_planner/config.json` | ✏️ 수정 | 1 |
| 4 | `.agent/agents/01_planner/A0_Orchestrator.md` | ✏️ 수정 | 1 |
| 5 | `.agent/agents/01_planner/A3_Curriculum_Architect.md` | ✏️ 수정 | 1 |
| 6 | `.agent/agents/01_planner/A5A_QA_Manager.md` | ✏️ 수정 | 1 |
| 7 | `.agent/workflows/01_Lecture_Planning.yaml` | ✏️ 전면 수정 | 1 |
| 8 | `.agent/agents/02_writer/A4B_Session_Writer.md` | ✏️ 전면 수정 | 2 |
| 9 | `.agent/agents/02_writer/A4C_Material_Aggregator.md` | ✏️ 전면 수정 | 2 |
| 10 | `.agent/agents/02_writer/A0_Orchestrator.md` | ✏️ 수정 | 2 |
| 11 | `.agent/agents/02_writer/A11_Chart_Specifier.md` | ✏️ 수정 | 2 |
| 12 | `.agent/agents/02_writer/config.json` | ✏️ 수정 | 2 |
| 13 | `AGENTS.md` (루트) | ✏️ 수정 | 3 |
| 14 | `.agent/Lecture_Creation_Guide.md` | ✏️ 수정 | 3 |

### 변경 불필요 파일 (확인 완료)

| 파일 | 사유 |
|------|------|
| `.agent/agents/01_planner/A1_Trend_Researcher.md` | 마이크로 세션 참조 없음 |
| `.agent/agents/01_planner/A2_Instructional_Designer.md` | 마이크로 세션 참조 없음 |
| `.agent/agents/01_planner/A5B_Learner_Analyst.md` | 마이크로 세션 참조 없음 |
| `.agent/agents/01_planner/A7_Differentiation_Advisor.md` | 마이크로 세션 참조 없음 |
| `.agent/AGENTS.md` | 루트 AGENTS.md에서 참조하는 메타 문서 — 자동 반영됨 |
| `참고자료/` 하위 파일들 | 백업/레퍼런스이므로 수정 대상 아님 |

---

## Phase 1: 기획 단계 (01_Lecture_Planning) 롤백

### Task 1.1: 에이전트 파일 삭제 (A3B, A3C)

**Files:**
- Delete: `.agent/agents/01_planner/A3B_MicroSession_Specifier.md` (222줄)
- Delete: `.agent/agents/01_planner/A3C_Session_Indexer.md` (267줄)

**Step 1: A3B 파일 삭제**
```bash
git rm .agent/agents/01_planner/A3B_MicroSession_Specifier.md
```

**Step 2: A3C 파일 삭제**
```bash
git rm .agent/agents/01_planner/A3C_Session_Indexer.md
```

**Step 3: 검증**
```bash
ls .agent/agents/01_planner/
# 예상: A3B, A3C 파일이 목록에 없어야 함
# 남아야 하는 파일: A0, A1, A2, A3, A5A, A5B, A7, config.json (8개)
```

---

### Task 1.2: config.json 정리

**Files:**
- Modify: `.agent/agents/01_planner/config.json`

**Step 1: A3B, A3C 항목 제거**

현재 (L11-12):
```json
"A3B_MicroSession_Specifier":{ "category": "curriculum-chunking", "note": "15~25min 마이크로 세션 설계 및 Gemini 최적화 태그 부여" },
"A3C_Session_Indexer":       { "category": "curriculum-chunking", "note": "의존성 그래프 및 학습 경로 설계" },
```

변경 후: 두 줄 모두 삭제.

**Step 2: 검증**
```bash
python3 -c "import json; f=open('.agent/agents/01_planner/config.json'); d=json.load(f); assert 'A3B_MicroSession_Specifier' not in d['agent_models']; assert 'A3C_Session_Indexer' not in d['agent_models']; print('OK:', list(d['agent_models'].keys()))"
# 예상: OK: ['A0_Orchestrator', 'A1_Trend_Researcher', 'A2_Instructional_Designer', 'A3_Curriculum_Architect', 'A5B_Learner_Analyst', 'A7_Differentiation_Advisor', 'A5A_QA_Manager']
```

---

### Task 1.3: A0_Orchestrator.md 수정 (01_planner)

**Files:**
- Modify: `.agent/agents/01_planner/A0_Orchestrator.md`

**변경 지점 3곳:**

**Step 1: 로깅 설정 — step 수 및 A3B/A3C 참조 제거 (L166-168)**

현재:
```
- **기본 실행 모델**: Step-by-Step (11 steps: step_0 ~ step_10)
- **step_4/step_5**: A3B(MicroSession Specifier), A3C(Session Indexer) — category `curriculum-chunking`으로 START/END 로깅
```

변경 후:
```
- **기본 실행 모델**: Step-by-Step (9 steps: step_0 ~ step_8)
```
(`step_4/step_5` 줄 삭제)

**Step 2: 모델 매핑 테이블 — A3B, A3C 행 제거 (L222-223)**

현재:
```
| A3B_MicroSession_Specifier | `curriculum-chunking` | `google/antigravity-gemini-3.1-pro` |
| A3C_Session_Indexer | `curriculum-chunking` | `google/antigravity-gemini-3.1-pro` |
```

변경 후: 두 행 삭제.

**Step 3: 골든 템플릿 — §4 마이크로 세션 인덱스 섹션 제거 (L255-258)**

현재:
```
4. **마이크로 세션 인덱스 (Step 4~5 산출물)**: 마이크로 세션 청킹 결과를 문서에 반드시 포함하세요.
   - **`micro_sessions/` 디렉토리 구조**: `_index.json`, `_flow.md`, `_dependency.mmd`, `_reference_mapping.json`, 세션별 `.md` 파일 링크
   - **의존성 그래프**: `_dependency.mmd`를 Mermaid 코드 블록으로 삽입하거나 파일 링크 제공
   - **학습 경로 요약**: 기본 경로(Default Path), 보충 경로(Supplementary), 단축 경로(Accelerated)의 세션 ID 나열
```

변경 후: 4번 항목 전체 삭제. (3번의 QA 검증 보고서 내 마이크로 세션 전용 QA 항목 문구도 제거)

**Step 4: QA 검증 보고서 내 마이크로 세션 참조 제거 (L253)**

현재:
```
마이크로 세션 전용 QA 항목(단일 개념 준수, 15~25분 범위, 분량, 연결성, chunk_type, 의존성 그래프)도 포함.
```

변경 후: 해당 문구 삭제 (기존 QA 체크리스트만 유지).

**Step 5: 검증**
```bash
grep -c "마이크로 세션\|micro_session\|A3B\|A3C\|curriculum-chunking" .agent/agents/01_planner/A0_Orchestrator.md
# 예상: 0
```

---

### Task 1.4: A3_Curriculum_Architect.md 수정

**Files:**
- Modify: `.agent/agents/01_planner/A3_Curriculum_Architect.md`

**변경 지점 2곳:**

**Step 1: Integration Hub에서 A3B/A3C 참조 제거 (L23-25)**

현재:
```
   - A3B(마이크로 세션 스펙)가 설계한 "Micro Session Specifications"를 커리큘럼에 통합
   - A3C(세션 인덱서)가 생성한 "Session Index, Dependency Graph"를 강의구성안에 링크
   - 마이크로 세션 링크와 의존성 그래프를 메인 문서에 포함
```

변경 후: 3줄 모두 삭제.

**Step 2: `integrate_outputs` 액션에서 마이크로 세션 참조 제거 (L39-47)**

현재:
```markdown
### Action: `integrate_outputs` (step_8 — 통합 업데이트)
- **입력**:
  - 강의구성안.md 초안 (step_3 산출물)
  - Micro Session Index (`01_Planning/micro_sessions/_index.json`, A3C 제공)
  - Dependency Graph (`01_Planning/micro_sessions/_dependency.mmd`, A3C 제공)
  - Learning Activities (A2 제공)
  - Differentiation Strategy (A7 제공)
- **산출물**: `01_Planning/강의구성안.md` 최종본 (마이크로 세션 통합 완결)
- **⚠️ 주의**: step_3의 초안을 기반으로 micro_sessions 데이터를 반영하여 업데이트. 초안을 덮어쓰지 말고, 섹션을 추가/보강할 것.
```

변경 후:
```markdown
### Action: `integrate_outputs` (step_6 — 통합 업데이트)
- **입력**:
  - 강의구성안.md 초안 (step_3 산출물)
  - Learning Activities (A2 제공)
  - Differentiation Strategy (A7 제공)
- **산출물**: `01_Planning/강의구성안.md` 최종본
- **⚠️ 주의**: step_3의 초안을 기반으로 A2, A7 산출물을 반영하여 업데이트. 초안을 덮어쓰지 말고, 섹션을 추가/보강할 것.
```

**Step 3: design_structure 노트에서 마이크로 세션 참조 제거 (L37)**

현재:
```
- **⚠️ 주의**: 이 시점에는 micro_sessions 데이터가 존재하지 않음. Micro Session Index, Dependency Graph를 참조하지 말 것.
```

변경 후:
```
- **⚠️ 주의**: 이 시점에는 A2, A7 산출물이 아직 없음. 병렬 실행 후 integrate_outputs에서 통합.
```

**Step 4: 검증**
```bash
grep -c "마이크로 세션\|micro_session\|A3B\|A3C\|micro_sessions" .agent/agents/01_planner/A3_Curriculum_Architect.md
# 예상: 0
```

---

### Task 1.5: A5A_QA_Manager.md 수정

**Files:**
- Modify: `.agent/agents/01_planner/A5A_QA_Manager.md`

**Step 1: 마이크로 세션 검증 항목 섹션 삭제 (L27-36)**

현재:
```markdown
### 마이크로 세션 검증 항목 (Micro Session Checklist)
- [ ] **단일 개념 준수**: 각 마이크로 세션이 단 1개의 핵심 학습 목표만 다루는가?
- [ ] **시간 범위**: 모든 마이크로 세션이 15~25분 범위 내인가?
- [ ] **세션별 합산 정합성**: 동일 부모 세션에 속한 마이크로 세션들의 `duration_min` 합이 부모 세션 시간(기본 90분)과 정확히 일치하는가?
- [ ] **일별 합산 정합성**: 각 Day의 마이크로 세션 `duration_min` 합이 일별 총 교육 시간(기본 360분 = 4세션×90분)과 일치하는가?
- [ ] **_index.json statistics 정합성**: `statistics.by_day` 값이 실제 세션 데이터의 합산과 정확히 일치하는가?
- [ ] **분량 적절성**: 각 세션의 예상 교안 분량이 3,000~4,500자 범위 내인가?
- [ ] **세션 연결성**: 모든 세션에 선행/후행 세션 연결이 명확히 정의되었는가?
- [ ] **chunk_type 태그**: 각 세션에 적절한 chunk_type (narrative|code|diagram|lab) 태그가 부여되었는가?
- [ ] **의존성 그래프 완결성**: 그래프에 고립 노드(orphan)나 순환 의존성(circular dependency)이 없는가?
```

변경 후: 전체 섹션 삭제 (기존 검증 항목 Checklist만 유지).

**Step 2: 검증**
```bash
grep -c "마이크로 세션\|micro_session\|chunk_type\|의존성 그래프" .agent/agents/01_planner/A5A_QA_Manager.md
# 예상: 0
```

---

### Task 1.6: 01_Lecture_Planning.yaml 전면 수정

**Files:**
- Modify: `.agent/workflows/01_Lecture_Planning.yaml`

이 태스크가 Phase 1에서 가장 큰 변경입니다. 변경점을 순서대로 나열합니다.

**Step 1: 이름 및 설명 변경 (L1-2)**

현재:
```yaml
name: "Lecture Planning Pipeline - Micro Session Chunking"
description: "Gemini 최적화된 15~25분 마이크로 세션 청킹 기반 강의 기획 워크플로우 ..."
```

변경 후:
```yaml
name: "Lecture Planning Pipeline"
description: "강의 기획 워크플로우 (Planner Team) ⚠️ MUST ANALYZE CONTEXT: If a local folder is provided, analyze its contents using list_dir/read_file BEFORE proceeding."
```

**Step 2: micro_session_policy 전체 섹션 삭제 (L8-31)**

24줄 전체 삭제 (`micro_session_policy:` ~ `rules:` 끝).

**Step 3: step_0 notes에서 마이크로 세션 언급 제거 (L87)**

현재:
```yaml
notes: |
  마이크로 세션 워크플로우임을 명시하고, Gemini 최적화된 15~25분 청킹 전략을 설명합니다.
```

변경 후:
```yaml
notes: |
  사용자 요청을 분석하여 스코프를 정의하고 에이전트 작업을 분배합니다.
```

**Step 4: step_3 notes에서 A3B 참조 제거 (L115-117)**

현재:
```yaml
notes: |
  기존 60~90분 단위 세션으로 초안 설계. A3B에서 마이크로 세션으로 세분화.
  ⚠️ 반드시 01_Planning/강의구성안.md 파일로 저장할 것 (step_2의 학습자 분석 섹션 유지).
  이 초안은 step_4~5의 micro_sessions 작업의 기반 입력이 되며, step_8에서 micro_sessions 데이터로 업데이트됩니다.
```

변경 후:
```yaml
notes: |
  60~90분 단위 세션으로 커리큘럼 초안 설계.
  ⚠️ 반드시 01_Planning/강의구성안.md 파일로 저장할 것 (step_2의 학습자 분석 섹션 유지).
  이 초안은 step_4, step_5의 병렬 작업 후 step_6에서 통합됩니다.
```

**Step 5: step_4_micro_chunking 삭제 (L119-141)**

23줄 전체 삭제.

**Step 6: step_5_session_indexing 삭제 (L143-165)**

23줄 전체 삭제.

**Step 7: step_6 → step_4로 재번호, depends_on 수정 (L167-180)**

현재:
```yaml
- id: step_6_instructional_design
  depends_on: "step_5_session_indexing"
  input:
    - "Curriculum Structure"
    - "Micro Session Index"
    - "Learner Persona"
    - "Output Language: Korean"
  output: "Learning Activities & Assessment Plan (01_Planning/micro_sessions/_activities.md)"
  notes: |
    각 마이크로 세션별 학습 활동 설계. 개별 세션 파일에 활동 정보 추가.
```

변경 후:
```yaml
- id: step_4_instructional_design
  depends_on: "step_3_curriculum_design"
  input:
    - "Curriculum Structure"
    - "Learner Persona"
    - "Output Language: Korean"
  output: "Learning Activities & Assessment Plan (01_Planning/강의구성안.md 내 활동 섹션)"
  notes: |
    각 세션별 학습 활동 설계.
```

**Step 8: step_7 → step_5로 재번호, depends_on 수정 (L182-192)**

현재:
```yaml
- id: step_7_differentiation
  depends_on: "step_5_session_indexing"
  input:
    - "Curriculum Structure"
    - "Micro Session Index"
    - "Trend Report"
    - "Output Language: Korean"
```

변경 후:
```yaml
- id: step_5_differentiation
  depends_on: "step_3_curriculum_design"
  input:
    - "Curriculum Structure"
    - "Trend Report"
    - "Output Language: Korean"
```

**Step 9: step_8 → step_6로 재번호, 마이크로 세션 참조 제거 (L194-210)**

현재:
```yaml
- id: step_8_integration
  depends_on:
    - "step_6_instructional_design"
    - "step_7_differentiation"
  input:
    - "Curriculum Structure (Skeleton)"
    - "Micro Session Index"
    - "Learning Activities (A2)"
    - "Differentiation Strategy (A7)"
    - "Output Language: Korean"
  output: "Integrated Curriculum Plan with Micro Sessions (Complete)"
  notes: |
    모든 마이크로 세션 정보를 통합하여 최종 강의구성안 완성.
    마이크로 세션 링크와 의존성 그래프를 메인 문서에 포함.
```

변경 후:
```yaml
- id: step_6_integration
  depends_on:
    - "step_4_instructional_design"
    - "step_5_differentiation"
  input:
    - "Curriculum Structure (Skeleton)"
    - "Learning Activities (A2)"
    - "Differentiation Strategy (A7)"
    - "Output Language: Korean"
  output: "Integrated Curriculum Plan (Complete)"
  notes: |
    A2, A7 산출물을 커리큘럼 초안에 통합하여 최종 강의구성안 완성.
```

**Step 10: step_9 → step_7로 재번호, 마이크로 세션 QA 기준 제거 (L212-234)**

현재 `qa_criteria`에서 마이크로 세션 전용 항목 6개 삭제:
```yaml
qa_criteria:
  - "마이크로 세션당 단일 개념 준수 여부"
  - "15~25분 시간 범위 준수 여부"
  - "3,000~4,500자 분량 적절성"
  - "선행/후행 세션 연결성"
  - "chunk_type 태그 적절성"
  - "의존성 그래프 완결성"
```

변경 후:
```yaml
- id: step_7_qa_review
  depends_on: "step_6_integration"
  qa_criteria:
    - "세션별 학습 목표 정렬 여부"
    - "시간 총합 정합성"
    - "세션 간 논리적 연결성"
    - "용어/포맷 일관성"
    - "완결성 (외부 의존 없이 교안 작성 가능 여부)"
```

마이크로 세션 전용 notes도 세션 단위 검증으로 교체.

**Step 11: step_10 → step_8로 재번호, save_targets에서 micro_sessions 제거 (L236-264)**

현재 `save_targets`:
```yaml
save_targets:
  - "01_Planning/강의구성안.md"
  - "01_Planning/Trend_Report.md"
  - "01_Planning/micro_sessions/_index.json"
  - "01_Planning/micro_sessions/_flow.md"
  - "01_Planning/micro_sessions/_dependency.mmd"
  - "01_Planning/micro_sessions/_reference_mapping.json"
  - "01_Planning/micro_sessions/_activities.md"
  - "01_Planning/micro_sessions/_differentiation.md"
  - "01_Planning/micro_sessions/세션-*.md"
```

변경 후:
```yaml
- id: step_8_final_approval
  depends_on: "step_7_qa_review"
  decision:
    approved:
      action: "Finish"
      save_targets:
        - "01_Planning/강의구성안.md"
        - "01_Planning/Trend_Report.md"
    rejected:
      action: "Retry from step_3_curriculum_design"
      max_retries: 2
```

`rejected.action`도 `step_4_micro_chunking` → `step_3_curriculum_design`으로 변경.

**Step 12: downstream_integration 섹션 수정 (L266-278)**

현재:
```yaml
downstream_integration:
  material_writing:
    input_format: "micro_session_based"
    session_files: "01_Planning/micro_sessions/세션-*.md"
    index_file: "01_Planning/micro_sessions/_index.json"
    flow_file: "01_Planning/micro_sessions/_flow.md"
    dependency_file: "01_Planning/micro_sessions/_dependency.mmd"
    reference_mapping_file: "01_Planning/micro_sessions/_reference_mapping.json"
    notes: |
      02_Material_Writing은 마이크로 세션별 개별 교안 작성 후 취합하는 방식.
      각 세션 파일은 독립적으로 처리되며, A4C_Material_Aggregator가 최종 통합.
```

변경 후:
```yaml
downstream_integration:
  material_writing:
    input_format: "session_based"
    plan_file: "01_Planning/강의구성안.md"
    notes: |
      02_Material_Writing은 강의구성안.md 기반으로 세션별 교안을 작성합니다.
```

**Step 13: 검증**
```bash
grep -c "마이크로 세션\|micro_session\|A3B\|A3C\|curriculum-chunking\|micro_sessions" .agent/workflows/01_Lecture_Planning.yaml
# 예상: 0
```

**Step 14: YAML 구문 검증**
```bash
python3 -c "import yaml; yaml.safe_load(open('.agent/workflows/01_Lecture_Planning.yaml')); print('YAML valid')"
# 예상: YAML valid
```

**Step 15: step 번호 매핑 확인**

| 기존 ID | 새 ID | 에이전트 |
|---------|-------|---------|
| step_0_scope | step_0_scope | A0 |
| step_1_trend_analysis | step_1_trend_analysis | A1 |
| step_2_learner_analysis | step_2_learner_analysis | A5B |
| step_3_curriculum_design | step_3_curriculum_design | A3 |
| ~~step_4_micro_chunking~~ | ❌ 삭제 | ~~A3B~~ |
| ~~step_5_session_indexing~~ | ❌ 삭제 | ~~A3C~~ |
| step_6_instructional_design | step_4_instructional_design | A2 |
| step_7_differentiation | step_5_differentiation | A7 |
| step_8_integration | step_6_integration | A3 |
| step_9_qa_review | step_7_qa_review | A5A |
| step_10_final_approval | step_8_final_approval | A0 |

---

### Task 1.7: Phase 1 커밋

**Step 1: 변경 사항 확인**
```bash
git status
git diff --stat
```

**Step 2: 커밋**
```bash
git add -A && git commit -m "refactor(01_planner): remove micro session chunking from planning pipeline

- Delete A3B_MicroSession_Specifier.md, A3C_Session_Indexer.md
- Remove A3B/A3C from config.json
- Clean micro session references from A0, A3, A5A agents
- Restructure workflow YAML: remove step_4/5, renumber step_6-10 to 4-8
- Update depends_on chains, save_targets, downstream_integration"
```

---

## Phase 2: 집필 단계 (02_Material_Writing) 단일화

### Task 2.1: A4B_Session_Writer.md 수정 — 통합 세션 기반으로 전환

**Files:**
- Modify: `.agent/agents/02_writer/A4B_Session_Writer.md`

**설계 결정:** A4B를 삭제하고 A4로 교체하는 대신, **A4B 파일을 유지하되 마이크로 세션 의존성을 제거**합니다. 이유: A4B의 7섹션 구조, 서술 규칙, 로깅 설정 등 유용한 콘텐츠가 많아 삭제보다 수정이 효율적.

**Step 1: 파일 헤더의 "마이크로 세션" 참조 변경 (L9, L12, L15)**

현재:
```
# 당신은 '세션별 교안 집필자 (Session Writer)'입니다.
> **핵심 차별점**: 단일 마이크로 세션(15~25분)에 완전히 집중하여 A0의 7섹션 구조를 완전히 구현하는 완결된 교안. 분량 제한 없음.
당신은 하나의 마이크로 세션(15~25분 분량)에 완전히 집중하여...
```

변경 후:
```
# 당신은 '세션별 교안 집필자 (Session Writer)'입니다.
> **핵심 차별점**: 단일 세션(60~90분)에 집중하여 A0의 7섹션 구조를 완전히 구현하는 완결된 교안. 분량 제한 없음.
당신은 하나의 세션(60~90분 분량)에 집중하여...
```

**Step 2: 핵심 책임 §1 — 마이크로 세션 분량 제약 제거 (L19-22)**

현재:
```
### 1. 마이크로 세션 완결성 확보
- **단일 세션 집중**: 오직 1개의 마이크로 세션만 처리 (15~25분 분량)
```

변경 후:
```
### 1. 세션 완결성 확보
- **단일 세션 집중**: 오직 1개의 세션만 처리 (60~90분 분량)
```

**Step 3: 입력 경로 변경 (L81, L308)**

현재:
```
- **세션 명세서**: `01_Planning/micro_sessions/세션-{번호}-{제목}.md` (A3B 제공) — **📚 참고자료 매핑 섹션 반드시 확인**
```

변경 후:
```
- **세션 명세서**: `01_Planning/강의구성안.md` 내 해당 세션 섹션 — **📚 참고자료 매핑 섹션 반드시 확인**
```

**Step 4: 출력 파일 템플릿에서 마이크로 세션 헤더 정리 (L100-106)**

현재:
```markdown
# 마이크로 세션: {번호} — {제목}
> **세션 ID**: MS-{코스ID}-{번호:03d}
> **소요 시간**: {15|20|25}분
```

변경 후:
```markdown
# 세션: {번호} — {제목}
> **세션 ID**: S-{코스ID}-{번호:03d}
> **소요 시간**: {60|75|90}분
```

**Step 5: 분량 관리 섹션 — v1.0 레퍼런스 유지, 마이크로 세션 언급 제거 (L250-255)**

"narrative 세션: v1.0 평균 ~554줄" 등의 레퍼런스 분량은 그대로 유지. "마이크로 세션" 용어만 "세션"으로 교체.

**Step 6: 검증**
```bash
grep -c "마이크로\|micro\|15~25\|15.25\|3,000~4,500\|A3B" .agent/agents/02_writer/A4B_Session_Writer.md
# 예상: 0
```

---

### Task 2.2: A4C_Material_Aggregator.md 수정

**Files:**
- Modify: `.agent/agents/02_writer/A4C_Material_Aggregator.md`

**설계 결정:** A4C는 유지. 보조 패킷 통합 + AM/PM 분할 + 최종 취합 기능은 마이크로 세션 없이도 필요함. 마이크로 세션 의존 참조만 제거.

**Step 1: 파일 헤더의 "마이크로 세션" 참조 변경 (L12, L15)**

현재:
```
> **핵심 차별점**: 개별 마이크로 세션 교안들을 검증하고 통합하여 완결된 전체 교안을 생성합니다.
당신은 A4B(Session Writer)가 작성한 개별 마이크로 세션 교안 파일들을 모두 읽고...
```

변경 후:
```
> **핵심 차별점**: 개별 세션 교안들을 검증하고 통합하여 완결된 전체 교안을 생성합니다.
당신은 A4B(Session Writer)가 작성한 개별 세션 교안 파일들을 모두 읽고...
```

**Step 2: 연결성 검증에서 A3C 참조 제거 (L25)**

현재:
```
- **의존성 체크**: A3C가 설계한 의존성 그래프와 실제 세션 내용의 일치성 확인
```

변경 후:
```
- **의존성 체크**: 강의구성안의 세션 순서와 실제 세션 내용의 일치성 확인
```

**Step 3: 입력에서 micro_sessions 경로 제거 (L68-70)**

현재:
```
- 세션 인덱스: `01_Planning/micro_sessions/_index.json` (A3C 제공)
- 학습 흐름 문서: `01_Planning/micro_sessions/_flow.md` (A3C 제공)
- 의존성 그래프: `01_Planning/micro_sessions/_dependency.mmd` (A3C 제공)
```

변경 후:
```
- 커리큘럼 구조: `01_Planning/강의구성안.md`
```

**Step 4: 산출물 헤더에서 마이크로 세션 참조 제거 (L100-104)**

현재:
```markdown
> **총 세션 수**: N개 마이크로 세션
> **작성 방식**: 7섹션 구조 마이크로 세션 청킹
```

변경 후:
```markdown
> **총 세션 수**: N개 세션
> **작성 방식**: 7섹션 구조 세션 단위 집필
```

**Step 5: AM/PM 분할 기준에서 마이크로 세션 번호 패턴 정리 (L42-46)**

마이크로 세션 번호 기준(001-011, 012-022 등)을 세션 기준으로 변경하거나, 실제 커리큘럼에 따라 유동적으로 설정하는 방식으로 수정.

변경 후:
```
- **분할 기준**: 강의구성안의 Day-세션 경계표 기반
  - 각 Day의 AM(오전)/PM(오후) 세션 구분에 따라 분할
```

**Step 6: 통합 교안에서 마이크로 세션 인덱스 참조 제거 (L127-134)**

Mermaid 의존성 그래프, "마이크로 세션" 용어를 "세션"으로 교체.

**Step 7: 산출물 입력 섹션 (L298-302)**

현재:
```
- 세션 인덱스: `01_Planning/micro_sessions/_index.json`
- 학습 흐름: `01_Planning/micro_sessions/_flow.md`
- 의존성 그래프: `01_Planning/micro_sessions/_dependency.mmd`
```

변경 후:
```
- 커리큘럼 구조: `01_Planning/강의구성안.md`
```

**Step 8: 검증**
```bash
grep -c "마이크로\|micro_session\|A3C\|_index.json\|_flow.md\|_dependency.mmd" .agent/agents/02_writer/A4C_Material_Aggregator.md
# 예상: 0
```

---

### Task 2.3: 02_writer/A0_Orchestrator.md 수정

**Files:**
- Modify: `.agent/agents/02_writer/A0_Orchestrator.md`

**변경 지점 5곳:**

**Step 1: L94 — 분량 제한 문구 수정**

현재:
```
- **분량 무제한**: 3,000~4,500자 제한을 적용하지 않습니다.
```

변경 후:
```
- **분량 무제한**: 세션 완결성을 우선하며 분량 제한을 적용하지 않습니다.
```

**Step 2: L119 — A4B 마이크로 세션 기본값 참조 수정**

현재:
```
- **A4B (Session Writer)**: 톤·수준 기본값에 따라 비유 중심 구어체로 마이크로 세션별 교안을 집필합니다.
```

변경 후:
```
- **A4B (Session Writer)**: 톤·수준 기본값에 따라 비유 중심 구어체로 세션별 교안을 집필합니다.
```

**Step 3: L200-210 — foreach_session 하이브리드 실행 설명 수정**

현재:
```
A4B의 `foreach_session` 모드는 Step-by-Step의 변형입니다:
- 각 마이크로 세션이 독립적인 step으로 취급되며, `batch_size: 3` 단위로 병렬 실행
```

변경 후:
```
A4B의 `foreach_session` 모드는 Step-by-Step의 변형입니다:
- 각 세션이 독립적인 step으로 취급되며, `batch_size: 3` 단위로 병렬 실행
```

**Step 4: L289 — 모델 매핑 테이블 A4B note 수정**

현재:
```
| A4B_Session_Writer | `micro-writing` | `google/antigravity-gemini-3.1-pro` |
```

note 변경은 config.json에서 처리 (Task 2.5 참조). 테이블 자체는 카테고리 이름이 변경되면 같이 수정.

**Step 5: 검증**
```bash
grep -c "마이크로 세션별\|마이크로 세션이\|3,000~4,500자" .agent/agents/02_writer/A0_Orchestrator.md
# 예상: 0
```

---

### Task 2.4: 02_writer/A11_Chart_Specifier.md 수정

**Files:**
- Modify: `.agent/agents/02_writer/A11_Chart_Specifier.md`

**Step 1: 입력 경로 변경 (L40, L214)**

현재:
```
- 세션 명세서: `01_Planning/micro_sessions/세션-{번호}-{제목}.md`
```

변경 후:
```
- 세션 명세서: `01_Planning/강의구성안.md` 내 해당 세션 섹션
```

**Step 2: 검증**
```bash
grep -c "micro_sessions" .agent/agents/02_writer/A11_Chart_Specifier.md
# 예상: 0
```

---

### Task 2.5: 02_writer/config.json 수정

**Files:**
- Modify: `.agent/agents/02_writer/config.json`

**Step 1: A4B note 수정 (L11)**

현재:
```json
"A4B_Session_Writer": { "category": "micro-writing", "note": "7섹션 교안 집필 — Gemini 최적화 마이크로 세션 서술형 집필" },
```

변경 후:
```json
"A4B_Session_Writer": { "category": "micro-writing", "note": "7섹션 교안 집필 — 세션 단위 서술형 집필" },
```

**Step 2: 검증**
```bash
python3 -c "import json; d=json.load(open('.agent/agents/02_writer/config.json')); print(d['agent_models']['A4B_Session_Writer']['note'])"
# 예상: "7섹션 교안 집필 — 세션 단위 서술형 집필" (마이크로 세션 문구 없음)
```

---

### Task 2.6: Phase 2 커밋

**Step 1: 변경 사항 확인**
```bash
git status
git diff --stat
```

**Step 2: 커밋**
```bash
git add -A && git commit -m "refactor(02_writer): remove micro session dependencies from writing pipeline

- Update A4B to work with 60-90min sessions instead of 15-25min micro sessions
- Remove micro_sessions/ path references from A4C, A0, A11
- Update input sources from micro_sessions/*.md to 강의구성안.md
- Clean A4B note in config.json"
```

---

## Phase 3: 문서 및 E2E 정리

### Task 3.1: 루트 AGENTS.md 수정

**Files:**
- Modify: `AGENTS.md` (루트)

**Step 1: Workflow Overview 테이블에서 micro_sessions 제거 (L80)**

현재:
```
| 1 | **Lecture Planning** | `01_Planning/강의구성안.md`, `01_Planning/micro_sessions/` |
```

변경 후:
```
| 1 | **Lecture Planning** | `01_Planning/강의구성안.md`, `01_Planning/Trend_Report.md` |
```

**Step 2: 검증**
```bash
grep -c "micro_sessions" AGENTS.md
# 예상: 0
```

---

### Task 3.2: .agent/Lecture_Creation_Guide.md 수정

**Files:**
- Modify: `.agent/Lecture_Creation_Guide.md`

**Step 1: 1단계 결과물에서 micro_sessions 제거 (L109)**

현재:
```
`YYYY-MM-DD_강의제목/01_Planning/micro_sessions/` (마이크로 세션 명세서, 인덱스, 의존성 그래프)
```

변경 후: 해당 줄 삭제.

**Step 2: 폴더 구조 예시에서 micro_sessions 제거 (L296-303)**

현재:
```
├── 01_Planning/
│   ├── 강의구성안.md
│   ├── Trend_Report.md
│   └── micro_sessions/
│       ├── _index.json
│       ├── _flow.md
│       ├── _dependency.mmd
│       ├── _reference_mapping.json
│       └── 세션-*.md
```

변경 후:
```
├── 01_Planning/
│   ├── 강의구성안.md
│   └── Trend_Report.md
```

**Step 3: 검증**
```bash
grep -c "micro_sessions\|마이크로 세션" .agent/Lecture_Creation_Guide.md
# 예상: 0
```

---

### Task 3.3: Phase 3 커밋

**Step 1: 커밋**
```bash
git add -A && git commit -m "docs: remove micro session references from AGENTS.md and guides

- Update Workflow Overview output paths in root AGENTS.md
- Remove micro_sessions/ from folder structure in Lecture_Creation_Guide.md
- Remove 1단계 micro_sessions result description"
```

---

### Task 3.4: main 브랜치 머지 및 정리

**Step 1: main으로 머지**
```bash
git checkout main && git merge --no-ff feat/remove-micro-sessions
```

**Step 2: 푸시 & 브랜치 삭제**
```bash
git push && git branch -d feat/remove-micro-sessions
```

---

## Phase 4: 최종 검증

### Task 4.1: 전체 교차 검증

**Step 1: 전체 프로젝트에서 마이크로 세션 잔존 참조 검색**
```bash
grep -r "마이크로 세션\|micro_session\|MicroSession\|A3B\|A3C\|micro_sessions\|curriculum-chunking" \
  --include="*.md" --include="*.yaml" --include="*.json" \
  .agent/ AGENTS.md \
  | grep -v "참고자료/" \
  | grep -v "REMOVE_MICRO_SESSIONS_PLAN"
# 예상: 0 결과
```

**Step 2: YAML 유효성 검증**
```bash
python3 -c "import yaml; yaml.safe_load(open('.agent/workflows/01_Lecture_Planning.yaml')); print('01_Lecture_Planning: OK')"
```

**Step 3: JSON 유효성 검증**
```bash
python3 -c "import json; json.load(open('.agent/agents/01_planner/config.json')); print('01_planner config: OK')"
python3 -c "import json; json.load(open('.agent/agents/02_writer/config.json')); print('02_writer config: OK')"
```

**Step 4: 에이전트 파일 수 확인**
```bash
ls .agent/agents/01_planner/*.md | wc -l
# 예상: 6 (A0, A1, A2, A3, A5A, A5B, A7 — A3B, A3C 삭제됨)
# 정정: 7개 (A0, A1, A2, A3, A5A, A5B, A7)
```

---

## 리스크 및 주의사항

### ⚠️ 수정하지 않는 파일들
- `참고자료/` 하위 모든 파일 — 백업/레퍼런스이므로 현행 유지
- `.agent/AGENTS.md` — 루트 AGENTS.md 변경이 반영되면 참조 문서로서 정합성 확인 필요하나, 직접 수정 대상이 아닐 수 있음. 그러나 `Project Structure`와 `Team 1 Flow`에 micro_sessions 참조가 있으므로 **실행 시 함께 검토 후 판단**
- `02_Material_Writing.yaml`, `00_E2E_Pipeline.yaml` — 존재 여부 미확인 (.agent/workflows/ 내). 존재 시 Phase 2/3에서 추가 수정 필요

### ⚠️ 잠재적 추가 작업
1. **`.agent/AGENTS.md` 내부** — Project Structure, Team 1 Flow, 모델 매핑 테이블에 A3B/A3C/micro_sessions 참조 존재. 실행 시 함께 수정해야 할 수 있음
2. **02_Material_Writing.yaml** — 파일이 존재하면 `foreach_session`, micro_sessions 입력 경로 등 추가 수정 필요
3. **00_E2E_Pipeline.yaml** — 파일이 존재하면 output_gate에서 micro_sessions 산출물 경로 제거 필요
4. **슬래시 커맨드 (.claude/commands/)** — lecture-plan 등에 마이크로 세션 참조가 있으면 추가 수정 필요

### ⚠️ A4B 에이전트 이름 결정
현 계획은 A4B 파일명을 유지합니다 (`A4B_Session_Writer.md`). 파일명을 `A4_Session_Writer.md`로 변경하면 02_writer 전체의 참조(A0, config.json, 워크플로우 YAML 등)를 광범위하게 수정해야 합니다. **현 단계에서는 파일명 유지를 권장**하며, 추후 리팩토링에서 이름 변경을 검토합니다.

---

## 요약: Phase별 파일 수/변경량

| Phase | 삭제 | 수정 | 커밋 수 |
|-------|------|------|---------|
| Phase 1 (01_planner) | 2개 파일 | 5개 파일 | 1 |
| Phase 2 (02_writer) | 0 | 5개 파일 | 1 |
| Phase 3 (문서/E2E) | 0 | 2개 파일 | 1 |
| Phase 4 (검증) | 0 | 0 | 0 |
| **합계** | **2** | **12** | **3** |
