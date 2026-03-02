07_Manus_Slide 워크플로우를 실행합니다.

> **워크플로우**: `.agent/workflows/07_Manus_Slide.yaml` | **에이전트 팀**: `.agent/agents/07_manus_slide/` (D0~D5, 6인) | 상세는 AGENTS.md Pipeline 7 참조.

## 입력
$ARGUMENTS

## 실행

전담 서브에이전트에게 위임하여 07_Manus_Slide 파이프라인을 실행합니다.

### 위임 지시
아래 4개 리소스를 로드한 서브에이전트가 파이프라인을 자율 실행합니다:
1. **워크플로우**: `.agent/workflows/07_Manus_Slide.yaml` (step 순서 & 의존성)
2. **에이전트 프롬프트**: `.agent/agents/07_manus_slide/` (D0~D5 역할 정의)
3. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)
4. **스크립트**: `.agent/scripts/manus_slide.py` (Manus API 연동)

- Manus AI(Nano Banana Pro) 기반 슬라이드 생성
- MANUS_API_KEY 필요
- 대형 프롬프트 교시 단위 자동 분할 + PPTX 병합
- 산출물: `07_ManusSlides/{세션ID}_{세션제목}.pptx`
