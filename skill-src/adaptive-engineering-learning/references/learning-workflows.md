# Learning workflows

## Contents

- Source teaching
- Contextual Q&A
- Exercises
- Review
- Debug
- Pair and implementation
- Progress evidence

## Source teaching

Run `sync` and load `context` for the active workstream. Read its attached task, exact resume point, code locations, and relevant shared updates; do not re-scan an unchanged repository. Define one bounded goal for the session, then teach in this order when applicable:

1. problem and system position
2. entrypoint
3. control/call flow
4. data transformation
5. module responsibilities
6. design rationale and alternatives
7. strengths, weaknesses, and current must-know details
8. details safe to defer

Prefer diagrams only when the relationship is otherwise hard to follow. Ask the learner to explain, trace, predict, or locate a key element when evidence is needed. Stop after a coherent unit, checkpoint the workstream, and update the task only when its status or evidence materially changed.

## Contextual Q&A

Use a `qa` workstream for a separate Q&A window; attach it to the relevant task when known. Answer from the current repository, stage, task, accepted shared context, and known prerequisites. Keep a narrow syntax question narrow. Explain responsibility and trade-offs for design questions. Then classify the result:

- stable verified knowledge useful to another window: publish a sourced `answer` or `finding`; update a stable note only when it has long-term value
- knowledge gap: publish a `question` or create a review item
- temporary operational detail: do not persist
- plan-changing concern: publish `plan_change`; never rewrite the route automatically

Do not change task status from a Q&A workstream. Preserve the mainline resume location and checkpoint only the Q&A workstream.

## Exercises

Prefer, in order: explain existing code, complete a local TODO, add validation/query, write a test, fix a verified defect, bounded refactor, then a from-scratch demo.

Every exercise specifies background, objective, files, allowed edit boundary, constraints, acceptance criteria, graded hints, and post-completion explanation questions. Create a separate exercise task only when it needs independent progress or a separate Codex window. Keep it feasible in one learning session. Do not reveal the core answer unless the user requests it or changes to pair/implementation mode.

## Review

Attach the review workstream to the task that produced the code. Review the learner's implementation without overwriting it by default. Classify findings as:

- functional/correctness defect
- required engineering fix
- recommended improvement
- style-only issue
- defer at the current learning stage
- over-refactoring to avoid

Use concrete paths/lines and explain impact. Ask the learner to attempt important fixes first when in mentor/review mode. Publish durable findings or blockers when another workstream needs them. Codex-written fixes are not learner evidence.

## Debug

Follow this evidence loop:

```text
symptom -> reproduction -> evidence -> hypotheses -> probability/cost order
-> validation experiment -> narrowed scope -> root cause -> fix -> verification
```

Do not patch from an unverified guess. Checkpoint the hypothesis/evidence boundary so another window can resume precisely. Preserve commands, logs, and results accurately. Publish the verified root cause or blocker. Record a debug note only if the root cause and method are reusable.

## Pair and implementation

Enter `pair` or `implementation` only after explicit user intent. Create an implementation task/workstream with a confirmation record when the work deserves independent scope. Keep source boundaries, acceptance criteria, and learning questions visible.

Separate:

- Codex-authored code and decisions
- learner-authored changes
- learner explanations or predictions
- test/build verification

Only learner-authored work plus learner explanations/predictions can support mastery. Completion of an implementation workstream never automatically masters its attached task.

## Progress evidence

Use `update-task --workstream <id>` for material transitions by the mainline or an attached non-Q&A workstream. Reading once may justify `learning`, not `mastered`. Valid evidence includes the learner explaining a flow in their own words, locating relevant code, completing a bounded change/test, detecting a common failure, or explaining a key trade-off.

Allowed task states are `not_started`, `learning`, `questioning`, `practicing`, `reviewing`, `blocked`, `needs_review`, `mastered`, `paused`, and `skipped`. `mastered` must include evidence when configured.

Pass `--learner-originated` only for evidence actually produced by the learner. A side workstream can publish learner evidence; synchronization adds it to the task without changing status, leaving the mastery decision deliberate.
