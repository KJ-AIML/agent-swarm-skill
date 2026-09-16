# Agent Swarm Skill

Portable multi-agent task orchestration for complex engineering work.

The skill gives a coordinating agent a repeatable way to decide whether work can be parallelized, write a shared specification, assign bounded missions, collect artifacts, review them, and validate the integrated result. It does not depend on a particular model, command, or host product.

## Install

Choose the destination explicitly:

```bash
python3 scripts/installer.py --target ~/.config/agent-host/skills/agent-swarm
```

An existing destination is updated file by file; use `--force` when replacing an installation is deliberate. The installer does not autodetect tools or write to hidden vendor directories.

## Use

Point a host runtime at `SKILL.md`, then describe the task and its boundaries. A compatible host should be able to start, observe, and cancel workers and provide a shared artifact directory. When those controls are unavailable, run the prompt files produced by `dispatch.py` through the host's documented interface.

## Workflow

```text
Decide → Specify → Initialize → Dispatch → Observe
  → Collect → Review → Integrate → Validate → Deliver
```

The coordinator owns the specification, integration, and final validation. Workers own only their assigned files. Dependent work stays sequential, and every handoff carries evidence rather than a conversational claim.

## Roles

- `architect`: architecture and interfaces
- `implementer`: bounded implementation
- `tester`: tests and edge cases
- `reviewer`: correctness and security review
- `documenter`: user and maintainer documentation
- `researcher`: sourced investigation
- `integrator`: merge and integration repair

See `references/` for patterns, templates, worktree guidance, and role-specific instructions.

## Verification

The repository includes dependency-free tests for installer isolation, safe subprocess invocation, prompt generation, frontmatter, and host-neutral wording:

```bash
python3 -m unittest discover -s agent-swarm/tests
```

Python 3.10+ and Git are the only optional local dependencies. No generated workspace or host configuration is required to run the tests.
