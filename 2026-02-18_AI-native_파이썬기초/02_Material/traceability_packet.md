# 추적성 패킷 (Traceability Packet)
> Pipeline 02 — Material Writing v4.0  
> 작성일: 2026-02-25  
> 과정: AI-native 파이썬기초 (40시간, 5일×8시간, 106 micro-sessions)

---

## 1. 출처 표 (Citation Table)

| ID | 출처 유형 | 출처명 | URL/경로 | 접근일 | 신뢰도 | 관련 세션 |
|---|---|---|---|---|---|---|
| **SRC-A01** | 로컬 문서 | AI 시대의 서사 v3 - Claude.md | 참고자료/ | 2026-02-24 | High | 001-022, 031-043, 066, 102, 106 |
| **SRC-A02** | 로컬 PDF | 3 프롬프트 엔지니어링.pdf | 참고자료/ | 2026-02-24 | High | 008, 015, 017, 022-043, 027, 030 |
| **SRC-A03** | 로컬 PDF | 7 기획.pdf | 참고자료/ | 2026-02-24 | High | 031-043, 067, 077-078, 084 |
| **SRC-A04** | 로컬 PDF | 8 코딩.pdf | 참고자료/ | 2026-02-24 | High | 044-064, 065-085, 086-106 |
| **SRC-A05** | 로컬 PDF | 9 디버깅, 테스트, 배포.pdf | 참고자료/ | 2026-02-24 | High | 010, 055, 070-085 |
| **SRC-A06** | 로컬 PDF | gemini-for-google-workspace-prompting-guide-101.pdf | 참고자료/ | 2026-02-24 | High | 024-026, 028-030, 041 |
| **SRC-A07** | 로컬 MD | AI-native_파이썬기초.md | 참고자료/ | 2026-02-24 | High | 004-007, 009, 011-014 |
| **SRC-B01** | NotebookLM | day1_notebooklm.md | source_data/ | 2026-02-24 | Medium | 001-022 |
| **SRC-B02** | NotebookLM | day2_notebooklm.md | source_data/ | 2026-02-24 | Medium | 023-043 |
| **SRC-B03** | NotebookLM | day3_notebooklm.md | source_data/ | 2026-02-24 | Medium | 044-064 |
| **SRC-B04** | NotebookLM | day4_notebooklm.md | source_data/ | 2026-02-24 | Medium | 065-085 |
| **SRC-B05** | NotebookLM | day5_notebooklm.md | source_data/ | 2026-02-24 | Medium | 086-106 |
| **SRC-C01** | Deep Research | day1_deep_research.md | source_data/ | 2026-02-24 | Medium | 001-022 |
| **SRC-C02** | Deep Research | day2_deep_research.md | source_data/ | 2026-02-24 | Medium | 023-043 |
| **SRC-C03** | Deep Research | day3_deep_research.md | source_data/ | 2026-02-24 | Medium | 044-064 |
| **SRC-C04** | Deep Research | day4_deep_research.md | source_data/ | 2026-02-24 | Medium | 065-085 |
| **SRC-C05** | Deep Research | day5_deep_research.md | source_data/ | 2026-02-24 | Medium | 086-106 |

---

## 2. 버전 메타데이터 (Version Metadata)

### 2.1 개발 환경 (Development Environment)

| 항목 | 버전 | 비고 |
|---|---|---|
| **Python** | 3.14.x | 강의 환경 기준 (Windows 11) |
| **OS** | Windows 11 | 수강생 환경 표준 |
| **IDE** | Antigravity | Google의 Agent-First IDE (2025년 11월 출시) |
| **AI Model** | Gemini 3 Pro | 강의 내 AI 협업 기준 모델 |
| **Package Manager** | uv | Rust 기반 초고속 패키지 매니저 |

### 2.2 핵심 라이브러리 및 도구

| 항목 | 버전/상태 | 사용 세션 | 비고 |
|---|---|---|---|
| **dataclasses** | Python 3.7+ | 089-093 | 데이터 클래스 데코레이터 |
| **json** | Built-in | 098 | JSON 파일 직렬화 |
| **sqlite3** | Built-in | 099 | SQLite 데이터베이스 |
| **typing** | Python 3.5+ | 056-057 | 타입 힌트 (Type Hints) |

### 2.3 강의 설계 기준

| 항목 | 값 | 설명 |
|---|---|---|
| **총 시간** | 40시간 | 5일 × 8시간 |
| **총 세션** | 106개 | Micro-session 단위 |
| **일일 구성** | 22, 21, 21, 21, 22 | 각 일차별 세션 수 |
| **학습 패러다임** | AI-native | 코드 타이핑 → 문제 정의 중심 |
| **개발 방법론** | SDD (Specification-Driven Development) | 명세 주도 개발 |

---

## 3. 업데이트 영향 분석 (Impact Analysis)

### 3.1 기술 변경 시 영향도 분석

| 변경 가능 항목 | 영향 세션 | 우선순위 | 영향 범위 | 메모 |
|---|---|---|---|---|
| **Python 버전 업데이트** | 044-064, 065-085, 086-106 | **High** | 문법, 타입 힌트, 데이터클래스 | 3.14.x → 4.0 시 주요 문법 변경 가능성 |
| **Antigravity IDE 업데이트** | 004-007 | **High** | 환경 구성, 에이전트 인터페이스 | Agent Manager 인터페이스 변경 시 전체 재교육 필요 |
| **Gemini 모델 업그레이드** | 001-106 (전체) | **Medium** | AI 응답 품질, 프롬프트 효율성 | 새 모델 출시 시 프롬프트 예시 업데이트 필요 |
| **uv 패키지 매니저 버전** | 011-014 | **Medium** | 설치 속도, 명령어 문법 | 주요 버전 변경 시 설치 스크립트 수정 |
| **Windows 11 업데이트** | 004-014 | **Low** | 환경 변수, 경로 설정 | 일반적으로 호환성 유지 |
| **SQLite 버전** | 099 | **Low** | DB 기능, SQL 문법 | 기본 CRUD 기능은 안정적 |

### 3.2 콘텐츠 변경 시 영향도 분석

| 변경 항목 | 영향 세션 | 우선순위 | 수정 난이도 | 메모 |
|---|---|---|---|---|
| **프롬프트 엔지니어링 기법** | 023-043 | **High** | 중간 | PTCF 프레임워크 변경 시 Day 2 전체 재구성 |
| **SDD 방법론** | 031-043, 067-085 | **High** | 높음 | 명세 작성 프로세스 변경 시 PRD 템플릿 전면 개정 |
| **CRUD 개념** | 068-071 | **Medium** | 낮음 | 기본 개념이므로 예시만 업데이트 |
| **OOP 패러다임** | 086-106 | **High** | 높음 | 클래스 설계 패턴 변경 시 Day 5 전체 영향 |
| **테스트 시나리오 분류** | 077-078, 084 | **Medium** | 낮음 | 정상/경계/예외 분류는 안정적 |
| **코드 리뷰 체크포인트** | 079-080, 085 | **Low** | 낮음 | 5대 체크포인트는 보편적 기준 |

### 3.3 출처 신뢰도 변경 시 영향

| 출처 ID | 신뢰도 | 변경 시나리오 | 영향 세션 | 대응 방안 |
|---|---|---|---|---|
| **SRC-A01** (AI 시대의 서사) | High | 철학적 프레임 변경 | 001-022, 066, 102, 106 | 새로운 비유 체계 개발 필요 |
| **SRC-A02~A06** (PDF 자료) | High | 내용 오류 발견 | 해당 세션 | 즉시 수정 및 재검증 |
| **SRC-B01~B05** (NotebookLM) | Medium | 생성 내용 부정확 | 해당 일차 전체 | 재생성 또는 로컬 자료로 대체 |
| **SRC-C01~C05** (Deep Research) | Medium | 정보 오래됨 | 해당 일차 전체 | 최신 정보로 재조사 |

---

## 4. 세션별 출처 매핑 (Session-Source Mapping)

### Day 1 (세션 001-022)
- **주요 출처**: SRC-A01 (서사), SRC-A02 (프롬프트), SRC-A07 (스펙), SRC-B01, SRC-C01
- **핵심 개념**: 패러다임 전환, Antigravity 환경, uv 패키지 매니저, 첫 프롬프트
- **신뢰도**: High (로컬 자료 중심)

### Day 2 (세션 023-043)
- **주요 출처**: SRC-A02 (프롬프트), SRC-A03 (기획), SRC-A06 (Gemini 가이드), SRC-B02, SRC-C02
- **핵심 개념**: PTCF 프레임워크, 5대 필수 항목, PRD 작성, SDD 방법론
- **신뢰도**: High (프롬프트 + 기획 자료 결합)

### Day 3 (세션 044-064)
- **주요 출처**: SRC-A04 (코딩), SRC-B03, SRC-C03
- **핵심 개념**: 변수, 자료구조, 제어문, 함수, 리스트 컴프리헨션
- **신뢰도**: High (코딩 기초 자료)

### Day 4 (세션 065-085)
- **주요 출처**: SRC-A04 (코딩), SRC-A05 (디버깅/테스트), SRC-B04, SRC-C04
- **핵심 개념**: 절차적 vs 구조적, 리팩토링, 테스트 시나리오, 코드 리뷰
- **신뢰도**: High (코딩 + 테스트 자료 결합)

### Day 5 (세션 086-106)
- **주요 출처**: SRC-A04 (코딩 OOP), SRC-A01 (서사 마무리), SRC-B05, SRC-C05
- **핵심 개념**: 클래스, 상속, 다형성, DI, 데이터 영속화
- **신뢰도**: High (OOP 심화 자료)

---

## 5. 출처 신뢰도 기준 (Source Credibility Criteria)

### High 신뢰도 (High Credibility)
- ✅ 로컬 참고자료 (내부 검증됨)
- ✅ 공식 문서 (Google Gemini 가이드)
- ✅ 학술 자료 (PDF 형식, 구조화됨)
- ✅ 강사 직접 작성 (AI 시대의 서사)

### Medium 신뢰도 (Medium Credibility)
- ⚠️ NotebookLM 생성 콘텐츠 (AI 생성, 검증 필요)
- ⚠️ Deep Research 보고서 (배경 조사용, 보조 자료)
- ⚠️ 온라인 검색 결과 (최신성 우수, 검증 필요)

### Low 신뢰도 (Low Credibility)
- ❌ 미검증 온라인 소스
- ❌ 개인 블로그 (특정 관점 편향 가능)
- ❌ 오래된 자료 (버전 호환성 문제)

---

## 6. 인용 규칙 (Citation Rules)

### 6.1 강의 자료 작성 시 인용 방식

```markdown
**개념 설명**
[개념 설명] [Source A: 파일명, 섹션] [Source B: NotebookLM] [Source C: Deep Research]

**예시**
변수는 데이터에 붙이는 이름표입니다 [Source A: 8 코딩.pdf, §8.1] 
[Source A: AI 시대의 서사 v3, §데이터는 재료, 변수는 그릇 비유]
```

### 6.2 세션 자료 내 출처 표기

- **[Source A]**: 로컬 참고자료 (신뢰도 최고)
- **[Source B]**: NotebookLM 생성 콘텐츠 (보조 설명)
- **[Source C]**: Deep Research 보고서 (배경 정보)

### 6.3 다중 출처 인용

```markdown
개념 정의 [Source A][Source B]
핵심 개념 [Source A][Source C]
실습 예시 [Source B][Source C]
```

---

## 7. 변경 이력 및 버전 관리 (Change Log)

| 날짜 | 버전 | 변경 사항 | 영향 세션 | 승인자 |
|---|---|---|---|---|
| 2026-02-25 | v1.0 | 초기 생성 | 001-106 | A2_Traceability_Curator |
| - | - | - | - | - |

---

## 8. 출처 접근성 및 보존 (Source Accessibility & Preservation)

### 8.1 로컬 자료 (Local Resources)
- **위치**: `/참고자료/` 디렉토리
- **형식**: MD, PDF
- **보존 상태**: ✅ 안정적 (로컬 저장)
- **접근성**: ✅ 항상 가능

### 8.2 NotebookLM 자료 (Cloud-based)
- **위치**: `source_data/day{1-5}_notebooklm.md`
- **형식**: MD (다운로드 저장)
- **보존 상태**: ⚠️ 클라우드 의존 (원본 URL 유지 필요)
- **접근성**: ✅ 로컬 사본 보유

### 8.3 Deep Research 자료 (Cloud-based)
- **위치**: `source_data/day{1-5}_deep_research.md`
- **형식**: MD (다운로드 저장)
- **보존 상태**: ⚠️ 클라우드 의존 (세션 ID 기록)
- **접근성**: ✅ 로컬 사본 보유

---

## 9. 출처 업데이트 체크리스트 (Source Update Checklist)

### 분기별 검증 항목

- [ ] **Q1**: Python 3.14.x 호환성 확인
- [ ] **Q1**: Antigravity IDE 최신 버전 기능 검증
- [ ] **Q2**: Gemini 모델 성능 변화 모니터링
- [ ] **Q2**: uv 패키지 매니저 업데이트 확인
- [ ] **Q3**: 로컬 PDF 자료 내용 정확성 재검증
- [ ] **Q3**: NotebookLM 생성 콘텐츠 품질 평가
- [ ] **Q4**: Deep Research 정보 최신성 확인
- [ ] **Q4**: 전체 출처 신뢰도 재평가

---

## 10. 부록: 출처 상세 정보 (Appendix: Detailed Source Information)

### A. 로컬 문서 (Local Documents)

#### SRC-A01: AI 시대의 서사 v3 - Claude.md
- **작성자**: 강사 (Claude)
- **작성일**: 2026년 초
- **크기**: ~806 lines
- **주요 섹션**: 패러다임 전환, 네비게이션 비유, 문제정의 vs 해결, SDD, 예측-검증-설명
- **신뢰도**: ⭐⭐⭐⭐⭐ (High)

#### SRC-A02~A06: PDF 자료 (5개)
- **형식**: PDF (OCR 처리됨)
- **추출 방법**: look_at 도구 활용
- **커버리지**: Day 1-5 전체
- **신뢰도**: ⭐⭐⭐⭐⭐ (High)

#### SRC-A07: AI-native_파이썬기초.md
- **내용**: 환경 구성, 도구 스펙, Antigravity 가이드
- **신뢰도**: ⭐⭐⭐⭐⭐ (High)

### B. NotebookLM 자료 (5개)
- **생성 방식**: Google NotebookLM 쿼리 기반
- **각 파일 크기**: 2,500~3,000 words
- **인용 포함**: ✅ Yes
- **신뢰도**: ⭐⭐⭐⭐ (Medium - AI 생성)

### C. Deep Research 자료 (5개)
- **생성 방식**: 배경 조사 에이전트 활용
- **각 파일 크기**: 5,000~8,000 words
- **세션 ID 기록**: ✅ Yes
- **신뢰도**: ⭐⭐⭐⭐ (Medium - 보조 자료)

---

## 11. 최종 검증 (Final Verification)

✅ **모든 106개 세션에 대한 출처 매핑 완료**  
✅ **3-Source 정책 준수 확인** (로컬 + NotebookLM + Deep Research)  
✅ **버전 메타데이터 기록** (Python 3.14.x, Windows 11, Gemini 3 Pro, uv)  
✅ **영향 분석 완료** (기술 변경, 콘텐츠 변경, 신뢰도 변경)  
✅ **인용 규칙 정의** (강의 자료 작성 시 적용)  
✅ **출처 신뢰도 분류** (High/Medium/Low)  

---

**문서 작성**: A2_Traceability_Curator  
**작성일**: 2026-02-25  
**버전**: v1.0  
**다음 검토**: 2026-03-31 (분기별 검증)
