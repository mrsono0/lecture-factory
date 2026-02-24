#!/bin/bash
# analyze_external_tools.sh - 외부 도구별 사용량 및 성능 분석
# version: 1.0.0
# created: 2026-02-24

set -euo pipefail

# 스크립트 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# 기본 설정
LOG_DIR="${PROJECT_ROOT}/.agent/logs"
OUTPUT_DIR="${PROJECT_ROOT}/.agent/dashboard/analysis"
DATE_STR=$(get_current_date)
OUTPUT_FILE="${OUTPUT_DIR}/tool_usage_${DATE_STR//-/}.md"

# 사용법
usage() {
    cat << EOF
사용법: $(basename "$0") [옵션]

외부 도구별 사용량 및 성능 분석 스크립트

옵션:
  -l, --log-dir DIR     로그 디렉토리 경로 (기본값: ${LOG_DIR})
  -o, --output FILE     출력 파일 경로 (기본값: ${OUTPUT_FILE})
  -d, --days N          최근 N일 로그만 분석 (기본값: 7)
  -h, --help            도움말 출력

예시:
  $(basename "$0")
  $(basename "$0") -d 30 -o custom_analysis.md
EOF
    exit 0
}

# 인자 파싱
DAYS=7
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--log-dir) LOG_DIR="$2"; shift 2 ;;
        -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
        -d|--days) DAYS="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "알 수 없는 옵션: $1"; usage ;;
    esac
done

# 로그 파일 찾기
log_info "로그 파일 검색 중... (${DAYS}일)"
LOG_FILES=$(find_recent_logs "$DAYS" "$LOG_DIR")

if [[ -z "$LOG_FILES" ]]; then
    log_error "로그 파일을 찾을 수 없습니다: ${LOG_DIR}"
    exit 1
fi

log_info "$(echo "$LOG_FILES" | wc -l)개 로그 파일 발견"

# 분석 시작
log_info "외부 도구 사용량 분석 시작..."

# 도구별 사용량 및 성공률 분석
TOOL_USAGE=$(concat_jsonl $LOG_FILES | filter_external_tool_events | jq -s '
    map(select(.status=="EXTERNAL_TOOL_END"))
    | group_by(.tool_name)
    | map({
        tool: .[0].tool_name,
        calls: length,
        success: (map(select(.tool_status=="success")) | length),
        failed: (map(select(.tool_status=="error")) | length),
        timeout: (map(select(.tool_status=="timeout")) | length),
        success_rate: ((map(select(.tool_status=="success")) | length) / length * 100),
        failure_rate: ((map(select(.tool_status=="error")) | length) / length * 100),
        timeout_rate: ((map(select(.tool_status=="timeout")) | length) / length * 100),
        total_duration: (map(.tool_duration_sec) | add),
        avg_duration: (map(.tool_duration_sec) | add) / length,
        p95_duration: (map(.tool_duration_sec) | sort | .[(length * 0.95 | floor)]),
        max_duration: (map(.tool_duration_sec) | max),
        total_input_bytes: (map(.tool_input_bytes) | add),
        total_output_bytes: (map(.tool_output_bytes) | add)
    })
    | sort_by(-.calls)
')

# 워크플로우별 분석
WORKFLOW_USAGE=$(concat_jsonl $LOG_FILES | filter_external_tool_events | jq -s '
    map(select(.status=="EXTERNAL_TOOL_END"))
    | group_by(.workflow)
    | map({
        workflow: .[0].workflow,
        total_calls: length,
        tools: (group_by(.tool_name) | map({tool: .[0].tool_name, calls: length}))
    })
    | sort_by(-.total_calls)
')

# 시간대별 패턴
HOURLY_PATTERN=$(concat_jsonl $LOG_FILES | filter_external_tool_events | jq -s '
    map(select(.status=="EXTERNAL_TOOL_END"))
    | group_by(.ts | split("T")[1] | split(":")[0])
    | map({
        hour: .[0].ts | split("T")[1] | split(":")[0],
        calls: length,
        avg_duration: (map(.tool_duration_sec) | add) / length
    })
    | sort_by(.hour)
')

# 결과 문서 생성
{
    add_metadata "외부 도구 사용량 분석" "도구별 호출 빈도, 성공률, 성능 메트릭 분석"
    
    echo "## 📊 요약"
    echo ""
    
    TOTAL_CALLS=$(echo "$TOOL_USAGE" | jq '[.[]|.calls] | add')
    TOTAL_SUCCESS=$(echo "$TOOL_USAGE" | jq '[.[]|.success] | add')
    TOTAL_FAILED=$(echo "$TOOL_USAGE" | jq '[.[]|.failed] | add')
    OVERALL_SUCCESS_RATE=$(echo "scale=2; $TOTAL_SUCCESS / $TOTAL_CALLS * 100" | bc)
    
    echo "- **총 호출 횟수**: ${TOTAL_CALLS}회"
    echo "- **성공**: ${TOTAL_SUCCESS}회 (${OVERALL_SUCCESS_RATE}%)"
    echo "- **실패**: ${TOTAL_FAILED}회"
    echo "- **분석 기간**: 최근 ${DAYS}일"
    echo "- **분석 대상**: $(echo "$LOG_FILES" | wc -l)개 로그 파일"
    echo ""
    
    echo "## 🔧 도구별 사용량"
    echo ""
    
    print_md_table_header "도구" "호출" "성공" "실패" "타임아웃" "성공률" "평균(s)" "P95(s)" "최대(s)"
    
    echo "$TOOL_USAGE" | jq -c '.[]' | while read -r tool_data; do
        tool=$(echo "$tool_data" | jq -r '.tool')
        calls=$(echo "$tool_data" | jq -r '.calls')
        success=$(echo "$tool_data" | jq -r '.success')
        failed=$(echo "$tool_data" | jq -r '.failed')
        timeout=$(echo "$tool_data" | jq -r '.timeout')
        success_rate=$(echo "$tool_data" | jq -r '.success_rate | tonumber | floor')
        avg_duration=$(echo "$tool_data" | jq -r '.avg_duration | tonumber * 10 | floor / 10')
        p95_duration=$(echo "$tool_data" | jq -r '.p95_duration | tonumber * 10 | floor / 10')
        max_duration=$(echo "$tool_data" | jq -r '.max_duration | tonumber * 10 | floor / 10')
        
        print_md_table_row "$tool" "$calls" "$success" "$failed" "$timeout" "${success_rate}%" "$avg_duration" "$p95_duration" "$max_duration"
    done
    
    echo ""
    echo "## 📁 워크플로우별 사용량"
    echo ""
    
    print_md_table_header "워크플로우" "총 호출" "사용 도구"
    
    echo "$WORKFLOW_USAGE" | jq -c '.[]' | while read -r wf_data; do
        workflow=$(echo "$wf_data" | jq -r '.workflow')
        calls=$(echo "$wf_data" | jq -r '.total_calls')
        tools=$(echo "$wf_data" | jq -r '[.tools[].tool] | join(", ")')
        
        print_md_table_row "$workflow" "$calls" "$tools"
    done
    
    echo ""
    echo "## ⏰ 시간대별 호출 패턴"
    echo ""
    
    print_md_table_header "시간대" "호출 횟수" "평균 응답(s)"
    
    echo "$HOURLY_PATTERN" | jq -c '.[]' | while read -r hour_data; do
        hour=$(echo "$hour_data" | jq -r '.hour')
        calls=$(echo "$hour_data" | jq -r '.calls')
        avg_duration=$(echo "$hour_data" | jq -r '.avg_duration | tonumber * 10 | floor / 10')
        
        print_md_table_row "${hour}:00~${hour}:59" "$calls" "$avg_duration"
    done
    
    echo ""
    print_separator
    echo ""
    echo "*분석 완료: $(get_current_datetime)*"
    
} > "$OUTPUT_FILE"

log_info "분석 완료: $OUTPUT_FILE"

# 간단한 요약 출력
echo ""
echo "📊 분석 결과 요약"
echo "=================="
echo "총 호출: ${TOTAL_CALLS}회 | 성공: ${OVERALL_SUCCESS_RATE}%"
echo "리포트: ${OUTPUT_FILE}"
echo ""
