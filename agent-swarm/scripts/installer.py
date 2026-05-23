#!/usr/bin/env python3
"""
Install agent-swarm skill to Kimi Code CLI and other tools.

Usage:
    python installer.py
"""

import os
import shutil
import sys
from pathlib import Path


TOOL_PATHS = {
    "kimi_code": [
        "~/.kimi/skills/agent-swarm/SKILL.md",
        ".kimi/skills/agent-swarm/SKILL.md",
    ],
    "claude_code": [
        "~/.claude/skills/agent-swarm/SKILL.md",
        ".claude/skills/agent-swarm/SKILL.md",
    ],
    "cursor": [
        "~/.cursor/skills/agent-swarm/SKILL.md",
        ".cursor/skills/agent-swarm/SKILL.md",
    ],
}


def install_skill(skill_dir: str, target_dir: str):
    """Install skill to target directory."""
    target = Path(target_dir).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    
    # Copy skill files
    src = Path(skill_dir)
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)
    
    return str(target)


def detect_installed_tools():
    """Detect which tools are installed by checking paths."""
    detected = []
    
    for tool, paths in TOOL_PATHS.items():
        for path in paths:
            expanded = Path(path).expanduser().parent
            if expanded.exists():
                detected.append(tool)
                break
    
    return detected


def main():
    skill_dir = Path(__file__).parent.parent
    
    print("Agent Swarm Skill Installer")
    print("=" * 40)
    
    # Detect tools
    detected = detect_installed_tools()
    
    if detected:
        print(f"Detected tools: {', '.join(detected)}")
    else:
        print("No known tools detected. Will install to project-level paths.")
    
    # Install to detected tools + project level
    installed = []
    
    for tool, paths in TOOL_PATHS.items():
        if tool in detected or not detected:
            for path in paths:
                target = Path(path).expanduser().parent
                try:
                    install_skill(skill_dir, target)
                    installed.append(f"{tool}: {target}")
                    break
                except Exception as e:
                    print(f"Warning: Failed to install to {path}: {e}")
    
    print("\nInstalled to:")
    for loc in installed:
        print(f"  {loc}")
    
    print("\nTo use: Start a new conversation. The skill auto-activates for parallelizable tasks.")


if __name__ == "__main__":
    main()
