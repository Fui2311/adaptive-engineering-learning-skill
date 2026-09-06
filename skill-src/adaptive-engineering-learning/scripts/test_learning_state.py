#!/usr/bin/env python3
from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("learning_state.py")
SPEC = importlib.util.spec_from_file_location("learning_state_under_test", SCRIPT)
assert SPEC and SPEC.loader
STATE_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATE_MODULE)


class LearningStateScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.project = self.inputs / "project.json"
        self.plan = self.inputs / "plan.json"
        self.project.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "name": "sample-go-api",
                    "repository_path": str(self.repo),
                    "stack": ["Go", "Gin"],
                    "entrypoints": ["cmd/server/main.go"],
                    "modules": ["http", "service", "repository"],
                    "commands": {
                        "test": {"command": "go test ./...", "verified": False}
                    },
                    "learning_value_summary": "Useful request-lifecycle example",
                    "scan": {"git_head": None},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.plan.write_text(
            json.dumps(
                {
                    "schema_version": 2,
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
                            "completion_criteria": [
                                "Learner explains the call chain"
                            ],
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
                            "completion_criteria": [
                                "Learner explains transaction ownership"
                            ],
                            "skippable": True,
                            "optional": False,
                        },
                    ],
                    "skipped_topics": [],
                    "optional_topics": [],
                    "manual_adjustments": [],
                    "change_log": [],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str, expected: int = 0) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(
            expected, result.returncode, msg=result.stdout + result.stderr
        )
        return json.loads(result.stdout)

    def propose(self) -> dict:
        return self.run_cli(
            "propose",
            "--repo",
            str(self.repo),
            "--project",
            str(self.project),
            "--plan",
            str(self.plan),
        )

    def activate(self) -> dict:
        return self.run_cli(
            "activate",
            "--repo",
            str(self.repo),
            "--confirmation",
            "Database later; request lifecycle first.",
        )

    def initialize(self) -> None:
        self.propose()
        self.activate()

    def open_qa(self) -> dict:
        return self.run_cli(
            "open-workstream",
            "--repo",
            str(self.repo),
            "--id",
            "qa-http",
            "--kind",
            "qa",
            "--title",
            "HTTP Q&A",
            "--task",
            "request-flow-chapter",
            "--focus",
            "Resolve middleware questions without moving mainline progress",
        )

    def test_proposal_does_not_create_runtime_state(self) -> None:
        output = self.propose()
        self.assertEqual("proposed", output["status"])
        state = self.repo / ".learning"
        self.assertFalse((state / "workspace.json").exists())
        self.assertFalse((state / "progress.json").exists())
        plan = json.loads((state / "plan.json").read_text(encoding="utf-8"))
        self.assertEqual(2, plan["schema_version"])

    def test_activation_requires_confirmation_and_creates_mainline(self) -> None:
        self.propose()
        denied = self.run_cli(
            "activate",
            "--repo",
            str(self.repo),
            "--confirmation",
            "",
            expected=2,
        )
        self.assertIn("confirmation", denied["error"])
        output = self.activate()
        self.assertEqual("mainline", output["mainline_workstream_id"])
        self.assertEqual("request-flow-chapter", output["current_task_id"])
        state = self.repo / ".learning"
        self.assertTrue((state / "dashboard.md").exists())
        self.assertTrue((state / "handoffs" / "mainline.md").exists())
        first = json.loads(
            (state / "tasks" / "request-flow-chapter.json").read_text(
                encoding="utf-8"
            )
        )
        second = json.loads(
            (state / "tasks" / "database-chapter.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("learning", first["status"])
        self.assertEqual("not_started", second["status"])

    def test_multiple_workstreams_keep_resume_state_isolated(self) -> None:
        self.initialize()
        self.open_qa()
        self.run_cli(
            "checkpoint",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--resume-at",
            "Explain middleware ordering",
            "--next-step",
            "Compare two middleware implementations",
            "--code",
            "internal/http/middleware.go:20",
        )
        mainline = json.loads(
            (
                self.repo
                / ".learning"
                / "workstreams"
                / "mainline.json"
            ).read_text(encoding="utf-8")
        )
        qa = json.loads(
            (
                self.repo / ".learning" / "workstreams" / "qa-http.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIsNone(mainline["resume_at"])
        self.assertEqual("Explain middleware ordering", qa["resume_at"])
        dashboard = (self.repo / ".learning" / "dashboard.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("qa-http", dashboard)

    def test_qa_workstream_cannot_directly_move_task_status(self) -> None:
        self.initialize()
        self.open_qa()
        denied = self.run_cli(
            "update-task",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--task",
            "request-flow-chapter",
            "--status",
            "mastered",
            "--evidence",
            "Question was answered",
            "--learner-originated",
            expected=2,
        )
        self.assertIn("do not directly change task state", denied["error"])

    def test_cross_workstream_publish_and_sync_share_knowledge_and_questions(self) -> None:
        self.initialize()
        self.open_qa()
        self.run_cli(
            "publish",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--kind",
            "answer",
            "--task",
            "request-flow-chapter",
            "--summary",
            "Middleware runs in registration order.",
            "--verification",
            "verified",
            "--source",
            "internal/http/routes.go:18",
        )
        self.run_cli(
            "publish",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--kind",
            "question",
            "--task",
            "request-flow-chapter",
            "--summary",
            "Where are database errors mapped?",
        )
        output = self.run_cli(
            "sync",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
        )
        self.assertEqual(2, output["processed_count"])
        shared = json.loads(
            (self.repo / ".learning" / "shared.json").read_text(encoding="utf-8")
        )
        self.assertEqual(1, len(shared["knowledge"]))
        self.assertEqual(1, len(shared["questions"]))
        task = json.loads(
            (
                self.repo
                / ".learning"
                / "tasks"
                / "request-flow-chapter.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(1, len(task["open_questions"]))

    def test_answer_sync_keeps_unrelated_task_revision_stable(self) -> None:
        self.initialize()
        self.open_qa()
        task_path = (
            self.repo / ".learning" / "tasks" / "request-flow-chapter.json"
        )
        before = json.loads(task_path.read_text(encoding="utf-8"))["revision"]
        self.run_cli(
            "publish",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--kind",
            "answer",
            "--task",
            "request-flow-chapter",
            "--summary",
            "Authentication stays transport-agnostic.",
            "--verification",
            "verified",
            "--source",
            "src/auth.py:1",
        )
        self.run_cli(
            "sync",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
        )
        after = json.loads(task_path.read_text(encoding="utf-8"))["revision"]
        self.assertEqual(before, after)

    def test_plan_change_is_queued_and_never_auto_applied(self) -> None:
        self.initialize()
        self.open_qa()
        self.run_cli(
            "publish",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--kind",
            "plan_change",
            "--summary",
            "Move database before HTTP.",
        )
        output = self.run_cli(
            "sync",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
        )
        self.assertFalse(output["plan_changes_auto_applied"])
        plan = json.loads(
            (self.repo / ".learning" / "plan.json").read_text(encoding="utf-8")
        )
        self.assertEqual("request-flow", plan["stages"][0]["id"])
        contribution = next((self.repo / ".learning" / "inbox").glob("*.json"))
        value = json.loads(contribution.read_text(encoding="utf-8"))
        self.assertEqual("queued", value["status"])

    def test_learner_evidence_can_cross_workstreams_but_does_not_auto_master(self) -> None:
        self.initialize()
        self.open_qa()
        self.run_cli(
            "publish",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--kind",
            "evidence",
            "--task",
            "request-flow-chapter",
            "--summary",
            "Learner independently predicted middleware order.",
            "--learner-originated",
        )
        self.run_cli(
            "sync",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
        )
        task_path = (
            self.repo / ".learning" / "tasks" / "request-flow-chapter.json"
        )
        task = json.loads(task_path.read_text(encoding="utf-8"))
        self.assertEqual("learning", task["status"])
        self.assertEqual(1, len(task["evidence"]))
        output = self.run_cli(
            "update-task",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
            "--task",
            "request-flow-chapter",
            "--status",
            "mastered",
        )
        self.assertEqual("mastered", output["status"])

    def test_mastery_rejects_codex_only_evidence(self) -> None:
        self.initialize()
        denied = self.run_cli(
            "update-task",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
            "--task",
            "request-flow-chapter",
            "--status",
            "mastered",
            "--evidence",
            "Codex implemented the change",
            expected=2,
        )
        self.assertIn("learner-originated", denied["error"])

    def test_create_feature_task_and_implementation_workstream_require_confirmation(
        self,
    ) -> None:
        self.initialize()
        denied_task = self.run_cli(
            "create-task",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
            "--id",
            "feature-auth",
            "--stage",
            "request-flow",
            "--kind",
            "implementation",
            "--title",
            "Implement auth middleware",
            "--objective",
            "Implement and explain one bounded feature",
            expected=2,
        )
        self.assertIn("confirmation", denied_task["error"])
        created = self.run_cli(
            "create-task",
            "--repo",
            str(self.repo),
            "--workstream",
            "mainline",
            "--id",
            "feature-auth",
            "--stage",
            "request-flow",
            "--kind",
            "implementation",
            "--title",
            "Implement auth middleware",
            "--objective",
            "Implement and explain one bounded feature",
            "--criterion",
            "Tests pass and learner explains the flow",
            "--confirmation",
            "User explicitly requested implementation mode for auth middleware.",
        )
        self.assertTrue(created["created"])
        denied_stream = self.run_cli(
            "open-workstream",
            "--repo",
            str(self.repo),
            "--id",
            "impl-auth",
            "--kind",
            "implementation",
            "--title",
            "Auth implementation",
            "--task",
            "feature-auth",
            expected=2,
        )
        self.assertIn("confirmation", denied_stream["error"])
        opened = self.run_cli(
            "open-workstream",
            "--repo",
            str(self.repo),
            "--id",
            "impl-auth",
            "--kind",
            "implementation",
            "--title",
            "Auth implementation",
            "--task",
            "feature-auth",
            "--confirmation",
            "User explicitly opened an implementation window.",
        )
        self.assertEqual("feature-auth", opened["attached_task_id"])
        denied_pair = self.run_cli(
            "open-workstream",
            "--repo",
            str(self.repo),
            "--id",
            "pair-auth",
            "--kind",
            "pair",
            "--title",
            "Auth pairing",
            "--task",
            "feature-auth",
            expected=2,
        )
        self.assertIn("explicit user confirmation", denied_pair["error"])
        denied_mode = self.run_cli(
            "set-mode",
            "--repo",
            str(self.repo),
            "--mode",
            "implementation",
            expected=2,
        )
        self.assertIn("explicit user confirmation", denied_mode["error"])
        mode = self.run_cli(
            "set-mode",
            "--repo",
            str(self.repo),
            "--mode",
            "implementation",
            "--confirmation",
            "User explicitly requested implementation mode.",
        )
        self.assertEqual("implementation", mode["mode"])

    def test_context_packet_is_scoped_to_one_workstream(self) -> None:
        self.initialize()
        self.open_qa()
        output = self.run_cli(
            "context",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
        )
        self.assertEqual("qa-http", output["workstream"]["id"])
        self.assertEqual(
            "request-flow-chapter", output["attached_task"]["id"]
        )
        self.assertEqual("mainline", output["other_workstreams"][0]["id"])

    def test_session_close_writes_per_workstream_log_and_handoff(self) -> None:
        self.initialize()
        self.open_qa()
        session = self.inputs / "session.json"
        session.write_text(
            json.dumps(
                {
                    "title": "Middleware Q&A",
                    "goal": "Resolve ordering",
                    "completed": ["Read route registration"],
                    "core_files": ["internal/http/routes.go"],
                    "key_insights": ["Ordering follows registration"],
                    "exercises": [],
                    "open_questions": ["How are nested groups ordered?"],
                    "next_step": "Read framework middleware tests",
                    "resume_at": "Nested route group behavior",
                }
            ),
            encoding="utf-8",
        )
        output = self.run_cli(
            "record-session",
            "--repo",
            str(self.repo),
            "--workstream",
            "qa-http",
            "--session",
            str(session),
        )
        self.assertIn("sessions", output["path"])
        log = Path(output["path"]).read_text(encoding="utf-8")
        self.assertIn("Workstream: `qa-http`", log)
        handoff = Path(output["handoff"]).read_text(encoding="utf-8")
        self.assertIn("Nested route group behavior", handoff)

    def test_custom_notes_missing_path_falls_back_without_mutating_on_failure(
        self,
    ) -> None:
        self.propose()
        missing = self.root / "missing-vault"
        output = self.run_cli(
            "set-notes",
            "--repo",
            str(self.repo),
            "--location",
            "custom",
            "--path",
            str(missing),
            "--fallback",
        )
        self.assertTrue(output["fallback_used"])
        config_path = self.repo / ".learning" / "config.json"
        before = config_path.read_text(encoding="utf-8")
        denied = self.run_cli(
            "set-notes",
            "--repo",
            str(self.repo),
            "--location",
            "custom",
            "--path",
            str(self.root / "another-missing"),
            "--no-fallback",
            expected=2,
        )
        self.assertIn("does not exist", denied["error"])
        self.assertEqual(before, config_path.read_text(encoding="utf-8"))

    def test_doctor_validates_multi_workstream_state(self) -> None:
        self.initialize()
        self.open_qa()
        result = self.run_cli("doctor", "--repo", str(self.repo))
        self.assertTrue(result["ok"])
        self.assertEqual(2, result["schema_version"])

    def test_project_lock_rejects_overlapping_mutations_without_deleting_lock(
        self,
    ) -> None:
        with STATE_MODULE.state_lock(
            self.repo, "first-writer", timeout_seconds=0.1
        ):
            with self.assertRaises(STATE_MODULE.StateError):
                with STATE_MODULE.state_lock(
                    self.repo, "second-writer", timeout_seconds=0.1
                ):
                    self.fail("overlapping lock unexpectedly succeeded")
            self.assertTrue(
                (self.repo / ".learning" / ".state.lock").exists()
            )
        self.assertFalse((self.repo / ".learning" / ".state.lock").exists())

    def test_migrate_v1_archives_and_splits_progress(self) -> None:
        state = self.repo / ".learning"
        state.mkdir()
        config = {
            "schema_version": 1,
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
                "categories": {},
            },
            "progress": {
                "enabled": True,
                "mastery_requires_evidence": True,
            },
            "project": {"focus": [], "excluded_topics": []},
        }
        project = {"schema_version": 1, "name": "legacy"}
        plan = json.loads(self.plan.read_text(encoding="utf-8"))
        plan["schema_version"] = 1
        plan["status"] = "active"
        progress = {
            "schema_version": 1,
            "plan_version": 1,
            "current_stage_id": "request-flow",
            "current_task_id": "request-flow-task-01",
            "current_code_locations": ["internal/http/routes.go"],
            "task_order": ["request-flow-task-01"],
            "tasks": {
                "request-flow-task-01": {
                    "stage_id": "request-flow",
                    "title": "Request lifecycle",
                    "objective": "Trace a request",
                    "source_scope": ["internal/http"],
                    "prerequisites": [],
                    "completion_criteria": ["Explain it"],
                    "status": "learning",
                    "evidence": [],
                    "open_questions": [],
                    "blockers": [],
                    "next_step": "Trace middleware",
                }
            },
            "next_step": "Trace middleware",
        }
        for name, value in (
            ("config.json", config),
            ("project.json", project),
            ("plan.json", plan),
            ("progress.json", progress),
        ):
            (state / name).write_text(json.dumps(value), encoding="utf-8")
        output = self.run_cli("migrate-v1", "--repo", str(self.repo))
        self.assertTrue(output["migrated"])
        self.assertTrue(Path(output["archive"]).exists())
        self.assertFalse((state / "progress.json").exists())
        self.assertTrue((state / "legacy" / "progress-v1.json").exists())
        self.assertTrue(
            (state / "tasks" / "request-flow-task-01.json").exists()
        )
        doctor = self.run_cli("doctor", "--repo", str(self.repo))
        self.assertTrue(doctor["ok"])


    def state_bytes(self) -> dict[str, bytes]:
        return {str(p.relative_to(self.repo)): p.read_bytes()
                for p in (self.repo / ".learning").rglob("*") if p.is_file()}

    def question_input(self, question: str = "为什么把 context 传下去？") -> Path:
        path = self.inputs / "qa.json"
        path.write_text(json.dumps({"question": question,
            "context": "刚才讲到 handler 调用 service，再传到 repository；这段是原讲解。",
            "confusion": "取消信号如何传播", "code_locations": ["internal/http/handler.go:42"],
            "known": ["函数参数"], "unknown": ["驱动是否支持取消"]}, ensure_ascii=False), encoding="utf-8")
        return path

    def handoff(self, request_id: str = "q-context") -> dict:
        return self.run_cli("prepare-qa", "--repo", str(self.repo), "--id", request_id,
                            "--packet", str(self.question_input()))

    def test_resume_fresh_question_does_not_initialize(self) -> None:
        output = self.run_cli("resume", "--repo", str(self.repo), "--intent", "qa")
        self.assertEqual("answer", output["action"])
        self.assertFalse((self.repo / ".learning").exists())
        self.assertEqual("discover", self.run_cli("resume", "--repo", str(self.repo))["action"])
        self.assertFalse((self.repo / ".learning").exists())

    def test_resume_proposal_answers_without_activation(self) -> None:
        self.propose()
        before = self.state_bytes()
        self.assertEqual("answer", self.run_cli("resume", "--repo", str(self.repo), "--intent", "qa")["action"])
        self.assertEqual("confirm_plan", self.run_cli("resume", "--repo", str(self.repo))["action"])
        self.assertEqual(before, self.state_bytes())

    def test_resume_existing_route_reads_without_scan_or_writes(self) -> None:
        self.propose()
        self.activate()
        self.run_cli("checkpoint", "--repo", str(self.repo), "--workstream", "mainline",
                     "--resume-at", "handler.go:42", "--explanation", "解释请求取消")
        before = self.state_bytes()
        restored = self.run_cli("resume", "--repo", str(self.repo))
        self.assertEqual("handler.go:42", restored["workstream"]["resume_at"])
        self.assertEqual(before, self.state_bytes())
        self.assertEqual("status", self.run_cli("resume", "--repo", str(self.repo), "--intent", "status")["action"])

    def test_qa_packet_freezes_context_without_moving_mainline(self) -> None:
        self.propose()
        self.activate()
        self.run_cli("checkpoint", "--repo", str(self.repo), "--workstream", "mainline",
                     "--resume-at", "handler.go:42", "--explanation", "原始讲解")
        protected = [self.repo / ".learning" / "plan.json",
                     self.repo / ".learning" / "workstreams" / "mainline.json",
                     *list((self.repo / ".learning" / "tasks").glob("*.json"))]
        before = {str(p): p.read_bytes() for p in protected}
        output = self.handoff()
        packet_path = Path(output["packet_path"])
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        self.assertEqual("原始讲解", packet["source_context"]["workstream"]["recent_explanation"])
        self.assertIn("原讲解", packet["input"]["context"])
        self.assertIn(str(self.repo), output["prompt"])
        self.assertIn(str(packet_path), output["prompt"])
        self.assertIn("$adaptive-engineering-learning", output["prompt"])
        self.assertEqual(before, {str(p): p.read_bytes() for p in protected})
        snapshot = packet_path.read_bytes()
        self.run_cli("checkpoint", "--repo", str(self.repo), "--workstream", "mainline",
                     "--resume-at", "database.go:100", "--explanation", "后来讲解")
        self.assertEqual(snapshot, packet_path.read_bytes())
        qa = self.run_cli("resume", "--repo", str(self.repo), "--workstream", output["workstream_id"], "--intent", "qa")
        self.assertEqual("answer", qa["action"])
        self.assertNotEqual("mainline", qa["workstream"]["id"])
        self.assertTrue(self.run_cli("doctor", "--repo", str(self.repo))["ok"])

    def test_handoff_retry_and_related_question_keep_qa_checkpoint(self) -> None:
        self.propose()
        self.activate()
        first = self.handoff()
        self.run_cli("checkpoint", "--repo", str(self.repo), "--workstream", first["workstream_id"],
                     "--resume-at", "解释取消信号中")
        before = self.state_bytes()
        self.assertEqual(first, self.handoff())
        self.assertEqual(before, self.state_bytes())
        other = self.handoff("q-follow-up")
        self.assertEqual(first["workstream_id"], other["workstream_id"])
        ws = self.run_cli("context", "--repo", str(self.repo), "--workstream", first["workstream_id"])["workstream"]
        self.assertEqual("解释取消信号中", ws["resume_at"])

    def test_handoff_rejects_id_collision_and_wrong_owner_without_mutation(self) -> None:
        self.propose()
        self.activate()
        self.handoff()
        before = self.state_bytes()
        self.run_cli("prepare-qa", "--repo", str(self.repo), "--id", "q-context",
                     "--packet", str(self.question_input("另一个问题")), expected=2)
        self.run_cli("prepare-qa", "--repo", str(self.repo), "--id", "q-wrong-owner",
                     "--workstream", "mainline", "--packet", str(self.question_input()), expected=2)
        self.assertEqual(before, self.state_bytes())

    def test_thread_binding_restores_qa_and_rejects_overwrite(self) -> None:
        self.propose()
        self.activate()
        first = self.handoff()
        ws_id = first["workstream_id"]
        self.run_cli("bind-thread", "--repo", str(self.repo), "--workstream", ws_id, "--thread", "actual-tool-id")
        before = self.state_bytes()
        self.assertFalse(self.run_cli("bind-thread", "--repo", str(self.repo), "--workstream", ws_id,
                                      "--thread", "actual-tool-id")["changed"])
        restored = self.run_cli("resume", "--repo", str(self.repo), "--thread", "actual-tool-id")
        self.assertEqual(ws_id, restored["workstream"]["id"])
        self.assertEqual("answer", restored["action"])
        self.run_cli("bind-thread", "--repo", str(self.repo), "--workstream", ws_id, "--thread", "another-id", expected=2)
        self.run_cli("bind-thread", "--repo", str(self.repo), "--workstream", "mainline", "--thread", "actual-tool-id", expected=2)
        self.assertEqual(before, self.state_bytes())
        self.assertEqual("actual-tool-id", self.handoff()["thread"]["id"])

    def test_unbound_qa_does_not_guess_latest_window(self) -> None:
        self.propose()
        self.activate()
        self.handoff()
        output = self.run_cli("resume", "--repo", str(self.repo), "--intent", "qa")
        self.assertEqual("select_qa_context", output["action"])
        self.assertNotIn("workstream", output)

    def test_handoff_from_other_cwd_keeps_full_source_context(self) -> None:
        self.propose()
        self.activate()
        path = self.question_input()
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["context"] = "相关源码讲解。" * 4000 + "END-OF-RELEVANT-PASSAGE"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        other_checkout = self.root / "other-checkout"
        other_checkout.mkdir()
        result = subprocess.run([sys.executable, str(SCRIPT), "prepare-qa", "--repo", str(self.repo),
                                 "--packet", str(path), "--id", "q-long-context"], cwd=other_checkout,
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        packet = json.loads(Path(receipt["packet_path"]).read_text(encoding="utf-8"))
        self.assertEqual(payload["context"], packet["input"]["context"])
        self.assertEqual(str(self.repo.resolve()), packet["source_repo"])
        self.assertFalse((other_checkout / ".learning").exists())

    def test_handoff_does_not_create_runtime_before_activation(self) -> None:
        self.run_cli("prepare-qa", "--repo", str(self.repo), "--packet", str(self.question_input()), expected=2)
        self.assertFalse((self.repo / ".learning").exists())
        self.propose()
        before = self.state_bytes()
        self.run_cli("prepare-qa", "--repo", str(self.repo), "--packet", str(self.question_input()), expected=2)
        self.assertEqual(before, self.state_bytes())

    def test_unchanged_checkpoint_is_noop_and_explanation_is_not_evidence(self) -> None:
        self.propose()
        self.activate()
        args = ("checkpoint", "--repo", str(self.repo), "--workstream", "mainline",
                "--resume-at", "函数入口", "--explanation", "完整讲解段落")
        self.run_cli(*args)
        before = self.state_bytes()
        self.assertFalse(self.run_cli(*args)["changed"])
        self.assertEqual(before, self.state_bytes())
        task = self.run_cli("context", "--repo", str(self.repo), "--workstream", "mainline")["attached_task"]
        self.assertFalse(task["evidence"])
        self.assertEqual("learning", task["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
