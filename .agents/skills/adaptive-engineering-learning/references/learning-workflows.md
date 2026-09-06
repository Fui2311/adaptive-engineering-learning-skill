# Learning workflows

Intent and persistence defaults live in SKILL.md. Read only the relevant section here; ordinary QA is direct explanation, not an exercise.

## Source teaching and Q&A

Start with the user's confusion or the saved lesson goal. Explain the problem, trace a real entrypoint through the relevant call/data/failure path, then discuss responsibility and trade-offs. Teach missing prerequisites inline. Do not translate every file or require a learner answer before explaining an unfamiliar concept.

Load compact context once at entry and source files as needed. Do not scan the unchanged repository or run sync/context before every answer. Keep short syntax questions short. A question within the mainline can be answered without changing its role or checkpoint. If the user wants isolation, follow [question-handoff](question-handoff.md) to move context into a dedicated task.

Save changed resume state at meaningful boundaries. Use `checkpoint --explanation` for a recent teaching passage needed for later questions, never as learner evidence. Mark uncertainty and source quality explicitly.

## Exercises

Only use an exercise when requested or accepted. Prefer explaining/tracing existing code, a bounded TODO, validation/test, verified defect fix, then a from-scratch demo.

Give the objective, source/edit boundary and acceptance criteria; include constraints when material. Offer graded hints one at a time. Do not reveal the core answer until requested. Avoid mandatory eight-field forms for small exercises. An exercise only needs a separate task when it has independent progress; it does not require a separate Codex window.

## Review and debug

For learner code, classify correctness defects, required engineering fixes, optional improvements and details safe to defer. Explain impact at concrete code locations; let the learner fix issues unless they request implementation.

For debug, reproduce the symptom, collect evidence, test plausible hypotheses, identify the root cause and verify the authorized fix. Preserve the last verified finding and next experiment when blocked. Do not turn a guess into a root-cause claim.

## Pair and implementation

The user's explicit request to implement or pair is authorization for the specified scope; record that intent instead of asking again. Keep business edit boundaries and acceptance criteria clear. Existing `pair`/`implementation` task/workstream commands require a non-empty confirmation record.

Distinguish Codex-authored changes, learner-authored work and test results. A passing assistant-written implementation does not prove learner mastery.

## Progress evidence

No forced quiz after routine teaching. Request a focused explanation, prediction or implementation only when assessing progress or when the learner asks for practice. Acknowledgement such as “懂了” alone is not evidence.

Use `update-task` for material status/evidence changes by an owning non-QA workstream. Existing statuses remain supported: not_started, learning, questioning, practicing, reviewing, blocked, needs_review, mastered, paused, skipped. Do not expose this list as a user form.

Use `--learner-originated` only for actual learner evidence. QA may publish evidence candidates, but cannot change task status. Synchronization never automatically masters a task or changes a route.
