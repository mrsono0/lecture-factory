03_Slide_Generation 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

전담 서브에이전트에게 위임하여 03_Slide_Generation 파이프라인을 실행합니다.

### 위임 지시
아래 3개 리소스를 로드한 서브에이전트가 파이프라인을 자율 실행합니다:
1. **워크플로우**: `.agent/workflows/03_Slide_Generation.yaml` (step 순서 & 의존성)
2. **에이전트 프롬프트**: `.agent/agents/03_visualizer/` (A0~A10 역할 정의)
3. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)

- 단일 파일 / 배치 모드 / 자동 탐색 모드를 서브에이전트가 판별합니다.
- 산출물: `03_Slides/{session}/슬라이드기획안.md` 및 Phase별 중간 산출물
