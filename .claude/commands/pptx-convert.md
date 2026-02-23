05_PPTX_Conversion 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

`pptx-converter` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="pptx-converter", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/05_PPTX_Conversion.yaml` 스텝 순서,
`.agent/agents/05_pptx_converter/` 에이전트 프롬프트, `.agent/skills/pptx-official/` 스킬을
참조하여 파이프라인을 자율 실행합니다.

- HTML 기반 PPTX 변환 (Playwright + PptxGenJS)
- 디자인 제약: 헤더/푸터 금지, 밝은 배경색만
- 산출물: `05_PPTX/최종_프레젠테이션.pptx`


## 로깅 (MANDATORY)

파이프라인 실행 시 `.agent/logging-protocol.md`에 따라 JSONL 로그를 기록해야 합니다.

1. **run_id 생성**: `run_{YYYYMMDD}_{HHMMSS}` 형식으로 생성합니다.
2. **로그 파일**: `.agent/logs/{DATE}_05_PPTX_Conversion.jsonl`에 append합니다.
3. **위임 시 전달**: 서브에이전트에게 위임할 때 prompt에 다음을 포함합니다:
   ```
   [LOGGING] 이 실행의 run_id는 "{run_id}"입니다.
   로그를 ".agent/logs/{DATE}_05_PPTX_Conversion.jsonl"에 기록하세요.
   로깅 프로토콜: .agent/logging-protocol.md
   ```
4. **로깅 프로토콜**: `.agent/logging-protocol.md`의 §9 오케스트레이터 구현 가이드를 참조합니다.