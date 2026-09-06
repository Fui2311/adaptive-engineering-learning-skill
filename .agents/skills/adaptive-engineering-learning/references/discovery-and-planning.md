# Discovery and planning

## Contents

- Existing-state check
- Repository scan
- Project learning map
- Candidate plan
- Confirmation and re-scan

## Existing-state check

This workflow applies only to a requested learning route or a material re-scan. A question, skill invocation or new Codex task is not discovery. Use `resume` first if state is not already known. For a genuinely new course, run `inspect`, then check applicable instructions, existing learning files, relevant notes, branch/HEAD and uncommitted changes. Read existing state rather than initializing again.

If a plan is active, do not replace it during a re-scan. Read the current compact context and only affected state/source files. Propose route changes only if the findings warrant them. If the user asks a question, answer in place or use the requested separate Q&A handoff without re-scanning or creating a course.

## Repository scan

Keep this phase read-only except for an optional proposed-plan snapshot. Inspect, in a risk-adjusted order:

1. README and authoritative documentation.
2. Top-level tree, manifests, lockfiles, generated-code markers, and independent subprojects.
3. Entrypoints, routes/commands/events, and one representative end-to-end flow.
4. Module boundaries, data models, external systems, configuration, logging, and error handling.
5. Tests, build/run/deploy commands, CI, migrations, containers, and observability.
6. Git branch/HEAD and working-tree changes that affect conclusions.

Use searches and focused reads before opening many files. Run existing tests or builds only when low-risk and relevant; label results as executed, failed, or not run. Do not infer active use from a dependency manifest alone.

For a large monorepo, first map subprojects and propose a scan boundary. For missing docs, infer cautiously from code and label uncertainty. For low-quality or obsolete projects, state the learning ceiling and identify anti-patterns.

## Project learning map

Report:

### Project overview

- problem solved and maturity
- actual primary stack
- entrypoints and major modules
- one representative call/data flow with paths
- known build/run/test commands and their verification status

### Learning directions

Include only categories present in meaningful code: language, framework, Web/API, database, project structure, errors, observability, tests, concurrency/async, config/deploy, architecture, AI engineering, debugging, and project-specific topics.

For each retained direction give:

- repository evidence and paths
- learning outcome and value
- recommended depth: deep / working knowledge / awareness / skip
- prerequisites and current suitability
- exemplar judgment: positive / mixed / negative / unverified

Classify value explicitly as focus, understand, awareness, skip-now, or do-not-copy.

## Candidate plan

Create 3–7 coherent stages unless repository scope strongly requires otherwise. Each stage follows one understanding thread rather than a generic layer name. Include:

- learning objective and core questions
- expected source scope
- prerequisites
- one optional repository-grounded exercise
- completion criteria based on observable learner behavior
- skip and extension options

Do not generate dozens of microtasks or pre-create side workstreams. Keep exercises optional when disabled. Save a proposal only when persistence is useful:

```text
python <skill-dir>/scripts/learning_state.py propose --repo <repo> --project <project.json> --plan <plan.json> [--map <project-map.md>] [--config <config.json>]
```

The input plan must use the schema in `state-model.md`. `propose` refuses to overwrite an active plan and never creates workspace, task, or workstream runtime state.

End with a concise confirmation request that makes these adjustments easy: accept, remove/reorder stages, change depth, select one direction, disable exercises, focus on framework rather than business, or re-scan a module.

## Confirmation and re-scan

When the user confirms with changes:

1. Edit a copy of the proposal to reflect their exact changes.
2. Run `revise-plan` with a reason while it is still proposed.
3. Run `activate` with the user's confirmation summary.
4. Read the generated `mainline` context and name only the first current task; do not teach the whole stage immediately.

On a later re-scan, compare the previous `project.json.scan.git_head` and relevant repository facts. Report new learning content, invalidated assumptions, affected stages/tasks/workstreams, and suggested revisions. Publish or record a plan-change request when useful, but never auto-apply or auto-activate a revised route.
