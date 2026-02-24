# 로그 분석 스크립트 개발 작업 계획서

> **프로젝트명**: Lecture Factory EXTERNAL_TOOL 로그 분석 자동화  
> **작성일**: 2026-02-24  
> **버전**: 1.0  
> **상태**: 계획 완료, 실행 대기

---

## 1. 작업 개요

### 1.1 목적
EXTERNAL_TOOL 로그(JSONL)에서 **사용 빈도, 실패 패턴, 성능 메트릭, 이상 징후**를 자동으로 분석하여 비용 최적화, 품질 개선, 운영 효율성 증대를 위한 인사이트를 도출합니다.

### 1.2 배경
- 현재 7개 에이전트에서 7가지 외부 도구(NotebookLM, Deep Research, Gemini API, Manus AI 등) 호출이 로깅됨
- 로그는 `.agent/logs/*.jsonl`에 축적되지만 분석 자동화 체계 부재
- 수동 분석 시 시간 소모(1시간+), 일관성 부족, 실시간 감지 불가

### 1.3 기대 효과
| 영역 | 효과 | 수치 목표 |
|------|------|----------|
| 비용 최적화 | 과도한 API 사용 도구 식별 | 불필요 호출 20% 감소 |
| 품질 관리 | 실패 패턴 실시간 감지 | 장애 인지 시간 80% 단축 |
| 운영 효율 | 병목 도구 자동 식별 | 성능 최적화 우선순위 자동화 |
| 규제 준수 | API 호출 이력 추적 | 감사 대응 시간 90% 단축 |

---

## 2. 작업 범위

### 2.1 포함 범위 (In-Scope)
- **분석 스크립트 개발**: 5개 핵심 스크립트
- **jq 쿼리 라이브러리**: 재사용 가능한 쿼리 20+개
- **자동화 설정**: cron 기반 주기적 실행
- **리포팅**: Markdown 기반 대시보드 생성
- **알림 체계**: 임계값 기반 경고 (선택적)

### 2.2 제외 범위 (Out-of-Scope)
- 실시간 스트리밍 분석 (Complex Event Processing)
- 머신러닝 기반 예측 모델 개발
- 외부 모니터링 도구 연동 (Datadog, Splunk 등)
- 웹 기반 GUI 대시보드

### 2.3 대상 로그
```
.agent/logs/
├── *_01_Lecture_Planning.jsonl      # NotebookLM, Deep Research, PDF
├── *_02_Material_Writing.jsonl       # 5가지 도구
├── *_06_NanoBanana_PPTX.jsonl        # Gemini API
└── *_07_Manus_Slide.jsonl            # Manus AI API
```

---

## 3. 작업 단계 및 산출물

### Phase 1: 기반 구조 설정 (Day 1-2)

| 작업 ID | 작업 내용 | 산출물 | 예상 소요시간 | 의존성 |
|---------|----------|--------|--------------|--------|
| P1-1 | 디렉토리 구조 생성 | `.agent/scripts/`, `.agent/dashboard/` | 30분 | - |
| P1-2 | jq 쿼리 라이브러리 작성 | `lib/jq_queries.json` (20개 쿼리) | 4시간 | P1-1 |
| P1-3 | 임계값 설정 파일 작성 | `lib/thresholds.conf` | 1시간 | P1-1 |
| P1-4 | 공통 함수 라이브러리 | `lib/common.sh` | 2시간 | P1-1 |

**Phase 1 산출물**:
```
.agent/scripts/
└── lib/
    ├── jq_queries.json      # 재사용 쿼리 라이브러리
    ├── thresholds.conf     # 알림 임계값 설정
    └── common.sh           # 공통 함수 (로그 파싱, JSONL 처리 등)
```

---

### Phase 2: 핵심 분석 스크립트 개발 (Day 3-7)

#### 스크립트 1: analyze_external_tools.sh (Day 3-4)
**목적**: 외부 도구별 사용량/성능 요약

| 기능 | 설명 | jq 쿼리 예시 |
|------|------|-------------|
| 호출 빈도 | 도구별 총 호출 횟수 | `group_by(.tool_name) \| map({tool, calls: length})` |
| 성공률 | 도구별 성공/실패/타임아웃 비율 | `map(select(.tool_status=="success")) \| length` |
| 성능 통계 | 평균/중간값/P95/P99 응답시간 | `map(.tool_duration_sec) \| (add/length)` |
| 데이터 전송량 | 입력/출력 바이트 합계 | `map(.tool_input_bytes) \| add` |

**산출물**: `.agent/dashboard/analysis/tool_usage_YYYYMMDD.md`

---

#### 스크립트 2: detect_anomalies.sh (Day 5-6)
**목적**: 자동 이상 징후 감지 및 알림

| 이상 유형 | 감지 방법 | 임계값 |
|-----------|----------|--------|
| 높은 실패율 | 실패율 > 5% | `ALERT_THRESHOLD_FAILURE=5` |
| 잦은 타임아웃 | 타임아웃 비율 > 10% | `ALERT_THRESHOLD_TIMEOUT=10` |
| 느린 응답 | 평균 응답 > 60초 | `ALERT_THRESHOLD_DURATION=60` |
| Z-score 이상 | \|z_score\| > 3 | 통계적 이상치 |
| 연속 실패 | 동일 도구 3회 연속 실패 | 연속성 패턴 매칭 |

**산출물**: `.agent/dashboard/alerts_YYYYMMDD.md`

---

#### 스크립트 3: analyze_api_costs.sh (Day 7)
**목적**: API 호출 비용 추정 및 최적화

| 계산 항목 | 공식 | 참고 |
|-----------|------|------|
| 토큰 수 | `bytes ÷ 3.3` | 한국어+코드 혼합 기준 |
| Gemini API | 이미지당 $0.03~0.05 (2K) | NanoBanana |
| Manus AI | 호출당 $0.10~0.50 (예상) | 세션당 비용 |
| NotebookLM | 무료 (현재) | - |

**산출물**: `.agent/dashboard/analysis/cost_estimate_YYYYMMDD.md`

---

### Phase 3: 고급 분석 스크립트 (Day 8-10)

#### 스크립트 4: analyze_trends.sh (Day 8-9)
**목적**: 시계열 추이 분석

| 분석 항목 | 설명 | jq 활용 |
|-----------|------|---------|
| 일별 호출 추이 | 날짜별 총 호출/에러/성공 | `group_by(.ts \| split("T")[0])` |
| 성능 저하 추이 | 3일 연속 20% 이상 성능 저하 감지 | Sliding window 비교 |
| 도구 도입 추이 | 새로운 도구 사용량 증가 패턴 | Rolling average |
| 계절성 패턴 | 요일/시간대별 패턴 | 시간대 group_by |

**산출물**: `.agent/dashboard/analysis/trends_YYYYMMDD.md`

---

#### 스크립트 5: generate_report.sh (Day 10)
**목적**: 통합 리포트 생성

| 섹션 | 내용 | 데이터 소스 |
|------|------|------------|
| Executive Summary | 핵심 인사이트 3-5개 | 모든 분석 결과 요약 |
| Tool Performance Matrix | 도구별 성능 테이블 | analyze_external_tools.sh |
| Alert Summary | 활성화된 경고 목록 | detect_anomalies.sh |
| Cost Analysis | 비용 추정 및 추이 | analyze_api_costs.sh |
| Recommendations | 최적화 제안 | Rule-based 추천 |

**산출물**: `.agent/dashboard/report_YYYYMMDD.md`

---

### Phase 4: 자동화 및 운영화 (Day 11-12)

| 작업 ID | 작업 내용 | 산출물 | 예상 소요시간 |
|---------|----------|--------|--------------|
| P4-1 | cron 스케줄 설정 | `.agent/scripts/crontab.txt` | 1시간 |
| P4-2 | 주간 리포트 자동화 | `weekly_report.sh` | 2시간 |
| P4-3 | 로그 로테이션 설정 | `logrotate.conf` | 1시간 |
| P4-4 | 문서화 | `README.md`, `TROUBLESHOOTING.md` | 2시간 |

**cron 스케줄 예시**:
```bash
# 매일 09:00: 전일 로그 분석
cat .agent/scripts/crontab.txt
0 9 * * * /bin/bash /Users/mrsono0/Obsidian\ Vault/0\ 리서치/_lecture-factory/.agent/scripts/daily_analysis.sh

# 매주 월요일 09:00: 주간 리포트
0 9 * * 1 /bin/bash /Users/mrsono0/Obsidian\ Vault/0\ 리서치/_lecture-factory/.agent/scripts/weekly_report.sh
```

---

## 4. 작업 일정

### 간트 차트 (총 12일)

```
Phase 1: 기반 구조 (Day 1-2)
[P1-1] 디렉토리 생성       ██
[P1-2] jq 쿼리 라이브러리   ████████
[P1-3] 임계값 설정         ██
[P1-4] 공통 함수          ████

Phase 2: 핵심 스크립트 (Day 3-7)
[S1] analyze_external_tools  ████████
[S2] detect_anomalies         ████████
[S3] analyze_api_costs        ████

Phase 3: 고급 스크립트 (Day 8-10)
[S4] analyze_trends           ████████
[S5] generate_report          ████

Phase 4: 자동화 (Day 11-12)
[P4-1] cron 설정              ██
[P4-2] 주간 리포트            ████
[P4-3] 로그 로테이션          ██
[P4-4] 문서화                 ████
```

### 마일스톤

| 마일스톤 | 날짜 | 완료 기준 | 산출물 |
|---------|------|----------|--------|
| M1: 기반 완료 | Day 2 | lib/ 디렉토리 4개 파일 완성 | 코드 리뷰 완료 |
| M2: 핵심 기능 | Day 7 | 3개 스크립트 실행 테스트 통과 | 테스트 로그 1000줄 처리 |
| M3: 고급 분석 | Day 10 | 5개 스크립트 통합 실행 | 통합 리포트 생성 |
| M4: 운영화 | Day 12 | cron 동작 확인, 문서 완성 | 운영 체계 확립 |

---

## 5. 리소스 요구사항

### 5.1 인적 리소스
| 역할 | 필요 기술 | 예상 투입 |
|------|----------|----------|
| 스크립트 개발자 | Bash, jq, JSONL 처리 | 100% (12일) |
| 검증 담당자 | Log 분석, 테스트 | 30% (4일) |
| 문서 작성자 | Markdown, 기술 문서 | 20% (3일) |

### 5.2 기술/도구
```bash
# 필수 도구
jq >= 1.6          # JSONL 처리
bash >= 4.0        # 스크립트 실행
GNU date           # 타임스탬프 처리

# 선택 도구
gnuplot            # (옵션) 시각화
curl               # (옵션) 외부 알림
```

### 5.3 테스트 데이터
```bash
# 테스트용 로그 파일 생성 (10,000줄)
.agent/scripts/generate_test_logs.sh  # 가짜 로그 생성
.agent/logs/test_logs.jsonl           # 테스트 대상
```

---

## 6. 품질 기준 및 검증

### 6.1 성능 요구사항
| 항목 | 기준 | 측정 방법 |
|------|------|----------|
| 처리 속도 | 10,000줄/초 이상 | `time cat logs.jsonl \| jq ...` |
| 메모리 사용 | 100MB 이하 | `/usr/bin/time -v` |
| 정확도 | 95% 이상 | 샘플 100개 수동 검증 |
| 가용성 | 99% (cron 실패율 <1%) | 로그 모니터링 |

### 6.2 테스트 계획

#### 단위 테스트 (각 스크립트별)
```bash
# 테스트 시나리오
1. 빈 로그 파일 처리
2. 1줄 로그 처리
3. 10,000줄 로그 처리
4. 깨진 JSON 라인 처리 (내결함성)
5. 임계값 경계값 테스트 (5% vs 5.01%)
```

#### 통합 테스트
```bash
# 전체 파이프라인 테스트
./run_all_analyses.sh test_logs.jsonl
# → 5개 리포트 파일 생성 확인
```

#### 성능 테스트
```bash
# 100,000줄 로그로 부하 테스트
./generate_test_logs.sh 100000
/usr/bin/time -v ./analyze_external_tools.sh large_logs.jsonl
```

---

## 7. 위험 관리

| 위험 ID | 위험 내용 | 가능성 | 영향 | 대응 전략 |
|---------|----------|--------|------|----------|
| R1 | jq 메모리 부족 (대용량 로그) | 중 | 중 | 스트리밍 처리, --slurp 피하기 |
| R2 | 로그 형식 변경 | 낮 | 높 | 스키마 검증, 하위호환성 |
| R3 | cron 실행 실패 (환경 변수) | 중 | 중 | 절대경로, .env 로드 |
| R4 | 임계값 설정 부적절 | 중 | 중 | 초기 1주일 모니터링 후 조정 |
| R5 | 분석 결과 과부하 (알림 피로) | 중 | 중 | 알림 그룹화, 심각도 레벨 |

---

## 8. 산출물 목록

### 8.1 코드 산출물
```
.agent/scripts/
├── lib/
│   ├── jq_queries.json          # 쿼리 라이브러리
│   ├── thresholds.conf          # 알림 설정
│   └── common.sh                # 공통 함수
├── analyze_external_tools.sh    # 도구별 분석
├── detect_anomalies.sh          # 이상 감지
├── analyze_api_costs.sh         # 비용 분석
├── analyze_trends.sh            # 추이 분석
├── generate_report.sh           # 리포트 생성
├── daily_analysis.sh            # 일일 자동화
├── weekly_report.sh             # 주간 자동화
├── generate_test_logs.sh        # 테스트 데이터
└── crontab.txt                  # 스케줄 설정
```

### 8.2 문서 산출물
```
.agent/scripts/
├── README.md                    # 사용 가이드
├── TROUBLESHOOTING.md          # 문제 해결
├── API.md                       # 함수 레퍼런스
└── CHANGELOG.md                 # 변경 이력

.agent/dashboard/
├── analysis/
│   ├── tool_usage_YYYYMMDD.md
│   ├── cost_estimate_YYYYMMDD.md
│   └── trends_YYYYMMDD.md
├── alerts_YYYYMMDD.md
└── report_YYYYMMDD.md
```

---

## 9. 성공 기준 (Acceptance Criteria)

### 9.1 기능적 기준
- [ ] 7가지 외부 도구 모두 분석 가능
- [ ] 10,000줄 로그 10초 내 처리
- [ ] 4가지 이상 유형의 이상 징후 감지
- [ ] 비용 추정 정확도 ±20% 이내
- [ ] cron 자동화 정상 동작 (7일 연속)

### 9.2 비기능적 기준
- [ ] jq 쿼리 재사용성 80% 이상
- [ ] 코드 커버리지 (테스트 시나리오) 90% 이상
- [ ] 문서화 완성도 100%
- [ ] 사용자 피드백 긍정 80% 이상

---

## 10. 승인 및 검토

| 역할 | 이름 | 서명/날짜 |
|------|------|----------|
| 작업 요청자 | | |
| 작업 담당자 | | |
| 검토자 (QA) | | |
| 승인자 (PM) | | |

---

## 11. 참고 자료

1. `.agent/LOG_ANALYSIS_INSIGHTS_RESEARCH_REPORT.md` - 리서치 보고서
2. `.agent/EXTERNAL_TOOL_LOGGING_EXPANSION_REPORT.md` - 로깅 확장 보고서
3. `.agent/logging-protocol.md` - 로깅 프로토콜 정의
4. jq Manual: https://jqlang.org/manual/
5. "Analyzing Log Analysis: An Empirical Study" (USENIX LISA14)

---

**계획서 버전**: 1.0  
**마지막 수정**: 2026-02-24  
**다음 검토**: 작업 완료 후
