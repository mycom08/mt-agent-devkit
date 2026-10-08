"""Meaningful transaction/preservation tests, separate from native discovery."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / ".mt-agent-devkit/distribution/phase2/deployment.py"
spec = importlib.util.spec_from_file_location("phase2_deployment", ENGINE)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.target = self.root / "target"
        self.target.mkdir()
        self.bundle = self.root / "bundle"
        self.bundle.mkdir()
        (self.bundle / "rule.md").write_bytes(b"shared authority\n")
        (self.bundle / "wrapper.md").write_bytes(b"{{PROVIDER_ROOT}} {{RUNTIME_ROOT}}\n")
        (self.bundle / "memory.md").write_bytes(b"empty seed\n")
        self.manifest = {"schema_version": 1, "layout_version": 2, "minimum_python": "3.10", "profiles": ["repo", "project_root"], "legacy_support": {}, "assets": [], "files": []}
        for name in ("rule", "wrapper", "memory"):
            content = (self.bundle / (name + ".md")).read_bytes()
            self.manifest["assets"].append({"id": name, "path": name + ".md", "sha256": d.digest(content), "bytes": len(content), "kind": "template"})
        for name, path, owner, ownership, renderer, phase in (
            ("rule", ".mt-agent-devkit/rules/Rule.md", "shared", "managed", "copy", "content"),
            ("wrapper", "{{PROVIDER_ROOT}}/harness/Wrapper.md", "selected_provider", "managed", "tokens", "discovery"),
            ("memory", "{{RUNTIME_ROOT}}/memory/Developer_Memory.md", "selected_provider", "runtime_seed", "create_if_absent", "content"),
        ):
            self.manifest["files"].append({"id": name, "sources": [name], "destination": path, "owner": owner, "ownership": ownership, "profiles": ["repo"], "modes": ["github", "strict"], "providers": sorted(d.PROVIDERS), "renderer": renderer, "legacy_paths": [], "phase": phase, "required": True})
        self.path = self.bundle / "deployment.json"
        self.flush()

    def flush(self):
        self.path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def plan(self, provider="codex", mode="github", all_providers=False):
        bound = {p: {"PROVIDER_ROOT": "." + p, "RUNTIME_ROOT": "." + p + "/agents", "COMMAND_ROOT": "." + p + "/agents"} for p in (sorted(d.PROVIDERS) if all_providers else [provider])}
        source = {"kind": "release", "tag": "v0.1.51", "commit": "a" * 40, "snapshot_version": None, "manifest_sha256": d.digest(self.path.read_bytes())}
        return d.plan(self.target, self.path, source, mode, "repo", bound)

    def test_six_combinations_preserve_memory_and_repeat_noop(self):
        for provider in sorted(d.PROVIDERS):
            for mode in ("github", "strict"):
                with self.subTest(provider=provider, mode=mode):
                    target = self.root / (provider + mode)
                    target.mkdir()
                    self.target = target
                    memory = target / ("." + provider) / "agents/memory/Developer_Memory.md"
                    memory.parent.mkdir(parents=True)
                    memory.write_bytes(b"user facts\r\n")
                    d.apply(target, self.plan(provider, mode))
                    self.assertEqual(memory.read_bytes(), b"user facts\r\n")
                    before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
                    self.assertTrue(d.apply(target, self.plan(provider, mode))["no_op"])
                    self.assertEqual(before, {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()})

    def test_asset_tamper_stops_before_writes(self):
        (self.bundle / "rule.md").write_bytes(b"untrusted changed source")
        with self.assertRaisesRegex(d.Conflict, "asset bytes"):
            self.plan()
        self.assertEqual(list(self.target.iterdir()), [])

    def test_unknown_schema_and_fields_rejected(self):
        for field, value in (("schema_version", 2), ("execute", "unsafe")):
            original = copy.deepcopy(self.manifest)
            self.manifest[field] = value
            self.flush()
            with self.assertRaises(d.Conflict): self.plan()
            self.manifest = original

    def test_escape_and_case_collision_rejected(self):
        for destination in ("../escape.md", "C:/escape.md", "/escape.md"):
            self.manifest["files"][0]["destination"] = destination
            self.flush()
            with self.assertRaises(d.Conflict): self.plan()
        self.manifest["files"][0]["destination"] = ".mt-agent-devkit/rules/Rule.md"
        duplicate = copy.deepcopy(self.manifest["files"][0])
        duplicate["id"] = "collision"
        duplicate["destination"] = ".MT-AGENT-DEVKIT/RULES/RULE.MD"
        self.manifest["files"].append(duplicate)
        self.flush()
        with self.assertRaisesRegex(d.Conflict, "collision"): self.plan()

    def test_custom_managed_file_is_conflict(self):
        path = self.target / ".mt-agent-devkit/rules/Rule.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"custom rule")
        with self.assertRaisesRegex(d.Conflict, "unknown baseline"): self.plan()
        self.assertEqual(path.read_bytes(), b"custom rule")

    def test_runtime_change_after_plan_blocks(self):
        memory = self.target / ".codex/agents/memory/Developer_Memory.md"
        memory.parent.mkdir(parents=True)
        memory.write_bytes(b"before")
        plan = self.plan()
        memory.write_bytes(b"after")
        with self.assertRaises(d.Conflict): d.apply(self.target, plan)
        self.assertFalse((self.target / d.RECEIPT).exists())

    def test_injected_failure_resume_and_delayed_receipt(self):
        plan = self.plan()
        with self.assertRaises(OSError): d.apply(self.target, plan, "applied:0")
        self.assertFalse((self.target / d.RECEIPT).exists())
        lock = d.load(self.target / d.LOCK)
        d.recover(self.target, lock["transaction_id"])
        d.verify(self.target)
        self.assertFalse((self.target / d.LOCK).exists())

    def test_rollback_restores_existing_and_removes_new_files(self):
        d.apply(self.target, self.plan())
        before = (self.target / ".mt-agent-devkit/rules/Rule.md").read_bytes()
        receipt_before = (self.target / d.RECEIPT).read_bytes()
        (self.bundle / "rule.md").write_bytes(b"new rule\n")
        asset = self.manifest["assets"][0]
        asset.update(sha256=d.digest(b"new rule\n"), bytes=len(b"new rule\n"))
        self.flush()
        with self.assertRaises(OSError): d.apply(self.target, self.plan(), "verified")
        lock = d.load(self.target / d.LOCK)
        d.recover(self.target, lock["transaction_id"], rollback=True)
        self.assertEqual((self.target / ".mt-agent-devkit/rules/Rule.md").read_bytes(), before)
        self.assertEqual((self.target / d.RECEIPT).read_bytes(), receipt_before)

    def test_rollback_rejects_intervening_edit(self):
        with self.assertRaises(OSError): d.apply(self.target, self.plan(), "verified")
        rule = self.target / ".mt-agent-devkit/rules/Rule.md"
        rule.write_bytes(b"human changed after interruption")
        lock = d.load(self.target / d.LOCK)
        with self.assertRaisesRegex(d.Conflict, "intervening edit"):
            d.recover(self.target, lock["transaction_id"], rollback=True)
        self.assertEqual(rule.read_bytes(), b"human changed after interruption")

    def test_multiple_providers_have_one_rule_and_separate_wrappers(self):
        d.apply(self.target, self.plan(all_providers=True))
        self.assertEqual(len(list((self.target / ".mt-agent-devkit/rules").glob("*.md"))), 1)
        for provider in d.PROVIDERS:
            self.assertIn(("." + provider).encode(), (self.target / ("." + provider) / "harness/Wrapper.md").read_bytes())

    def test_mode_switch_and_active_pipeline_block(self):
        d.apply(self.target, self.plan())
        with self.assertRaisesRegex(d.Conflict, "switching"): self.plan(mode="strict")
        state = self.target / ".codex/agents/tmp/sprint_pipeline_state.md"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text("**Stage:** 1\n")
        with self.assertRaisesRegex(d.Conflict, "nonterminal"): self.plan()

    def test_cli_dead_owner_recovery(self):
        plan = self.plan()
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(plan))
        code = "import importlib.util,json; s=importlib.util.spec_from_file_location('d',r'" + str(ENGINE) + "');d=importlib.util.module_from_spec(s);s.loader.exec_module(d);d.apply(r'" + str(self.target) + "',json.load(open(r'" + str(plan_path) + "')),'backed_up')"
        child = subprocess.run([sys.executable, "-c", code], capture_output=True)
        self.assertNotEqual(child.returncode, 0)
        lock = d.load(self.target / d.LOCK)
        d.recover(self.target, lock["transaction_id"])
        d.verify(self.target)

    def test_shared_mode_assembly_keeps_real_appendix(self):
        (self.bundle / "rule.md").write_bytes(b"<!-- header -->\n<!-- SHARED-START -->\nshared\n<!-- SHARED-END -->\n")
        (self.bundle / "wrapper.md").write_bytes(b"<!-- Shared logic: source -->\nstrict appendix {{MODE}}\n")
        for asset in self.manifest["assets"]:
            content = (self.bundle / asset["path"]).read_bytes()
            asset.update(sha256=d.digest(content), bytes=len(content))
        self.manifest["files"] = [self.manifest["files"][0]]
        self.manifest["files"][0].update(sources=["rule", "wrapper"], renderer="shared_mode")
        self.flush()
        d.apply(self.target, self.plan(mode="strict"))
        self.assertEqual((self.target / ".mt-agent-devkit/rules/Rule.md").read_text(), "shared\n\n---\n\nstrict appendix strict\n")

    def test_exact_resolution_allows_reviewed_custom_replacement(self):
        path = self.target / ".mt-agent-devkit/rules/Rule.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"custom baseline")
        bound = {"codex": {"PROVIDER_ROOT": ".codex", "RUNTIME_ROOT": ".codex/agents", "COMMAND_ROOT": ".codex/agents"}}
        source = {"kind": "local", "tag": None, "commit": "b" * 40, "snapshot_version": "0.1.51-SNAPSHOT", "manifest_sha256": d.digest(self.path.read_bytes())}
        resolution = {".mt-agent-devkit/rules/Rule.md": {"before_sha256": d.digest(b"custom baseline"), "after_sha256": d.digest(b"shared authority\n"), "reason": "reviewed custom replacement"}}
        plan = d.plan(self.target, self.path, source, "github", "repo", bound, resolutions=resolution)
        d.apply(self.target, plan)
        self.assertEqual(d.verify(self.target)["source"]["kind"], "local")

    def test_add_provider_preserves_first_provider_files(self):
        d.apply(self.target, self.plan(provider="claude"))
        wrapper = self.target / ".claude/harness/Wrapper.md"
        before = wrapper.read_bytes()
        d.apply(self.target, self.plan(all_providers=True))
        self.assertEqual(wrapper.read_bytes(), before)
        self.assertEqual(len(d.verify(self.target)["providers"]), 3)

    def test_receipt_tamper_after_failure_blocks_rollback(self):
        with self.assertRaises(OSError): d.apply(self.target, self.plan(), "receipt")
        (self.target / d.RECEIPT).write_bytes(b"user receipt edit")
        lock = d.load(self.target / d.LOCK)
        with self.assertRaisesRegex(d.Conflict, "receipt edit"):
            d.recover(self.target, lock["transaction_id"], rollback=True)

    def retirement_plan(self, path=".codex/agents/rules/Old.md", ownership="managed"):
        destination = self.target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"legacy managed rule")
        item = copy.deepcopy(self.manifest["files"][0])
        item.update(id="old", sources=[], destination=path, ownership=ownership, phase="retirement")
        self.manifest["files"].append(item)
        self.manifest["legacy_support"]["retirements"] = [{"logical_id": "old", "path": path, "after_verified_ids": ["rule"]}]
        self.flush()
        bound = {"codex": {"PROVIDER_ROOT": ".codex", "RUNTIME_ROOT": ".codex/agents", "COMMAND_ROOT": ".codex/agents"}}
        source = {"kind": "release", "tag": "v0.1.51", "commit": "a" * 40, "snapshot_version": None, "manifest_sha256": d.digest(self.path.read_bytes())}
        resolutions = {path: {"before_sha256": d.digest(b"legacy managed rule"), "after_sha256": None, "reason": "reviewed exact obsolete managed file"}}
        return d.plan(self.target, self.path, source, "github", "repo", bound, resolutions=resolutions)

    def test_surviving_reference_to_retired_path_blocks_serialized_apply(self):
        value = self.retirement_plan()
        op = next(op for op in value["operations"] if op["operation_id"] == "rule")
        content = b"Read .codex/agents/rules/Old.md before work\n"
        op["content_hex"], op["after_sha256"] = content.hex(), d.digest(content)
        value.pop("plan_id")
        value["plan_id"] = d.digest(d.canonical(value))
        with self.assertRaisesRegex(d.Conflict, "references retired"):
            d.apply(self.target, value)
        self.assertFalse((self.target/d.LOCK).exists())

    def test_final_stamp_waits_for_content_verification_and_rolls_back(self):
        item = copy.deepcopy(self.manifest["files"][1])
        item.update(id="stamp", destination="{{RUNTIME_ROOT}}/devkit_version.txt", phase="compatibility", ownership="provider_config")
        self.manifest["files"].append(item); self.flush()
        value = self.plan()
        with self.assertRaises(OSError): d.apply(self.target, value, "before_compatibility")
        self.assertTrue((self.target/".mt-agent-devkit/rules/Rule.md").is_file())
        self.assertFalse((self.target/".codex/agents/devkit_version.txt").exists())
        self.assertFalse((self.target/d.RECEIPT).exists())
        lock = d.load(self.target/d.LOCK)
        d.recover(self.target, lock["transaction_id"], rollback=True)
        self.assertFalse((self.target/".mt-agent-devkit/rules/Rule.md").exists())

    def test_retirement_verifies_survivor_and_rollback_restores_legacy(self):
        plan = self.retirement_plan()
        with self.assertRaises(OSError): d.apply(self.target, plan, "verified")
        self.assertFalse((self.target / ".codex/agents/rules/Old.md").exists())
        self.assertTrue((self.target / ".mt-agent-devkit/rules/Rule.md").exists())
        lock = d.load(self.target / d.LOCK)
        d.recover(self.target, lock["transaction_id"], rollback=True)
        self.assertEqual((self.target / ".codex/agents/rules/Old.md").read_bytes(), b"legacy managed rule")

    def test_reviewed_retirement_cannot_override_protected_ownership(self):
        for ownership in ("project_owned", "project_adapted", "runtime_seed", "provider_config"):
            with self.subTest(ownership=ownership):
                self.setUp()
                with self.assertRaisesRegex(d.Conflict, "forbidden"):
                    self.retirement_plan(ownership=ownership)

    def test_runtime_retirement_rejected_in_manifest_and_serialized_plan(self):
        with self.assertRaisesRegex(d.Conflict, "forbidden"):
            self.retirement_plan(path=".codex/agents/memory/Custom_Memory.md")
        self.setUp()
        value = self.retirement_plan()
        operation = next(op for op in value["operations"] if op["action"] == "retire")
        operation["path"] = ".codex/agents/docs/custom.md"
        identity = dict(value)
        identity.pop("plan_id")
        value["plan_id"] = d.digest(d.canonical(identity))
        with self.assertRaisesRegex(d.Conflict, "runtime retirement"):
            d.apply(self.target, value)
        self.assertFalse((self.target / d.LOCK).exists())


if __name__ == "__main__": unittest.main()
