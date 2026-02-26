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


## 로깅 (MANDATORY)

파이프라인 실행 시 `.agent/logging-protocol.md`에 따라 JSONL 로그를 기록해야 합니다.

1. **run_id 생성**: `run_{YYYYMMDD}_{HHMMSS}` 형식으로 생성합니다.
2. **로그 파일**: `.agent/logs/{DATE}_02_Material_Writing.jsonl`에 append합니다.
3. **위임 시 전달**: 서브에이전트에게 위임할 때 prompt에 다음을 포함합니다:
   ```
   [LOGGING] 이 실행의 run_id는 "{run_id}"입니다.
   로그를 ".agent/logs/{DATE}_02_Material_Writing.jsonl"에 기록하세요.
   로깅 프로토콜: .agent/logging-protocol.md
   ```
4. **로깅 프로토콜**: `.agent/logging-protocol.md`의 §9 오케스트레이터 구현 가이드를 참조합니다.
