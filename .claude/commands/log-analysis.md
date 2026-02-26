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