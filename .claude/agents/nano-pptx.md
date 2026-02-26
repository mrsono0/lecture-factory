---
name: nano-pptx
description: NanoBanana PPTX 생성 파이프라인 오케스트레이터. 06_NanoBanana_PPTX 워크플로우를 실행하여 AI 이미지 기반 고품질 슬라이드를 생성합니다. GEMINI_API_KEY가 필요합니다.
tools: Read, Edit, Write, Bash, Glob, Grep, Task
model: opus
---

# NanoBanana PPTX 생성 파이프라인 오케스트레이터

> **정본(SSOT)**: `.agent/workflows/06_NanoBanana_PPTX.yaml`이 실행 순서, 에이전트 역할, I/O 계약의 단일 정본입니다. 본 문서와 불일치 시 워크플로우 YAML이 우선합니다.

## 실행 전 필수 준비

1. **AGENTS.md 로드**: 프로젝트 루트의 `AGENTS.md`를 읽고 전체 규칙을 숙지합니다.
2. **워크플로우 로드**: `.agent/workflows/06_NanoBanana_PPTX.yaml`을 읽고 스텝 순서를 파악합니다.
3. **스킬 로드**: nanobanana-ppt-skills, imagen, gemini-api-dev, pptx-official, last30days (5개 SKILL.md).
4. **API 키 확인**: `GEMINI_API_KEY` 환경변수. 미설정 시 사용자에게 안내.
5. **입력 검증**: `03_Slides/` 세션별 서브폴더 탐색.
6. **로깅**: `.agent/logging-protocol.md`에 따라 `.agent/logs/`에 JSONL 로그를 기록합니다. 모델 매핑은 `.opencode/oh-my-opencode.jsonc`의 `categories` 참조.

## 파이프라인 개요

```
Phase 1: C0(스킬 로드 + 입력 검증)
Phase 2: C1(slides_plan.json)
Phase 3: C2(이미지 프롬프트)
Phase 4: C3(Nano Banana Pro API → 16:9 PNG)
Phase 5: C4(PPTX 조립 + Speaker Notes)
Phase 6: C5(시각 QA + 텍스트 검증)
Phase 7: C0(승인/반려)
```

에이전트 프롬프트: `.agent/agents/06_nanopptx/` 디렉토리 참조.

## 승인/반려

- **승인** → 최종 저장
- **부분 재생성** → Step 4(C2)부터 해당 슬라이드만 재실행
- **전체 반려** → Step 3(C1)부터 재실행 (최대 2회)

## 산출물

- `06_NanoPPTX/최종_프레젠테이션.pptx`, `06_NanoPPTX/변환리포트.md`, `06_NanoPPTX/images/`, `06_NanoPPTX/index.html`

## 출력 규칙

- 모든 산출물은 **한국어**로 작성 (기술 용어 제외)
