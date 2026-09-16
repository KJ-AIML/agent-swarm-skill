#!/usr/bin/env python3
"""Merge worker outputs by git merge or file copy."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(argv: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str] | None:
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        print(f"Error: {argv}\n{detail}", file=sys.stderr)
        return None
    return result


def merge_git(swarm_dir: str) -> bool:
    del swarm_dir
    if not os.path.exists(".git"):
        print("Error: Not a git repo. Use --strategy copy", file=sys.stderr)
        sys.exit(1)

    result = run(["git", "branch", "--list", "agent-*"], check=False)
    if result is None or not result.stdout.strip():
        print("Error: No agent branches found", file=sys.stderr)
        sys.exit(1)

    branches = [line.strip().lstrip("* ").strip() for line in result.stdout.splitlines() if line.strip()]
    print(f"Merging {len(branches)} branches: {', '.join(branches)}")

    octopus = run(["git", "merge", *branches, "--no-edit"], check=False)
    if octopus is None or octopus.returncode != 0:
        print("Octopus merge failed. Trying sequential merge...")
        for branch in branches:
            print(f"Merging {branch}...")
            sequential = run(["git", "merge", branch, "--no-edit"], check=False)
            if sequential is None or sequential.returncode != 0:
                print(f"Conflict in {branch}. Manual resolution needed.")
                print("Run: git status")
                return False
    print("Merge complete!")
    return True


def merge_copy(swarm_dir: str) -> bool:
    integration_dir = os.path.join(swarm_dir, "integration")
    try:
        os.makedirs(integration_dir, exist_ok=True)
    except OSError as error:
        raise SystemExit(f"MERGE_DIRECTORY_FAILED: {integration_dir}: {error}") from error
    agent_dirs = sorted(Path(swarm_dir).glob("agent-*"))
    print(f"Copying files from {len(agent_dirs)} agents...")
    for agent_dir in agent_dirs:
        print(f"  {agent_dir.name}...")
        for file_path in agent_dir.rglob("*"):
            if file_path.is_file() and file_path.name != "PROMPT.md":
                dest = Path(integration_dir) / file_path.relative_to(agent_dir)
                try:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest)
                except OSError as error:
                    raise SystemExit(f"MERGE_COPY_FAILED: {file_path} -> {dest}: {error}") from error
    print(f"All files copied to: {integration_dir}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge agent outputs")
    parser.add_argument("--swarm-dir", type=str, required=True, help="Swarm output directory")
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["git", "copy"],
        default="copy",
        help="Merge strategy",
    )
    args = parser.parse_args()
    if args.strategy == "git":
        merge_git(args.swarm_dir)
    else:
        merge_copy(args.swarm_dir)
