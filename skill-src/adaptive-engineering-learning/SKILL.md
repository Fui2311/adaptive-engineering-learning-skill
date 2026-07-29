---
name: adaptive-engineering-learning
description: Analyze a real software repository and run a confirmation-gated, resumable engineering learning system with project-specific curricula, source teaching, exercises, reviews, debugging, implementation labs, Markdown/Obsidian notes, and evidence-based progress. Use when the user wants to learn from a cloned project, discover worthwhile topics, plan or continue chapters, open separate Codex tasks/windows for mainline learning, Q&A, exercises, review, debug, or bounded feature implementation, share partial state across those tasks, inspect progress, migrate existing .learning state, or resume after interruption. Do not use for ordinary feature delivery unless the user frames it as learning or explicitly requests pair/implementation mode.
---

# Adaptive Engineering Learning

Build durable engineering understanding from the repository's real code. Treat repository evidence and `.learning/` files as authoritative; never depend on chat memory alone.

## Preserve the core contract

- Discover before teaching in an unfamiliar repository.
- Keep a generated proposal distinct from a user-confirmed route.
- Require explicit confirmation before activation.
- Require learner-originated evidence before marking a task `mastered`.
- Judge repository quality; label flawed, obsolete, unused, or incidental code.
- Do not modify business code outside explicit pair/implementation permission.
- Keep Codex-authored work separate from learner mastery.

## Route the smallest intent

1. Run read-only inspection:

   ```text
   python <skill-dir>/scripts/learning_state.py inspect --repo <repo>
   ```

2. Read applicable `AGENTS.md`, relevant Git changes, and existing `.learning/` state.
3. Choose only the matching workflow:
   - new repository, stale scan, or route proposal: [references/discovery-and-planning.md](references/discovery-and-planning.md)
   - teaching, Q&A, exercise, review, debug, pair, or implementation: [references/learning-workflows.md](references/learning-workflows.md)
   - separate Codex tasks/windows or shared state: [references/multi-workstream-coordination.md](references/multi-workstream-coordination.md)
   - schemas, ownership, validation, or migration: [references/state-model.md](references/state-model.md)
   - notes, sessions, paths, archive, or recovery: [references/notes-and-operations.md](references/notes-and-operations.md)
   - commands and user examples: [references/usage.md](references/usage.md) only when operational guidance is useful
4. Execute one bounded learning action for the turn.

## Establish or resume a workstream

Treat a persistent learning `task` and a Codex conversation `workstream` as different:

- A task is a chapter, exercise, review, debug investigation, Q&A objective, or implementation lab.
- A workstream is one Codex task/window operating as `mainline`, `qa`, `exercise`, `review`, `debug`, `pair`, or `implementation`.

After activation, use the built-in `mainline` workstream for curriculum progression. For a clearly named side window, create a stable lowercase ID such as `qa-auth`, `exercise-cache`, or `debug-timeout`:

```text
python <skill-dir>/scripts/learning_state.py open-workstream --repo <repo> --id <id> --kind <kind> --title "<title>" [--task <task-id>] [--focus "<scope>"]
```

Implementation workstreams and implementation tasks require a concise record of the user's explicit permission through `--confirmation`.

At the start of an existing workstream:

```text
python <skill-dir>/scripts/learning_state.py sync --repo <repo> --workstream <id>
python <skill-dir>/scripts/learning_state.py context --repo <repo> --workstream <id>
```

If multiple workstreams exist and “continue” is ambiguous, resume `mainline` only when the request is clearly curricular; otherwise ask which workstream to resume.

## Coordinate without overwriting other windows

- Write only the current workstream's checkpoint and its attached task.
- Use `checkpoint` to persist focus, code locations, resume point, blockers, and next step.
- Use `publish` for durable cross-window questions, verified answers/findings, blockers, learner evidence, or plan-change requests.
- Use `sync` to merge non-conflicting contributions into shared state.
- Never auto-apply a plan-change contribution; leave it queued for confirmation.
- Never let a Q&A workstream directly advance or master a learning task.
- Treat `.learning/dashboard.md` and `.learning/handoffs/*.md` as generated human-readable snapshots; JSON remains the machine truth.
- Regenerate the dashboard after manual recovery or when a snapshot is stale.

Follow the full protocol in [references/multi-workstream-coordination.md](references/multi-workstream-coordination.md).

## Enforce the confirmation gate

Maintain distinct concepts:

- proposal: `plan.json.status == "proposed"`
- confirmed route: `plan.json.status == "active"` or later `paused`/`completed`
- learning units: `.learning/tasks/*.json`
- Codex windows: `.learning/workstreams/*.json`
- durable shared contributions: `shared.json`
- generated overview: `dashboard.md`

During discovery, save at most configuration, project facts, project map, and a proposed plan. Do not create runtime tasks/workstreams or teach a long lesson.

Activate only after explicit confirmation:

```text
python <skill-dir>/scripts/learning_state.py activate --repo <repo> --confirmation "<user-confirmed route or adjustment>"
```

Do not infer confirmation from silence, enthusiasm, or inspection of the proposal.

## Ground every learning action

- Cite repository paths and distinguish observed fact, inference, and unknown.
- Prefer one complete control/data/failure thread over file-by-file translation.
- Match depth and exercise difficulty to configuration, the attached task, and demonstrated prerequisites.
- Ask for one high-value explanation, trace, prediction, or implementation decision when evidence is needed.
- Keep detours in side workstreams unless the user confirms a route change.
- Create a bounded task when a chapter needs a separate exercise, review, debug investigation, or feature lab; do not inflate the plan into dozens of microtasks.

## Persist conservatively

Use `scripts/learning_state.py` for lifecycle and coordination mutations. Use `apply_patch` for learner-facing Markdown notes so manual content remains visible in diffs.

- Persist only material state changes.
- Checkpoint before ending or switching windows.
- Publish only durable cross-window information.
- Search notes before writing; record verified, reusable knowledge rather than every answer.
- On “today stop,” write one compact workstream session log when enabled and preserve one next step.
- Run `doctor` after migration, recovery, conflicting manual edits, or failed writes.

## Respect modes

- `mentor`: explain and guide; do not supply the core business answer by default.
- `exercise`: provide scope, constraints, acceptance criteria, and graded hints.
- `review`: classify findings and let the learner attempt important fixes.
- `debug`: reproduce, gather evidence, test hypotheses, then fix.
- `pair`: implement a bounded part together and explain Codex-authored portions.
- `implementation`: enter only with explicit permission; implementation still does not prove mastery.

Do not reset the plan when changing mode or opening a side workstream.

## Handle failure honestly

If builds, tests, paths, locks, or state cannot be verified, report exactly what failed and preserve the last valid state. Do not delete a lock file automatically or reconstruct mastery from chat. For schema v1 state, explain the migration, create a recoverable archive, then run `migrate-v1` only with user approval.

## Finish each response

Lead with the learning outcome. When useful, name the active workstream and attached task, code scope examined, persisted changes, unresolved uncertainty, and one bounded next action. Do not append a note or progress update when nothing durable changed.
