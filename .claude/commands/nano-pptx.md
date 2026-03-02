06_NanoBanana_PPTX 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

전담 서브에이전트에게 위임하여 06_NanoBanana_PPTX 파이프라인을 실행합니다.

### 위임 지시
아래 3개 리소스를 로드한 서브에이전트가 파이프라인을 자율 실행합니다:
1. **워크플로우**: `.agent/workflows/06_NanoBanana_PPTX.yaml` (step 순서 & 의존성)
2. **에이전트 프롬프트**: `.agent/agents/06_nanopptx/` (C0~C5 역할 정의)
3. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)

- AI 이미지 기반 고품질 슬라이드 생성 (Nano Banana Pro)
- GEMINI_API_KEY 필요
- 디자인 제약: 헤더/푸터 금지, 밝은 배경색만
- 산출물: `06_NanoPPTX/최종_프레젠테이션.pptx`
