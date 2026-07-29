# Multi-workstream coordination

## Contents

- Mental model
- Workstream roles
- Start and resume protocol
- Creating learning tasks
- Checkpoints and handoffs
- Cross-workstream publishing
- Synchronization rules
- Conflict and ownership rules
- Recommended window patterns
- End-of-window protocol

## Mental model

Keep two axes separate:

```text
learning task = what the learner is trying to understand or do
workstream    = which Codex task/window is working on it
```

One learning task can receive evidence or questions from several workstreams, but each workstream owns only its own resume state. A workstream can attach to a different task later without resetting the route.

Use:

- `mainline` for curriculum position, chapter progression, and plan-level decisions
- side workstreams for bounded Q&A, exercises, reviews, debug investigations, pair sessions, or implementation labs
- `dashboard.md` for a generated project-wide view
- `handoffs/<workstream>.md` for a generated window-specific resume card
- `inbox/*.json` and `shared.json` for durable cross-window contributions

Do not use Markdown snapshots as the source of task status. They are safe to read in every window because the script can regenerate them from JSON.

## Workstream roles

| Kind | May do | Must not do by default |
| --- | --- | --- |
| `mainline` | advance chapters, change the mainline task, assess mastery, coordinate plan decisions | auto-apply an unconfirmed plan change |
| `qa` | answer a narrow question, publish verified answers/questions/evidence candidates | directly change task status |
| `exercise` | guide and assess a bounded exercise attached to a task | reveal the core answer without permission |
| `review` | classify findings and guide learner fixes | overwrite learner code by default |
| `debug` | reproduce, test hypotheses, identify and verify root cause | patch from an unverified guess |
| `pair` | implement a bounded part with the learner | count Codex-authored code as mastery |
| `implementation` | implement the explicitly authorized scope | expand scope or imply mastery |

Keep one `mainline` workstream. Use stable side IDs that describe the purpose, not an ephemeral conversation number.

## Start and resume protocol

For a new side window:

1. Run `inspect` and `doctor` when state integrity is uncertain.
2. Identify the target task from `dashboard.md` or `show`.
3. Create the workstream:

   ```text
   python <skill-dir>/scripts/learning_state.py open-workstream \
     --repo <repo> \
     --id qa-auth \
     --kind qa \
     --title "Authentication Q&A" \
     --task request-flow-chapter \
     --focus "Resolve token validation questions without moving mainline progress"
   ```

4. Synchronize accepted/pending shared changes and load the compact context:

   ```text
   python <skill-dir>/scripts/learning_state.py sync --repo <repo> --workstream qa-auth
   python <skill-dir>/scripts/learning_state.py context --repo <repo> --workstream qa-auth
   ```

For an existing window, never create a second workstream with the same purpose. Run `context` using its existing ID.

If the workstream is `implementation`, pass `--confirmation "<explicit user permission>"`. Reject an empty or inferred confirmation.

## Creating learning tasks

Create a task when work has its own objective, completion criteria, and evidence. Do not create a task for every short question.

Use task kinds:

- `chapter`: a coherent curriculum understanding thread
- `qa`: a substantial question set worth tracking independently
- `exercise`: a bounded learner implementation or test
- `review`: a review objective with learner fixes
- `debug`: a reproducible investigation
- `implementation`: an explicitly authorized feature lab

Example:

```text
python <skill-dir>/scripts/learning_state.py create-task \
  --repo <repo> \
  --workstream mainline \
  --id exercise-auth-errors \
  --stage request-flow \
  --kind exercise \
  --title "Map authentication errors" \
  --objective "Implement and explain HTTP error mapping for rejected tokens" \
  --source internal/http/auth.go \
  --criterion "Tests pass" \
  --criterion "Learner explains each status-code choice" \
  --after request-flow-chapter
```

Require `--confirmation` for kind `implementation`. Use `--attach` only when the creating workstream should immediately own the new task.

## Checkpoints and handoffs

Checkpoint after a coherent unit, before switching windows, and at session end:

```text
python <skill-dir>/scripts/learning_state.py checkpoint \
  --repo <repo> \
  --workstream qa-auth \
  --resume-at "Token expiry branch in auth middleware" \
  --code internal/http/auth.go:47 \
  --next-step "Compare expiry and signature failure handling"
```

Persist:

- current focus
- exact resume location
- relevant code locations
- blockers and open questions
- one next step
- workstream status when paused, blocked, or completed

Do not copy the full chat into a handoff. The generated Markdown card must remain compact enough for another Codex task to read immediately.

Use `record-session --workstream <id>` when the user ends a learning session and session logs are enabled. It writes under `sessions/<workstream>/`.

## Cross-workstream publishing

Publish only information that another window would benefit from:

```text
python <skill-dir>/scripts/learning_state.py publish \
  --repo <repo> \
  --workstream qa-auth \
  --kind answer \
  --task request-flow-chapter \
  --summary "The middleware maps expired tokens before the handler runs." \
  --verification verified \
  --source internal/http/auth.go:47
```

Contribution kinds:

- `question`: a durable unresolved question
- `answer`: a verified reusable answer
- `finding`: an observed architectural, quality, or debugging fact
- `evidence`: a mastery evidence candidate
- `blocker`: a condition preventing progress
- `plan_change`: a suggestion that affects route scope, order, or depth

Verified answers and findings require repository sources. Mark uncertain material `pending`.

For evidence, pass `--learner-originated` only when the learner actually explained, predicted, located, implemented, tested, or diagnosed the relevant behavior. Codex-generated explanations and code are not learner-originated.

## Synchronization rules

Run:

```text
python <skill-dir>/scripts/learning_state.py sync --repo <repo> --workstream <id>
```

The deterministic merge behavior is:

- accept answers and findings into shared knowledge
- accept questions and blockers into shared state and the related task
- accept learner-originated evidence into the related task without changing its status
- queue non-learner evidence as a candidate only
- queue every plan change as `needs_confirmation`
- never auto-mark a task `mastered`
- never auto-reorder or replace the plan

Run `context` after synchronization so the window receives the latest shared revision.

## Conflict and ownership rules

Every mutation acquires `.learning/.state.lock`. If another Codex task is writing, wait for the command to return or retry after the reported lock clears. Never delete the lock automatically; inspect the owning process and state first.

Avoid lost updates through narrow writes:

- update only explicit task fields through `update-task`
- update only one workstream through `checkpoint`
- publish append-only contributions instead of directly editing another window's state
- let `sync` re-read files after taking the lock

Use these authority boundaries:

- `plan.json`: change only through the confirmed planning workflow
- `tasks/<id>.json`: update through the mainline or an attached non-Q&A workstream
- `workstreams/<id>.json`: update only from that workstream
- `shared.json`: update only through `sync`
- `dashboard.md` and `handoffs/*.md`: regenerate; never treat manual edits as state
- stable notes: edit through the note workflow and index after writing

If manual edits conflict, stop mutations, run `doctor`, compare Git/archive copies, and repair the smallest authoritative JSON file.

## Recommended window patterns

### Mainline plus Q&A

- Mainline teaches the active chapter and owns mastery decisions.
- Q&A attaches to the current chapter, publishes verified answers or questions, and checkpoints its own detour.
- Mainline runs `sync` before continuing and incorporates only durable results.

### Mainline plus exercise/review

- Create one exercise task with clear acceptance criteria.
- Attach an exercise workstream while the learner implements.
- Open a review workstream on the same task when code is ready.
- Publish findings; let the owning workstream update task status after learner action.

### Mainline plus feature implementation

- Record explicit permission in both the implementation task and workstream.
- Bound source paths and acceptance criteria.
- Keep learning objectives visible even when Codex writes code.
- Publish reusable findings and learner evidence separately.

### Parallel chapter exploration

- Keep the confirmed route in `plan.json`.
- Create separate chapter tasks only when the user wants parallel study.
- Attach one workstream per chapter.
- Do not move `mainline_task_id` merely because a side chapter produced progress.

## End-of-window protocol

1. Checkpoint the exact resume location and one next step.
2. Publish durable shared findings, questions, blockers, or evidence.
3. Run `sync` when another window needs the result immediately.
4. Write a compact session log only when the user stops or a durable session record is useful.
5. Report which JSON state and Markdown snapshots changed.

Do not mark a workstream completed when its attached learning task still needs a deliberate handoff, and do not mark a learning task mastered merely because the workstream completed.
