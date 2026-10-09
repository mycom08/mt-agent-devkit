"""Actual generated target bundle layout and resolver contracts."""
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest
import os
import shutil
import subprocess
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / ".mt-agent-devkit/distribution/phase2" / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


d, builder, resolver = module("deployment"), module("build_bundle"), module("provider_context")


class BundleTests(unittest.TestCase):
    def test_authoritative_corpus_checks_do_not_fall_back_to_frozen_templates(self):
        from scripts import validate_templates as validator
        self.assertIn(validator.PHASE2_TEMPLATES, validator.SCAN_DIRS)
        with tempfile.TemporaryDirectory() as folder:
            corpus = Path(folder)
            source = corpus / "github/workflows/Example_template.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Example\n<!-- Shared logic: templates/shared/workflows/Start_Story_Workflow_Shared_template.md -->\nStory_Standard §4\n", encoding="utf-8")
            # Both references resolve in frozen sources, but must fail here:
            # missing Phase 2 counterparts cannot inherit frozen validity.
            with patch.object(validator, "PHASE2_TEMPLATES", corpus):
                findings = []
                validator.scan_file(source, findings)
                self.assertTrue(any("does not exist" in f[3] for f in findings))
                self.assertTrue(any("file not found or unreadable" in f[3] for f in findings))
                self.assertFalse(validator._resolve_file_ref(
                    ".claude/agents/templates/rules/Story_Standard_template.md", source))

    def test_real_bundle_six_layouts_and_minimal_root_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bundle = root / "bundle"
            builder.build(ROOT, bundle)
            manifest = bundle / "deployment.json"
            source = {"kind": "local", "tag": None, "commit": "a" * 40, "snapshot_version": "0.1.51-SNAPSHOT", "manifest_sha256": d.digest(manifest.read_bytes())}
            for provider in d.PROVIDERS:
                for mode in ("github", "strict"):
                    for profile in ("repo", "project_root"):
                        with self.subTest(provider=provider, mode=mode, profile=profile):
                            target = root / (provider + mode + profile)
                            target.mkdir()
                            bound = {provider: {"PROVIDER_ROOT": "." + provider, "RUNTIME_ROOT": "." + provider + "/agents", "COMMAND_ROOT": "." + provider + "/agents"}}
                            entrypoint = "CLAUDE.md" if provider == "claude" else "AGENTS.md"
                            adaptations = {entrypoint: "# Fixture\n\n**Mode:** " + mode + "\nRead .mt-agent-devkit/contracts/Provider_Contract.md; select explicit enabled provider tools.\n", ".mt-agent-devkit/context/Project_Priming.md": "# Fixture context\nFixed test repository.\n", ".mt-agent-devkit/context/Document_Index.md": "# Docs\n", ".gitignore": ".mt-agent-devkit-migration.lock\n"}
                            plan = d.plan(target, manifest, source, mode, profile, bound, adaptations)
                            d.apply(target, plan)
                            d.verify(target)
                            # Concrete shared reads resolve in the installed target, not in the devkit.
                            for document in (target / ".mt-agent-devkit").rglob("*.md"):
                                for line in document.read_text(encoding="utf-8").splitlines():
                                    if any(marker in line for marker in ("<repo-path>/", "<absolute-repo-path>/")):
                                        continue  # Explicit per-repository harness, not project-root read.
                                    for reference in re.findall(r"\.mt-agent-devkit/[A-Za-z0-9_./-]+\.(?:md|py|ps1|sh)", line):
                                        self.assertTrue((target/reference).is_file(), str(document.relative_to(target))+" -> "+reference)
                            self.assertTrue((target / entrypoint).exists())
                            self.assertIn("provider_context.py", (target / entrypoint).read_text())
                            self.assertIn("Provider_Contract.md", (target / entrypoint).read_text())
                            self.assertIn("Provider_Adapter.md", (target / entrypoint).read_text())
                            self.assertFalse((target / ("AGENTS.md" if provider == "claude" else "CLAUDE.md")).exists())
                            if profile == "repo":
                                self.assertTrue((target / ".mt-agent-devkit/rules/Agent_Common_Bootstrap.md").exists())
                                self.assertTrue((target / ".mt-agent-devkit/workflows/Start_Story_Workflow.md").exists())
                                self.assertNotIn("new `Agent` call", (target / ".mt-agent-devkit/instructions/orchestrator_instructions.md").read_text())
                            else:
                                self.assertFalse((target / ".mt-agent-devkit/rules").exists())
                                self.assertFalse((target / ".mt-agent-devkit/instructions").exists())
                                self.assertTrue((target / ".mt-agent-devkit/workflows/Sync_Devkit_Project_Workflow.md").exists())
                            if provider == "codex":
                                tools = {"collaboration.spawn_agent", "collaboration.followup_task", "collaboration.send_message", "collaboration.wait_agent"}
                                selected = resolver.select_provider(target, tools, "codex")
                                self.assertEqual(selected["bindings"]["RUNTIME_ROOT"], ".codex/agents")
                            if provider == "claude":
                                settings = json.loads((target / ".claude/settings.json").read_text())
                                self.assertIn("Bash(gh pr *)", settings["permissions"]["allow"])
                                self.assertIn("version_notice.py", settings["hooks"]["SessionStart"][0]["hooks"][0]["command"])
                                self.assertTrue((target / ".claude/skills/read-section/SKILL.md").is_file())
                            adapter = (target / ("." + provider) / "harness/Provider_Adapter.md").read_text()
                            self.assertNotIn("Internal Harness Adapter", adapter)
                            tools_file = root / "tools.json"
                            tools_file.write_text(json.dumps(["collaboration.spawn_agent", "collaboration.followup_task", "collaboration.send_message", "collaboration.wait_agent"]))
                            if provider == "codex":
                                result = subprocess.run([__import__("sys").executable, str(target/".mt-agent-devkit/scripts/provider_context.py"), "--target", str(target), "--tools", str(tools_file), "--provider", provider], capture_output=True, text=True)
                                self.assertEqual(result.returncode, 0, result.stderr)
                                self.assertEqual(json.loads(result.stdout)["adapter"], ".codex/harness/Provider_Adapter.md")
                            if provider == "antigravity":
                                with self.assertRaises(ValueError): resolver.select_provider(target, set(), provider)
                                mapping = {"operations": {op: "observed." + op for op in resolver.OPERATIONS}}
                                capabilities_file = root / "verified-runtime.json"
                                capabilities_file.write_text(json.dumps({provider: mapping}))
                                tools_file.write_text(json.dumps(list(mapping["operations"].values())))
                                result = subprocess.run([__import__("sys").executable, str(target/".mt-agent-devkit/scripts/provider_context.py"), "--target", str(target), "--tools", str(tools_file), "--provider", provider, "--capabilities", str(capabilities_file)], capture_output=True, text=True)
                                self.assertEqual(result.returncode, 0, result.stderr)
                                self.assertEqual(json.loads(result.stdout)["adapter"], ".antigravity/harness/Provider_Adapter.md")

    def test_ambiguous_or_missing_provider_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(ValueError): resolver.select_provider(root, set())

    def test_lifecycle_preserves_adapted_instructions_and_rules_without_resupplying(self):
        import sys
        sys.path.insert(0, str(ROOT / ".mt-agent-devkit/distribution/phase2"))
        import lifecycle
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "target"
            target.mkdir()
            inputs = {"AGENTS.md": "# Project\n", ".mt-agent-devkit/context/Project_Priming.md": "# Context\n", ".mt-agent-devkit/context/Document_Index.md": "# Index\n"}
            custom = {".mt-agent-devkit/instructions/developer_instructions.md": "# Customized developer\nKeep project choices.\n", ".mt-agent-devkit/rules/Clean_Code_Rules.md": "# Customized rules\nKeep project style.\n"}
            lifecycle.local(target, ROOT, "codex", "github", "repo", {**inputs, **custom}, apply=True)
            lifecycle.local(target, ROOT, "codex", "github", "repo", inputs, apply=True)
            for path, content in custom.items(): self.assertEqual((target/path).read_text(), content)

    def test_actual_shell_lifecycle_commands_and_idempotent_update(self):
        with tempfile.TemporaryDirectory() as folder:
            scratch = Path(folder)
            adaptations = scratch / "adaptations.json"
            adaptations.write_text(json.dumps({"AGENTS.md": "# Fixture\n\n**Mode:** github\nShared provider contract: .mt-agent-devkit/contracts/Provider_Contract.md\n", ".mt-agent-devkit/context/Project_Priming.md": "# Fixture\n", ".mt-agent-devkit/context/Document_Index.md": "# Index\n"}))
            directory = ROOT / ".mt-agent-devkit/distribution/phase2"
            shells = [["powershell", "-NoProfile", "-File", str(directory / "lifecycle.ps1")]] if os.name == "nt" else []
            bash = str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe") if os.name == "nt" else shutil.which("bash")
            if bash: shells.append([bash, str(directory / "lifecycle.sh")])
            for index, shell in enumerate(shells):
                target = scratch / ("target" + str(index))
                common = ["--target", str(target), "--devkit-root", str(ROOT), "--provider", "codex", "--mode", "github", "--adaptations", str(adaptations), "--apply"]
                result = subprocess.run(shell + ["init"] + common, capture_output=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["status"], "verified")
                memory = target / ".codex/agents/memory/Developer_Memory.md"
                memory.write_bytes(b"durable user fact\n")
                result = subprocess.run(shell + ["update"] + common, capture_output=True, encoding="utf-8")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(json.loads(result.stdout)["no_op"])
                self.assertEqual(memory.read_bytes(), b"durable user fact\n")


if __name__ == "__main__": unittest.main()
