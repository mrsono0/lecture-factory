#!/usr/bin/env python3
"""aggregate_material.py — step_5a(pair_merge) + step_6(최종 취합) 자동화 스크립트.

워크플로우 02_Material_Writing의 기계적 스텝들을 LLM 호출 없이 수행합니다.
Usage:
    python aggregate_material.py pair_merge  <project_dir>  # pairs/ → Day AM/PM 파일
    python aggregate_material.py ampm_split  <project_dir>  # sessions/ → Day AM/PM 파일
    python aggregate_material.py aggregate   <project_dir>  # 최종 취합
    python aggregate_material.py all        <project_dir>   # ampm_split → aggregate 순차 실행
    project_dir: 프로젝트 루트 (예: 2026-03-01_AI-native_클로드_...)
                 하위에 01_Planning/강의구성안.md, 02_Material/sessions/ 가 존재해야 함.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


# ──────────────────────────────────────────────────────────────
# Data models
# ──────────────────────────────────────────────────────────────


@dataclass
class SessionInfo:
    number: int  # 1, 2, ..., 40
    session_id: str  # 세션-001-제목
    title: str  # 제목 부분
    time_range: str  # 09:00~09:50
    duration: str  # 50분
    file_path: Path | None = None
    chunk_type: str = "narrative"  # narrative, lab, code, diagram


@dataclass
class HalfDay:
    day: int  # 1~5
    period: str  # AM or PM
    time_range: str  # 09:00~12:50 or 14:00~17:50
    sessions: list[SessionInfo] = field(default_factory=list)
    day_title: str = ""  # Day 1: 파트1 — ...
    day_goal: str = ""  # Day 목표


# ──────────────────────────────────────────────────────────────
# Parsing: 강의구성안 → HalfDay 리스트
# ──────────────────────────────────────────────────────────────

_RE_DAY_HEADER = re.compile(r"^## Day (\d+):\s*(.+)$")
_RE_HALFDAY = re.compile(r"^### Day \d+ (AM|PM) \((.+?)\)")
_RE_SESSION = re.compile(
    r"^#### 세션 (\d{3}):\s*(.+?)\s*\((\d{2}:\d{2}~\d{2}:\d{2}),\s*(\d+분)\)"
)
_RE_SESSION_ID = re.compile(r"\*\*세션 ID\*\*\s*\|\s*(.+)")
_RE_DAY_GOAL = re.compile(r"🎯 \*\*Day \d+ 목표\*\*:\s*(.+)")


def _guess_chunk_type(title: str, activities: str = "") -> str:
    """세션 제목/활동 내용으로 청크 타입 추론."""
    lower = (title + activities).lower()
    if "lab" in lower:
        return "lab"
    if "코드" in lower or "code" in lower or "구현" in lower:
        return "code"
    if "다이어그램" in lower or "diagram" in lower or "시각화" in lower:
        return "diagram"
    return "narrative"


def parse_syllabus(syllabus_path: Path) -> list[HalfDay]:
    """강의구성안.md를 파싱하여 HalfDay 리스트 반환."""
    text = syllabus_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    halfdays: list[HalfDay] = []
    current_day = 0
    current_day_title = ""
    current_day_goal = ""
    current_hd: HalfDay | None = None
    current_session: SessionInfo | None = None

    for line in lines:
        # Day 헤더
        m = _RE_DAY_HEADER.match(line)
        if m:
            current_day = int(m.group(1))
            current_day_title = m.group(2).strip()
            current_day_goal = ""
            continue

        # Day 목표
        m = _RE_DAY_GOAL.search(line)
        if m:
            current_day_goal = m.group(1).strip()
            continue

        # AM/PM 헤더
        m = _RE_HALFDAY.match(line)
        if m:
            current_hd = HalfDay(
                day=current_day,
                period=m.group(1),
                time_range=m.group(2),
                day_title=current_day_title,
                day_goal=current_day_goal,
            )
            halfdays.append(current_hd)
            continue

        # 세션 헤더
        m = _RE_SESSION.match(line)
        if m and current_hd is not None:
            num = int(m.group(1))
            title = m.group(2).strip()
            current_session = SessionInfo(
                number=num,
                session_id="",
                title=title,
                time_range=m.group(3),
                duration=m.group(4),
                chunk_type=_guess_chunk_type(title),
            )
            current_hd.sessions.append(current_session)
            continue

        # 세션 ID 행 (테이블 내부)
        m = _RE_SESSION_ID.search(line)
        if m and current_session is not None:
            current_session.session_id = m.group(1).strip()
            continue

    return halfdays


# ──────────────────────────────────────────────────────────────
# 세션 파일 매칭
# ──────────────────────────────────────────────────────────────

_RE_SESSION_FILE = re.compile(r"세션-(\d{3})-(.+?)(?:_v[\d.]+)?\.md$")


def match_session_files(sessions_dir: Path, halfdays: list[HalfDay]) -> dict[int, Path]:
    """세션 번호 → 파일 경로 매핑."""
    mapping: dict[int, Path] = {}
    if not sessions_dir.exists():
        return mapping
    for f in sorted(sessions_dir.glob("세션-*.md")):
        m = _RE_SESSION_FILE.search(f.name)
        if m:
            mapping[int(m.group(1))] = f

    # HalfDay 내부 세션에 파일 경로 할당
    for hd in halfdays:
        for s in hd.sessions:
            s.file_path = mapping.get(s.number)

    return mapping




# ──────────────────────────────────────────────────────────────
# step_5a: pair_merge — pairs/ → Day AM/PM 파일
# ──────────────────────────────────────────────────────────────

_RE_PAIR_FILE = re.compile(r"Day(\d+)_(AM|PM)_Part(\d+)_(.+?)\.md$")


def merge_pairs(project_dir: Path) -> list[Path]:
    """pairs/ 내 Part 파일들을 Day/AM|PM 단위로 머지하여 Day AM/PM 파일 생성."""
    pairs_dir = project_dir / "02_Material" / "pairs"
    material_dir = project_dir / "02_Material"
    material_dir.mkdir(parents=True, exist_ok=True)

    if not pairs_dir.exists():
        print(f"  ⚠️ pairs/ 디렉토리 미발견: {pairs_dir}")
        return []

    # 강의 제목 추출
    syllabus = project_dir / "01_Planning" / "강의구성안.md"
    course_title = "강의"
    if syllabus.exists():
        first_line = syllabus.read_text(encoding="utf-8").splitlines()[0]
        course_title = first_line.lstrip("# ").split("—")[0].strip()

    # 1. Part 파일 수집 및 그룹핑 (day, period) → [(part_num, topic, path)]
    groups: dict[tuple[int, str], list[tuple[int, str, Path]]] = {}
    for f in sorted(pairs_dir.glob("Day*_Part*.md")):
        m = _RE_PAIR_FILE.search(f.name)
        if not m:
            continue
        day = int(m.group(1))
        period = m.group(2)
        part_num = int(m.group(3))
        topic = m.group(4)
        key = (day, period)
        groups.setdefault(key, []).append((part_num, topic, f))

    if not groups:
        print("  ⚠️ pairs/ 내 Part 파일 없음")
        return []

    generated: list[Path] = []

    for (day, period), parts in sorted(groups.items()):
        parts.sort(key=lambda x: x[0])  # Part 번호 순

        # 주제 요약: 첫 Part과 마지막 Part의 topic 결합
        if len(parts) == 1:
            topic_summary = parts[0][1]
        else:
            topic_summary = f"{parts[0][1]}~{parts[-1][1]}"
        topic_summary = re.sub(r"[/\\:*?\"<>|]", "", topic_summary)
        topic_summary = re.sub(r"\s+", "_", topic_summary)
        if len(topic_summary) > 30:
            topic_summary = topic_summary[:30]

        filename = f"Day{day}_{period}_{topic_summary}.md"
        out_path = material_dir / filename

        content_parts: list[str] = []

        # 헤더
        content_parts.append(f"# {course_title} — Day {day} {period}")
        content_parts.append("")
        content_parts.append(f"> **과정명**: {course_title}")
        content_parts.append(f"> **일자**: Day {day}")
        content_parts.append(f"> **시간대**: {period}")
        content_parts.append(f"> **Part 수**: {len(parts)}개")
        content_parts.append("")
        content_parts.append("---")
        content_parts.append("")

        # 본문: Part 파일 순서대로 연결
        for _part_num, _topic, fpath in parts:
            content = fpath.read_text(encoding="utf-8")
            content_parts.append(content.rstrip())
            content_parts.append("")
            content_parts.append("---")
            content_parts.append("")

        out_path.write_text("\n".join(content_parts), encoding="utf-8")
        generated.append(out_path)
        print(
            f"  ✅ {filename} ({len(parts)} parts, {out_path.stat().st_size:,} bytes)"
        )

    return generated

# ──────────────────────────────────────────────────────────────
# 세션 파일 메타데이터 추출
# ──────────────────────────────────────────────────────────────

_RE_META_TIME = re.compile(r"⏱️?\s*(\d+분)")
_RE_META_CHUNK = re.compile(
    r"📖\s*(narrative)|💻\s*(code|lab)|🔬\s*(lab)|📊\s*(diagram)"
)


def extract_session_meta(file_path: Path) -> dict[str, str]:
    """세션 파일 첫 20줄에서 메타데이터 추출."""
    meta: dict[str, str] = {"title": "", "time": "50분", "chunk_type": "narrative"}
    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return meta

    lines = text.splitlines()[:20]
    for line in lines:
        if line.startswith("# "):
            meta["title"] = line.lstrip("# ").strip()
        m = _RE_META_TIME.search(line)
        if m:
            meta["time"] = m.group(1)
        m = _RE_META_CHUNK.search(line)
        if m:
            meta["chunk_type"] = next(g for g in m.groups() if g)
    return meta


# ──────────────────────────────────────────────────────────────
# step_12: AM/PM 분할 파일 생성
# ──────────────────────────────────────────────────────────────


def _summarize_topic(sessions: list[SessionInfo], max_len: int = 30) -> str:
    """세션 제목들에서 주제 요약 문자열 생성."""
    if not sessions:
        return "빈블록"
    # 첫 번째와 마지막 세션 제목의 핵심 키워드 결합
    first = sessions[0].title
    last = sessions[-1].title
    if len(sessions) == 1:
        summary = first
    else:
        summary = f"{first}~{last}"
    # 파일명에 쓸 수 없는 문자 제거
    summary = re.sub(r"[/\\:*?\"<>|]", "", summary)
    summary = re.sub(r"\s+", "_", summary)
    if len(summary) > max_len:
        summary = summary[:max_len]
    return summary


def generate_ampm_files(project_dir: Path, halfdays: list[HalfDay]) -> list[Path]:
    """AM/PM 분할 파일 생성. 반환: 생성된 파일 경로 리스트."""
    material_dir = project_dir / "02_Material"
    material_dir.mkdir(parents=True, exist_ok=True)
    sessions_dir = material_dir / "sessions"

    generated: list[Path] = []

    # 강의 제목 추출 (강의구성안 첫 줄)
    syllabus = project_dir / "01_Planning" / "강의구성안.md"
    course_title = "강의"
    if syllabus.exists():
        first_line = syllabus.read_text(encoding="utf-8").splitlines()[0]
        course_title = first_line.lstrip("# ").split("—")[0].strip()

    for hd in halfdays:
        if not hd.sessions:
            continue

        topic = _summarize_topic(hd.sessions)
        filename = f"Day{hd.day}_{hd.period}_{topic}.md"
        out_path = material_dir / filename

        parts: list[str] = []

        # 헤더
        parts.append(f"# {course_title} — Day {hd.day} {hd.period}")
        parts.append("")
        parts.append(f"> **과정명**: {course_title}")
        parts.append(f"> **일자**: Day {hd.day}")
        parts.append(f"> **시간대**: {hd.period} ({hd.time_range})")
        first_num = hd.sessions[0].number
        last_num = hd.sessions[-1].number
        parts.append(
            f"> **세션 범위**: 세션 {first_num:03d} ~ {last_num:03d} ({len(hd.sessions)}개)"
        )
        if hd.day_goal:
            parts.append(f"> **Day 목표**: {hd.day_goal}")
        parts.append("")
        parts.append("---")
        parts.append("")

        # 목차
        parts.append("## 📋 목차")
        parts.append("")
        for s in hd.sessions:
            parts.append(f"- [{s.number:03d}. {s.title}](#세션-{s.number:03d})")
        parts.append("")
        parts.append("---")
        parts.append("")

        # 본문: 세션 내용 연결
        for s in hd.sessions:
            if s.file_path and s.file_path.exists():
                content = s.file_path.read_text(encoding="utf-8")
                parts.append(content.rstrip())
            else:
                parts.append(f"## 세션 {s.number:03d}: {s.title}")
                parts.append("")
                parts.append(
                    f"> ⚠️ 세션 파일 미발견: `sessions/세션-{s.number:03d}-*.md`"
                )
            parts.append("")
            parts.append("---")
            parts.append("")

        out_path.write_text("\n".join(parts), encoding="utf-8")
        generated.append(out_path)
        print(
            f"  ✅ {filename} ({len(hd.sessions)}세션, {out_path.stat().st_size:,} bytes)"
        )

    return generated


# ──────────────────────────────────────────────────────────────
# step_13: 최종 취합 (강의교안_v2.1.md)
# ──────────────────────────────────────────────────────────────


def aggregate_sessions(project_dir: Path, halfdays: list[HalfDay]) -> Path:
    """최종 강의교안_v2.1.md 생성."""
    material_dir = project_dir / "02_Material"
    sessions_dir = material_dir / "sessions"

    # 강의 제목 / 메타데이터
    syllabus = project_dir / "01_Planning" / "강의구성안.md"
    course_title = "강의"
    if syllabus.exists():
        first_line = syllabus.read_text(encoding="utf-8").splitlines()[0]
        course_title = first_line.lstrip("# ").split("—")[0].strip()

    # 전체 세션 수집 (번호순 정렬)
    all_sessions: list[SessionInfo] = []
    for hd in halfdays:
        all_sessions.extend(hd.sessions)
    all_sessions.sort(key=lambda s: s.number)
    total_sessions = len(all_sessions)
    total_minutes = sum(int(s.duration.replace("분", "")) for s in all_sessions)
    hours = total_minutes // 60
    mins = total_minutes % 60

    parts: list[str] = []

    # ── 헤더 ──
    parts.append(f"# {course_title} — 강의교안 v2.1")
    parts.append("")
    parts.append(f"> **버전**: 2.1")
    parts.append(f"> **총 세션 수**: {total_sessions}개 세션")
    parts.append(f"> **총 예상 시간**: {hours}시간 {mins}분")
    parts.append(f"> **작성 일시**: {datetime.now().strftime('%Y-%m-%d')}")
    parts.append(f"> **작성 방식**: 청크 타입별 4~7섹션 구조 세션 단위 집필")
    parts.append("")
    parts.append("---")
    parts.append("")

    # ── 목차: 전체 세션 인덱스 ──
    parts.append("## 📋 목차 및 네비게이션")
    parts.append("")
    parts.append("### 전체 세션 인덱스")
    parts.append("")
    parts.append("| 세션 | 제목 | 시간 | 청크 타입 | 바로가기 |")
    parts.append("|------|------|------|-----------|----------|")
    for s in all_sessions:
        ct_icon = {"narrative": "📖", "lab": "🔬", "code": "💻", "diagram": "📊"}.get(
            s.chunk_type, "📖"
        )
        parts.append(
            f"| {s.number:03d} | {s.title} | {s.duration} | {ct_icon} {s.chunk_type} | "
            f"[바로가기](#세션-{s.number:03d}) |"
        )
    parts.append("")

    # ── 목차: 일자별 진행표 ──
    parts.append("### 일자별 진행표")
    parts.append("")
    days_seen: set[int] = set()
    for hd in halfdays:
        if hd.day not in days_seen:
            if days_seen:
                parts.append("")
            parts.append(f"**Day {hd.day}**: {hd.day_title}")
            days_seen.add(hd.day)
        if hd.sessions:
            first = hd.sessions[0].number
            last = hd.sessions[-1].number
            label = "오전" if hd.period == "AM" else "오후"
            parts.append(f"- {label} ({hd.time_range}): 세션 {first:03d} ~ {last:03d}")
    parts.append("")
    parts.append("---")
    parts.append("")

    # ── 의존성 그래프 (A3 골격 패킷 기반, 템플릿) ──
    parts.append("## 🗺️ 전체 의존성 그래프")
    parts.append("")
    parts.append("```mermaid")
    parts.append("graph TD")
    for s in all_sessions:
        safe_title = s.title[:20].replace('"', "'")
        parts.append(f'    S{s.number:03d}["{s.number:03d}: {safe_title}"]')
    # 순차 의존성 (기본)
    for i in range(len(all_sessions) - 1):
        a = all_sessions[i].number
        b = all_sessions[i + 1].number
        parts.append(f"    S{a:03d} --> S{b:03d}")
    parts.append("```")
    parts.append("")
    parts.append("---")
    parts.append("")

    # ── 본문: 세션 내용 통합 ──
    parts.append("## 📚 본문")
    parts.append("")

    for s in all_sessions:
        if s.file_path and s.file_path.exists():
            content = s.file_path.read_text(encoding="utf-8")
            # 원본 파일 참조 링크 추가
            rel_path = f"sessions/{s.file_path.name}"
            ct_icon = {
                "narrative": "📖",
                "lab": "🔬",
                "code": "💻",
                "diagram": "📊",
            }.get(s.chunk_type, "📖")
            parts.append(
                f"> [원본 파일]({rel_path}) | ⏱️ {s.duration} | {ct_icon} {s.chunk_type}"
            )
            parts.append("")
            parts.append(content.rstrip())
        else:
            parts.append(f"### 세션 {s.number:03d}: {s.title}")
            parts.append("")
            parts.append(f"> ⚠️ 세션 파일 미발견: `sessions/세션-{s.number:03d}-*.md`")

        parts.append("")
        parts.append("---")
        parts.append("")

    # ── 부록 ──
    parts.append("## 📦 부록")
    parts.append("")

    # A. 키워드 인덱스 (템플릿)
    parts.append("### A. 키워드 인덱스")
    parts.append("")
    parts.append("| 키워드 | 정의 | 첫 등장 세션 |")
    parts.append("|--------|------|--------------|")
    parts.append("| _(자동 생성 대상 — 추후 LLM 보조 또는 수동 작성)_ | | |")
    parts.append("")

    # B. 학습 로드맵 (템플릿)
    parts.append("### B. 학습 로드맵")
    parts.append("")
    parts.append("#### 이 강의 이후 학습 경로")
    parts.append("1. **심화 과정**: _(추후 작성)_")
    parts.append("2. **관련 기술**: _(추후 작성)_")
    parts.append("3. **실전 프로젝트**: _(추후 작성)_")
    parts.append("")

    # C. 강사 체크리스트
    parts.append("### C. 강사 체크리스트")
    parts.append("")
    parts.append("#### 강의 준비")
    parts.append("- [ ] 모든 세션 파일 확인")
    parts.append("- [ ] 코드 예제 실행 테스트")
    parts.append("- [ ] 실습 환경 준비")
    parts.append("- [ ] 보충 자료 준비")
    parts.append("")
    parts.append("#### 강의 진행")
    for s in all_sessions:
        parts.append(f"- [ ] 세션 {s.number:03d}: {s.title} 완료")
    parts.append("")

    parts.append("---")
    parts.append("")
    parts.append(
        f"*취합: aggregate_material.py | 생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
    )

    out_path = material_dir / "강의교안_v2.1.md"
    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(
        f"  ✅ 강의교안_v2.1.md ({total_sessions}세션, {out_path.stat().st_size:,} bytes)"
    )

    return out_path


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    action = sys.argv[1]
    project_dir = Path(sys.argv[2]).resolve()

    if action not in ("pair_merge", "ampm_split", "aggregate", "all"):
        print(f"❌ Unknown action: {action}")
        print("   Valid actions: pair_merge, ampm_split, aggregate, all")
        return 1

    syllabus = project_dir / "01_Planning" / "강의구성안.md"
    if not syllabus.exists():
        print(f"❌ 강의구성안을 찾을 수 없습니다: {syllabus}")
        return 1

    sessions_dir = project_dir / "02_Material" / "sessions"

    print(f"📂 프로젝트: {project_dir.name}")
    print(f"📄 강의구성안: {syllabus}")
    print(f"📁 세션 디렉토리: {sessions_dir}")
    print()

    # 1. 강의구성안 파싱
    print("🔍 강의구성안 파싱 중...")
    halfdays = parse_syllabus(syllabus)
    total_sessions = sum(len(hd.sessions) for hd in halfdays)
    print(f"   → {len(halfdays)} 블록, {total_sessions} 세션 발견")
    print()

    # 2. 세션 파일 매칭
    file_map = match_session_files(sessions_dir, halfdays)
    matched = sum(1 for v in file_map.values() if v is not None)
    print(f"📎 세션 파일 매칭: {matched}/{total_sessions}")
    if matched < total_sessions:
        missing = [
            s.number for hd in halfdays for s in hd.sessions if s.file_path is None
        ]
        print(f"   ⚠️ 미발견: {missing}")
    print()

    # 3. 실행
    if action == "pair_merge":
        print("📋 step_5a: pair_merge — pairs/ → Day AM/PM 파일...")
        files = merge_pairs(project_dir)
        print(f"   → {len(files)} 파일 생성 완료")
        print()
    if action in ("ampm_split", "all"):
        print("📋 ampm_split (legacy, 현재 미사용)...")
        files = generate_ampm_files(project_dir, halfdays)
        print(f"   → {len(files)} 파일 생성 완료")
        print()
    if action in ("aggregate", "all"):
        print("📋 step_6: 최종 교안 취합...")
        out = aggregate_sessions(project_dir, halfdays)
        print(f"   → {out}")
        print()

    print("✅ 완료!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
