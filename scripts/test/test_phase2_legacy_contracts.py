"""Frozen blob integrity and executable legacy helpers; not native sync proof."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "scripts/test/fixtures/phase2/legacy"
HASHES = {
    "v0.1.48": "ffec60ef03f700209a5ac7616bc592ea52fe1f3a41bb7b84f45948836d257bd7",
    "v0.1.49": "b208100ca217dab81710ac93a1ef73c0ecab7c613ee94bc5330951a7b635d2a6",
    "v0.1.50": "e7110855efac0639ef1ee581721a6259d6c8795dd4b5daf0b09ee0f3791d741d",
}
sys.path.insert(0, str(ROOT / ".mt-agent-devkit/distribution/phase2"))
import build_bundle
import deployment
import sync
import migration

BRIDGES = {
    ".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md",
    ".claude/agents/templates/workflows/Sync_Devkit_Project_Workflow_template.md",
}


def materialize(tag, destination):
    archive = FIXTURES / (tag + ".zip")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != HASHES[tag]:
        raise AssertionError("frozen archive identity mismatch")
    with zipfile.ZipFile(archive) as source:
        metadata = json.loads(source.read("frozen-release.json"))
        for entry in metadata["files"]:
            name = entry["path"]
            if name.startswith("/") or ".." in Path(name).parts:
                raise AssertionError("unsafe frozen fixture")
            content = source.read(name)
            if hashlib.sha256(content).hexdigest() != entry["sha256"]:
                raise AssertionError("frozen blob mismatch")
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return metadata


class LegacyContracts(unittest.TestCase):
    def test_targeted_alias_dedup_and_fullscan_payload_isolation(self):
        latest = {"files": sorted(BRIDGES), "new": [], "modified": sorted(BRIDGES), "deployment": {"schema_version": 1, "manifest": ".mt-agent-devkit/distribution/phase2/bundle/deployment.json"}}
        for tag in HASHES:
            with self.subTest(tag=tag), zipfile.ZipFile(FIXTURES / (tag + ".zip")) as archive:
                workflow = archive.read(".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md").decode("utf-8-sig")
                fields = ("files", "new", "modified") if "combine `files`, `new`, and `modified`" in workflow else ("files",)
                targeted = list(dict.fromkeys(path for field in fields for path in latest.get(field, [])))
                self.assertEqual(set(targeted), BRIDGES)
                self.assertEqual(len(targeted), 2)
                # Explicit template-source namespace contract, not native interpretation.
                full_scan = [p for p in archive.namelist() if p.startswith(".claude/agents/templates/")]
                self.assertTrue(BRIDGES.issubset(full_scan))
                self.assertFalse(any("distribution/phase2" in p for p in full_scan))
                for path in targeted:
                    bridge = (ROOT / path).read_bytes()
                    self.assertNotEqual(hashlib.sha256(archive.read(path)).hexdigest(), hashlib.sha256(bridge).hexdigest())
                    self.assertIn(b"BEFORE old version comparisons", bridge)
                    self.assertIn(b"bootstrap.py", bridge)
                    # The byte-identical compatible bridge may skip; stale workflow cannot.
                    checksum = hashlib.sha256(bridge).hexdigest()
                    self.assertNotEqual(checksum, hashlib.sha256(archive.read(path)).hexdigest())

    def test_two_pass_offline_mechanical_upgrade_supported_clients(self):
        """Pass1 executes documented frozen write set; pass2 real pinned sync engine.

        Markdown interpretation is deliberately not native-provider evidence.
        """
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bundle = root / "bundle"
            manifest = build_bundle.build(ROOT, bundle)
            commit = "d" * 40
            metadata = {"0.1.51": {"files": sorted(BRIDGES), "modified": sorted(BRIDGES), "deployment": {"schema_version": 1, "manifest": ".mt-agent-devkit/distribution/phase2/bundle/deployment.json"}}}
            def acquire(url):
                base = "https://raw.githubusercontent.com/fixture/devkit/" + commit + "/"
                self.assertTrue(url.startswith(base))
                relative = url[len(base):]
                if relative == "changes.json": return json.dumps(metadata).encode()
                return (bundle / relative.removeprefix(".mt-agent-devkit/distribution/phase2/bundle/")).read_bytes()
            for tag in HASHES:
                frozen = root / tag
                materialize(tag, frozen)
                for provider in ("claude", "antigravity"):
                    for mode in ("github", "strict"):
                        for missing_stamp in (False, True):
                            with self.subTest(tag=tag, provider=provider, mode=mode, missing=missing_stamp):
                                target = root / (tag + provider + mode + str(missing_stamp))
                                agents = target / ("." + provider) / "agents"
                                (agents / "workflows").mkdir(parents=True)
                                native = "CLAUDE.md" if provider == "claude" else "AGENTS.md"
                                (target / native).write_text("# Customized project\n**Mode:** " + mode + "\n", encoding="utf-8")
                                old_sync = frozen / ".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md"
                                destination = agents / "workflows/Sync_Devkit_Workflow.md"
                                destination.write_bytes(old_sync.read_bytes())
                                (agents / "developer_instructions.md").write_text("# Customized developer\nPreserve project decisions.\n", encoding="utf-8")
                                (agents / "instructions").mkdir()
                                (agents / "instructions/developer_instructions.md").write_bytes((agents / "developer_instructions.md").read_bytes())
                                (agents / "context").mkdir()
                                (agents / "context/Project_Priming.md").write_text("# Reviewed context\n", encoding="utf-8")
                                (agents / "orchestrator_instructions.md").write_text("# Legacy orchestrator\n", encoding="utf-8")
                                (agents / "scripts").mkdir()
                                (agents / "scripts/check_devkit_version.sh").write_text("legacy version notice\n", encoding="utf-8")
                                (agents / "scripts/check_devkit_version.ps1").write_text("# legacy PowerShell version notice\n", encoding="utf-8")
                                settings_path = target / ("." + provider) / "settings.json"
                                settings = {"hooks": {"SessionStart": [{"hooks": [
                                    {"type": "command", "command": "bash ." + provider + "/agents/scripts/check_devkit_version.sh"},
                                    {"type": "command", "command": "powershell -File ." + provider + "/agents/scripts/check_devkit_version.ps1"},
                                ]}]}, "custom_setting": "preserve"}
                                settings_path.write_text(json.dumps(settings), encoding="utf-8")
                                retained_native = {p: p.read_bytes() for p in (
                                    settings_path, agents / "scripts/check_devkit_version.sh", agents / "scripts/check_devkit_version.ps1")}
                                memory = agents / "memory/Developer_Memory.md"
                                memory.parent.mkdir(); memory.write_bytes(b"durable personalized memory\n")
                                counter = agents / "docs/story_counter.txt"
                                counter.parent.mkdir(); counter.write_bytes(b"47\n")
                                if not missing_stamp: (agents / "devkit_version.txt").write_text(tag[1:], encoding="utf-8")
                                before_runtime = {p: p.read_bytes() for p in (memory, counter)}
                                # First old invocation consumes frozen-client-supported alias fields.
                                fields = ("files", "new", "modified") if tag == "v0.1.50" else ("files",)
                                paths = list(dict.fromkeys(p for field in fields for p in metadata["0.1.51"].get(field, [])))
                                self.assertEqual(set(paths), BRIDGES)
                                source = ROOT / ".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md"
                                bridge = source.read_text(encoding="utf-8-sig")
                                for token, value in (("AGENT_DIR_PREFIX", "."+provider), ("ROOT_FILE", native), ("AGENT_CLI_NAME", "Claude Code" if provider == "claude" else "Antigravity")):
                                    bridge = bridge.replace("{{"+token+"}}", value)
                                destination.write_text(bridge, encoding="utf-8")
                                # Actual frozen Stage 3 finalizes the first pass at
                                # the newest release, even though layout is legacy.
                                (agents / "devkit_version.txt").write_text("0.1.51", encoding="utf-8")
                                with (target/native).open("a", encoding="utf-8") as entry:
                                    entry.write("**Devkit version:** 0.1.51\n")
                                self.assertIn(b"bootstrap.py", destination.read_bytes())
                                self.assertFalse((target / deployment.RECEIPT).exists())
                                # Second invocation reviewed transfer is explicit, not guessed by engine.
                                _, candidates = migration.review_candidates(target, [provider], bundle/"deployment.json")
                                adaptations = {p: value["bytes"].decode("utf-8-sig") for p, value in candidates.items()}
                                adaptations[".mt-agent-devkit/workflows/Sync_Devkit_Workflow.md"] = (ROOT/".mt-agent-devkit/distribution/phase2/Sync_Devkit_Workflow_template.md").read_text(encoding="utf-8")
                                adaptations.pop(".mt-agent-devkit/instructions/orchestrator_instructions.md")
                                # Review retains the canonical shared orchestrator instead
                                # of reviving obsolete routing in a legacy customization.
                                adaptations[".mt-agent-devkit/instructions/orchestrator_instructions.md"] = deployment.substituted((bundle/"assets/orchestrator_shared").read_text(), {})
                                adaptations.update({native: "# Reviewed project\n**Mode:** " + mode + "\n", ".mt-agent-devkit/context/Project_Priming.md": "# Reviewed context\n", ".mt-agent-devkit/context/Document_Index.md": "# Reviewed index\n"})
                                bound = {provider: {"PROVIDER_ROOT": "."+provider, "RUNTIME_ROOT": "."+provider+"/agents", "COMMAND_ROOT": "."+provider+"/agents"}}
                                root_asset = next(a for a in manifest["assets"] if a["id"] == "root_repo")
                                rendered_root = deployment.managed_sections(adaptations[native], deployment.substituted((bundle / root_asset["path"]).read_text(), {"MODE": mode}))
                                resolutions = {native: {"before_sha256": deployment.digest((target/native).read_bytes()), "after_sha256": deployment.digest(rendered_root.encode()), "reason": "Reviewed entrypoint switch"}}
                                if provider == "claude":
                                    settings_asset = next(a for a in manifest["assets"] if a["id"] == "claude/settings")
                                    required = deployment.substituted((bundle/settings_asset["path"]).read_text(), {"PYTHON_COMMAND": "python" if os.name == "nt" else "python3"})
                                    merged = deployment.provider_settings(settings_path.read_text(), required)
                                    resolutions[settings_path.relative_to(target).as_posix()] = {"before_sha256": deployment.digest(settings_path.read_bytes()), "after_sha256": deployment.digest(merged.encode()), "reason": "Reviewed hook transfer"}
                                resolutions[(agents/"devkit_version.txt").relative_to(target).as_posix()] = {"before_sha256": deployment.digest((agents/"devkit_version.txt").read_bytes()), "after_sha256": deployment.digest(b"0.1.51\n"), "reason": "Receipt-backed final compatibility stamp"}
                                for record in manifest["legacy_support"]["retirements"]:
                                    legacy = target / record["path"]
                                    if legacy.is_file(): resolutions[record["path"]] = {"before_sha256": deployment.digest(legacy.read_bytes()), "after_sha256": None, "reason": "Reviewed shared transfer and exact obsolete managed workflow retirement"}
                                result = sync.release(target, "fixture/devkit", provider, mode, "repo", adaptations, resolutions, True, acquire, commit+" refs/tags/v0.1.51\n")
                                self.assertEqual(result["status"], "verified")
                                self.assertEqual(deployment.verify(target)["source"]["commit"], commit)
                                self.assertFalse(destination.exists())
                                for obsolete in ("developer_instructions.md", "instructions/developer_instructions.md", "orchestrator_instructions.md", "context/Project_Priming.md"):
                                    self.assertFalse((agents/obsolete).exists(), obsolete)
                                for suffix in ("sh", "ps1"):
                                    self.assertEqual((agents/("scripts/check_devkit_version." + suffix)).exists(), provider == "antigravity")
                                if provider == "antigravity":
                                    for p, content in retained_native.items(): self.assertEqual(p.read_bytes(), content)
                                    # A repeat update must keep the settings and both hook
                                    # targets byte-for-byte, rather than merely skipping
                                    # their retirement during the first migration.
                                    repeat = sync.release(target, "fixture/devkit", provider, mode, "repo", {}, {}, True, acquire, commit+" refs/tags/v0.1.51\n")
                                    self.assertEqual(repeat["status"], "verified")
                                    for p, content in retained_native.items(): self.assertEqual(p.read_bytes(), content)
                                self.assertIn("Preserve project decisions", (target/".mt-agent-devkit/instructions/developer_instructions.md").read_text())
                                for p, content in before_runtime.items(): self.assertEqual(p.read_bytes(), content)
                                self.assertEqual((agents/"devkit_version.txt").read_text(), "0.1.51\n")

    def test_v50_legacy_sources_frozen_except_declared_bridges(self):
        with zipfile.ZipFile(FIXTURES / "v0.1.50.zip") as archive:
            for path in archive.namelist():
                if path.startswith(".claude/agents/templates/") and path not in BRIDGES:
                    # Git checkout line endings are not immutable source identity.
                    self.assertEqual(archive.read(path).decode("utf-8-sig").replace("\r\n", "\n"), (ROOT / path).read_text(encoding="utf-8-sig"))
    def test_all_release_blobs_available_offline(self):
        with tempfile.TemporaryDirectory() as folder:
            for tag in HASHES:
                metadata = materialize(tag, Path(folder) / tag)
                self.assertEqual(metadata["tag"], tag)
                self.assertGreater(len(metadata["files"]), 90)

    def test_unknown_release_object_field_is_outside_documented_file_lists(self):
        """Mechanical oracle for the explicit legacy parser field contract."""
        for tag in HASHES:
            with zipfile.ZipFile(FIXTURES / (tag + ".zip")) as archive:
                workflow = archive.read(".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md").decode("utf-8-sig")
                fields = ("files", "new", "modified") if "combine `files`, `new`, and `modified`" in workflow else ("files",)
                self.assertIn("When parsing, if the version value is an array", workflow)
                self.assertIn("all template files", workflow)
                legacy = {"files": ["one"], "new": ["two"], "modified": ["three"], "deployment": {"manifest": ".mt-agent-devkit/distribution/phase2/deployment.json"}}
                consumed = [p for field in fields for p in legacy.get(field, [])]
                self.assertEqual(consumed, ["one", "two", "three"] if tag == "v0.1.50" else ["one"])

    def test_frozen_helpers_actual_both_modes_and_surfaces(self):
        bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe" if os.name == "nt" else Path(shutil.which("bash") or "")
        self.assertTrue(bash.is_file(), "Bash required for actual frozen-helper fixture")
        with tempfile.TemporaryDirectory() as folder:
            scratch = Path(folder)
            for tag in HASHES:
                devkit = scratch / tag
                materialize(tag, devkit)
                # Deliberately place new incompatible assets outside legacy template namespace.
                isolated = devkit / ".mt-agent-devkit/distribution/phase2/incompatible.md"
                isolated.parent.mkdir(parents=True)
                isolated.write_text("SHOULD NEVER BE INSTALLED BY LEGACY HELPER")
                for provider in ("claude", "antigravity"):
                    for mode in ("github", "strict"):
                        with self.subTest(tag=tag, provider=provider, mode=mode):
                            target = scratch / (tag + provider + mode)
                            target.mkdir()
                            suffix = ".ps1" if provider == "antigravity" and os.name == "nt" else ".sh"
                            script = devkit / ("." + provider) / ("agents/working/scripts/scaffold_mechanical" + suffix)
                            command = ["powershell", "-NoProfile", "-File", str(script), "-DevkitRoot", str(devkit), "-TargetProject", str(target), "-Mode", mode, "-GhSlug", "fixture/project"] if suffix == ".ps1" else [str(bash), str(script), str(devkit), str(target), mode, "fixture/project"]
                            result = subprocess.run(command, capture_output=True, text=True)
                            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                            self.assertFalse((target / ".mt-agent-devkit").exists())
                            self.assertNotIn(b"SHOULD NEVER", b"".join(p.read_bytes() for p in target.rglob("*") if p.is_file()))
                            self.assertTrue((target / ("." + provider) / "agents/scripts/check_devkit_version.sh").exists())
                            self.assertEqual((target / ("." + provider) / "agents/scripts/branch_preflight.py").exists(), tag == "v0.1.50")


if __name__ == "__main__": unittest.main()
