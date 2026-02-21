#!/usr/bin/env python3
"""
Manus AI 슬라이드 생성 헬퍼 스크립트

06_SlidePrompt/*.md 프롬프트 파일을 Manus AI에 일괄 제출하여
Nano Banana Pro로 슬라이드를 생성하고 PPTX를 다운로드합니다.

사용법:
  python .agent/scripts/manus_slide.py [프로젝트폴더]
  python .agent/scripts/manus_slide.py                           # 자동 탐색
  python .agent/scripts/manus_slide.py /path/to/project          # 명시적 지정
  python .agent/scripts/manus_slide.py --resume task_log.json    # 중단된 작업 재개
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    print("[ERROR] requests 패키지가 필요합니다: pip install requests")
    sys.exit(1)


# ─── 설정 ───────────────────────────────────────────────────
MANUS_API_BASE = "https://api.manus.ai/v1"
POLL_INTERVAL = 30        # 폴링 간격 (초)
MAX_WAIT_TIME = 1800      # 최대 대기 시간 (30분)
MAX_CONCURRENT = 5        # 동시 제출 최대 수
PROMPT_GLOB = "*슬라이드 생성 프롬프트.md"

# ─── 헤더/풋터 금지 프리픽스 ─────────────────────────────────
# Manus AI에 프롬프트 전송 시 최상단에 삽입하여 디자인 규칙을 강제합니다.
SLIDE_GENERATION_PREFIX = """[최우선 규칙 — 모든 슬라이드에 예외 없이 적용]

■ 슬라이드 생성 방식 (필수)
반드시 Nano Banana Pro 이미지 생성을 사용하여 각 슬라이드를 고품질 AI 이미지로 생성하세요.
HTML 기반 텍스트 슬라이드가 아닌, 각 슬라이드가 AI가 생성한 이미지여야 합니다.
확인이나 진행 여부를 묻지 말고 바로 슬라이드 이미지 생성을 시작하세요.

■ 파일 내보내기 (필수)
모든 슬라이드 이미지 생성이 완료되면 반드시 다음을 수행하세요:
1. 생성된 모든 슬라이드 이미지를 하나의 PPTX 파일로 조립하세요
2. 각 슬라이드의 발표자 노트(Speaker Notes)를 PPTX에 포함하세요
3. 완성된 PPTX 파일을 다운로드 가능한 형태로 출력하세요
4. 발표자 노트를 별도 마크다운 파일(slide_notes.md)로도 저장하세요
PPTX 파일 출력을 절대 생략하지 마세요.

■ 디자인 규칙
1. 슬라이드에 상단 헤더 바(header bar)를 절대 배치하지 마세요.
2. 슬라이드에 하단 풋터 바(footer bar)를 절대 배치하지 마세요.
3. 페이지 번호(page number)를 표시하지 마세요.
4. 로고 영역을 배치하지 마세요.
5. 콘텐츠가 슬라이드 전체 영역(full bleed)을 활용해야 합니다.
6. 슬라이드 상단이나 하단에 반복되는 장식 요소(줄, 바, 밴드)를 넣지 마세요.

■ 발표자 노트(Speaker Notes) 규칙 — 필수
모든 슬라이드에 발표자 노트(Speaker Notes)를 반드시 작성하세요. 발표자 노트는 프로그래밍을 처음 가르치는 초보 강사가 슬라이드 화면만 보면서 막힘 없이 발표할 수 있도록, 아래 항목을 포함하여 충분히 자세하게 작성합니다:

1. **도입 멘트**: 이 슬라이드를 처음 보여줄 때 강사가 말할 오프닝 한두 문장
2. **핵심 설명**: 슬라이드의 핵심 내용을 학습자에게 어떻게 설명할지 구어체로 풀어쓴 3~5문장
3. **비유/예시 안내**: 슬라이드에 비유가 있으면 "이렇게 설명하세요"라는 구체적 화법 제시
4. **학습자 반응 예상**: "이 부분에서 학습자들이 자주 하는 질문은..." 또는 "여기서 막히는 분이 있으면..."
5. **시간 안배**: "이 슬라이드는 약 2분, 실습 포함 시 5분 정도 소요됩니다"
6. **전환 멘트**: 다음 슬라이드로 넘어갈 때의 연결 문장

발표자 노트 분량 기준: 슬라이드당 최소 3문장, 실습/코드 슬라이드는 최소 5문장.
발표자 노트가 없는 슬라이드가 있으면 안 됩니다.

---

"""


def get_api_key():
    """환경변수 또는 .agent/.env에서 MANUS_API_KEY 로드"""
    key = os.environ.get("MANUS_API_KEY")
    if key:
        return key

    env_paths = [
        Path.cwd() / ".claude" / ".env",
        Path(__file__).parent.parent / ".claude" / ".env",
    ]
    for env_path in env_paths:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("MANUS_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val and not val.startswith("your_"):
                        return val
    return None


def find_project_folder(arg_path=None):
    """프로젝트 폴더 자동 탐색"""
    if arg_path:
        p = Path(arg_path)
        if (p / "06_SlidePrompt").is_dir():
            return p
        # 날짜 프리픽스 프로젝트 폴더 탐색
        for d in sorted(p.glob("20*"), reverse=True):
            if (d / "06_SlidePrompt").is_dir():
                return d

    cwd = Path.cwd()
    # 현재 디렉토리에 06_SlidePrompt가 있으면 바로 사용
    if (cwd / "06_SlidePrompt").is_dir():
        return cwd
    # 하위 프로젝트 폴더 탐색
    for d in sorted(cwd.glob("20*"), reverse=True):
        if (d / "06_SlidePrompt").is_dir():
            return d

    return None


def discover_prompts(project_dir):
    """06_SlidePrompt/ 내 프롬프트 파일 목록 반환"""
    prompt_dir = project_dir / "06_SlidePrompt"
    files = sorted(prompt_dir.glob(PROMPT_GLOB))
    return files


def create_task(api_key, prompt_content, filename):
    """Manus AI에 슬라이드 생성 Task 생성 (헤더/풋터 금지 프리픽스 자동 삽입)"""
    # 프롬프트 최상단에 규칙 프리픽스, 최하단에 export 지시 삽입
    export_suffix = "\n\n---\n\n[최종 출력 지시]\n위 교안의 모든 슬라이드를 Nano Banana Pro 이미지로 생성한 후, 반드시 하나의 PPTX 파일로 조립하여 다운로드 가능한 파일로 출력하세요. 발표자 노트도 PPTX 안에 포함하고, 별도 slide_notes.md 파일로도 저장하세요. PPTX 파일 출력은 절대 생략하지 마세요.\n"
    prefixed_content = SLIDE_GENERATION_PREFIX + prompt_content + export_suffix
    headers = {
        "API_KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "prompt": prefixed_content,
        "agentProfile": "manus-1.6-max",
        "taskMode": "agent",
        "interactiveMode": False,
        "createShareableLink": True,
    }
    resp = requests.post(
        f"{MANUS_API_BASE}/tasks",
        headers=headers,
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        error_detail = resp.text[:300] if resp.text else "No response body"
        raise requests.RequestException(
            f"{resp.status_code} {resp.reason}: {error_detail}"
        )
    data = resp.json()
    task_id = data.get("id") or data.get("task_id") or data.get("taskId")
    share_url = data.get("share_url") or data.get("task_url", "")
    if share_url:
        print(f"  share_url: {share_url}", flush=True)
    return task_id, data


def poll_task(api_key, task_id, filename, max_wait=MAX_WAIT_TIME):
    """Task 완료까지 폴링"""
    headers = {"API_KEY": api_key}
    start = time.time()
    last_status = None

    while time.time() - start < max_wait:
        try:
            resp = requests.get(
                f"{MANUS_API_BASE}/tasks/{task_id}",
                headers=headers,
                params={"convert": "true"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status", "unknown")

            if status != last_status:
                elapsed = int(time.time() - start)
                print(f"  [{filename}] status={status} ({elapsed}s)", flush=True)
                last_status = status

            if status in ("completed", "stopped", "done"):
                stop_reason = data.get("stop_reason") or data.get("stopReason", "")
                if status == "stopped" and stop_reason not in ("finish", "completed"):
                    return {"status": "failed", "reason": stop_reason, "data": data}
                return {"status": "completed", "data": data}

            if status in ("failed", "error", "cancelled"):
                return {"status": "failed", "reason": status, "data": data}

        except requests.RequestException as e:
            elapsed = int(time.time() - start)
            print(f"  [{filename}] 폴링 오류 ({elapsed}s): {e}", flush=True)

        time.sleep(POLL_INTERVAL)

    return {"status": "timeout", "reason": f"최대 대기 시간 {max_wait}초 초과"}


def extract_file_urls(task_data):
    """Task 응답에서 다운로드 가능한 파일 URL 추출

    Manus API 응답 구조:
      output: [
        { type: "message", content: [
            { type: "output_text", text: "..." },
            { type: "output_file", fileUrl: "...", fileName: "..." },
        ]},
        ...
      ]
    """
    urls = []
    seen_urls = set()

    def _add(url, name, mime=""):
        if url and url not in seen_urls:
            seen_urls.add(url)
            urls.append({"url": url, "name": name, "mime": mime})

    output = task_data.get("output") or task_data.get("outputs") or []

    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue

            # 최상위 레벨 파일 URL (구형 응답 호환)
            file_url = item.get("fileUrl") or item.get("file_url") or item.get("url")
            file_name = item.get("fileName") or item.get("file_name") or item.get("name", "")
            mime = item.get("mimeType") or item.get("mime_type", "")
            if file_url:
                _add(file_url, file_name, mime)

            # content 배열 내부의 output_file 항목 (현행 Manus 응답 형식)
            content_list = item.get("content") or []
            if isinstance(content_list, list):
                for c in content_list:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") == "output_file":
                        c_url = c.get("fileUrl") or c.get("file_url") or c.get("url", "")
                        c_name = c.get("fileName") or c.get("file_name") or c.get("name", "")
                        c_mime = c.get("mimeType") or c.get("mime_type", "")
                        _add(c_url, c_name, c_mime)

    # attachments 필드도 확인
    attachments = task_data.get("attachments") or []
    if isinstance(attachments, list):
        for att in attachments:
            if isinstance(att, dict):
                url = att.get("url") or att.get("fileUrl")
                name = att.get("file_name") or att.get("fileName") or att.get("name", "")
                _add(url, name, att.get("mimeType", ""))

    # artifacts 필드도 확인
    artifacts = task_data.get("artifacts") or []
    if isinstance(artifacts, list):
        for art in artifacts:
            if isinstance(art, dict):
                url = art.get("url") or art.get("downloadUrl")
                name = art.get("name") or art.get("fileName", "")
                _add(url, name, art.get("mimeType", ""))

    return urls


def download_file(url, save_path):
    """URL에서 파일 다운로드"""
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return save_path.stat().st_size


def strip_headers_footers(pptx_path):
    """PPTX 파일에서 헤더/풋터/페이지번호를 프로그래밍으로 제거 (후처리)"""
    try:
        from pptx import Presentation
        from pptx.util import Emu
        import copy
    except ImportError:
        print("  [WARN] python-pptx 미설치 — 후처리 건너뜀 (pip install python-pptx)", flush=True)
        return False

    prs = Presentation(str(pptx_path))
    modified = False

    # 슬라이드 크기 (기준값)
    slide_w = prs.slide_width
    slide_h = prs.slide_height
    # 상단 15% / 하단 15% 영역을 헤더/풋터 판정 기준으로 사용
    header_zone = int(slide_h * 0.12)
    footer_zone = int(slide_h * 0.88)

    for slide in prs.slides:
        shapes_to_remove = []
        for shape in slide.shapes:
            # 1) 명시적 placeholder: 슬라이드 번호, 날짜, 풋터
            if shape.is_placeholder:
                ph_idx = shape.placeholder_format.idx
                # idx 10 = slide_number, 11 = date, 12 = footer
                if ph_idx in (10, 11, 12):
                    shapes_to_remove.append(shape)
                    continue

            # 2) 위치 기반 판정: 상단 12% 또는 하단 12%에 있는 작은 텍스트 박스
            if hasattr(shape, "top") and hasattr(shape, "height") and hasattr(shape, "text"):
                top = shape.top or 0
                height = shape.height or 0
                bottom = top + height
                text = (shape.text or "").strip()

                # 빈 텍스트는 장식 요소일 가능성
                # 상단 영역의 얇은 도형 (높이 < 슬라이드 10%)
                is_thin = height < int(slide_h * 0.10)
                in_header = top < header_zone and is_thin
                in_footer = bottom > footer_zone and is_thin

                if in_header or in_footer:
                    # 텍스트가 짧거나 (페이지번호, 날짜, 제목 반복) 비어있으면 제거
                    if len(text) < 80 or not text:
                        shapes_to_remove.append(shape)
                        continue

            # 3) 도형 이름 기반: "Footer", "Header", "Slide Number", "Date" 등
            name = (shape.name or "").lower()
            if any(kw in name for kw in ("footer", "header", "slide number",
                                          "date placeholder", "page number",
                                          "ftr", "hdr", "sldnum")):
                shapes_to_remove.append(shape)

        # 제거 실행
        for shape in shapes_to_remove:
            sp = shape._element
            sp.getparent().remove(sp)
            modified = True

    # 슬라이드 마스터 / 레이아웃에서도 제거
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            for ph in list(layout.placeholders):
                if ph.placeholder_format.idx in (10, 11, 12):
                    sp = ph._element
                    sp.getparent().remove(sp)
                    modified = True

    if modified:
        prs.save(str(pptx_path))
        print(f"  [후처리] 헤더/풋터/페이지번호 제거 완료", flush=True)
    else:
        print(f"  [후처리] 제거할 헤더/풋터 없음 (깨끗한 상태)", flush=True)

    return modified


def process_single(api_key, prompt_file, output_dir):
    """단일 프롬프트 파일 처리: 제출 → 폴링 → 다운로드"""
    filename = prompt_file.stem
    short_name = filename.replace("_슬라이드 생성 프롬프트", "")
    print(f"\n{'='*60}", flush=True)
    print(f"[제출] {short_name}", flush=True)

    prompt_content = prompt_file.read_text(encoding="utf-8")

    # Task 생성
    try:
        task_id, create_data = create_task(api_key, prompt_content, short_name)
        print(f"  task_id: {task_id}", flush=True)
    except requests.RequestException as e:
        print(f"  [ERROR] Task 생성 실패: {e}", flush=True)
        return {
            "file": str(prompt_file.name),
            "status": "submit_failed",
            "error": str(e),
        }

    # 폴링
    result = poll_task(api_key, task_id, short_name)

    if result["status"] != "completed":
        print(f"  [FAIL] {result.get('reason', 'unknown')}", flush=True)
        return {
            "file": str(prompt_file.name),
            "task_id": task_id,
            "status": result["status"],
            "reason": result.get("reason", ""),
        }

    # 파일 다운로드
    task_data = result["data"]
    file_urls = extract_file_urls(task_data)

    if not file_urls:
        print(f"  [WARN] 다운로드 가능한 파일 없음 — Task 페이지 확인 필요", flush=True)
        # shareable link가 있으면 기록
        share_link = task_data.get("shareableLink") or task_data.get("shareable_link", "")
        return {
            "file": str(prompt_file.name),
            "task_id": task_id,
            "status": "completed_no_file",
            "shareable_link": share_link,
            "note": "Manus 웹에서 수동 다운로드 필요",
        }

    downloaded = []
    pptx_count = 0
    for finfo in file_urls:
        raw_name = finfo.get("name", "")
        # 파일 확장자 결정
        if raw_name:
            ext = Path(raw_name).suffix
        else:
            ext = ""
        if not ext:
            # URL에서 확장자 추출 시도
            url_path = finfo["url"].split("?")[0]
            ext = Path(url_path).suffix if "." in Path(url_path).name else ".pptx"

        # 파일명 결정: PPTX는 세션명, 기타는 원본 이름 유지
        if ext.lower() == ".pptx":
            pptx_count += 1
            save_name = f"{short_name}.pptx"
        else:
            # 발표자 노트 등 부가 파일은 원본 이름 또는 세션명+확장자
            base = Path(raw_name).stem if raw_name else f"{short_name}_notes"
            save_name = f"{short_name}_{base}{ext}" if raw_name else f"{short_name}{ext}"

        save_path = output_dir / save_name
        try:
            size = download_file(finfo["url"], save_path)
            print(f"  [OK] 다운로드: {save_name} ({size:,} bytes)", flush=True)
            # PPTX 후처리: 헤더/풋터/페이지번호 자동 제거
            if ext.lower() == ".pptx":
                strip_headers_footers(save_path)
                size = save_path.stat().st_size
            downloaded.append({"path": str(save_path), "size": size})
        except (requests.RequestException, Exception) as e:
            print(f"  [ERROR] 다운로드 실패 ({save_name}): {e}", flush=True)
            downloaded.append({"url": finfo["url"], "error": str(e)})

    return {
        "file": str(prompt_file.name),
        "task_id": task_id,
        "status": "completed",
        "downloaded": downloaded,
    }


def filter_prompts(prompts, file_filter):
    """--file 옵션으로 프롬프트 목록을 필터링"""
    if not file_filter:
        return prompts

    matched = []
    for keyword in file_filter:
        kw_lower = keyword.lower()
        for p in prompts:
            name_lower = p.name.lower()
            stem_lower = p.stem.lower()
            # 파일명 완전 일치, 부분 일치, 세션ID 일치 모두 지원
            if (kw_lower == name_lower
                    or kw_lower == stem_lower
                    or kw_lower in name_lower
                    or kw_lower in stem_lower):
                if p not in matched:
                    matched.append(p)

    return matched


def main():
    parser = argparse.ArgumentParser(
        description="Manus AI 슬라이드 생성",
        epilog="예시: python .agent/scripts/manus_slide.py project/ --file Day1_AM",
    )
    parser.add_argument("project_dir", nargs="?", help="프로젝트 폴더 경로")
    parser.add_argument("--file", "-f", nargs="+", dest="file_filter",
                        help="처리할 파일 필터 (부분 매칭 지원, 복수 지정 가능). "
                             "예: --file Day1_AM  /  -f Day1_AM Day2_PM  /  -f 환경구축")
    parser.add_argument("--resume", help="중단된 작업 로그 파일로 재개")
    parser.add_argument("--max-concurrent", type=int, default=MAX_CONCURRENT, help="동시 처리 수")
    parser.add_argument("--dry-run", action="store_true", help="실제 API 호출 없이 테스트")
    args = parser.parse_args()

    # API Key 확인
    api_key = get_api_key()
    if not api_key:
        print("[ERROR] MANUS_API_KEY를 찾을 수 없습니다.")
        print("  .agent/.env 파일에 MANUS_API_KEY를 설정하세요.")
        sys.exit(1)
    print(f"[OK] API Key 확인됨: {api_key[:10]}...{api_key[-4:]}")

    # 프로젝트 폴더 탐색
    project = find_project_folder(args.project_dir)
    if not project:
        print("[ERROR] 06_SlidePrompt/ 폴더를 찾을 수 없습니다.")
        print("  프로젝트 폴더 경로를 인자로 지정하세요.")
        sys.exit(1)
    print(f"[OK] 프로젝트: {project.name}")

    # 프롬프트 파일 탐색
    prompts = discover_prompts(project)
    if not prompts:
        print(f"[ERROR] {project / '06_SlidePrompt'} 에 프롬프트 파일이 없습니다.")
        sys.exit(1)

    # --file 필터 적용
    if args.file_filter:
        prompts = filter_prompts(prompts, args.file_filter)
        if not prompts:
            print(f"[ERROR] --file 필터 '{' '.join(args.file_filter)}'에 매칭되는 파일이 없습니다.")
            print(f"  사용 가능한 파일:")
            for p in discover_prompts(project):
                print(f"    {p.name}")
            sys.exit(1)
        print(f"[OK] --file 필터 적용: {len(prompts)}개 선택")
    print(f"[OK] 프롬프트 파일 {len(prompts)}개 발견:")
    for p in prompts:
        print(f"     {p.name}")

    # 출력 디렉토리
    output_dir = project / "07_ManusSlides"
    output_dir.mkdir(exist_ok=True)
    print(f"[OK] 출력 폴더: {output_dir}")

    if args.dry_run:
        print("\n[DRY-RUN] 실제 API 호출을 건너뜁니다.")
        return

    # 실행 시작
    start_time = time.time()
    print(f"\n{'='*60}")
    print(f"슬라이드 생성 시작 — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")

    results = []
    task_log = []

    # 순차 처리 (Manus API 제한 고려)
    for prompt_file in prompts:
        result = process_single(api_key, prompt_file, output_dir)
        results.append(result)

        # 중간 로그 저장 (중단 복구용)
        task_log.append(result)
        log_path = output_dir / "manus_task_log.json"
        log_path.write_text(
            json.dumps(task_log, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # 최종 리포트
    elapsed = int(time.time() - start_time)
    print(f"\n{'='*60}")
    print(f"슬라이드 생성 완료 — 총 {elapsed}초 소요")
    print(f"{'='*60}")

    success = [r for r in results if r["status"] == "completed"]
    no_file = [r for r in results if r["status"] == "completed_no_file"]
    failed = [r for r in results if r["status"] not in ("completed", "completed_no_file")]

    print(f"\n  성공 (PPTX 다운로드): {len(success)}개")
    for r in success:
        for d in r.get("downloaded", []):
            if "path" in d:
                print(f"    {Path(d['path']).name} ({d['size']:,} bytes)")

    if no_file:
        print(f"\n  완료 (수동 다운로드 필요): {len(no_file)}개")
        for r in no_file:
            link = r.get("shareable_link", "N/A")
            print(f"    {r['file']} → {link}")

    if failed:
        print(f"\n  실패: {len(failed)}개")
        for r in failed:
            print(f"    {r['file']}: {r.get('reason', r.get('error', 'unknown'))}")

    print(f"\n  로그: {output_dir / 'manus_task_log.json'}")

    # 최종 리포트 저장
    report = {
        "generated_at": datetime.now().isoformat(),
        "project": str(project),
        "total_files": len(prompts),
        "success": len(success),
        "no_file": len(no_file),
        "failed": len(failed),
        "elapsed_seconds": elapsed,
        "results": results,
    }
    report_path = output_dir / "generation_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  리포트: {report_path}")


if __name__ == "__main__":
    main()
