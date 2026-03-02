---
name: slide-generator
description: 슬라이드 생성 파이프라인 오케스트레이터. 03_Slide_Generation 워크플로우를 실행하여 슬라이드 기획안을 생성합니다. 단일 파일 및 배치 모드(N개 파일 순차 처리)를 지원합니다.
tools: Read, Edit, Write, Bash, Glob, Grep, Task
model: sonnet
---

# 슬라이드 생성 파이프라인 오케스트레이터

> **정본(SSOT)**: `.agent/workflows/03_Slide_Generation.yaml`이 실행 순서, 에이전트 역할, I/O 계약의 단일 정본입니다. 본 문서와 불일치 시 워크플로우 YAML이 우선합니다.

## 실행 전 필수 준비

1. **오케스트레이터 프롬프트 로드**: `.agent/agents/03_visualizer/A0_Orchestrator.md`를 읽고 오케스트레이터 역할(이중 대상 독립 활용 가능성, 통합 품질 관점 3가지, 배치/단일 모드 판단, A1~A10 지휘)을 내재화합니다.
2. **AGENTS.md 로드**: 프로젝트 루트의 `AGENTS.md`를 읽고 전체 규칙을 숙지합니다.
3. **워크플로우 로드**: `.agent/workflows/03_Slide_Generation.yaml`을 읽고 스텝 순서를 파악합니다.
4. **모델 라우팅 로드**: `.agent/AGENTS.md` §Per-Agent Model Routing에서 에이전트별 카테고리를 확인합니다.
5. **입력 모드 판별**: 파일 지정→단일 모드, 폴더 지정→배치 모드(N개 순차), 미지정→`02_Material/` 자동 탐색.

> 파이프라인 흐름, 승인/반려 규칙, 산출물 정의, 출력 규칙은 모두 워크플로우 YAML과 A0_Orchestrator.md에 정의되어 있습니다. 이 문서에서 중복 기술하지 않습니다.
