#!/usr/bin/env python3
"""
Dispatch parallel agents with templated prompts.

Usage:
    python dispatch.py --swarm-dir .swarm/output/20240101-120000 --agents 3
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def load_spec(swarm_dir: str) -> dict:
    """Load SPEC.md and extract agent assignments."""
    spec_path = os.path.join(swarm_dir, "SPEC.md")
    if not os.path.exists(spec_path):
        print(f"Error: SPEC.md not found at {spec_path}", file=sys.stderr)
        sys.exit(1)
    
    with open(spec_path) as f:
        content = f.read()
    
    # Simple parsing - in production, use proper markdown parser
    agents = []
    lines = content.split("\n")
    current_agent = None
    
    for line in lines:
        if line.startswith("### Agent "):
            current_agent = {
                "id": line.replace("### Agent ", "").strip(),
                "scope": "",
                "files": "",
                "interfaces": ""
            }
            agents.append(current_agent)
        elif current_agent and line.startswith("- Scope:"):
            current_agent["scope"] = line.replace("- Scope:", "").strip()
        elif current_agent and line.startswith("- Files:"):
            current_agent["files"] = line.replace("- Files:", "").strip()
        elif current_agent and line.startswith("- Interfaces:"):
            current_agent["interfaces"] = line.replace("- Interfaces:", "").strip()
    
    return {"agents": agents, "content": content}


def build_prompt(agent: dict, spec_content: str, swarm_dir: str) -> str:
    """Build subagent prompt from template."""
    
    agent_num = agent["id"]
    agent_dir = os.path.join(swarm_dir, f"agent-{int(agent_num):02d}")
    
    prompt = f"""You are Implementer Agent {agent_num}.

## Mission
Implement: {agent['scope']}

## Spec
Read `{swarm_dir}/SPEC.md` before any work.

## Your Scope
Files to create/modify: {agent['files']}
Interfaces: {agent['interfaces']}

## Output Directory
Write all deliverables to: `{agent_dir}`

## Requirements
1. Implement exactly per SPEC.md
2. Include docstrings for all public functions
3. Handle errors gracefully
4. Run tests if applicable
5. Return concise summary of what you built
"""
    return prompt


def dispatch_agents(swarm_dir: str, agent_count: int = None):
    """Dispatch all agents in parallel."""
    
    spec = load_spec(swarm_dir)
    agents = spec["agents"]
    
    if agent_count:
        agents = agents[:agent_count]
    
    if not agents:
        print("Error: No agents found in SPEC.md", file=sys.stderr)
        sys.exit(1)
    
    print(f"Dispatching {len(agents)} agents...")
    
    # In Kimi Code CLI, we'd use Agent tool here
    # For standalone script, we generate prompt files
    for agent in agents:
        prompt = build_prompt(agent, spec["content"], swarm_dir)
        prompt_path = os.path.join(swarm_dir, f"agent-{int(agent['id']):02d}", "PROMPT.md")
        
        with open(prompt_path, "w") as f:
            f.write(prompt)
        
        print(f"  Agent {agent['id']}: {agent['scope']}")
        print(f"    Prompt: {prompt_path}")
    
    # Update metadata
    meta_files = list(Path(".swarm-log").glob("swarm-*.json"))
    if meta_files:
        latest = max(meta_files, key=lambda p: p.stat().st_mtime)
        with open(latest) as f:
            meta = json.load(f)
        meta["status"] = "dispatched"
        meta["agents_dispatched"] = len(agents)
        with open(latest, "w") as f:
            json.dump(meta, f, indent=2)
    
    print("\nNext steps:")
    print("1. Copy each PROMPT.md into an Agent() call")
    print("2. Use Agent(run_in_background=True) for parallel execution")
    print("3. Monitor with TaskOutput")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dispatch swarm agents")
    parser.add_argument("--swarm-dir", type=str, required=True, help="Swarm output directory")
    parser.add_argument("--agents", type=int, help="Limit to N agents")
    
    args = parser.parse_args()
    dispatch_agents(args.swarm_dir, args.agents)
