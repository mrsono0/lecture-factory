#!/bin/bash
# detect_anomalies.sh - 이상 징후 자동 감지 및 알림
# version: 1.0.0
# created: 2026-02-24

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"
load_config

LOG_DIR="${PROJECT_ROOT}/.agent/logs"
OUTPUT_DIR="${PROJECT_ROOT}/.agent/dashboard"
DATE_STR=$(get_current_date)
ALERTS_FILE="${OUTPUT_DIR}/alerts_${DATE_STR//-/}.md"

DAYS=1

usage() {
    cat << EOF
사용법: $(basename "$0") [옵션]

이상 징후 자동 감지 스크립트

옵션:
  -l, --log-dir DIR     로그 디렉토리 경로
  -o, --output FILE     출력 파일 경로
  -d, --days N          분석 기간 (기본값: 1)
  -h, --help            도움말 출력
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--log-dir) LOG_DIR="$2"; shift 2 ;;
        -o|--output) ALERTS_FILE="$2"; shift 2 ;;
        -d|--days) DAYS="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "알 수 없는 옵션: $1"; usage ;;
    esac
done

log_info "이상 징후 감지 시작... (${DAYS}일)"

LOG_FILES=$(find_recent_logs "$DAYS" "$LOG_DIR")

if [[ -z "$LOG_FILES" ]]; then
    log_warning "로그 파일을 찾을 수 없습니다"
    exit 0
fi

ALERT_COUNT=0

{
    add_metadata "이상 징후 감지 결과" "자동 감지된 경고 및 이상 징후 목록"
    
    echo "## 🚨 높은 실패율 (>${CONFIG_FAILURE_RATE_WARNING:-5}%)"
    echo ""
    
    HIGH_FAILURE=$(concat_jsonl $LOG_FILES | filter_external_tool_events | jq -s '
        map(select(.status=="EXTERNAL_TOOL_END"))
        | group_by(.tool_name)
        | map({
            tool: .[0].tool_name,
            total: length,
            success: (map(select(.tool_status=="success")) | length),
            failed: (map(select(.tool_status=="error")) | length),
            timeout: (map(select(.tool_status=="timeout")) | length),
            failure_rate: ((map(select(.tool_status!="success")) | length) / length * 100)
        })
        | map(select(.failure_rate > '${CONFIG_FAILURE_RATE_WARNING:-5}'))
        | sort_by(-.failure_rate)
    ')
    
    if [[ $(echo "$HIGH_FAILURE" | jq 'length') -gt 0 ]]; then
        print_md_table_header "도구" "총 호출" "성공" "실패" "타임아웃" "실패율" "상태"
        
        echo "$HIGH_FAILURE" | jq -c '.[]' | while read -r data; do
            tool=$(echo "$data" | jq -r '.tool')
            total=$(echo "$data" | jq -r '.total')
            success=$(echo "$data" | jq -r '.success')
            failed=$(echo "$data" | jq -r '.failed')
            timeout=$(echo "$data" | jq -r '.timeout')
            rate=$(echo "$data" | jq -r '.failure_rate | floor')
            
            if (( $(echo "$rate > ${CONFIG_FAILURE_RATE_CRITICAL:-15}" | bc -l) )); then
                status="🔴 CRITICAL"
            else
                status="🟡 WARNING"
            fi
            
            print_md_table_row "$tool" "$total" "$success" "$failed" "$timeout" "${rate}%" "$status"
            ((ALERT_COUNT++))
        done
    else
        echo "✅ 정상: 실패율 임계값 초과 없음"
    fi
    
    echo ""
    echo "## 🐌 느린 응답 (평균 >${CONFIG_AVG_DURATION_WARNING:-60}s)"
    echo ""
    
    SLOW_TOOLS=$(concat_jsonl $LOG_FILES | filter_external_tool_events | jq -s '
        map(select(.status=="EXTERNAL_TOOL_END"))
        | group_by(.tool_name)
        | map({
            tool: .[0].tool_name,
            avg_duration: (map(.tool_duration_sec) | add) / length,
            max_duration: (map(.tool_duration_sec) | max),
            p95_duration: (map(.tool_duration_sec) | sort | .[(length * 0.95 | floor)]),
            calls: length
        })
        | map(select(.avg_duration > '${CONFIG_AVG_DURATION_WARNING:-60}'))
        | sort_by(-.avg_duration)
    ')
    
    if [[ $(echo "$SLOW_TOOLS" | jq 'length') -gt 0 ]]; then
        print_md_table_header "도구" "평균(s)" "P95(s)" "최대(s)" "호출" "상태"
        
        echo "$SLOW_TOOLS" | jq -c '.[]' | while read -r data; do
            tool=$(echo "$data" | jq -r '.tool')
            avg=$(echo "$data" | jq -r '.avg_duration | floor')
            p95=$(echo "$data" | jq -r '.p95_duration | floor')
            max=$(echo "$data" | jq -r '.max_duration | floor')
            calls=$(echo "$data" | jq -r '.calls')
            
            if (( avg > ${CONFIG_AVG_DURATION_CRITICAL:-120} )); then
                status="🔴 CRITICAL"
            else
                status="🟡 WARNING"
            fi
            
            print_md_table_row "$tool" "$avg" "$p95" "$max" "$calls" "$status"
            ((ALERT_COUNT++))
        done
    else
        echo "✅ 정상: 응답시간 임계값 초과 없음"
    fi
    
    echo ""
    echo "## 📊 성능 이상치 (평균의 2배 이상 소요)"
    echo ""
    
    OUTLIERS=$(concat_jsonl $LOG_FILES | filter_external_tool_events | jq -s '
        map(select(.status=="EXTERNAL_TOOL_END"))
        | group_by(.tool_name)
        | map({
            tool: .[0].tool_name,
            avg: (map(.tool_duration_sec) | add) / length,
            outliers: map(select(.tool_duration_sec > ((map(.tool_duration_sec) | add) / length * 2))),
            calls: length
        })
        | map({tool, avg_duration: .avg, outlier_count: (.outliers | length), calls})
        | map(select(.outlier_count > 0))
        | sort_by(-.outlier_count)
    ')
    
    if [[ $(echo "$OUTLIERS" | jq 'length') -gt 0 ]]; then
        print_md_table_header "도구" "평균(s)" "이상치 수" "비율(%)"
        
        echo "$OUTLIERS" | jq -c '.[]' | while read -r data; do
            tool=$(echo "$data" | jq -r '.tool')
            avg=$(echo "$data" | jq -r '.avg_duration | floor')
            count=$(echo "$data" | jq -r '.outlier_count')
            calls=$(echo "$data" | jq -r '.calls')
            pct=$(echo "scale=1; $count * 100 / $calls" | bc)
            
            print_md_table_row "$tool" "$avg" "$count" "$pct%"
            ((ALERT_COUNT++))
        done
    else
        echo "✅ 정상: 성능 이상치 없음"
    fi
    
    echo ""
    echo "## 📝 요약"
    echo ""
    echo "- **총 경고 수**: ${ALERT_COUNT}개"
    echo "- **분석 기간**: 최근 ${DAYS}일"
    echo "- **분석 시간**: $(get_current_datetime)"
    echo ""
    
    if [[ $ALERT_COUNT -eq 0 ]]; then
        echo "✅ 모든 시스템 정상 작동 중"
    else
        echo "⚠️ ${ALERT_COUNT}개 항목에 대한 조치가 필요합니다"
    fi
    
    echo ""
    print_separator
    echo ""
    echo "*자동 생성됨: $(get_current_datetime)*"
    
} > "$ALERTS_FILE"

log_info "이상 감지 완료: ${ALERTS_FILE} (${ALERT_COUNT}개 경고)"

if [[ $ALERT_COUNT -gt 0 ]]; then
    echo ""
    echo "⚠️ ${ALERT_COUNT}개 경고가 감지되었습니다"
    echo "자세한 내용: ${ALERTS_FILE}"
    exit 1
fi
