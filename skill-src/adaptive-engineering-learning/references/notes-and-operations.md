# Notes and operations

## Contents

- Note decision
- Markdown and Obsidian writing
- Generated coordination Markdown
- Paths and fallback
- Session close
- Status, pause, re-scan, migration, and recovery

## Note decision

Before writing, search `notes-index.json`, the effective note root, and likely headings. Record only verified, durable material: an important call flow, framework mechanism, reusable debug method, meaningful review, trade-off, corrected misconception, or persistent knowledge gap.

Simple syntax is eligible when it resolves a persistent gap or is useful for later review. Do not create stable notes for temporary paths, guesses, duplicate Q&A, one-off operations, task status or resume state. Prefer updating a related file over creating a micro-note. The per-question context/answer archive described in question-handoff.md is separate from stable knowledge notes.

Cross-window sharing and stable notes serve different purposes:

- publish/sync a result when another active workstream needs it
- write a stable note when the learner will benefit from long-term review
- do both only when both conditions are true

## Markdown and Obsidian writing

Separate general concepts from project-specific experience through headings or a small number of files; do not pre-create category folders. Preserve user prose and unknown sections. Correct contradictions in the relevant managed section rather than appending both claims. Mark unverified content `待验证`.

Use templates in `assets/templates/`. Optional Obsidian links are acceptable, but keep ordinary Markdown readable. After a write, update `notes-index.json` with the effective path, kind, related task IDs, related sources, verification status, and last update. State which notes changed.

Use `apply_patch` for note edits. The state helper indexes existing notes but does not author or overwrite their prose.

## Generated coordination Markdown

The state helper writes:

- `.learning/dashboard.md`
- `.learning/handoffs/<workstream>.md`
- `.learning/sessions/<workstream>/<timestamp>.md`

Dashboard and handoff files are generated snapshots from JSON. Read them freely across Codex tasks, but do not manually maintain authoritative status in them. Rerun:

```text
python <skill-dir>/scripts/learning_state.py dashboard --repo <repo>
```

after recovery or manual JSON repair.

Session logs are historical Markdown. Keep them compact; do not copy the whole chat.

## Paths and fallback

Default notes live at `<repo>/.learning/notes`. For custom notes, set:

```json
"notes": {
  "location": "custom",
  "custom_path": "D:/Obsidian/MyVault/Engineering/ProjectName",
  "fallback_to_project": true,
  "namespace_by_project": false
}
```

Prefer forward slashes in portable examples; Python accepts them on Windows. Relative paths are resolved from the repository and are best for in-repo locations. Absolute external paths can break after moving repositories or switching OS. Keep per-platform path variants in user-managed copies rather than guessing translations.

Run `resolve-notes` before external writes. It reports the effective path and fallback reason. It never creates a missing custom directory. Writing outside the repository may require explicit filesystem approval. If inaccessible and fallback is enabled, use the project path and say so; otherwise do not claim success.

Do not modify `.gitignore` automatically. Ask whether project notes/state should be tracked when Git policy is unknown. Namespace shared Vault paths by project to avoid collisions.

## Session close

On “today stop” in a named workstream:

1. summarize the bounded goal and actual completion
2. update only affected task status/evidence
3. checkpoint the exact resume location and one next step
4. publish durable questions, blockers, findings, or evidence
5. write high-value stable notes only after the note decision
6. write one compact workstream session log when enabled

Use the JSON shape in `assets/examples/minimal-session.json` and run:

```text
python <skill-dir>/scripts/learning_state.py record-session \
  --repo <repo> \
  --workstream <id> \
  --session <session.json>
```

Do not mark a task mastered or a workstream completed merely because the user ends today's session.

## Status, pause, re-scan, migration, and recovery

- Inspect full state: `show --repo <repo> [--workstream <id>]`.
- Load a compact window packet: `context --repo <repo> --workstream <id>`.
- Validate state: `doctor --repo <repo>`.
- Pause/resume the route: use `set-plan-status`; resume only an intact paused plan.
- Pause/resume a window: use `checkpoint --status paused|active`.
- Re-scan: update project facts and report affected tasks/workstreams; keep the active plan unchanged until confirmed.
- Archive: `archive --repo <repo> [--destination <path>]`; it copies state and deletes nothing.
- Migrate v1: explain the layout change, obtain approval, run `migrate-v1`, then run `doctor`.
- Reset: after an archive and explicit request, move the old `.learning/` aside instead of recursively deleting it.
- Migrate notes: copy first, verify files/index and permissions, update config, then leave the source intact until cleanup is approved.
- Corruption: stop writes, run `doctor`, inspect Git/archive/manual edits, and repair the smallest authoritative file.
- Lock timeout: wait for the other Codex task or inspect the lock metadata; never delete a lock automatically.

Never reconstruct mastery from conversation history alone.
