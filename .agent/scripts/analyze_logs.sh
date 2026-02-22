#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────
# Lecture Factory — Agent Execution Log Analyzer
# ─────────────────────────────────────────────────────────
# Usage:
#   ./analyze_logs.sh                    # 전체 분석 (모든 로그)
#   ./analyze_logs.sh summary            # 파이프라인 요약만
#   ./analyze_logs.sh bottleneck [N]     # 보틀넥 TOP N (기본 5)
#   ./analyze_logs.sh cost               # 비용 분석
#   ./analyze_logs.sh agent              # 에이전트별 통계
#   ./analyze_logs.sh failure            # 재시도/실패 분석
#   ./analyze_logs.sh parallel           # 병렬 실행 효율
#   ./analyze_logs.sh category           # 카테고리별 비용
#   ./analyze_logs.sh timeline [run_id]  # 실행 타임라인
#   ./analyze_logs.sh validate           # 스키마 검증
#   ./analyze_logs.sh report             # 종합 리포트 (마크다운)
#
# Requires: jq >= 1.6
# Log dir:  .agent/logs/*.jsonl
# Protocol: .agent/logging-protocol.md
# ─────────────────────────────────────────────────────────
set -euo pipefail

# ── 경로 설정 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/.agent/logs"

# ── 색상 코드 ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── 유틸리티 ──
header() {
  echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${NC}"
  echo -e "${BOLD}${CYAN}  $1${NC}"
  echo -e "${BOLD}${CYAN}══════════════════════════════════════════${NC}"
}

subheader() {
  echo -e "\n${BOLD}${BLUE}── $1 ──${NC}"
}

warn() { echo -e "${YELLOW}⚠ $1${NC}"; }
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; }

check_deps() {
  if ! command -v jq &>/dev/null; then
    fail "jq가 설치되어 있지 않습니다. brew install jq 또는 apt install jq"
    exit 1
  fi
}

get_log_files() {
  local -a files=()
  while IFS= read -r -d '' f; do
    files+=("$f")
  done < <(find "$LOG_DIR" -name '*.jsonl' -type f -print0 2>/dev/null | sort -z)
  if [[ ${#files[@]} -eq 0 ]]; then
    warn "로그 파일이 없습니다: $LOG_DIR/*.jsonl"
    exit 0
  fi
  printf '%s\0' "${files[@]}"
}
concat_logs() {
  while IFS= read -r -d '' f; do
    cat "$f"
  done < <(get_log_files)
}

# ════════════════════════════════════════
# 1. 파이프라인 요약 (Pipeline Summary)
# ════════════════════════════════════════
cmd_summary() {
  header "파이프라인 실행 요약"

  concat_logs | jq -s '
    group_by(.run_id) | map({
      run_id: .[0].run_id,
      workflow: .[0].workflow,
      start_ts: (map(.ts) | min),
      end_ts: (map(.ts) | max),
      steps: (map(select(.status=="END")) | length),
      total_duration_sec: (map(select(.status=="END") | .duration_sec) | add),
      total_input_tokens: (map(select(.status=="END") | .est_input_tokens) | add),
      total_output_tokens: (map(select(.status=="END") | .est_output_tokens) | add),
      total_cost_usd: (map(select(.status=="END") | .est_cost_usd) | add),
      failures: (map(select(.status=="FAIL")) | length),
      retries: (map(select(.status=="RETRY")) | length),
      decision: (map(select(.status=="END" and .decision != null) | .decision) | last // "N/A")
    }) | sort_by(.start_ts) | reverse
  '
}

# ════════════════════════════════════════
# 2. 보틀넥 분석 (Bottleneck Analysis)
# ════════════════════════════════════════
cmd_bottleneck() {
  local top_n=${1:-5}
  header "보틀넥 분석 — 소요시간 TOP $top_n"

  concat_logs | jq -s --argjson n "$top_n" '
    map(select(.status=="END"))
    | sort_by(-.duration_sec)
    | .[0:$n]
    | to_entries | map({
      rank: (.key + 1),
      step_id: .value.step_id,
      agent: .value.agent,
      model: (.value.model // "N/A"),
      category: .value.category,
      workflow: .value.workflow,
      duration_sec: .value.duration_sec,
      duration_min: ((.value.duration_sec / 60 * 10 | round) / 10),
      est_cost_usd: .value.est_cost_usd,
      total_tokens: (.value.est_input_tokens + .value.est_output_tokens)
    })
  '

  subheader "소요시간 분포"
  concat_logs | jq -s '
    map(select(.status=="END") | .duration_sec) |
    {
      count: length,
      min_sec: min,
      max_sec: max,
      avg_sec: ((add / length * 10 | round) / 10),
      median_sec: (sort | .[length/2 | floor]),
      p90_sec: (sort | .[(length * 0.9) | floor])
    }
  '
}

# ════════════════════════════════════════
# 3. 비용 분석 (Cost Analysis)
# ════════════════════════════════════════
cmd_cost() {
  header "비용 분석"

  subheader "파이프라인별 총 비용"
  concat_logs | jq -s '
    map(select(.status=="END"))
    | group_by(.workflow)
    | map({
      workflow: .[0].workflow,
      total_cost_usd: ((map(.est_cost_usd) | add) * 1000 | round | . / 1000),
      total_input_tokens: (map(.est_input_tokens) | add),
      total_output_tokens: (map(.est_output_tokens) | add),
      total_input_bytes: (map(.input_bytes) | add),
      total_output_bytes: (map(.output_bytes) | add),
      step_count: length
    }) | sort_by(-.total_cost_usd)
  '

  subheader "비용 TOP 5 스텝 (가장 비싼 작업)"
  concat_logs | jq -s '
    map(select(.status=="END"))
    | sort_by(-.est_cost_usd)
    | .[0:5]
    | map({step_id, agent, category, workflow, est_cost_usd,
          tokens: (.est_input_tokens + .est_output_tokens)})
  '
}

# ════════════════════════════════════════
# 4. 에이전트별 통계 (Agent Stats)
# ════════════════════════════════════════
cmd_agent() {
  header "에이전트별 통계"

  concat_logs | jq -s '
    map(select(.status=="END"))
    | group_by(.agent)
    | map({
      agent: .[0].agent,
      model: (.[0].model // "N/A"),
      category: .[0].category,
      runs: length,
      avg_duration_sec: ((map(.duration_sec) | add / length * 10 | round) / 10),
      total_duration_sec: (map(.duration_sec) | add),
      total_cost_usd: ((map(.est_cost_usd) | add) * 1000 | round | . / 1000),
      avg_input_tokens: ((map(.est_input_tokens) | add / length) | round),
      avg_output_tokens: ((map(.est_output_tokens) | add / length) | round)
    }) | sort_by(-.total_cost_usd)
  '
}

# ════════════════════════════════════════
# 5. 재시도/실패 분석 (Failure Analysis)
# ════════════════════════════════════════
cmd_failure() {
  header "재시도/실패 분석"

  local fail_count
  fail_count=$(concat_logs | jq -s 'map(select(.status=="FAIL" or .status=="RETRY")) | length')

  if [[ "$fail_count" == "0" ]]; then
    ok "실패/재시도 없음 — 모든 스텝 성공"
    return
  fi

  subheader "실패 이벤트"
  concat_logs | jq -s '
    map(select(.status=="FAIL"))
    | map({run_id, step_id, agent, error_message, ts})
  '

  subheader "재시도 이벤트"
  concat_logs | jq -s '
    map(select(.status=="RETRY"))
    | map({run_id, step_id, agent, retry, ts})
  '

  subheader "에이전트별 실패 빈도"
  concat_logs | jq -s '
    map(select(.status=="FAIL" or .status=="RETRY"))
    | group_by(.agent)
    | map({
      agent: .[0].agent,
      fail_count: (map(select(.status=="FAIL")) | length),
      retry_count: (map(select(.status=="RETRY")) | length),
      errors: [.[] | select(.status=="FAIL") | .error_message] | unique
    })
  '
}

# ════════════════════════════════════════
# 6. 병렬 실행 효율 (Parallel Efficiency)
# ════════════════════════════════════════
cmd_parallel() {
  header "병렬 실행 효율 분석"

  local para_count
  para_count=$(concat_logs | jq -s 'map(select(.status=="END" and .parallel_group != null)) | length')

  if [[ "$para_count" == "0" ]]; then
    warn "병렬 실행 기록 없음"
    return
  fi

  concat_logs | jq -s '
    map(select(.status=="END" and .parallel_group != null))
    | group_by(.parallel_group)
    | map({
      group: .[0].parallel_group,
      agents: [.[] | .agent],
      max_duration_sec: (map(.duration_sec) | max),
      total_if_sequential_sec: (map(.duration_sec) | add),
      saved_sec: ((map(.duration_sec) | add) - (map(.duration_sec) | max)),
      parallelism_gain_pct: (((1 - ((map(.duration_sec) | max) / (map(.duration_sec) | add))) * 100 * 10 | round) / 10),
      combined_cost_usd: ((map(.est_cost_usd) | add) * 1000 | round | . / 1000)
    })
  '
}

# ════════════════════════════════════════
# 7. 카테고리별 비용 (Category Cost)
# ════════════════════════════════════════
cmd_category() {
  header "LLM 카테고리별 비용 분석"

  concat_logs | jq -s '
    map(select(.status=="END"))
    | group_by(.category)
    | map({
      category: .[0].category,
      step_count: length,
      total_cost_usd: ((map(.est_cost_usd) | add) * 1000 | round | . / 1000),
      avg_cost_usd: ((map(.est_cost_usd) | add / length) * 1000 | round | . / 1000),
      total_duration_sec: (map(.duration_sec) | add),
      total_tokens: (map(.est_input_tokens + .est_output_tokens) | add),
      cost_per_minute: (((map(.est_cost_usd) | add) / ((map(.duration_sec) | add) / 60)) * 1000 | round | . / 1000)
    }) | sort_by(-.total_cost_usd)
  '
}

# ════════════════════════════════════════
# 8. 실행 타임라인 (Run Timeline)
# ════════════════════════════════════════
cmd_timeline() {
  local target_run="${1:-}"

  if [[ -z "$target_run" ]]; then
    header "실행 히스토리 (전체 run_id 목록)"
    concat_logs | jq -s '
      group_by(.run_id) | map({
        run_id: .[0].run_id,
        workflow: .[0].workflow,
        start: (map(.ts) | min),
        end_ts: (map(.ts) | max),
        events: length
      }) | sort_by(.start) | reverse
    '
    return
  fi

  header "실행 타임라인 — $target_run"
  concat_logs | jq -s --arg rid "$target_run" '
    map(select(.run_id == $rid))
    | sort_by(.ts)
    | map({
      ts: .ts,
      status: .status,
      step_id: .step_id,
      agent: .agent,
      model: (.model // "N/A"),
      category: .category,
      parallel_group: .parallel_group,
      duration_sec: (.duration_sec // null),
      est_cost_usd: (.est_cost_usd // null),
      decision: (.decision // null),
      error: (.error_message // null)
    })
  '
}

# ════════════════════════════════════════
# 9. 스키마 검증 (Schema Validation)
# ════════════════════════════════════════
cmd_validate() {
  header "JSONL 스키마 검증"

  local total_lines=0 valid_lines=0 errors=0
  
  while IFS= read -r -d '' f; do
    local fname
    fname=$(basename "$f")
    local line_count
    line_count=$(wc -l < "$f" | tr -d ' ')
    total_lines=$((total_lines + line_count))

    # JSON 유효성
    local json_errors
    json_errors=$(jq -c '.' "$f" 2>&1 | grep -c 'parse error' || true)
    if [[ "$json_errors" -gt 0 ]]; then
      fail "$fname: ${json_errors}개 JSON 파싱 에러"
      errors=$((errors + 1))
    fi

    # 필수 필드 검증 (공통 10필드)
    local missing_fields
    missing_fields=$(jq -c '
      ["run_id","ts","status","workflow","step_id","agent","category","model","action","parallel_group","retry"]
      - keys | select(length > 0)
    ' "$f" 2>/dev/null | head -5)
    if [[ -n "$missing_fields" ]]; then
      fail "$fname: 필수 필드 누락 — $missing_fields"
      errors=$((errors + 1))
    fi

    # END 이벤트 전용 필드 검증
    local end_missing
    end_missing=$(jq -c '
      select(.status=="END") |
      ["duration_sec","input_bytes","output_bytes","est_input_tokens","est_output_tokens","est_cost_usd"]
      - keys | select(length > 0)
    ' "$f" 2>/dev/null | head -5)
    if [[ -n "$end_missing" ]]; then
      fail "$fname: END 이벤트 필수 필드 누락 — $end_missing"
      errors=$((errors + 1))
    fi

    # run_id 일관성 검증
    local run_id_count
    run_id_count=$(jq -r '.run_id' "$f" | sort -u | wc -l | tr -d ' ')

    # START/END 쌍 검증
    local start_count end_count
    start_count=$(jq -s 'map(select(.status=="START")) | length' "$f")
    end_count=$(jq -s 'map(select(.status=="END")) | length' "$f")

    # 토큰 추정 정확성 검증 (bytes/3.3 ≈ tokens, ±2 허용)
    local token_mismatch
    token_mismatch=$(jq -c '
      select(.status=="END") |
      select(
        ((.input_bytes / 3.3 | round) - .est_input_tokens | fabs) > 2 or
        ((.output_bytes / 3.3 | round) - .est_output_tokens | fabs) > 2
      ) | {step_id, expected_in: (.input_bytes/3.3|round), got_in: .est_input_tokens,
           expected_out: (.output_bytes/3.3|round), got_out: .est_output_tokens}
    ' "$f" 2>/dev/null)
    if [[ -n "$token_mismatch" ]]; then
      warn "$fname: 토큰 추정 오차 (±2 초과)"
      echo "$token_mismatch"
    fi

    echo -e "${BOLD}${fname}${NC}: ${line_count}줄, run_id ${run_id_count}개, START=${start_count} END=${end_count}"

    if [[ "$start_count" != "$end_count" ]]; then
      local unmatched
      unmatched=$((start_count - end_count))
      if [[ "$unmatched" -gt 0 ]]; then
        warn "START ${unmatched}개가 END 없이 남아있음 (중단된 스텝?)"
      fi
    fi

    valid_lines=$((valid_lines + line_count))
  done < <(get_log_files)

  echo ""
  echo -e "${BOLD}검증 결과${NC}: 총 ${total_lines}줄, 유효 ${valid_lines}줄, 에러 ${errors}건"
  if [[ "$errors" -eq 0 ]]; then
    ok "모든 검증 통과"
  else
    fail "${errors}건의 검증 실패"
  fi
}

# ════════════════════════════════════════
# 10. 종합 리포트 (Markdown Report)
# ════════════════════════════════════════
cmd_report() {
  local report_date
  report_date=$(date '+%Y-%m-%d')
  local dashboard_dir="$PROJECT_ROOT/.agent/dashboard"
  mkdir -p "$dashboard_dir"
  local report_file="$dashboard_dir/analysis_report_${report_date}.md"

  {
    echo "# Agent Execution Log Analysis Report"
    echo ""
    echo "> 분석일: $report_date"
    echo "> 로그 디렉토리: .agent/logs/"
    echo "> 분석 도구: analyze_logs.sh (jq $(jq --version 2>&1))"
    echo ""
    echo "---"
    echo ""
    echo "## 1. 파이프라인 요약"
    echo ""
    echo '```json'
    concat_logs | jq -s '
      group_by(.run_id) | map({
        run_id: .[0].run_id,
        workflow: .[0].workflow,
        steps: (map(select(.status=="END")) | length),
        total_duration_min: ((map(select(.status=="END") | .duration_sec) | add) / 60 * 10 | round | . / 10),
        total_cost_usd: ((map(select(.status=="END") | .est_cost_usd) | add) * 1000 | round | . / 1000),
        total_tokens: (map(select(.status=="END") | .est_input_tokens + .est_output_tokens) | add),
        decision: (map(select(.status=="END" and .decision != null) | .decision) | last // "N/A")
      }) | sort_by(.run_id) | reverse
    '
    echo '```'
    echo ""
    echo "## 2. 보틀넥 TOP 5"
    echo ""
    echo '```json'
    concat_logs | jq -s '
      map(select(.status=="END")) | sort_by(-.duration_sec) | .[0:5]
      | map({step_id, agent, category, duration_min: ((.duration_sec/60*10|round)/10), est_cost_usd})
    '
    echo '```'
    echo ""
    echo "## 3. 카테고리별 비용"
    echo ""
    echo "| 카테고리 | 스텝 수 | 총 비용 (USD) | 총 토큰 | 분당 비용 |"
    echo "|----------|---------|---------------|---------|----------|"
    concat_logs | jq -sr '
      map(select(.status=="END")) | group_by(.category)
      | map(
        "| " + .[0].category +
        " | " + (length | tostring) +
        " | $" + ((map(.est_cost_usd)|add)*1000|round|./1000|tostring) +
        " | " + (map(.est_input_tokens+.est_output_tokens)|add|tostring) +
        " | $" + (((map(.est_cost_usd)|add)/((map(.duration_sec)|add)/60))*1000|round|./1000|tostring) +
        " |"
      ) | .[]
    '
    echo ""
    echo "## 4. 에이전트별 통계"
    echo ""
    echo "| 에이전트 | 모델 | 카테고리 | 실행 수 | 평균 소요(sec) | 총 비용 |"
    echo "|----------|------|----------|---------|---------------|---------|"
    concat_logs | jq -sr '
      map(select(.status=="END")) | group_by(.agent)
      | sort_by(-(map(.est_cost_usd)|add))
      | map(
        "| " + .[0].agent +
        " | " + (.[0].model // "N/A") +
        " | " + .[0].category +
        " | " + (length|tostring) +
        " | " + ((map(.duration_sec)|add/length*10|round)/10|tostring) +
        " | $" + ((map(.est_cost_usd)|add)*1000|round|./1000|tostring) +
        " |"
      ) | .[]
    '
    echo ""
    echo "## 5. 병렬 실행 효율"
    echo ""
    local para_data
    para_data=$(concat_logs | jq -s 'map(select(.status=="END" and .parallel_group != null)) | length')
    if [[ "$para_data" == "0" ]]; then
      echo "병렬 실행 기록 없음"
    else
      echo '```json'
      concat_logs | jq -s '
        map(select(.status=="END" and .parallel_group != null))
        | group_by(.parallel_group)
        | map({
          group: .[0].parallel_group,
          agents: [.[]|.agent],
          wall_clock_sec: (map(.duration_sec)|max),
          sequential_sec: (map(.duration_sec)|add),
          saved_sec: ((map(.duration_sec)|add)-(map(.duration_sec)|max)),
          efficiency_pct: (((1-((map(.duration_sec)|max)/(map(.duration_sec)|add)))*100*10|round)/10)
        })
      '
      echo '```'
    fi
    echo ""
    echo "## 6. 실패/재시도"
    echo ""
    local fail_n
    fail_n=$(concat_logs | jq -s 'map(select(.status=="FAIL" or .status=="RETRY")) | length')
    if [[ "$fail_n" == "0" ]]; then
      echo "✅ 실패/재시도 없음"
    else
      echo '```json'
      concat_logs | jq -s '
        map(select(.status=="FAIL" or .status=="RETRY"))
        | map({ts, status, step_id, agent, error_message: (.error_message // null), retry: (.retry // null)})
      '
      echo '```'
    fi
    echo ""
    echo "---"
    echo "*Generated by analyze_logs.sh*"
  } > "$report_file"

  ok "리포트 생성: $report_file"
  echo "  파일: $report_file"
}

# ════════════════════════════════════════
# 전체 분석 (All)
# ════════════════════════════════════════
cmd_all() {
  cmd_summary
  cmd_bottleneck 5
  cmd_cost
  cmd_agent
  cmd_category
  cmd_parallel
  cmd_failure
  cmd_validate
}

# ════════════════════════════════════════
# 메인
# ════════════════════════════════════════
main() {
  check_deps

  local cmd=${1:-all}
  shift 2>/dev/null || true

  case "$cmd" in
    summary)    cmd_summary ;;
    bottleneck) cmd_bottleneck "${1:-5}" ;;
    cost)       cmd_cost ;;
    agent)      cmd_agent ;;
    failure)    cmd_failure ;;
    parallel)   cmd_parallel ;;
    category)   cmd_category ;;
    timeline)   cmd_timeline "${1:-}" ;;
    validate)   cmd_validate ;;
    report)     cmd_report ;;
    all)        cmd_all ;;
    help|-h|--help)
      echo "Usage: $0 [command] [args]"
      echo ""
      echo "Commands:"
      echo "  summary            파이프라인 실행 요약"
      echo "  bottleneck [N]     보틀넥 TOP N (기본 5)"
      echo "  cost               비용 분석"
      echo "  agent              에이전트별 통계"
      echo "  failure            재시도/실패 분석"
      echo "  parallel           병렬 실행 효율"
      echo "  category           카테고리별 비용"
      echo "  timeline [run_id]  실행 타임라인"
      echo "  validate           스키마 검증"
      echo "  report             종합 리포트 (마크다운)"
      echo "  all                전체 분석 (기본)"
      echo "  help               이 도움말"
      ;;
    *)
      fail "알 수 없는 명령: $cmd"
      echo "$0 help 로 사용법을 확인하세요."
      exit 1
      ;;
  esac
}

main "$@"
