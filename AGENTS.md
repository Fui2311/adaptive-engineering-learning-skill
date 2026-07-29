# Repository guidance

This repository authors the `adaptive-engineering-learning` Codex Skill.

- Treat `skill-src/adaptive-engineering-learning/` as the editable source of truth.
- Keep `.agents/skills/adaptive-engineering-learning/` synchronized for repository-level Codex discovery.
- Preserve the confirmation invariant: a proposed plan must not have runtime tasks/workstreams; activation requires explicit user confirmation.
- Preserve multi-workstream ownership: Q&A cannot directly advance tasks, side windows write their own state, and plan changes remain confirmation-gated.
- Keep `SKILL.md` concise and place detailed workflows one level under `references/`.
- Use only standard-library Python in `scripts/learning_state.py` unless portability requirements change.
- Do not weaken learner-originated evidence requirements for `mastered` tasks.
- Validate changes with:
  - `python skill-src/adaptive-engineering-learning/scripts/test_learning_state.py`
  - `PYTHONUTF8=1 python <skill-creator>/scripts/quick_validate.py skill-src/adaptive-engineering-learning` (or the platform equivalent)
- Do not commit generated `.learning/` state from validation fixtures.
