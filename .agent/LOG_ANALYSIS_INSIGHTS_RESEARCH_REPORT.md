# 로그 분석 스크립트 인사이트 도출 검토 보고서

> **작성일**: 2026-02-24  
> **리서치 범위**: Log Analysis Best Practices, Usage Frequency Metrics, Failure Pattern Detection, jq Queries  
> **상태**: ✅ 검토 완료

---

## 1. 리서치 개요

인터넷 리서치를 통해 **로그 데이터에서 인사이트를 도출하는 체계적인 방법론**을 조사했습니다. 주요 초점:
- 사용 빈도(Usage Frequency) 분석
- 실패 패턴(Failure Pattern) 감지
- 성능 메트릭(Performance Metrics) 추출
- 이상 징후(Anomaly Detection) 탐지

---

## 2. 핵심 발견: 인사이트 도출 4대 카테고리

### 2.1 사용량/빈도 기반 인사이트 (Usage Analysis)

**참고 자료**: Chronosphere "How Usage Analysis helps teams optimize log data" (2025)

| 인사이트 유형 | 설명 | 비즈니스 가치 |
|-------------|------|--------------|
| **도구별 호출 빈도** | 어떤 외부 도구가 가장 많이 사용되는지 | 비용 최적화, 리소스 할당 |
| **시간대별 사용 패턴** | 피크/오프피크 시간대 식별 | 용량 계획, 스케줄링 최적화 |
| **워크플로우별 사용량** | 파이프라인 간 사용량 비교 | 병목 지점 식별 |
| **사용자/에이전트별 패턴** | 특정 에이전트의 과도한 사용 탐지 | 이상 징후 감지 |

**jq 쿼리 예시**:
```bash
# 도구별 총 호출 횟수 (빈도 분석)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({tool: .[0].tool_name, total_calls: length, percentage: 0})
  | sort_by(-.total_calls)
  | . as $tools | $tools | 
    map(.percentage = (.total_calls / ($tools | map(.total_calls) | add) * 100))
'

# 시간대별 호출 패턴 (시간대 분석)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.ts | split("T")[1] | split(":")[0])  # 시간대 추출
  | map({hour: .[0].ts | split("T")[1] | split(":")[0], calls: length})
  | sort_by(.hour)
'
```

---

### 2.2 실패/에러 패턴 인사이트 (Failure Analysis)

**참고 자료**: 
- "Anomaly Detection in Log Data: A Comparative Study" (IFIP CNSM 2025)
- "A Taxonomy of Anomalies in Log Data" (IEEE 2021)
- "An Empirical Investigation of Practical Log Anomaly Detection" (Tsinghua University 2021)

| 인사이트 유형 | 설명 | jq 활용 |
|-------------|------|--------|
| **실패율(Failure Rate)** | 도구별 실패 비율 계산 | `select(.tool_status=="error")` |
| **타임아웃 패턴** | 타임아웃 발생 빈도/시간대 | `select(.tool_status=="timeout")` |
| **에러 유형 분류** | 재시도 가능 vs 불가능 에러 | `.tool_error` 그룹화 |
| **연속 실패 감지** | 특정 기간 내 연속 실패 | 시간 윈도우 분석 |

**jq 쿼리 예시**:
```bash
# 실패율 계산 (경고 임계값: >5%)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({
      tool: .[0].tool_name,
      total: length,
      success: map(select(.tool_status=="success")) | length,
      failed: map(select(.tool_status=="error")) | length,
      timeout: map(select(.tool_status=="timeout")) | length,
      failure_rate: ((map(select(.tool_status!="success")) | length) / length * 100)
    })
  | sort_by(-.failure_rate)
  | map(select(.failure_rate > 5))  # 임계값 초과만 표시
'

# 에러 메시지 패턴 분석 (Top 10)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END" and .tool_status=="error" and .tool_error!=null))
  | group_by(.tool_error)
  | map({error_message: .[0].tool_error, count: length})
  | sort_by(-.count)
  | .[0:10]
'

# 재시도 패턴 분석 (효율성 평가)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.run_id, .step_id)
  | map({
      run_id: .[0].run_id,
      step_id: .[0].step_id,
      total_attempts: length,
      success_after_retry: (map(.tool_status) | index("success")) as $idx | if $idx > 0 then true else false end,
      final_status: .[-1].tool_status
    })
  | map(select(.total_attempts > 1))  # 재시도 발생한 경우만
'
```

---

### 2.3 성능/소요시간 인사이트 (Performance Analysis)

**참고 자료**: 
- "Insights into KPI-based performance anomaly detection in database systems" (Expert Systems 2025)
- Azure Well-Architected Framework - Log Analytics

| 인사이트 유형 | 설명 | 비즈니스 가치 |
|-------------|------|--------------|
| **평균/중간값/최대 응답 시간** | 도구별 성능 지표 | SLA 관리, 성능 최적화 |
| **성능 저하 감지** | 평균 대비 현저히 느린 호출 | early warning |
| **병목 도구 식별** | 전체 시간 대비 차지 비율 높은 도구 | 최적화 우선순위 |
| **시간별 성능 추이** | 특정 시간대 성능 저하 | 용량 계획 |

**jq 쿼리 예시**:
```bash
# 성능 통계 (평균/중간값/최대/표준편차)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({
      tool: .[0].tool_name,
      avg_duration: (map(.tool_duration_sec) | add) / length,
      median_duration: (map(.tool_duration_sec) | sort | if length % 2 == 0 then 
        (.[length/2 - 1] + .[length/2]) / 2 else .[(length-1)/2] end),
      max_duration: (map(.tool_duration_sec) | max),
      min_duration: (map(.tool_duration_sec) | min),
      total_calls: length,
      p95: (map(.tool_duration_sec) | sort | .[(length * 0.95 | floor)]),
      p99: (map(.tool_duration_sec) | sort | .[(length * 0.99 | floor)])
    })
  | sort_by(-.avg_duration)
'

# 성능 이상치 탐지 (평균의 2배 이상 소요된 호출)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name) as $by_tool
  | $by_tool | map({
      tool: .[0].tool_name,
      avg: (map(.tool_duration_sec) | add) / length,
      outliers: map(select(.tool_duration_sec > ((map(.tool_duration_sec) | add) / length * 2)))
    })
  | map({tool, avg_duration: .avg, outlier_count: (.outliers | length), outlier_rate: ((.outliers | length) / (. | length) * 100)})
'

# 누적 소요시간 기준 병목 도구 식별 (Pareto 분석)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({tool: .[0].tool_name, total_duration: (map(.tool_duration_sec) | add), calls: length})
  | sort_by(-.total_duration)
  | . as $sorted
  | $sorted | to_entries | map({
      tool: .value.tool,
      total_duration: .value.total_duration,
      percentage: (.value.total_duration / ($sorted | map(.total_duration) | add) * 100),
      cumulative_percentage: (($sorted[0:.key+1] | map(.total_duration) | add) / ($sorted | map(.total_duration) | add) * 100)
    })
'
```

---

### 2.4 이상 징후/트렌드 인사이트 (Anomaly & Trend Analysis)

**참고 자료**:
- "Data Anomaly Detection at Scale: Best Practices" (Eyer.ai 2024)
- "Anomaly Detection Algorithms for Real-Time Log Data Analysis at Scale" (IEEE Access 2025)
- AWS CloudWatch Logs Anomaly Detection

| 인사이트 유형 | 설명 | 알고리즘/기법 |
|-------------|------|-------------|
| **Sudden Spike** | 평소 대비 갑작스러운 호출 증가 | Z-score, 3-sigma rule |
| **Seasonality Change** | 주기적 패턴의 변화 | Rolling average 비교 |
| **Drift Detection** | 서서히 변화하는 성능 저하 | CUSUM, EWMA |
| **Correlated Failures** | 여러 도구 동시 실패 | 시간 윈도우 내 집계 |

**jq 쿼리 예시**:
```bash
# 일별 호출량 추이 (트렌드 분석)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.ts | split("T")[0])  # 날짜별
  | map({date: .[0].ts | split("T")[0], total_calls: length, error_count: (map(select(.tool_status=="error")) | length)})
  | sort_by(.date)
'

# Z-score 기반 이상치 탐지 (일별 호출량 기준)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.ts | split("T")[0])
  | map({date: .[0].ts | split("T")[0], count: length})
  | sort_by(.date)
  | . as $daily
  | ($daily | map(.count) | add) / ($daily | length) as $mean
  | ($daily | map(.count) | map(pow(. - $mean; 2)) | add / ($daily | length) | sqrt) as $std
  | $daily | map({
      date, 
      count, 
      z_score: ((.count - $mean) / $std),
      is_anomaly: ((.count - $mean) / $std) > 3 or ((.count - $mean) / $std) < -3
    })
'

# 연속적인 성능 저하 감지 (Sliding Window)
cat .agent/logs/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END" and .tool_name=="gemini-api"))
  | group_by(.ts | split("T")[0])
  | map({date: .[0].ts | split("T")[0], avg_duration: (map(.tool_duration_sec) | add) / length})
  | sort_by(.date)
  | . as $trend
  | $trend | keys[] as $i | $trend[$i] | select($i >= 2) | {
      date,
      avg_duration,
      prev_avg: ($trend[$i-1].avg_duration),
      change_pct: ((.avg_duration - $trend[$i-1].avg_duration) / $trend[$i-1].avg_duration * 100),
      trend_3day: ((.avg_duration - $trend[$i-2].avg_duration) / $trend[$i-2].avg_duration * 100)
    }
  | select(.trend_3day > 20)  # 3일 연속 20% 이상 증가
'
```

---

## 3. 추천 분석 스크립트 구조

리서치 결과를 바탕으로 다음과 같은 로그 분석 스크립트 구조를 권장합니다:

### 3.1 스크립트 구성

```
.agent/scripts/
├── analyze_logs.sh              # 메인 분석 스크립트
├── analyze_external_tools.sh    # 외부 도구 상세 분석
├── analyze_api_costs.sh         # API 비용 추정
├── detect_anomalies.sh          # 이상 징후 자동 감지
├── generate_report.sh           # 리포트 생성
└── lib/
    ├── jq_queries.json          # 재사용 가능한 jq 쿼리 라이브러리
    └── thresholds.conf          # 임계값 설정
```

### 3.2 핵심 분석 카테고리별 스크립트

#### `analyze_external_tools.sh` (사용량 분석)
```bash
#!/bin/bash
# 외부 도구 사용량 및 성능 분석

LOG_DIR=".agent/logs"
OUTPUT_DIR=".agent/dashboard/analysis"

# 1. 도구별 호출 빈도
echo "## 외부 도구 호출 빈도" > $OUTPUT_DIR/tool_usage.md
cat $LOG_DIR/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({
      tool: .[0].tool_name,
      calls: length,
      success_rate: (map(select(.tool_status=="success")) | length) / length * 100,
      total_duration: (map(.tool_duration_sec) | add),
      total_input_bytes: (map(.tool_input_bytes) | add),
      total_output_bytes: (map(.tool_output_bytes) | add)
    })
  | sort_by(-.calls)
' >> $OUTPUT_DIR/tool_usage.md
```

#### `detect_anomalies.sh` (이상 감지)
```bash
#!/bin/bash
# 이상 징후 자동 감지 및 알림

LOG_DIR=".agent/logs"
ALERT_THRESHOLD_FAILURE=5      # 5% 실패율 임계값
ALERT_THRESHOLD_TIMEOUT=10     # 10% 타임아웃 임계값
ALERT_THRESHOLD_DURATION=60    # 60초 응답시간 임계값

echo "## 이상 징후 감지 결과 ($(date))" > .agent/dashboard/alerts.md

# 1. 높은 실패율 도구
echo "### 🚨 높은 실패율 (> $ALERT_THRESHOLD_FAILURE%)" >> .agent/dashboard/alerts.md
cat $LOG_DIR/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({
      tool: .[0].tool_name,
      failure_rate: ((map(select(.tool_status!="success")) | length) / length * 100)
    })
  | map(select(.failure_rate > '$ALERT_THRESHOLD_FAILURE'))
  | sort_by(-.failure_rate)
' >> .agent/dashboard/alerts.md

# 2. 느린 응답 도구
echo "### 🐌 느린 응답시간 (평균 > ${ALERT_THRESHOLD_DURATION}s)" >> .agent/dashboard/alerts.md
cat $LOG_DIR/*.jsonl | jq -s '
  map(select(.status=="EXTERNAL_TOOL_END"))
  | group_by(.tool_name)
  | map({
      tool: .[0].tool_name,
      avg_duration: (map(.tool_duration_sec) | add) / length,
      max_duration: (map(.tool_duration_sec) | max)
    })
  | map(select(.avg_duration > '$ALERT_THRESHOLD_DURATION'))
  | sort_by(-.avg_duration)
' >> .agent/dashboard/alerts.md
```

---

## 4. 비즈니스 인사이트 요약

### 4.1 비용 최적화 인사이트

| 메트릭 | 인사이트 | 조치 |
|--------|---------|------|
| 도구별 호출 비율 | 과도하게 사용되는 API 식별 | 대체 도구 검토, 캐싱 전략 |
| 데이터 전송량 | 불필요한 대용량 응답 | 프롬프트 최적화, 필요 필드만 요청 |
| 피크 시간대 분포 | 예측 가능한 트래픽 | 사전 스케일링, 배치 처리 |

### 4.2 품질/신뢰성 인사이트

| 메트릭 | 인사이트 | 조치 |
|--------|---------|------|
| 실패율 추이 | 특정 도구의 품질 저하 | 대체 업체 평가, SLA 재협상 |
| 재시도 성공률 | 임시적 오류 vs 근본 문제 | 재시도 정책 최적화 |
| 타임아웃 패턴 | 네트워크/서버 문제 | 타임아웃 설정 조정, fallback 전략 |

### 4.3 운영 효율성 인사이트

| 메트릭 | 인사이트 | 조치 |
|--------|---------|------|
| 병목 도구 식별 | 전체 시간의 대부분 차지 | 병렬화, 비동기 처리 검토 |
| 성능 추이 | 점진적 성능 저하 | 용량 확보, 아키텍처 개선 |
| 상관관계 분석 | 동시에 실패하는 도구들 | 공통 의존성 문제 식별 |

---

## 5. 권장 jq 쿼리 라이브러리

`.agent/scripts/lib/jq_queries.json`:

```json
{
  "queries": {
    "tool_usage_summary": "map(select(.status==\"EXTERNAL_TOOL_END\")) | group_by(.tool_name) | map({tool: .[0].tool_name, calls: length, success_rate: (map(select(.tool_status==\"success\")) | length) / length * 100}) | sort_by(-.calls)",
    
    "failure_analysis": "map(select(.status==\"EXTERNAL_TOOL_END\" and .tool_status!=\"success\")) | group_by(.tool_name, .tool_status) | map({tool: .[0].tool_name, status: .[0].tool_status, count: length}) | sort_by(-.count)",
    
    "performance_stats": "map(select(.status==\"EXTERNAL_TOOL_END\")) | group_by(.tool_name) | map({tool: .[0].tool_name, avg_duration: (map(.tool_duration_sec) | add) / length, p95: (map(.tool_duration_sec) | sort | .[(length * 0.95 | floor)]), max_duration: (map(.tool_duration_sec) | max)}) | sort_by(-.avg_duration)",
    
    "daily_trend": "map(select(.status==\"EXTERNAL_TOOL_END\")) | group_by(.ts | split(\"T\")[0]) | map({date: .[0].ts | split(\"T\")[0], total_calls: length, error_count: (map(select(.tool_status==\"error\")) | length), avg_duration: (map(.tool_duration_sec) | add) / length}) | sort_by(.date)",
    
    "cost_estimation": "map(select(.status==\"EXTERNAL_TOOL_END\")) | group_by(.tool_name) | map({tool: .[0].tool_name, total_calls: length, total_input_tokens: (map(.tool_input_bytes) | add) / 3.3, total_output_tokens: (map(.tool_output_bytes) | add) / 3.3}) | map({tool, total_calls, est_cost_usd: ((.total_input_tokens * 0.015 / 1000) + (.total_output_tokens * 0.075 / 1000))})"
  }
}
```

---

## 6. 결론 및 권장사항

### 6.1 인사이트 도출 가능성: **높음** ✅

리서치 결과, EXTERNAL_TOOL 로그에서 다음 인사이트를 체계적으로 도출할 수 있습니다:

1. **사용량 패턴**: 어떤 도구를, 얼마나, 언제 사용하는지
2. **품질 메트릭**: 성공률, 응답시간, 에러 패턴
3. **비용 추정**: 토큰 사용량 기반 비용 예측
4. **이상 징후**: 통계적 이상값, 추이 변화
5. **병목 식별**: 전체 성능에 미치는 영향

### 6.2 우선 적용 권장 스크립트

| 우선순위 | 스크립트 | 목적 | 예상 소요시간 |
|---------|---------|------|--------------|
| 1 | `analyze_external_tools.sh` | 도구별 사용량/성능 요약 | 2시간 |
| 2 | `detect_anomalies.sh` | 자동 이상 감지 | 3시간 |
| 3 | `analyze_api_costs.sh` | 비용 추정 및 최적화 | 2시간 |
| 4 | `generate_report.sh` | 통합 리포트 생성 | 2시간 |

### 6.3 참고 문헌

- Alspaugh et al. "Analyzing Log Analysis: An Empirical Study of User Log Mining" (USENIX LISA14)
- Zhao et al. "An Empirical Investigation of Practical Log Anomaly Detection for Online Service Systems" (2021)
- Wittkopp et al. "A Taxonomy of Anomalies in Log Data" (IEEE 2021)
- Sedlacek et al. "Anomaly Detection in Log Data: A Comparative Study" (IFIP CNSM 2025)
- Chronosphere Logs Usage Analysis Best Practices (2025)
- AWS CloudWatch Logs Insights Documentation

---

**종합 평가**: 로그 분석 스크립트에서 사용 빈도, 실패 빈도, 성능 메트릭 등을 기반으로 한 **체계적인 인사이트 도출이 충분히 가능**하며, 업계 표준 방법론(jq 기반 JSONL 분석, 통계적 이상 감지, KPI 추적)을 적용할 수 있습니다.

*검토 완료: 2026-02-24*
