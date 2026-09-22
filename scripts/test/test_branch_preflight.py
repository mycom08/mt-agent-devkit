"""Temporary-repository regression tests for branch_preflight.py."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = ROOT / ".claude" / "agents" / "templates" / "scripts" / "branch_preflight.py"
SPEC = importlib.util.spec_from_file_location("branch_preflight", HELPER_PATH)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = preflight
SPEC.loader.exec_module(preflight)


def run(cwd: Path, *args: str, check: bool = True) -> str:
    completed = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and completed.returncode:
        raise AssertionError(f"{' '.join(args)} failed: {completed.stderr}")
    return completed.stdout.strip()


class PreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "scripts" / "test")
        self.root = Path(self.temp.name).resolve()
        self.remote = self.root / "remote.git"
        self.local = self.root / "local"
        run(self.root, "git", "init", "--bare", str(self.remote))
        run(self.root, "git", "init", "-b", "main", str(self.local))
        run(self.local, "git", "config", "user.email", "fixture@example.invalid")
        run(self.local, "git", "config", "user.name", "Fixture")
        (self.local / "README.md").write_text("base\n", encoding="utf-8")
        run(self.local, "git", "add", "README.md")
        run(self.local, "git", "commit", "-m", "base")
        run(self.local, "git", "remote", "add", "origin", str(self.remote))
        run(self.local, "git", "push", "-u", "origin", "main")
        self.previous_cwd = Path.cwd()
        os.chdir(self.local)

    def tearDown(self) -> None:
        os.chdir(self.previous_cwd)
        self.temp.cleanup()

    def inspect(self, mode: str = "github", branch: str = "story/ST-000001"):
        return preflight.inspect(mode, "main", branch)

    def assert_blocked_no_mutation(self, before_refs: str, before_status: str, result) -> None:
        self.assertFalse(result.passed)
        self.assertEqual(before_refs, run(self.local, "git", "show-ref", "--heads"))
        self.assertEqual(before_status, run(self.local, "git", "status", "--porcelain"))
        self.assertEqual("", run(self.local, "git", "stash", "list"))

    def snapshot(self) -> tuple[str, str]:
        return run(self.local, "git", "show-ref", "--heads"), run(self.local, "git", "status", "--porcelain")

    def test_b01_clean_synced_base_passes_and_b10_creates_at_recorded_sha(self) -> None:
        result = self.inspect()
        self.assertTrue(result.passed)
        created = preflight.create("github", "main", "story/ST-000001", result.base_sha, result.remote_sha)
        self.assertTrue(created.passed)
        self.assertEqual("story/ST-000001", created.story_branch)
        self.assertEqual(result.base_sha, run(self.local, "git", "rev-parse", "HEAD"))

    def test_b02_dirty_tracked_file_blocks_without_recovery(self) -> None:
        (self.local / "README.md").write_text("changed\n", encoding="utf-8")
        refs, status = self.snapshot()
        self.assert_blocked_no_mutation(refs, status, self.inspect())

    def test_b03_untracked_file_blocks(self) -> None:
        (self.local / "user-file.txt").write_text("keep\n", encoding="utf-8")
        refs, status = self.snapshot()
        self.assert_blocked_no_mutation(refs, status, self.inspect())

    def test_b04_behind_blocks(self) -> None:
        peer = self.root / "peer"
        run(self.root, "git", "clone", str(self.remote), str(peer))
        run(peer, "git", "checkout", "-b", "main", "origin/main")
        run(peer, "git", "config", "user.email", "fixture@example.invalid")
        run(peer, "git", "config", "user.name", "Fixture")
        (peer / "remote.txt").write_text("remote\n", encoding="utf-8")
        run(peer, "git", "add", "remote.txt")
        run(peer, "git", "commit", "-m", "remote")
        run(peer, "git", "push")
        refs, status = self.snapshot()
        result = self.inspect()
        self.assertIn("behind", result.reason)
        self.assert_blocked_no_mutation(refs, status, result)

    def test_b05_ahead_blocks_with_bounded_evidence(self) -> None:
        (self.local / "ahead.txt").write_text("ahead\n", encoding="utf-8")
        run(self.local, "git", "add", "ahead.txt")
        run(self.local, "git", "commit", "-m", "ahead")
        refs, status = self.snapshot()
        result = self.inspect()
        self.assertIn("ahead", result.reason)
        self.assertLessEqual(len(result.evidence or []), 3)
        self.assert_blocked_no_mutation(refs, status, result)

    def test_ahead_agent_commit_reports_agent_state_before_ahead_block(self) -> None:
        run(self.local, "git", "commit", "--allow-empty", "-m", "Agent: runtime handoff")
        result = self.inspect()
        self.assertEqual("base is ahead of upstream", result.reason)
        self.assertEqual("yes", result.agent_state)

    def test_b06_diverged_blocks(self) -> None:
        (self.local / "local.txt").write_text("local\n", encoding="utf-8")
        run(self.local, "git", "add", "local.txt")
        run(self.local, "git", "commit", "-m", "local")
        peer = self.root / "peer"
        run(self.root, "git", "clone", str(self.remote), str(peer))
        run(peer, "git", "checkout", "-b", "main", "origin/main")
        run(peer, "git", "config", "user.email", "fixture@example.invalid")
        run(peer, "git", "config", "user.name", "Fixture")
        (peer / "remote.txt").write_text("remote\n", encoding="utf-8")
        run(peer, "git", "add", "remote.txt")
        run(peer, "git", "commit", "-m", "remote")
        run(peer, "git", "push")
        refs, status = self.snapshot()
        result = self.inspect()
        self.assertIn("diverges", result.reason)
        self.assert_blocked_no_mutation(refs, status, result)

    def test_b07_synced_and_strict_tracked_runtime_state_block_but_unrelated_fetch_ref_does_not(self) -> None:
        state = self.local / ".antigravity" / "agents" / "memory"
        state.mkdir(parents=True)
        (state / "Developer_Memory.md").write_text("runtime\n", encoding="utf-8")
        run(self.local, "git", "add", ".antigravity")
        run(self.local, "git", "commit", "-m", "Agent: update memory")
        run(self.local, "git", "push")
        self.assertIn("runtime state", self.inspect().reason)
        self.assertIn("runtime state", self.inspect("strict").reason)

        clean = self.root / "clean"
        run(self.root, "git", "clone", str(self.remote), str(clean))
        run(clean, "git", "config", "user.email", "fixture@example.invalid")
        run(clean, "git", "config", "user.name", "Fixture")
        run(clean, "git", "checkout", "-b", "other")
        (clean / "other.txt").write_text("state\n", encoding="utf-8")
        run(clean, "git", "add", "other.txt")
        run(clean, "git", "commit", "-m", "Agent: unrelated")
        run(clean, "git", "push", "-u", "origin", "other")
        # A clean independent fixture with an unrelated fetched Agent: ref must pass.
        second = self.root / "second"
        run(self.root, "git", "init", "-b", "main", str(second))
        run(second, "git", "config", "user.email", "fixture@example.invalid")
        run(second, "git", "config", "user.name", "Fixture")
        (second / "README.md").write_text("clean\n", encoding="utf-8")
        run(second, "git", "add", "README.md")
        run(second, "git", "commit", "-m", "base")
        bare = self.root / "clean-remote.git"
        run(self.root, "git", "init", "--bare", str(bare))
        run(second, "git", "remote", "add", "origin", str(bare))
        run(second, "git", "push", "-u", "origin", "main")
        run(second, "git", "fetch", str(self.remote), "other:refs/remotes/external/other")
        old_local = self.local
        self.local = second
        old_cwd = Path.cwd()
        os.chdir(second)
        try:
            self.assertTrue(self.inspect().passed)
        finally:
            os.chdir(old_cwd)
            self.local = old_local

    def test_b08_strict_without_remote_passes_with_unavailable_remote_fields(self) -> None:
        local = self.local
        run(local, "git", "remote", "remove", "origin")
        fetch_head = local / ".git" / "FETCH_HEAD"
        if fetch_head.exists():
            fetch_head.unlink()
        result = self.inspect("strict")
        self.assertTrue(result.passed)
        self.assertIsNone(result.remote_sha)
        self.assertEqual("unavailable", result.ahead_behind)
        self.assertFalse(fetch_head.exists(), "strict inspect must not fetch")

    def test_strict_new_sprint_then_resumed_sprint_then_story_is_sha_pinned(self) -> None:
        sprint = preflight.inspect("strict", "main", "sprint-1-dev")
        self.assertTrue(sprint.passed)
        created_sprint = preflight.create("strict", "main", "sprint-1-dev", sprint.base_sha, None)
        self.assertTrue(created_sprint.passed)
        self.assertEqual(sprint.base_sha, run(self.local, "git", "rev-parse", "HEAD"))

        # A resume treats the existing sprint branch as the base and supplies
        # a future story branch target, so it cannot collide with itself.
        resumed = preflight.inspect("strict", "sprint-1-dev", "story/ST-000001")
        self.assertTrue(resumed.passed)
        self.assertEqual(created_sprint.story_branch, run(self.local, "git", "branch", "--show-current"))
        created_story = preflight.create("strict", "sprint-1-dev", "story/ST-000001", resumed.base_sha, None)
        self.assertTrue(created_story.passed)
        self.assertEqual(resumed.base_sha, run(self.local, "git", "rev-parse", "HEAD"))

    def test_strict_claude_runtime_state_in_verified_tree_blocks(self) -> None:
        state = self.local / ".claude" / "agents" / "memory"
        state.mkdir(parents=True)
        (state / "Developer_Memory.md").write_text("runtime\n", encoding="utf-8")
        run(self.local, "git", "add", ".claude")
        run(self.local, "git", "commit", "-m", "tracked runtime state")
        result = self.inspect("strict")
        self.assertEqual("yes", result.agent_state)
        self.assertIn("runtime state", result.reason)

    def test_b09_wrong_base_blocks(self) -> None:
        run(self.local, "git", "checkout", "-b", "wrong")
        result = self.inspect()
        self.assertIn("not the checked-out", result.reason)

    def test_create_blocks_when_base_ref_drifts_after_inspect(self) -> None:
        inspected = self.inspect()
        peer = self.root / "peer"
        run(self.root, "git", "clone", str(self.remote), str(peer))
        run(peer, "git", "checkout", "-b", "main", "origin/main")
        run(peer, "git", "config", "user.email", "fixture@example.invalid")
        run(peer, "git", "config", "user.name", "Fixture")
        (peer / "drift.txt").write_text("new base\n", encoding="utf-8")
        run(peer, "git", "add", "drift.txt")
        run(peer, "git", "commit", "-m", "new base")
        run(peer, "git", "push")
        run(self.local, "git", "fetch", "origin", "main")
        run(self.local, "git", "reset", "--hard", "origin/main")
        result = preflight.create("github", "main", "story/ST-000001", inspected.base_sha, inspected.remote_sha)
        self.assertEqual("verified base changed since inspection", result.reason)
        self.assertIsNone(preflight.ref_sha("refs/heads/story/ST-000001"))

    def test_status_rename_parsing_keeps_both_nul_paths(self) -> None:
        status = b"R  new-name.txt\x00old-name.txt\x00"
        with mock.patch.object(preflight, "git", return_value=status):
            self.assertEqual([b"new-name.txt", b"old-name.txt"], preflight.status_paths())

    def test_cli_rendering_escapes_controls_and_bounds_exact_evidence(self) -> None:
        result = preflight.Result(mode="strict", base="main", evidence=["bad\x01" + "x" * 300] * 25)
        rendered = result.render().splitlines()
        evidence = [line for line in rendered if line.startswith("Evidence: ")]
        self.assertEqual(preflight.MAX_PATHS, len(evidence))
        self.assertTrue(all("\\x01" in line for line in evidence))
        self.assertTrue(all(len(line) == len("Evidence: ") + preflight.MAX_EVIDENCE_CHARS for line in evidence))

    def test_scaffold_ignore_policy_is_declared_for_antigravity_and_claude_modes(self) -> None:
        shell = (ROOT / ".antigravity" / "agents" / "working" / "scripts" / "scaffold_mechanical.sh").read_text(encoding="utf-8")
        powershell = (ROOT / ".antigravity" / "agents" / "working" / "scripts" / "scaffold_mechanical.ps1").read_text(encoding="utf-8")
        for content in (shell, powershell):
            self.assertIn(".antigravity/agents/memory/", content)
            self.assertIn(".antigravity/agents/retros/", content)
            self.assertIn(".antigravity/agents/tmp/", content)
            self.assertIn(".antigravity/agents/", content)
        for suffix in ("memory/", "working-record/", "retros/", "tmp/", "internal/"):
            self.assertIn(f".claude/agents/{suffix}", powershell)
        claude_shell = (ROOT / ".claude" / "agents" / "working" / "scripts" / "scaffold_mechanical.sh").read_text(encoding="utf-8")
        for suffix in ("memory/", "working-record/", "retros/", "tmp/", "internal/"):
            self.assertIn(f".claude/agents/{suffix}", claude_shell)
        self.assertNotIn(".antigravity/agents/memory/", claude_shell)

    def test_rendered_strict_pipeline_creates_story_once_before_any_state_write(self) -> None:
        workflow = (ROOT / ".claude" / "agents" / "templates" / "shared" / "workflows" / "Shared_Pipeline_Stages_Shared_template.md").read_text(encoding="utf-8")
        stage = workflow[workflow.index("1. **Spawn**"):workflow.index("7. **CI/CD check:**")]
        self.assertEqual(1, stage.count("branch_preflight.py create"))
        create_at = stage.index("branch_preflight.py create")
        self.assertLess(create_at, stage.index("write `impl_session"))
        self.assertLess(create_at, stage.index("update story status"))
        for mirror in (
            ROOT / ".claude" / "agents" / "working" / "workflows" / "Shared_Pipeline_Stages.md",
            ROOT / ".antigravity" / "agents" / "working" / "workflows" / "Shared_Pipeline_Stages.md",
        ):
            rendered = mirror.read_text(encoding="utf-8")
            self.assertLess(rendered.index("branch_preflight.py create"), rendered.index("write `impl_session"))


if __name__ == "__main__":
    unittest.main()
