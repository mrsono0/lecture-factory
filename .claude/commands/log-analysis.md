08_Log_Analysis 워크플로우를 실행합니다.

> **워크플로우**: `.agent/workflows/08_Log_Analysis.yaml` | **에이전트 팀**: `.agent/agents/08_log_analyzer/` (L0~L5, 6인) | 상세는 AGENTS.md Pipeline 8 참조.

## 입력
$ARGUMENTS

## 실행

전담 서브에이전트에게 위임하여 08_Log_Analysis 파이프라인을 실행합니다.

### 위임 지시
아래 4개 리소스를 로드한 서브에이전트가 파이프라인을 자율 실행합니다:
1. **워크플로우**: `.agent/workflows/08_Log_Analysis.yaml` (step 순서 & 의존성)
2. **에이전트 프롬프트**: `.agent/agents/08_log_analyzer/` (L0~L5 역할 정의)
3. **모델 라우팅**: `.agent/AGENTS.md` §Per-Agent Model Routing (카테고리→모델)
4. **스크립트**: `.agent/scripts/analyze_logs.sh` (jq 기반 분석 도구)

- 파이프라인 실행 로그(JSONL) 자동 분석 (보틀넥, 비용, 실패 패턴)
- 5가지 분석 모드: `auto`(기본), `cost`, `performance`, `reliability`, `compare`
- `jq >= 1.6` 필요
- 산출물: `.agent/dashboard/log_analysis_{date}.md`
