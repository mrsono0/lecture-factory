#!/bin/bash
# analyze_api_costs.sh - API 비용 추정 및 분석
# version: 1.0.0
# created: 2026-02-24

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"
load_config

LOG_DIR="${PROJECT_ROOT}/.agent/logs"
OUTPUT_DIR="${PROJECT_ROOT}/.agent/dashboard/analysis"
DATE_STR=$(get_current_date)
OUTPUT_FILE="${OUTPUT_DIR}/cost_estimate_${DATE_STR//-/}.md"

DAYS=7

usage() {
    cat << EOF
사용법: $(basename "$0") [옵션]

API 비용 추정 및 분석 스크립트

옵션:
  -l, --log-dir DIR     로그 디렉토리 경로
  -o, --output FILE     출력 파일 경로
  -d, --days N          분석 기간 (기본값: 7)
  -h, --help            도움말 출력
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--log-dir) LOG_DIR="$2"; shift 2 ;;
        -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
        -d|--days) DAYS="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "알 수 없는 옵션: $1"; usage ;;
    esac
done

log_info "API 비용 분석 시작... (${DAYS}일)"

LOG_FILES=$(find_recent_logs "$DAYS" "$LOG_DIR")

if [[ -z "$LOG_FILES" ]]; then
    log_warning "로그 파일을 찾을 수 없습니다"
    exit 0
fi

COST_DATA=$(concat_jsonl $LOG_FILES | filter_external_tool_events | jq -s '
    map(select(.status=="EXTERNAL_TOOL_END"))
    | group_by(.tool_name)
    | map({
        tool: .[0].tool_name,
        total_calls: length,
        total_input_bytes: (map(.tool_input_bytes) | add),
        total_output_bytes: (map(.tool_output_bytes) | add),
        total_input_tokens: ((map(.tool_input_bytes) | add) / 3.3),
        total_output_tokens: ((map(.tool_output_bytes) | add) / 3.3),
        est_input_cost_usd: (((map(.tool_input_bytes) | add) / 3.3) * 0.015 / 1000),
        est_output_cost_usd: (((map(.tool_output_bytes) | add) / 3.3) * 0.075 / 1000),
        total_duration: (map(.tool_duration_sec) | add)
    })
    | map({
        tool,
        total_calls,
        total_input_bytes,
        total_output_bytes,
        total_input_tokens,
        total_output_tokens,
        est_input_cost_usd,
        est_output_cost_usd,
        est_total_cost_usd: (.est_input_cost_usd + .est_output_cost_usd),
        total_duration
    })
    | sort_by(-.est_total_cost_usd)
')

{
    add_metadata "API 비용 추정" "외부 도구 호출 비용 추정 및 최적화 제안"
    
    echo "## 💰 비용 요약"
    echo ""
    
    TOTAL_COST=$(echo "$COST_DATA" | jq '[.[]|.est_total_cost_usd] | add')
    TOTAL_CALLS=$(echo "$COST_DATA" | jq '[.[]|.total_calls] | add')
    AVG_COST_PER_CALL=$(echo "scale=4; $TOTAL_COST / $TOTAL_CALLS" | bc)
    
    echo "- **추정 총 비용**: \$${TOTAL_COST} USD"
    echo "- **총 호출 횟수**: ${TOTAL_CALLS}회"
    echo "- **호출당 평균 비용**: \$${AVG_COST_PER_CALL} USD"
    echo "- **분석 기간**: 최근 ${DAYS}일"
    echo ""
    
    echo "## 🔧 도구별 비용 상세"
    echo ""
    
    print_md_table_header "도구" "호출" "입력 토큰" "출력 토큰" "입력 비용" "출력 비용" "총 비용"
    
    echo "$COST_DATA" | jq -c '.[]' | while read -r data; do
        tool=$(echo "$data" | jq -r '.tool')
        calls=$(echo "$data" | jq -r '.total_calls')
        in_tokens=$(echo "$data" | jq -r '.total_input_tokens | floor')
        out_tokens=$(echo "$data" | jq -r '.total_output_tokens | floor')
        in_cost=$(echo "$data" | jq -r '.est_input_cost_usd * 100 | floor / 100')
        out_cost=$(echo "$data" | jq -r '.est_output_cost_usd * 100 | floor / 100')
        total_cost=$(echo "$data" | jq -r '.est_total_cost_usd * 100 | floor / 100')
        
        print_md_table_row "$tool" "$calls" "$in_tokens" "$out_tokens" "\$${in_cost}" "\$${out_cost}" "\$${total_cost}"
    done
    
    echo ""
    echo "## 📊 비용 분포"
    echo ""
    
    echo "```"
    echo "$COST_DATA" | jq -r '.[] | "\(.tool): \(.est_total_cost_usd * 100 | floor / 100) USD (\((.est_total_cost_usd / '"$TOTAL_COST"' * 100) | floor)%)")'
    echo "```"
    
    echo ""
    echo "## 💡 최적화 제안"
    echo ""
    
    TOP_COST=$(echo "$COST_DATA" | jq -c '.[0]')
    if [[ $(echo "$TOP_COST" | jq '.est_total_cost_usd') != "0" ]]; then
        TOP_TOOL=$(echo "$TOP_COST" | jq -r '.tool')
        TOP_COST_VAL=$(echo "$TOP_COST" | jq -r '.est_total_cost_usd * 100 | floor / 100')
        TOP_PCT=$(echo "scale=1; $TOP_COST_VAL * 100 / $TOTAL_COST" | bc)
        
        echo "1. **${TOP_TOOL}** 도구가 전체 비용의 ${TOP_PCT}%를 차지합니다"
        echo "   - 캐싱 전략 검토: 반복 호출 결과 캐싱"
        echo "   - 배치 처리: 여러 요청을 한 번에 처리"
        echo ""
    fi
    
    HIGH_OUTPUT=$(echo "$COST_DATA" | jq -c 'map(select(.total_output_tokens > 100000)) | .[0] // empty')
    if [[ -n "$HIGH_OUTPUT" ]]; then
        echo "2. **출력 토큰 최적화**: 일부 도구에서 출력 크기가 큽니다"
        echo "   - 필요한 필드만 요청"
        echo "   - 응답 압축 또는 요약"
        echo ""
    fi
    
    echo "## 📝 참고 사항"
    echo ""
    echo "- 토큰 추정: bytes ÷ 3.3 (한국어+코드 혼합 기준)"
    echo "- 입력 비용: \$0.015 / 1K tokens (ultrabrain 기준)"
    echo "- 출력 비용: \$0.075 / 1K tokens (ultrabrain 기준)"
    echo "- 실제 비용은 제공업체 정책에 따라 변동될 수 있습니다"
    echo ""
    
    print_separator
    echo ""
    echo "*추정 생성일: $(get_current_datetime)*"
    
} > "$OUTPUT_FILE"

log_info "비용 분석 완료: $OUTPUT_FILE"
echo ""
echo "💰 총 추정 비용: \$${TOTAL_COST} USD"
echo "리포트: ${OUTPUT_FILE}"
