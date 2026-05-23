# Orchestration Patterns for Agent Swarm

Reference guide for multi-agent coordination patterns. Use the right pattern for the task structure.

## Pattern 1: Map-Reduce

**Best for**: Independent sub-tasks with no dependencies.

```
Main Agent
├── Agent 1: Task A → Output A
├── Agent 2: Task B → Output B
├── Agent 3: Task C → Output C
└── Main Agent: Merge outputs → Final result
```

**Examples**:
- Research: 3 agents research different competitors → merge into report
- Refactor: 3 agents refactor different modules → merge commits
- Generate: 5 agents write different chapters → assemble book

**Pros**: Maximum parallelism, simple merge
**Cons**: No cross-agent learning, rigid boundaries

---

## Pattern 2: Supervisor (Hierarchical)

**Best for**: Complex tasks requiring oversight and quality gates.

```
Supervisor Agent
├── Planner Agent → Task decomposition
├── Worker 1 → Implementation
├── Worker 2 → Implementation
├── Worker 3 → Implementation
├── Reviewer Agent → Quality check
└── Supervisor: Approve/reject → Iterate if needed
```

**Examples**:
- Software build: planner designs architecture, workers implement, reviewer checks
- Report writing: planner outlines, writers draft, editor reviews

**Pros**: Quality control, iterative improvement
**Cons**: Sequential bottleneck at review stage

---

## Pattern 3: Debate / Adversarial

**Best for**: Evaluating tradeoffs, security review, controversial decisions.

```
Main Agent
├── Agent 1 (Pro) → Arguments for X
├── Agent 2 (Con) → Arguments against X
└── Main Agent: Synthesize balanced conclusion
```

**Examples**:
- Architecture decision: one agent argues for REST, one for GraphQL
- Security review: one agent finds vulnerabilities, one defends implementation
- Ethics check: one agent proposes aggressive data collection, one raises privacy concerns

**Pros**: Surfaces hidden risks, balanced perspective
**Cons**: Can be slow, may not converge

---

## Pattern 4: Pipeline (Sequential)

**Best for**: Tasks with strict dependencies.

```
Agent 1: Design → Output (design.md)
  ↓
Agent 2: Implement (reads design.md) → Output (code)
  ↓
Agent 3: Test (reads code) → Output (tests)
  ↓
Agent 4: Document (reads code + tests) → Output (docs)
```

**Examples**:
- Design → Implement → Test → Document
- Research → Outline → Write → Edit
- Parse → Transform → Validate → Load

**Pros**: Natural dependency flow, each agent builds on previous
**Cons**: No parallelism, slower than other patterns

---

## Pattern 5: Iterative Refinement

**Best for**: Creative tasks requiring multiple drafts.

```
Agent 1: Draft v1
  ↓
Agent 2: Review → Feedback
  ↓
Agent 1 (or new agent): Draft v2
  ↓
Agent 2: Review → Approve / More feedback
```

**Examples**:
- Writing: draft → critique → revise → polish
- Design: mockup → feedback → iterate → final
- Code: prototype → review → refactor → merge

**Pros**: High quality output, iterative improvement
**Cons**: Slow, requires persistent agent context

---

## Pattern 6: Ensemble (Voting)

**Best for**: High-stakes decisions, error-prone tasks.

```
Main Agent
├── Agent 1: Solve problem → Answer A
├── Agent 2: Solve problem → Answer B
├── Agent 3: Solve problem → Answer C
└── Main Agent: Compare, vote, pick consensus
```

**Examples**:
- Bug diagnosis: 3 agents analyze same bug, take majority diagnosis
- Code review: 3 agents review same PR, flag only issues 2+ agree on
- Fact checking: 3 agents verify same claim, require consensus

**Pros**: Higher accuracy, catches individual agent errors
**Cons**: 3x compute cost, may disagree without resolution

---

## Hybrid Pattern: Swarm + Pipeline

**Best for**: Complex projects (matches Kimi Web's deep-research-swarm).

```
Phase 1: Parallel Research (Map-Reduce)
  ├── Researcher 1: Dimension A
  ├── Researcher 2: Dimension B
  └── Researcher 3: Dimension C

Phase 2: Cross-Verification (Debate)
  └── Reviewer: Compare findings, flag conflicts

Phase 3: Resolution (Iterative)
  └── Researcher: Resolve conflicts, strengthen weak claims

Phase 4: Synthesis (Pipeline)
  ├── Writer: Draft report
  ├── Editor: Review and refine
  └── Formatter: Convert to final format
```

**Examples**:
- Deep research: parallel research → verify → resolve → write → edit
- Large refactor: parallel module refactor → integration test → fix → merge

**Pros**: Best of all patterns, handles complexity
**Cons**: Complex orchestration, requires careful phase management

---

## Pattern Selection Guide

| Task Characteristics | Recommended Pattern |
|---------------------|---------------------|
| Independent sub-tasks | Map-Reduce |
| Needs quality oversight | Supervisor |
| Evaluating tradeoffs | Debate |
| Strict dependencies | Pipeline |
| Creative/creative output | Iterative Refinement |
| High-stakes, error-prone | Ensemble |
| Complex, multi-phase | Hybrid (Swarm + Pipeline) |

---

## Kimi Code CLI Adaptation Notes

Since CLI agents use `Agent(run_in_background=true)`:

- **Map-Reduce**: Launch all agents in one turn. Poll `TaskOutput` for completion.
- **Pipeline**: Launch Agent 1, wait, read output, launch Agent 2, etc.
- **Debate**: Launch Pro + Con simultaneously. Read both, synthesize.
- **Iterative**: Use `Agent(resume=...)` to continue same agent across rounds.
- **Ensemble**: Launch 3+ agents with same prompt. Compare outputs.

**Key constraint**: CLI agents don't share memory. Pass all context via files.
