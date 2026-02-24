#!/usr/bin/env python3
"""
A4C Material Aggregator — Assembles 106 micro-session files into unified 강의교안_v2.0.md
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

BASE = Path(
    "/Users/mrsono0/Obsidian Vault/0 리서치/_lecture-factory/2026-02-18_AI-native_파이썬기초"
)
SESSIONS_DIR = BASE / "02_Material" / "sessions"
PLANNING_DIR = BASE / "01_Planning" / "micro_sessions"
MATERIAL_DIR = BASE / "02_Material"
OUTPUT = MATERIAL_DIR / "강의교안_v2.0.md"

# Load index
with open(PLANNING_DIR / "_index.json", encoding="utf-8") as f:
    index = json.load(f)

sessions_meta = {s["number"]: s for s in index["sessions"]}

# Load dependency graph
dep_graph = (PLANNING_DIR / "_dependency.mmd").read_text(encoding="utf-8")

# Load visualization packet
viz_packet = (MATERIAL_DIR / "visualization_packet.md").read_text(encoding="utf-8")

# Load visual specs (tables) per day
visual_specs = {}
for day in range(1, 6):
    spec_file = MATERIAL_DIR / "visual_specs" / f"day{day}_tables.md"
    if spec_file.exists():
        visual_specs[day] = spec_file.read_text(encoding="utf-8")

# Day themes
DAY_THEMES = {
    1: "AI 도구 탐험과 개발 환경 구축",
    2: "프롬프트 엔지니어링과 요구사항 분석",
    3: "파이썬 문법 기초와 데이터 다루기",
    4: "절차적에서 구조적 프로그래밍으로",
    5: "객체지향 프로그래밍과 과정 마무리",
}

DAY_RANGES = {1: (1, 22), 2: (23, 43), 3: (44, 64), 4: (65, 85), 5: (86, 106)}

# Collect session files sorted by number
session_files = {}
for f in sorted(SESSIONS_DIR.glob("세션-*_v1.0.md")):
    match = re.search(r"세션-(\d{3})", f.name)
    if match:
        num = int(match.group(1))
        session_files[num] = f


# Bridge note templates
def bridge_note(
    current_num, current_title, next_num, next_title, prev_num=None, prev_title=None
):
    lines = []
    if prev_num:
        lines.append(
            f"> 🔗 **이전 세션**: [세션 {prev_num:03d}: {prev_title}](#세션-{prev_num:03d})에서 배운 내용을 이어갑니다."
        )
    if next_num:
        lines.append(
            f"> 🔗 **다음 세션**: [세션 {next_num:03d}: {next_title}](#세션-{next_num:03d})에서 계속됩니다."
        )
    return "\n".join(lines)


# Build document
parts = []

# === HEADER ===
parts.append(f"""# AI-native 파이썬기초 — 강의교안 v2.0

> **버전**: 2.0
> **총 세션 수**: 106개 마이크로 세션
> **총 예상 시간**: 2,305분 (38시간 25분)
> **교육 기간**: 5일 (하루 8시간, 09:00~18:00)
> **작성 일시**: {datetime.now().strftime("%Y-%m-%d")}
> **작성 방식**: 3-Source Mandatory 팩트 패킷 기반 마이크로 세션 청킹
> **대상**: 비전공자 (AI와 협업하는 방식으로 학습)
> **도구**: Windows 11, Antigravity IDE, Gemini 3 Pro, uv 패키지 매니저

---
""")

# === TOC ===
parts.append("## 📋 목차 및 네비게이션\n")
parts.append("### 전체 세션 인덱스\n")
parts.append("| 세션 | 제목 | 시간 | 청크 타입 | 난이도 | 바로가기 |")
parts.append("|------|------|------|-----------|--------|----------|")

chunk_emoji = {"narrative": "📖", "code": "💻", "lab": "🧪"}
for num in sorted(sessions_meta.keys()):
    meta = sessions_meta[num]
    emoji = chunk_emoji.get(meta["chunk_type"], "📝")
    parts.append(
        f"| {num:03d} | {meta['title']} | {meta['duration_min']}분 | {emoji} {meta['chunk_type']} | {meta['complexity']} | [바로가기](#세션-{num:03d}) |"
    )

parts.append("")

# === DAY SCHEDULE ===
parts.append("### 일자별 진행표\n")
for day in range(1, 6):
    start, end = DAY_RANGES[day]
    duration = index["statistics"]["duration_per_day_minutes"][str(day)]
    parts.append(f"**Day {day}: {DAY_THEMES[day]}** ({duration}분)")

    # Morning sessions (roughly first half)
    mid = start + (end - start) // 2
    am_sessions = [f"{n:03d}" for n in range(start, mid + 1) if n in sessions_meta]
    pm_sessions = [f"{n:03d}" for n in range(mid + 1, end + 1) if n in sessions_meta]

    parts.append(f"- 오전 (09:00~12:00): 세션 {am_sessions[0]} ~ {am_sessions[-1]}")
    parts.append(f"- 오후 (13:00~18:00): 세션 {pm_sessions[0]} ~ {pm_sessions[-1]}")
    parts.append("")

parts.append("---\n")

# === DEPENDENCY GRAPH ===
parts.append("## 🗺️ 전체 의존성 그래프\n")
parts.append("```mermaid")
parts.append(dep_graph)
parts.append("```\n")
parts.append("---\n")

# === MAIN CONTENT ===
parts.append("## 📚 본문\n")

current_day = 0
for num in sorted(session_files.keys()):
    meta = sessions_meta.get(num)
    if not meta:
        continue

    day = meta["day"]

    # Day header
    if day != current_day:
        current_day = day
        start, end = DAY_RANGES[day]
        parts.append(f"\n---\n")
        parts.append(f"# 📅 Day {day}: {DAY_THEMES[day]}\n")
        parts.append(
            f"> 세션 {start:03d} ~ {end:03d} | {index['statistics']['duration_per_day_minutes'][str(day)]}분\n"
        )

        # Insert day visual specs (tables)
        if day in visual_specs:
            parts.append(f"### 📊 Day {day} 시각화 레퍼런스\n")
            parts.append(visual_specs[day])
            parts.append("")

    # Session content
    emoji = chunk_emoji.get(meta["chunk_type"], "📝")
    parts.append(f"### 세션 {num:03d}: {meta['title']}")
    parts.append(
        f"> [원본 파일](sessions/{session_files[num].name}) | ⏱️ {meta['duration_min']}분 | {emoji} {meta['chunk_type']} | 난이도: {meta['complexity']}"
    )
    parts.append("")

    # Read and insert session content (skip the first H1 title line to avoid duplication)
    content = session_files[num].read_text(encoding="utf-8")
    # Remove leading title if it starts with # 세션
    content_lines = content.split("\n")
    skip = 0
    for i, line in enumerate(content_lines):
        if line.strip().startswith("# 세션") or line.strip().startswith("# "):
            skip = i + 1
            # Also skip blank lines after title
            while skip < len(content_lines) and content_lines[skip].strip() == "":
                skip += 1
            break

    session_content = "\n".join(content_lines[skip:])
    parts.append(session_content)
    parts.append("")

    # Bridge note
    prev_num = num - 1 if num - 1 in sessions_meta else None
    next_num = num + 1 if num + 1 in sessions_meta else None
    prev_title = sessions_meta[prev_num]["title"] if prev_num else None
    next_title = sessions_meta[next_num]["title"] if next_num else None

    bn = bridge_note(num, meta["title"], next_num, next_title, prev_num, prev_title)
    if bn:
        parts.append(bn)
    parts.append("")
    parts.append("---\n")

# === APPENDIX ===
parts.append("""
## 📦 부록

### A. 과정 전체 요약

#### 5일간의 학습 여정

| Day | 핵심 테마 | 패러다임 | 주요 산출물 |
|-----|-----------|----------|------------|
| 1 | AI 도구 & 환경 구축 | 탐험과 설치 | Antigravity + Python + uv 환경 완성 |
| 2 | 프롬프트 엔지니어링 | SDD (명세 주도 개발) | PRD 문서 + 미니 스펙 프로젝트 |
| 3 | 파이썬 문법 기초 | 데이터와 로직 | 학생 성적 관리 프로그램 |
| 4 | 절차적 → 구조적 | 리팩토링과 테스트 | 고객관리 v1(절차) → v2(구조) |
| 5 | 객체지향 & DI | 캡슐화와 유연성 | 고객관리 v3(OOP) → v4(DI) |

#### 핵심 개념 맵

```mermaid
mindmap
  root((AI-native 파이썬기초))
    Day1 환경구축
      Antigravity IDE
      Python & uv
      가상환경
      첫 코드 생성
    Day2 프롬프트
      4대 요소 PTCF
      SDD 방법론
      PRD 작성
      미니 스펙
    Day3 문법기초
      변수와 타입
      리스트와 딕셔너리
      조건문과 반복문
      함수 정의
    Day4 구조화
      CRUD 패턴
      함수 분리
      테스트 시나리오
      코드 리뷰
    Day5 OOP
      클래스와 객체
      캡슐화
      상속과 다형성
      의존성 주입
```

### B. 참고 자료

#### 로컬 참고자료 (Source A)
- `AI 시대의 서사 v3 - Claude.md` — 패러다임 전환 서사, 비유 체계
- `3 프롬프트 엔지니어링.pdf` — 프롬프트 구성 요소, 기법
- `7 기획.pdf` — 기획 방법론, PRD 작성법
- `8 코딩.pdf` — 코딩 패턴, 구조적 프로그래밍
- `9 디버깅, 테스트, 배포.pdf` — 테스트 전략, 디버깅 기법
- `gemini-for-google-workspace-prompting-guide-101.pdf` — Gemini 프롬프트 가이드
- `AI-native_파이썬기초.md` — 과정 명세서

#### 외부 참고자료 (Source B: NotebookLM, Source C: Deep Research)
- NotebookLM 기반 5일차별 참조 데이터
- Deep Research 기반 5일차별 최신 트렌드 및 모범 사례

### C. 이 강의 이후 학습 경로

1. **심화 파이썬**: 파일 I/O, 예외 처리 심화, 데코레이터, 제너레이터
2. **웹 개발**: FastAPI/Flask 기반 REST API 구축
3. **데이터 분석**: pandas, matplotlib를 활용한 데이터 분석
4. **AI 활용 심화**: LangChain, RAG 패턴, 에이전트 개발
5. **프로젝트 실전**: 팀 프로젝트, Git 협업, CI/CD 파이프라인

### D. 체크리스트 (강사용)

#### 강의 준비 체크리스트
- [ ] Windows 11 + Antigravity IDE 설치 확인
- [ ] Python 3.14+ 설치 확인
- [ ] uv 패키지 매니저 설치 확인
- [ ] Gemini 3 Pro API 연동 확인
- [ ] 네트워크 환경 점검
- [ ] 실습용 프로젝트 폴더 구성
- [ ] 참고자료 준비 (PDF, 교안)

#### 일자별 진행 체크리스트
""")

for day in range(1, 6):
    start, end = DAY_RANGES[day]
    parts.append(f"\n**Day {day}**")
    for num in range(start, end + 1):
        if num in sessions_meta:
            parts.append(
                f"- [ ] 세션 {num:03d}: {sessions_meta[num]['title']} ({sessions_meta[num]['duration_min']}분)"
            )

parts.append("""

---

*취합 및 통합: A4C_Material_Aggregator*
*3-Source Mandatory 정책 적용*
*최종 검증: A8_QA_Editor (예정)*
""")

# Write output
output_text = "\n".join(parts)
OUTPUT.write_text(output_text, encoding="utf-8")

# Stats
lines = output_text.count("\n")
size_kb = len(output_text.encode("utf-8")) / 1024
print(f"✅ 강의교안_v2.0.md 생성 완료")
print(f"   - 총 라인 수: {lines:,}")
print(f"   - 파일 크기: {size_kb:,.1f} KB")
print(f"   - 포함 세션 수: {len(session_files)}/106")
print(f"   - 시각화 스펙 삽입: {len(visual_specs)}개 Day")
print(f"   - 의존성 그래프: 포함")
print(f"   - 부록: 포함")
