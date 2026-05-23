# Git Worktree Guide for Agent Swarm

Reference for using git worktrees to isolate parallel agent work.

## Why Worktrees?

Each subagent works in its own directory without interfering with others:
- No file locking conflicts
- Clean separation of concerns
- Easy merge via git
- Rollback capability per agent

## Setup

### Prerequisites

Git repo must exist:
```bash
cd /path/to/project
git init  # if not already a repo
git add -A && git commit -m "init"
```

### Create Worktrees (one per agent)

```bash
# Main agent: create branches
git branch agent-01
git branch agent-02
git branch agent-03

# Each agent runs:
git worktree add $HOME/work-agent-01 agent-01
git worktree add $HOME/work-agent-02 agent-02
git worktree add $HOME/work-agent-03 agent-03
```

### Agent Workflow

```bash
# Agent 1:
cd $HOME/work-agent-01
# ... do work ...
git add -A
git commit -m "agent-01: implement core module"

# Agent 2:
cd $HOME/work-agent-02
# ... do work ...
git add -A
git commit -m "agent-02: implement tree builder"
```

### Merge (Main Agent)

```bash
cd /path/to/project

# Try octopus merge first
git merge agent-01 agent-02 agent-03 --no-edit

# If conflicts:
git merge agent-01 --no-edit
git merge agent-02 --no-edit  # resolve if needed
git merge agent-03 --no-edit  # resolve if needed
```

### Cleanup

```bash
# After all merges complete
git worktree remove $HOME/work-agent-01
git worktree remove $HOME/work-agent-02
git worktree remove $HOME/work-agent-03

# Optional: delete branches
git branch -d agent-01 agent-02 agent-03
```

## Rules

1. **Each agent MUST use unique worktree path.** `$HOME/work-<agent-id>`
2. **Never run `git worktree prune`** — destroys other agents' entries.
3. **Never work directly in main repo** during agent execution.
4. **Agents commit before returning.** Main agent merges, not agents.
5. **Branch from clean master.** Ensure master is committed before creating branches.

## Without Git (Simple Projects)

For non-git projects, use directory isolation:

```bash
mkdir -p .swarm/output/agent-01
mkdir -p .swarm/output/agent-02
mkdir -p .swarm/output/agent-03

# Each agent writes to their directory
# Main agent copies files to final location
```

## Conflict Resolution

When agents modify same file:

1. **Detect**: `git merge` will show conflicts
2. **Strategy**: Dispatch Integrator agent with both versions + spec
3. **Manual**: Main agent resolves using `git checkout --ours` / `--theirs`
4. **Prevention**: Good decomposition minimizes overlap
