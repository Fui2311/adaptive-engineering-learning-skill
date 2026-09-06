---
name: adaptive-engineering-learning
description: Learn from a real code repository with a resumable route, direct explanations, exercises, and automatic notes. Use for project learning, continuing lessons, learning Q&A, or moving a question with its context into a separate task. Reuse existing .learning state; invoking this skill does not mean initialization. Ordinary feature delivery is outside scope unless explicitly requested as learning or pair work.
---

# Adaptive Engineering Learning

Teach from real code; keep the mainline easy to follow and questions easy to revisit. The learner speaks naturally and never needs to manage workstream IDs or state commands.

## Recognize intent first

Use the current request and conversation context, not the mere presence of this skill:

| Intent | Action |
| --- | --- |
| Learn a new project / plan a course | Inspect the repository, propose a tailored route, activate only after explicit confirmation. Read [discovery-and-planning](references/discovery-and-planning.md). |
| Continue learning | Resume the conversation's saved role and exact code location. In an identified mainline, continue teaching without another mode-selection gate. |
| Why / explain / I do not understand | Answer directly, fill missing prerequisites, preserve the mainline position. A short question needs neither a new task nor a course. |
| Open a separate Q&A task / move this question out | Carry the question and relevant explanation automatically. Read [question-handoff](references/question-handoff.md); create or reuse the requested Q&A task. |
| Exercise / review my attempt | Use a bounded exercise or review; graded hints apply to exercises. Read [learning-workflows](references/learning-workflows.md). |
| Stop / progress / save | Save material changes and one next step; report compactly. |

Explicit user intent wins over a saved mode. In an identified Q&A conversation, “continue” continues that question. Only ask when the source, question, or intended continuation cannot be identified. Never invent missing context or create a Codex task merely because the user asked a question.

## Load only what is needed

Resolve the actual source repository and applicable `AGENTS.md`. An incoming handoff's explicit source path takes precedence over a new task's incidental working directory. At entry or after context loss, use:

```text
python <skill-dir>/scripts/learning_state.py resume --repo <repo> [--workstream <known-id>] [--thread <known-thread-id>] [--intent qa]
```

`resume` reads state without initializing or scanning. Follow its action: `discover`, `confirm_plan`, `resume`, `answer`, `status`, `select_qa_context`, or `migration_required`. QA can answer before course activation. Prefer an exact incoming question packet or known thread binding; never guess the latest question from another window. Do not repeat entry checks on every message. Load relevant source files and, only if needed, pending shared updates with `sync`.

## Explain first

Default to clear, direct teaching: the problem, a real call/data flow, and why the implementation makes those choices. Explain prerequisites instead of making the learner guess unfamiliar material. Cite paths and distinguish observed facts, inference, and unknowns; label flawed or obsolete code.

Do not force a quiz after every explanation. In exercises, give scope, acceptance criteria and incremental hints, one question at a time. For review/debug/pair work, use [learning-workflows](references/learning-workflows.md). Explicitly authorized implementation is allowed within scope; Codex-authored work is never learner mastery evidence.

## Save without ceremony

- At a meaningful teaching boundary, checkpoint the current workstream's focus, exact resume point, code locations and next step. Include `--explanation` with the relevant passage to preserve referents such as “刚才这段”. This is context, not mastery evidence. Unchanged checkpoints need no write.
- For separate Q&A, freeze a question packet before dispatch. Keep the detailed answer there; bring back only useful verified conclusions.
- Automatically update useful, verified notes in the configured location, deduplicating by topic. Concise syntax explanations are eligible when useful for review. Read [notes-and-operations](references/notes-and-operations.md) when writing notes or closing a session. Mention actual updates briefly.
- Save before ending a meaningful learning turn or switching tasks; do not wait for “save”. On “today stop”, keep one next step and a compact session log if enabled. No transcript dumps or obligatory status footers.

Use `learning_state.py` for state mutations and `apply_patch` for note/answer prose. The usual path is one `resume` at entry, teaching or answering, then one changed `checkpoint`; extra commands serve actual handoff, evidence or note changes.

## Keep these guarantees

- A proposed route is not active. Confirmation is needed to activate or change a route, not for ordinary explanations, saves or an already-authorized action.
- Mark `mastered` only from learner-originated explanation, prediction, implementation or other demonstrated evidence. Reading or ending a session is insufficient.
- Q&A preserves mainline progress; windows own separate checkpoints. Keep task evidence in tasks, shared findings in shared state, and knowledge in notes.
- Retain schema v2 state and existing preferences. Do not reinitialize on skill invocation or mode change. For v1, corruption, locks or recovery, read [state-model](references/state-model.md) and run `doctor` as appropriate; migration needs approval and an archive.

For advanced coordination use [multi-workstream-coordination](references/multi-workstream-coordination.md); for commands and user examples use [usage](references/usage.md). These are reference material, not a checklist for every answer.
