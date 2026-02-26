#!/usr/bin/env python3
"""
Step 12 + Step 13: AM/PM 분할 파일 10개 생성 + 통합본 강의교안_v2.1.md 생성
- v2.1 세션 파일 기반
- A4C_Material_Aggregator 명세 준수
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def resolve_base():
    """프로젝트 베이스 경로를 결정합니다.
    1순위: CLI 인자 (sys.argv[1])
    2순위: CWD에서 02_Material/ 폴더를 포함하는 프로젝트 디렉토리 자동 탐지
    """
    if len(sys.argv) > 1:
        base = Path(sys.argv[1])
        if base.exists():
            return base
        raise FileNotFoundError(f"지정된 경로가 존재하지 않습니다: {base}")
    cwd = Path.cwd()
    if (cwd / "02_Material").exists():
        return cwd
    for p in sorted(cwd.glob("????-??-??_*"), reverse=True):
        if (p / "02_Material").exists():
            return p
    raise FileNotFoundError("02_Material/ 폴더를 포함하는 프로젝트 디렉토리를 찾을 수 없습니다.")


BASE = resolve_base()
SESSIONS_DIR = BASE / "02_Material" / "sessions"
PLANNING_DIR = BASE / "01_Planning" / "micro_sessions"
MATERIAL_DIR = BASE / "02_Material"

# Load index
with open(PLANNING_DIR / "_index.json", encoding="utf-8") as f:
    index = json.load(f)

sessions_meta = {s["number"]: s for s in index["sessions"]}

# Load dependency graph
dep_graph = (PLANNING_DIR / "_dependency.mmd").read_text(encoding="utf-8")

DAY_THEMES = {
    1: "AI 도구 탐험과 개발 환경 구축",
    2: "프롬프트 엔지니어링과 요구사항 분석",
    3: "파이썬 문법 기초와 데이터 다루기",
    4: "절차적에서 구조적 프로그래밍으로",
    5: "객체지향 프로그래밍과 과정 마무리",
}

DAY_RANGES = {1: (1, 22), 2: (23, 43), 3: (44, 64), 4: (65, 85), 5: (86, 106)}

AM_PM_RANGES = {
    (1, "AM"): (1, 11),
    (1, "PM"): (12, 22),
    (2, "AM"): (23, 33),
    (2, "PM"): (34, 43),
    (3, "AM"): (44, 54),
    (3, "PM"): (55, 64),
    (4, "AM"): (65, 75),
    (4, "PM"): (76, 85),
    (5, "AM"): (86, 96),
    (5, "PM"): (97, 106),
}

AM_PM_TIMES = {
    "AM": "09:00~12:30",
    "PM": "13:30~18:00",
}

# AM/PM 주제 요약 (기존 v1.0 파일명 기반 + 내용 반영)
AM_PM_TOPICS = {
    (1, "AM"): "환경구축_Antigravity_Python",
    (1, "PM"): "uv_첫프로그램_종합실습",
    (2, "AM"): "프롬프트_기본_코드생성",
    (2, "PM"): "요구사항_PRD_종합실습",
    (3, "AM"): "변수_타입_자료구조",
    (3, "PM"): "제어문_함수_종합실습",
    (4, "AM"): "절차적_고객관리_v1",
    (4, "PM"): "구조적_리팩토링_v2",
    (5, "AM"): "클래스_OOP_리팩토링_v3",
    (5, "PM"): "상속_DI_전체회고",
}

chunk_emoji = {"narrative": "📖", "code": "💻", "lab": "🧪"}

# Collect v2.1 session files sorted by number
session_files = {}
for f in sorted(SESSIONS_DIR.glob("세션-*_v2.1.md")):
    match = re.search(r"세션-(\d{3})", f.name)
    if match:
        num = int(match.group(1))
        session_files[num] = f


def read_session_content(filepath):
    """Read session file, skip H1 title line."""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    skip = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("# 세션") or line.strip().startswith("# "):
            skip = i + 1
            while skip < len(lines) and lines[skip].strip() == "":
                skip += 1
            break
    return "\n".join(lines[skip:])


def bridge_note(
    current_num, next_num=None, next_title=None, prev_num=None, prev_title=None
):
    """Generate bridge notes."""
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


# ============================================================
# STEP 12: AM/PM 분할 파일 10개 생성
# ============================================================
print("=" * 60)
print("Step 12: AM/PM 분할 파일 생성")
print("=" * 60)

ampm_files_created = []

for day in range(1, 6):
    for half in ["AM", "PM"]:
        key = (day, half)
        start, end = AM_PM_RANGES[key]
        topic = AM_PM_TOPICS[key]
        filename = f"Day{day}_{half}_{topic}_v2.1.md"
        filepath = MATERIAL_DIR / filename

        parts = []

        # Header
        half_kr = "오전" if half == "AM" else "오후"
        time_range = AM_PM_TIMES[half]

        # Calculate total duration for this half
        total_min = sum(
            sessions_meta[n]["duration_min"]
            for n in range(start, end + 1)
            if n in sessions_meta
        )

        parts.append(f"# Day {day} {half_kr}: {topic.replace('_', ' ')}")
        parts.append("")
        parts.append(f"> **과정**: AI-native 파이썬 기초 | Day {day}/5 | {time_range}")
        parts.append(f"> **테마**: {DAY_THEMES[day]}")
        parts.append(f"> **세션**: {start:03d} ~ {end:03d} ({end - start + 1}개 세션)")
        parts.append(f"> **총 소요 시간**: {total_min}분")
        parts.append(f"> **버전**: v2.1 (7섹션 구조, 보조 패킷 통합)")
        parts.append(f"> **작성 일시**: {datetime.now().strftime('%Y-%m-%d')}")
        parts.append("")
        parts.append("---")
        parts.append("")

        # 학습목표
        parts.append(f"## 🎯 학습 목표 ({half_kr})")
        parts.append("")
        obj_num = 1
        for n in range(start, end + 1):
            if n in sessions_meta:
                meta = sessions_meta[n]
                parts.append(
                    f"{obj_num}. **세션 {n:03d}**: {meta.get('learning_objective', meta['title'])}"
                )
                obj_num += 1
        parts.append("")
        parts.append("---")
        parts.append("")

        # 목차
        parts.append("## 📋 목차")
        parts.append("")
        for n in range(start, end + 1):
            if n in sessions_meta:
                meta = sessions_meta[n]
                emoji = chunk_emoji.get(meta["chunk_type"], "📝")
                parts.append(
                    f"- [{emoji} 세션 {n:03d}: {meta['title']}](#세션-{n:03d}) ({meta['duration_min']}분)"
                )
        parts.append("")
        parts.append("---")
        parts.append("")

        # 세션 인덱스 테이블
        parts.append("## 📊 세션 인덱스")
        parts.append("")
        parts.append("| 세션 | 제목 | 시간 | 청크 타입 | 난이도 | 바로가기 |")
        parts.append("|------|------|------|-----------|--------|----------|")
        for n in range(start, end + 1):
            if n in sessions_meta:
                meta = sessions_meta[n]
                emoji = chunk_emoji.get(meta["chunk_type"], "📝")
                parts.append(
                    f"| {n:03d} | {meta['title']} | {meta['duration_min']}분 | {emoji} {meta['chunk_type']} | {meta['complexity']} | [바로가기](#세션-{n:03d}) |"
                )
        parts.append("")
        parts.append("---")
        parts.append("")

        # 본문
        parts.append("## 📚 본문")
        parts.append("")

        for n in range(start, end + 1):
            if n not in session_files or n not in sessions_meta:
                continue
            meta = sessions_meta[n]
            emoji = chunk_emoji.get(meta["chunk_type"], "📝")

            parts.append(f"### 세션 {n:03d}: {meta['title']}")
            parts.append(
                f"> [원본 파일](sessions/{session_files[n].name}) | ⏱️ {meta['duration_min']}분 | {emoji} {meta['chunk_type']} | 난이도: {meta['complexity']}"
            )
            parts.append("")

            # Session content
            content = read_session_content(session_files[n])
            parts.append(content)
            parts.append("")

            # Bridge note
            prev_num = n - 1 if n - 1 in sessions_meta else None
            next_num = n + 1 if n + 1 in sessions_meta else None
            prev_title = sessions_meta[prev_num]["title"] if prev_num else None
            next_title = sessions_meta[next_num]["title"] if next_num else None
            bn = bridge_note(n, next_num, next_title, prev_num, prev_title)
            if bn:
                parts.append(bn)
            parts.append("")
            parts.append("---")
            parts.append("")

        # AM→PM / PM→AM 브릿지
        if half == "AM":
            pm_start = AM_PM_RANGES[(day, "PM")][0]
            if pm_start in sessions_meta:
                parts.append(
                    f"> 🔗 **오후 세션으로 이어집니다**: Day {day} 오후({AM_PM_TIMES['PM']})에서 세션 {pm_start:03d}부터 계속됩니다."
                )
                parts.append("")
        elif half == "PM" and day < 5:
            next_am_start = AM_PM_RANGES[(day + 1, "AM")][0]
            if next_am_start in sessions_meta:
                parts.append(
                    f"> 🔗 **내일 오전으로 이어집니다**: Day {day + 1} 오전({AM_PM_TIMES['AM']})에서 세션 {next_am_start:03d}부터 계속됩니다."
                )
                parts.append("")

        # 부록
        parts.append("## 📦 부록")
        parts.append("")
        parts.append(f"### 강사 체크리스트 (Day {day} {half_kr})")
        parts.append("")
        for n in range(start, end + 1):
            if n in sessions_meta:
                parts.append(
                    f"- [ ] 세션 {n:03d}: {sessions_meta[n]['title']} ({sessions_meta[n]['duration_min']}분)"
                )
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append(f"*Day {day} {half_kr} 교안 — AI-native 파이썬 기초 v2.1*  ")
        parts.append("*취합: A4C_Material_Aggregator*  ")
        parts.append("*검증: A8_QA_Editor*")
        parts.append("")

        # Write file
        output_text = "\n".join(parts)
        filepath.write_text(output_text, encoding="utf-8")

        line_count = output_text.count("\n")
        ampm_files_created.append((filename, line_count))
        print(f"  ✅ {filename} — {line_count:,}줄")

print(f"\n총 {len(ampm_files_created)}개 AM/PM 파일 생성 완료\n")


# ============================================================
# STEP 13: 통합본 강의교안_v2.1.md 생성
# ============================================================
print("=" * 60)
print("Step 13: 통합본 강의교안_v2.1.md 생성")
print("=" * 60)

OUTPUT = MATERIAL_DIR / "강의교안_v2.1.md"
parts = []

# === HEADER ===
total_duration = sum(sessions_meta[n]["duration_min"] for n in sessions_meta)
parts.append(f"""# AI-native 파이썬기초 — 강의교안 v2.1

> **버전**: 2.1 (7섹션 구조, 보조 패킷 인라인 통합)
> **총 세션 수**: 106개 마이크로 세션
> **총 예상 시간**: {total_duration:,}분 ({total_duration // 60}시간 {total_duration % 60}분)
> **교육 기간**: 5일 (하루 8시간, 09:00~18:00)
> **작성 일시**: {datetime.now().strftime("%Y-%m-%d")}
> **작성 방식**: 7섹션 구조 마이크로 세션 청킹 + 6개 보조 패킷 인라인 통합
> **대상**: 비전공자 (AI와 협업하는 방식으로 학습)
> **도구**: Windows 11, Antigravity IDE, Gemini 3 Pro, uv 패키지 매니저

---
""")

# === TOC ===
parts.append("## 📋 목차 및 네비게이션\n")
parts.append("### 전체 세션 인덱스\n")
parts.append("| 세션 | 제목 | 시간 | 청크 타입 | 난이도 | 바로가기 |")
parts.append("|------|------|------|-----------|--------|----------|")

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
    duration = index["statistics"]["duration_per_day_minutes"][str(day)]
    parts.append(f"**Day {day}: {DAY_THEMES[day]}** ({duration}분)")

    for half in ["AM", "PM"]:
        key = (day, half)
        start, end = AM_PM_RANGES[key]
        half_kr = "오전" if half == "AM" else "오후"
        time_range = AM_PM_TIMES[half]
        topic = AM_PM_TOPICS[key]
        parts.append(
            f"- {half_kr} ({time_range}): 세션 {start:03d} ~ {end:03d} — [{topic.replace('_', ' ')}](Day{day}_{half}_{topic}_v2.1.md)"
        )
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

    # Session content
    emoji = chunk_emoji.get(meta["chunk_type"], "📝")
    parts.append(f"### 세션 {num:03d}: {meta['title']}")
    parts.append(
        f"> [원본 파일](sessions/{session_files[num].name}) | ⏱️ {meta['duration_min']}분 | {emoji} {meta['chunk_type']} | 난이도: {meta['complexity']}"
    )
    parts.append("")

    content = read_session_content(session_files[num])
    parts.append(content)
    parts.append("")

    # Bridge note
    prev_num = num - 1 if num - 1 in sessions_meta else None
    next_num = num + 1 if num + 1 in sessions_meta else None
    prev_title = sessions_meta[prev_num]["title"] if prev_num else None
    next_title = sessions_meta[next_num]["title"] if next_num else None

    bn = bridge_note(num, next_num, next_title, prev_num, prev_title)
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

### B. AM/PM 분할 파일 인덱스

| 파일 | Day | 시간대 | 세션 범위 |
|------|-----|--------|-----------|""")

for day in range(1, 6):
    for half in ["AM", "PM"]:
        key = (day, half)
        start, end = AM_PM_RANGES[key]
        topic = AM_PM_TOPICS[key]
        filename = f"Day{day}_{half}_{topic}_v2.1.md"
        half_kr = "오전" if half == "AM" else "오후"
        parts.append(
            f"| [{filename}]({filename}) | Day {day} | {half_kr} | {start:03d}~{end:03d} |"
        )

parts.append("""
### C. 참고 자료

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

### D. 이 강의 이후 학습 경로

1. **심화 파이썬**: 파일 I/O, 예외 처리 심화, 데코레이터, 제너레이터
2. **웹 개발**: FastAPI/Flask 기반 REST API 구축
3. **데이터 분석**: pandas, matplotlib를 활용한 데이터 분석
4. **AI 활용 심화**: LangChain, RAG 패턴, 에이전트 개발
5. **프로젝트 실전**: 팀 프로젝트, Git 협업, CI/CD 파이프라인

### E. 체크리스트 (강사용)

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
*7섹션 구조 + 6개 보조 패킷 인라인 통합*
*최종 검증: A8_QA_Editor*
""")

# Write output
output_text = "\n".join(parts)
OUTPUT.write_text(output_text, encoding="utf-8")

lines = output_text.count("\n")
size_kb = len(output_text.encode("utf-8")) / 1024
print(f"\n✅ 강의교안_v2.1.md 생성 완료")
print(f"   - 총 라인 수: {lines:,}")
print(f"   - 파일 크기: {size_kb:,.1f} KB")
print(f"   - 포함 세션 수: {len(session_files)}/106")
print(f"   - 의존성 그래프: 포함")
print(f"   - AM/PM 분할 인덱스: 포함")
print(f"   - 부록: 포함")
