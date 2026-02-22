Manus AI를 이용하여 06_SlidePrompt의 프롬프트 파일로 슬라이드를 생성합니다.

> **워크플로우**: `.agent/workflows/07_Manus_Slide.yaml` | **에이전트 팀**: `.agent/agents/07_manus_slide/` (D0~D5, 6인) | 상세는 AGENTS.md Pipeline 7 참조.

## 입력
$ARGUMENTS

## 실행 지침

1. **사전 준비**: 프로젝트 루트의 `AGENTS.md`를 읽고 Pipeline 7(Manus Slide Generation)의 운영 규칙을 숙지하세요.
2. **환경 확인**:
   - `.agent/.env`에서 `MANUS_API_KEY`가 설정되어 있는지 확인하세요.
   - 미설정 시 사용자에게 Manus 대시보드(https://manus.im)에서 API Key 발급을 안내하세요.
   - `requests` 패키지가 설치되어 있는지 확인하고, 없으면 `pip install requests`를 실행하세요.

3. **프로젝트 폴더 결정**:
   - 입력이 있으면 해당 경로를 사용합니다.
   - 입력이 없으면 프로젝트 루트의 최신 날짜 프로젝트 폴더(예: `2026-02-19_AI-native_데이터사이언스기초`)를 자동 탐색합니다.
   - `06_SlidePrompt/` 폴더가 존재하는지 확인합니다.

4. **프롬프트 파일 목록 확인**:
   - `06_SlidePrompt/*슬라이드 생성 프롬프트.md` 패턴으로 파일을 탐색합니다.
   - 발견된 파일 목록을 사용자에게 보여주고 진행 여부를 확인합니다.

5. **슬라이드 생성 실행**:
   - `.agent/scripts/manus_slide.py` 스크립트를 실행합니다.
   - 전체 처리: `python .agent/scripts/manus_slide.py {프로젝트폴더경로}`
   - 단일/복수 파일 지정: `python .agent/scripts/manus_slide.py {프로젝트폴더경로} --file Day1_AM`
   - **분할 비활성화**: `python .agent/scripts/manus_slide.py {프로젝트폴더경로} --no-split`
   - 사용자가 $ARGUMENTS에 특정 파일명이나 세션ID(예: "Day1_AM", "환경구축")를 지정한 경우, `--file` 옵션으로 해당 파일만 처리합니다.
   - 스크립트가 자동으로:
     - **교시 분할 판정**: 1,000줄 초과 또는 슬라이드 35장 초과 시 교시(세션) 단위로 자동 분할
     - 각 프롬프트(또는 청크)를 Manus AI에 순차 제출
     - 30초 간격으로 완료 폴링 (파일당 최대 30분)
     - 완료 시 PPTX 파일 자동 다운로드
     - **분할 시**: 청크별 PPTX를 python-pptx로 자동 병합 (슬라이드 노트 보존)
     - `07_ManusSlides/` 폴더에 저장
   - 실행 시간이 길 수 있으므로 (10개 파일 기준 30분~2시간) 백그라운드 실행을 권장합니다.

6. **드라이런 모드** (선택):
   - API를 호출하지 않고 파일 탐색만 확인하려면:
   - `python .agent/scripts/manus_slide.py {프로젝트폴더경로} --dry-run`

7. **결과 확인**:
   - 실행 완료 후 `07_ManusSlides/` 폴더의 파일을 확인합니다.
   - `07_ManusSlides/generation_report.json`에서 성공/실패 현황을 확인합니다.
   - `07_ManusSlides/manus_task_log.json`에서 개별 task_id를 확인합니다.
   - 수동 다운로드가 필요한 경우 shareable_link를 안내합니다.

8. **결과 리포트 출력**:
   - 성공한 파일 목록 (파일명 + 크기)
   - 수동 다운로드 필요 파일 (Manus 웹 링크)
   - 실패 파일 (원인)
   - 총 소요 시간

## 교시 분할 전략 (Chunking)

P06 프롬프트 파일이 대용량(860~1,950줄)인 경우, Manus AI의 최적 처리를 위해 교시(세션) 단위로 자동 분할합니다:

| 조건 | 동작 |
|------|------|
| ≤1,000줄 AND ≤35 슬라이드 | 원샷 제출 (분할 없음) |
| >1,000줄 OR >35 슬라이드 | 교시 단위 자동 분할 |

- **분할 기준**: ③ 슬라이드 명세의 `#### N. 세션 X-Y 파트:`, ⑥ 교안 원문의 `## 세션 X-Y:` 경계
- **청크 구성**: ①②④⑤ 공통 헤더 + ③-N번째 교시 슬라이드 + ⑥-N번째 교시 원문
- **병합**: 청크별 PPTX를 python-pptx로 병합 (슬라이드 노트 텍스트 보존)
- **비활성화**: `--no-split` 플래그로 분할 없이 원본 전체 제출 가능

## 트러블슈팅

- **API Key 오류**: `.agent/.env`의 `MANUS_API_KEY` 값을 확인하세요. Manus Pro 또는 Team 플랜이 필요합니다.
- **타임아웃**: Manus 슬라이드 생성은 3~15분 소요됩니다. 30분 초과 시 타임아웃으로 처리됩니다.
- **다운로드 실패**: Manus 파일은 48시간 후 자동 삭제됩니다. task_log.json의 task_id로 Manus 웹에서 확인하세요.
- **중단 복구**: `07_ManusSlides/manus_task_log.json`에 중간 결과가 저장됩니다. 이미 완료된 파일은 건너뛰도록 스크립트를 재실행하세요.

## 주의사항

- Nano Banana Pro 슬라이드 생성은 **Manus Pro/Team 플랜** (유료)이 필요합니다.
- 10개 프롬프트 파일 기준 예상 소요 시간: 30분~2시간
- Manus에 업로드된 파일은 **48시간 후 자동 삭제**되므로 즉시 다운로드하세요.
- API 호출 비용이 발생할 수 있습니다. 프롬프트 수에 비례합니다.
