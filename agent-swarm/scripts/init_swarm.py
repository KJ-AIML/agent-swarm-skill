#!/usr/bin/env python3
"""Initialize a swarm workspace: directories, optional git branches, and a SPEC template."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def run(argv: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        print(f"Error: {argv}\n{detail}", file=sys.stderr)
        sys.exit(1)
    return result


def ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as error:
        raise SystemExit(f"INIT_DIRECTORY_FAILED: {path}: {error}") from error


def write_text(path: str, content: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as error:
        raise SystemExit(f"INIT_WRITE_FAILED: {path}: {error}") from error


def init_swarm(agent_count: int, project_name: str, use_git: bool = True) -> str:
    if agent_count < 1:
        raise SystemExit("INIT_INVALID_AGENTS: agent count must be at least 1")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    swarm_dir = f".swarm/output/{timestamp}"

    ensure_dir(swarm_dir)
    ensure_dir(f"{swarm_dir}/reviews")
    ensure_dir(f"{swarm_dir}/integration")
    for i in range(1, agent_count + 1):
        ensure_dir(f"{swarm_dir}/agent-{i:02d}")
    ensure_dir(".swarm-log")

    if use_git and os.path.exists(".git"):
        for i in range(1, agent_count + 1):
            branch = f"agent-{i:02d}"
            listed = run(["git", "branch", "--list", branch], check=False)
            if branch not in listed.stdout:
                run(["git", "branch", branch])
                print(f"Created branch: {branch}")

    spec_path = f"{swarm_dir}/SPEC.md"
    spec_lines = [
        f"# SPEC: {project_name}",
        "",
        "## Overview",
        "",
        "[Describe project purpose]",
        "",
        "## Architecture",
        "",
        "[Component diagram or description]",
        "",
        "## Module Boundaries",
        "",
    ]
    for i in range(1, agent_count + 1):
        spec_lines.extend(
            [
                f"### Agent {i}",
                "",
                "- Scope: ",
                "- Files: ",
                "- Interfaces: ",
                "",
            ]
        )
    spec_lines.extend(
        [
            "## Data Schemas",
            "",
            "[Define shared data structures]",
            "",
            "## Integration Points",
            "",
            "[How modules connect]",
            "",
        ]
    )
    write_text(spec_path, "\n".join(spec_lines))

    meta_path = f".swarm-log/swarm-{timestamp}.json"
    try:
        with open(meta_path, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "project": project_name,
                    "agent_count": agent_count,
                    "timestamp": timestamp,
                    "swarm_dir": swarm_dir,
                    "status": "initialized",
                },
                handle,
                indent=2,
            )
    except OSError as error:
        raise SystemExit(f"INIT_WRITE_FAILED: {meta_path}: {error}") from error

    print(f"Swarm initialized: {swarm_dir}")
    print(f"Agents: {agent_count}")
    print(f"SPEC template: {spec_path}")
    print("Edit SPEC.md, then run dispatch.py")
    return swarm_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize swarm workspace")
    parser.add_argument("--agents", type=int, default=3, help="Number of agents")
    parser.add_argument("--project", type=str, default="swarm-project", help="Project name")
    parser.add_argument("--no-git", action="store_true", help="Skip git branch creation")
    args = parser.parse_args()
    init_swarm(args.agents, args.project, use_git=not args.no_git)
