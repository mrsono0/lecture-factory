AGENTS.md의 규칙을 따라 Lecture Factory의 전체 파이프라인(End-to-End)을 오케스트레이션합니다.

## 입력
$ARGUMENTS

## 실행 지침

1. **사전 준비**: 프로젝트 루트의 `AGENTS.md`를 읽고 전체 운영 규칙을 숙지하세요.
2. **역할**: 당신은 전체 파이프라인을 조율하는 마스터 오케스트레이터입니다.
3. **입력 파싱**: 사용자 입력에서 다음을 추출하세요:
   - **입력 파일**: 코어 마크다운 파일 (예: `파이썬기초.md`)
   - **로컬 폴더**: 참고할 로컬 디렉토리 경로
   - **NotebookLM URL**: 참고할 웹 주소
   - **딥리서치**: "자료 수집 시 필수로 딥리서치를 수행할 것" 이라는 조건을 모든 에이전트에게 강제해야 합니다.
3. **순차적 파이프라인 실행**: 다음 단계를 **순차적(Sequentially)**으로 하나씩 지시하고, 각 단계의 산출물이 완전히 생성된 것을 확인한 후 다음 단계로 넘어가야 합니다. (병렬 실행 절대 금지)
   
   - **Phase 1: 기획 (`/project:lecture-plan`)**
     - 입력: 사용자가 제공한 초기 파일 및 URL, 로컬 폴더를 **반드시** `$ARGUMENTS` 형태로 전달하세요. (예: `/project:lecture-plan 입력 파일은 파이썬기초.md 이고 로컬 폴더는 참고자료, NotebookLM은 https://... 야.`)
     - 지시: "딥리서치를 필수로 수행하여 강의 구성안 작성"
     - 대기: `01_Planning/강의구성안.md`가 생성되었는지 확인
   
   - **Phase 2: 집필 (`/project:material-write`)**
     - 입력: Phase 1에서 생성된 `01_Planning/강의구성안.md` 및 **초기 사용자가 제공한 URL과 로컬 폴더 정보를 유실하지 말고 반드시 포함해서 전달하세요.** (예: `/project:material-write 입력 파일은 01_Planning/강의구성안.md 이고 로컬 폴더는 참고자료, NotebookLM은 https://... 야.`)
     - 지시: "딥리서치를 필수로 수행하여 상세 교안 작성"
     - 대기: `02_Material/강의교안_v1.0.md`가 생성되었는지 확인
   
   - **Phase 3: 시각화 (`/project:slide-gen`)**
     - 입력: Phase 2에서 생성된 `02_Material/강의교안_v1.0.md` (예: `/project:slide-gen 입력 파일은 02_Material/강의교안_v1.0.md 야.`)
     - 지시: "슬라이드 스토리보드 및 기획안 작성"
     - 대기: `03_Slides/` 디렉토리 내에 기획안이 생성되었는지 확인
   
   - **Phase 4: 프롬프트 생성 (`/project:slide-prompt`)**
     - 입력: Phase 2 교안 및 Phase 3 스토리보드 (예: `/project:slide-prompt 입력 파일은 02_Material/강의교안_v1.0.md 이고 03_Slides/ 산출물을 참조해.`)
     - 지시: "원샷 슬라이드 프롬프트 추출 생성"
     - 대기: `04_SlidePrompt/` 디렉토리에 마크다운 파일 생성 확인

   *(참고: 사용자가 특별히 4, 5, 7단계(PPTX 생성)를 지정하지 않았다면 기본 E2E 프로세스는 6단계 프롬프트 생성까지를 의미합니다.)*

5. **검증 및 통신**: 각 단계로 넘어갈 때 사용자에게 현재 어느 단계를 진행 중인지 명확히 알리세요.
6. **작업 분할의 원칙**: 단일 턴(Single turn)에 모든 것을 한 번에 처리하려 하지 마세요. 각 파이프라인의 내부 워크플로우 YAML을 준수하며 깊이 있게(Depth over Speed) 순서대로 진행해야 합니다.

## 로깅 (MANDATORY — E2E 특수)

E2E 파이프라인 실행 시 `.agent/logging-protocol.md`에 따라 JSONL 로그를 기록해야 합니다.

1. **마스터 run_id 생성**: `run_{YYYYMMDD}_{HHMMSS}` 형식으로 E2E 실행 전체를 추적하는 마스터 `run_id`를 생성합니다.
2. **하위 파이프라인 전달**: 각 Phase 실행 시 마스터 `run_id`를 하위 커맨드에 전달합니다:
   ```
   [LOGGING] parent_run_id="{마스터 run_id}"
   ```
   - Phase 1 (`/project:lecture-plan`) → 로그: `.agent/logs/{DATE}_01_Lecture_Planning.jsonl`
   - Phase 2 (`/project:material-write`) → 로그: `.agent/logs/{DATE}_02_Material_Writing.jsonl`
   - Phase 3 (`/project:slide-gen`) → 로그: `.agent/logs/{DATE}_03_Slide_Generation.jsonl`
   - Phase 4 (`/project:slide-prompt`) → 로그: `.agent/logs/{DATE}_04_SlidePrompt_Generation.jsonl`
3. **각 하위 파이프라인**은 자체 로그 파일에 기록하되, `parent_run_id` 필드도 포함합니다.
4. **로깅 프로토콜**: `.agent/logging-protocol.md`의 §9.4 상위 오케스트레이터 로깅 책임을 참조합니다.