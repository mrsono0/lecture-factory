AGENTS.md의 규칙을 따라 Lecture Factory의 전체 파이프라인(End-to-End)을 오케스트레이션합니다.

## 입력
$ARGUMENTS

## 실행

`lecture-orchestrator` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="lecture-orchestrator", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙을 참조하여 Phase 1~4를 순차적으로 실행합니다.

- Phase 1: 기획 (`/project:lecture-plan`)
- Phase 2: 집필 (`/project:material-write`)
- Phase 3: 시각화 (`/project:slide-gen`)
- Phase 4: 프롬프트 생성 (`/project:slide-prompt`)

각 단계의 산출물을 검증한 후 다음 단계로 진행합니다.
사용자가 5, 6, 7단계(PPTX 생성)를 지정하지 않으면 기본 E2E는 Phase 4까지입니다.