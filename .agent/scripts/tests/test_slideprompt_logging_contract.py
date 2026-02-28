#!/usr/bin/env python3
"""Regression tests for SlidePrompt logging contract rules."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / ".agent" / "scripts" / "validate_logging_schema.py"
FIXTURES = ROOT / ".agent" / "scripts" / "tests" / "fixtures"


def _run_validator(fixture_name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--log",
            str(FIXTURES / fixture_name),
            "--strict",
            "--check-duplicate-end",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


class SlidePromptLoggingContractTest(unittest.TestCase):
    def test_partial_rejected_decision_with_scoped_step_id_is_valid(self) -> None:
        result = _run_validator("p04_scoped_partial_rejected_valid.jsonl")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[PASS] no schema issues detected", result.stdout)

    def test_invalid_decision_value_is_rejected(self) -> None:
        result = _run_validator("p04_invalid_decision.jsonl")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("INVALID_DECISION", result.stdout)

    def test_missing_instance_scope_on_repeated_step_is_rejected(self) -> None:
        result = _run_validator("p04_missing_scope_step_id.jsonl")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("P04_STEP_SCOPE_MISSING", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
