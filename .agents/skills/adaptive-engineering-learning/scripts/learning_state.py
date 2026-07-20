#!/usr/bin/env python3
"""Deterministic state transitions for adaptive-engineering-learning.

Uses only the Python standard library. It intentionally does not analyze or teach a
repository; Codex performs those evidence-sensitive tasks and supplies validated JSON.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
PLAN_STATUSES = {"proposed", "active", "paused", "completed", "superseded"}
TASK_STATUSES = {
    "not_started", "learning", "questioning", "practicing", "reviewing",
    "blocked", "needs_review", "mastered", "paused", "skipped",
}
MODES = {"mentor", "exercise", "review", "debug", "pair", "implementation"}


class StateError(RuntimeError):
    pass


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def repo_path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise StateError(f"Repository directory does not exist: {path}")
    return path


def state_dir(repo: Path) -> Path:
    return repo / ".learning"


def read_json(path: Path, *, required: bool = True) -> dict[str, Any] | None:
    if not path.exists():
        if required:
            raise StateError(f"Missing state file: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError(f"Cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise StateError(f"Expected a JSON object in {path}")
    return value


def atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temp, path)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def load_input(path_text: str) -> dict[str, Any]:
    return read_json(Path(path_text).expanduser().resolve()) or {}


def default_config() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "learning": {
            "mode": "mentor",
            "explanation_depth": "normal",
            "exercise_enabled": True,
            "review_enabled": True,
        },
        "permissions": {
            "allow_test_skeletons": False,
            "allow_business_code_changes": False,
        },
        "planning": {
            "require_confirmation": True,
            "auto_activate_plan": False,
        },
        "notes": {
            "enabled": True,
            "location": "project",
            "project_path": ".learning/notes",
            "custom_path": None,
            "fallback_to_project": True,
            "namespace_by_project": False,
            "session_logs": True,
            "update_existing_notes": True,
            "git_tracking": "ask",
            "categories": {
                "concepts": True,
                "architecture": True,
                "debugging": True,
                "project": True,
            },
        },
        "progress": {"enabled": True, "mastery_requires_evidence": True},
        "project": {"focus": [], "excluded_topics": []},
    }


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if config.get("schema_version") != SCHEMA_VERSION:
        errors.append("config.schema_version must be 1")
    planning = config.get("planning", {})
    if planning.get("require_confirmation") is not True:
        errors.append("planning.require_confirmation must be true")
    if planning.get("auto_activate_plan") is not False:
        errors.append("planning.auto_activate_plan must be false")
    mode = config.get("learning", {}).get("mode")
    if mode not in MODES:
        errors.append(f"learning.mode must be one of {sorted(MODES)}")
    notes = config.get("notes", {})
    if notes.get("location") not in {"project", "custom"}:
        errors.append("notes.location must be project or custom")
    if notes.get("location") == "custom" and not notes.get("custom_path"):
        errors.append("notes.custom_path is required when location is custom")
    return errors


def validate_plan(plan: dict[str, Any], *, expected_status: str | None = None) -> list[str]:
    errors: list[str] = []
    if plan.get("schema_version") != SCHEMA_VERSION:
        errors.append("plan.schema_version must be 1")
    if not isinstance(plan.get("plan_version"), int) or plan.get("plan_version", 0) < 1:
        errors.append("plan.plan_version must be a positive integer")
    status = plan.get("status")
    if status not in PLAN_STATUSES:
        errors.append(f"plan.status must be one of {sorted(PLAN_STATUSES)}")
    if expected_status and status != expected_status:
        errors.append(f"plan.status must be {expected_status}")
    stages = plan.get("stages")
    if not isinstance(stages, list) or not stages:
        errors.append("plan.stages must be a non-empty list")
        return errors
    ids: set[str] = set()
    for index, stage in enumerate(stages, 1):
        if not isinstance(stage, dict):
            errors.append(f"stage {index} must be an object")
            continue
        stage_id = stage.get("id")
        if not isinstance(stage_id, str) or not stage_id.strip():
            errors.append(f"stage {index} requires a non-empty id")
        elif stage_id in ids:
            errors.append(f"duplicate stage id: {stage_id}")
        else:
            ids.add(stage_id)
        for field in ("title", "learning_thread"):
            if not isinstance(stage.get(field), str) or not stage[field].strip():
                errors.append(f"stage {stage_id or index} requires {field}")
        criteria = stage.get("completion_criteria")
        if not isinstance(criteria, list) or not criteria:
            errors.append(f"stage {stage_id or index} requires completion_criteria")
    return errors


def require_valid(errors: list[str]) -> None:
    if errors:
        raise StateError("; ".join(errors))


def git_value(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], cwd=repo, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=10, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def cmd_inspect(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    ignored = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv"}
    markdown: list[str] = []
    for path in repo.rglob("*.md"):
        if any(part in ignored for part in path.parts):
            continue
        markdown.append(path.relative_to(repo).as_posix())
        if len(markdown) >= 200:
            break
    state_files = {}
    for name in ("config.json", "project.json", "project-map.md", "plan.json", "progress.json", "notes-index.json"):
        state_files[name] = (state / name).exists()
    plan_status = None
    if state_files["plan.json"]:
        try:
            plan_status = read_json(state / "plan.json")["status"]
        except (StateError, KeyError):
            plan_status = "invalid"
    status = git_value(repo, "status", "--short")
    emit({
        "repo": str(repo),
        "git": {
            "branch": git_value(repo, "branch", "--show-current"),
            "head": git_value(repo, "rev-parse", "HEAD"),
            "has_uncommitted_changes": bool(status),
            "status": status.splitlines() if status else [],
        },
        "markers": {
            "agents_md": [p.relative_to(repo).as_posix() for p in repo.rglob("AGENTS.md") if not any(x in ignored for x in p.parts)],
            "repo_skills": (repo / ".agents" / "skills").exists(),
            "learning_state": state.exists(),
            "state_files": state_files,
            "plan_status": plan_status,
            "markdown_sample": sorted(markdown),
        },
    })


def cmd_propose(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    existing_plan = read_json(state / "plan.json", required=False)
    if existing_plan and existing_plan.get("status") != "proposed":
        raise StateError("Refusing to overwrite a non-proposed plan; archive or explicitly supersede it")
    if existing_plan and not args.replace_proposal:
        raise StateError("A proposal already exists; use revise-plan or --replace-proposal")
    if (state / "progress.json").exists():
        raise StateError("Stale progress.json exists; inspect and archive it before saving a proposal")
    if args.map and (state / "project-map.md").exists() and not args.replace_proposal:
        raise StateError("project-map.md already exists; use --replace-proposal only after checking it")

    existing_config = read_json(state / "config.json", required=False)
    config = load_input(args.config) if args.config else (existing_config or default_config())
    project = load_input(args.project)
    plan = load_input(args.plan)
    require_valid(validate_config(config))
    plan["schema_version"] = SCHEMA_VERSION
    plan["plan_version"] = int(plan.get("plan_version", 1))
    plan["status"] = "proposed"
    plan.setdefault("goals", [])
    plan.setdefault("skipped_topics", [])
    plan.setdefault("optional_topics", [])
    plan.setdefault("manual_adjustments", [])
    plan.setdefault("change_log", [])
    plan["proposed_at"] = now()
    require_valid(validate_plan(plan, expected_status="proposed"))
    project.setdefault("schema_version", SCHEMA_VERSION)
    project.setdefault("scan", {})
    project["scan"].setdefault("scanned_at", now())

    state.mkdir(parents=True, exist_ok=True)
    atomic_json(state / "config.json", config)
    atomic_json(state / "project.json", project)
    atomic_json(state / "plan.json", plan)
    if args.map:
        source = Path(args.map).expanduser().resolve()
        atomic_text(state / "project-map.md", source.read_text(encoding="utf-8"))
    emit({"status": "proposed", "plan_version": plan["plan_version"], "progress_created": False, "state_dir": str(state)})


def cmd_revise_plan(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    path = state_dir(repo) / "plan.json"
    current = read_json(path) or {}
    if current.get("status") != "proposed":
        raise StateError("Only a proposed plan can be revised without a separate re-confirmation workflow")
    revised = load_input(args.plan)
    revised["schema_version"] = SCHEMA_VERSION
    revised["plan_version"] = int(current.get("plan_version", 1)) + 1
    revised["status"] = "proposed"
    revised.setdefault("goals", current.get("goals", []))
    revised.setdefault("skipped_topics", [])
    revised.setdefault("optional_topics", [])
    revised["manual_adjustments"] = copy.deepcopy(current.get("manual_adjustments", []))
    revised["change_log"] = copy.deepcopy(current.get("change_log", []))
    entry = {"at": now(), "reason": args.reason, "from_version": current.get("plan_version"), "to_version": revised["plan_version"]}
    revised["manual_adjustments"].append(entry)
    revised["change_log"].append(entry)
    require_valid(validate_plan(revised, expected_status="proposed"))
    atomic_json(path, revised)
    emit({"status": "proposed", "plan_version": revised["plan_version"], "reason": args.reason})


def make_progress(plan: dict[str, Any]) -> dict[str, Any]:
    tasks: dict[str, Any] = {}
    ordered: list[str] = []
    for stage in plan["stages"]:
        task_id = f"{stage['id']}-task-01"
        ordered.append(task_id)
        tasks[task_id] = {
            "stage_id": stage["id"],
            "title": stage["title"],
            "objective": stage["learning_thread"],
            "source_scope": stage.get("source_scope", []),
            "prerequisites": stage.get("prerequisites", []),
            "completion_criteria": stage.get("completion_criteria", []),
            "status": "not_started",
            "evidence": [],
            "open_questions": [],
            "blockers": [],
            "next_step": None,
            "updated_at": now(),
        }
    first = ordered[0]
    tasks[first]["status"] = "learning"
    return {
        "schema_version": SCHEMA_VERSION,
        "plan_version": plan["plan_version"],
        "current_stage_id": tasks[first]["stage_id"],
        "current_task_id": first,
        "current_code_locations": [],
        "task_order": ordered,
        "tasks": tasks,
        "recently_completed": [],
        "review_queue": [],
        "open_questions": [],
        "next_step": f"Begin {tasks[first]['title']}",
        "updated_at": now(),
    }


def cmd_activate(args: argparse.Namespace) -> None:
    if not args.confirmation.strip():
        raise StateError("Activation requires a non-empty explicit confirmation record")
    repo = repo_path(args.repo)
    state = state_dir(repo)
    config = read_json(state / "config.json") or {}
    plan = read_json(state / "plan.json") or {}
    require_valid(validate_config(config))
    require_valid(validate_plan(plan, expected_status="proposed"))
    if (state / "progress.json").exists():
        raise StateError("progress.json already exists; refusing to replace runtime state")
    activated = copy.deepcopy(plan)
    activated["status"] = "active"
    activated["confirmed_at"] = now()
    activated["confirmation_summary"] = args.confirmation.strip()
    activated.setdefault("change_log", []).append({"at": now(), "event": "activated", "confirmation": args.confirmation.strip()})
    progress = make_progress(activated)
    atomic_json(state / "plan.json", activated)
    try:
        atomic_json(state / "progress.json", progress)
    except OSError:
        atomic_json(state / "plan.json", plan)
        raise
    emit({
        "status": "active",
        "plan_version": activated["plan_version"],
        "current_stage_id": progress["current_stage_id"],
        "current_task_id": progress["current_task_id"],
    })


def cmd_show(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    result: dict[str, Any] = {"repo": str(repo), "initialized": state.exists()}
    for name in ("config", "project", "plan", "progress", "notes-index"):
        result[name] = read_json(state / f"{name}.json", required=False)
    emit(result)


def cmd_doctor(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    errors: list[str] = []
    warnings: list[str] = []
    if not state.exists():
        emit({"ok": True, "initialized": False, "errors": [], "warnings": ["No .learning directory"]})
        return
    try:
        read_json(state / "project.json")
    except StateError as exc:
        errors.append(str(exc))
    try:
        config = read_json(state / "config.json") or {}
        errors.extend(validate_config(config))
    except StateError as exc:
        errors.append(str(exc))
        config = {}
    try:
        plan = read_json(state / "plan.json") or {}
        errors.extend(validate_plan(plan))
    except StateError as exc:
        errors.append(str(exc))
        plan = {}
    progress_path = state / "progress.json"
    progress = None
    if progress_path.exists():
        try:
            progress = read_json(progress_path)
        except StateError as exc:
            errors.append(str(exc))
    if plan.get("status") == "proposed" and progress is not None:
        errors.append("A proposed plan must not have progress.json")
    if plan.get("status") in {"active", "paused", "completed"} and progress is None:
        errors.append(f"A {plan.get('status')} plan requires progress.json")
    if progress and progress.get("plan_version") != plan.get("plan_version"):
        errors.append("progress.plan_version does not match plan.plan_version")
    if progress:
        tasks = progress.get("tasks")
        if not isinstance(tasks, dict):
            errors.append("progress.tasks must be an object")
        else:
            for task_id, task in tasks.items():
                status = task.get("status")
                if status not in TASK_STATUSES:
                    errors.append(f"Invalid task status for {task_id}: {status}")
                if status == "mastered" and config.get("progress", {}).get("mastery_requires_evidence", True) and not task.get("evidence"):
                    errors.append(f"Mastered task lacks evidence: {task_id}")
            if progress.get("current_task_id") not in tasks:
                errors.append("progress.current_task_id does not identify an existing task")
    emit({"ok": not errors, "initialized": True, "errors": errors, "warnings": warnings})
    if errors:
        raise SystemExit(2)


def cmd_update_task(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    config = read_json(state / "config.json") or {}
    plan = read_json(state / "plan.json") or {}
    progress = read_json(state / "progress.json") or {}
    if plan.get("status") != "active":
        raise StateError("Task updates require an active plan")
    if progress.get("plan_version") != plan.get("plan_version"):
        raise StateError("Plan/progress version mismatch; run doctor")
    task = progress.get("tasks", {}).get(args.task)
    if not task:
        raise StateError(f"Unknown task: {args.task}")
    evidence = list(task.get("evidence", []))
    if args.evidence:
        evidence.append({"at": now(), "kind": args.evidence_kind, "detail": args.evidence})
    if args.status == "mastered" and config.get("progress", {}).get("mastery_requires_evidence", True) and not evidence:
        raise StateError("Cannot mark mastered without learner evidence")
    task["status"] = args.status
    task["evidence"] = evidence
    if args.question:
        task.setdefault("open_questions", []).append({"at": now(), "question": args.question})
    if args.blocker:
        task.setdefault("blockers", []).append({"at": now(), "detail": args.blocker})
    if args.next_step is not None:
        task["next_step"] = args.next_step
        progress["next_step"] = args.next_step
    if args.code:
        progress["current_code_locations"] = args.code
    progress["current_task_id"] = args.task
    progress["current_stage_id"] = task["stage_id"]
    stamp = now()
    task["updated_at"] = stamp
    progress["updated_at"] = stamp
    if args.status == "mastered" and args.task not in progress.setdefault("recently_completed", []):
        progress["recently_completed"].append(args.task)
    elif args.status != "mastered" and args.task in progress.setdefault("recently_completed", []):
        progress["recently_completed"].remove(args.task)
    atomic_json(state / "progress.json", progress)
    emit({"task": args.task, "status": args.status, "evidence_count": len(evidence), "next_step": task.get("next_step")})


def cmd_set_plan_status(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    plan = read_json(state / "plan.json") or {}
    progress = read_json(state / "progress.json") or {}
    old = plan.get("status")
    allowed = {("active", "paused"), ("paused", "active"), ("active", "completed")}
    if (old, args.status) not in allowed:
        raise StateError(f"Unsupported transition: {old} -> {args.status}")
    if args.status == "completed":
        incomplete = [task_id for task_id, task in progress.get("tasks", {}).items() if task.get("status") not in {"mastered", "skipped"}]
        if incomplete:
            raise StateError(f"Cannot complete plan with unfinished tasks: {', '.join(incomplete)}")
    plan["status"] = args.status
    plan.setdefault("change_log", []).append({"at": now(), "event": f"status:{old}->{args.status}", "reason": args.reason})
    progress["updated_at"] = now()
    atomic_json(state / "plan.json", plan)
    atomic_json(state / "progress.json", progress)
    emit({"from": old, "to": args.status, "reason": args.reason})


def cmd_set_mode(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    path = state_dir(repo) / "config.json"
    config = read_json(path) or {}
    config.setdefault("learning", {})["mode"] = args.mode
    require_valid(validate_config(config))
    atomic_json(path, config)
    emit({"mode": args.mode})


def resolve_notes(repo: Path, config: dict[str, Any], *, ensure_project: bool = False) -> dict[str, Any]:
    notes = config.get("notes", {})
    project_raw = notes.get("project_path") or ".learning/notes"
    project = Path(project_raw).expanduser()
    if not project.is_absolute():
        project = repo / project
    project = project.resolve()
    if ensure_project:
        project.mkdir(parents=True, exist_ok=True)
    if notes.get("location") != "custom":
        return {"requested": "project", "effective_path": str(project), "fallback_used": False, "writable": os.access(project if project.exists() else project.parent, os.W_OK)}
    custom_raw = notes.get("custom_path")
    custom = Path(custom_raw).expanduser() if custom_raw else None
    if custom and not custom.is_absolute():
        custom = repo / custom
    if custom:
        custom = custom.resolve()
        if notes.get("namespace_by_project"):
            custom = custom / repo.name
    reason = None
    if not custom or not custom.exists():
        reason = "custom path does not exist"
    elif not custom.is_dir():
        reason = "custom path is not a directory"
    elif not os.access(custom, os.W_OK):
        reason = "custom path is not writable by this process"
    if reason:
        if notes.get("fallback_to_project", True):
            if ensure_project:
                project.mkdir(parents=True, exist_ok=True)
            return {"requested": str(custom) if custom else None, "effective_path": str(project), "fallback_used": True, "reason": reason, "writable": os.access(project if project.exists() else project.parent, os.W_OK)}
        raise StateError(reason)
    return {"requested": str(custom), "effective_path": str(custom), "fallback_used": False, "writable": True}


def cmd_resolve_notes(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    config = read_json(state_dir(repo) / "config.json") or {}
    emit(resolve_notes(repo, config, ensure_project=args.ensure_project))


def cmd_set_notes(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    path = state_dir(repo) / "config.json"
    config = read_json(path) or {}
    candidate = copy.deepcopy(config)
    notes = candidate.setdefault("notes", {})
    notes["location"] = args.location
    notes["custom_path"] = args.path if args.location == "custom" else None
    notes["fallback_to_project"] = args.fallback
    notes["namespace_by_project"] = args.namespace
    require_valid(validate_config(candidate))
    result = resolve_notes(repo, candidate)
    atomic_json(path, candidate)
    result["config_updated"] = True
    emit(result)


def cmd_index_note(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    config = read_json(state / "config.json") or {}
    resolved = resolve_notes(repo, config)
    root = Path(resolved["effective_path"]).resolve()
    note = Path(args.path).expanduser()
    if not note.is_absolute():
        note = root / note
    note = note.resolve()
    if root != note and root not in note.parents:
        raise StateError("Note path must be inside the effective notes root")
    if not note.exists():
        raise StateError(f"Note file does not exist: {note}")
    index_path = state / "notes-index.json"
    index = read_json(index_path, required=False) or {"schema_version": SCHEMA_VERSION, "notes": [], "conflicts": [], "pending_verification": []}
    relative = note.relative_to(root).as_posix()
    entry = {"path": relative, "kind": args.kind, "verification": args.verification, "sources": args.source or [], "updated_at": now()}
    notes = [item for item in index.get("notes", []) if item.get("path") != relative]
    notes.append(entry)
    index["notes"] = sorted(notes, key=lambda item: item["path"])
    index["effective_root"] = str(root)
    index["updated_at"] = now()
    atomic_json(index_path, index)
    emit(entry)


def cmd_record_session(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    state = state_dir(repo)
    config = read_json(state / "config.json") or {}
    plan = read_json(state / "plan.json") or {}
    progress = read_json(state / "progress.json") or {}
    if plan.get("status") not in {"active", "paused"}:
        raise StateError("Session logs require an active or paused plan")
    notes_config = config.get("notes", {})
    if not notes_config.get("enabled", True) or not notes_config.get("session_logs", True):
        emit({"written": False, "reason": "notes or session_logs disabled"})
        return
    data = load_input(args.session)
    stamp = dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    title = data.get("title") or "Learning session"
    def bullets(key: str) -> str:
        values = data.get(key) or []
        return "\n".join(f"- {value}" for value in values) if values else "- None"
    content = (
        f"# {title}\n\n"
        f"## Goal\n\n{data.get('goal', 'Not recorded')}\n\n"
        f"## Completed\n\n{bullets('completed')}\n\n"
        f"## Core files\n\n{bullets('core_files')}\n\n"
        f"## Key insights\n\n{bullets('key_insights')}\n\n"
        f"## Exercises\n\n{bullets('exercises')}\n\n"
        f"## Open questions\n\n{bullets('open_questions')}\n\n"
        f"## Next step\n\n{data.get('next_step', 'Not decided')}\n"
    )
    target = state / "sessions" / f"{stamp}.md"
    atomic_text(target, content)
    progress["open_questions"] = data.get("open_questions", progress.get("open_questions", []))
    progress["next_step"] = data.get("next_step", progress.get("next_step"))
    progress["updated_at"] = now()
    atomic_json(state / "progress.json", progress)
    emit({"written": True, "path": str(target), "next_step": progress.get("next_step")})


def cmd_archive(args: argparse.Namespace) -> None:
    repo = repo_path(args.repo)
    source = state_dir(repo)
    if not source.is_dir():
        raise StateError("No .learning directory to archive")
    if args.destination:
        destination = Path(args.destination).expanduser().resolve()
    else:
        destination = (repo / ".learning-archives" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")).resolve()
    if destination == source or source in destination.parents:
        raise StateError("Archive destination must not be inside .learning")
    if destination.exists():
        raise StateError(f"Archive destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    emit({"archived": True, "source_preserved": True, "destination": str(destination)})


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    def add_repo(name: str, help_text: str) -> argparse.ArgumentParser:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--repo", required=True)
        return command

    add_repo("inspect", "Read-only repository and learning-state inspection").set_defaults(func=cmd_inspect)

    propose = add_repo("propose", "Persist a candidate plan without creating progress")
    propose.add_argument("--project", required=True)
    propose.add_argument("--plan", required=True)
    propose.add_argument("--map")
    propose.add_argument("--config")
    propose.add_argument("--replace-proposal", action="store_true")
    propose.set_defaults(func=cmd_propose)

    revise = add_repo("revise-plan", "Revise an existing proposed plan")
    revise.add_argument("--plan", required=True)
    revise.add_argument("--reason", required=True)
    revise.set_defaults(func=cmd_revise_plan)

    activate = add_repo("activate", "Activate an explicitly confirmed proposal")
    activate.add_argument("--confirmation", required=True)
    activate.set_defaults(func=cmd_activate)

    add_repo("show", "Show persisted learning state").set_defaults(func=cmd_show)
    add_repo("doctor", "Validate state invariants and JSON integrity").set_defaults(func=cmd_doctor)

    update = add_repo("update-task", "Update one active task")
    update.add_argument("--task", required=True)
    update.add_argument("--status", required=True, choices=sorted(TASK_STATUSES))
    update.add_argument("--evidence")
    update.add_argument("--evidence-kind", default="learner_explanation")
    update.add_argument("--question")
    update.add_argument("--blocker")
    update.add_argument("--next-step")
    update.add_argument("--code", action="append")
    update.set_defaults(func=cmd_update_task)

    plan_status = add_repo("set-plan-status", "Pause, resume, or complete an active route")
    plan_status.add_argument("--status", required=True, choices=["active", "paused", "completed"])
    plan_status.add_argument("--reason", required=True)
    plan_status.set_defaults(func=cmd_set_plan_status)

    mode = add_repo("set-mode", "Switch learning interaction mode")
    mode.add_argument("--mode", required=True, choices=sorted(MODES))
    mode.set_defaults(func=cmd_set_mode)

    notes = add_repo("resolve-notes", "Resolve and validate the effective notes path")
    notes.add_argument("--ensure-project", action="store_true")
    notes.set_defaults(func=cmd_resolve_notes)

    set_notes = add_repo("set-notes", "Configure project or custom notes path")
    set_notes.add_argument("--location", required=True, choices=["project", "custom"])
    set_notes.add_argument("--path")
    set_notes.add_argument("--fallback", action=argparse.BooleanOptionalAction, default=True)
    set_notes.add_argument("--namespace", action=argparse.BooleanOptionalAction, default=False)
    set_notes.set_defaults(func=cmd_set_notes)

    index = add_repo("index-note", "Register an existing note in notes-index.json")
    index.add_argument("--path", required=True)
    index.add_argument("--kind", required=True, choices=["concept", "architecture", "debugging", "project", "question"])
    index.add_argument("--verification", default="verified", choices=["verified", "pending"])
    index.add_argument("--source", action="append")
    index.set_defaults(func=cmd_index_note)

    session = add_repo("record-session", "Write one compact session log from JSON")
    session.add_argument("--session", required=True)
    session.set_defaults(func=cmd_record_session)

    archive = add_repo("archive", "Copy learning state to a recoverable archive without deleting source")
    archive.add_argument("--destination")
    archive.set_defaults(func=cmd_archive)
    return root


def main() -> int:
    try:
        args = parser().parse_args()
        args.func(args)
        return 0
    except StateError as exc:
        emit({"ok": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
