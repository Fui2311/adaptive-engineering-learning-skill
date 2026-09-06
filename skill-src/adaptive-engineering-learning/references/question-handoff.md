# Questions outside the mainline

The learner only needs to say “把这个问题单独开个问答任务”. Preserve the lesson and give the destination enough context to explain immediately. A skill invocation loads instructions; it does not request initialization.

## Prepare a question packet

Resolve the question and referents from the visible conversation first, then its saved `recent_explanation` after interruption. If the source task is explicitly identified and task-reading tools exist, read the relevant turns. Do not scan unrelated tasks or hidden application databases. If “这段” still has no identifiable referent, ask one short clarification.

For an active/paused v2 route, write a temporary JSON input outside the skill directory:

```json
{
  "question": "这里的 context 为什么要往下传？",
  "context": "The actual relevant explanation and code passage from this lesson.",
  "confusion": "How request cancellation reaches the repository.",
  "code_locations": ["internal/http/handler.go:42"],
  "known": ["Only prerequisites demonstrated or stated by the learner"],
  "unknown": ["Whether this driver supports cancellation; verify in source"]
}
```

The agent supplies these fields, never the user. Include the relevant passage, not just a topic label; exclude unrelated history and credentials. Checkpoint changed source lesson state, then:

```text
python <skill-dir>/scripts/learning_state.py prepare-qa --repo <source-repo> --source <source-workstream> --id <stable-question-id> --packet <input.json>
```

The helper freezes `.learning/questions/<id>.json`, renders `<id>.md` for review, and returns a ready-to-send `prompt`, answer path and optional destination thread binding. It reuses a QA workstream per chapter without changing its live checkpoint. Related follow-ups can update the same answer; new questions get new packets. Retrying the same ID/input preserves the snapshot; different content under the same ID is rejected.

JSON is historical question context, not live task status. If the mainline advances, retain the captured lesson and verify code changes. Never substitute today's mainline lesson for an older packet.

Without an active route, answer standalone questions directly. For an explicitly requested separate task, construct the same self-contained startup prompt from visible context and explicit repository/skill paths, without `prepare-qa`, runtime workstreams or course activation.

## Dispatch with the host's task tools

Discover available task tools and follow their current schemas; they are optional host capabilities, not Python dependencies.

1. Dispatch only when the user requests a new/separate task or continuation in an identified QA task. An ordinary “why?” does not authorize creation.
2. Reuse an accessible recorded destination via `send_message_to_thread` for related questions. Keep the exact packet ID in every message, including queued messages; the source must not overwrite a busy QA checkpoint. For an explicit new task or distinct topic, use a new `--workstream qa-<topic>` when preparing the packet. A failed read is not proof a task was deleted. Retain packets on failure; do not duplicate tasks after an uncertain dispatch.
3. Before `create_thread`, inspect `list_projects` for the matching project. Follow the host's environment rules, including its Git worktree default. The startup prompt includes the **absolute source repository**, **skill path**, **packet path** and **QA workstream**. Read source/state at those paths even if the new checkout lacks `.learning`; never initialize a detached copy. Use projectless when no saved project matches and those paths are accessible on the host. Do not choose another repository by title alone.
4. Record a confirmed `threadId`/`hostId` using `bind-thread --repo <source-repo> --workstream <qa-id> --thread <returned-id> --host <returned-host>`. Never bind an invented ID or queued `clientThreadId`; resolve queued creation via available status/list tools. Do not silently replace an existing binding.
5. Follow required task-created UI directives and observe a bounded status update when the host requires it. Keep detailed QA in its destination; report only handoff status in the mainline.

Do not default to `fork_thread`: its completed-turn boundary can omit the question currently being prepared, while copying unrelated history. If explicitly asked to fork, send the exact packet in a follow-up.

If task tools are unavailable, retain the packet and give one short startup message with its absolute path plus source/skill paths; clearly state that task opening is manual in this environment. Do not claim control of sidebar selection or automatic capture of unsubmitted text. A contextless chat cannot be guaranteed to invoke a skill; an agent-created task carries the invocation in its startup prompt.

## Answer and return

The destination reads the skill, exact packet and applicable repository instructions. Use `resume --repo <source-repo> --workstream <qa-id> --intent qa` for current preferences and QA checkpoint. The source lesson in the packet remains historical context, not permission to edit code or advance progress.

Explain directly, including missing prerequisites. Use `apply_patch` to save the question, answer, source references and remaining uncertainty to `<id>-answer.md`; link it in the response. Preserve prior answer content on follow-up. This per-question archive makes QA revisitable; stable notes separately collect reusable knowledge. If notes are disabled, do not claim that this coordination archive is a knowledge-note update.

Only the destination checkpoints its QA focus. Publish a short sourced answer/finding when useful to the mainline. On mainline continuation, sync pending contributions and mention only a relevant conclusion; never import the whole archive or mark mastery from an assistant answer.
