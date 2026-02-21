AGENTS.md의 규칙을 따라 02_Material_Writing 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행 지침

1. 프로젝트 루트의 `AGENTS.md`를 읽고 전체 운영 규칙을 숙지하세요.
2. `.agent/workflows/02_Material_Writing.yaml`을 읽고 파이프라인 스텝 순서를 확인하세요.
3. 사용자 입력에서 다음을 파싱하세요:
   - **입력 파일**: (선택) 강의구성안 파일. 미지정 시 `01_Planning/강의구성안.md` 자동 탐색
   - **NotebookLM URL**: (선택) A1 Source Miner가 참조할 URL
   - **로컬 폴더**: (선택) 프로젝트 폴더 경로 → 스타일/기존 내용 분석
4. 각 스텝 실행 전 `.agent/agents/02_writer/` 내 해당 에이전트 프롬프트 파일을 읽고 역할을 수행하세요.
5. 파이프라인을 실행하세요:
   - Phase 1: A1 (팩트 추출) → A2 (추적성)
   - Phase 2: A3 (골격) → A4 (초안)
   - Phase 3: A5, A6, A7, A9, A10 (5개 병렬 — `run_in_background` 활용)
   - Phase 4: A4 (통합) → A8 (QA — 승인/반려)
6. 최종 산출물을 `{YYYY-MM-DD_강의제목}/02_Material/강의교안_v1.0.md`로 저장하세요.
