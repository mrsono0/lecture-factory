04_SlidePrompt_Generation 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

`slide-prompt-gen` 에이전트(`.claude/agents/slide-prompt-gen.md`)에게 위임하여 04_SlidePrompt_Generation 파이프라인을 실행합니다.

### 위임 지시
아래 3개 리소스를 로드한 서브에이전트가 파이프라인을 자율 실행합니다:
1. **워크플로우**: `.agent/workflows/04_SlidePrompt_Generation.yaml` (step 순서 & 의존성)
2. **에이전트 프롬프트**: `.agent/agents/04_prompt_generator/` (P0~P4 역할 정의)
3. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)

- 교안 N개를 분석하여 각각 독립적인 프롬프트 파일을 생성합니다.
- 03_Slides 산출물이 있으면 품질 향상에 참조합니다.
- 산출물: `04_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개)
