#!/bin/bash
# 공통 함수 라이브러리
# Common Functions Library for Log Analysis
# version: 1.0.0
# created: 2026-02-24

# ============================================================
# 설정 로드
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 설정 파일 로드
load_config() {
    local config_file="${SCRIPT_DIR}/thresholds.conf"
    if [[ -f "$config_file" ]]; then
        # 설정 파일 파싱
        while IFS='=' read -r key value; do
            # 주석 및 빈 줄 제외
            [[ "$key" =~ ^[[:space:]]*# ]] && continue
            [[ -z "$key" ]] && continue
            
            # 키 정제
            key=$(echo "$key" | tr -d '[:space:]')
            value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            
            # 환경 변수로 설정
            export "CONFIG_${key^^}=$value"
        done < "$config_file"
    else
        echo "경고: 설정 파일을 찾을 수 없습니다: $config_file" >&2
    fi
}

# jq 쿼리 로드
load_jq_query() {
    local query_name="$1"
    local query_file="${SCRIPT_DIR}/jq_queries.json"
    
    if [[ -f "$query_file" ]]; then
        jq -r ".queries.${query_name}.query // empty" "$query_file"
    else
        echo "경고: jq 쿼리 파일을 찾을 수 없습니다: $query_file" >&2
        return 1
    fi
}

# ============================================================
# 로그 파일 처리
# ============================================================

# 로그 파일 찾기
find_log_files() {
    local log_dir="${1:-${PROJECT_ROOT}/.agent/logs}"
    local pattern="${2:-*_EXTERNAL_TOOL.jsonl}"
    
    find "$log_dir" -name "$pattern" -type f 2>/dev/null | sort
}

# 최근 N일 로그 파일 찾기
find_recent_logs() {
    local days="${1:-7}"
    local log_dir="${2:-${PROJECT_ROOT}/.agent/logs}"
    
    find "$log_dir" -name "*.jsonl" -type f -mtime -$days 2>/dev/null | sort
}

# 로그 파일 유효성 검사
validate_log_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "오류: 파일을 찾을 수 없습니다: $file" >&2
        return 1
    fi
    
    if [[ ! -r "$file" ]]; then
        echo "오류: 파일을 읽을 수 없습니다: $file" >&2
        return 1
    fi
    
    # JSONL 형식 검사 (첫 5줄)
    local invalid_lines=$(head -n 5 "$file" | jq -c '.' 2>&1 | grep -c "parse error" || true)
    if [[ $invalid_lines -gt 0 ]]; then
        echo "경고: JSONL 형식 오류가 감지되었습니다: $file" >&2
    fi
    
    return 0
}

# ============================================================
# 날짜/시간 유틸리티
# ============================================================

# 현재 날짜 문자열
get_current_date() {
    date "+%Y-%m-%d"
}

# 현재 시간 문자열
get_current_datetime() {
    date "+%Y-%m-%d %H:%M:%S"
}

# 날짜 패턴 치환
replace_date_pattern() {
    local pattern="$1"
    local date_str="${2:-$(get_current_date)}"
    
    echo "$pattern" | sed "s/YYYYMMDD/${date_str//-/}/g; s/YYYY-MM-DD/$date_str/g"
}

# ============================================================
# 출력 포맷팅
# ============================================================

# 마크다운 테이블 헤더 출력
print_md_table_header() {
    local columns=("$@")
    local header="| "
    local separator="|"
    
    for col in "${columns[@]}"; do
        header+="$col | "
        separator+="---|"
    done
    
    echo "$header"
    echo "$separator"
}

# 마크다운 테이블 행 출력
print_md_table_row() {
    local values=("$@")
    local row="|"
    
    for val in "${values[@]}"; do
        row+=" $val |"
    done
    
    echo "$row"
}

# 구분선 출력
print_separator() {
    echo "---"
}

# ============================================================
# JSONL 처리
# ============================================================

# JSONL 파일 합치기 (스트리밍)
concat_jsonl() {
    local files=("$@")
    
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            cat "$file"
        fi
    done
}

# JSONL 라인 수 세기
count_jsonl_lines() {
    local file="$1"
    
    if [[ -f "$file" ]]; then
        wc -l < "$file"
    else
        echo 0
    fi
}

# EXTERNAL_TOOL 이벤트만 필터링
filter_external_tool_events() {
    jq 'select(.status | startswith("EXTERNAL_TOOL"))'
}

# ============================================================
# 분석 결과 처리
# ============================================================

# 결과 저장
save_result() {
    local content="$1"
    local output_file="$2"
    
    # 출력 디렉토리 생성
    local output_dir=$(dirname "$output_file")
    mkdir -p "$output_dir"
    
    # 결과 저장
    echo "$content" > "$output_file"
    echo "결과 저장됨: $output_file"
}

# 결과에 메타데이터 추가
add_metadata() {
    local title="$1"
    local description="$2"
    
    cat << EOF
# $title

> **생성일**: $(get_current_datetime)  
> **분석 도구**: Lecture Factory Log Analysis  
> **버전**: 1.0.0

$description

---

EOF
}

# ============================================================
# 임계값 체크
# ============================================================

# 실패율 체크
check_failure_rate() {
    local rate="$1"
    local warning_threshold="${CONFIG_FAILURE_RATE_WARNING:-5.0}"
    local critical_threshold="${CONFIG_FAILURE_RATE_CRITICAL:-15.0}"
    
    if (( $(echo "$rate > $critical_threshold" | bc -l) )); then
        echo "CRITICAL"
    elif (( $(echo "$rate > $warning_threshold" | bc -l) )); then
        echo "WARNING"
    else
        echo "OK"
    fi
}

# 응답시간 체크
check_response_time() {
    local duration="$1"
    local warning_threshold="${CONFIG_AVG_DURATION_WARNING:-60}"
    local critical_threshold="${CONFIG_AVG_DURATION_CRITICAL:-120}"
    
    if (( $(echo "$duration > $critical_threshold" | bc -l) )); then
        echo "CRITICAL"
    elif (( $(echo "$duration > $warning_threshold" | bc -l) )); then
        echo "WARNING"
    else
        echo "OK"
    fi
}

# ============================================================
# 비용 계산
# ============================================================

# 토큰 수 계산
calculate_tokens() {
    local bytes="$1"
    local bytes_per_token="${CONFIG_BYTES_PER_TOKEN:-3.3}"
    
    echo "scale=0; $bytes / $bytes_per_token" | bc
}

# 비용 계산 (USD)
calculate_cost() {
    local input_tokens="$1"
    local output_tokens="$2"
    local input_price="${CONFIG_INPUT_TOKEN_PRICE:-0.015}"
    local output_price="${CONFIG_OUTPUT_TOKEN_PRICE:-0.075}"
    
    local input_cost=$(echo "scale=6; $input_tokens * $input_price / 1000" | bc)
    local output_cost=$(echo "scale=6; $output_tokens * $output_price / 1000" | bc)
    
    echo "scale=6; $input_cost + $output_cost" | bc
}

# ============================================================
# 에러 핸들링
# ============================================================

# 에러 로깅
log_error() {
    local message="$1"
    local timestamp=$(get_current_datetime)
    
    echo "[ERROR] $timestamp - $message" >&2
}

# 경고 로깅
log_warning() {
    local message="$1"
    local timestamp=$(get_current_datetime)
    
    echo "[WARN] $timestamp - $message" >&2
}

# 정보 로깅
log_info() {
    local message="$1"
    local timestamp=$(get_current_datetime)
    
    echo "[INFO] $timestamp - $message"
}

# ============================================================
# 메인 실행
# ============================================================

# 설정 로드 (소스로 사용될 때는 실행하지 않음)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 직접 실행 시 도움말 출력
    cat << 'EOF'
공통 함수 라이브러리

사용법: source common.sh

제공 함수:
  - load_config()                    : 설정 파일 로드
  - load_jq_query(query_name)        : jq 쿼리 로드
  - find_log_files([dir] [pattern])  : 로그 파일 찾기
  - find_recent_logs([days])         : 최근 N일 로그 찾기
  - validate_log_file(file)          : 로그 파일 유효성 검사
  - get_current_date()               : 현재 날짜
  - get_current_datetime()           : 현재 날짜/시간
  - print_md_table_header(...)       : 마크다운 테이블 헤더
  - print_md_table_row(...)          : 마크다운 테이블 행
  - filter_external_tool_events()    : EXTERNAL_TOOL 이벤트 필터
  - save_result(content, file)       : 결과 저장
  - add_metadata(title, desc)        : 메타데이터 추가
  - check_failure_rate(rate)         : 실패율 체크
  - check_response_time(duration)    : 응답시간 체크
  - calculate_tokens(bytes)          : 토큰 수 계산
  - calculate_cost(in_tokens, out_tokens) : 비용 계산
  - log_error/warning/info(message)  : 로깅 함수
EOF
fi
