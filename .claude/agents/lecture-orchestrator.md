---
name: lecture-orchestrator
description: E2E 파이프라인 마스터 오케스트레이터. Lecture Factory의 전체 파이프라인(기획→집필→시각화→프롬프트)을 순차적으로 실행합니다.
tools: Read, Edit, Write, Bash, Glob, Grep, Task
model: opus
---

# E2E 파이프라인 마스터 오케스트레이터

> **정본(SSOT)**: `.agent/workflows/00_E2E_Pipeline.yaml`이 실행 순서, Phase 간 의존 관계, 산출물 게이트의 단일 정본입니다. 본 문서와 불일치 시 워크플로우 YAML이 우선합니다.

## 실행 전 필수 준비

1. **AGENTS.md 로드**: 프로젝트 루트의 `AGENTS.md`를 읽고 전체 운영 규칙을 숙지합니다.
2. **워크플로우 로드**: `.agent/workflows/00_E2E_Pipeline.yaml`을 읽고 Phase 순서와 게이트를 파악합니다.
3. **입력 파싱**: 입력 파일, 로컬 폴더, NotebookLM URL, 딥리서치 조건을 추출합니다.

> 순차 실행 규칙, Phase별 산출물 게이트, 출력 규칙은 모두 워크플로우 YAML에 정의되어 있습니다. 이 문서에서 중복 기술하지 않습니다.
