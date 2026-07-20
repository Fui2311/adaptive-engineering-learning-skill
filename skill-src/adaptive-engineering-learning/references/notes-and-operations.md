# Notes and operations

## Contents

- Note decision
- Markdown/Obsidian writing
- Paths and fallback
- Session close
- Status, pause, re-scan, migration, and recovery

## Note decision

Before writing, search `notes-index.json`, the effective note root, and likely headings. Record only verified, durable material: an important call flow, framework mechanism, reusable debug method, meaningful review, trade-off, corrected misconception, or persistent knowledge gap.

Do not create a stable note for simple syntax, temporary paths, guesses, repeated Q&A, or one-off operation details. Prefer updating a related file over creating a micro-note.

## Markdown/Obsidian writing

Separate general concepts from project-specific experience through headings or a small number of files; do not pre-create category folders. Preserve user prose and unknown sections. Correct contradictions in the relevant managed section rather than appending both claims. Mark unverified content `待验证`.

Use templates in `assets/templates/`. Optional Obsidian links are acceptable, but keep ordinary Markdown readable. After a write, update `notes-index.json` with the effective path, kind, related sources, verification status, and last update. State which notes changed.

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

Run `resolve-notes` before external writes. It reports the effective path and fallback reason. It never creates a missing custom directory. Writing outside the repository may require explicit filesystem approval. If inaccessible and fallback is enabled, use the project path and say so; otherwise do not claim success. Do not modify `.gitignore` automatically. Ask whether project notes/state should be tracked when Git policy is unknown. Namespace shared Vault paths by project to avoid collisions.

## Session close

On “today stop”:

1. Summarize the goal and actual completion.
2. Update affected task state and evidence only.
3. Write high-value notes only after the note decision.
4. Record open questions and one next step.
5. If session logs are enabled, create one compact log from `assets/examples/minimal-session.md`; never copy the whole chat.

## Status, pause, re-scan, migration, and recovery

- View current state: `show --repo <repo>`.
- Validate state: `doctor --repo <repo>`.
- Pause/resume: use `set-plan-status`; resume only an intact paused plan.
- Re-scan: inspect repository changes, update `project.json`, and issue a diff report; keep active plan unchanged until confirmed.
- Archive before reset: `archive --repo <repo> [--destination <path>]`. By default it copies to `.learning-archives/<timestamp>` and deletes nothing.
- Reset: after an archive and explicit request, move the old `.learning/` aside rather than recursively deleting it, then begin discovery.
- Migrate notes: copy first, verify files/index and permissions, update config, then leave the source intact until the user approves cleanup.
- Corruption: stop writes to the damaged file, run `doctor`, inspect Git/archive/manual edits, and repair the smallest field. Never infer mastery from conversation history alone.
