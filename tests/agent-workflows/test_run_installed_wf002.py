"""Deterministic checks for installed WF-002 preparation; no paid sessions."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import subprocess


RUNNER = Path(__file__).with_name("run_installed_wf002.py")
spec = importlib.util.spec_from_file_location("run_installed_wf002", RUNNER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class InstalledPreparationTests(unittest.TestCase):
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
            with self.assertRaisesRegex(ValueError, "already contains"):
                runner.add_story(target)

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
                  patch.object(runner, "add_story"),
                  patch.object(runner, "run_cli", side_effect=[success, blocked]),
                  patch.object(runner, "command", side_effect=[
                      Mock(stdout=""), Mock(stdout="story-branch\n"), Mock(stdout="")])):
                side = runner.run_side("baseline-1", "a" * 40, Path(directory), 2.0)
            self.assertTrue(side["installed"])
            self.assertFalse(side["story_started"])
            self.assertIn("blocked outcome", side["blocked_reason"])


if __name__ == "__main__":
    unittest.main()
