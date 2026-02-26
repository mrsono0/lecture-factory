02_Material_Writing 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

`material-writer` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="material-writer", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/02_Material_Writing.yaml` 스텝 순서,
`.agent/agents/02_writer/` 에이전트 프롬프트를 참조하여 파이프라인을 자율 실행합니다.

- 입력 파싱(강의구성안, NotebookLM URL, 로컬 폴더)은 서브에이전트가 판별합니다.
- 산출물: `02_Material/강의교안_v1.0.md` 및 세션별 교안 파일