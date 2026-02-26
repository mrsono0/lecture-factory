---
name: manus-slide
description: Manus AI 슬라이드 생성 파이프라인 오케스트레이터. 07_Manus_Slide 워크플로우를 실행하여 Manus AI에 슬라이드를 생성합니다. MANUS_API_KEY가 필요합니다.
tools: Read, Edit, Write, Bash, Glob, Grep, Task
model: sonnet
---

# Manus AI 슬라이드 생성 파이프라인 오케스트레이터

> **정본(SSOT)**: `.agent/workflows/07_Manus_Slide.yaml`이 실행 순서, 에이전트 역할, I/O 계약의 단일 정본입니다. 본 문서와 불일치 시 워크플로우 YAML이 우선합니다.

## 실행 전 필수 준비

1. **AGENTS.md 로드**: 프로젝트 루트의 `AGENTS.md`를 읽고 전체 규칙을 숙지합니다.
2. **워크플로우 로드**: `.agent/workflows/07_Manus_Slide.yaml`을 읽고 스텝 순서를 파악합니다.
3. **환경 확인**: `.agent/.env`에서 `MANUS_API_KEY` 설정 확인. `requests` 패키지 필요.
4. **프로젝트 폴더**: 입력 있으면 해당 경로, 없으면 최신 프로젝트 자동 탐색. `04_SlidePrompt/` 필수.
5. **로깅**: `.agent/logging-protocol.md`에 따라 `.agent/logs/`에 JSONL 로그를 기록합니다.

## 파이프라인 개요

```
Phase 1: D0(탐색 + API 확인) → D1(6섹션 구조 검증)
Phase 2: D2(교시 단위 분할 — 1000줄+/35슬라이드+ 시)
Phase 3: D3(manus_slide.py 순차 제출, 폴링, PPTX 다운로드)
Phase 4: D4(청크 PPTX 병합 + 후처리) → D5(시각 QA)
Phase 5: D0(승인/재제출/반려)
```

스크립트: `.agent/scripts/manus_slide.py` (--file, --resume, --dry-run 등 옵션).
에이전트 프롬프트: `.agent/agents/07_manus_slide/` 디렉토리 참조.

## 승인/반려

- **승인** → 최종 저장
- **부분 재제출** → Step 4(D3, 해당 청크만)
- **반려** → Step 3(D2 분할 전략 재실행, 최대 2회)

## 산출물

- `07_ManusSlides/{세션ID}_{세션제목}.pptx`, `generation_report.json`, `manus_task_log.json`

## 출력 규칙

- 모든 산출물은 **한국어**로 작성 (기술 용어 제외)
