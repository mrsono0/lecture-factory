01_Lecture_Planning 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

전담 서브에이전트에게 위임하여 01_Lecture_Planning 파이프라인을 실행합니다.

### 위임 지시
아래 3개 리소스를 로드한 서브에이전트가 파이프라인을 자율 실행합니다:
1. **워크플로우**: `.agent/workflows/01_Lecture_Planning.yaml` (step 순서 & 의존성)
2. **에이전트 프롬프트**: `.agent/agents/01_planner/` (A0~A7 역할 정의)
3. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)

- 입력 파싱(강의 주제 파일, NotebookLM URL, 로컬 폴더)은 서브에이전트가 판별합니다.
- 산출물: `01_Planning/강의구성안.md`, `01_Planning/Trend_Report.md`

> 💡 주제 파일 없이 참고자료와 NotebookLM URL만 제공해도, brainstorming을 통해 주제를 포함한 8개 항목을 수집한 후 기획을 진행합니다. 인수 없이 실행하면 전체 8개 항목을 brainstorming으로 수집합니다.
