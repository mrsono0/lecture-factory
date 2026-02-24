# 로그 파일 중복 생성 문제 분석 및 해결 방안

## 문제 요약

로그 파일이 같은 날 여러 개 생성되고 있습니다:
- `2026-02-24_01_Lecture_Planning.jsonl` (정상)
- `2026-02-24_01_Lecture_Planning_run2.jsonl` (중복)

## 원인 분석

### 1. 로깅 프로토콜 위반
`.agent/logging-protocol.md` §1에 명시된 규칙:
> 같은 날 같은 파이프라인 재실행 시 **append** (덮어쓰기 금지)

하지만 현재 `_run2` 접미사가 붙은 파일이 별도로 생성되고 있습니다.

### 2. 파일 포맷 차이
```bash
# 정상 파일 (logging-protocol.md 준수)
{"run_id":"run_20260224_204705","ts":"2026-02-24T20:47:05","status":"START",...}

# run2 파일 (다른 포맷 - event, pipeline, step 필드 사용)
{"event":"SESSION_START","run_id":"run_20260224_194045","pipeline":"01_Lecture_Planning",...}
```

**결론**: 두 파일은 서로 다른 코드/프로세스에 의해 생성되었습니다. `_run2` 파일은 외부 스크립트나 수동 실행으로 생성된 것으로 보입니다.

## 해결 방안

### 1. 표준 로깅 유틸리티 사용
`.agent/scripts/agent_logger.py`를 사용하여 일관된 로깅을 구현합니다:

```python
from agent_logger import AgentLogger

logger = AgentLogger(workflow="01_Lecture_Planning")

# START 이벤트
logger.log_start(
    step_id="step_1_trend",
    agent="A1_Trend_Researcher",
    category="deep",
    action="research_trend",
    input_bytes=15000
)

# END 이벤트
logger.log_end(
    step_id="step_1_trend",
    output_bytes=28500,
    duration_sec=274
)
```

**핵심 동작**: `AgentLogger._write_log()` 메서드는 `'a'` (append) 모드로 파일을 열어 기존 파일이 있어도 내용을 추가합니다.

### 2. Bash 스크립트 연동
Bash 스크립트에서도 동일한 경로 규칙을 사용:

```bash
# 로그 파일 경로 가져오기
LOG_FILE=$(python3 -c "from agent_logger import get_log_path; print(get_log_path('01_Lecture_Planning'))")

# append 모드로 로그 기록
echo '{"run_id":"...",...}' >> "$LOG_FILE"
```

### 3. 기존 로그 병합 (선택사항)
`_run2` 파일의 내용을 메인 로그 파일에 병합하려면:

```bash
# .agent/logs/ 디렉토리에서 실행
# (주의: run2 파일의 JSON 포맷이 다르므로 변환이 필요할 수 있음)
cat 2026-02-24_01_Lecture_Planning_run2.jsonl >> 2026-02-24_01_Lecture_Planning.jsonl
```

## 권장사항

1. **Agent 구현 시**: `agent_logger.py`를 import하여 표준 로깅 사용
2. **Bash 스크립트**: `get_log_path()` 함수로 경로 획득 후 append 모드 사용
3. **워크플로우 YAML**: `logging.path` 설정에 `{YYYY-MM-DD}_{workflow}.jsonl` 패턴 사용
4. **E2E 실행**: `parent_run_id` 필드로 실행 간 연관성 표시

## 검증 방법

```bash
# 로그 파일 목록 확인
ls -la .agent/logs/

# 파일이 append 모드로 증가하는지 확인 (실행 전후 파일 크기 비교)
wc -l .agent/logs/2026-02-24_01_Lecture_Planning.jsonl
```

## 참조

- 로깅 프로토콜: `.agent/logging-protocol.md`
- 로거 구현: `.agent/scripts/agent_logger.py`
- 분석 스크립트: `.agent/scripts/analyze_logs.sh`
