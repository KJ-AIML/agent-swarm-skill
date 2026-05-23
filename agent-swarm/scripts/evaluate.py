#!/usr/bin/env python3
"""
Swarm-style evaluation: compare with_skill vs without_skill (baseline).

Usage:
    python evaluate.py --task-dir ./eval-task-1 --with-skill ./agent-swarm
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_agent(prompt: str, skill_path: str = None) -> dict:
    """
    Run a single agent task. 
    In Kimi Code CLI, this would use Agent() tool.
    For standalone script, we write prompt files for manual execution.
    """
    mode = "with_skill" if skill_path else "baseline"
    
    return {
        "mode": mode,
        "skill_path": skill_path,
        "prompt": prompt,
        "status": "prompt_generated"
    }


def setup_eval_workspace(task_name: str) -> str:
    """Create evaluation workspace."""
    
    workspace = f"eval-workspace/{task_name}"
    os.makedirs(f"{workspace}/with_skill", exist_ok=True)
    os.makedirs(f"{workspace}/without_skill", exist_ok=True)
    os.makedirs(f"{workspace}/grader", exist_ok=True)
    os.makedirs(f"{workspace}/comparator", exist_ok=True)
    
    return workspace


def generate_eval_prompts(task_description: str, skill_path: str) -> tuple:
    """Generate paired prompts for with_skill and baseline."""
    
    with_skill_prompt = f"""Execute this task using the agent-swarm skill.

Skill path: {skill_path}/SKILL.md
Task: {task_description}

Requirements:
1. Read the skill before solving
2. Follow skill instructions exactly
3. Save deliverables to ./output/
4. Return summary of approach and results
"""
    
    baseline_prompt = f"""Execute this task WITHOUT using any swarm skill.

Task: {task_description}

Requirements:
1. Solve directly as a single agent
2. Save deliverables to ./output/
3. Return summary of approach and results
"""
    
    return with_skill_prompt, baseline_prompt


def grade_outputs(workspace: str, expectations: list) -> dict:
    """Generate grader prompt."""
    
    grader_prompt = f"""Grade these evaluation outputs.

Original task: [see task description]

Outputs to grade:
- With skill: {workspace}/with_skill/output/
- Baseline: {workspace}/without_skill/output/

Expectations:
{chr(10).join(f'- {e}' for e in expectations)}

Return:
- pass/fail for each expectation (both outputs)
- evidence for each judgment
- overall verdict: which approach was better and why
"""
    
    grader_path = f"{workspace}/grader/PROMPT.md"
    with open(grader_path, "w") as f:
        f.write(grader_prompt)
    
    return {"grader_prompt": grader_path}


def compare_blind(workspace: str) -> dict:
    """Generate blind comparator prompt."""
    
    comparator_prompt = f"""Compare two outputs blindly.

Original task: [see task description]
Output A: {workspace}/with_skill/output/
Output B: {workspace}/without_skill/output/

Do NOT infer which used the skill.
Judge only on: task completion, quality, correctness, completeness, usability.

Return:
- winner: A, B, or TIE
- concise reasoning
- strengths/weaknesses of each
"""
    
    comp_path = f"{workspace}/comparator/PROMPT.md"
    with open(comp_path, "w") as f:
        f.write(comparator_prompt)
    
    return {"comparator_prompt": comp_path}


def run_evaluation(task_description: str, skill_path: str, expectations: list):
    """Run full evaluation pipeline."""
    
    task_name = f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    workspace = setup_eval_workspace(task_name)
    
    print(f"Evaluation workspace: {workspace}")
    print(f"Task: {task_description}")
    print()
    
    # Generate prompts
    with_skill_prompt, baseline_prompt = generate_eval_prompts(task_description, skill_path)
    
    # Save prompts
    with open(f"{workspace}/with_skill/PROMPT.md", "w") as f:
        f.write(with_skill_prompt)
    with open(f"{workspace}/without_skill/PROMPT.md", "w") as f:
        f.write(baseline_prompt)
    
    print("Generated prompts:")
    print(f"  With skill: {workspace}/with_skill/PROMPT.md")
    print(f"  Baseline: {workspace}/without_skill/PROMPT.md")
    print()
    
    # Generate grader and comparator
    grade_outputs(workspace, expectations)
    compare_blind(workspace)
    
    print("Generated evaluation prompts:")
    print(f"  Grader: {workspace}/grader/PROMPT.md")
    print(f"  Comparator: {workspace}/comparator/PROMPT.md")
    print()
    
    # Save metadata
    meta = {
        "task": task_description,
        "skill_path": skill_path,
        "workspace": workspace,
        "expectations": expectations,
        "status": "prompts_generated",
        "next_steps": [
            "1. Run with_skill agent with its prompt",
            "2. Run baseline agent with its prompt",
            "3. Run grader to evaluate both outputs",
            "4. Run comparator for blind comparison",
            "5. Analyze results and revise skill"
        ]
    }
    
    with open(f"{workspace}/meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    
    print("Next: Execute both agents, then run grader/comparator")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Swarm skill evaluation")
    parser.add_argument("--task", type=str, required=True, help="Task description")
    parser.add_argument("--skill", type=str, default="./agent-swarm", help="Skill directory path")
    parser.add_argument("--expectations", type=str, nargs="+", 
                        default=["output exists", "task completed", "quality acceptable"],
                        help="Evaluation expectations")
    
    args = parser.parse_args()
    run_evaluation(args.task, args.skill, args.expectations)
