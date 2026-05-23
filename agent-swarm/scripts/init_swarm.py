#!/usr/bin/env python3
"""
Initialize swarm workspace: create directories, git branches, and agent folders.

Usage:
    python init_swarm.py --agents 3 --project my-project
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime


def run(cmd, cwd=None, check=True):
    """Run shell command."""
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {cmd}\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result


def init_swarm(agent_count: int, project_name: str, use_git: bool = True):
    """Initialize swarm workspace."""
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    swarm_dir = f".swarm/output/{timestamp}"
    
    # Create directories
    os.makedirs(swarm_dir, exist_ok=True)
    os.makedirs(f"{swarm_dir}/reviews", exist_ok=True)
    os.makedirs(f"{swarm_dir}/integration", exist_ok=True)
    
    for i in range(1, agent_count + 1):
        os.makedirs(f"{swarm_dir}/agent-{i:02d}", exist_ok=True)
    
    # Create log directory
    os.makedirs(".swarm-log", exist_ok=True)
    
    # Git setup
    if use_git and os.path.exists(".git"):
        for i in range(1, agent_count + 1):
            branch = f"agent-{i:02d}"
            # Check if branch exists
            result = run(f"git branch --list {branch}", check=False)
            if branch not in result.stdout:
                run(f"git branch {branch}")
                print(f"Created branch: {branch}")
    
    # Create SPEC.md template
    spec_path = f"{swarm_dir}/SPEC.md"
    with open(spec_path, "w") as f:
        f.write(f"# SPEC: {project_name}\n\n")
        f.write("## Overview\n\n[Describe project purpose]\n\n")
        f.write("## Architecture\n\n[Component diagram or description]\n\n")
        f.write("## Module Boundaries\n\n")
        for i in range(1, agent_count + 1):
            f.write(f"### Agent {i}\n\n- Scope: \n- Files: \n- Interfaces: \n\n")
        f.write("## Data Schemas\n\n[Define shared data structures]\n\n")
        f.write("## Integration Points\n\n[How modules connect]\n\n")
    
    # Create metadata file
    meta_path = f".swarm-log/swarm-{timestamp}.json"
    import json
    with open(meta_path, "w") as f:
        json.dump({
            "project": project_name,
            "agent_count": agent_count,
            "timestamp": timestamp,
            "swarm_dir": swarm_dir,
            "status": "initialized"
        }, f, indent=2)
    
    print(f"Swarm initialized: {swarm_dir}")
    print(f"Agents: {agent_count}")
    print(f"SPEC template: {spec_path}")
    print(f"Edit SPEC.md, then run dispatch.py")
    return swarm_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize swarm workspace")
    parser.add_argument("--agents", type=int, default=3, help="Number of agents")
    parser.add_argument("--project", type=str, default="swarm-project", help="Project name")
    parser.add_argument("--no-git", action="store_true", help="Skip git branch creation")
    
    args = parser.parse_args()
    init_swarm(args.agents, args.project, use_git=not args.no_git)
