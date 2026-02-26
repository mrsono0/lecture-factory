06_NanoBanana_PPTX 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

`nano-pptx` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="nano-pptx", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/06_NanoBanana_PPTX.yaml` 스텝 순서,
`.agent/agents/06_nanopptx/` 에이전트 프롬프트, 관련 스킬 5개를
참조하여 파이프라인을 자율 실행합니다.

- AI 이미지 기반 고품질 슬라이드 생성 (Nano Banana Pro)
- GEMINI_API_KEY 필요
- 디자인 제약: 헤더/푸터 금지, 밝은 배경색만
- 산출물: `06_NanoPPTX/최종_프레젠테이션.pptx`