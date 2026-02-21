---
name: flowith-kb
description: "Flowith Knowledge Garden API를 통한 지식 베이스 검색. 업로드된 문서/자료 기반으로 RAG 검색 수행. 강의 참고자료 분석, 팩트 검증, 심층 질의응답에 활용."
model: opus
version: "1.0"
---

# Flowith Knowledge Garden 검색 스킬

Flowith Knowledge Garden에 업로드된 지식 베이스에서 RAG 기반 검색을 수행합니다.

## When to Use

- 강의 참고자료에서 특정 개념/팩트를 검색할 때
- 업로드된 문서 기반으로 질의응답이 필요할 때
- 팩트 검증이 필요할 때 (A1 Source Miner, A2 Traceability Curator)
- 심층 리서치에서 1차 소스로 활용할 때

## Requirements

- `FLOWITH_API_TOKEN`: Flowith API 인증 토큰 (필수)
- `FLOWITH_KB_LIST`: 검색할 지식 베이스 ID 목록 (필수, 쉼표 구분)
- `FLOWITH_MODEL`: 사용할 LLM 모델 (기본값: `claude-opus-4.6`)

## Setup

1. [Flowith](https://flowith.io) 계정에서 Knowledge Garden 생성
2. 참고자료 업로드 (PDF, 문서 등)
3. API 토큰 발급
4. Knowledge Base ID 확인
5. `.agent/.env`에 환경변수 설정:
   ```
   FLOWITH_API_TOKEN="your_flowith_token_here"
   FLOWITH_KB_LIST="kb_id_1,kb_id_2"
   FLOWITH_MODEL="claude-opus-4.6"
   ```

## API Reference

### 엔드포인트

| API | Method | URL | 비고 |
|-----|--------|-----|------|
| 지식 검색 | POST | `https://edge.flowith.net/external/use/knowledge-base/seek` | 핵심 API |
| 모델 목록 | GET | `https://edge.flowith.net/external/use/knowledge-base/models` | 공식 문서와 경로 다름 (실제 작동 확인) |
| ~~KB 목록 조회~~ | - | - | **미지원** — KB ID는 Flowith 웹 대시보드에서 수동 확인 필요 |

> **주의**: 공식 문서의 모델 목록 경로(`/seek-knowledge/models`)는 404를 반환합니다. 실제 작동 경로는 `/knowledge-base/models`입니다.

### Rate Limit

- **12 RPM** (분당 12회 요청)
- 초과 시 HTTP 429 반환
- Flowith Credits 차감 과금

---

## 사용법

### 1. 지식 베이스 검색 (Non-Streaming)

```bash
curl -s -X POST "https://edge.flowith.net/external/use/knowledge-base/seek" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Host: edge.flowith.net" \
  -d '{
    "messages": [
      {"role": "user", "content": "<검색 질의>"}
    ],
    "model": "'"${FLOWITH_MODEL:-claude-opus-4.6}"'",
    "stream": false,
    "kb_list": ["'"$FLOWITH_KB_ID"'"]
  }'
```

**응답 형식** (stream=false):
```json
{
  "tag": "final",
  "content": "검색 결과 텍스트..."
}
```

### 2. 지식 베이스 검색 (Streaming)

```bash
curl -s -X POST "https://edge.flowith.net/external/use/knowledge-base/seek" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Host: edge.flowith.net" \
  -d '{
    "messages": [
      {"role": "user", "content": "<검색 질의>"}
    ],
    "model": "'"${FLOWITH_MODEL:-claude-opus-4.6}"'",
    "stream": true,
    "kb_list": ["'"$FLOWITH_KB_ID"'"]
  }'
```

**스트리밍 응답 태그**:
| Tag | 의미 | content 형태 |
|-----|------|-------------|
| `searching` | 검색 진행 중 | 진행 상황 텍스트 |
| `seeds` | 중간 검색 결과 | JSON 배열 (`id`, `tokens`, `content`, `source_title` 등) |
| `final` | 최종 결과 | 완성된 응답 텍스트 |

### 3. 사용 가능 모델 확인

```bash
curl -s -X GET "https://edge.flowith.net/external/use/seek-knowledge/models" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Host: edge.flowith.net"
```

### 4. 다중 턴 대화 (컨텍스트 유지)

```bash
curl -s -X POST "https://edge.flowith.net/external/use/knowledge-base/seek" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Host: edge.flowith.net" \
  -d '{
    "messages": [
      {"role": "user", "content": "파이썬 변수의 정의를 알려줘"},
      {"role": "assistant", "content": "변수는 데이터를 저장하는 이름 붙은 공간입니다..."},
      {"role": "user", "content": "그러면 타입 변환은 어떻게 하나요?"}
    ],
    "model": "'"${FLOWITH_MODEL:-claude-opus-4.6}"'",
    "stream": false,
    "kb_list": ["'"$FLOWITH_KB_ID"'"]
  }'
```

---

## 실전 활용 패턴

### 패턴 A: 단일 질의 검색

교안 작성 중 특정 개념을 참고자료에서 확인할 때:

```bash
# 환경변수 로드
source .agent/.env

# 검색 실행
RESULT=$(curl -s -X POST "https://edge.flowith.net/external/use/knowledge-base/seek" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Host: edge.flowith.net" \
  -d '{
    "messages": [{"role": "user", "content": "AI 시대의 서사에서 변수를 설명할 때 사용한 비유는 무엇인가?"}],
    "model": "claude-opus-4.6",
    "stream": false,
    "kb_list": ["'$FLOWITH_KB_ID_1'"]
  }')

echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['content'])"
```

### 패턴 B: 복수 KB 동시 검색

여러 지식 베이스를 동시에 검색할 때:

```bash
curl -s -X POST "https://edge.flowith.net/external/use/knowledge-base/seek" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Host: edge.flowith.net" \
  -d '{
    "messages": [{"role": "user", "content": "객체지향 프로그래밍의 캡슐화 개념을 설명해줘"}],
    "model": "claude-opus-4.6",
    "stream": false,
    "kb_list": ["'$FLOWITH_KB_ID_1'", "'$FLOWITH_KB_ID_2'"]
  }'
```

### 패턴 C: seeds 활용 (출처 추적)

스트리밍 모드에서 `seeds` 태그로 원본 출처를 확인할 때:

```bash
curl -s -X POST "https://edge.flowith.net/external/use/knowledge-base/seek" \
  -H "Authorization: Bearer $FLOWITH_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Host: edge.flowith.net" \
  -d '{
    "messages": [{"role": "user", "content": "Antigravity IDE의 3-Surface 아키텍처란?"}],
    "model": "claude-opus-4.6",
    "stream": true,
    "kb_list": ["'$FLOWITH_KB_ID_1'"]
  }' 2>/dev/null | grep '"seeds"' | head -1
```

`seeds` 응답의 각 항목 구조:
```json
{
  "id": "chunk_id",
  "tokens": 150,
  "content": "원본 텍스트 청크...",
  "order": 1,
  "source_id": "doc_id",
  "source_title": "문서 제목",
  "nip": 0.95
}
```

---

## Lecture Factory 워크플로우 연동

### A1 Source Miner에서 활용

팩트 패킷 추출 시 로컬 참고자료가 부족할 때 Flowith KB를 2차 소스로 활용:

```
[Step 1] 로컬 참고자료 분석 → 부족 판단
    ↓
[Step 2] Flowith KB 검색 (이 스킬)
    ↓
[Step 3] 딥리서치 (deep-research 스킬) — 여전히 부족할 때만
```

### A2 Traceability Curator에서 활용

출처 검증 시 `seeds` 태그의 `source_title`과 `content`로 원본 추적:

```
검색 결과의 seeds → source_title로 원본 문서 식별
                  → content로 인용 텍스트 확인
                  → nip(관련도 점수)로 신뢰도 판단
```

---

## Troubleshooting

| 증상 | 원인 | 해결 |
|------|------|------|
| HTTP 401 | 토큰 만료/잘못됨 | `FLOWITH_API_TOKEN` 재발급 |
| HTTP 429 | Rate limit 초과 (12 RPM) | 5초 대기 후 재시도 |
| 빈 content | KB에 관련 내용 없음 | 질의 재구성 또는 다른 KB 지정 |
| `kb_list` 오류 | KB ID 잘못됨 | Flowith 대시보드에서 ID 재확인 |

## Related Skills

- deep-research: 웹 전체 심층 리서치 (Flowith KB에 없는 정보)
- tavily-web: 웹 검색 (실시간 정보)
- context7-auto-research: 라이브러리/프레임워크 공식 문서
- firecrawl-scraper: 특정 웹페이지 구조화 데이터 추출
