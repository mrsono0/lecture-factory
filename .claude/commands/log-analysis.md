08_Log_Analysis 워크플로우를 실행합니다.

> **워크플로우**: `.agent/workflows/08_Log_Analysis.yaml` | **에이전트 팀**: `.agent/agents/08_log_analyzer/` (L0~L5, 6인) | 상세는 AGENTS.md Pipeline 8 참조.

## 입력
$ARGUMENTS

## 실행

`log-analyzer` 서브에이전트에게 위임하여 실행합니다.

```
Task(subagent_type="log-analyzer", prompt=$ARGUMENTS)
```

서브에이전트가 AGENTS.md 규칙, `.agent/workflows/08_Log_Analysis.yaml` 스텝 순서,
`.agent/agents/08_log_analyzer/` 에이전트 프롬프트, `.agent/scripts/analyze_logs.sh` 분석 스크립트를
참조하여 파이프라인을 자율 실행합니다.

- 파이프라인 실행 로그(JSONL) 자동 분석 (보틀넥, 비용, 실패 패턴)
- 5가지 분석 모드: `auto`(기본), `cost`, `performance`, `reliability`, `compare`
- `jq >= 1.6` 필요
- 산출물: `.agent/dashboard/log_analysis_{date}.md`

## 분석 모드 지정

```bash
# 기본 (전체 분석)
/project:log-analysis

# 비용 집중 분석
/project:log-analysis --mode cost

# 성능/보틀넥 집중
/project:log-analysis --mode performance

# 안정성/실패 집중
/project:log-analysis --mode reliability

# 실행 간 비교
/project:log-analysis --mode compare

# 특정 로그 파일 지정
/project:log-analysis .agent/logs/2026-02-23_01_Lecture_Planning.jsonl

# 특정 파이프라인만 분석
/project:log-analysis 01_Lecture_Planning 파이프라인만 분석해줘
```

## 분석 스크립트 직접 사용 (에이전트 없이)

```bash
# 전체 분석
.agent/scripts/analyze_logs.sh

# 개별 서브커맨드
.agent/scripts/analyze_logs.sh summary            # 파이프라인별 실행 요약
.agent/scripts/analyze_logs.sh bottleneck 10      # 소요시간 TOP 10
.agent/scripts/analyze_logs.sh cost               # 비용 분석
.agent/scripts/analyze_logs.sh agent              # 에이전트별 통계
.agent/scripts/analyze_logs.sh failure            # 재시도/실패 분석
.agent/scripts/analyze_logs.sh parallel           # 병렬 실행 효율
.agent/scripts/analyze_logs.sh category           # LLM 카테고리별 비용
.agent/scripts/analyze_logs.sh timeline [run_id]  # 특정 실행의 타임라인
.agent/scripts/analyze_logs.sh validate           # JSONL 스키마 검증
.agent/scripts/analyze_logs.sh report             # 종합 마크다운 리포트 생성
.agent/scripts/analyze_logs.sh all                # 위 모든 분석 한번에 실행
```

## 사전 요구사항

- `jq >= 1.6` 설치 (`brew install jq` / `apt install jq`)
- `.agent/logs/` 디렉토리에 JSONL 로그 파일 1개 이상 존재
- 로그는 파이프라인 실행 시 자동 생성됨 (`.agent/logging-protocol.md` 참조)