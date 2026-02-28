#!/usr/bin/env python3
"""Validate workflow/agent/config consistency for Lecture Factory."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = ROOT / ".agent" / "workflows"
AGENTS_DIR = ROOT / ".agent" / "agents"
MODEL_CONFIG = ROOT / ".opencode" / "oh-my-opencode.jsonc"
E2E_WORKFLOW = WORKFLOW_DIR / "00_E2E_Pipeline.yaml"


@dataclass
class Issue:
    code: str
    path: Path
    line: int
    message: str


def _strip_jsonc_comments(text: str) -> str:
    return re.sub(r"(?m)(?<!:)//.*$", "", text)


def load_model_categories() -> dict[str, str]:
    data = json.loads(_strip_jsonc_comments(MODEL_CONFIG.read_text(encoding="utf-8")))
    categories = data.get("categories", {})
    return {k: v.get("model", "unknown") for k, v in categories.items()}


def load_team_configs() -> dict[str, dict[str, Any]]:
    configs: dict[str, dict[str, Any]] = {}
    for cfg in sorted(AGENTS_DIR.glob("*/config.json")):
        team = cfg.parent.name
        payload = json.loads(cfg.read_text(encoding="utf-8"))
        default_category = payload.get("default_category")
        overrides = {
            agent: meta.get("category")
            for agent, meta in payload.get("agent_models", {}).items()
        }
        configs[team] = {
            "path": cfg,
            "default_category": default_category,
            "overrides": overrides,
        }
    return configs


def parse_workflow_agent_refs(path: Path) -> list[tuple[str, int, str]]:
    refs: list[tuple[str, int, str]] = []
    current_step = ""
    current_step_line = 1
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m_step = re.match(r"^\s*-\s+id:\s*([A-Za-z0-9_\-:.]+)\s*$", line)
        if m_step:
            current_step = m_step.group(1)
            current_step_line = idx
            continue
        m_agent = re.match(r'^\s*agent:\s*"([0-9]{2}_[^/"]+/[^\"]+)"\s*$', line)
        if m_agent:
            step_label = current_step or f"<unknown@{current_step_line}>"
            refs.append((step_label, idx, m_agent.group(1)))
    return refs


def parse_quickref_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_section = False
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "에이전트별 category→model 매핑" in line:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section or not line.strip().startswith("|"):
            continue

        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        agent_cell, category_cell, model_cell = cells[0], cells[1], cells[2]
        if agent_cell in {"에이전트", "---"} or agent_cell.startswith("---"):
            continue
        cat_match = re.search(r"`([^`]+)`", category_cell)
        model_match = re.search(r"`([^`]+)`", model_cell)
        rows.append(
            {
                "line": idx,
                "agent": agent_cell,
                "category": cat_match.group(1) if cat_match else category_cell,
                "model": model_match.group(1) if model_match else model_cell,
                "is_default": agent_cell.startswith("(기타"),
            }
        )
    return rows


def check_workflow_agent_paths(issues: list[Issue]) -> None:
    for wf in sorted(WORKFLOW_DIR.glob("*.yaml")):
        for step_id, line_no, agent_ref in parse_workflow_agent_refs(wf):
            if "/" not in agent_ref:
                issues.append(
                    Issue(
                        "WF_AGENT_REF_FORMAT",
                        wf,
                        line_no,
                        f"invalid agent ref: {agent_ref}",
                    )
                )
                continue
            team, agent = agent_ref.split("/", 1)
            expected = AGENTS_DIR / team / f"{agent}.md"
            if not expected.exists():
                issues.append(
                    Issue(
                        "WF_AGENT_FILE_MISSING",
                        wf,
                        line_no,
                        f"{step_id}: {agent_ref} -> missing {expected.relative_to(ROOT)}",
                    )
                )


def check_category_validity(
    team_configs: dict[str, dict[str, Any]],
    category_models: dict[str, str],
    issues: list[Issue],
) -> None:
    valid_categories = set(category_models.keys())
    for team, cfg in team_configs.items():
        cfg_path: Path = cfg["path"]
        default_cat = cfg["default_category"]
        if default_cat not in valid_categories:
            issues.append(
                Issue(
                    "CFG_DEFAULT_CATEGORY_UNKNOWN",
                    cfg_path,
                    1,
                    f"{team}: default_category={default_cat!r} is not in oh-my-opencode categories",
                )
            )
        for agent, category in sorted(cfg["overrides"].items()):
            if category not in valid_categories:
                issues.append(
                    Issue(
                        "CFG_AGENT_CATEGORY_UNKNOWN",
                        cfg_path,
                        1,
                        f"{team}.{agent}: category={category!r} is not in oh-my-opencode categories",
                    )
                )


def check_quickref_tables(
    team_configs: dict[str, dict[str, Any]],
    category_models: dict[str, str],
    issues: list[Issue],
) -> None:
    for orchestrator in sorted(AGENTS_DIR.glob("*/*Orchestrator.md")):
        team = orchestrator.parent.name
        cfg = team_configs.get(team)
        if not cfg:
            continue
        default_cat = cfg["default_category"]
        overrides = cfg["overrides"]

        rows = parse_quickref_rows(orchestrator)
        for row in rows:
            row_line = row["line"]
            agent_name = row["agent"]
            listed_cat = row["category"]
            listed_model = row["model"]

            if row["is_default"]:
                expected_cat = default_cat
                expected_model = category_models.get(expected_cat, "unknown")
            else:
                expected_cat = overrides.get(agent_name, default_cat)
                expected_model = category_models.get(expected_cat, "unknown")
                agent_file = orchestrator.parent / f"{agent_name}.md"
                if not agent_file.exists():
                    issues.append(
                        Issue(
                            "QREF_AGENT_NAME_MISSING_FILE",
                            orchestrator,
                            row_line,
                            f"table agent {agent_name!r} has no file {agent_file.name}",
                        )
                    )

            if listed_cat != expected_cat:
                issues.append(
                    Issue(
                        "QREF_CATEGORY_MISMATCH",
                        orchestrator,
                        row_line,
                        f"{agent_name}: listed={listed_cat!r}, expected={expected_cat!r}",
                    )
                )
            if expected_model != "unknown" and listed_model != expected_model:
                issues.append(
                    Issue(
                        "QREF_MODEL_MISMATCH",
                        orchestrator,
                        row_line,
                        f"{agent_name}: listed={listed_model!r}, expected={expected_model!r}",
                    )
                )


def check_pipeline_registry_team_size(issues: list[Issue]) -> None:
    line_re = re.compile(
        r'^\s*-\s*\{[^}]*id:\s*"(?P<id>[0-9]+)"[^}]*agents:\s*"(?P<agents>[^"]+)"[^}]*team_size:\s*(?P<size>[0-9]+)'
    )
    lines = E2E_WORKFLOW.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines, 1):
        m = line_re.match(line)
        if not m:
            continue
        agents_rel = m.group("agents").strip("/")
        declared = int(m.group("size"))
        team_dir = AGENTS_DIR / agents_rel
        if not team_dir.exists():
            issues.append(
                Issue(
                    "REGISTRY_TEAM_DIR_MISSING",
                    E2E_WORKFLOW,
                    idx,
                    f"pipeline {m.group('id')}: missing team dir {team_dir.relative_to(ROOT)}",
                )
            )
            continue
        actual = len([p for p in team_dir.glob("*.md") if p.name != "README.md"])
        if declared != actual:
            issues.append(
                Issue(
                    "REGISTRY_TEAM_SIZE_MISMATCH",
                    E2E_WORKFLOW,
                    idx,
                    f"pipeline {m.group('id')} {agents_rel}: declared={declared}, actual={actual}",
                )
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate workflow-agent consistency")
    parser.add_argument(
        "--mode",
        choices=["all", "quickref", "mapping", "category", "registry"],
        default="all",
    )
    parser.add_argument("--all", action="store_true", help="alias for --mode all")
    parser.add_argument(
        "--strict", action="store_true", help="return non-zero when issues exist"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.all:
        args.mode = "all"

    issues: list[Issue] = []
    category_models = load_model_categories()
    team_configs = load_team_configs()

    if args.mode == "all":
        check_workflow_agent_paths(issues)
        check_category_validity(team_configs, category_models, issues)
        check_quickref_tables(team_configs, category_models, issues)
        check_pipeline_registry_team_size(issues)
    elif args.mode == "mapping":
        check_workflow_agent_paths(issues)
    elif args.mode == "category":
        check_category_validity(team_configs, category_models, issues)
    elif args.mode == "quickref":
        check_quickref_tables(team_configs, category_models, issues)
        check_pipeline_registry_team_size(issues)
    elif args.mode == "registry":
        check_pipeline_registry_team_size(issues)

    issues.sort(key=lambda x: (x.path.as_posix(), x.line, x.code))

    if issues:
        print(f"[FAIL] {len(issues)} issue(s) detected")
        for it in issues:
            rel = it.path.relative_to(ROOT)
            print(f"- {it.code} {rel}:{it.line} :: {it.message}")
        return 1 if args.strict else 0

    print("[PASS] no consistency issues detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
