07_Manus_Slide 워크플로우를 실행합니다.

> **워크플로우**: `.agent/workflows/07_Manus_Slide.yaml` | **에이전트 팀**: `.agent/agents/07_manus_slide/` (D0~D5, 6인) | 상세는 AGENTS.md Pipeline 7 참조.

## 입력
$ARGUMENTS

## 실행

`manus-slide` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="manus-slide", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/07_Manus_Slide.yaml` 스텝 순서,
`.agent/agents/07_manus_slide/` 에이전트 프롬프트, `.agent/scripts/manus_slide.py` 스크립트를
참조하여 파이프라인을 자율 실행합니다.

- Manus AI(Nano Banana Pro) 기반 슬라이드 생성
- MANUS_API_KEY 필요
- 대형 프롬프트 교시 단위 자동 분할 + PPTX 병합
- 산출물: `07_ManusSlides/{세션ID}_{세션제목}.pptx`