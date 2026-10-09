"""Actual offline release acquisition against a commit-frozen artifact tree."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".mt-agent-devkit/distribution/phase2"))
import build_bundle
import sync
import bootstrap
from scripts.open_next_snapshot import next_snapshot


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = self.root / "target"
        self.target.mkdir()
        self.bundle = self.root / "bundle"
        build_bundle.build(ROOT, self.bundle)
        self.commit = "c" * 40
        self.refs = self.commit + " refs/tags/v0.1.51\n" + "a" * 40 + " refs/tags/v7\n"
        self.metadata = {"0.1.51": {"files": [], "new": [], "modified": [], "deployment": {"schema_version": 1, "manifest": ".mt-agent-devkit/distribution/phase2/bundle/deployment.json"}}}
        self.urls = []
        self.adaptations = {"AGENTS.md": "# Fixture\n**Mode:** github\n**Devkit source:** https://github.com/fixture/devkit\n", ".mt-agent-devkit/context/Project_Priming.md": "# Actual project context\n", ".mt-agent-devkit/context/Document_Index.md": "# Actual index\n"}

    def acquire(self, url):
        self.urls.append(url)
        base = "https://raw.githubusercontent.com/fixture/devkit/" + self.commit + "/"
        if not url.startswith(base): raise AssertionError("un-pinned artifact read")
        relative = url.removeprefix(base)
        if relative == "changes.json": return json.dumps(self.metadata).encode()
        suffix = relative.removeprefix(".mt-agent-devkit/distribution/phase2/bundle/")
        return (self.bundle / suffix).read_bytes()

    def test_commit_pinned_real_release_apply_and_repeat(self):
        result = sync.release(self.target, "fixture/devkit", "codex", "github", "repo", self.adaptations, apply=True, acquire=self.acquire, refs=self.refs)
        self.assertEqual(result["status"], "verified")
        receipt = sync.deployment.verify(self.target)
        self.assertEqual(receipt["source"]["commit"], self.commit)
        self.assertEqual(receipt["source"]["tag"], "v0.1.51")
        self.assertTrue(all("/main/" not in url for url in self.urls))
        self.assertTrue(sync.release(self.target, "fixture/devkit", "codex", "github", "repo", self.adaptations, apply=True, acquire=self.acquire, refs=self.refs)["no_op"])
        self.assertIn(".codex/agents/memory/", (self.target / ".gitignore").read_text())
        self.assertTrue((self.target / ".mt-agent-devkit/scripts/sync.py").exists())

    def test_partial_fetch_never_changes_target(self):
        count = 0
        def fail(url):
            nonlocal count
            count += 1
            if count == 4: raise OSError("network unavailable")
            return self.acquire(url)
        with self.assertRaises(OSError): sync.release(self.target, "fixture/devkit", "codex", "github", "repo", self.adaptations, apply=True, acquire=fail, refs=self.refs)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_annotation_peels_to_immutable_commit(self):
        tag_object = "b" * 40
        refs = tag_object + " refs/tags/v0.1.51\n" + self.commit + " refs/tags/v0.1.51^{}\n"
        self.assertEqual(sync.resolve(refs), ("v0.1.51", self.commit))

    def test_old_release_without_deployment_stops_safely(self):
        self.metadata = {"0.1.51": {"modified": []}}
        with self.assertRaisesRegex(sync.deployment.Conflict, "lacks shared"):
            sync.release(self.target, "fixture/devkit", "codex", "github", "repo", self.adaptations, acquire=self.acquire, refs=self.refs)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_next_release_keeps_deployment_and_can_sync(self):
        current = json.loads((ROOT / "changes.json").read_text(encoding="utf-8"))
        opened = next_snapshot(current, "0.1.52-SNAPSHOT")
        self.assertEqual(opened["0.1.52-SNAPSHOT"]["deployment"], current["0.1.51-SNAPSHOT"]["deployment"])
        self.metadata = {"0.1.52": opened["0.1.52-SNAPSHOT"]}
        refs = self.commit + " refs/tags/v0.1.52\n"
        result = sync.release(self.target, "fixture/devkit", "codex", "github", "repo", self.adaptations, apply=True, acquire=self.acquire, refs=refs)
        self.assertEqual(result["status"], "verified")
        self.assertEqual(sync.deployment.verify(self.target)["source"]["tag"], "v0.1.52")

    def test_divergent_flat_and_nested_legacy_aliases_block(self):
        agents = self.target / ".claude/agents"
        (agents / "instructions").mkdir(parents=True)
        (agents / "developer_instructions.md").write_text("flat customization")
        (agents / "instructions/developer_instructions.md").write_text("different nested customization")
        with self.assertRaisesRegex(sync.deployment.Conflict, "divergent legacy aliases"):
            sync.migration.review_candidates(self.target, ["claude"])
        self.assertFalse((self.target/sync.deployment.RECEIPT).exists())

    def test_documented_bootstrap_blocks_unreviewed_then_preserves_custom_legacy_rule(self):
        agents = self.target / ".claude/agents"
        (agents / "rules").mkdir(parents=True)
        custom = agents / "rules/Clean_Code_Rules.md"
        custom.write_text("# Custom rule\nKeep project decisions.\n")
        (agents / "devkit_version.txt").write_text("0.1.48")
        bound = {"claude": {"PROVIDER_ROOT": ".claude", "RUNTIME_ROOT": ".claude/agents", "COMMAND_ROOT": ".claude/agents"}}
        adaptations = dict(self.adaptations)
        adaptations["CLAUDE.md"] = adaptations.pop("AGENTS.md")
        inputs = self.root / "adaptations.json"
        bindings = self.root / "bindings.json"
        resolutions = self.root / "resolutions.json"
        inputs.write_text(json.dumps(adaptations))
        bindings.write_text(json.dumps(bound))
        output = self.root / "plan.json"
        arguments = ["bootstrap.py", "--repo", "fixture/devkit", "--tag", "v0.1.51", "--commit", self.commit, "--target", str(self.target), "--mode", "github", "--profile", "repo", "--bindings", str(bindings), "--adaptations", str(inputs), "--output", str(output), "--resolutions", str(resolutions), "--apply"]
        def acquired(repo, tag, commit, directory):
            shutil.copytree(self.bundle, directory, dirs_exist_ok=True)
            source = {"kind": "release", "tag": tag, "commit": commit, "snapshot_version": None, "manifest_sha256": sync.deployment.digest((Path(directory)/"deployment.json").read_bytes())}
            (Path(directory)/"source.json").write_text(json.dumps(source))
            return source
        resolutions.write_text("{}")
        with patch.object(sys, "argv", arguments), patch.object(bootstrap, "acquire_bundle", acquired):
            self.assertEqual(bootstrap.main(), 2)
        self.assertFalse((self.target / sync.deployment.RECEIPT).exists())
        self.assertIn("Keep project decisions", custom.read_text())
        adaptations[".mt-agent-devkit/rules/Clean_Code_Rules.md"] = custom.read_text()
        inputs.write_text(json.dumps(adaptations))
        decisions = {custom.relative_to(self.target).as_posix(): {"before_sha256": sync.deployment.digest(custom.read_bytes()), "after_sha256": None, "reason": "Reviewed custom rule transfer"}, ".claude/agents/devkit_version.txt": {"before_sha256": sync.deployment.digest(b"0.1.48"), "after_sha256": sync.deployment.digest(b"0.1.51\n"), "reason": "Final compatibility stamp"}}
        resolutions.write_text(json.dumps(decisions))
        run = subprocess.run
        def quiet(command, **kwargs):
            if "bundle" in command: kwargs["stdout"] = subprocess.DEVNULL
            return run(command, **kwargs)
        with patch.object(sys, "argv", arguments), patch.object(bootstrap, "acquire_bundle", acquired), patch.object(bootstrap.subprocess, "run", quiet):
            self.assertEqual(bootstrap.main(), 0)
        self.assertFalse(custom.exists())
        self.assertIn("Keep project decisions", (self.target/".mt-agent-devkit/rules/Clean_Code_Rules.md").read_text())


if __name__ == "__main__": unittest.main()
