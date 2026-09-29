"""Deterministic checks for installed WF-002 preparation; no paid sessions."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


RUNNER = Path(__file__).with_name("run_installed_wf002.py")
spec = importlib.util.spec_from_file_location("run_installed_wf002", RUNNER)
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class InstalledPreparationTests(unittest.TestCase):
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
            hashes = runner.verify_install(target)
            self.assertEqual(set(hashes), set(runner.REQUIRED_INSTALLED))
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
            self.assertIn("exactly 5,000 cents", story)
            with self.assertRaisesRegex(ValueError, "already contains"):
                runner.add_story(target)


if __name__ == "__main__":
    unittest.main()
