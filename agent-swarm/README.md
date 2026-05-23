# Agent Swarm Skill for Kimi Code CLI

Multi-agent task orchestration for Kimi Code CLI. Brings web-tier swarm intelligence (K2.6-style) to the terminal environment.

## What It Does

When you have a complex task with multiple independent parts, this skill:

1. **Auto-detects** parallelizable work (or obeys explicit "swarm this")
2. **Writes a SPEC.md** — single source of truth
3. **Spawns N parallel agents** — each with scoped mission + forbidden zones
4. **Monitors progress** — tracks completion
5. **Cross-verifies** — optional reviewer agents for quality
6. **Merges results** — git merge or file copy
7. **Tests integration** — validates everything works together

## Quick Start

```bash
# Install skill
python scripts/installer.py

# Use it
kimi  # Start Kimi Code CLI
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
├── SKILL.md                          # Core skill
├── scripts/
│   ├── init_swarm.py                # Init workspace + SPEC template
│   ├── dispatch.py                  # Generate agent prompts
│   ├── merge.py                     # Merge outputs
│   ├── evaluate.py                  # A/B test skill vs baseline
│   └── installer.py                 # Register with CLI tools
├── references/
│   ├── orchestration-patterns.md    # 6 swarm patterns
│   ├── subagent-templates.md        # Prompt templates
│   ├── worktree-guide.md           # Git worktree isolation
│   └── roles/                       # Per-role guides
│       ├── architect.md
│       ├── implementer.md
│       ├── tester.md
│       ├── reviewer.md
│       ├── documenter.md
│       ├── researcher.md
│       └── integrator.md
└── README.md                         # This file
```

## Core Principles

1. **Mode-first** — Skill decides whether to swarm, not the user
2. **Spec-first** — SPEC.md before any implementation
3. **Main agent orchestrates** — plans, dispatches, merges
4. **Parallelism by modules** — each agent owns a cohesive slice
5. **File system coordination** — agents communicate through files
6. **Interface contracts** — sacred, no unilateral changes
7. **Test before merge** — each agent tests, main agent integrates

## Verification

We verified the primitive works:
- ✅ 3 parallel agents spawned successfully
- ✅ Shared filesystem with no race conditions
- ✅ Parent detects completion via notifications

## Inspired By

- Kimi Web K2.6 Agent Swarm (260 internal skills)
- `deep-research-swarm` — adaptive routing, file-based coordination
- `vibecoding-general-swarm` — spec-first, git worktree isolation
- `skill-creator-swarm` — mandatory A/B evaluation

## License

MIT
