# State model

## Contents

- Storage layout
- Configuration
- Project and plan schemas
- Progress ownership
- Lifecycle invariants

## Storage layout

Use `.learning/` as the project-local default because it separates agent-managed learning state from product documentation and avoids clutter. Do not create category directories until content exists.

```text
.learning/
  config.json          # preferences and permissions
  project.json         # last verified repository facts
  project-map.md       # human learning map
  plan.json            # proposed/confirmed route and version history
  progress.json        # runtime task state; active plans only
  notes-index.json     # note locations/checksums; create on first note
  notes/               # default Markdown/Obsidian notes
  sessions/            # compact session logs; create on first log
  archives/            # optional recovery snapshots
```

Do not duplicate task status in Markdown. `plan.json` owns intended route; `progress.json` owns execution state; notes contain knowledge, not workflow truth.

## Configuration

Use JSON because the bundled state helper can parse, validate, and atomically update it with the Python standard library on Windows, macOS, and Linux. Markdown remains the human knowledge format. See `assets/examples/minimal-config.json`.

Important controls:

- `learning.mode`, `explanation_depth`, exercise/review switches
- `permissions.allow_business_code_changes` and `allow_test_skeletons`
- `planning.require_confirmation` and `auto_activate_plan` (must remain true/false respectively for the confirmation gate)
- `progress.mastery_requires_evidence`
- `notes.location`, `custom_path`, fallback, logs, and category switches
- `project.focus` and `excluded_topics`

## Project and plan schemas

`project.json` stores repository identity, branch/head, verified commands, stack, entrypoints, modules, important docs, learning-value summary, and scan timestamp. Facts should carry verification status where ambiguity matters.

`plan.json` contains:

```json
{
  "schema_version": 1,
  "plan_version": 1,
  "status": "proposed",
  "goals": ["..."],
  "stages": [
    {
      "id": "stage-01",
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

Plan statuses: `proposed`, `active`, `paused`, `completed`, `superseded`. A major alternative route should supersede an archived prior plan instead of silently replacing it.

## Progress ownership

`progress.json` is created only by activation. It owns current stage/task, current code locations, per-task status/evidence/questions, blockers, review queue, recent completion, next step, and review topics. The helper initially creates one coherent task per stage; split a stage only when actual teaching requires it.

## Lifecycle invariants

1. Proposal creation must not create progress.
2. Activation requires an explicit non-empty confirmation record.
3. Plan revision increments `plan_version` and preserves a concise change log.
4. `progress.plan_version` must match the active plan before task updates.
5. `mastered` requires learner evidence when configured.
6. Re-scan updates project facts but never activates or overwrites an active route.
7. Missing/corrupt files do not justify inventing completed work.
8. Low-risk state updates are allowed; destructive reset requires a recoverable archive and explicit user intent.
