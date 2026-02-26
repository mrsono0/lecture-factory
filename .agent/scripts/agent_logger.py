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
import os
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
        "deep": {"input": 0.003, "output": 0.015},
        "visual-engineering": {"input": 0.003, "output": 0.015},
        "writing": {"input": 0.003, "output": 0.015},
        "micro-writing": {"input": 0.003, "output": 0.015},
        "curriculum-chunking": {"input": 0.003, "output": 0.015},
        "ultrabrain": {"input": 0.015, "output": 0.075},
        "artistry": {"input": 0.015, "output": 0.075},
        "unspecified-high": {"input": 0.015, "output": 0.075},
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

        # step별 category/input_bytes 추적 (log_end에서 조회용)
        self._step_categories: Dict[str, str] = {}
        self._step_input_bytes: Dict[str, int] = {}

    def _generate_run_id(self) -> str:
        """run_id 생성: run_{YYYYMMDD}_{HHMMSS}"""
        return datetime.now().strftime("run_%Y%m%d_%H%M%S")

    def _load_model_config(self) -> Dict[str, str]:
        """model_config에서 category→model 매핑 로드"""
        try:
            config_path = Path(self.model_config_path)
            if config_path.exists():
                # JSONC (JSON with comments) 처리
                content = config_path.read_text(encoding="utf-8")
                # 주석 제거 (간단한 처리)
                lines = []
                for line in content.split("\n"):
                    if "//" in line:
                        line = line[: line.index("//")]
                    lines.append(line)
                config = json.loads("\n".join(lines))

                categories = config.get("categories", {})
                return {
                    cat: info.get("model", "unknown")
                    for cat, info in categories.items()
                }
        except Exception as e:
            print(f"[WARN] model_config 로드 실패: {e}")

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
        print(f"[LOG:START] {step_id} ({agent})")
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

        entry = {
            "run_id": self.run_id,
            "ts": ts,
            "status": "END",
            "workflow": self.workflow,
            "step_id": step_id,
            "duration_sec": round(duration_sec, 1),
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "est_input_tokens": est_input_tokens,
            "est_output_tokens": est_output_tokens,
            "est_cost_usd": est_cost_usd,
            "decision": decision,
        }

        self._write_log(entry)
        print(f"[LOG:END] {step_id} ({duration_sec:.1f}s, ${est_cost_usd:.4f})")
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
        print(f"[LOG:FAIL] {step_id} - {error_message}")
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
        print(f"[LOG:RETRY] {step_id} (retry={retry})")
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
        print(f"[LOG:SESSION_START] {session_id} ({session_name})")
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

        entry = {
            "run_id": self.run_id,
            "ts": ts,
            "status": "SESSION_END",
            "workflow": self.workflow,
            "step_id": step_id,
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
            f"[LOG:SESSION_END] {session_id} ({duration_sec:.1f}s, ${est_cost_usd:.4f})"
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
        print(f"[LOG:TOOL_START] {tool_name}.{tool_action}")
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
        print(f"[LOG:TOOL_END] {tool_name}.{tool_action} ({duration:.1f}s, {status})")
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


if __name__ == "__main__":
    # 테스트 실행
    print("AgentLogger 테스트")

    logger = AgentLogger(
        workflow="01_Lecture_Planning",
        model_config_path="../../.opencode/oh-my-opencode.jsonc",
    )

    print(f"로그 파일: {logger.get_log_path()}")
    print(f"Run ID: {logger.run_id}")

    # 테스트 이벤트 기록
    logger.log_start(
        step_id="step_0_scope",
        agent="A0_Orchestrator",
        category="unspecified-low",
        action="analyze_request",
        input_bytes=8000,
    )

    import time

    time.sleep(0.5)

    logger.log_end(
        step_id="step_0_scope",
        output_bytes=4000,
    )

    print(f"\n로그 파일 확인: {logger.get_log_path()}")
    print("파일 내용:")
    with open(logger.get_log_path(), "r") as f:
        for line in f:
            print(json.loads(line))
