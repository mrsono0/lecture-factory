AGENTS.md의 규칙을 따라 06_NanoBanana_PPTX 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행 지침

1. 프로젝트 루트의 `AGENTS.md`를 읽고 전체 운영 규칙을 숙지하세요.
2. `.agent/workflows/06_NanoBanana_PPTX.yaml`을 읽고 파이프라인 스텝 순서를 확인하세요.
3. 스킬 파일 5개를 로드하세요:
   - `.agent/skills/nanobanana-ppt-skills/SKILL.md`
   - `.agent/skills/imagen/SKILL.md`
   - `.agent/skills/gemini-api-dev/SKILL.md`
   - `.agent/skills/pptx-official/SKILL.md`
   - `.agent/skills/last30days/SKILL.md`
4. `GEMINI_API_KEY` 환경변수를 확인하세요. 미설정 시 사용자에게 안내합니다.
5. **입력 검증**: `03_Slides/` 디렉토리의 세션별 서브폴더를 탐색합니다.
6. 각 스텝 실행 전 `.agent/agents/06_nanopptx/` 내 해당 에이전트 프롬프트 파일을 읽고 역할을 수행하세요.
7. 파이프라인을 순차 실행하세요 (병렬 없음):
   - C0 (검증) → C1 (플래닝) → C2 (프롬프트) → C3 (이미지 생성)
   - C4 (PPTX 빌드) → C5 (QA) → C0 (승인/부분재생성/반려)
8. 디자인 제약 준수: 헤더/푸터 금지, 밝은 배경색만
9. 최종 산출물을 `06_NanoPPTX/최종_프레젠테이션.pptx`로 저장하세요.
