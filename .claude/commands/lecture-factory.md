AGENTS.md의 규칙을 따라 Lecture Factory의 전체 파이프라인(End-to-End)을 오케스트레이션합니다.

## 입력
$ARGUMENTS

## 실행

전담 서브에이전트에게 위임하여 E2E 파이프라인을 실행합니다.

### 위임 지시
아래 2개 리소스를 로드한 서브에이전트가 Phase 1~4를 순차적으로 실행합니다:
1. **워크플로우**: `.agent/workflows/00_E2E_Pipeline.yaml` (전체 파이프라인 순서)
2. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)

- Phase 1: 기획 (`/project:lecture-plan`)
- Phase 2: 집필 (`/project:material-write`)
- Phase 3: 시각화 (`/project:slide-gen`)
- Phase 4: 프롬프트 생성 (`/project:slide-prompt`)

각 단계의 산출물을 검증한 후 다음 단계로 진행합니다.
사용자가 5, 6, 7단계(PPTX 생성)를 지정하지 않으면 기본 E2E는 Phase 4까지입니다.
