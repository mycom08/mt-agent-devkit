"""Actual offline release acquisition against a commit-frozen artifact tree."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".mt-agent-devkit/distribution/phase2"))
import build_bundle
import sync


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


if __name__ == "__main__": unittest.main()
