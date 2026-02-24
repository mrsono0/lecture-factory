# Gemini 최적화 Lecture Factory v2 구현 가이드

## 개요

이 문서는 Lecture Factory의 01_Lecture_Planning 및 02_Material_Writing 워크플로우를 Gemini 3.1 Pro에 최적화하기 위한 새로운 아키텍처에 대한 구현 가이드입니다.

## 배경

### 기존 시스템의 한계
- **출력 토큰 제한**: AI 모델은 한 번에 3,000~4,500자 이상의 고품질 장문 생성에 어려움
- **압축 편향**: 대규모 언어 모델은 정보를 핵심 위주로 요약하려는 경향
- **문맥 집중도 분산**: 한 번에 많은 세션을 처리하면 디테일 품질 저하

### 해결 방안: 마이크로 세션 청킹 (Micro-Session Chunking)
- **15~25분 단위 분할**: 최적의 출력 토큰 범위 (3,000~4,500자)
- **단일 개념 집중**: 각 세션은 단 1개의 핵심 학습 목표만 다룸
- **개별 파일화**: 검색/수정/병렬 처리가 용이한 구조

---

## 새로운 워크플로우 아키텍처

### 01_Lecture_Planning_v2

#### 핵심 변경사항

| 구성요소 | 기존 (v1) | 새로운 (v2) |
|---------|----------|------------|
| 세션 단위 | 60~90분 | **15~25분** |
| 출력 파일 | 단일 강의구성안.md | **마이크로 세션별 개별 파일 + 통합 인덱스** |
| 세분화 | AM/PM 4시간 | **15-25분 Chunk 기반** |

#### 새로운 에이전트

**A3B_MicroSession_Specifier**
- 역할: 기존 세션을 15~25분 마이크로 세션으로 세분화
- 출력: `01_Planning/micro_sessions/세션-{번호}-{제목}.md`
- 태그: chunk_type (narrative|code|diagram|lab), complexity, estimated_chars

**A3C_Session_Indexer**
- 역할: 마이크로 세션 간 의존성 그래프 및 학습 경로 설계
- 출력: 
  - `_index.json`: 전체 세션 메타데이터
  - `_flow.md`: 학습 흐름 문서
  - `_dependency.mmd`: Mermaid 의존성 그래프

#### 출력 파일 구조

```
01_Planning/
├── 강의구성안.md (통합본 - 기존 형식 유지)
├── micro_sessions/
│   ├── _index.json (세션 메타데이터 인덱스)
│   ├── _flow.md (학습 흐름 문서)
│   ├── _dependency.mmd (Mermaid 의존성 그래프)
│   ├── 세션-001-오리엔테이션.md
│   ├── 세션-002-환경구축.md
│   └── ...
```

### 02_Material_Writing_v2

#### 핵심 변경사항

| 구성요소 | 기존 (v1) | 새로운 (v2) |
|---------|----------|------------|
| 집필 방식 | 단일 파일 집필 | **세션별 개별 집필 → 취합** |
| 병렬 처리 | Phase 3 (5개 에이전트) | **세션 단위 병렬 집필** |
| 시각화 | Mermaid 중심 | **표 + 흐름도 + 구조화 강화** |

#### 새로운 에이전트

**A4B_Session_Writer**
- 역할: 단일 마이크로 세션의 완전한 교안 작성
- 모델: Gemini 3.1 Pro (micro-writing 카테고리)
- 출력: `02_Material/sessions/세션-{번호}-{제목}_v1.0.md`
- 분량: 3,000~4,500자 (공백 포함)

**A4C_Material_Aggregator**
- 역할: 개별 세션 교안들을 검증하고 통합
- 입력: 모든 세션 파일 + 의존성 그래프
- 출력: `02_Material/강의교안_v1.0.md` (통합본)

**A11_Chart_Specifier**
- 역할: 표(Tables) 및 Mermaid 다이어그램 설계
- 출력: `02_Material/visual_specs/session_{번호}_tables.md`

#### 출력 파일 구조

```
02_Material/
├── 강의교안_v1.0.md (통합된 최종 교안)
├── sessions/
│   ├── 세션-001-{제목}_v1.0.md
│   ├── 세션-002-{제목}_v1.0.md
│   └── ...
├── visual_specs/
│   ├── session_001_tables.md
│   ├── session_002_tables.md
│   └── ...
└── src/ (코드 예제 모음)
```

---

## 모델 설정 업데이트

### .opencode/oh-my-opencode.jsonc

새로운 카테고리 추가:

```jsonc
// NEW: Micro Session Chunking - 15~25min session design
"curriculum-chunking": {
  "model": "google/antigravity-gemini-3.1-pro",
  "variant": "high",
  "prompt_append": "You are designing MICRO-SESSIONS (15-25min chunks)..."
},

// NEW: Micro Session Writing - Individual session material
"micro-writing": {
  "model": "google/antigravity-gemini-3.1-pro",
  "variant": "high",
  "prompt_append": "You are writing a SINGLE micro-session (15-25min)..."
}
```

---

## 마이크로 세션 명세서 템플릿

### 메타 정보
```markdown
# 마이크로 세션: {번호}-{제목}

## 📋 메타 정보
| 항목 | 값 |
|------|-----|
| **세션 ID** | MS-{코스ID}-{번호:03d} |
| **소요 시간** | {15|20|25}분 |
| **예상 교안 분량** | {3,000|4,000|4,500}자 |
| **선행 세션** | 세션-{번호} ({필수|권장}) |
| **후행 세션** | 세션-{번호} |
| **핵심 키워드** | 키워드1, 키워드2, 키워드3 |
| **난이도** | {low|medium|high} |
| **청크 타입** | {narrative|code|diagram|lab} |
```

### Gemini 최적화 태그
```yaml
gemini_optimized:
  chunk_type: {narrative|code|diagram|lab}
  complexity: {low|medium|high}
  estimated_chars: {3000|4000|4500}
  output_style: continuous_prose
  tone: friendly_spoken_korean
  include:
    - instructor_script: true
    - lab_guide: {true|false}
    - analogy: detailed_situation
    - mermaid_diagram: {true|false}
  prerequisites:
    mandatory: [{세션_번호_목록}]
    recommended: [{세션_번호_목록}]
```

---

## 청크 타입별 설계 가이드

### narrative (개념 설명형)
- **목적**: 이론적 개념, 원리, 철학적 배경
- **비중**: 비유 40% + 설명 60%
- **코드**: 없거나 5줄 이하 예시
- **시각화**: 비교 표, mindmap

### code (코드 중심형)
- **목적**: 구문, 패턴, 알고리즘 학습
- **비중**: 설명 30% + 코드 50% + 해설 20%
- **코드**: 20~50줄, PEP 8 준수
- **시각화**: 순서도, 블록 다이어그램

### diagram (시각화 중심형)
- **목적**: 구조, 흐름, 관계 이해
- **비중**: 설명 40% + 다이어그램 40% + 해설 20%
- **산출물**: Mermaid 다이어그램 필수
- **시각화**: 아키텍처, 시퀀스, 클래스 다이어그램

### lab (실습 중심형)
- **목적**: hands-on 경험, 실제 동작 확인
- **비중**: 설명 20% + 실습 70% + 정리 10%
- **산출물**: 🎙️ 실습 가이드 대본 상세
- **시각화**: 단계별 표, 체크리스트, Gantt 차트

---

## 서술의 흐름 (Expansion Framework)

모든 교안은 다음 5단계 구조로 작성:

### ① 도입 (Hook) - 300~500자
- 선행 세션 내용 환기 (2~3문장)
- 오늘 배울 개념의 필요성 제시
- 학습자의 흥미 유발

### ② 비유 풀이 (Analogy) - 800~1,200자
- 'AI 시대의 서사' 톤의 구체적 상황극
- 일상적 비유를 디테일하게 묘사
- 개념과 비유의 매칭을 자연스럽게 설명

### ③ 개념 설명 (What) - 800~1,000자
- 정확한 기술 정의
- 핵심 포인트를 단계별로 설명
- 학습자가 속으로 궁금해할 만한 질문 자체 제기 및 답변

### ④ 코드/실제 활용 (How) - 600~1,000자
- 코드를 제시하고 한 줄씩 구두로 해설
- 예시를 통해 실제 활용법 설명
- 체크포인트 질문 포함

### ⑤ 정리 및 다음 세션 예고 (Closing) - 200~300자
- 핵심 요약
- 다음 마이크로 세션과의 연결성 명시
- 브릿지 노트

---

## 품질 기준

### 절대 금지
- ❌ 단일 마이크로 세션에 2개 이상의 개념 포함
- ❌ 예상 분량이 4,500자를 초과하는 설계
- ❌ 선행 세션 없이 독립적인 복잡한 개념 설계
- ❌ 개조식 요약만 있는 명세서/교안
- ❌ 중간에 끊어지는 출력

### 반드시 준수
- ✅ 단 1개의 핵심 학습 목표
- ✅ 15~25분 시간 범위
- ✅ 공백 포함 3,000~4,500자 분량
- ✅ chunk_type, complexity 태그 부여
- ✅ 선행/후행 세션 명확한 연결
- ✅ 'AI 시대의 서사' 톤의 비유와 스토리텔링
- ✅ 🗣️ 강사 대본 + 🎙️ 실습 가이드 포함

---

## 다운스트림 파이프라인 연동

### 03_Visualizer (슬라이드 생성)
- 입력: `02_Material/sessions/세션-*.md`
- 처리: 세션별로 개별 슬라이드 스토리보드 생성

### 04_Prompt_Generator (슬라이드 프롬프트)
- 입력: `02_Material/sessions/세션-*.md`
- 출력: 세션별 개별 프롬프트 파일

### 05_PPTX_Converter / 06_NanoBanana / 07_ManusSlide
- 입력: 마이크로 세션별 개별 처리 가능
- 병렬 처리: 세션별 동시 변환 후 취합

---

## 구현 체크리스트

### 1단계: 에이전트 프롬프트 작성
- [x] A3B_MicroSession_Specifier.md
- [x] A3C_Session_Indexer.md
- [x] A4B_Session_Writer.md
- [x] A4C_Material_Aggregator.md
- [x] A11_Chart_Specifier.md

### 2단계: 워크플로우 파일 생성
- [x] 01_Lecture_Planning_v2.yaml
- [x] 02_Material_Writing_v2.yaml

### 3단계: 모델 설정 업데이트
- [x] oh-my-opencode.jsonc (curriculum-chunking, micro-writing 카테고리 추가)

### 4단계: 테스트 및 검증
- [ ] 샘플 강의로 end-to-end 테스트
- [ ] 출력 토큰 분량 검증
- [ ] 의존성 그래프 정확성 확인
- [ ] 통합 교안 완결성 검증

### 5단계: 문서화
- [x] 구현 가이드 작성
- [ ] 사용 매뉴얼 작성
- [ ] 트러블슈팅 가이드 작성

---

## 향후 개선 방향

### 단기 (1~2개월)
- [ ] 마이크로 세션 자동 분할 알고리즘 개선
- [ ] 세션 의존성 자동 감지 기능
- [ ] Gemini API rate limit 대응 로직

### 중기 (3~6개월)
- [ ] A/B 테스트: v1 vs v2 품질 비교
- [ ] 학습자 피드백 기반 세션 재설계
- [ ] 다국어 지원 (영어, 일본어 등)

### 장기 (6개월+)
- [ ] AI 기반 세션 난이도 자동 조정
- [ ] 개인화된 학습 경로 생성
- [ ] 실시간 강의 편집 및 업데이트

---

## 참고 자료

- [Gemini 3.1 Pro Documentation](https://ai.google.dev/gemini-api/docs)
- [Lecture Factory AGENTS.md](/AGENTS.md)
- [기존 01_Lecture_Planning.yaml](/.agent/workflows/01_Lecture_Planning.yaml)
- [기존 02_Material_Writing.yaml](/.agent/workflows/02_Material_Writing.yaml)

---

*작성일: 2026-02-24*  
*버전: v2.0*  
*작성자: Sisyphus (Gemini-optimized Lecture Factory Architecture)*
