# Learning workflows

## Contents

- Source teaching
- Contextual Q&A
- Exercises
- Review
- Debug
- Progress evidence

## Source teaching

Read the active task and resume from its `current_code_locations`; do not re-scan an unchanged repository. Define one bounded goal for the session, then teach in this order when applicable:

1. problem and system position
2. entrypoint
3. control/call flow
4. data transformation
5. module responsibilities
6. design rationale and alternatives
7. strengths, weaknesses, and current must-know details
8. details safe to defer

Prefer diagrams only when the relationship is otherwise hard to follow. Ask the learner to explain, trace, predict, or locate a key element when evidence is needed. Stop after a coherent unit.

## Contextual Q&A

Answer from the current repository, stage, task, and known prerequisites. Keep a narrow syntax question narrow. Explain responsibility and trade-offs for design questions. Then silently classify the result:

- stable verified knowledge: update an existing note or create one useful note
- knowledge gap: add an open question or review item
- temporary operational detail: do not persist
- plan-changing concern: suggest a revision, but do not rewrite the route automatically

Do not interrupt the current task for a detour; preserve the resume location.

## Exercises

Prefer, in order: explain existing code, complete a local TODO, add validation/query, write a test, fix a verified defect, bounded refactor, then a from-scratch demo.

Every exercise specifies background, objective, files, allowed edit boundary, constraints, acceptance criteria, graded hints, and post-completion explanation questions. Keep it feasible in one learning session. Do not reveal the core answer unless the user requests it or changes to pair/implementation mode.

## Review

Review the learner's implementation without overwriting it by default. Classify findings as:

- functional/correctness defect
- required engineering fix
- recommended improvement
- style-only issue
- defer at the current learning stage
- over-refactoring to avoid

Use concrete paths/lines and explain impact. Ask the learner to attempt important fixes first when in mentor/review mode. Codex-written fixes are not learner evidence.

## Debug

Follow this evidence loop:

```text
symptom -> reproduction -> evidence -> hypotheses -> probability/cost order
-> validation experiment -> narrowed scope -> root cause -> fix -> verification
```

Do not patch from an unverified guess. Preserve commands, logs, and results accurately. After verification, record a debug note only if the root cause and method are reusable.

## Progress evidence

Use `update-task` for material transitions. Reading once may justify `learning`, not `mastered`. Valid evidence includes the learner explaining a flow in their own words, locating relevant code, completing a bounded change/test, detecting a common failure, or explaining a key trade-off.

Allowed task states are `not_started`, `learning`, `questioning`, `practicing`, `reviewing`, `blocked`, `needs_review`, `mastered`, `paused`, and `skipped`. `mastered` must include evidence when configured.
