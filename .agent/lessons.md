# Lecture Factory Lessons Learned

> 수정받은 실수, 스타일 가이드 위반, 반복 패턴과 교훈 기록

---

## 2026-02-24: NotebookLM 미실행 문제 (Pipeline 01)

### 문제 상황
- **증상**: Pipeline 01 실행 시 NotebookLM URL이 제공되었으나, A1_Trend_Researcher가 실제로 쿼리를 실행하지 않음
- **결과**: 강의구성안.md (v2.1)에 NotebookLM 내용 미반영, 로컬 파일만으로 작성됨
- **검출**: grep으로 NotebookLM URL/"Query 1"/"소스 기반" 검색 시 미출현

### 근본 원인
1. **Subagent 도구 제한**: Subagent가 `skill()` 도구에 접근 불가
2. **Anti-Hallucination 실패**: "반드시 실행하세요" 프롬프트 ≠ 실제 실행 보장
3. **검증 부재**: A0_Orchestrator가 A1의 실행 결과를 검증하지 않음

### 적용된 수정방안

#### 1. A1_Trend_Researcher.md 강화
- 🔴 CRITICAL 섹션 추가: bash() 도구 사용 강제
- 검증 체크포인트 4항목 추가 (PASS/FAIL 기준)
- Mandatory Output Format 정의 (실행 증거 형식)

#### 2. A0_Orchestrator.md 검증 프로토콜 추가
- A1 산출물 검증 체크리스트 5항목
- 실패 시 워크플로우 (반려 → RETRY → 로그 기록)
- 검증 통과 시 DECISION 이벤트 기록

#### 3. Workflow YAML 문서화
- NotebookLM Execution Note 추가 (Critical)
- Step 1에 notes 필드 추가 (검증 방법, 실패 시 조치)

### 교훈
- **Subagent에 skill 사용 위임 금지**: Main Agent에서 선실행 후 결과 전달
- **검증 체크포인트 의무화**: "실행하세요" → "실행 결과를 검증하세요"
- **할루시네이션 방지**: stdout 출력이 답변에 포함되었는지 확인

### 관련 파일
- `.agent/agents/01_planner/A1_Trend_Researcher.md` (수정됨)
- `.agent/agents/01_planner/A0_Orchestrator.md` (수정됨)
- `.agent/workflows/01_Lecture_Planning.yaml` (수정됨)

