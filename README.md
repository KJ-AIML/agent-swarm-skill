# Agent Swarm Skill for Kimi Code CLI

> Multi-agent task orchestration skill that brings web-tier swarm intelligence to the terminal.

[![Kimi Code CLI](https://img.shields.io/badge/Kimi%20Code%20CLI-Swarm-blue)](https://github.com/MoonshotAI/kimi-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

A **skill** for [Kimi Code CLI](https://github.com/MoonshotAI/kimi-cli) that enables **multi-agent swarm orchestration** — inspired by Kimi Web's K2.6 Agent Swarm, but built entirely using Kimi Code CLI's native `Agent` tool.

When you have a complex task with multiple independent parts, this skill automatically:

1. 🔍 **Detects parallelizable work** (or obeys explicit "swarm this")
2. 📝 **Writes a SPEC.md** — single source of truth
3. 🤖 **Spawns N parallel agents** — each with scoped mission + forbidden zones
4. 📊 **Monitors progress** — tracks completion
5. ✅ **Cross-verifies** — optional reviewer agents for quality
6. 🔗 **Merges results** — git merge or file copy
7. 🧪 **Tests integration** — validates everything works together

## Quick Start

```bash
# Clone the skill
git clone https://github.com/KJ-AIML/agent-swarm-skill.git

# Install to Kimi Code CLI
python agent-swarm-skill/agent-swarm/scripts/installer.py

# Use it
kimi
# Then say: "Swarm: build a CLI tool with auth, tests, and docs"
# Or let it auto-detect: "Refactor auth module, write tests, update docs"
```

## How It Works

### Mode Selection

The skill decides whether to swarm based on task complexity:

| Trigger | Mode |
|---------|------|
| "swarm", "parallel", "multi-agent" | **Multi-agent** |
| 3+ independent modules | **Multi-agent** |
| "refactor + test + doc" (auto-detected) | **Multi-agent** |
| Single file, bug fix | **Single agent** |

### 8-Phase Workflow

```
Plan & Decompose → Init Workspace → Dispatch Agents → Monitor
  → Collect Results → Cross-Verify → Merge & Integrate → Deliver
```

### Agent Roles

| Role | Purpose |
|------|---------|
| `architect` | System design, API contracts |
| `implementer` | Write code per SPEC |
| `tester` | Write tests |
| `reviewer` | Code review, quality audit |
| `documenter` | README, API docs |
| `researcher` | Deep research on dimension |
| `integrator` | Merge outputs, resolve conflicts |

## File Structure

```
agent-swarm/
├── SKILL.md                          # Core orchestration skill
├── README.md                         # Skill documentation
├── scripts/
│   ├── init_swarm.py                # Init workspace + SPEC template
│   ├── dispatch.py                  # Generate agent prompts
│   ├── merge.py                     # Merge outputs
│   ├── evaluate.py                  # A/B test skill vs baseline
│   └── installer.py                 # Register with CLI tools
└── references/
    ├── orchestration-patterns.md    # 6 swarm patterns
    ├── subagent-templates.md        # Prompt templates
    ├── worktree-guide.md           # Git worktree isolation
    └── roles/                       # Per-role guides
        ├── architect.md
        ├── implementer.md
        ├── tester.md
        ├── reviewer.md
        ├── documenter.md
        ├── researcher.md
        └── integrator.md
```

## Verified: It Works

We tested the skill with a real task: **"Build a JSON-to-CSV CLI tool"**

- ✅ 3 parallel agents spawned successfully
- ✅ Agent 1: Core converter module
- ✅ Agent 2: CLI interface  
- ✅ Agent 3: 39 tests + README (93% coverage)
- ✅ All tests passed in 0.54s
- ✅ Merge + integration verified

## Core Principles

1. **Mode-first** — Skill decides whether to swarm, not the user
2. **Spec-first** — SPEC.md before any implementation
3. **Main agent orchestrates** — plans, dispatches, merges
4. **Parallelism by modules** — each agent owns a cohesive slice
5. **File system coordination** — agents communicate through files
6. **Interface contracts** — sacred, no unilateral changes
7. **Test before merge** — each agent tests, main agent integrates

## Inspired By

- [Kimi Web](https://kimi.com) K2.6 Agent Swarm (260 internal skills)
- `deep-research-swarm` — adaptive routing, file-based coordination
- `vibecoding-general-swarm` — spec-first, git worktree isolation
- `skill-creator-swarm` — mandatory A/B evaluation

## Requirements

- Kimi Code CLI
- Python 3.10+
- Git (optional, for branch-based merging)

## License

MIT
