AGENTS.md의 규칙을 따라 01_Lecture_Planning 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행 지침

1. 프로젝트 루트의 `AGENTS.md`를 읽고 전체 운영 규칙을 숙지하세요.
2. `.agent/workflows/01_Lecture_Planning.yaml`을 읽고 파이프라인 스텝 순서를 확인하세요.
3. 사용자 입력에서 다음을 파싱하세요:
   - **입력 파일**: 강의 주제 파일 (예: `AI-native_파이썬기초.md`)
   - **NotebookLM URL**: (선택) 참고할 NotebookLM 주소
   - **로컬 폴더**: (선택) 참고할 로컬 폴더 경로 → 모든 파일을 먼저 분석
4. 각 스텝 실행 전 `.agent/agents/01_planner/` 내 해당 에이전트 프롬프트 파일을 읽고 역할을 수행하세요.
5. 파이프라인을 순서대로 실행하세요:
   - Step 0: A0 (요청 분석) → Step 1: A1 (트렌드) → Step 2: A5B (학습자)
   - Step 3: A3 (커리큘럼) → Step 4∥5: A2+A7 (병렬) → Step 6: A5A (QA)
   - Step 7: A0 (승인/반려)
6. 최종 산출물을 `{YYYY-MM-DD_강의제목}/01_Planning/강의구성안.md`로 저장하세요.
