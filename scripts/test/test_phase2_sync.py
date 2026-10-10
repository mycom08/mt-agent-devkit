"""Actual offline release acquisition against a commit-frozen artifact tree."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import shutil
import subprocess
import os

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".mt-agent-devkit/distribution/phase2"))
import lifecycle
import migration
import deployment
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
        self.assertEqual(opened["0.1.52-SNAPSHOT"]["deployment"], next(iter(current.values()))["deployment"])
        self.metadata = {"0.1.52": opened["0.1.52-SNAPSHOT"]}
        refs = self.commit + " refs/tags/v0.1.52\n"
        result = sync.release(self.target, "fixture/devkit", "codex", "github", "repo", self.adaptations, apply=True, acquire=self.acquire, refs=refs)
        self.assertEqual(result["status"], "verified")
        self.assertEqual(sync.deployment.verify(self.target)["source"]["tag"], "v0.1.52")

    def legacy(self, provider, version, text=None, bridge=False):
        agents = self.target / ("."+provider) / "agents"
        (agents/"rules").mkdir(parents=True, exist_ok=True)
        (agents/"rules/Clean_Code_Rules.md").write_text(text or "# Rules\nRead ."+provider+"/agents/memory/Developer_Memory.md\n")
        (agents/"devkit_version.txt").write_text(version)
        native = "CLAUDE.md" if provider == "claude" else "AGENTS.md"
        (self.target/native).write_text("# Project customizations\n**Mode:** github\n")
        memory = agents/"memory/Developer_Memory.md"
        memory.parent.mkdir(exist_ok=True); memory.write_bytes(b"keep private runtime\r\n")
        if bridge:
            (agents/"workflows").mkdir(exist_ok=True)
            content = (ROOT/".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md").read_text(encoding="utf-8-sig")
            for token, value in (("AGENT_DIR_PREFIX", "."+provider), ("ROOT_FILE", native), ("AGENT_CLI_NAME", "Claude Code" if provider == "claude" else "Antigravity")):
                content = content.replace("{{"+token+"}}", value)
            (agents/"workflows/Sync_Devkit_Workflow.md").write_text(content, encoding="utf-8")

    def snapshot(self):
        return {p.relative_to(self.target).as_posix(): p.read_bytes() for p in self.target.rglob("*") if p.is_file()}

    def test_bridge_stamp_requires_exact_authenticated_compatible_bridge(self):
        self.legacy("claude", "0.1.51", bridge=True)
        report, _ = migration.review_candidates(self.target, ["claude"], self.bundle/"deployment.json")
        self.assertTrue(report["providers"]["claude"]["compatible_bridge"])
        bridge = self.target/".claude/agents/workflows/Sync_Devkit_Workflow.md"
        bridge.write_text(bridge.read_text(encoding="utf-8")+"# incompatible edit\n", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(deployment.Conflict, "unknown older layout") as error:
            migration.review_candidates(self.target, ["claude"], self.bundle/"deployment.json")
        self.assertIn("claude", error.exception.inventory["providers"])
        self.assertEqual(before, self.snapshot())
        bridge.unlink()
        with self.assertRaisesRegex(deployment.Conflict, "unknown older layout"):
            migration.review_candidates(self.target, ["claude"], self.bundle/"deployment.json")

    def test_unknown_stamp_and_tampered_provenance_fail_closed(self):
        self.legacy("claude", "9.9.9", bridge=True)
        with self.assertRaisesRegex(deployment.Conflict, "unknown older layout"):
            migration.inventory(self.target, ["claude"], self.bundle/"deployment.json")
        (self.target/".claude/agents/devkit_version.txt").write_text("0.1.51")
        (self.bundle/"assets/bridge_provenance.json").write_text('{"versions":["0.1.51"],"bridges":{}}')
        with self.assertRaisesRegex(deployment.Conflict, "provenance asset identity"):
            migration.inventory(self.target, ["claude"], self.bundle/"deployment.json")

    def test_equivalent_substitutions_and_mixed_versions_require_explicit_review(self):
        self.legacy("claude", "0.1.49")
        self.legacy("antigravity", "0.1.50")
        report, candidates = migration.review_candidates(self.target, ["claude", "antigravity"])
        self.assertEqual(report["versions"], ["0.1.49", "0.1.50"])
        rule = candidates[".mt-agent-devkit/rules/Clean_Code_Rules.md"]
        self.assertTrue(rule["equivalent"])
        self.assertIsNone(rule["bytes"])
        self.assertEqual(len(rule["variants"]), 2)
        for engine in (ROOT/".mt-agent-devkit/distribution/phase2/migration.py", self.bundle/"assets/migration.py"):
            run = subprocess.run([sys.executable, str(engine), "--target", ".", "--manifest", str(self.bundle/"deployment.json"), "--provider", "claude", "--provider", "antigravity"], cwd=self.target, capture_output=True, encoding="utf-8")
            self.assertEqual(run.returncode, 0, run.stderr)
            reported = json.loads(run.stdout)["candidates"][".mt-agent-devkit/rules/Clean_Code_Rules.md"]
            self.assertTrue(reported["equivalent"])
            self.assertIsNone(reported["proposed_text_for_review"])
            self.assertEqual(len(reported["variants"]), 2)
        for variant in rule["variants"]:
            self.assertEqual(variant["bytes"], (self.target/variant["path"]).read_bytes())
        bound = deployment.inspect(self.target)["providers"]
        before = self.snapshot()
        with self.assertRaisesRegex(deployment.Conflict, "review legacy content"):
            lifecycle.prepare(self.target, bound, "github", {}, manifest_path=self.bundle/"deployment.json")
        self.assertEqual(before, self.snapshot())
        with self.assertRaisesRegex(deployment.Conflict, "bind every"):
            lifecycle.prepare(self.target, {"claude":bound["claude"]}, "github", {}, manifest_path=self.bundle/"deployment.json")

    def test_divergent_content_report_and_reviewed_multi_provider_apply_preserve_runtime(self):
        self.legacy("claude", "0.1.49", "# Rules\nKeep team A.\n")
        self.legacy("antigravity", "0.1.50", "# Rules\nKeep team B.\n")
        before = self.snapshot()
        _, candidates = migration.review_candidates(self.target, ["claude", "antigravity"])
        rule = candidates[".mt-agent-devkit/rules/Clean_Code_Rules.md"]
        self.assertFalse(rule["equivalent"])
        self.assertIsNone(rule["bytes"]); self.assertIsNone(rule["normalized_bytes"])
        adaptations = {"CLAUDE.md": "# Project customizations\n**Mode:** github\n", "AGENTS.md":"# Project customizations\n**Mode:** github\n", ".mt-agent-devkit/context/Project_Priming.md":"# Context\n", ".mt-agent-devkit/context/Document_Index.md":"# Index\n", ".mt-agent-devkit/rules/Clean_Code_Rules.md":"# Rules\nKeep team A.\nKeep team B.\n"}
        bound = deployment.inspect(self.target)["providers"]
        adaptations, resolutions = lifecycle.prepare(self.target, bound, "github", adaptations, manifest_path=self.bundle/"deployment.json")
        source = {"kind":"release", "tag":"v0.1.51", "commit":self.commit, "snapshot_version":None, "manifest_sha256":deployment.digest((self.bundle/"deployment.json").read_bytes())}
        manifest = deployment.load(self.bundle/"deployment.json")
        for native in ("CLAUDE.md", "AGENTS.md"):
            asset = next(a for a in manifest["assets"] if a["id"] == "root_repo")
            after = deployment.managed_sections(adaptations[native], deployment.substituted((self.bundle/asset["path"]).read_text(), {"MODE":"github"}))
            resolutions[native] = {"before_sha256":deployment.digest(before[native]), "after_sha256":deployment.digest(after.encode()), "reason":"Reviewed project entrypoint transfer"}
        for provider in bound:
            stamp = "."+provider+"/agents/devkit_version.txt"
            resolutions[stamp] = {"before_sha256":deployment.digest(before[stamp]), "after_sha256":deployment.digest(b"0.1.51\n"), "reason":"Reviewed final compatibility stamp"}
            path = "."+provider+"/agents/rules/Clean_Code_Rules.md"
            resolutions[path] = {"before_sha256":deployment.digest(before[path]), "after_sha256":None, "reason":"Reviewed union of both custom rules"}
        plan = deployment.plan(self.target, self.bundle/"deployment.json", source, "github", "repo", bound, adaptations, resolutions)
        self.assertEqual(before, self.snapshot())
        deployment.apply(self.target, plan)
        self.assertEqual((self.target/".mt-agent-devkit/rules/Clean_Code_Rules.md").read_text(), adaptations[".mt-agent-devkit/rules/Clean_Code_Rules.md"])
        for provider in bound:
            memory = "."+provider+"/agents/memory/Developer_Memory.md"
            self.assertEqual((self.target/memory).read_bytes(), before[memory])
            self.assertFalse((self.target/("."+provider+"/agents/rules/Clean_Code_Rules.md")).exists())
        self.assertTrue(list(self.target.glob(".*/agents/tmp/devkit-migrations/*/journal.json")))
        deployment.verify(self.target)

    def test_relative_target_inventory_inspection_and_plan_equal_absolute(self):
        self.legacy("claude", "0.1.49")
        bound = deployment.inspect(self.target)["providers"]
        absolute = migration.review_candidates(self.target, ["claude"])
        inspected = deployment.inspect(self.target)
        old = Path.cwd()
        try:
            os.chdir(self.target)
            self.assertEqual(migration.review_candidates(".", ["claude"]), absolute)
            self.assertEqual(deployment.inspect("."), inspected)
            adaptations = {"CLAUDE.md":"# Project customizations\n**Mode:** github\n", ".mt-agent-devkit/context/Project_Priming.md":"# Context\n", ".mt-agent-devkit/context/Document_Index.md":"# Index\n", ".mt-agent-devkit/rules/Clean_Code_Rules.md":"# Reviewed rule\n"}
            source = {"kind":"release", "tag":"v0.1.51", "commit":self.commit, "snapshot_version":None, "manifest_sha256":deployment.digest((self.bundle/"deployment.json").read_bytes())}
            manifest = deployment.load(self.bundle/"deployment.json")
            asset = next(a for a in manifest["assets"] if a["id"] == "root_repo")
            after = deployment.managed_sections(adaptations["CLAUDE.md"], deployment.substituted((self.bundle/asset["path"]).read_text(encoding="utf-8"), {"MODE":"github"}))
            resolutions = {"CLAUDE.md":{"before_sha256":deployment.digest((self.target/"CLAUDE.md").read_bytes()), "after_sha256":deployment.digest(after.encode()), "reason":"Reviewed entrypoint"}, ".claude/agents/devkit_version.txt":{"before_sha256":deployment.digest(b"0.1.49"), "after_sha256":deployment.digest(b"0.1.51\n"), "reason":"Reviewed stamp"}}
            adaptations, resolutions = lifecycle.prepare(".", bound, "github", adaptations, resolutions, self.bundle/"deployment.json")
            legacy_path = ".claude/agents/rules/Clean_Code_Rules.md"
            resolutions[legacy_path] = {"before_sha256":deployment.digest((self.target/legacy_path).read_bytes()), "after_sha256":None, "reason":"Reviewed shared rule transfer"}
            # Compare the exact serialized read-only plan, including fingerprints.
            a = deployment.plan(".", self.bundle/"deployment.json", source, "github", "repo", bound, adaptations, resolutions)
            b = deployment.plan(self.target, self.bundle/"deployment.json", source, "github", "repo", bound, adaptations, resolutions)
            self.assertEqual(a, b)
            deployment.apply(".", a)
            deployment.verify(".")
        finally:
            os.chdir(old)

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
