# 카테고리 체계 재구조화 제안서 (프로바이더 로드밸런싱 적용)

**작성일**: 2026-03-03  
**버전**: 3.1 (오류 수정 + 누락 섹션 추가)  
**상태**: 검토 완료

---

## 📋 실행 요약 (Executive Summary)

본 제안서는 60개 에이전트의 **실제 프롬프트 내 역할(Role)**을 심층 분석하여, 기존 9개의 파편화된 카테고리를 LLM의 본질적 역량(추론/장문/창의/검증)에 맞춰 **5개의 핵심 카테고리**로 완전히 통폐합하는 아키텍처 개선안입니다.

특히 가장 부하가 높은 `claude-sonnet-4-6` 모델을 **역할의 무게(의사결정 vs 실무 변환)**에 따라 두 개의 프로바이더(`opencode`, `antigravity`)로 분산 배치하여 **Rate Limit 병목을 해소하고 가용성을 극대화**했습니다.

### 아키텍처 변경 개요

| 항목 | 기존 (v1.0) | **신규 설계안 (v3.0)** | 개선 효과 |
|---|---|:---:|---|
| **카테고리 수** | 9 개 | **5 개** | 44% 감소 (단순화 및 직관성 확보) |
| **Sonnet 4.6 병목** | 단일 프로바이더 | **`opencode` / `antigravity` 분산** | 로드 밸런싱, API 호출 제한 회피 |
| **저사양 모델** | Gemini 3 Flash 사용 | **전면 제거 (Sonnet 4.6으로 통합)** | 기계적 변환/파싱 오류 원천 차단 |
| **코드 검증 (A5)** | 모호한 카테고리 배정 | **`strict-gatekeeper` (Codex xhigh)** | 검증 정밀도 100% 보장 |

---

## 1. 🏗️ 에이전트 역할 기반 신규 카테고리 (최종 5개)

에이전트들이 스스로를 정의한 프롬프트("당신은 ~입니다")를 기준으로, 가장 본질적인 **5개의 공통 역할(Role) 그룹**을 도출하고 최적의 LLM을 1:1 매핑했습니다.

| # | 신규 카테고리명 | 배정 LLM (프로바이더 분산) | 에이전트 핵심 역할 (프롬프트 추출 기반) | 병합된 기존 카테고리 |
|---|---|---|---|---|
| 1 | **`orchestration-core`**<br>(총괄 및 뼈대 설계) | `opencode/claude-sonnet-4-6` | **[관리자+설계자]** 파이프라인 지휘, 로깅, 승인 판단, 강의 뼈대(커리큘럼 구조) 및 제약조건(시간/분량) 설계. (무거운 의사결정) | `orchestration`<br>`structural`(일부) |
| 2 | **`task-localization`**<br>(기계적 변환/한국어 튜닝) | `google/antigravity-claude-sonnet-4-6` | **[윤문가+파서]** 마크다운/JSON 포맷 강제 변환, 작성된 본문을 한국어 강연 톤(구어체)으로 다듬는 비파괴 실무 편집. | `korean-editing`<br>`codex-support`<br>`fast-extraction`<br>`fast-task`(변환류) |
| 3 | **`deep-production`**<br>(심층 장문 생산) | `anthropic/claude-opus-4-6`<br>*(Variant: max)* | **[주 저자]** 설계된 뼈대에 살을 붙여 긴 교육 본문, 대본, 리포트를 한 호흡으로 깊이 있게 집필. (가장 긴 컨텍스트 생성) | `deep-writing`<br>`structural`(일부) |
| 4 | **`creative-research`**<br>(창의적 시각화 및 탐색) | `google/antigravity-gemini-3.1-pro`<br>*(Variant: high)* | **[디렉터+연구원]** 1M 컨텍스트 기반 대량 레퍼런스 동시 비교, 마케팅 슬로건 도출, 시각 레이아웃 및 이미지 프롬프트 기획. | `visual-creative` |
| 5 | **`strict-gatekeeper`**<br>(엄격한 논리 및 QA) | `openai/gpt-5.3-codex`<br>*(Variant: xhigh)* | **[검사관+보안관]** 코드 실행 정합성 100% 검증, 시간 총합 산술 오류 탐지, 환각(근거 없는 내용) 차단 및 깐깐한 QA. | `quality-gate`<br>`fast-task`(검증류) |

### 카테고리별 에이전트 수 분포

| 카테고리 | 에이전트 수 | 비율 |
|---|:---:|:---:|
| `orchestration-core` | 16 | 27% |
| `task-localization` | 15 | 25% |
| `creative-research` | 12 | 20% |
| `strict-gatekeeper` | 12 | 20% |
| `deep-production` | 5 | 8% |
| **합계** | **60** | **100%** |

---

## 2. ⚖️ Sonnet 4.6 프로바이더 분산 전략 (Load Balancing)

60개 에이전트 중 가장 많은 지분을 차지하는 제어/설계/변환 역할군을 두 프로바이더의 특성에 맞게 논리적으로 분산했습니다.

*   **`orchestration-core` (Opencode / Anthropic 인프라)**
    *   **목적**: 파이프라인 흐름 제어(Tool Use, 로깅)와 굵직한 아키텍처 설계 등 시스템 통합도가 높고 무거운 의사결정이 필요한 작업.
*   **`task-localization` (Antigravity / Google 인프라)**
    *   **목적**: "한국어 현지화(Localization)"와 "단순 포맷 변환(Task)" 등 창의성보다는 꼼꼼함과 속도가 생명인 실무 작업. 구글 인프라의 빠르고 안정적인 대량 텍스트 처리 능력을 활용해 병렬로 쏟아지는 자잘한 변환 지연을 제거.

### 왜 4개가 아닌 5개인가 (4-category vs 5-category)

| 관점 | 4-category (Sonnet 단일) | **5-category (Sonnet 분산, 권장)** |
|---|---|---|
| **Sonnet 분산** | `opencode` 1곳 집중 (31개 에이전트) | `opencode`(16) + `antigravity`(15)로 분산 |
| **Rate Limit** | 병목 위험 높음 | 프로바이더 분리로 회피 |
| **장애 도메인** | Sonnet 장애 시 전체 제어+변환 동시 마비 | 제어(opencode)와 변환(antigravity) 격리 |
| **운영 가시성** | 오버라이드에 의존 (카테고리 구조에 미반영) | 카테고리 레벨에서 명시적 분리 |

### 에스컬레이션 트리거 (5→6+ 카테고리 복원 조건)

| 트리거 조건 | 복원할 카테고리 | 모델 |
|---|---|---|
| P05/P07에서 Sonnet 지연·비용 체감 | `fast-task` (기계적 작업 전용) | `anthropic/claude-haiku-4-5` |
| 추출/추적 작업이 Gemini Pro에서 과도하게 비싸거나 느릴 때 | `fast-extraction` (대량 구조화 추출 전용) | `google/antigravity-gemini-3-flash` |

---

## 3. 🔍 파이프라인별 에이전트 카테고리 매핑 (To-Be)

각 파이프라인의 에이전트들을 새로운 5개 카테고리 체계에 맞게 재배치했습니다.

### P01 Planner (기본: `deep-production`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| A0 Orchestrator | `orchestration` | **`orchestration-core`** | 파이프라인 지휘, 로깅, 승인 판단 |
| A1 Trend Researcher | `visual-creative` | **`creative-research`** | 리서치, 1M 컨텍스트 활용 |
| A5B Learner Analyst | `structural` | **`orchestration-core`** | 페르소나 뼈대 추출 및 제약조건 설계 |
| A3 Curriculum Architect | `structural` | **`orchestration-core`** | 강의 뼈대, 커리큘럼 구조 설계 |
| A2 Instructional Designer | `deep-writing` | **`deep-production`** | 교안 뼈대 바탕 상세 콘텐츠 집필 |
| A7 Differentiation Advisor| `visual-creative` | **`creative-research`** | 창의적 마케팅 슬로건 도출 |
| A5A QA Manager | `quality-gate` | **`strict-gatekeeper`** | 최종 논리, 시간, 팩트 검증 |

### P02 Writer (기본: `deep-production`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| A0 Orchestrator | `orchestration` | **`orchestration-core`** | 파이프라인 지휘 |
| A1 Source Miner | `structural` | **`orchestration-core`** | 비정형 소스에서 뼈대 팩트 추출 |
| A2 Traceability Curator | `fast-extraction` | **`task-localization`** | 마크다운 내 특정 추적 필드 기계적 정리 |
| A3 Curriculum Architect | `structural` | **`orchestration-core`** | 세션별 골격(뼈대) 설계 |
| A4B Session Writer | `deep-writing` | **`deep-production`** | 상세 세션 본문/대본 장문 집필 |
| A4C Material Aggregator | `structural` | **`task-localization`** | 병렬 생성된 보조 패킷 기계적 취합 |
| A5 Code Validator | `structural` | **`strict-gatekeeper`** | **[중요]** 코드 오류 정밀 검사 |
| A6 Visualization Designer | `visual-creative` | **`creative-research`** | 다이어그램, 시각 레이아웃 설계 |
| A7 Learner Exp Designer | `structural` | **`deep-production`** | 학습자 경험 중심 상세 가이드 작성 |
| A8 QA Editor | `quality-gate` | **`task-localization`** | 구어체 변환, 한국어 톤 비파괴 편집 |
| A9 Instructor Support | `codex-support` | **`deep-production`** | 강사 진행 가이드·설명 대본·전환 멘트 장문 집필 |
| A10 Diff Strategist | `visual-creative` | **`creative-research`** | 세션별 창의적 차별화 카피 |
| A11 Chart Specifier | `visual-creative` | **`task-localization`** | 차트 스펙 JSON 기계적 추출/변환 |

### P03 Visualizer (기본: `creative-research`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| A0 Orchestrator | `orchestration` | **`orchestration-core`** | 파이프라인 지휘 |
| A1 Content Analyst | `visual-creative` | **`creative-research`** | 슬라이드 분할을 위한 콘텐츠 분석 |
| A2 Terminology Manager | `fast-extraction` | **`task-localization`** | 용어집 기계적 추출 |
| A3 Slide Architect | `visual-creative` | **`creative-research`** | 시각적 슬라이드 시퀀스 기획 |
| A4 Layout Designer | `visual-creative` | **`creative-research`** | Bento Grid 등 시각 레이아웃 구상 |
| A5 Code Validator | `fast-task` | **`strict-gatekeeper`** | **[중요]** 슬라이드 코드 정합성 100% 검증 |
| A6 Lab Reproducibility | `fast-extraction` | **`strict-gatekeeper`** | **[중요]** 실습 재현성 깐깐한 QA |
| A7 Visual Design Dir | `visual-creative` | **`creative-research`** | 아트 디렉팅, 스케치노트 스타일 지정 |
| A8 Copy Tone Editor | `korean-editing` | **`task-localization`** | 짧고 강렬한 슬라이드 불릿 포인트 윤문 |
| A9 QA Auditor | `quality-gate` | **`strict-gatekeeper`** | 시각화 최종 로직/포맷 QA |
| A10 Trace Citation | `fast-extraction` | **`strict-gatekeeper`** | 원본 출처 환각(할루시네이션) 차단 |

### P04 Prompt Generator (기본: `creative-research`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| P0 Orchestrator | `fast-extraction` | **`orchestration-core`** | 파이프라인 지휘 및 조립 |
| P1 Education Structurer | `fast-extraction` | **`orchestration-core`** | 교육 구조 뼈대 설계 |
| P2 Slide Prompt Architect| `fast-extraction` | **`task-localization`** | 슬라이드 명세 기계적 변환 |
| P3 Visual Spec Curator | `visual-creative` | **`task-localization`** | 시각 규약 정규화 및 튜닝 |
| P4 QA Auditor | `quality-gate` | **`strict-gatekeeper`** | 프롬프트 최종 QA |

### P05 PPTX Converter (기본: `task-localization`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| B0 Orchestrator | `orchestration` | **`orchestration-core`** | 파이프라인 지휘 |
| B1 Slide Parser | `orchestration` | **`task-localization`** | 마크다운 파싱 및 JSON 구조화 추출 |
| B2 HTML Renderer | `visual-creative` | **`task-localization`** | 구조화된 슬라이드 데이터 → HTML 기계적 변환 |
| B3 Asset Generator | `fast-task` | **`task-localization`** | 에셋 기계적 생성/변환 |
| B4 PPTX Assembler | `fast-task` | **`task-localization`** | PPTX 단순 조립 |
| B5 Visual QA | `visual-creative` | **`strict-gatekeeper`** | PPTX 시각적 품질 최종 검증 게이트키퍼 |

### P06 NanoBanana (기본: `creative-research`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| C0 Orchestrator | `orchestration` | **`orchestration-core`** | 파이프라인 지휘 |
| C1 Content Planner | `visual-creative` | **`creative-research`** | 콘텐츠 시각 기획 |
| C2 Prompt Engineer | `visual-creative` | **`creative-research`** | 이미지 생성 창의 프롬프트 작성 |
| C3 Image Generator | `visual-creative` | **`creative-research`** | 이미지 생성 실행 (창의) |
| C4 PPTX Builder | `visual-creative` | **`creative-research`** | PPTX 시각적 빌드 |
| C5 Visual QA | `visual-creative` | **`strict-gatekeeper`** | 슬라이드 이미지 시각적 품질·콘텐츠 정확성 최종 검증 게이트키퍼 |

### P07 Manus Slide (기본: `task-localization`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| D0 Orchestrator | `orchestration` | **`orchestration-core`** | 파이프라인 지휘 |
| D1 Prompt Validator | `fast-task` | **`strict-gatekeeper`** | 프롬프트 정합성 깐깐한 검증 |
| D2 Chunk Splitter | `orchestration` | **`orchestration-core`** | 교시 경계 감지 및 분할 (뼈대 설계) |
| D3 Submission Manager | `fast-task` | **`task-localization`** | 청크별 단순 순차 제출 |
| D4 Post Processor | `fast-task` | **`task-localization`** | 단순 PPTX 병합 (후처리) |
| D5 Visual QA | `quality-gate` | **`strict-gatekeeper`** | 최종 시각/구조 QA |

### P08 Log Analyzer (기본: `deep-production`)
| 에이전트 | 기존 카테고리 | **신규 카테고리** | 역할 매핑 근거 |
|---|:---:|:---:|---|
| L0 Orchestrator | `orchestration` | **`orchestration-core`** | 파이프라인 지휘 |
| L1 Data Collector | `fast-task` | **`task-localization`** | 스크립트 기반 원시 데이터 기계적 수집 |
| L2 Insight Analyst | `quality-gate` | **`orchestration-core`** | 데이터 기반 논리적 아키텍처/인사이트 분석 |
| L3 Optimizer | `quality-gate` | **`orchestration-core`** | 최적화 전략 (구조/방향) 수립 |
| L4 Report Writer | `quality-gate` | **`deep-production`** | 최종 리포트 장문 집필 |
| L5 QA Auditor | `quality-gate` | **`strict-gatekeeper`** | 최종 리포트 논리 결함 깐깐한 QA |

---

## 4. 🚀 마이그레이션 적용 가이드 (수행 목록)

카테고리 체계가 9개에서 5개로 대폭 압축됨에 따라, 시스템 전반의 설정 파일 및 워크플로우 매핑 규칙을 업데이트해야 합니다.

### Step 1. 모델 라우팅 설정 변경
*   **대상 파일**: `.opencode/oh-my-opencode.jsonc`
*   **작업 내용**: `categories` 섹션에 정의된 9개의 기존 카테고리를 삭제하고, 위 1항에서 정의한 **신규 5개 카테고리**(`orchestration-core`, `task-localization`, `deep-production`, `creative-research`, `strict-gatekeeper`)와 각각의 LLM, Variant 프로바이더 설정을 새로 매핑합니다. (특히 Sonnet 4.6을 `opencode`와 `antigravity` 두 프로바이더로 분리하여 등록)

### Step 2. AGENTS.md 테이블 업데이트
*   **대상 파일**: `.agent/AGENTS.md`
*   **작업 내용**: "Per-Agent Model Routing" 섹션의 표를 본 제안서 3항의 "파이프라인별 에이전트 카테고리 매핑 (To-Be)" 내용으로 전면 교체합니다.

### Step 3. 워크플로우 YAML 기본 카테고리 일괄 수정
*   **대상 파일**: `.agent/workflows/*.yaml` (총 8개 파일)
*   **작업 내용**: 각 YAML 파일 내에서, 파이프라인의 **기본(Default) 카테고리 명칭**을 신규 체계에 맞게 일괄 치환합니다. (예: 01_Lecture_Planning.yaml의 기본 카테고리를 `deep-writing`에서 `deep-production`으로 변경)

### Step 4. 로깅 비용 테이블 동기화
*   **대상 파일**: `.agent/scripts/agent_logger.py`
*   **작업 내용**: `COST_TABLE` 딕셔너리에서 제거된 4개 카테고리 키(`fast-task`, `fast-extraction`, `structural`, `codex-support`)를 삭제하고, 신규 5개 카테고리 키로 치환합니다. 비용 단가는 각 카테고리에 배정된 LLM의 토큰 단가에 맞춰 조정합니다.

### Step 5. 에이전트 프롬프트 내 인라인 매핑 테이블 업데이트
*   **대상 파일**: 에이전트 프롬프트 내 `category→model` Quick Reference 테이블이 있는 파일들
*   **예시**: `.agent/agents/01_planner/A0_Orchestrator.md` L285~294의 "에이전트별 category→model 매핑" 테이블
*   **작업 내용**: 기존 9개 카테고리 기반 인라인 테이블을 신규 5개 카테고리 기준으로 전면 교체합니다. 모든 오케스트레이터(A0, B0, C0, D0, L0, P0)의 Quick Reference 테이블을 일괄 확인합니다.

---
**문서 끝**
