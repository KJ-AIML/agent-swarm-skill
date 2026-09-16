# Agent Swarm Skill

> Portable, spec-first orchestration for complex engineering work that benefits from coordinated specialists.

The skill helps a coordinating agent decide when parallel work is useful, define a shared specification, assign bounded missions, collect evidence, and integrate the result. It is host-neutral: an agent runtime may provide native subprocess or task controls, or the scripts can generate prompts for manual or external execution.

## What it provides

1. Detects work that can be split safely, while retaining a single-agent fallback.
2. Creates a `SPEC.md` that records architecture, boundaries, interfaces, and ownership.
3. Generates scoped worker prompts with explicit deliverables and forbidden zones.
4. Tracks outputs through files so progress survives a chat or process restart.
5. Supports review, integration, and deterministic local validation.
6. Installs to an explicit host skill directory without probing or modifying unrelated tools.

## Quick start

```bash
# Clone the repository
git clone https://github.com/KJ-AIML/agent-swarm-skill.git

# Install to a host skill directory you choose
python3 agent-swarm-skill/agent-swarm/scripts/installer.py \
  --target ~/.config/agent-host/skills/agent-swarm

# In a host that loads SKILL.md, request a bounded parallel task.
# Example: "Swarm this refactor: split the parser, tests, and documentation."
```

The installer never guesses a host, writes to a home-directory convention, or removes files from the destination. Pass `--force` only when replacing an existing installation is intentional. The skill can also be used directly from the checkout by giving the host the path to `agent-swarm/SKILL.md`.

## Host contract

A host integration should expose, at minimum:

- a way to start a worker with a prompt and bounded scope;
- status and cancellation signals;
- a shared filesystem or artifact directory;
- a final result that identifies changed files and validation evidence.

If a host does not provide one of these controls, use the generated prompt files and run workers through the host's documented mechanism. The skill does not assume a particular command, API, model, or vendor.

## Workflow

```text
Decide → Specify → Initialize → Dispatch → Observe
  → Collect → Review → Integrate → Validate → Deliver
```

Use parallel work only when boundaries are real. Keep dependent work sequential, and let the coordinator own integration and the final test run.

## Roles

| Role | Purpose |
|------|---------|
| `architect` | Define system design, contracts, and module boundaries |
| `implementer` | Build one assigned slice from the specification |
| `tester` | Exercise behavior, edge cases, and integration paths |
| `reviewer` | Audit correctness, security, and specification compliance |
| `documenter` | Keep usage and operational documentation accurate |
| `researcher` | Investigate one bounded question and record sources |
| `integrator` | Resolve interfaces and assemble the final result |

Role guides live under `agent-swarm/references/roles/`.

## Layout

```text
agent-swarm/
├── SKILL.md
├── README.md
├── scripts/
│   ├── init_swarm.py
│   ├── dispatch.py
│   ├── merge.py
│   ├── evaluate.py
│   └── installer.py
└── references/
    ├── orchestration-patterns.md
    ├── subagent-templates.md
    ├── worktree-guide.md
    └── roles/
```

Generated workspaces are intentionally outside the installed skill and should be kept out of version control (`.swarm/`, `.swarm-log/`, and evaluation output).

## Requirements

- Python 3.10 or newer for the helper scripts
- Git only when branch or worktree isolation is selected
- A host runtime that can execute the prompts, or a human/operator for manual execution

The helper scripts use only the Python standard library. Run `python3 -m unittest discover -s agent-swarm/tests` from the repository root to validate the portable behavior.
