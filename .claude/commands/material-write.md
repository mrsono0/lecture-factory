02_Material_Writing 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행

전담 서브에이전트에게 위임하여 02_Material_Writing 파이프라인을 실행합니다.

### 위임 지시
아래 3개 리소스를 로드한 서브에이전트가 파이프라인을 자율 실행합니다:
1. **워크플로우**: `.agent/workflows/02_Material_Writing.yaml` (step 순서 & 의존성)
2. **에이전트 프롬프트**: `.agent/agents/02_writer/` (A0~A10 역할 정의)
3. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)

- 입력 파싱(강의구성안, NotebookLM URL, 로컬 폴더)은 서브에이전트가 판별합니다.
- 산출물: `02_Material/강의교안_v1.0.md` 및 세션별 교안 파일
