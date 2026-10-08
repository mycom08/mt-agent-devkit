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

ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / ".mt-agent-devkit/distribution/phase2" / (name + ".py"))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


d, builder, resolver = module("deployment"), module("build_bundle"), module("provider_context")


class BundleTests(unittest.TestCase):
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
                            self.assertFalse((target / ("AGENTS.md" if provider == "claude" else "CLAUDE.md")).exists())
                            if profile == "repo":
                                self.assertTrue((target / ".mt-agent-devkit/rules/Agent_Common_Bootstrap.md").exists())
                                self.assertTrue((target / ".mt-agent-devkit/workflows/Start_Story_Workflow.md").exists())
                            else:
                                self.assertFalse((target / ".mt-agent-devkit/rules").exists())
                                self.assertFalse((target / ".mt-agent-devkit/instructions").exists())
                                self.assertTrue((target / ".mt-agent-devkit/workflows/Sync_Devkit_Project_Workflow.md").exists())
                            if provider == "codex":
                                tools = {"collaboration.spawn_agent", "collaboration.followup_task", "collaboration.send_message", "collaboration.wait_agent"}
                                selected = resolver.select_provider(target, tools, "codex")
                                self.assertEqual(selected["bindings"]["RUNTIME_ROOT"], ".codex/agents")

    def test_ambiguous_or_missing_provider_blocks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with self.assertRaises(ValueError): resolver.select_provider(root, set())

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
