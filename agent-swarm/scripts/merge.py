#!/usr/bin/env python3
"""
Merge agent outputs: git merge or file copy.

Usage:
    python merge.py --swarm-dir .swarm/output/20240101-120000 --strategy git
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None, check=True):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {cmd}\n{result.stderr}", file=sys.stderr)
        return None
    return result


def merge_git(swarm_dir: str):
    """Merge using git branches."""
    if not os.path.exists(".git"):
        print("Error: Not a git repo. Use --strategy copy", file=sys.stderr)
        sys.exit(1)
    
    # Find agent branches
    result = run("git branch --list 'agent-*'", check=False)
    if not result or not result.stdout.strip():
        print("Error: No agent branches found", file=sys.stderr)
        sys.exit(1)
    
    branches = [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
    branches = [b.replace("* ", "") for b in branches]  # Remove active branch marker
    
    print(f"Merging {len(branches)} branches: {', '.join(branches)}")
    
    # Try octopus merge
    branch_list = " ".join(branches)
    result = run(f"git merge {branch_list} --no-edit", check=False)
    
    if result is None or result.returncode != 0:
        print("Octopus merge failed. Trying sequential merge...")
        
        for branch in branches:
            print(f"Merging {branch}...")
            result = run(f"git merge {branch} --no-edit", check=False)
            if result is None or result.returncode != 0:
                print(f"Conflict in {branch}. Manual resolution needed.")
                print("Run: git status")
                print("Then: git add -A && git commit -m 'merge: resolve conflicts'")
                return False
    
    print("Merge complete!")
    return True


def merge_copy(swarm_dir: str):
    """Merge by copying files from agent directories."""
    
    integration_dir = os.path.join(swarm_dir, "integration")
    os.makedirs(integration_dir, exist_ok=True)
    
    agent_dirs = sorted(Path(swarm_dir).glob("agent-*"))
    
    print(f"Copying files from {len(agent_dirs)} agents...")
    
    for agent_dir in agent_dirs:
        agent_name = agent_dir.name
        print(f"  {agent_name}...")
        
        for file_path in agent_dir.rglob("*"):
            if file_path.is_file() and file_path.name != "PROMPT.md":
                rel_path = file_path.relative_to(agent_dir)
                dest = Path(integration_dir) / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
    
    print(f"All files copied to: {integration_dir}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge agent outputs")
    parser.add_argument("--swarm-dir", type=str, required=True, help="Swarm output directory")
    parser.add_argument("--strategy", type=str, choices=["git", "copy"], default="copy",
                        help="Merge strategy")
    
    args = parser.parse_args()
    
    if args.strategy == "git":
        merge_git(args.swarm_dir)
    else:
        merge_copy(args.swarm_dir)
