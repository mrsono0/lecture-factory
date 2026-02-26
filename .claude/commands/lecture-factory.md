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


## 로깅 (MANDATORY — E2E 특수)

E2E 파이프라인 실행 시 `.agent/logging-protocol.md`에 따라 JSONL 로그를 기록해야 합니다.

1. **마스터 run_id 생성**: `run_{YYYYMMDD}_{HHMMSS}` 형식으로 E2E 실행 전체를 추적하는 마스터 `run_id`를 생성합니다.
2. **하위 파이프라인 전달**: 각 Phase 실행 시 마스터 `run_id`를 하위 커맨드에 전달합니다:
   ```
   [LOGGING] parent_run_id="{마스터 run_id}"
   ```
   - Phase 1 → `.agent/logs/{DATE}_01_Lecture_Planning.jsonl`
   - Phase 2 → `.agent/logs/{DATE}_02_Material_Writing.jsonl`
   - Phase 3 → `.agent/logs/{DATE}_03_Slide_Generation.jsonl`
   - Phase 4 → `.agent/logs/{DATE}_04_SlidePrompt_Generation.jsonl`
3. **각 하위 파이프라인**은 자체 로그 파일에 기록하되, `parent_run_id` 필드도 포함합니다.
4. **로깅 프로토콜**: `.agent/logging-protocol.md`의 §9.4 상위 오케스트레이터 로깅 책임을 참조합니다.
