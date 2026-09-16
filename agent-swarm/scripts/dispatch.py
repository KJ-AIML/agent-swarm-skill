#!/usr/bin/env python3
"""Generate one worker prompt file per SPEC.md assignment."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def read_text(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as error:
        raise SystemExit(f"DISPATCH_READ_FAILED: {path}: {error}") from error


def write_text(path: str, content: str) -> None:
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
    except OSError as error:
        raise SystemExit(f"DISPATCH_WRITE_FAILED: {path}: {error}") from error


def load_spec(swarm_dir: str) -> dict:
    spec_path = os.path.join(swarm_dir, "SPEC.md")
    if not os.path.exists(spec_path):
        print(f"Error: SPEC.md not found at {spec_path}", file=sys.stderr)
        sys.exit(1)

    content = read_text(spec_path)
    agents = []
    current_agent = None
    for line in content.split("\n"):
        if line.startswith("### Agent "):
            current_agent = {
                "id": line.replace("### Agent ", "").strip(),
                "scope": "",
                "files": "",
                "interfaces": "",
            }
            agents.append(current_agent)
        elif current_agent and line.startswith("- Scope:"):
            current_agent["scope"] = line.replace("- Scope:", "").strip()
        elif current_agent and line.startswith("- Files:"):
            current_agent["files"] = line.replace("- Files:", "").strip()
        elif current_agent and line.startswith("- Interfaces:"):
            current_agent["interfaces"] = line.replace("- Interfaces:", "").strip()
    return {"agents": agents, "content": content}


def agent_dir_name(agent_id: str) -> str:
    try:
        return f"agent-{int(agent_id):02d}"
    except ValueError as error:
        raise SystemExit(f"DISPATCH_INVALID_AGENT_ID: {agent_id}") from error


def build_prompt(agent: dict, swarm_dir: str) -> str:
    folder = os.path.join(swarm_dir, agent_dir_name(agent["id"]))
    return f"""You are Implementer Agent {agent["id"]}.

## Mission
Implement: {agent["scope"]}

## Spec
Read `{swarm_dir}/SPEC.md` before any work.

## Your Scope
Files to create/modify: {agent["files"]}
Interfaces: {agent["interfaces"]}

## Output Directory
Write all deliverables to: `{folder}`

## Requirements
1. Implement exactly per SPEC.md
2. Include docstrings for all public functions
3. Handle errors gracefully
4. Run tests if applicable
5. Return concise summary of what you built
"""


def dispatch_agents(swarm_dir: str, agent_count: int | None = None) -> None:
    spec = load_spec(swarm_dir)
    agents = spec["agents"]
    if agent_count:
        agents = agents[:agent_count]
    if not agents:
        print("Error: No agents found in SPEC.md", file=sys.stderr)
        sys.exit(1)

    print(f"Dispatching {len(agents)} agents...")
    for agent in agents:
        prompt_path = os.path.join(swarm_dir, agent_dir_name(agent["id"]), "PROMPT.md")
        write_text(prompt_path, build_prompt(agent, swarm_dir))
        print(f"  Agent {agent['id']}: {agent['scope']}")
        print(f"    Prompt: {prompt_path}")

    meta_files = list(Path(".swarm-log").glob("swarm-*.json"))
    if meta_files:
        latest = max(meta_files, key=lambda path: path.stat().st_mtime)
        try:
            meta = json.loads(read_text(str(latest)))
            meta["status"] = "dispatched"
            meta["agents_dispatched"] = len(agents)
            write_text(str(latest), json.dumps(meta, indent=2))
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit(f"DISPATCH_METADATA_FAILED: {latest}: {error}") from error

    print("\nNext steps:")
    print("1. Give each PROMPT.md to a worker through the host's documented runner")
    print("2. Collect worker artifacts in the assigned output directory")
    print("3. Review, integrate, and run the project validation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dispatch swarm agents")
    parser.add_argument("--swarm-dir", type=str, required=True, help="Swarm output directory")
    parser.add_argument("--agents", type=int, help="Limit to N agents")
    args = parser.parse_args()
    dispatch_agents(args.swarm_dir, args.agents)
