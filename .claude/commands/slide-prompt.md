AGENTS.md의 규칙을 따라 06_SlidePrompt_Generation 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행 지침

1. 프로젝트 루트의 `AGENTS.md`를 읽고 전체 운영 규칙을 숙지하세요.
2. `.agent/workflows/06_SlidePrompt_Generation.yaml`을 읽고 파이프라인 스텝 순서를 확인하세요.
3. **입력 폴더 탐색**:
   - 미지정 → `02_Material/` 내 `*.md` 자동 탐색
   - 외부 폴더 지정 → 해당 폴더 스캔
   - 파일 수는 가변(N개), 발견된 만큼 처리
4. 각 스텝 실행 전 `.agent/agents/06_prompt_generator/` 내 해당 에이전트 프롬프트 파일을 읽고 역할을 수행하세요.
5. 파이프라인을 실행하세요:
   - Phase A: P0 (파일 발견 + 스캐폴딩)
   - Phase B: P1 (교육 구조 ×N) ∥ P3 (전역 비주얼 스펙) — 병렬
   - Phase C: P2 (슬라이드 명세 ×N)
   - Phase D: P0 (교안별 조립) → P4 (QA) → P0 (최종 저장)
6. 03_Slides 산출물이 있으면 품질 향상에 참조하세요.
7. 산출물을 `06_SlidePrompt/{세션ID}_{세션제목}_슬라이드 생성 프롬프트.md` (×N개)로 저장하세요.
