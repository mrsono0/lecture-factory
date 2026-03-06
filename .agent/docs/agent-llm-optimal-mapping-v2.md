# Lecture Factory 에이전트-LLM 최적 매핑 가이드 (v2.1)

> **작성일**: 2026-03-06  
> **버전**: v2.1 (리서치 기반 가격 수정)  
> **정본**: `.agent/AGENTS.md`, `.opencode/oh-my-opencode.jsonc`  
> **비교 원본**: `agent-llm-mappings.md` v1.0, `agent-llm-routing-guide.md`

---

## Executive Summary

### 문서 비교 분석 결과

| 문서 | 특성 | 주요 차이 |
|------|------|----------|
| `agent-llm-mappings.md` v1.0 | Gemini 제외, 상세 표 | Pipeline별 전체 에이전트 포함 |
| `agent-llm-routing-guide.md` | Slash command 중심 | 오케스트레이터 + 비용 분석 |
| **불일치점** | 7개 에이전트 | A3, A1, A4C, P1 등 Opus/Sonnet 선택 상이 |

### 주요 문제점
1. **`deep-production-alt` (GLM-5) 의존** - 한국어 및 추론 품질 불안정
2. **`creative-research` 과다 배정** - 정확성 작업에 창의성 모델 배정
3. **고비용 모델 낭비** - 기계적 작업에 Opus/Sonnet 배정

---

## 1. 새로운 카테고리 체계 (8개)

### 1.1 카테고리 재설계 개요

| # | 카테고리 | 모델 | 월별 비용 지수 | 용도 |
|---|---------|------|---------------|------|
| 1 | `orchestration-core` | `claude-sonnet-4-6` | ★★★☆☆ | 파이프라인 총괄, 조율 |
| 2 | `task-localization` | `claude-sonnet-4-6` | ★★★☆☆ | 한국어 톤, 용어 정규화 |
| 3 | **`premium-production`** ⭐ | `claude-opus-4-6` | ★★★★★ | 핵심 집필, 딥리서치 |
| 4 | **`long-context-prod`** ⭐ | `minimax-2.5` | ★☆☆☆☆ | 장문 교안, 머지, 리포트 |
| 5 | `visual-creative` | `qwen3.5-plus` | ★★☆☆☆ | 시각 설계, 이미지 프롬프트 |
| 6 | `strict-gatekeeper` | `gpt-5.3-codex` | ★★★★☆ | 코드 검증, QA, 스키마 |
| 7 | `mechanical-pipeline` | `kimi-k2.5` | ★☆☆☆☆ | 파싱, 조립, 제출 |
| 8 | **`standard-production`** | `claude-sonnet-4-6` | ★★★☆☆ | 일반 집필, 구조 설계 |

### 1.2 카테고리별 상세 스펙

#### `orchestration-core` (Sonnet)
- **용도**: 워크플로우 조율, 흐름 제어, 의사결정
- **특성**: 균형 잡힌 성능, 빠른 응답
- **적용 에이전트**: 모든 A0/P0 오케스트레이터

#### `task-localization` (Sonnet)
- **용도**: 한국어 톤 편집, 용어 정규화, 출처 큐레이션
- **특성**: 한국어 문법/어조 정확도 중시
- **적용 에이전트**: A2, A8, P2 등 한국어 처리

#### `premium-production` (Opus) ⭐
- **용도**: **최고 품질 필요** 핵심 집필, 딥리서치, 복잡 설계
- **특성**: 최상위 추론 능력, 장문 생성
- **적용 에이전트**: P02-A4B (세션 집필), P01-A1 (딥리서치)

#### `long-context-prod` (MiniMax 2.5) ⭐
- **용도**: **장문 컨텍스트 활용** 교안 집필, 머지, 리포트
- **특성**: 1M 토큰, Opus 대비 98% 저렴 ($0.30/$1.20), 한국어 우수
- **적용 에이전트**: P02-A4C (머지), P08-L4 (리포트), P02-A4B (대안)

#### `visual-creative` (Qwen 3.5 Plus)
- **용도**: 시각 설계, 이미지 프롬프트, 창의적 작업
- **특성**: 창의성, 저비용
- **적용 에이전트**: P03-A3/A4/A7, P06-C1/C2

#### `strict-gatekeeper` (GPT-5.3 Codex)
- **용도**: 코드 검증, QA, 스키마 준수 검증
- **특성**: 논리적 검증, 코드 실행 정확성
- **적용 에이전트**: 모든 QA, 코드 검증

#### `mechanical-pipeline` (Kimi K2.5)
- **용도**: 파싱, 렌더링, 조립, API 제출
- **특성**: tool-use #1, Sonnet 대비 ~30배 저렴
- **적용 에이전트**: P05, P07 파싱/조립

#### `standard-production` (Sonnet)
- **용도**: 일반 집필, 구조 설계, 보조 콘텐츠
- **특성**: 균형, 비용 효율
- **적용 에이전트**: P01-A3, P02-A3/A9, P04-P1

---

## 2. 파이프라인별 최적 매핑

### 2.1 P01 — Lecture Planning (7 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| A0 Orchestrator | 기획 총괄 | `orchestration-core` | Sonnet | 유지 |
| A1 Trend Researcher | 딥리서치 | **`premium-production`** | **Opus** | 복잡한 트렌드 분석 |
| A2 Instructional Designer | 교수설계 | **`long-context-prod`** | **MiniMax 2.5** | 1M 컨텍스트로 다양한 교수법 참고 |
| A3 Curriculum Architect | 커리큘럼 | **`standard-production`** | **Sonnet** | 구조 설계 (GLM-5→Sonnet) |
| A5A QA Manager | 품질 검증 | `strict-gatekeeper` | Codex | 유지 |
| A5B Learner Analyst | 학습자 분석 | **`standard-production`** | **Sonnet** | 페르소나 분석 (GLM-5→Sonnet) |
| A7 Differentiation Advisor | 차별화 전략 | **`standard-production`** | **Sonnet** | USP 설계 (Qwen→Sonnet) |

**P01 변경 요약**:
- ❌ `deep-production-alt` (GLM-5) → ✅ `standard-production` (Sonnet)
- ✅ `premium-production` (Opus) for 딥리서치
- ✅ `long-context-prod` (MiniMax) for 교수설계

---

### 2.2 P02 — Material Writing (13 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| A0 Orchestrator | 교안 총괄 | `orchestration-core` | Sonnet | 유지 |
| A1 Source Miner | 3-Source 수집 | **`standard-production`** | **Sonnet** | 팩트 추출 정확성 (orchestration→standard) |
| A2 Traceability Curator | 출처 큐레이션 | `task-localization` | Sonnet | 유지 |
| A3 Curriculum Architect | 골격 설계 | **`standard-production`** | **Sonnet** | 구조 설계 (GLM-5→Sonnet) |
| **A4B Session Writer** | **세션 집필** | **`premium-production`** or **`long-context-prod`** | **Opus/MiniMax** | **핵심 집필** |
| **A4C Material Aggregator** | **머지/보강** | **`long-context-prod`** | **MiniMax 2.5** | **전체 파일 한 번에 처리** |
| A5 Code Validator | 코드 검증 | `strict-gatekeeper` | Codex | 유지 |
| A6 Visualization Designer | 다이어그램 | `visual-creative` | Qwen | 유지 |
| A7 Learner Experience Designer | UX 설계 | **`long-context-prod`** | **MiniMax 2.5** | UX 플로우 설계 |
| A8 QA Editor | 톤 QA | `task-localization` | Sonnet | 유지 |
| A9 Instructor Support Designer | 강사 지원 | **`standard-production`** | **Sonnet** | 보조 콘텐츠 (Opus→Sonnet, 비용 절감) |
| A10 Differentiation Strategist | 차별화 전략 | **`standard-production`** | **Sonnet** | 전략 설계 (Qwen→Sonnet) |
| A11 Chart Specifier | 표/차트 | `visual-creative` | Qwen | (Opus→Qwen, 시각 설계) |

**P02 핵심 변경**:
- ✅ **A4B Session Writer**: Opus or MiniMax 2.5 선택 가능
  - Opus: 최고 품질 우선
  - MiniMax 2.5: 1M 컨텍스트로 전체 세션 한 번에 집필, 비용 절감
- ✅ **A4C Aggregator**: MiniMax 2.5 (1M로 다중 파일 머지)
- ❌ `deep-production-alt` (GLM-5) → ✅ `standard-production` (Sonnet)

---

### 2.3 P03 — Slide Generation (11 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| A0 Orchestrator | 슬라이드 총괄 | `orchestration-core` | Sonnet | 유지 |
| A1 Content Analyst | 교안 분석 | **`standard-production`** | **Sonnet** | 정확한 구조 분석 (creative→standard) |
| A2 Terminology Manager | 용어 관리 | `task-localization` | Sonnet | 유지 |
| A3 Slide Architect | 슬라이드 구조 | `visual-creative` | Qwen | 유지 |
| A4 Copywriter | 카피 작성 | **`standard-production`** | **Sonnet** | 교육 카피 정확성 (creative→standard) |
| A5 Code Validator | 코드 검증 | `strict-gatekeeper` | Codex | 유지 |
| A6 Lab Reproducibility | 실습 검증 | `strict-gatekeeper` | Codex | 유지 |
| A7 Visual Design Director | 시각 디자인 | `visual-creative` | Qwen | 유지 |
| A8 Copy Tone Editor | 톤 편집 | `task-localization` | Sonnet | 유지 |
| A9 QA Auditor | 최종 QA | `strict-gatekeeper` | Codex | 유지 |
| A10 Trace Citation Keeper | 출처 검증 | `strict-gatekeeper` | Codex | 유지 |

**P03 변경 요약**:
- ✅ A1, A4: `creative-research` → `standard-production` (정확성 중시)

---

### 2.4 P04 — Slide Prompt Generation (5 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| P0 Orchestrator | 프롬프트 총괄 | `orchestration-core` | Sonnet | 유지 |
| P1 Education Structurer | 교육 구조 | **`standard-production`** | **Sonnet** | 6섹션 설계 (GLM-5→Sonnet) |
| P2 Slide Prompt Architect | 슬라이드 명세 | **`premium-production`** | **Opus** | 정밀 명세 작성 |
| P3 Visual Spec Curator | 비주얼 스펙 | `visual-creative` | Qwen | (gatekeeper→visual) |
| P4 QA Auditor | 프롬프트 QA | `strict-gatekeeper` | Codex | 유지 |

**P04 변경 요약**:
- ✅ P1: `deep-production-alt` → `standard-production`
- ✅ P2: `gatekeeper` → `premium-production` (정밀 명세)
- ✅ P3: `gatekeeper` → `visual-creative` (시각 설계)

---

### 2.5 P05 — PPTX Conversion (6 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| B0 Orchestrator | PPTX 총괄 | `orchestration-core` | Sonnet | 유지 |
| B1 Slide Parser | MD→JSON 파싱 | `mechanical-pipeline` | Kimi | 유지 |
| B2 HTML Renderer | HTML 렌더링 | `mechanical-pipeline` | Kimi | 유지 |
| B3 Asset Generator | 에셋 생성 | `mechanical-pipeline` | Kimi | 유지 |
| B4 PPTX Assembler | PPTX 조립 | `mechanical-pipeline` | Kimi | 유지 |
| B5 Visual QA | 시각 QA | `strict-gatekeeper` | Codex | 유지 |

**P05**: ✅ 모두 적정 배정 (기계적 작업 = Kimi)

---

### 2.6 P06 — NanoBanana PPTX (6 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| C0 Orchestrator | NanoBanana 총괄 | `orchestration-core` | Sonnet | 유지 |
| C1 Content Planner | 콘텐츠 플랜 | `visual-creative` | Qwen | 유지 |
| C2 Prompt Engineer | 이미지 프롬프트 | `visual-creative` | Qwen | 유지 |
| C3 Image Generator | 이미지 생성 | **`long-context-prod`** | **MiniMax 2.5** | 이미지 생성 조율 |
| **C4 PPTX Builder** | **이미지→PPTX** | **`mechanical-pipeline`** | **Kimi** | **기계적 조립 (creative→mechanical)** |
| C5 Visual QA | 시각 QA | `strict-gatekeeper` | Codex | 유지 |

**P06 핵심 변경**:
- ✅ **C4 PPTX Builder**: `creative-research` → `mechanical-pipeline` (**비용 ~30배 절감**)

---

### 2.7 P07 — Manus Slide (6 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| D0 Orchestrator | Manus 총괄 | `orchestration-core` | Sonnet | 유지 |
| D1 Prompt Validator | 프롬프트 검증 | `strict-gatekeeper` | Codex | 유지 |
| **D2 Chunk Splitter** | **교시 분할** | **`mechanical-pipeline`** | **Kimi** | **규칙 기반 분할 (orchestration→mechanical)** |
| D3 Submission Manager | API 제출 | `mechanical-pipeline` | Kimi | 유지 |
| D4 Post Processor | PPTX 병합 | `mechanical-pipeline` | Kimi | 유지 |
| D5 Visual QA | 시각 QA | `strict-gatekeeper` | Codex | 유지 |

**P07 핵심 변경**:
- ✅ **D2 Chunk Splitter**: `orchestration-core` → `mechanical-pipeline` (**비용 ~30배 절감**)

---

### 2.8 P08 — Log Analysis (6 agents)

| 에이전트 | 역할 | **v2.0 카테고리** | 모델 | 변경 사유 |
|---------|------|------------------|------|----------|
| L0 Orchestrator | 로그 분석 총괄 | `orchestration-core` | Sonnet | 유지 |
| L1 Data Collector | 데이터 수집 | `mechanical-pipeline` | Kimi | 유지 |
| L2 Insight Analyst | 인사이트 분석 | **`standard-production`** | **Sonnet** | 패턴 분석 (GLM-5→Sonnet) |
| L3 Optimizer | 최적화 전략 | **`standard-production`** | **Sonnet** | 전략 수립 (GLM-5→Sonnet) |
| **L4 Report Writer** | **리포트 집필** | **`long-context-prod`** | **MiniMax 2.5** | **장문 리포트, 1M 컨텍스트** |
| L5 QA Auditor | QA 검증 | `strict-gatekeeper` | Codex | 유지 |

**P08 핵심 변경**:
- ✅ **L4 Report Writer**: `deep-production` → `long-context-prod` (MiniMax 2.5)
  - 장문 리포트 + 1M 컨텍스트로 다양한 로그 패턴 한 번에 분석
  - 비용 절감

---

## 3. MiniMax 2.5 적용 상세

### 3.1 적용 가능 에이전트 (11개)

| 에이전트 | 기존 모델 | v2.0 모델 | 기대 효과 |
|---------|----------|----------|----------|
| P01-A2 Instructional Designer | Opus | MiniMax 2.5 | 1M로 다양한 교수법 참고, 비용 ↓98% |
| **P02-A4B Session Writer** | Opus | **MiniMax 2.5** | **전체 세션 한 번에 집필, 비용 ↓98%** |
| **P02-A4C Material Aggregator** | Opus/Sonnet | **MiniMax 2.5** | **다중 파일 머지, 1M 컨텍스트** |
| P02-A7 Learner Experience Designer | Opus | MiniMax 2.5 | UX 플로우 설계, 비용 ↓98% |
| P02-A9 Instructor Support Designer | Opus/Sonnet | MiniMax 2.5 | 강사 가이드, 한국어 글쓰기 |
| P03-A4 Copywriter | Qwen→Opus | MiniMax 2.5 | 교육 카피, 창작성 + 정확성 |
| P04-P1 Education Structurer | GLM→Sonnet | MiniMax 2.5 | 6섹션 구조, 장문 처리 |
| P06-C1/C2 Image Prompt | Qwen | MiniMax 2.5 | 이미지 프롬프트 품질 향상 |
| **P08-L4 Report Writer** | Opus | **MiniMax 2.5** | **장문 로그 리포트, 1M 컨텍스트** |

### 3.2 MiniMax 2.5 vs 기존 모델 비교

| 항목 | Opus | MiniMax 2.5 | Sonnet |
|------|------|-------------|--------|
| **컨텍스트** | 200K | **1M** ✅ | 200K |
| **한국어** | 우수 | 우수 | 우수 |
| **추론** | 최고 | 우수 | 좋음 |
| **속도** | 중간 | 빠름 | 빠름 |
| **비용 (Input/Output per 1M)** | $15.00/$75.00 | **$0.30/$1.20** ✅ | $3.00/$15.00 |
| **창작성** | 좋음 | **우수** ✅ | 좋음 |

### 3.3 적용 시나리오

#### 시나리오 A: 품질 우선 (Opus 유지)
- P02-A4B Session Writer: Opus
- 목적: 최고 품질 교안

#### 시나리오 B: 비용-품질 균형 (MiniMax)
- P02-A4B Session Writer: MiniMax 2.5
- 목적: 1M 컨텍스트로 효율적 집필, 비용 절감

---

## 4. 비용 영향 분석

### 4.1 v1.0 → v2.0 변경 비용 비교

| 변경 유형 | 에이전트 수 | 예상 비용 변화 | 연간 절감/증가 |
|----------|------------|---------------|---------------|
| **GLM-5 → Sonnet** | 8개 | +50~80% | ~+$500 |
| **Qwen → Sonnet** | 4개 | +200% | ~+$800 |
| **Opus → MiniMax** | 5개 | **-98%** | **~-$2,900** ✅ |
| **Creative → Mechanical** | 2개 | **-95%** | **~-$300** ✅ |
| **Opus → Sonnet** | 2개 | -80% | ~-$600 ✅ |

### 4.2 총비용 영향

| 시나리오 | 연간 추정 비용 | 변화 |
|---------|---------------|------|
| v1.0 현재 | ~$5,000 | 기준 |
| v2.0 품질 우선 | ~$5,500 | +10% |
| **v2.0 균형형** | **~$2,500** | **-50%** ✅ |

### 4.3 품질-비용 최적 포인트

```
높은 품질
    ↑
    │    P02-A4B (Opus)
    │         │
    │    P01-A1 (Opus)
    │         │
    │    P02-A4B (MiniMax) ← 최적 포인트
    │         │
    │    P04-P2 (Opus)
    │         │
    └────┬────┘
       낮은 비용
```

---

## 5. 구현 가이드

### 5.1 `.opencode/oh-my-opencode.jsonc` 설정

```jsonc
{
  "categories": {
    "orchestration-core": {
      "model": "anthropic/claude-sonnet-4-6",
      "temperature": 0.3
    },
    "task-localization": {
      "model": "anthropic/claude-sonnet-4-6",
      "temperature": 0.2
    },
    "premium-production": {
      "model": "anthropic/claude-opus-4-6",
      "variant": "max",
      "temperature": 0.4
    },
    "long-context-prod": {
      "model": "opencode-go/minimax-2.5"
    },
    "visual-creative": {
      "model": "comet_qwen/qwen3.5-plus",
      "temperature": 0.7
    },
    "strict-gatekeeper": {
      "model": "openai/gpt-5.3-codex",
      "variant": "xhigh",
      "temperature": 0.1
    },
    "mechanical-pipeline": {
      "model": "opencode-go/kimi-k2.5",
      "temperature": 0.0
    },
    "standard-production": {
      "model": "anthropic/claude-sonnet-4-6",
      "temperature": 0.4
    }
  }
}
```

### 5.2 `.agent/AGENTS.md` 업데이트

```markdown
### P02 Writer (v2.0)

| Pipeline | 기본 카테고리 | 오버라이드 에이전트 | 카테고리 |
|----------|--------------|-------------------|---------|
| **P02** | `standard-production` | A4B Session Writer | `premium-production` or `long-context-prod` |
| | | A4C Material Aggregator | `long-context-prod` |
| | | A5 Code Validator | `strict-gatekeeper` |
| | | A6 Visualization Designer | `visual-creative` |
| | | A7 Learner Experience Designer | `long-context-prod` |
```

---

## 6. Migration Roadmap

### Phase 1: 긴급 변경 (즉시)
- [ ] `deep-production-alt` (GLM-5) → `standard-production` (Sonnet)
- [ ] `creative-research` → `mechanical-pipeline` (C4, D2)

### Phase 2: MiniMax 도입 (1주차)
- [ ] MiniMax 2.5 API 키 설정
- [ ] P02-A4C (Aggregator) MiniMax 적용
- [ ] P08-L4 (Report Writer) MiniMax 적용

### Phase 3: 품질 검증 (2주차)
- [ ] P02-A4B (Session Writer) MiniMax vs Opus A/B 테스트
- [ ] P01-A2 (Instructional Designer) MiniMax 검증

### Phase 4: 완전 전환 (3주차)
- [ ] 검증된 MiniMax 적용 확대
- [ ] 모니터링 및 비용 트래킱

---

## 7. 체크리스트

### v2.0 적용 전 확인사항

- [ ] MiniMax 2.5 API 키 확보
- [ ] `.opencode/oh-my-opencode.jsonc` 백업
- [ ] `.agent/AGENTS.md` 백업
- [ ] 각 Pipeline 테스트 실행 계획
- [ ] 롤백 절차 문서화

### 검증 항목

- [ ] P02-A4B Session Writer 품질 유지
- [ ] P02-A4C Aggregator 1M 컨텍스트 정상 작동
- [ ] P08-L4 Report Writer 장문 출력 검증
- [ ] 한국어 품질 체크 (MiniMax)
- [ ] 비용 모니터링 설정

---

## 8. 부록: 모델 비교표

| 모델 | 컨텍스트 | 한국어 | 추론 | Input $/1M | Output $/1M | 적합 카테고리 |
|------|---------|--------|------|-----------|------------|-------------|
| `claude-opus-4-6` | 200K | ★★★★★ | ★★★★★ | $15.00 | $75.00 | premium-production |
| `minimax-m2.5` | **1M** | ★★★★☆ | ★★★★☆ | **$0.30** | **$1.20** | long-context-prod |
| `claude-sonnet-4-6` | 200K | ★★★★★ | ★★★☆☆ | $3.00 | $15.00 | orchestration, task, standard |
| `gpt-5.3-codex` | 400K | ★★★☆☆ | ★★★★★ | $1.75 | $14.00 | strict-gatekeeper |
| `qwen3.5-plus` | 1M | ★★★☆☆ | ★★★★☆ | ~$0.40 | ~$2.40 | visual-creative |
| `kimi-k2.5` | 262K | ★★★☆☆ | ★★★★☆ | $0.60 | $2.50 | mechanical-pipeline |

> **퇴역 모델**: `glm-5` (744B/40B active) — Input $0.80/1M, Output $2.56/1M, 200K context, Intelligence Index 50, Agentic Index 63  
> 퇴역 사유: 한국어 품질 미검증. 배정된 모든 에이전트가 한국어 출력을 요구하므로 `standard-production` (Sonnet)으로 전환.

---

**문서 이력**:
- v1.0 (2025-03-06): 초안 작성 (agent-llm-mappings.md)
- v2.0 (2025-03-06): MiniMax 2.5 통합, 카테고리 재설계, 비용 분석 추가
- **v2.1 (2026-03-06)**: 리서치 기반 가격 수정, Provider ID 교정, GLM-5 실사양 추가
