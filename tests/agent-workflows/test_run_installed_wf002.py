"""Deterministic checks for installed WF-002 preparation; no paid sessions."""

from __future__ import annotations

import importlib.util
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import subprocess
import sys


RUNNER = Path(__file__).with_name("run_installed_wf002.py")
spec = importlib.util.spec_from_file_location("run_installed_wf002", RUNNER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class InstalledPreparationTests(unittest.TestCase):
    def test_verifier_rejects_unfinished_init_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            state = target / '.claude/agents/tmp/init_project_state.md'
            state.parent.mkdir(parents=True)
            state.write_text('Stage: 4', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Incomplete init workflow'):
                runner.verify_install(target)

    def test_cli_passes_trusted_policy_and_detects_success_with_denial(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            settings = root / "settings.json"
            def fake_run(argv, **kwargs):
                self.assertIn("--restricted", argv)
                self.assertNotIn("--no-session-persistence", argv)
                self.assertEqual(argv[argv.index("--settings") + 1], str(settings))
                self.assertEqual(argv.count("--append-system-prompt"), 1)
                self.assertTrue(argv[argv.index("--append-system-prompt") + 1].startswith(runner.FILE_TOOL_POLICY))
                self.assertIn((root / '.wf002-tmp').as_posix(), argv[argv.index('--append-system-prompt') + 1])
                kwargs["stdout"].write(json.dumps({"type": "result", "is_error": False,
                    "result": "Done", "permission_denials": [{"tool_name": "Bash"}]}) + "\n")
                return subprocess.CompletedProcess(argv, 0, "", "")
            with patch.object(runner.subprocess, "run", side_effect=fake_run):
                result = runner.run_cli(root, root / "stream.jsonl", "test", 1, settings=settings)
            self.assertEqual(result["permission_denials"], 1)
            self.assertFalse(runner.session_completed(result))

    def test_permission_denial_is_not_workflow_success(self) -> None:
        session = {"exit_code": 0, "result_present": True, "is_error": False,
                   "blocked_signal": False, "timed_out": False, "permission_denials": 1}
        self.assertFalse(runner.session_completed(session))

    def test_permission_policy_is_stored_outside_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target"
            target.mkdir()
            settings = runner.permission_settings(target, root / "policy.json")
            data = json.loads(settings.read_text(encoding="utf-8"))
            hook = data["hooks"]["PermissionRequest"][0]
            self.assertEqual(hook["matcher"], "Write|Edit|Bash")
            self.assertIn(target.resolve().as_posix(), hook["hooks"][0]["command"])
            with self.assertRaisesRegex(ValueError, "outside"):
                runner.permission_settings(target, target / "policy.json")

    def test_complete_capture_still_requires_g2_quality_review(self) -> None:
        completed = [{"story_started": True}, {"story_started": True}]
        self.assertEqual(runner.run_exit_code(completed, 2), 2)
        self.assertEqual(runner.run_exit_code(completed[:1], 2), 1)
        self.assertEqual(runner.run_exit_code([completed[0], {"story_started": False}], 2), 1)

    def test_export_pinned_baseline_and_seed_remote_free_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            root = Path(directory)
            source, target = root / "devkit", root / "target"
            ref = runner.full_ref("a30460a87c6d439b1193c45b77cc638a8f237fdb")
            runner.export_source(ref, source)
            self.assertTrue((source / "CLAUDE.md").is_file())
            self.assertTrue((source / ".claude/agents/working/scripts/scaffold_mechanical.sh").is_file())
            runner.seed_target(target)
            self.assertEqual(runner.command(["git", "remote"], target).stdout.strip(), "")
            self.assertEqual(runner.command(["git", "branch", "--show-current"], target).stdout.strip(), "main")
            self.assertIn("if subtotal_cents >", (target / "pricing.py").read_text(encoding="utf-8"))

    def test_verifier_requires_real_installed_files_before_story(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            target = Path(directory)
            with self.assertRaisesRegex(ValueError, "Incomplete installed project"):
                runner.verify_install(target)
            runner.command(["git", "init", "-q", "-b", "main"], target)
            for name in runner.REQUIRED_INSTALLED:
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("**Mode:** strict\n" if name == "CLAUDE.md" else "installed\n",
                                encoding="utf-8")
            for role in runner.ROLES:
                path = target / ".claude/agents" / f"{role}_instructions.md"
                path.write_text("installed\n", encoding="utf-8")
            for name in ("context/Project_Priming.md", "context/Document_Index.md"):
                path = target / ".claude/agents" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("adapted\n", encoding="utf-8")
            hashes = runner.verify_install(target)
            self.assertEqual(set(hashes), set(runner.REQUIRED_INSTALLED))
            (target / ".claude/agents/context/Project_Priming.md").write_text(
                "{project-name}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "adaptive files are incomplete"):
                runner.verify_install(target)
            (target / ".claude/agents/context/Project_Priming.md").write_text(
                "adapted\n", encoding="utf-8")
            (target / "CLAUDE.md").write_text("**Mode:** {{MODE}}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not fully adapted"):
                runner.verify_install(target)

    def test_story_is_strict_ready_with_immutable_main_base(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            target = Path(directory)
            (target / ".claude/agents/docs/stories").mkdir(parents=True)
            runner.add_story(target)
            story = (target / ".claude/agents/docs/stories" / f"{runner.STORY_ID}.md").read_text(
                encoding="utf-8")
            self.assertIn("**Status:** ready", story)
            self.assertIn("**Sprint:** sprint-1", story)
            self.assertIn("**Project Base Branch:** main", story)
            self.assertIn("**Assigned:** Developer", story)
            self.assertIn("**Feature:** none", story)
            self.assertIn("**Phase:** none", story)
            self.assertIn("## Technical Scope", story)
            self.assertIn("exactly 5,000 cents", story)
            self.assertEqual(story.count("- [ ] "), 5)
            self.assertNotIn("1. Standard shipping", story)
            with self.assertRaisesRegex(ValueError, "already contains"):
                runner.add_story(target)

    def test_installed_scaffold_commit_creates_clean_main_base(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            target = Path(directory) / "target"
            runner.seed_target(target)
            for name in (".claude/settings.json", ".claude/skills/read-section/SKILL.md",
                         ".gitignore", "CHANGELOG.md", "CLAUDE.md", "VERSION",
                         "docs/wiki/Testing_Guidelines.md"):
                path = target / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("installed\n", encoding="utf-8")
            sha = runner.commit_install_scaffold(target)
            self.assertEqual(len(sha), 40)
            self.assertEqual(runner.command(["git", "status", "--porcelain"], target).stdout, "")
            self.assertEqual(runner.command(["git", "branch", "--show-current"], target).stdout.strip(), "main")

    def test_installed_diff_allows_required_changelog_but_checks_exact_product_change(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            target = Path(directory) / "target"
            runner.seed_target(target)
            (target / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            runner.command(["git", "add", "CHANGELOG.md"], target)
            runner.command(["git", "-c", "user.name=Benchmark", "-c",
                            "user.email=benchmark@example.invalid", "commit", "-qm", "Install changelog"], target)
            base_sha = runner.command(["git", "rev-parse", "HEAD"], target).stdout.strip()
            pricing = target / "pricing.py"
            pricing.write_text(pricing.read_text(encoding="utf-8").replace(
                "if subtotal_cents > FREE_STANDARD_SHIPPING_THRESHOLD_CENTS:",
                "if subtotal_cents >= FREE_STANDARD_SHIPPING_THRESHOLD_CENTS:"), encoding="utf-8")
            (target / "CHANGELOG.md").write_text("# Changelog\n- [ST-000211] Fix standard shipping at the 5,000-cent threshold.\n",
                                                   encoding="utf-8")
            runner.command(["git", "add", "pricing.py", "CHANGELOG.md"], target)
            runner.command(["git", "-c", "user.name=Benchmark", "-c",
                            "user.email=benchmark@example.invalid", "commit", "-qm", "Fix shipping"], target)
            report = runner.inspect_product_diff(target, base_sha)
            self.assertTrue(report["product_paths_match"])
            self.assertTrue(report["pricing_change_exact"])
            self.assertTrue(report["changelog_entry_present"])
            self.assertTrue(report["changelog_scope_valid"])
            self.assertTrue(report["working_tree_clean"])
            self.assertEqual(len(report["implementation_sha"]), 40)
            self.assertEqual(report["unexpected_paths"], [])
            untracked = target / "unrelated.txt"
            untracked.write_text("extra", encoding="utf-8")
            self.assertFalse(runner.inspect_product_diff(target, base_sha)["working_tree_clean"])
            untracked.unlink()
            (target / "CHANGELOG.md").write_text("# Changelog\n" + runner.CHANGELOG_ENTRY
                + "\n- Unrelated feature.\n", encoding="utf-8")
            runner.command(["git", "add", "CHANGELOG.md"], target)
            self.assertFalse(runner.inspect_product_diff(target, base_sha)["working_tree_clean"])
            runner.command(["git", "-c", "user.name=Benchmark", "-c",
                            "user.email=benchmark@example.invalid", "commit", "-qm", "Unrelated changelog"], target)
            self.assertFalse(runner.inspect_product_diff(target, base_sha)["changelog_scope_valid"])
            (target / "README.md").write_text("Unrelated change\n", encoding="utf-8")
            runner.command(["git", "add", "README.md"], target)
            runner.command(["git", "-c", "user.name=Benchmark", "-c",
                            "user.email=benchmark@example.invalid", "commit", "-qm", "Unrelated"], target)
            report = runner.inspect_product_diff(target, base_sha)
            self.assertFalse(report["product_paths_match"])
            self.assertEqual(report["unexpected_paths"], ["README.md"])

    def test_frozen_preflight_and_drift_fail_before_any_agent_run(self):
        frozen = json.loads(runner.contracts.MANIFEST.read_text(encoding="utf-8"))
        original = runner.command
        def fake_command(argv, cwd, **kwargs):
            if argv == ["claude", "--version"]:
                return Mock(stdout=frozen["cli_version"])
            return original(argv, cwd, **kwargs)
        with patch.object(runner, "command", side_effect=fake_command), patch.object(runner, "run_cli") as paid:
            with patch.object(sys, "argv", ["runner"]), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(runner.main(), 0)
            self.assertEqual(json.loads(output.getvalue()), frozen)
            for argv in (["runner", "--repetitions", "1", "--execute"],
                         ["runner", "--max-budget-usd", "2", "--execute"]):
                with patch.object(sys, "argv", argv), self.assertRaisesRegex(ValueError, "drift"):
                    runner.main()
            with patch.object(runner.contracts, "source_digest", return_value="changed"), \
                 patch.object(sys, "argv", ["runner", "--execute"]), self.assertRaisesRegex(ValueError, "drift"):
                runner.main()
            paid.assert_not_called()

    def test_resolved_model_drift_blocks_session(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def fake_run(argv, **kwargs):
                kwargs["stdout"].write(json.dumps({"type": "assistant", "message": {"model": "other-model"}}) + "\n")
                kwargs["stdout"].write(json.dumps({"type": "result", "is_error": False, "result": "Done"}) + "\n")
                return subprocess.CompletedProcess(argv, 0, "", "")
            with patch.object(runner.subprocess, "run", side_effect=fake_run):
                result = runner.run_cli(root, root / "stream.jsonl", "test", 4)
            self.assertFalse(result["resolved_model_matches"])
            self.assertFalse(runner.session_completed(result))

    def test_assessment_uses_install_base_and_keeps_missing_reviews_pending(self):
        with tempfile.TemporaryDirectory() as folder:
            side = Path(folder)
            target = side / "target"
            runner.seed_target(target)
            base = runner.command(["git", "rev-parse", "HEAD"], target).stdout.strip()
            result = runner.assess_quality(side, base)
            self.assertTrue(result["main_unchanged"])
            self.assertFalse(result["automated_quality_checks_pass"])
            self.assertFalse(result["review_evidence"]["evidence_valid"])
            self.assertEqual(result["gate_g2"], "unassessed")

    def test_offline_capture_assessment_preserves_original_and_never_launches_agent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            frozen = json.loads(runner.contracts.MANIFEST.read_text(encoding="utf-8"))
            summary = {"config": frozen, "sides": [{"label": "baseline-1", "installed_base_sha": "a" * 40}]}
            path = root / "summary.json"
            path.write_text(json.dumps(summary), encoding="utf-8")
            with patch.object(runner, "run_cli") as paid, \
                 patch.object(runner, "assess_quality", return_value={"gate_g2": "unassessed"}) as assessment:
                self.assertEqual(runner.assess_capture(root), 2)
                assessment.assert_called_once_with(root / "baseline-1", "a" * 40)
                paid.assert_not_called()
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), summary)
            self.assertTrue((root / "assessment.json").is_file())
            summary["sides"][0]["label"] = "../escape"
            path.write_text(json.dumps(summary), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "label"):
                runner.assess_capture(root)

    def test_stage_telemetry_requires_four_distinct_measured_roles(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            target = Path(directory)
            self.assertFalse(runner.inspect_stage_telemetry(target)["required_stages_present_once"])
            folder = target / ".claude/agents/tmp/token-metrics"
            folder.mkdir(parents=True)
            stages = ("developer_implementation", "technical_lead_review", "qa_verification",
                      "product_owner_closure")
            rows = [runner.contracts.telemetry.build_record({
                "run_id": "wf002-test", "story_id": runner.STORY_ID,
                "role": runner.contracts.STAGE_ROLES[stage], "stage": stage,
                "session_mode": "fresh", "model": runner.EXPECTED_MODEL,
                "started_at": "2026-10-02T00:00:00Z", "ended_at": "2026-10-02T00:00:01Z",
                "duration_ms": 1000, "completion_status": "completed", "notes": ""},
                "raw_transcript", {"requests": 2, "tool_invocations": 3,
                    "input_tokens": 10, "cache_creation_input_tokens": 0,
                    "cache_read_input_tokens": 100, "output_tokens": 5}) for stage in stages]
            path = folder / "run.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            report = runner.inspect_stage_telemetry(target)
            self.assertTrue(report["required_stages_present_once"])
            self.assertTrue(report["measured_usage_for_every_stage"])
            rows[3]["usage_source"] = "unavailable"
            rows[3]["requests"] = None
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            self.assertFalse(runner.inspect_stage_telemetry(target)["measured_usage_for_every_stage"])
            rows[3]["stage"] = stages[2]
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            self.assertFalse(runner.inspect_stage_telemetry(target)["required_stages_present_once"])

    def test_story_quality_requires_unchanged_checked_ac_and_six_passing_tests(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            target = Path(directory) / "target"
            runner.seed_target(target)
            story_dir = target / ".claude/agents/docs/stories"
            story_dir.mkdir(parents=True)
            runner.add_story(target)
            report = runner.inspect_story_quality(target)
            self.assertEqual(report["tests_run"], 6)
            self.assertFalse(report["tests_pass"])
            self.assertFalse(report["acceptance_criteria_complete"])
            pricing = target / "pricing.py"
            pricing.write_text(pricing.read_text(encoding="utf-8").replace(
                "if subtotal_cents > FREE_STANDARD_SHIPPING_THRESHOLD_CENTS:",
                "if subtotal_cents >= FREE_STANDARD_SHIPPING_THRESHOLD_CENTS:"), encoding="utf-8")
            story_path = story_dir / f"{runner.STORY_ID}.md"
            story = story_path.read_text(encoding="utf-8").replace(
                "**Status:** ready", "**Status:** done").replace("- [ ] ", "- [x] ")
            story_path.write_text(story, encoding="utf-8")
            report = runner.inspect_story_quality(target)
            self.assertEqual(report["story_status"], "done")
            self.assertTrue(report["acceptance_criteria_complete"])
            self.assertTrue(report["tests_pass"])
            story_path.write_text(story.replace("Standard shipping costs 500 cents",
                                                "Standard shipping costs 400 cents"), encoding="utf-8")
            self.assertFalse(runner.inspect_story_quality(target)["acceptance_criteria_complete"])

    def test_successful_cli_exit_does_not_complete_blocked_workflow(self) -> None:
        session = {"exit_code": 0, "result_present": True, "is_error": False,
                   "blocked_signal": True, "timed_out": False}
        self.assertFalse(runner.session_completed(session))
        session["blocked_signal"] = False
        self.assertTrue(runner.session_completed(session))
        session["timed_out"] = True
        self.assertFalse(runner.session_completed(session))

    def test_timeout_preserves_partial_event_count(self) -> None:
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            root = Path(directory)
            stream = root / "events.jsonl"

            def timeout(*args: object, **kwargs: object) -> None:
                kwargs["stdout"].write('{"type":"assistant","message":{"model":"claude-sonnet-5-5"}}\n')
                kwargs["stdout"].write('{"type":"assistant","message":')
                raise subprocess.TimeoutExpired(args[0], runner.CLI_TIMEOUT_SECONDS)

            with patch.object(runner.subprocess, "run", side_effect=timeout):
                outcome = runner.run_cli(root, stream, "test", 2.0)
            self.assertTrue(outcome["timed_out"])
            self.assertEqual(outcome["partial_assistant_events"], 1)
            self.assertEqual(outcome["partial_model_ids"], ["claude-sonnet-5-5"])
            self.assertEqual(outcome["truncated_events"], 1)
            self.assertFalse(runner.session_completed(outcome))

    def test_run_side_rejects_blocked_init_with_zero_cli_exit(self) -> None:
        blocked = {"exit_code": 0, "result_present": True, "is_error": False,
                   "blocked_signal": True, "timed_out": False}
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            with (patch.object(runner, "export_source"), patch.object(runner, "seed_target"),
                  patch.object(runner, "run_cli", return_value=blocked),
                  patch.object(runner, "verify_install") as verify):
                side = runner.run_side("baseline-1", "a" * 40, Path(directory), 2.0)
            self.assertFalse(side["installed"])
            self.assertFalse(side["story_started"])
            self.assertIn("blocked outcome", side["blocked_reason"])
            verify.assert_not_called()

    def test_run_side_rejects_blocked_start_with_zero_cli_exit(self) -> None:
        success = {"exit_code": 0, "result_present": True, "is_error": False,
                   "blocked_signal": False, "timed_out": False}
        blocked = dict(success, blocked_signal=True)
        with tempfile.TemporaryDirectory(prefix="wf002-installed-test-", dir=RUNNER.parent) as directory:
            with (patch.object(runner, "export_source"), patch.object(runner, "seed_target"),
                  patch.object(runner, "verify_install", return_value={}),
                  patch.object(runner, "commit_install_scaffold", return_value="a" * 40),
                  patch.object(runner, "add_story"),
                  patch.object(runner, "inspect_product_diff", return_value={}),
                  patch.object(runner, "inspect_stage_telemetry", return_value={}),
                  patch.object(runner, "inspect_story_quality", return_value={}),
                  patch.object(runner, "assess_quality", return_value={}),
                  patch.object(runner, "run_cli", side_effect=[success, blocked]),
                  patch.object(runner, "command", side_effect=[
                      Mock(stdout=""), Mock(stdout="story-branch\n"), Mock(stdout=""), Mock(stdout="a" * 40)])):
                side = runner.run_side("baseline-1", "a" * 40, Path(directory), 2.0)
            self.assertTrue(side["installed"])
            self.assertFalse(side["story_started"])
            self.assertIn("blocked outcome", side["blocked_reason"])


if __name__ == "__main__":
    unittest.main()
