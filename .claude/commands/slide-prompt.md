04_SlidePrompt_Generation 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

`slide-prompt-gen` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="slide-prompt-gen", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/04_SlidePrompt_Generation.yaml` 스텝 순서,
`.agent/agents/04_prompt_generator/` 에이전트 프롬프트를 참조하여 파이프라인을 자율 실행합니다.

- 교안 N개를 분석하여 각각 독립적인 프롬프트 파일을 생성합니다.
- 03_Slides 산출물이 있으면 품질 향상에 참조합니다.
- 산출물: `04_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개)
