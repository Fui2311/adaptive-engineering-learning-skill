# State model

The streamlined interface retains schema v2: no migration for existing v2 projects. `resume` reads without initialization; `prepare-qa` adds immutable `questions/<id>.json` snapshots and derived reading pages. Answers live in `questions/<id>-answer.md`. Workstreams may contain optional `recent_explanation` and `thread: {id, host}` fields; these are neither learner evidence nor task status. Older v2 state needs no new fields. A saved source repository/HEAD identifies the historical question context; the destination still verifies current source. Runtime question handoff requires an active/paused route; standalone Q&A needs no course state.

## Contents

- Storage layout
- Sources of truth
- Configuration
- Project and plan
- Learning tasks
- Workstreams
- Shared coordination
- Markdown snapshots and notes
- Lifecycle invariants
- Locking and recovery
- Schema v1 migration

## Storage layout

Use `.learning/` as the project-local default:

```text
.learning/
  config.json               # preferences, permissions, coordination policy
  project.json              # last verified repository facts
  project-map.md            # human-facing discovery map
  plan.json                 # proposed or confirmed curriculum route
  workspace.json            # task/workstream registry and mainline pointers
  shared.json               # accepted cross-workstream knowledge and queues
  dashboard.md              # generated human-readable project overview
  tasks/
    <task-id>.json           # one authoritative learning-unit state per file
  workstreams/
    <workstream-id>.json     # one Codex window state per file
  inbox/
    <contribution-id>.json   # append-only cross-window contributions
  handoffs/
    <workstream-id>.md       # generated resumable Markdown card
  notes-index.json           # stable note registry
  notes/                     # verified Markdown/Obsidian knowledge
  sessions/
    <workstream-id>/         # compact per-window session logs
  legacy/                    # preserved migrated state
```

Do not pre-create empty note trees. Activation creates only runtime files required by the confirmed route.

## Sources of truth

Keep each kind of information in one authoritative place:

| Concern | Authority | Derived/read-only views |
| --- | --- | --- |
| repository facts | `project.json` | `project-map.md` |
| curriculum scope/order | `plan.json` | dashboard route section |
| task status/evidence | `tasks/<id>.json` | dashboard task table |
| Codex window resume point | `workstreams/<id>.json` | `handoffs/<id>.md` |
| accepted shared context | `shared.json` | dashboard shared sections |
| pending cross-window update | `inbox/<id>.json` | pending count in `context` |
| stable knowledge | Markdown notes | `notes-index.json` metadata |

Never duplicate task status in notes, handoffs, or session logs. Regenerate derived Markdown after recovery or manual JSON repair.

## Configuration

Use schema version 2. Important controls include:

- `learning.mode`, explanation depth, and exercise/review switches
- `permissions.allow_business_code_changes` and `allow_test_skeletons`
- `planning.require_confirmation == true`
- `planning.auto_activate_plan == false`
- `coordination.multi_workstream == true`
- `coordination.mainline_workstream_id`
- `coordination.plan_changes_require_confirmation == true`
- `progress.mastery_requires_evidence`
- `progress.mastery_requires_learner_origin`
- note location, fallback, logging, and categories
- project focus and exclusions

Keep the confirmation and plan-change guards fixed. Do not use configuration to bypass them.

## Project and plan

`project.json` stores repository identity, scan branch/head, verified commands, stack, entrypoints, modules, important docs, learning-value judgment, and scan time.

`plan.json` contains:

```json
{
  "schema_version": 2,
  "plan_version": 1,
  "status": "proposed",
  "goals": ["..."],
  "stages": [
    {
      "id": "request-flow",
      "title": "...",
      "learning_thread": "...",
      "core_questions": ["..."],
      "source_scope": ["path/..."],
      "prerequisites": ["..."],
      "exercise": null,
      "completion_criteria": ["learner can ..."],
      "skippable": false,
      "optional": false
    }
  ],
  "skipped_topics": [],
  "optional_topics": [],
  "manual_adjustments": [],
  "change_log": []
}
```

Plan statuses remain `proposed`, `active`, `paused`, `completed`, and `superseded`. Re-scan project facts without rewriting an active plan. Queue cross-window plan-change requests until the user confirms a revision.

## Learning tasks

Store each learning unit in `tasks/<task-id>.json` to avoid unrelated Codex windows rewriting one monolithic progress file.

Task kinds:

```text
chapter
qa
exercise
review
debug
implementation
```

Task states:

```text
not_started
learning
questioning
practicing
reviewing
blocked
needs_review
mastered
paused
skipped
```

A task owns:

- stage and kind
- objective, source scope, prerequisites, and completion criteria
- status
- learner evidence
- open questions and blockers
- code locations and next step
- owner workstream
- revision and timestamps

Activation creates one chapter task per confirmed stage. Split or add a task only when a bounded exercise, review, debug investigation, Q&A body, feature implementation, or parallel chapter needs its own objective and completion criteria.

Implementation tasks require a non-empty user confirmation record.

## Workstreams

Store each Codex task/window in `workstreams/<id>.json`.

A workstream owns:

- role kind and status
- attached learning task
- parent workstream
- current focus
- exact resume point
- code locations
- local questions and blockers
- one next step
- last seen shared revision
- revision and timestamps

Use exactly one `mainline` role. Side roles can attach to mainline or additional tasks. A completed workstream does not imply a mastered task.

`workspace.json` owns:

- `plan_version`
- mainline workstream and task pointers
- ordered task IDs
- ordered workstream IDs
- latest shared revision
- workspace revision

Require `workspace.plan_version == plan.plan_version` before task changes.

## Shared coordination

Side windows publish immutable contribution files to `inbox/`. The synchronizer processes each pending contribution once and records its terminal inbox state:

- `accepted`: merged into shared/task state
- `queued`: preserved for judgment or confirmation

`shared.json` contains:

- verified or pending knowledge
- shared questions
- shared blockers
- evidence candidates
- plan-change requests

Apply merge rules:

1. Merge answers/findings into shared knowledge.
2. Merge questions/blockers into shared state and the related task.
3. Add learner-originated evidence to the related task without changing its status.
4. Queue evidence without learner origin.
5. Queue all plan changes with `needs_confirmation`.
6. Never auto-mark mastery or auto-edit the plan.

## Markdown snapshots and notes

Use Markdown for human continuity:

- `dashboard.md`: project-wide task/workstream/shared overview
- `handoffs/<id>.md`: one window resume card
- `sessions/<id>/*.md`: compact session history
- stable notes: durable verified knowledge

The script regenerates dashboards and handoffs from JSON. Preserve user-authored stable notes with `apply_patch`; never replace them from generated state.

## Lifecycle invariants

1. Proposal creation must not create workspace, tasks, workstreams, or legacy `progress.json`.
2. Activation requires explicit non-empty confirmation.
3. Plan revision increments `plan_version` and preserves a concise change log.
4. Active/paused/completed plans require `workspace.json`.
5. Workspace and plan versions must match.
6. Every workspace task/workstream ID must resolve to a valid file.
7. A Q&A workstream cannot directly change task status.
8. A non-mainline workstream can directly update only its attached task.
9. Mastery requires evidence and at least one learner-originated item by default.
10. Codex implementation or explanation alone is not learner evidence.
11. Implementation tasks/workstreams require explicit permission records.
12. Cross-window plan changes remain queued until confirmation.
13. Re-scan never activates or overwrites an active route.
14. Corrupt or missing files never justify inventing completed work.

## Locking and recovery

Every mutating command acquires `.learning/.state.lock` using exclusive file creation. Each command re-reads authoritative files after taking the lock and writes atomically with `os.replace`.

If lock acquisition times out:

- do not delete the lock automatically
- wait for the other Codex task or inspect the recorded PID/operation
- verify whether a process is still active
- run `doctor` after resolving a genuinely stale lock

Use append-only inbox files to reduce cross-window contention. Keep writes narrow: checkpoint one workstream, update one task, or synchronize contributions.

Archive before destructive recovery. Repair the smallest field or file and regenerate Markdown views.

## Schema v1 migration

Schema v1 used one `progress.json` and assumed a single active Codex window. Migrate only after explaining the change and obtaining approval:

```text
python <skill-dir>/scripts/learning_state.py migrate-v1 --repo <repo>
```

The command:

1. copies the full state to `.learning-archives/migration-v1-<timestamp>`
2. upgrades config, project, plan, and note index to schema 2
3. converts each old progress task into `tasks/<id>.json`
4. creates the `mainline` workstream and workspace registry
5. copies old progress to `legacy/progress-v1.json`
6. removes only the now-migrated root `progress.json`
7. generates the mainline handoff and dashboard

Run `doctor` immediately after migration. Never infer new evidence or mastered statuses during conversion.
