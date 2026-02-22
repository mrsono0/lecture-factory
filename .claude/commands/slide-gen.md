03_Slide_Generation 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

`slide-generator` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="slide-generator", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/03_Slide_Generation.yaml` 스텝 순서,
`.agent/agents/03_visualizer/` 에이전트 프롬프트를 참조하여 파이프라인을 자율 실행합니다.

- 단일 파일 / 배치 모드 / 자동 탐색 모드를 서브에이전트가 판별합니다.
- 산출물: `03_Slides/{session}/슬라이드기획안.md` 및 Phase별 중간 산출물
