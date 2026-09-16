# Git Isolation Guide

Use a worktree when parallel workers would otherwise touch the same checkout. The coordinator should create the branches and remove worktrees only after every result is collected.

## Setup

```bash
git branch worker-01
git worktree add /absolute/path/worker-01 worker-01
```

Each worker changes only its own worktree and reports a commit. The coordinator reviews the commits and merges them in dependency order.

## Rules

1. Use one unique absolute worktree path per worker.
2. Start from a clean, known revision.
3. Do not run `git worktree prune` while another worker may be active.
4. Keep generated artifacts in the assigned output directory.
5. Never merge a worker that has not reported its validation result.
6. Do not use force pushes or delete branches as part of routine integration.

## No Git

For a non-Git project, create one output directory per worker and copy only reviewed artifacts into an integration directory. Preserve the original paths in the report so the coordinator can reproduce the copy.

## Conflict handling

Inspect the conflicting files and the specification, resolve the smallest interface mismatch, rerun the affected checks, and record the resolution. Do not silently choose one worker's version when behavior differs.
