#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("learning_state.py")


class LearningStateScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        self.inputs = Path(self.temp.name) / "inputs"
        self.inputs.mkdir()
        self.project = self.inputs / "project.json"
        self.plan = self.inputs / "plan.json"
        self.project.write_text(json.dumps({
            "schema_version": 1,
            "name": "sample-go-api",
            "repository_path": str(self.repo),
            "stack": ["Go", "Gin"],
            "entrypoints": ["cmd/server/main.go"],
            "modules": ["http", "service", "repository"],
            "commands": {"test": {"command": "go test ./...", "verified": False}},
            "learning_value_summary": "Useful request-lifecycle example",
            "scan": {"git_head": None},
        }, ensure_ascii=False), encoding="utf-8")
        self.plan.write_text(json.dumps({
            "schema_version": 1,
            "plan_version": 1,
            "status": "proposed",
            "goals": ["Trace a complete request"],
            "stages": [
                {
                    "id": "request-flow",
                    "title": "Request lifecycle",
                    "learning_thread": "Trace route, middleware, handler, service, repository, and response.",
                    "core_questions": ["Where does the request enter?"],
                    "source_scope": ["cmd/server", "internal/http"],
                    "prerequisites": ["basic Go"],
                    "exercise": None,
                    "completion_criteria": ["Learner explains the call chain"],
                    "skippable": False,
                    "optional": False,
                },
                {
                    "id": "database",
                    "title": "Database boundary",
                    "learning_thread": "Trace persistence and transaction ownership.",
                    "core_questions": ["Who owns the transaction?"],
                    "source_scope": ["internal/repository"],
                    "prerequisites": ["SQL basics"],
                    "exercise": None,
                    "completion_criteria": ["Learner explains transaction ownership"],
                    "skippable": True,
                    "optional": False,
                },
            ],
            "skipped_topics": [],
            "optional_topics": [],
            "manual_adjustments": [],
            "change_log": [],
        }, ensure_ascii=False), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str, expected: int = 0) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args], capture_output=True,
            text=True, encoding="utf-8", errors="replace", check=False,
        )
        self.assertEqual(expected, result.returncode, msg=result.stdout + result.stderr)
        return json.loads(result.stdout)

    def propose(self) -> dict:
        return self.run_cli(
            "propose", "--repo", str(self.repo), "--project", str(self.project),
            "--plan", str(self.plan),
        )

    def activate(self) -> dict:
        return self.run_cli(
            "activate", "--repo", str(self.repo),
            "--confirmation", "Database later; request lifecycle first.",
        )

    def test_scenario_1_proposal_does_not_create_progress(self) -> None:
        output = self.propose()
        self.assertEqual("proposed", output["status"])
        self.assertFalse((self.repo / ".learning" / "progress.json").exists())
        plan = json.loads((self.repo / ".learning" / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual("proposed", plan["status"])

    def test_scenario_2_activation_requires_confirmation_and_initializes_one_current_task(self) -> None:
        self.propose()
        denied = self.run_cli("activate", "--repo", str(self.repo), "--confirmation", "", expected=2)
        self.assertIn("confirmation", denied["error"])
        output = self.activate()
        self.assertEqual("request-flow-task-01", output["current_task_id"])
        progress = json.loads((self.repo / ".learning" / "progress.json").read_text(encoding="utf-8"))
        self.assertEqual("learning", progress["tasks"]["request-flow-task-01"]["status"])
        self.assertEqual("not_started", progress["tasks"]["database-task-01"]["status"])

    def test_scenario_3_resume_reads_current_task_without_rescan(self) -> None:
        self.propose()
        self.activate()
        state = self.run_cli("show", "--repo", str(self.repo))
        self.assertEqual("request-flow-task-01", state["progress"]["current_task_id"])
        self.assertEqual("active", state["plan"]["status"])

    def test_scenario_4_question_updates_only_current_task(self) -> None:
        self.propose()
        self.activate()
        self.run_cli(
            "update-task", "--repo", str(self.repo), "--task", "request-flow-task-01",
            "--status", "questioning", "--question", "Why middleware instead of handler code?",
        )
        progress = json.loads((self.repo / ".learning" / "progress.json").read_text(encoding="utf-8"))
        self.assertEqual(1, len(progress["tasks"]["request-flow-task-01"]["open_questions"]))
        self.assertEqual("not_started", progress["tasks"]["database-task-01"]["status"])

    def test_scenario_5_session_close_is_compact_and_mastery_needs_evidence(self) -> None:
        self.propose()
        self.activate()
        denied = self.run_cli(
            "update-task", "--repo", str(self.repo), "--task", "request-flow-task-01",
            "--status", "mastered", expected=2,
        )
        self.assertIn("evidence", denied["error"])
        self.run_cli(
            "update-task", "--repo", str(self.repo), "--task", "request-flow-task-01",
            "--status", "mastered", "--evidence", "Learner explained route-to-response flow",
            "--next-step", "Trace database errors",
        )
        session = self.inputs / "session.json"
        session.write_text(json.dumps({
            "title": "Request lifecycle",
            "goal": "Trace one request",
            "completed": ["Traced request flow"],
            "core_files": ["internal/http/routes.go"],
            "key_insights": ["Middleware owns cross-cutting concerns"],
            "exercises": [],
            "open_questions": ["How are DB errors mapped?"],
            "next_step": "Trace database errors",
        }), encoding="utf-8")
        output = self.run_cli("record-session", "--repo", str(self.repo), "--session", str(session))
        log = Path(output["path"]).read_text(encoding="utf-8")
        self.assertIn("## Goal", log)
        self.assertNotIn("full chat", log.lower())
        doctor = self.run_cli("doctor", "--repo", str(self.repo))
        self.assertTrue(doctor["ok"])

    def test_custom_notes_missing_path_falls_back_without_claiming_success(self) -> None:
        self.propose()
        missing = Path(self.temp.name) / "missing-vault"
        output = self.run_cli(
            "set-notes", "--repo", str(self.repo), "--location", "custom",
            "--path", str(missing), "--fallback",
        )
        self.assertTrue(output["fallback_used"])
        self.assertIn("does not exist", output["reason"])

    def test_existing_config_is_preserved_when_saving_first_proposal(self) -> None:
        state = self.repo / ".learning"
        state.mkdir()
        config = {
            "schema_version": 1,
            "learning": {"mode": "mentor", "explanation_depth": "deep", "exercise_enabled": False, "review_enabled": True},
            "permissions": {"allow_test_skeletons": False, "allow_business_code_changes": False},
            "planning": {"require_confirmation": True, "auto_activate_plan": False},
            "notes": {"enabled": False, "location": "project", "project_path": ".learning/notes", "custom_path": None, "fallback_to_project": True, "namespace_by_project": False, "session_logs": False, "update_existing_notes": True, "git_tracking": "ask", "categories": {}},
            "progress": {"enabled": True, "mastery_requires_evidence": True},
            "project": {"focus": ["HTTP"], "excluded_topics": ["database"]},
        }
        (state / "config.json").write_text(json.dumps(config), encoding="utf-8")
        self.propose()
        saved = json.loads((state / "config.json").read_text(encoding="utf-8"))
        self.assertFalse(saved["learning"]["exercise_enabled"])
        self.assertEqual(["HTTP"], saved["project"]["focus"])

    def test_failed_custom_notes_configuration_does_not_mutate_config(self) -> None:
        self.propose()
        config_path = self.repo / ".learning" / "config.json"
        before = config_path.read_text(encoding="utf-8")
        missing = Path(self.temp.name) / "missing-no-fallback"
        self.run_cli(
            "set-notes", "--repo", str(self.repo), "--location", "custom",
            "--path", str(missing), "--no-fallback", expected=2,
        )
        self.assertEqual(before, config_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
