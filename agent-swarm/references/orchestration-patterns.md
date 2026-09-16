# Orchestration Patterns

Choose a topology that matches the dependency graph. Keep the number of workers small enough that the coordinator can inspect every result.

## Map and reduce

Use for independent slices with a shared final format.

```text
Coordinator
├── Worker A → artifact A
├── Worker B → artifact B
└── Coordinator → validate and integrate
```

This maximizes parallelism, but it requires clear interfaces and a final conflict check.

## Supervisor

Use when work needs repeated quality gates.

```text
Coordinator → plan
├── workers → bounded artifacts
└── reviewer → findings → coordinator → repair and validate
```

The review stage is a deliberate bottleneck for security or correctness-sensitive work.

## Debate

Use for a disputed architecture or policy. Ask independent reviewers to identify benefits, failure modes, and falsifying experiments, then record the decision and evidence.

## Pipeline

Use when each stage depends on the previous artifact: design, implementation, tests, documentation, then release validation.

## Iterative refinement

Use for drafts that need feedback. Preserve each draft and review so the coordinator can explain what changed.

## Ensemble

Use sparingly for high-uncertainty diagnosis. Multiple independent analyses are useful only when the coordinator has a clear rule for reconciling disagreement.

## Selecting a pattern

| Task shape | Pattern |
|-----------|---------|
| Independent modules | Map and reduce |
| Quality gates | Supervisor |
| Trade-off analysis | Debate |
| Strict dependencies | Pipeline |
| Draft and critique | Iterative refinement |
| High uncertainty | Ensemble |

## Host integration notes

A host adapter should map these concepts to its own worker lifecycle. The skill needs a start operation, bounded context, status signal, cancellation path, and shared artifact location. If the host lacks native worker controls, `dispatch.py` emits one prompt file per assignment and the operator runs those prompts through the host's documented interface. A prompt file is a handoff artifact, not proof that work ran.

Avoid passing large source trees or secrets in prompts. Prefer repository paths, immutable checkpoints, and small evidence files. Workers should write outputs atomically and report an explicit failure state when a prerequisite is missing.
