#!/usr/bin/env python3
"""Validate Lecture Factory JSONL logging schema and anomalies."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Issue:
    code: str
    line: int
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate log schema")
    parser.add_argument("--log", required=True, help="Path to jsonl log file")
    parser.add_argument(
        "--strict", action="store_true", help="Fail on schema violations"
    )
    parser.add_argument(
        "--check-duplicate-end",
        action="store_true",
        help="Detect duplicate END/SESSION_END",
    )
    parser.add_argument(
        "--run-id", default=None, help="Validate only records for this run_id"
    )
    parser.add_argument(
        "--since-ts",
        default=None,
        help="Validate only records with ts >= this ISO-8601 value",
    )
    return parser.parse_args()


def load_rows(path: Path, issues: list[Issue]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            issues.append(Issue("JSON_PARSE_ERROR", idx, str(exc)))
            continue
        row["_line"] = idx
        rows.append(row)
    return rows


def apply_filters(
    rows: list[dict[str, Any]], run_id: str | None, since_ts: str | None
) -> list[dict[str, Any]]:
    filtered = rows
    if run_id:
        filtered = [r for r in filtered if r.get("run_id") == run_id]
    if since_ts:
        filtered = [r for r in filtered if str(r.get("ts", "")) >= since_ts]
    return filtered


def validate_rows(
    rows: list[dict[str, Any]], issues: list[Issue], strict: bool
) -> None:
    statuses = {
        "START",
        "END",
        "FAIL",
        "RETRY",
        "DECISION",
        "SESSION_START",
        "SESSION_END",
        "EXTERNAL_TOOL_START",
        "EXTERNAL_TOOL_END",
    }
    allowed_decisions = {"approved", "partial_rejected", "rejected"}
    p04_instance_scoped_steps = {
        "step_2_education_structure",
        "step_4_slide_blueprint",
        "step_5_assembly",
        "step_6_qa",
        "step_7_finalize",
    }

    for row in rows:
        line = row["_line"]
        status = row.get("status")

        if strict:
            if "status" not in row or not status:
                issues.append(
                    Issue(
                        "MISSING_STATUS",
                        line,
                        "status field is required in strict mode",
                    )
                )
            if "ts" not in row or not row.get("ts"):
                issues.append(
                    Issue("MISSING_TS", line, "ts field is required in strict mode")
                )
            if "event" in row and "status" not in row:
                issues.append(
                    Issue(
                        "EVENT_ONLY_SCHEMA",
                        line,
                        "event-only row is forbidden in strict mode",
                    )
                )
            if status and status not in statuses:
                issues.append(
                    Issue(
                        "UNKNOWN_STATUS",
                        line,
                        f"unsupported status in strict mode: {status!r}",
                    )
                )

        if status and status in statuses:
            for field in ("run_id", "workflow", "step_id"):
                if not row.get(field):
                    issues.append(
                        Issue(
                            "MISSING_CORE_FIELD",
                            line,
                            f"missing {field!r} for status={status}",
                        )
                    )

        if strict and row.get("workflow") == "04_SlidePrompt_Generation":
            step_id = str(row.get("step_id", ""))
            base_step_id = step_id.split("::", 1)[0]
            if (
                base_step_id in p04_instance_scoped_steps
                and status in {"START", "END", "FAIL", "RETRY", "DECISION"}
                and "::" not in step_id
            ):
                issues.append(
                    Issue(
                        "P04_STEP_SCOPE_MISSING",
                        line,
                        f"step_id must include instance scope for {base_step_id}: expected format '{base_step_id}::{{session_id}}'",
                    )
                )

        if status in {"END", "SESSION_END"}:
            for field in (
                "duration_sec",
                "input_bytes",
                "output_bytes",
                "est_input_tokens",
                "est_output_tokens",
                "est_cost_usd",
            ):
                if field not in row:
                    issues.append(
                        Issue("END_FIELD_MISSING", line, f"missing {field!r}")
                    )
            if row.get("agent") in (None, "", "null"):
                issues.append(
                    Issue(
                        "END_NULL_AGENT",
                        line,
                        "END/SESSION_END must not have null agent",
                    )
                )
            if row.get("action") in (None, "", "null"):
                issues.append(
                    Issue(
                        "END_NULL_ACTION",
                        line,
                        "END/SESSION_END must not have null action",
                    )
                )
            decision = row.get("decision")
            if decision not in (None, "", "null") and decision not in allowed_decisions:
                issues.append(
                    Issue(
                        "INVALID_DECISION",
                        line,
                        f"unsupported decision value: {decision!r}",
                    )
                )

        if status == "DECISION":
            decision = row.get("decision")
            if decision not in allowed_decisions:
                issues.append(
                    Issue(
                        "INVALID_DECISION",
                        line,
                        f"DECISION event requires one of {sorted(allowed_decisions)}",
                    )
                )


def validate_duplicate_end(rows: list[dict[str, Any]], issues: list[Issue]) -> None:
    bucket: defaultdict[tuple[str, str, str], list[int]] = defaultdict(list)
    for row in rows:
        status = row.get("status")
        if status not in {"END", "SESSION_END"}:
            continue
        key = (str(row.get("run_id")), str(row.get("step_id")), str(status))
        bucket[key].append(row["_line"])

    for key, line_numbers in sorted(bucket.items()):
        if len(line_numbers) > 1:
            rid, step, status = key
            issues.append(
                Issue(
                    "DUPLICATE_END",
                    line_numbers[0],
                    f"{status} duplicated for run_id={rid}, step_id={step}, lines={line_numbers}",
                )
            )


def main() -> int:
    args = parse_args()
    log_path = Path(args.log)
    if not log_path.exists():
        print(f"[FAIL] missing log file: {log_path}")
        return 1

    issues: list[Issue] = []
    rows = load_rows(log_path, issues)
    rows = apply_filters(rows, args.run_id, args.since_ts)

    if not rows:
        print("[FAIL] no rows after filters")
        return 1

    validate_rows(rows, issues, args.strict)
    if args.check_duplicate_end:
        validate_duplicate_end(rows, issues)

    print(
        "[INFO] checked rows="
        f"{len(rows)} run_id={args.run_id or 'ALL'} since_ts={args.since_ts or 'NONE'} strict={args.strict}"
    )

    if issues:
        print(f"[FAIL] {len(issues)} issue(s) detected")
        for issue in sorted(issues, key=lambda x: (x.line, x.code)):
            print(f"- {issue.code} line={issue.line} :: {issue.message}")
        return 1 if args.strict else 0

    print("[PASS] no schema issues detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
