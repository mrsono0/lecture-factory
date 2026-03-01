#!/usr/bin/env python3
"""
Agent Execution Logger
Lecture Factory 로깅 프로토콜(.agent/logging-protocol.md) 구현

사용법:
    from agent_logger import AgentLogger

    logger = AgentLogger(
        workflow="01_Lecture_Planning",
        run_id="run_20260224_143005",
        model_config_path=".opencode/oh-my-opencode.jsonc"
    )

    # START 이벤트 기록
    logger.log_start(
        step_id="step_1_trend",
        agent="A1_Trend_Researcher",
        category="deep",
        action="research_trend",
        input_bytes=15000
    )

    # ... 에이전트 실행 ...

    # END 이벤트 기록
    logger.log_end(
        step_id="step_1_trend",
        output_bytes=28500,
        duration_sec=274
    )

특징:
- 같은 날 같은 파이프라인 재실행 시 **자동으로 append** (덮어쓰기 금지)
- JSONL 형식 (한 줄에 하나의 JSON 객체)
- UTF-8 인코딩
- model_config에서 category→model 자동 매핑
- 토큰/비용 자동 추정
"""

import json
import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class AgentLogger:
    """
    Lecture Factory Agent Execution Logger

    로깅 프로토콜: .agent/logging-protocol.md
    """

    # 비용 테이블 (USD per 1K tokens)
    COST_TABLE = {
        "quick": {"input": 0.00025, "output": 0.00125},
        "unspecified-low": {"input": 0.003, "output": 0.015},
        "deep": {"input": 0.015, "output": 0.075},
        "visual-engineering": {"input": 0.003, "output": 0.015},
        "writing": {"input": 0.003, "output": 0.015},
        "micro-writing": {"input": 0.003, "output": 0.015},
        "curriculum-chunking": {"input": 0.003, "output": 0.015},
        "ultrabrain": {"input": 0.015, "output": 0.075},
        "artistry": {"input": 0.003, "output": 0.015},
        "unspecified-high": {"input": 0.015, "output": 0.075},
        "research": {"input": 0.002, "output": 0.012},
        "curriculum-architecture": {"input": 0.003, "output": 0.015},
        "glm5": {"input": 0.003, "output": 0.015},
        "material-aggregation": {"input": 0.003, "output": 0.015},
        "instructor-support-codex": {"input": 0.015, "output": 0.075},
    }

    BYTES_PER_TOKEN = 3.3

    def __init__(
        self,
        workflow: str,
        run_id: Optional[str] = None,
        parent_run_id: Optional[str] = None,
        model_config_path: str = ".opencode/oh-my-opencode.jsonc",
        log_dir: str = ".agent/logs",
    ):
        """
        로거 초기화

        Args:
            workflow: 파이프라인명 (예: "01_Lecture_Planning")
            run_id: 실행 ID (없으면 자동 생성)
            parent_run_id: E2E 실행 시 마스터 run_id
            model_config_path: 모델 설정 파일 경로
            log_dir: 로그 디렉토리 경로
        """
        self.workflow = workflow
        self.run_id = run_id or self._generate_run_id()
        self.parent_run_id = parent_run_id
        self.model_config_path = model_config_path
        self.log_dir = Path(log_dir)

        # 로그 디렉토리 생성
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # 로그 파일 경로: 같은 날 같은 파이프라인은 동일 파일에 append
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_path = self.log_dir / f"{today}_{workflow}.jsonl"

        # model_config 로드
        self.category_to_model = self._load_model_config()

        # 실행 중인 step의 시작 시간 추적
        self._start_times: Dict[str, float] = {}

        # step별 category/input_bytes/agent/action/parallel_group/retry 추적 (log_end에서 조회용)
        self._step_categories: Dict[str, str] = {}
        self._step_input_bytes: Dict[str, int] = {}
        self._step_meta: Dict[
            str, Dict[str, Any]
        ] = {}  # agent, action, parallel_group, retry

    def _generate_run_id(self) -> str:
        """run_id 생성: run_{YYYYMMDD}_{HHMMSS}"""
        return datetime.now().strftime("run_%Y%m%d_%H%M%S")

    def _load_model_config(self) -> Dict[str, str]:
        """model_config에서 category→model 매핑 로드"""
        try:
            config_path = Path(self.model_config_path)
            if config_path.exists():
                # JSONC (JSON with comments) 처리 — 문자열 내부 // 보존
                content = config_path.read_text(encoding="utf-8")
                content = re.sub(r"(?<!:)//.*$", "", content, flags=re.MULTILINE)
                config = json.loads(content)

                categories = config.get("categories", {})
                return {
                    cat: info.get("model", "unknown")
                    for cat, info in categories.items()
                }
        except Exception as e:
            print(f"[WARN] model_config 로드 실패: {e}", file=sys.stderr)

        return {}

    def _get_model_for_category(self, category: str) -> str:
        """category에 해당하는 model 조회"""
        return self.category_to_model.get(category, "unknown")

    def _calculate_tokens(self, bytes_count: int) -> int:
        """바이트 수를 토큰 수로 변환"""
        return round(bytes_count / self.BYTES_PER_TOKEN)

    def _calculate_cost(
        self, input_tokens: int, output_tokens: int, category: str
    ) -> float:
        """비용 계산 (USD)"""
        prices = self.COST_TABLE.get(category, self.COST_TABLE["deep"])
        input_cost = input_tokens * prices["input"] / 1000
        output_cost = output_tokens * prices["output"] / 1000
        return round(input_cost + output_cost, 6)

    def _write_log(self, entry: Dict[str, Any]) -> None:
        """
        로그 엔트리를 파일에 기록 (append 모드)

        프로토콜: 같은 날 같은 파이프라인은 동일 파일에 append
        """
        # 파일이 존재하지 않아도 'a' 모드는 자동 생성
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_start(
        self,
        step_id: str,
        agent: str,
        category: str,
        action: str,
        input_bytes: int = 0,
        parallel_group: Optional[str] = None,
        retry: int = 0,
    ) -> Dict[str, Any]:
        """
        START 이벤트 기록

        Args:
            step_id: 워크플로우 YAML의 step id
            agent: 에이전트명
            category: LLM 카테고리
            action: 워크플로우 YAML의 action 필드
            input_bytes: 입력 데이터 크기 (bytes)
            parallel_group: 병렬 실행 그룹
            retry: 재시도 횟수

        Returns:
            기록된 로그 엔트리
        """
        ts = datetime.now().isoformat()
        self._start_times[step_id] = time.time()
        self._step_categories[step_id] = category
        self._step_input_bytes[step_id] = input_bytes
        self._step_meta[step_id] = {
            "agent": agent,
            "action": action,
            "parallel_group": parallel_group,
            "retry": retry,
        }

        entry = {
            "run_id": self.run_id,
            "parent_run_id": self.parent_run_id,
            "ts": ts,
            "status": "START",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": agent,
            "category": category,
            "model": self._get_model_for_category(category),
            "action": action,
            "parallel_group": parallel_group,
            "retry": retry,
        }

        self._write_log(entry)
        print(f"[LOG:START] {step_id} ({agent})", file=sys.stderr)
        return entry

    def log_end(
        self,
        step_id: str,
        output_bytes: int,
        duration_sec: Optional[float] = None,
        decision: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        END 이벤트 기록

        Args:
            step_id: 워크플로우 YAML의 step id
            output_bytes: 출력 데이터 크기 (bytes)
            duration_sec: 소요 시간 (초) - 없으면 START부터 자동 계산
            decision: QA/승인 판정 (approved/rejected/null)

        Returns:
            기록된 로그 엔트리
        """
        ts = datetime.now().isoformat()

        # duration 계산
        if duration_sec is None:
            start_time = self._start_times.get(step_id)
            if start_time:
                duration_sec = time.time() - start_time
            else:
                duration_sec = 0

        # START 이벤트에서 input_bytes 가져오기 (또는 0)
        input_bytes = self._step_input_bytes.pop(step_id, 0)

        # 토큰/비용 계산
        category = self._get_category_for_step(step_id)
        est_input_tokens = self._calculate_tokens(input_bytes)
        est_output_tokens = self._calculate_tokens(output_bytes)
        est_cost_usd = self._calculate_cost(
            est_input_tokens, est_output_tokens, category
        )

        # START에서 저장한 메타데이터 복원 (공통 필드)
        meta = self._step_meta.pop(step_id, {})

        entry = {
            "run_id": self.run_id,
            "parent_run_id": self.parent_run_id,
            "ts": ts,
            "status": "END",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": meta.get("agent"),
            "category": category,
            "model": self._get_model_for_category(category),
            "action": meta.get("action"),
            "parallel_group": meta.get("parallel_group"),
            "retry": meta.get("retry", 0),
            "duration_sec": round(duration_sec, 1),
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "est_input_tokens": est_input_tokens,
            "est_output_tokens": est_output_tokens,
            "est_cost_usd": est_cost_usd,
            "decision": decision,
        }

        self._write_log(entry)
        print(
            f"[LOG:END] {step_id} ({duration_sec:.1f}s, ${est_cost_usd:.4f})",
            file=sys.stderr,
        )
        return entry

    def log_fail(
        self,
        step_id: str,
        agent: str,
        category: str,
        action: str,
        error_message: str,
        retry: int = 0,
    ) -> Dict[str, Any]:
        """FAIL 이벤트 기록"""
        ts = datetime.now().isoformat()

        entry = {
            "run_id": self.run_id,
            "ts": ts,
            "status": "FAIL",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": agent,
            "category": category,
            "model": self._get_model_for_category(category),
            "action": action,
            "error_message": error_message,
            "retry": retry,
        }

        self._write_log(entry)
        print(f"[LOG:FAIL] {step_id} - {error_message}", file=sys.stderr)
        return entry

    def log_retry(
        self, step_id: str, agent: str, category: str, action: str, retry: int
    ) -> Dict[str, Any]:
        """RETRY 이벤트 기록"""
        ts = datetime.now().isoformat()

        entry = {
            "run_id": self.run_id,
            "ts": ts,
            "status": "RETRY",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": agent,
            "category": category,
            "model": self._get_model_for_category(category),
            "action": action,
            "retry": retry,
        }

        self._write_log(entry)
        print(f"[LOG:RETRY] {step_id} (retry={retry})", file=sys.stderr)
        return entry

    def log_decision(
        self,
        step_id: str,
        agent: str,
        category: str,
        action: str,
        decision: str,
        parallel_group: Optional[str] = None,
        retry: int = 0,
    ) -> Dict[str, Any]:
        """DECISION 이벤트 기록 (QA/승인 스텝 판정)"""
        ts = datetime.now().isoformat()

        entry = {
            "run_id": self.run_id,
            "parent_run_id": self.parent_run_id,
            "ts": ts,
            "status": "DECISION",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": agent,
            "category": category,
            "model": self._get_model_for_category(category),
            "action": action,
            "parallel_group": parallel_group,
            "retry": retry,
            "decision": decision,
        }

        self._write_log(entry)
        print(f"[LOG:DECISION] {step_id} ({decision})", file=sys.stderr)
        return entry

    def log_session_start(
        self,
        step_id: str,
        agent: str,
        category: str,
        action: str,
        session_id: str,
        session_name: str,
        parallel_group: Optional[str] = None,
        retry: int = 0,
    ) -> Dict[str, Any]:
        """SESSION_START 이벤트 기록 (Session-Parallel 모델)"""
        ts = datetime.now().isoformat()

        entry = {
            "run_id": self.run_id,
            "parent_run_id": self.parent_run_id,
            "ts": ts,
            "status": "SESSION_START",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": agent,
            "category": category,
            "model": self._get_model_for_category(category),
            "action": action,
            "parallel_group": parallel_group,
            "retry": retry,
            "session_id": session_id,
            "session_name": session_name,
        }

        self._write_log(entry)
        print(f"[LOG:SESSION_START] {session_id} ({session_name})", file=sys.stderr)
        return entry

    def log_session_end(
        self,
        step_id: str,
        session_id: str,
        session_name: str,
        input_bytes: int,
        output_bytes: int,
        output_files: list,
        total_slides: Optional[int] = None,
        duration_sec: Optional[float] = None,
        decision: Optional[str] = None,
    ) -> Dict[str, Any]:
        """SESSION_END 이벤트 기록 (Session-Parallel 모델)"""
        ts = datetime.now().isoformat()

        if duration_sec is None:
            start_time = self._start_times.get(step_id)
            if start_time:
                duration_sec = time.time() - start_time
            else:
                duration_sec = 0

        category = self._get_category_for_step(step_id)
        est_input_tokens = self._calculate_tokens(input_bytes)
        est_output_tokens = self._calculate_tokens(output_bytes)
        est_cost_usd = self._calculate_cost(
            est_input_tokens, est_output_tokens, category
        )

        # START에서 저장한 메타데이터 복원 (공통 필드)
        meta = self._step_meta.pop(step_id, {})

        entry = {
            "run_id": self.run_id,
            "parent_run_id": self.parent_run_id,
            "ts": ts,
            "status": "SESSION_END",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": meta.get("agent"),
            "category": category,
            "model": self._get_model_for_category(category),
            "action": meta.get("action"),
            "parallel_group": meta.get("parallel_group"),
            "retry": meta.get("retry", 0),
            "duration_sec": round(duration_sec, 1),
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "est_input_tokens": est_input_tokens,
            "est_output_tokens": est_output_tokens,
            "est_cost_usd": est_cost_usd,
            "decision": decision,
            "session_id": session_id,
            "session_name": session_name,
            "total_slides": total_slides,
            "output_files": output_files,
        }

        self._write_log(entry)
        print(
            f"[LOG:SESSION_END] {session_id} ({duration_sec:.1f}s, ${est_cost_usd:.4f})",
            file=sys.stderr,
        )
        return entry

    def log_external_tool_start(
        self,
        step_id: str,
        agent: str,
        category: str,
        action: str,
        tool_name: str,
        tool_action: str,
        notebook_id: Optional[str] = None,
        retry: int = 0,
    ) -> float:
        """
        EXTERNAL_TOOL_START 이벤트 기록

        Returns:
            시작 시간 (time.time()) - log_external_tool_end에 전달
        """
        ts = datetime.now().isoformat()
        start_time = time.time()

        entry = {
            "run_id": self.run_id,
            "ts": ts,
            "status": "EXTERNAL_TOOL_START",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": agent,
            "category": category,
            "model": self._get_model_for_category(category),
            "action": action,
            "tool_name": tool_name,
            "tool_action": tool_action,
            "tool_input_bytes": 0,
            "notebook_id": notebook_id,
            "retry": retry,
        }

        self._write_log(entry)
        print(f"[LOG:TOOL_START] {tool_name}.{tool_action}", file=sys.stderr)
        return start_time

    def log_external_tool_end(
        self,
        step_id: str,
        agent: str,
        category: str,
        action: str,
        tool_name: str,
        tool_action: str,
        start_time: float,
        output_bytes: int,
        status: str = "success",
        error: Optional[str] = None,
        notebook_id: Optional[str] = None,
        retry: int = 0,
    ) -> Dict[str, Any]:
        """EXTERNAL_TOOL_END 이벤트 기록"""
        ts = datetime.now().isoformat()
        duration = time.time() - start_time

        entry = {
            "run_id": self.run_id,
            "ts": ts,
            "status": "EXTERNAL_TOOL_END",
            "workflow": self.workflow,
            "step_id": step_id,
            "agent": agent,
            "category": category,
            "model": self._get_model_for_category(category),
            "action": action,
            "tool_name": tool_name,
            "tool_action": tool_action,
            "tool_input_bytes": 0,
            "tool_output_bytes": output_bytes,
            "tool_duration_sec": round(duration, 3),
            "tool_status": status,
            "tool_error": error,
            "notebook_id": notebook_id,
            "retry": retry,
        }

        self._write_log(entry)
        print(
            f"[LOG:TOOL_END] {tool_name}.{tool_action} ({duration:.1f}s, {status})",
            file=sys.stderr,
        )
        return entry

    def _get_category_for_step(self, step_id: str) -> str:
        """step_id에 대응하는 category 조회 (log_start에서 저장된 매핑 사용)"""
        return self._step_categories.pop(step_id, "deep")

    def get_log_path(self) -> Path:
        """현재 로그 파일 경로 반환"""
        return self.log_path


# Bash 스크립트용 헬퍼 함수
def get_log_path(workflow: str, log_dir: str = ".agent/logs") -> str:
    """
    오늘 날짜의 로그 파일 경로 반환 (Bash 스크립트 연동용)

    Returns:
        로그 파일 전체 경로 (이미 존재해도 append 모드로 사용)
    """
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = Path(log_dir) / f"{today}_{workflow}.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return str(log_path)


# ─── CLI 상태 관리 ───

STATE_DIR = Path(".agent/logs/.state")


def _state_path(workflow: str, run_id: str) -> Path:
    """실행 중인 step 시작 시간을 저장하는 상태 파일 경로"""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return STATE_DIR / f"{run_id}_{workflow}.json"


def _load_state(workflow: str, run_id: str) -> Dict[str, Any]:
    p = _state_path(workflow, run_id)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def _save_state(workflow: str, run_id: str, state: Dict[str, Any]) -> None:
    p = _state_path(workflow, run_id)
    p.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")


def _state_pop_step(state: Dict[str, Any], step_id: str) -> Dict[str, Any]:
    value = state.pop(step_id, None)
    if isinstance(value, dict):
        return value
    return {}


def _state_get_ended(state: Dict[str, Any]) -> Dict[str, Any]:
    value = state.get("__ended__", {})
    if isinstance(value, dict):
        return value
    return {}


def _state_mark_ended(state: Dict[str, Any], step_id: str) -> None:
    ended = _state_get_ended(state)
    ended[step_id] = datetime.now().isoformat()
    state["__ended__"] = ended


def _state_clear_ended(state: Dict[str, Any], step_id: str) -> None:
    ended = _state_get_ended(state)
    if step_id in ended:
        ended.pop(step_id, None)
        state["__ended__"] = ended


# ─── CLI 진입점 ───


def main():
    parser = argparse.ArgumentParser(
        description="Agent Logger CLI — 오케스트레이터용 로깅 인터페이스",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""사용 예시:
  # 1) 파이프라인 시작 — run_id 생성 및 출력
  RUN_ID=$(python .agent/scripts/agent_logger.py init --workflow 02_Material_Writing)

  # 2) step START 기록
  python .agent/scripts/agent_logger.py start \\
    --workflow 02_Material_Writing --run-id $RUN_ID \\
    --step-id step_1 --agent A1_Source_Miner --category deep \\
    --action source_mining --input-bytes 15000

  # 3) step END 기록
  python .agent/scripts/agent_logger.py end \\
    --workflow 02_Material_Writing --run-id $RUN_ID \\
    --step-id step_1 --output-bytes 28500

  # 4) step FAIL 기록
  python .agent/scripts/agent_logger.py fail \\
    --workflow 02_Material_Writing --run-id $RUN_ID \\
    --step-id step_1 --agent A1_Source_Miner --category deep \\
    --action source_mining --error "timeout after 300s"
""",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── init ──
    p_init = sub.add_parser("init", help="파이프라인 시작: run_id 생성 및 출력")
    p_init.add_argument("--workflow", required=True)
    p_init.add_argument("--parent-run-id", default=None)

    # ── start ──
    p_start = sub.add_parser("start", help="step START 이벤트 기록")
    p_start.add_argument("--workflow", required=True)
    p_start.add_argument("--run-id", required=True)
    p_start.add_argument("--step-id", required=True)
    p_start.add_argument("--agent", required=True)
    p_start.add_argument("--category", required=True)
    p_start.add_argument("--action", required=True)
    p_start.add_argument("--input-bytes", type=int, default=0)
    p_start.add_argument("--parallel-group", default=None)
    p_start.add_argument("--retry", type=int, default=0)
    p_start.add_argument("--parent-run-id", default=None)

    # ── end ──
    p_end = sub.add_parser("end", help="step END 이벤트 기록")
    p_end.add_argument("--workflow", required=True)
    p_end.add_argument("--run-id", required=True)
    p_end.add_argument("--step-id", required=True)
    p_end.add_argument("--output-bytes", type=int, required=True)
    p_end.add_argument("--decision", default=None)

    # ── fail ──
    p_fail = sub.add_parser("fail", help="step FAIL 이벤트 기록")
    p_fail.add_argument("--workflow", required=True)
    p_fail.add_argument("--run-id", required=True)
    p_fail.add_argument("--step-id", required=True)
    p_fail.add_argument("--agent", required=True)
    p_fail.add_argument("--category", required=True)
    p_fail.add_argument("--action", required=True)
    p_fail.add_argument("--error", required=True)
    p_fail.add_argument("--retry", type=int, default=0)

    # ── decision ──
    p_decision = sub.add_parser("decision", help="DECISION 이벤트 기록 (QA/승인 판정)")
    p_decision.add_argument("--workflow", required=True)
    p_decision.add_argument("--run-id", required=True)
    p_decision.add_argument("--step-id", required=True)
    p_decision.add_argument("--agent", required=True)
    p_decision.add_argument("--category", required=True)
    p_decision.add_argument("--action", required=True)
    p_decision.add_argument(
        "--decision",
        required=True,
        choices=["approved", "partial_rejected", "rejected"],
    )
    p_decision.add_argument("--parallel-group", default=None)
    p_decision.add_argument("--retry", type=int, default=0)

    # ── retry ──
    p_retry = sub.add_parser("retry", help="RETRY 이벤트 기록")
    p_retry.add_argument("--workflow", required=True)
    p_retry.add_argument("--run-id", required=True)
    p_retry.add_argument("--step-id", required=True)
    p_retry.add_argument("--agent", required=True)
    p_retry.add_argument("--category", required=True)
    p_retry.add_argument("--action", required=True)
    p_retry.add_argument("--retry", type=int, required=True)

    # ── session-start ──
    p_ss = sub.add_parser("session-start", help="SESSION_START 이벤트 기록")
    p_ss.add_argument("--workflow", required=True)
    p_ss.add_argument("--run-id", required=True)
    p_ss.add_argument("--step-id", required=True)
    p_ss.add_argument("--agent", required=True)
    p_ss.add_argument("--category", required=True)
    p_ss.add_argument("--action", required=True)
    p_ss.add_argument("--session-id", required=True)
    p_ss.add_argument("--session-name", required=True)
    p_ss.add_argument("--parallel-group", default=None)
    p_ss.add_argument("--retry", type=int, default=0)
    p_ss.add_argument("--input-bytes", type=int, default=0)
    p_ss.add_argument("--parent-run-id", default=None)

    # ── session-end ──
    p_se = sub.add_parser("session-end", help="SESSION_END 이벤트 기록")
    p_se.add_argument("--workflow", required=True)
    p_se.add_argument("--run-id", required=True)
    p_se.add_argument("--step-id", required=True)
    p_se.add_argument("--session-id", required=True)
    p_se.add_argument("--session-name", required=True)
    p_se.add_argument("--input-bytes", type=int, default=0)
    p_se.add_argument("--output-bytes", type=int, required=True)
    p_se.add_argument("--output-files", nargs="*", default=[])
    p_se.add_argument("--total-slides", type=int, default=None)
    p_se.add_argument("--decision", default=None)


    # ── external-tool-start ──
    p_ets = sub.add_parser("external-tool-start", help="EXTERNAL_TOOL_START 이벤트 기록")
    p_ets.add_argument("--workflow", required=True)
    p_ets.add_argument("--run-id", required=True)
    p_ets.add_argument("--step-id", required=True)
    p_ets.add_argument("--agent", required=True)
    p_ets.add_argument("--category", required=True)
    p_ets.add_argument("--action", required=True)
    p_ets.add_argument("--tool-name", required=True)
    p_ets.add_argument("--tool-action", required=True)
    p_ets.add_argument("--notebook-id", default=None)
    p_ets.add_argument("--retry", type=int, default=0)

    # ── external-tool-end ──
    p_ete = sub.add_parser("external-tool-end", help="EXTERNAL_TOOL_END 이벤트 기록")
    p_ete.add_argument("--workflow", required=True)
    p_ete.add_argument("--run-id", required=True)
    p_ete.add_argument("--step-id", required=True)
    p_ete.add_argument("--agent", required=True)
    p_ete.add_argument("--category", required=True)
    p_ete.add_argument("--action", required=True)
    p_ete.add_argument("--tool-name", required=True)
    p_ete.add_argument("--tool-action", required=True)
    p_ete.add_argument("--ext-key", required=True, help="external-tool-start가 stdout으로 출력한 상태 키")
    p_ete.add_argument("--output-bytes", type=int, required=True)
    p_ete.add_argument("--tool-status", default="success", choices=["success", "timeout", "error"])
    p_ete.add_argument("--tool-error", default=None)
    p_ete.add_argument("--notebook-id", default=None)
    p_ete.add_argument("--retry", type=int, default=0)

    args = parser.parse_args()

    if args.command == "init":
        logger = AgentLogger(
            workflow=args.workflow,
            parent_run_id=args.parent_run_id,
        )
        # stdout에 run_id만 출력 (bash 변수 캡처용)
        print(logger.run_id)

    elif args.command == "start":
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
            parent_run_id=args.parent_run_id,
        )
        logger.log_start(
            step_id=args.step_id,
            agent=args.agent,
            category=args.category,
            action=args.action,
            input_bytes=args.input_bytes,
            parallel_group=args.parallel_group,
            retry=args.retry,
        )
        # 상태 파일에 시작 시간 + category 저장 (end에서 사용)
        state = _load_state(args.workflow, args.run_id)
        _state_clear_ended(state, args.step_id)
        state[args.step_id] = {
            "start_time": time.time(),
            "category": args.category,
            "input_bytes": args.input_bytes,
            "agent": args.agent,
            "action": args.action,
            "parallel_group": args.parallel_group,
            "retry": args.retry,
        }
        _save_state(args.workflow, args.run_id, state)

    elif args.command == "end":
        # 상태 파일에서 시작 시간 + category 복원
        state = _load_state(args.workflow, args.run_id)
        ended = _state_get_ended(state)
        if args.step_id in ended:
            print(
                f"[LOG:ERROR] duplicate END blocked: workflow={args.workflow} run_id={args.run_id} step_id={args.step_id}",
                file=sys.stderr,
            )
            sys.exit(2)

        step_state = _state_pop_step(state, args.step_id)
        if not step_state:
            print(
                f"[LOG:ERROR] END without START blocked: workflow={args.workflow} run_id={args.run_id} step_id={args.step_id}",
                file=sys.stderr,
            )
            sys.exit(2)

        start_time = step_state.get("start_time")
        category = step_state.get("category", "deep")
        input_bytes = step_state.get("input_bytes", 0)
        agent = step_state.get("agent")
        action = step_state.get("action")
        parallel_group = step_state.get("parallel_group")
        retry = step_state.get("retry", 0)

        duration_sec = None
        if start_time:
            duration_sec = time.time() - start_time
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
        )
        # category/input_bytes/meta를 수동 주입 (CLI 모드)
        logger._step_categories[args.step_id] = category
        logger._step_input_bytes[args.step_id] = input_bytes
        logger._step_meta[args.step_id] = {
            "agent": agent,
            "action": action,
            "parallel_group": parallel_group,
            "retry": retry,
        }
        logger.log_end(
            step_id=args.step_id,
            output_bytes=args.output_bytes,
            duration_sec=duration_sec,
            decision=args.decision,
        )
        _state_mark_ended(state, args.step_id)
        _save_state(args.workflow, args.run_id, state)

    elif args.command == "fail":
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
        )
        logger.log_fail(
            step_id=args.step_id,
            agent=args.agent,
            category=args.category,
            action=args.action,
            error_message=args.error,
            retry=args.retry,
        )

    elif args.command == "decision":
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
        )
        logger.log_decision(
            step_id=args.step_id,
            agent=args.agent,
            category=args.category,
            action=args.action,
            decision=args.decision,
            parallel_group=args.parallel_group,
            retry=args.retry,
        )

    elif args.command == "retry":
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
        )
        logger.log_retry(
            step_id=args.step_id,
            agent=args.agent,
            category=args.category,
            action=args.action,
            retry=args.retry,
        )

    elif args.command == "session-start":
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
            parent_run_id=args.parent_run_id,
        )
        logger.log_session_start(
            step_id=args.step_id,
            agent=args.agent,
            category=args.category,
            action=args.action,
            session_id=args.session_id,
            session_name=args.session_name,
            parallel_group=args.parallel_group,
            retry=args.retry,
        )
        # 상태 파일에 시작 시간 + 메타데이터 저장 (session-end에서 사용)
        state = _load_state(args.workflow, args.run_id)
        _state_clear_ended(state, args.step_id)
        state[args.step_id] = {
            "start_time": time.time(),
            "category": args.category,
            "input_bytes": args.input_bytes,
            "agent": args.agent,
            "action": args.action,
            "parallel_group": args.parallel_group,
            "retry": args.retry,
        }
        _save_state(args.workflow, args.run_id, state)

    elif args.command == "session-end":
        # 상태 파일에서 시작 시간 + 메타데이터 복원
        state = _load_state(args.workflow, args.run_id)
        ended = _state_get_ended(state)
        if args.step_id in ended:
            print(
                f"[LOG:ERROR] duplicate SESSION_END blocked: workflow={args.workflow} run_id={args.run_id} step_id={args.step_id}",
                file=sys.stderr,
            )
            sys.exit(2)

        step_state = _state_pop_step(state, args.step_id)
        if not step_state:
            print(
                f"[LOG:ERROR] SESSION_END without SESSION_START blocked: workflow={args.workflow} run_id={args.run_id} step_id={args.step_id}",
                file=sys.stderr,
            )
            sys.exit(2)

        start_time = step_state.get("start_time")
        category = step_state.get("category", "deep")
        input_bytes_state = step_state.get("input_bytes", 0)
        agent = step_state.get("agent")
        action = step_state.get("action")
        parallel_group = step_state.get("parallel_group")
        retry = step_state.get("retry", 0)

        duration_sec = None
        if start_time:
            duration_sec = time.time() - start_time
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
        )
        # category/meta를 수동 주입 (CLI 모드)
        logger._step_categories[args.step_id] = category
        logger._step_input_bytes[args.step_id] = args.input_bytes or input_bytes_state
        logger._step_meta[args.step_id] = {
            "agent": agent,
            "action": action,
            "parallel_group": parallel_group,
            "retry": retry,
        }
        logger.log_session_end(
            step_id=args.step_id,
            session_id=args.session_id,
            session_name=args.session_name,
            input_bytes=args.input_bytes or input_bytes_state,
            output_bytes=args.output_bytes,
            output_files=args.output_files,
            total_slides=args.total_slides,
            duration_sec=duration_sec,
            decision=args.decision,
        )
        _state_mark_ended(state, args.step_id)
        _save_state(args.workflow, args.run_id, state)


    elif args.command == "external-tool-start":
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
        )
        start_time = logger.log_external_tool_start(
            step_id=args.step_id,
            agent=args.agent,
            category=args.category,
            action=args.action,
            tool_name=args.tool_name,
            tool_action=args.tool_action,
            notebook_id=args.notebook_id,
            retry=args.retry,
        )
        # 상태 파일에 시작 시간 저장 (external-tool-end에서 사용)
        # 타임스탬프 기반 키로 같은 step 내 다중 호출 충돌 방지
        state = _load_state(args.workflow, args.run_id)
        ext_key = f"{args.step_id}__ext__{args.tool_name}_{int(start_time * 1000)}"
        state[ext_key] = {
            "start_time": start_time,
            "agent": args.agent,
            "category": args.category,
            "action": args.action,
            "tool_name": args.tool_name,
            "tool_action": args.tool_action,
            "notebook_id": args.notebook_id,
            "retry": args.retry,
        }
        _save_state(args.workflow, args.run_id, state)
        # stdout에 ext_key 출력 (bash 변수 캡처용: EXT_KEY=$(python3 ... external-tool-start ...))
        print(ext_key)

    elif args.command == "external-tool-end":
        state = _load_state(args.workflow, args.run_id)
        ext_state = state.pop(args.ext_key, None)
        start_time = ext_state.get("start_time", time.time()) if ext_state else time.time()
        logger = AgentLogger(
            workflow=args.workflow,
            run_id=args.run_id,
        )
        logger.log_external_tool_end(
            step_id=args.step_id,
            agent=args.agent,
            category=args.category,
            action=args.action,
            tool_name=args.tool_name,
            tool_action=args.tool_action,
            start_time=start_time,
            output_bytes=args.output_bytes,
            status=args.tool_status,
            error=args.tool_error,
            notebook_id=args.notebook_id,
            retry=args.retry,
        )
        _save_state(args.workflow, args.run_id, state)

if __name__ == "__main__":
    main()
