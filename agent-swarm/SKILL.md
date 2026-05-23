---
name: agent-swarm
description: >
  Multi-agent task orchestration for Kimi Code CLI. Spawns parallel sub-agents
  to work on independent modules, features, or research dimensions simultaneously.
  MANDATORY when:
  - User explicitly says "swarm this", "deploy agents", "parallelize", "multi-agent"
  - Task has 3+ independent modules, components, or dimensions
  - Task involves both infrastructure and application logic
  - Task is "refactor X + write tests + update docs" (auto-detected parallelizable)
  - Comprehensive research requiring multi-dimensional deep dive
  
  Mode A (multi-agent): 3+ modules, full system build, complex research, explicit swarm request
  Mode B (single agent): Simple task, bug fix, single file, focused feature
  
  Do NOT use for: simple factual lookup, single-file edits, trivial one-step tasks.
---

# Agent Swarm

Orchestrate parallel sub-agents in Kimi Code CLI. Inspired by Kimi Web's K2.6 Agent
Swarm — adapted for terminal environment using native `Agent` tool primitives.

**Core insight**: The `Agent(run_in_background=true)` tool is our spawn primitive.
The filesystem is our coordination hub. The main agent is the orchestrator.

## Core Principles

1. **Mode-first.** The skill itself decides whether to swarm. Not the user. Mode selection is mandatory.
2. **Spec-first.** A specification (`SPEC.md`) is written before any implementation. Single source of truth.
3. **Main agent owns plan, init, merge, integrate.** Subagents implement and commit.
4. **Parallelism by modules & features.** Each subagent owns one or more related modules. Group related work to minimize cross-agent dependencies.
5. **File system is the coordination hub.** Agents communicate through files, not chat. Chat is for status updates only.
6. **Interface contracts are sacred.** Define function signatures, data schemas, and file formats in the spec. Subagents implement to these contracts.
7. **Test before merge.** Each subagent runs tests for their scope. Main agent runs integration tests after merge.
8. **Everything is a file.** No long-form content in chat outputs. All deliverables written to `.swarm/output/`.

## Mode Selection

| Condition | Mode |
|-----------|------|
| User explicitly says "swarm", "parallel", "agents", "multi-agent" | **Mode A** (multi-agent) |
| Task has 3+ independent modules or components | **Mode A** |
| Task involves both infrastructure and application logic | **Mode A** |
| Task is "refactor X + write tests + update docs" (auto-detected) | **Mode A** |
| Full system build (API + workers + data pipeline, etc.) | **Mode A** |
| Single script, tool, or focused feature | **Mode B** (single agent) |
| Bug fix or small enhancement | **Mode B** |
| When in doubt | **Mode B** |

## Auto-Detection Heuristics

The skill auto-detects parallelizable tasks using these signals:

| Signal | Example | Action |
|--------|---------|--------|
| Conjunctions of independent work | "refactor auth AND write tests AND update docs" | Decompose into 3 parallel agents |
| Multiple file groups | "update all API endpoints and all frontend components" | 2 agents: backend + frontend |
| Research dimensions | "research market size, competitors, and regulations" | 3 research agents |
| Explicit enumeration | "1) fix login, 2) add oauth, 3) write tests" | 3 implementation agents |
| Scope keywords | "full system", "end-to-end", "complete rewrite" | Analyze for parallel modules |

**Rule**: If auto-detection is ambiguous, ask user: "This task has N independent parts. Use Agent Swarm to parallelize?"

---

## Mode A — Multi-Agent Swarm

### Phase 0: Plan & Decompose (Main Agent)

1. **Analyze task**: Identify independent modules, features, or dimensions.
2. **Group related work**: Minimize cross-agent dependencies. Each agent should own a cohesive slice.
3. **Decide agent count**: 3-10 agents optimal. Never exceed 15 (coordination overhead dominates).
4. **Write SPEC.md** to `.swarm/output/SPEC.md`:
   - Architecture overview
   - Module boundaries and interfaces
   - Data schemas and file formats
   - Agent assignments (which agent owns what)
   - Integration points (how modules connect)

### Phase 1: Init Workspace (Main Agent)

```bash
# Create swarm workspace
mkdir -p .swarm/output

# If git repo exists, create branches per agent
git branch agent-01
git branch agent-02
# ... etc

# If no git repo, init fresh
cd .swarm/output && git init
```

### Phase 2: Dispatch Parallel Agents (Main Agent)

Launch all subagents simultaneously using `Agent(run_in_background=true)`.

Each subagent receives:
1. **Mission**: Clear scope (modules/features to implement)
2. **SPEC.md path**: Read the spec before any work
3. **Output directory**: Where to write deliverables
4. **Interface contracts**: Function signatures, data schemas they must adhere to
5. **Forbidden zones**: Files they must NOT modify (other agents' scope)
6. **Test requirement**: Run tests before declaring complete
7. **Commit requirement**: Git commit before returning

**Subagent prompt template** (see `references/subagent-templates.md`):

```
You are {role} implementing {scope} for {project}.

## Mission
{mission}

## Spec
Read `.swarm/output/SPEC.md` before any work.

## Your Scope
{files_to_create}
{files_to_modify}

## Forbidden
Do NOT modify: {other_agents_files}

## Contracts
{interface_signatures}
{data_schemas}

## Output
Write all deliverables to: {output_dir}

## Requirements
- Implement exactly per SPEC.md
- Run tests before completing
- Git commit with message: "{scope}: implement"
- Return concise summary of what you built
```

### Phase 3: Monitor Progress (Main Agent)

Track agent status via `TaskOutput` polling or automatic notifications.

Display live progress table:

```
Agent Swarm Progress
┌─────────┬─────────────────────┬──────────┬──────────┐
│ Agent   │ Scope               │ Status   │ Time     │
├─────────┼─────────────────────┼──────────┼──────────┤
│ Agent 1 │ Core data layer     │ Running  │ 2m 15s   │
│ Agent 2 │ Tree builder        │ Done     │ 1m 48s   │
│ Agent 3 │ CLI interface       │ Running  │ 2m 05s   │
│ Agent 4 │ Tests               │ Waiting  │ --       │
└─────────┴─────────────────────┴──────────┴──────────┘
```

### Phase 4: Collect Results (Main Agent)

After all agents complete:
1. Read each agent's output directory
2. Verify files exist per SPEC.md
3. Check for missing deliverables
4. If agent failed: analyze error, decide retry or fallback

### Phase 5: Cross-Verification (Reviewer Agents — Optional)

For quality-critical tasks, launch reviewer agents:

```
Agent: code_reviewer
Mission: Review Agent 1's output for correctness, style, SPEC compliance
Input: Agent 1's output files + SPEC.md
Output: Review report with pass/fail per criterion
```

Run reviewers in parallel for speed.

### Phase 6: Merge & Integrate (Main Agent)

**Strategy A — Git Merge** (if using branches):
```bash
git merge agent-01 agent-02 agent-03 --no-edit
```
If octopus merge fails, merge sequentially with conflict resolution.

**Strategy B — File Copy** (if using output directories):
```bash
cp -r .swarm/output/agent-01/* src/
cp -r .swarm/output/agent-02/* src/
# ... etc
```

**Strategy C — Integration Agent** (for complex merges):
Launch a single integration agent to merge outputs manually.

### Phase 7: Integration Test (Main Agent)

1. Run full test suite
2. Verify cross-module integration points
3. Fix any integration issues
4. Git commit: "swarm: integrate all agents"

### Phase 8: Deliver

Present final result to user with:
- Summary of what each agent built
- Integration test results
- Any issues found and resolved
- Final commit hash

---

## Mode B — Single Agent

1. **Main agent**: Analyze task, decide single agent is sufficient.
2. **Single subagent**: Dispatch one `Agent` with full task.
3. **Main agent**: Collect result, present to user.

No swarm overhead. Simple and fast.

---

## Agent Roles

Pre-defined roles with optimized prompts:

| Role | Type | Best For | Prompt Template |
|------|------|----------|----------------|
| `architect` | explore | System design, API design, module boundaries | `references/roles/architect.md` |
| `implementer` | coder | Writing code per SPEC.md | `references/roles/implementer.md` |
| `tester` | coder | Writing tests, test coverage | `references/roles/tester.md` |
| `reviewer` | explore | Code review, quality audit | `references/roles/reviewer.md` |
| `documenter` | explore | Docs, README, API docs | `references/roles/documenter.md` |
| `researcher` | explore | Deep research on one dimension | `references/roles/researcher.md` |
| `integrator` | coder | Merge outputs, resolve conflicts | `references/roles/integrator.md` |

---

## Actor Reference

| Action | Actor |
|--------|-------|
| Mode selection | Main agent (this skill) |
| Task decomposition | Main agent |
| Write SPEC.md | Main agent |
| Init workspace / git branches | Main agent |
| Dispatch subagents | Main agent |
| Implement modules | Implementer subagents (parallel) |
| Write tests | Tester subagents (parallel) |
| Code review | Reviewer subagents (parallel) |
| Merge outputs | Main agent or Integrator subagent |
| Integration test | Main agent |
| Deliver to user | Main agent |

---

## File Layout

```
.swarm/
├── output/                          # Swarm output directory
│   ├── SPEC.md                      # Project specification
│   ├── agent-01/                    # Agent 1 deliverables
│   │   └── ...
│   ├── agent-02/                    # Agent 2 deliverables
│   │   └── ...
│   ├── reviews/                     # Reviewer reports
│   │   ├── agent-01-review.md
│   │   └── ...
│   └── integration/                 # Final merged output
│       └── ...
│
.swarm-log/                          # Execution logs (auto-generated)
├── swarm-{timestamp}.json           # Run metadata
├── agent-01-log.md                  # Per-agent log
└── ...
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Agent fails with error | Retry once with clearer prompt. If still fails, reassign scope to another agent or fall back to single-agent. |
| Agent produces incomplete output | Analyze what's missing, dispatch follow-up agent with delta scope. |
| Merge conflicts | Attempt auto-resolution first. If complex, dispatch Integrator agent. |
| Integration test fails | Identify failing module, dispatch fix agent. Retry integration. |
| All agents fail | Fall back to single-agent mode. Log failure reason for skill improvement. |
| Timeout (agent stuck >10min) | Cancel agent, retry with smaller scope. |

---

## Evaluation (Mandatory for Skill Development)

When improving this skill, run swarm-style evaluation:

1. **Draft test prompts**: 3-5 realistic tasks with known complexity
2. **Paired execution**: Run with skill (Mode A) vs without (Mode B baseline)
3. **Measure**: Time to completion, output quality, integration success rate
4. **Compare**: Which mode produced better results faster?
5. **Iterate**: Adjust decomposition logic, prompt templates, merge strategy

See `references/evaluation-guide.md` for full methodology.
