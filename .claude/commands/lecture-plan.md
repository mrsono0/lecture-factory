01_Lecture_Planning 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

`lecture-planner` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="lecture-planner", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/01_Lecture_Planning.yaml` 스텝 순서,
`.agent/agents/01_planner/` 에이전트 프롬프트를 참조하여 파이프라인을 자율 실행합니다.

- 입력 파싱(강의 주제 파일, NotebookLM URL, 로컬 폴더)은 서브에이전트가 판별합니다.
- 산출물: `01_Planning/강의구성안.md`, `01_Planning/micro_sessions/` 및 관련 인덱스 파일