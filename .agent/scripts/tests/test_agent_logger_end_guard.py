#!/usr/bin/env python3
"""Regression tests for agent_logger END guard behavior."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
LOGGER = ROOT / ".agent" / "scripts" / "agent_logger.py"


def _run(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LOGGER), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )


def _read_log(cwd: Path, workflow: str) -> list[dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    path = cwd / ".agent" / "logs" / f"{today}_{workflow}.jsonl"
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class AgentLoggerEndGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)
        (self.cwd / ".agent" / "logs").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_duplicate_end_is_rejected(self) -> None:
        workflow = "test_logger_guard"
        init = _run(self.cwd, "init", "--workflow", workflow)
        self.assertEqual(init.returncode, 0, init.stderr)
        run_id = init.stdout.strip()

        start = _run(
            self.cwd,
            "start",
            "--workflow",
            workflow,
            "--run-id",
            run_id,
            "--step-id",
            "step_1",
            "--agent",
            "A0_Orchestrator",
            "--category",
            "deep",
            "--action",
            "demo",
            "--input-bytes",
            "100",
        )
        self.assertEqual(start.returncode, 0, start.stderr)

        first_end = _run(
            self.cwd,
            "end",
            "--workflow",
            workflow,
            "--run-id",
            run_id,
            "--step-id",
            "step_1",
            "--output-bytes",
            "120",
        )
        self.assertEqual(first_end.returncode, 0, first_end.stderr)

        second_end = _run(
            self.cwd,
            "end",
            "--workflow",
            workflow,
            "--run-id",
            run_id,
            "--step-id",
            "step_1",
            "--output-bytes",
            "200",
        )

        self.assertNotEqual(second_end.returncode, 0, "duplicate END must be rejected")

        rows = _read_log(self.cwd, workflow)
        end_rows = [
            r for r in rows if r.get("status") == "END" and r.get("step_id") == "step_1"
        ]
        self.assertEqual(
            len(end_rows), 1, "exactly one END row should exist for same step/run"
        )

    def test_end_without_start_is_rejected(self) -> None:
        workflow = "test_logger_guard_no_start"
        init = _run(self.cwd, "init", "--workflow", workflow)
        self.assertEqual(init.returncode, 0, init.stderr)
        run_id = init.stdout.strip()

        end = _run(
            self.cwd,
            "end",
            "--workflow",
            workflow,
            "--run-id",
            run_id,
            "--step-id",
            "step_missing_start",
            "--output-bytes",
            "42",
        )

        self.assertNotEqual(end.returncode, 0, "END without START must be rejected")

        rows = _read_log(self.cwd, workflow)
        leaked_end = [
            r
            for r in rows
            if r.get("status") == "END" and r.get("step_id") == "step_missing_start"
        ]
        self.assertEqual(leaked_end, [], "END without START should not be emitted")


if __name__ == "__main__":
    unittest.main(verbosity=2)
