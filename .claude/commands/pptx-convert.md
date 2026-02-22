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
