---
name: agent-swarm
description: >
  Portable, spec-first orchestration for complex engineering tasks. Use when a
  task has independent modules or research dimensions, when the user asks for
  parallel work, or when a coordinator needs explicit worker boundaries,
  progress evidence, and an integration gate. Fall back to one worker for a
  small or tightly coupled change.
---

# Agent Swarm

Use this skill to coordinate bounded workers around one shared specification. The skill describes a workflow and host contract; it does not assume a model provider, command name, or native task API.

## Core principles

1. **Choose the mode first.** Parallelism is useful only when the work has real, testable boundaries.
2. **Specify before editing.** Write `SPEC.md` with the objective, architecture, interfaces, ownership, data formats, and acceptance checks.
3. **Keep one coordinator.** The coordinator decomposes work, owns integration, and runs the final validation.
4. **Give each worker a cohesive slice.** A worker receives an explicit mission, files it may change, files it must not change, and a result format.
5. **Coordinate through artifacts.** Use a shared output directory and small status files; do not rely on hidden chat state.
6. **Protect contracts.** A worker proposes interface changes in the specification or an evidence note before changing another worker's boundary.
7. **Validate before integration.** Each worker runs the narrowest useful check, and the coordinator repeats the relevant checks after assembly.
8. **Record uncertainty.** A missing result, interrupted worker, or unresolved merge is evidence to act on, not success.

## Mode selection

Use **parallel mode** when the user requests it or when at least three independent slices can be tested separately. Typical slices include architecture, implementation, tests, documentation, or independent research dimensions. Use **single-worker mode** for one file, a tightly coupled fix, or work whose dependencies make parallel edits unsafe. When uncertain, choose the smaller mode and state the reason in the task record.

### Parallel mode phases

1. **Plan and decompose.** Identify boundaries and write `SPEC.md`.
2. **Initialize.** Create an output directory and, when needed, isolated branches or worktrees.
3. **Dispatch.** Generate one prompt per worker with scope, contracts, forbidden zones, and validation.
4. **Observe.** Track status, cancellations, and timeouts in the output directory.
5. **Collect.** Confirm every expected artifact exists and is readable.
6. **Review.** Check correctness, security, tests, and specification compliance.
7. **Integrate.** Resolve interfaces in one place and keep the working tree reviewable.
8. **Validate and deliver.** Run the project checks, summarize evidence, and record remaining risks.

The helper scripts implement the planning, prompt, evaluation, and copy-merge portions of this workflow. A host runtime remains responsible for actually starting workers.

### Single-worker mode

Create a small specification when it clarifies the change, give one worker the full bounded scope, and apply the same collect, validate, and evidence rules. Do not create parallel branches merely to follow the template.

## Worker prompt requirements

Every prompt should include:

- the mission and success criteria;
- the path to `SPEC.md`;
- files the worker may create or modify;
- forbidden files and external effects;
- interface and data contracts;
- the exact validation command;
- the output path and failure format.

Workers should return a short result that names changed files, tests run, and unresolved issues. They should not silently widen scope, rewrite unrelated files, or claim a remote effect that was not observed.

## Host integration contract

A native integration may provide worker start, status, cancellation, and isolated execution. If it does not, the scripts generate prompt files for the host's documented runner or for manual execution. Pass context through files and bounded arguments. Keep secrets out of prompts, filenames, logs, and result artifacts.

## Reference material

- `references/orchestration-patterns.md` — choose a topology for the dependency graph.
- `references/subagent-templates.md` — prompt templates with evidence requirements.
- `references/worktree-guide.md` — safe Git isolation and cleanup.
- `references/roles/` — role-specific deliverables and review questions.
- `scripts/` — dependency-free workspace and prompt helpers.
