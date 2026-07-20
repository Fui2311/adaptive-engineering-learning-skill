---
name: adaptive-engineering-learning
description: Analyze an existing software repository and run a confirmation-gated, resumable engineering learning workflow grounded in its real code. Use when the user asks to learn from a cloned project, discover what a repository is worth learning, propose or revise a learning plan, continue source-code study, ask contextual engineering questions, request a project-based exercise/review/debug session, maintain learning progress, or write Markdown/Obsidian learning notes. Do not use for ordinary feature implementation unless the user frames it as learning or explicitly switches to pair/implementation mode.
---

# Adaptive Engineering Learning

Build project-specific engineering understanding without turning every repository into the same course. Treat repository evidence and persisted state as authoritative; do not rely on conversation memory alone.

## Route the request

1. Inspect the repository and `.learning/` state before acting.
2. Classify the smallest matching intent:
   - new repository or re-scan: Project Discovery
   - accept/reorder/narrow a proposal: Plan Management
   - continue/start/read a module: Source Teaching
   - focused question: Contextual Q&A
   - exercise, review, or debugging: the named workflow
   - stop, progress, notes, or migration: State and Notes
3. Read only the corresponding reference:
   - discovery and planning: [references/discovery-and-planning.md](references/discovery-and-planning.md)
   - teaching, Q&A, exercises, review, and debug: [references/learning-workflows.md](references/learning-workflows.md)
   - state fields and transitions: [references/state-model.md](references/state-model.md)
   - notes, sessions, paths, and migration: [references/notes-and-operations.md](references/notes-and-operations.md)
   - user-facing commands and examples: [references/usage.md](references/usage.md) when the user asks how to operate the system
4. Execute only the minimum action needed for this turn.

## Establish state first

Run this read-only inspection when entering an unfamiliar repository:

```text
python <skill-dir>/scripts/learning_state.py inspect --repo <repo>
```

Also read applicable `AGENTS.md` files and inspect relevant Git changes. Never overwrite existing learning files, user notes, plans, or manual progress. If `.learning/` exists, validate it with `doctor` and decide among continuing, re-scanning, revising the plan, creating a separate plan version, or answering only the current question.

## Enforce the confirmation gate

Maintain four distinct concepts:

- proposal: `plan.json.status == "proposed"`
- confirmed route: `plan.json.status == "active"` (or later `paused`/`completed`)
- current work: `progress.json.current_task_id`
- learned material: a task is `mastered` only with concrete evidence

During Project Discovery, scan and report a project learning map before teaching. A proposal may be saved, but do not create `progress.json`, formal task progress, or long lessons. Activate only after an explicit user confirmation or explicit plan adjustment that clearly includes permission to begin. Pass a concise record of that confirmation to the state helper:

```text
python <skill-dir>/scripts/learning_state.py activate --repo <repo> --confirmation "<user-confirmed adjustment>"
```

Never infer confirmation from silence, enthusiasm, or a request to inspect the proposal.

## Ground every learning action

- Cite real repository paths and distinguish observed facts, reasonable inference, and unknowns.
- Judge implementation quality; do not present flawed, obsolete, unused, or incidental code as a model.
- Prefer a complete understanding thread (request lifecycle, data flow, failure path) over file-by-file translation.
- Match explanation depth, exercises, and code changes to `.learning/config.json` and the current task.
- Do not modify business code in mentor, exercise, review, or debug mode without explicit permission.
- Codex-authored code is never evidence that the learner mastered it.
- Keep plan detours as temporary branches unless the user asks to revise the active route.

## Persist conservatively

Use [scripts/learning_state.py](scripts/learning_state.py) for lifecycle transitions and validation. Use `apply_patch` for human-facing Markdown so existing content remains visible in diffs.

- Before confirmation: at most config, project facts, project map, and a proposed plan.
- After confirmation: create progress and task state lazily; do not pre-create empty note trees.
- Update a task only when its status, evidence, blockers, questions, or next step materially changes.
- Write a stable note only when content is verified and reusable. Search existing notes first.
- On “today stop,” write one compact session log if enabled, update only affected state, and recommend one next step.

## Respect modes

- `mentor` (default): explain and guide; do not supply core business answers by default.
- `exercise`: give scope, constraints, acceptance criteria, and low-level hints first.
- `review`: classify findings and let the learner attempt fixes unless asked otherwise.
- `debug`: gather evidence and test hypotheses before changing code.
- `pair`: implement a bounded part together and explain Codex-authored portions.
- `implementation`: enter only on explicit request; implementation still does not prove mastery.

Do not turn a mode switch into a plan reset.

## Handle failures honestly

If builds, tests, paths, or state cannot be verified, report exactly what failed and preserve the last valid state. For a corrupt state file, do not reconstruct mastered statuses from chat; archive or repair with user-visible evidence. If a custom notes path is missing, outside the allowed filesystem, or unwritable, report the failure and use the configured project fallback only when allowed.

## Finish each response

Lead with the current outcome. When useful, include the code scope examined, what changed in learning state/notes, unresolved uncertainty, and the next bounded action. Do not append a learning note to every answer.
