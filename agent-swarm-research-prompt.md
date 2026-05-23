# Deep Research Prompt: Agent Swarm Skill for Kimi Code CLI

## Mission Statement

Design and specify a complete Agent Swarm system for Kimi Code CLI that brings web-tier multi-agent orchestration (K2.6 Agent Swarm-style) to the terminal environment. Output: a production-ready SKILL.md for inline swarm activation + a standalone `kimi-swarm` CLI tool specification for heavy parallel workloads.

## Background & Context

- Kimi Web (K2.5/K2.6) has native Agent Swarm: 3-300 sub-agents, dynamic decomposition, progress tracking, named workers, worktree isolation
- Kimi Code CLI is single-agent only — no native swarm mode (confirmed by Kimi team, feature request #746 open)
- Kimi Code CLI HAS `Agent` tool with `run_in_background=true` and `resume` capabilities — this is the primitive we build on
- User observed Kimi Web Swarm behavior across 3 real chats (MemCtrl, Canopy, AXGA/Pi fork) with patterns:
  - Main agent plans → creates named sub-agents → dispatches parallel → tracks progress → merges results
  - Sub-agents get: mission, worktree/branch, files to create, context, key files to read, output path
  - Scale observed: 3-10 agents, task progress UI, file-based outputs
- User wants: auto-detection of parallelizable tasks + role-typed sub-agents (coder/explore/review)
- Existing memory skill (memctrl) and research skill (deep-research-prompt) already in user's skill ecosystem

## Research Scope

**In scope:**
- Kimi Code CLI `Agent` tool internals and limitations (background execution, session persistence, context passing)
- Multi-agent orchestration patterns: map-reduce, supervisor, debate, reviewer-writer, hierarchical
- Task decomposition algorithms for auto-detecting parallelizable sub-tasks from a single user prompt
- Role-typed agent design: coder (file editing), explore (read-only research), review (audit/quality), test (test generation), doc (documentation)
- Worktree/branch isolation strategies using git worktrees and temp directories
- Result merging strategies: file-based outputs, structured JSON, diff-based integration
- Terminal progress tracking: rich tables, spinners, task lists, live agent status
- Error handling: retry logic, fallback to single-agent, partial failure recovery
- Existing multi-agent frameworks: CrewAI, AutoGen, LangGraph, OpenAI Swarm — what to borrow/avoid
- SKILL.md format for Kimi Code CLI skill registration and trigger conditions
- CLI tool architecture for `kimi-swarm` wrapper (typer, rich, async)
- MCP server design for external tool integration

**Out of scope:**
- Modifying Kimi Code CLI source code (we build ON TOP, not fork)
- Cloud infrastructure or distributed computing (local-only swarm)
- Vector databases or RAG (not needed for orchestration)
- GUI/web interface (terminal-first)
- Language models other than Kimi K2.5/K2.6 (focus on what CLI can access)

## Research Questions

### 1. Kimi Code CLI Agent Tool: Capabilities & Limitations
What are the exact capabilities and constraints of the `Agent` tool in Kimi Code CLI?
- What happens when `run_in_background=true`? Is there a limit on concurrent agents?
- How does `resume` work across context resets? Can sub-agents persist state?
- What is the context window sharing model? Do sub-agents inherit parent context or start fresh?
- Can sub-agents write to shared files? Is there race condition risk?
- What is the timeout behavior for background agents?
- Can the parent agent detect when a background agent completes or fails?
- Are there any rate limits or throttling on Agent tool usage?

### 2. Task Decomposition: Auto-Detecting Parallelizable Work
How can we algorithmically detect when a user prompt contains multiple independent sub-tasks?
- What NLP/LLM techniques work best for extracting independent work streams? (e.g., "refactor auth + write tests + update docs")
- Should decomposition be rule-based (keyword patterns) or LLM-reasoned ("analyze this task for parallelism")?
- What is the granularity sweet spot? File-level? Module-level? Function-level?
- How do we handle dependencies between sub-tasks? (e.g., tests depend on refactored code)
- What heuristics prevent over-decomposition? (e.g., don't spawn 50 agents for 50 files)
- How does Kimi Web's K2.6 do dynamic decomposition? Can we replicate the logic?

### 3. Role-Typed Agent Design: Architectures & Prompts
How should we design role-specific agents that are optimized for their function?
- What is the optimal prompt template for a `coder` agent vs `explore` agent vs `review` agent?
- Should roles be hardcoded (coder/explore/review/test/doc) or user-configurable?
- How do we prevent role drift? (e.g., a coder agent trying to do research)
- What context should each role receive? Full project context or scoped subset?
- How do we handle agent-to-agent communication? (e.g., reviewer needs to see coder's output)
- What is the ideal agent lifecycle? Create → dispatch → monitor → collect → destroy?

### 4. Worktree Isolation & Result Merging
How do we achieve clean isolation and safe merging of parallel agent outputs?
- Git worktrees vs temp directories: which is better for CLI agent isolation?
- How do we handle merge conflicts when multiple agents touch related files?
- Should agents work on branches that get merged, or write to separate output directories?
- What is the safest merge strategy? (manual review gate, auto-merge with tests, diff preview)
- How do we preserve atomicity? (all-or-nothing commit vs incremental)
- What happens when agents need shared resources? (e.g., all need to read the same config file)

### 5. Terminal UX: Progress Tracking & Live Status
How do we provide a compelling real-time view of swarm execution in the terminal?
- What terminal UI patterns work best? (rich.live, tqdm, custom TUI)
- How do we show: agent names, current task, status (running/done/failed), time elapsed?
- Should there be a summary view (all agents) and detail view (one agent's logs)?
- How do we handle streaming output from multiple agents without interleaving garbage?
- What keyboard shortcuts should exist? (pause, cancel agent, view logs, etc.)
- How do we persist swarm history for later review? (log files, JSON reports)

### 6. Error Handling, Retry & Fallback
How do we build resilience into the swarm system?
- What retry strategies work best? (immediate, exponential backoff, manual)
- When should we fall back to single-agent execution? (partial failure, coordination overhead)
- How do we handle infinite loops or stuck agents? (heartbeat timeout, max execution time)
- What is the recovery story? (restart failed agents only, or restart entire swarm?)
- How do we surface errors to the user? (summary at end, or interrupt immediately?)
- What about resource exhaustion? (disk space, memory, too many parallel processes)

### 7. Existing Frameworks: What to Steal, What to Skip
What can we learn from existing multi-agent frameworks?
- CrewAI: role-based agents, task delegation, process types — what's portable to CLI?
- AutoGen: conversational agents, group chat, code execution — any patterns worth adapting?
- LangGraph: state machines, conditional edges — useful for swarm orchestration?
- OpenAI Swarm: handoffs, function calling — applicable to Kimi Code CLI?
- What are the common anti-patterns? (over-engineering, too much coordination overhead)
- Which framework has the best task decomposition approach?

### 8. SKILL.md Design: Trigger Conditions & Behavior
How should the Agent Swarm skill integrate with Kimi Code CLI's skill system?
- What trigger conditions should activate the skill? ("swarm:", auto-detect, slash command?)
- How do we prevent accidental swarm activation on simple tasks?
- What should the skill's behavior section specify? (when to auto-detect, when to ask user)
- How does the skill interact with the user's existing `memctrl` and `deep-research-prompt` skills?
- Should the skill register an MCP server for external swarm management?
- What is the installation story? (`memctrl install`-style registration to multiple tools?)

## Deliverables Expected

For each research question, provide:
- [ ] Concrete answer with evidence (official docs, source code, benchmark data)
- [ ] Comparison table where applicable (frameworks, strategies, tools)
- [ ] Code example / config snippet where applicable
- [ ] Recommendation with tradeoffs (why X over Y)

Additional deliverables:
- [ ] Architecture diagram for the swarm system (text-based or ASCII)
- [ ] Example swarm execution flow for a sample task ("refactor auth module + write tests + update docs")
- [ ] Draft SKILL.md structure with trigger conditions and behavior rules
- [ ] Draft `kimi-swarm` CLI command specification

## Constraints to Respect

- Stack: Python 3.10+, must work with Kimi Code CLI's existing tool ecosystem
- Must use Kimi Code CLI's native `Agent` tool — no external API calls required
- Must be installable via `uv tool install` or `pip install -e .`
- Must work offline (no cloud dependencies)
- Must respect user's existing `.memoryrc` and skill ecosystem
- Must handle failures gracefully — never leave the user's repo in a broken state
- Must be minimal and focused — avoid over-engineering

## Success Criteria

The research is complete when:
1. We have a clear technical specification for both the SKILL.md and the `kimi-swarm` CLI tool
2. We can explain exactly how task auto-detection will work with concrete examples
3. We have role-specific agent prompt templates that are tested against real tasks
4. We have a proven worktree/merge strategy that doesn't corrupt user repos
5. We have a terminal UI mockup that shows real-time swarm progress
6. We understand Kimi Code CLI's Agent tool limits and have workarounds for all blockers
7. We can compare our approach to CrewAI/AutoGen/LangGraph and justify our design decisions

## Suggested Research Approach

**Parallel research threads:**
- Thread A: Deep-dive Kimi Code CLI source code (Agent tool implementation, session management)
- Thread B: Audit existing multi-agent frameworks (CrewAI, AutoGen, LangGraph, OpenAI Swarm)
- Thread C: Research terminal UI patterns (rich, textual, tqdm, progress bar libraries)
- Thread D: Study git worktree and branch isolation patterns (monorepo tools, git-worktree docs)
- Thread E: Analyze user's 3 Kimi Web swarm chats for behavioral patterns and extract reusable logic

**Sources to prioritize:**
- Kimi Code CLI GitHub repo (MoonshotAI/kimi-cli) — read Agent tool source
- CrewAI docs and source code
- AutoGen (Microsoft) documentation
- LangGraph multi-agent patterns
- Git worktree documentation
- Rich library documentation for live displays

**What to verify empirically:**
- Test Kimi Code CLI's `Agent(run_in_background=true)` with 3+ parallel agents
- Test git worktree creation and merging with parallel file edits
- Test rich.live with multiple concurrent progress indicators
