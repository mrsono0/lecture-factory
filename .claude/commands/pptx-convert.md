AGENTS.md의 규칙을 따라 05_PPTX_Conversion 워크플로우를 실행합니다.

## 입력
$ARGUMENTS

## 실행 지침

1. 프로젝트 루트의 `AGENTS.md`를 읽고 전체 운영 규칙을 숙지하세요.
2. `.agent/workflows/05_PPTX_Conversion.yaml`을 읽고 파이프라인 스텝 순서를 확인하세요.
3. `.agent/skills/pptx-official/SKILL.md`와 `html2pptx.md`를 읽고 변환 규칙을 숙지하세요.
4. **입력 검증**: `03_Slides/` 디렉토리의 세션별 서브폴더를 탐색합니다. 1개면 자동 선택, 복수면 사용자에게 확인합니다.
5. 각 스텝 실행 전 `.agent/agents/05_pptx_converter/` 내 해당 에이전트 프롬프트 파일을 읽고 역할을 수행하세요.
6. 파이프라인을 실행하세요:
   - B0 (검증) → B1 (파싱) → B3 (에셋) → B2 (HTML) → B4 (PPTX 조립)
   - B5 (QA) → B0 (승인/반려/재작업)
7. 디자인 제약 준수: 헤더/푸터 금지, 밝은 배경색만
8. 최종 산출물을 `05_PPTX/최종_프레젠테이션.pptx`로 저장하세요.
