#!/usr/bin/env python3
"""
Step 11: 보조 패킷 인라인 통합 스크립트
6개 보조 패킷의 내용을 106개 v2.1 세션 파일에 삽입한다.

삽입 규칙:
- lab_packet → §4 끝 (§5 직전): ### 📋 실습 설계 보강 (Lab Packet)
- visualization_packet → §2 끝 (§3 직전): ### 🎨 추가 시각화 (Visualization Packet)
- visual_specs → §3 끝 (§4 직전): ### 📊 참고 표 (Visual Specs)
- instructor_support → §4 끝 (§5 직전, lab_packet 뒤): ### 🎓 강사 노트 (Instructor Support)
- code_validation → §5 내부 (세션 095만)
- differentiation → §1 끝 (§2 직전): 차별화 포인트
"""

import os, re, glob, sys
from pathlib import Path


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


BASE = str(resolve_base() / "02_Material")
SESSIONS_DIR = os.path.join(BASE, "sessions")


# ──────────────────────────────────────────
# 1. lab_packet.md 파싱 → {session_id: content_block}
# ──────────────────────────────────────────
def parse_lab_packet():
    path = os.path.join(BASE, "packets", "lab_packet.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    # Split by ### 세션 NNN:
    pattern = r"### 세션 (\d{3}): (.+?)(?=\n### 세션 \d{3}:|\n---\n|\n## \d+\.)"
    matches = re.findall(pattern, text, re.DOTALL)
    result = {}
    for sid, body in matches:
        sid_int = int(sid)
        # Clean up: remove trailing whitespace lines
        body = body.strip()
        result[sid_int] = f"**세션 {sid} 실습 설계 보강**\n\n{body}"
    return result


# ──────────────────────────────────────────
# 2. visualization_packet.md 파싱 → {session_id: mermaid_block}
# ──────────────────────────────────────────
def parse_visualization_packet():
    """Extract diagrams mapped to specific sessions."""
    # Hardcoded mapping from packet analysis
    mapping = {
        2: "AI-Human 협업 워크플로우",
        3: "예측-검증-설명 (POE) 학습 사이클",
        11: "파이썬 개발 환경 구축 흐름",
        23: "프롬프트 엔지니어링 4대 요소 (PTCF)",
        36: "SDD (명세서 기반 개발) 워크플로우",
        40: "PRD (제품 요구사항 명세서) 구조",
        46: "파이썬 자료형 (Data Type) 계층 구조",
        54: "if/else 조건문 제어 흐름",
        57: "for/while 반복문 제어 흐름",
        62: "함수(Function) 호출과 데이터 흐름",
        74: "절차적 vs 구조적 프로그래밍 비교",
        69: "데이터 CRUD 흐름도",
        80: "테스트 피라미드 (Test Pyramid)",
        75: "파이썬 모듈화 컴포넌트 구조",
        88: "클래스와 객체(인스턴스)의 관계",
        96: "상속 계층도 (Inheritance Hierarchy)",
        100: "의존성 주입 (Dependency Injection) 기본 패턴",
        104: "프로그램 아키텍처 진화 (Evolution v1 → v4)",
    }

    path = os.path.join(BASE, "packets", "visualization_packet.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    result = {}
    # Split by ### N. headers (### 1., ### 2., etc.)
    blocks = re.split(r"\n(?=### \d+\. )", text)
    for block in blocks:
        m = re.match(r"### (\d+)\. (.+)", block)
        if not m:
            continue
        diagram_title = m.group(2).strip()
        # Find which session this maps to
        for sid, title in mapping.items():
            if title == diagram_title:
                # Extract the mermaid block and description
                # Get the 설명 line and mermaid code
                desc_match = re.search(r"\* \*\*설명\*\*: (.+)", block)
                mermaid_match = re.search(r"```mermaid\n(.+?)```", block, re.DOTALL)
                if mermaid_match:
                    desc = desc_match.group(1) if desc_match else ""
                    content = f"**{diagram_title}**\n\n{desc}\n\n```mermaid\n{mermaid_match.group(1).strip()}\n```"
                    result[sid] = content
                break
    return result


# ──────────────────────────────────────────
# 3. visual_specs 파싱 → {session_id: table_block}
# ──────────────────────────────────────────
def parse_visual_specs():
    """Maps visual spec tables to specific sessions."""
    # Hardcoded mapping from "추천 위치" analysis
    table_session_map = {
        # day1_tables.md
        "day1_tables.md##1": 4,  # IDE 비교
        "day1_tables.md##2": 9,  # 환경 체크리스트
        "day1_tables.md##3": 10,  # 트러블슈팅
        # day2_tables.md
        "day2_tables.md##1": 26,  # 프롬프트 나쁜/좋은
        "day2_tables.md##2": 25,  # 4대 핵심 요소
        "day2_tables.md##3": 38,  # PRD 템플릿
        "day2_tables.md##4": 33,  # SDD vs 전통
        # day3_tables.md
        "day3_tables.md##1": 45,  # 데이터 타입
        "day3_tables.md##2": 48,  # 컬렉션 타입
        "day3_tables.md##3": 47,  # 연산자 우선순위
        "day3_tables.md##4": 58,  # 내장 함수
        # day4_tables.md
        "day4_tables.md##1": 75,  # 절차 vs 구조
        "day4_tables.md##2": 69,  # CRUD
        "day4_tables.md##3": 78,  # 테스트 3유형
        "day4_tables.md##4": 79,  # 코드 리뷰 5대
        # day5_tables.md
        "day5_tables.md##1": 86,  # OOP 핵심
        "day5_tables.md##2": 89,  # Class vs Dataclass
        "day5_tables.md##3": 94,  # 상속
        "day5_tables.md##4": 100,  # DI
        "day5_tables.md##5": 101,  # v1~v4 진화
    }

    result = {}
    specs_dir = os.path.join(BASE, "visual_specs")
    for day_n in range(1, 6):
        fname = f"day{day_n}_tables.md"
        fpath = os.path.join(specs_dir, fname)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()
        # Split by ## N. headers
        blocks = re.split(r"\n(?=## \d+\. )", text)
        for block in blocks:
            m = re.match(r"## (\d+)\. (.+)", block)
            if not m:
                continue
            table_num = m.group(1)
            table_title = m.group(2).strip()
            key = f"{fname}##{table_num}"
            if key in table_session_map:
                sid = table_session_map[key]
                # Extract the table content (skip the 추천위치 and 강사설명 lines, keep the table)
                table_match = re.search(r"(\|.+\|[\s\S]*?\|.+\|)", block)
                if table_match:
                    table_content = table_match.group(1).strip()
                    content = f"**{table_title}**\n\n{table_content}"
                    if sid not in result:
                        result[sid] = content
                    else:
                        result[sid] += f"\n\n{content}"
    return result


# ──────────────────────────────────────────
# 4. instructor_support 파싱 → {session_id: instructor_note}
# ──────────────────────────────────────────
def parse_instructor_support():
    """Extract per-session instructor notes from cue sheets."""
    path = os.path.join(BASE, "packets", "instructor_support_packet.md")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    result = {}
    # Parse cue sheet table rows: | 시간 | 세션# | 제목 | 분 | 타입 | 핵심활동 | 강사주의사항 |
    rows = re.findall(
        r"\|\s*(\d{2}:\d{2})\s*\|\s*(\d{3})\s*\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\w+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
        text,
    )
    for time_str, sid_str, title, minutes, stype, activity, note in rows:
        sid = int(sid_str)
        note = note.strip()
        if note and note != "—":
            content = (
                f"- ⏱️ **타이밍**: {time_str} ({minutes}분, {stype})\n"
                f"- 🎯 **핵심 활동**: {activity.strip()}\n"
                f"- ⚠️ **강사 주의사항**: {note}"
            )
            result[sid] = content
    return result


# ──────────────────────────────────────────
# 5. differentiation_strategy → {session_id: hook}
# ──────────────────────────────────────────
def parse_differentiation():
    """Map differentiation narrative hooks to day-opening sessions."""
    # Day opening sessions and their narrative arcs
    day_hooks = {
        1: (
            1,
            "패러다임의 전환",
            "수동적 탑승객에서 목적지를 정하는 운전자로 — \"코드를 치는 시대는 끝났다.\" AI라는 완벽한 네비게이션을 켜고, 목적지(What)를 정하는 주체가 '나'임을 깨닫는 출발점.",
        ),
        2: (
            23,
            "통역의 기술",
            "모호한 일상어에서 명확한 지시어로 — 기억력은 완벽하지만 눈치가 전혀 없는 천재 신입사원(AI)을 다루는 법. 나의 의도를 모호함 없이 전달하는 프롬프트를 작성하고, 백지상태의 아이디어를 PRD(설계도)로 변환합니다.",
        ),
        3: (
            44,
            "재료의 이해",
            "마법의 주문 해독하기 — AI가 1초 만에 뱉어낸 코드가 더 이상 마법이 아님을 깨닫는 날. 변수, 제어문, 함수라는 요리 재료들의 특성을 파헤쳐 안목(리터러시)을 갖춥니다.",
        ),
        4: (
            65,
            "질서의 발견",
            "혼돈 속에서 통제력 되찾기 — 프로그램이 조금만 커져도 전역 변수와 중복 코드로 인해 무너지는 '도미노의 악몽'을 직접 겪고, 코드를 논리적 상자(함수)에 나누어 담으며 통제력을 회복합니다.",
        ),
        5: (
            86,
            "창조주의 시선",
            "설계도로 생명 불어넣기 — 흩어진 데이터와 행동을 하나의 생명체(객체)로 묶어내는 객체지향의 마법. 나아가 부품을 자유롭게 갈아끼우는 의존성 주입(DI)을 통해 '소프트웨어 아키텍트'의 시선으로 마무리합니다.",
        ),
    }
    result = {}
    for day, (sid, title, desc) in day_hooks.items():
        content = f"> 🌟 **Day {day} 서사: {title}** — {desc}"
        result[sid] = content
    return result


# ──────────────────────────────────────────
# 6. code_validation → session 095 only
# ──────────────────────────────────────────
def get_code_validation_note():
    return {
        95: (
            "> ⚠️ **코드 검증 결과** (code_validation_report)\n"
            "> VIPCustomer `__init__` 매개변수 들여쓰기: 17개 공백 사용 (PEP 8은 4의 배수 권장).\n"
            "> 기능상 문제 없음 — 여는 괄호에 정렬하는 hanging indent 스타일(PEP 8 허용).\n"
            "> 교육 시 들여쓰기 스타일 선택의 여지를 언급하면 좋습니다."
        )
    }


# ──────────────────────────────────────────
# 메인: 각 v2.1 파일에 삽입
# ──────────────────────────────────────────
def find_section_line(lines, section_num):
    """Find the line index of ## §N. header."""
    pattern = f"## §{section_num}."
    for i, line in enumerate(lines):
        if line.startswith(pattern):
            return i
    return None


def insert_before_section(lines, section_num, subheader, content):
    """Insert content block before ## §N header (at end of previous section)."""
    idx = find_section_line(lines, section_num)
    if idx is None:
        return lines, False
    # Insert before this line, with blank lines for separation
    insert_block = [
        "",
        f"### {subheader}",
        "",
        *content.split("\n"),
        "",
    ]
    return lines[:idx] + insert_block + lines[idx:], True


def insert_in_section5(lines, content):
    """Insert note at the end of §5, before §6."""
    idx = find_section_line(lines, 6)
    if idx is None:
        return lines, False
    insert_block = [
        "",
        *content.split("\n"),
        "",
    ]
    return lines[:idx] + insert_block + lines[idx:], True


def main():
    print("=" * 60)
    print("Step 11: 보조 패킷 인라인 통합 시작")
    print("=" * 60)

    # Parse all packets
    print("\n[1/6] lab_packet.md 파싱...")
    lab_data = parse_lab_packet()
    print(f"  → {len(lab_data)}개 세션 매핑 완료")

    print("[2/6] visualization_packet.md 파싱...")
    viz_data = parse_visualization_packet()
    print(f"  → {len(viz_data)}개 세션 매핑 완료")

    print("[3/6] visual_specs 파싱...")
    specs_data = parse_visual_specs()
    print(f"  → {len(specs_data)}개 세션 매핑 완료")

    print("[4/6] instructor_support_packet.md 파싱...")
    instructor_data = parse_instructor_support()
    print(f"  → {len(instructor_data)}개 세션 매핑 완료")

    print("[5/6] differentiation_strategy.md 파싱...")
    diff_data = parse_differentiation()
    print(f"  → {len(diff_data)}개 세션 매핑 완료")

    print("[6/6] code_validation_report.md 파싱...")
    code_val_data = get_code_validation_note()
    print(f"  → {len(code_val_data)}개 세션 매핑 완료")

    # Find all v2.1 session files
    pattern = os.path.join(SESSIONS_DIR, "세션-*_v2.1.md")
    files = sorted(glob.glob(pattern))
    print(f"\n총 {len(files)}개 v2.1 파일 발견")

    # Stats
    stats = {"modified": 0, "skipped": 0, "insertions": 0}
    modified_files = []

    for fpath in files:
        fname = os.path.basename(fpath)
        # Extract session ID from filename: 세션-NNN-...
        m = re.match(r"세션-(\d{3})-", fname)
        if not m:
            continue
        sid = int(m.group(1))

        with open(fpath, "r", encoding="utf-8") as f:
            original_lines = f.read().split("\n")

        lines = list(original_lines)
        file_modified = False
        insertions = 0

        # Skip if already has supplementary subheaders (idempotency)
        joined = "\n".join(lines)
        if (
            "### 📋 실습 설계 보강" in joined
            or "### 🎨 추가 시각화" in joined
            or "### 📊 참고 표" in joined
            or "### 🎓 강사 노트" in joined
        ):
            stats["skipped"] += 1
            continue

        # Insert in REVERSE ORDER (bottom to top) to preserve line numbers

        # (a) code_validation in §5 (only session 095)
        if sid in code_val_data:
            lines, ok = insert_in_section5(lines, code_val_data[sid])
            if ok:
                file_modified = True
                insertions += 1

        # (b) instructor_support before §5 (at end of §4)
        if sid in instructor_data:
            lines, ok = insert_before_section(
                lines, 5, "🎓 강사 노트 (Instructor Support)", instructor_data[sid]
            )
            if ok:
                file_modified = True
                insertions += 1

        # (c) lab_packet before §5 (at end of §4), before instructor_support
        # Since we inserted instructor_support first, lab_packet goes before it
        if sid in lab_data:
            lines, ok = insert_before_section(
                lines, 5, "📋 실습 설계 보강 (Lab Packet)", lab_data[sid]
            )
            if ok:
                file_modified = True
                insertions += 1

        # (d) visual_specs before §4 (at end of §3)
        if sid in specs_data:
            lines, ok = insert_before_section(
                lines, 4, "📊 참고 표 (Visual Specs)", specs_data[sid]
            )
            if ok:
                file_modified = True
                insertions += 1

        # (e) visualization before §3 (at end of §2)
        if sid in viz_data:
            lines, ok = insert_before_section(
                lines, 3, "🎨 추가 시각화 (Visualization Packet)", viz_data[sid]
            )
            if ok:
                file_modified = True
                insertions += 1

        # (f) differentiation before §2 (at end of §1)
        if sid in diff_data:
            lines, ok = insert_before_section(
                lines, 2, "🌟 차별화 포인트 (Differentiation Strategy)", diff_data[sid]
            )
            if ok:
                file_modified = True
                insertions += 1

        if file_modified:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            stats["modified"] += 1
            stats["insertions"] += insertions
            modified_files.append((sid, insertions))
        else:
            stats["skipped"] += 1

    print(f"\n{'=' * 60}")
    print(f"완료!")
    print(f"  수정된 파일: {stats['modified']}개")
    print(f"  건너뛴 파일: {stats['skipped']}개 (매칭 없거나 이미 삽입됨)")
    print(f"  총 삽입 블록: {stats['insertions']}개")
    print(f"\n수정된 세션 목록:")
    for sid, n_ins in modified_files:
        print(f"  세션 {sid:03d}: {n_ins}개 블록 삽입")


if __name__ == "__main__":
    main()
