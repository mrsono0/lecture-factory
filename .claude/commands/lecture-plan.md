AGENTS.md의 규칙을 따라 01_Lecture_Planning 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행 지침

1. 사용자 입력에서 다음을 파싱하세요:
   - **입력 파일**: 강의 주제 파일 (예: `AI-native_파이썬기초.md`)
   - **NotebookLM URL**: (선택) 참고할 NotebookLM 주소
   - **로컬 폴더**: (선택) 참고할 로컬 폴더 경로 → 모든 파일을 먼저 분석
2. `lecture-planner` 서브에이전트에게 작업을 위임하세요:
   ```
   Task(subagent_type="lecture-planner", prompt="<파싱된 입력 정보를 포함한 실행 지시>")
   ```
   - 파싱된 입력 파일, NotebookLM URL, 로컬 폴더 경로를 prompt에 모두 포함하세요.
   - 서브에이전트가 `AGENTS.md`, 워크플로우 YAML, 에이전트 프롬프트를 자체 로드하여 파이프라인을 실행합니다.
3. 서브에이전트 완료 후 산출물이 `{YYYY-MM-DD_강의제목}/01_Planning/강의구성안.md`에 저장되었는지 확인하세요.
