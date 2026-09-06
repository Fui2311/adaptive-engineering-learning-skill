# Advanced state coordination

The everyday UX has two places: the learning mainline and separate Q&A. Exercise, review, debug, pair and implementation remain supported roles for existing state or explicit requests; do not require a new window for every activity.

For the ordinary question transfer, read [question-handoff](question-handoff.md). Use this file only for independent tracking, concurrency or manual recovery.

## Ownership

A learning task owns its objective/status/evidence. A workstream owns a conversation's focus and resume state. One chapter can be referenced by mainline and QA without duplicating progress.

- Activation creates the only mainline.
- QA never directly changes task status.
- Each window checkpoints only itself. The source can prepare an immutable question packet and register a missing QA workstream, but must not overwrite a live QA checkpoint.
- `shared.json` holds accepted cross-window knowledge; inbox entries carry contributions.
- JSON is authoritative; dashboard/handoffs are derived. Stable notes are reader-facing knowledge.

## Register only when needed

```text
python <skill-dir>/scripts/learning_state.py open-workstream --repo <repo> --id <id> --kind <kind> --title "<title>" --task <task-id> --focus "<scope>"
```

Reuse the existing ID in a known conversation. Do not derive identity from whichever window was most recently updated. Pair/implementation require `--confirmation` containing the actual user's permission.

New independent learning objectives use `create-task`; small exercises and short questions do not need another objective. `prepare-qa` registers a QA workstream automatically, without another learning task.

## Read and write

```text
python <skill-dir>/scripts/learning_state.py resume --repo <repo> --workstream <id>
python <skill-dir>/scripts/learning_state.py checkpoint --repo <repo> --workstream <id> --resume-at "<where>" --next-step "<next>" --code "<path:line>" --explanation "<relevant passage>"
```

Checkpoint only changed information. Explain/source passages belong in resume context, not evidence. On leaving a window, save material changes; on session close, record a compact session only if enabled.

## Share durable results

```text
python <skill-dir>/scripts/learning_state.py publish --repo <repo> --workstream <id> --kind answer --task <task-id> --summary "<short conclusion>" --verification verified --source "<path:line>"
python <skill-dir>/scripts/learning_state.py sync --repo <repo> --workstream mainline
```

Publish when the mainline needs the result, not for every QA message. Contributions may be question, answer, finding, blocker, evidence or plan_change. Mark only actually checked results verified; read verification labels on shared items.

Sync merges contributions under the project lock. Answers/findings enter shared knowledge; questions/blockers/evidence may add information to the attached task without changing status. Plan changes remain queued for confirmation. Do not automatically teach, re-plan or master because a side conversation finished.

## Concurrent and failed operations

Use the state helper's lock and atomic writes. Do not manually remove another window's lock or rewrite its checkpoint. On failed writes, stop further mutation, run doctor and inspect the smallest affected files before retrying. Individual atomic file replacements do not constitute a multi-file transaction; preserve the last valid archive and report partial failure honestly.

Thread bindings contain actual task-tool IDs, not a global chat-memory service. If the host cannot access the source repository or task, preserve the packet and report that specific limitation. Do not invent a successful transfer.
