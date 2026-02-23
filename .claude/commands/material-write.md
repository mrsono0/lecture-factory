AGENTS.md의 규칙을 따라 02_Material_Writing 워크플로우를 실행합니다.
## 입력
$ARGUMENTS
## 실행 지침

1. 사용자 입력에서 다음을 파싱하세요:
   - **입력 파일**: (선택) 강의구성안 파일. 미지정 시 `01_Planning/강의구성안.md` 자동 탐색
   - **NotebookLM URL**: (선택) A1 Source Miner가 참조할 URL
   - **로컬 폴더**: (선택) 프로젝트 폴더 경로 → 스타일/기존 내용 분석
2. `material-writer` 서브에이전트에게 작업을 위임하세요:
   ```
   Task(subagent_type="material-writer", prompt="<파싱된 입력 정보를 포함한 실행 지시>")
   ```
   - 파싱된 입력 파일, NotebookLM URL, 로컬 폴더 경로를 prompt에 모두 포함하세요.
   - 서브에이전트가 `AGENTS.md`, 워크플로우 YAML, 에이전트 프롬프트를 자체 로드하여 파이프라인을 실행합니다.
3. 서브에이전트 완료 후 산출물이 `{YYYY-MM-DD_강의제목}/02_Material/강의교안_v1.0.md`에 저장되었는지 확인하세요.

## 로깅 (MANDATORY)

파이프라인 실행 시 `.agent/logging-protocol.md`에 따라 JSONL 로그를 기록해야 합니다.

1. **run_id 생성**: `run_{YYYYMMDD}_{HHMMSS}` 형식으로 생성합니다.
2. **로그 파일**: `.agent/logs/{DATE}_02_Material_Writing.jsonl`에 append합니다.
3. **위임 시 전달**: 서브에이전트에게 위임할 때 prompt에 다음을 포함합니다:
   ```
   [LOGGING] 이 실행의 run_id는 "{run_id}"입니다.
   로그를 ".agent/logs/{DATE}_02_Material_Writing.jsonl"에 기록하세요.
   로깅 프로토콜: .agent/logging-protocol.md
   ```
4. **로깅 프로토콜**: `.agent/logging-protocol.md`의 §9 오케스트레이터 구현 가이드를 참조합니다.