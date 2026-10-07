"""Execute narrow install/legacy-upgrade contracts in disposable repositories.

This is deployment coverage, not an agent-in-the-loop sync completion claim.
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = {"check_devkit_version.ps1", "check_devkit_version.sh", "telemetry.py", "branch_preflight.py"}


def command(cwd, *args, check=True):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return result


class UpgradeDeploymentTests(unittest.TestCase):
    def test_mechanical_target_trees_match_pinned_phase1_baseline(self):
        """Relocating internal authority must not change a single scaffolded target byte."""
        base = "62349287bc9835093a02586d8658993ba8ac685b"
        bash = str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe") if os.name == "nt" else shutil.which("bash")
        with tempfile.TemporaryDirectory(dir=ROOT / "scripts/test") as folder:
            scratch = Path(folder)
            for surface in (".claude", ".antigravity"):
                suffix = ".ps1" if surface == ".antigravity" and os.name == "nt" else ".sh"
                source = f"{surface}/agents/working/scripts/scaffold_mechanical{suffix}"
                baseline = scratch / f"baseline-{surface[1:]}{suffix}"
                before = subprocess.run(("git", "show", f"{base}:{source}"), cwd=ROOT, capture_output=True, check=True).stdout
                baseline.write_bytes(before.replace(b"\r\n", b"\n"))
                current = scratch / f"current-{surface[1:]}{suffix}"
                current.write_bytes((ROOT / source).read_bytes().replace(b"\r\n", b"\n"))
                for mode in ("github", "strict"):
                    trees = []
                    for label, script in (("baseline", baseline), ("current", current)):
                        target = scratch / f"{surface[1:]}-{mode}-{label}"
                        target.mkdir()
                        if suffix == ".ps1":
                            command(ROOT, "powershell", "-NoProfile", "-File", str(script), "-DevkitRoot", str(ROOT), "-TargetProject", str(target), "-Mode", mode, "-GhSlug", "fixture/project")
                        else:
                            command(ROOT, bash, str(script), str(ROOT), str(target), mode, "fixture/project")
                        trees.append({p.relative_to(target).as_posix(): p.read_bytes() for p in target.rglob("*") if p.is_file()})
                    with self.subTest(surface=surface, mode=mode):
                        self.assertEqual(trees[0], trees[1])

    def test_both_surface_workflow_inventories_include_preflight(self):
        for surface in (".claude", ".antigravity"):
            for name in ("Init_Project_Workflow.md", "Update_Project_Workflow.md", "Build_Software_Workflow.md"):
                with self.subTest(surface=surface, workflow=name):
                    text = (ROOT / surface / "agents/workflows" / name).read_text(encoding="utf-8")
                    for line in text.splitlines():
                        if "telemetry.py" in line and ("Copy" in line or "Source:" in line or "Target:" in line or "version-check" in line or line.startswith("`check_devkit")):
                            self.assertIn("branch_preflight.py", line)
                    if name == "Init_Project_Workflow.md":
                        self.assertIn(f"{surface}/agents/memory/", text)

    def test_sync_project_scoped_plan_does_not_filter_out_scripts(self):
        text = (ROOT / ".claude/agents/templates/workflows/Sync_Devkit_Project_Workflow_template.md").read_text(encoding="utf-8")
        plan = text.split("### Update plan", 1)[0]
        for name in SCRIPTS:
            self.assertIn(f"templates/scripts/{name}", plan)
        sources = re.findall(r"\| `([^`]+_template\.md)` \|", plan)
        self.assertEqual(4, len(sources))
        for source in sources:
            self.assertTrue(source.startswith(".claude/agents/templates/"))
        for surface in (".claude", ".antigravity"):
            rendered = plan.replace("{{AGENT_DIR_PREFIX}}", surface)
            self.assertTrue(all(source in rendered for source in sources))

    def test_fresh_scaffolds_install_canonical_helpers_in_both_modes_and_surfaces(self):
        bash = str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe") if os.name == "nt" else shutil.which("bash")
        self.assertTrue(bash and Path(bash).exists(), "deployment gate requires Bash")
        with tempfile.TemporaryDirectory(dir=ROOT / "scripts/test") as folder:
            scratch = Path(folder)
            for surface in (".claude", ".antigravity"):
                source = ROOT / surface / "agents/working/scripts/scaffold_mechanical.sh" if surface == ".claude" else ROOT / surface / "agents/working/scripts/scaffold_mechanical.ps1"
                for mode in ("github", "strict"):
                    target = scratch / (surface[1:] + "-" + mode)
                    target.mkdir()
                    if surface == ".claude":
                        script = scratch / "scaffold.sh"
                        script.write_bytes(source.read_bytes().replace(b"\r\n", b"\n"))
                        command(ROOT, bash, str(script), str(ROOT), str(target), mode, "fixture/project")
                    elif os.name == "nt":
                        command(ROOT, "powershell", "-NoProfile", "-File", str(source), "-DevkitRoot", str(ROOT), "-TargetProject", str(target), "-Mode", mode, "-GhSlug", "fixture/project")
                    else:
                        # Antigravity's POSIX scaffold is the supported non-Windows installer.
                        script = scratch / "scaffold.sh"
                        script.write_bytes((ROOT / surface / "agents/working/scripts/scaffold_mechanical.sh").read_bytes().replace(b"\r\n", b"\n"))
                        command(ROOT, bash, str(script), str(ROOT), str(target), mode, "fixture/project")
                    for name in ("telemetry.py", "branch_preflight.py"):
                        self.assertEqual((ROOT / ".claude/agents/templates/scripts" / name).read_bytes(), (target / surface / "agents/scripts" / name).read_bytes())
                    command(target, "git", "init")
                    for runtime in ("memory/Developer_Memory.md", "working-record/Developer_Working_Record.md", "retros/story.md", "tmp/metrics.jsonl", "internal/audit.md"):
                        command(target, "git", "check-ignore", f"{surface}/agents/{runtime}")

    def test_legacy_github_upgrade_preserves_memory_history_and_confirmed_base(self):
        template = (ROOT / ".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md").read_text(encoding="utf-8")
        self.assertIn("Legacy runtime-state migration", template)
        self.assertIn("--auto does not authorize", template)
        self.assertIn("Base Branch", template)
        # Execute the documented script inventory and ignore block, not a guessed list.
        inventory = set(re.findall(r"templates/scripts/([a-z0-9_.]+)", template))
        self.assertEqual(SCRIPTS, inventory)
        ignore_block = re.search(r"```gitignore\n(.*?)\n```", template, re.S).group(1)
        with tempfile.TemporaryDirectory(dir=ROOT / "scripts/test") as folder:
            scratch = Path(folder)
            for surface in (".claude", ".antigravity"):
                repo, remote = scratch / surface[1:], scratch / (surface[1:] + ".git")
                repo.mkdir()
                command(repo, "git", "init", "-b", "main")
                command(repo, "git", "config", "user.name", "Fixture")
                command(repo, "git", "config", "user.email", "fixture@example.invalid")
                command(scratch, "git", "init", "--bare", str(remote))
                memory = repo / surface / "agents/memory/Developer_Memory.md"
                memory.parent.mkdir(parents=True)
                memory.write_bytes(b"retained local knowledge\n")
                (repo / ".gitignore").write_text(f"{surface}/agents/tmp/\n/custom-ignore/\n")
                story = repo / surface / "agents/tmp/legacy-story.md"
                story.parent.mkdir()
                story.write_text("**Status:** ready\n")
                (repo / "product.txt").write_text("unchanged\n")
                original_product = (repo / "product.txt").read_bytes()
                command(repo, "git", "add", ".")
                command(repo, "git", "commit", "-m", "legacy tracked memory")
                old_sha = command(repo, "git", "rev-parse", "HEAD").stdout.strip()
                command(repo, "git", "remote", "add", "origin", str(remote))
                command(repo, "git", "push", "-u", "origin", "main")
                helper = ROOT / ".claude/agents/templates/scripts/branch_preflight.py"
                args = (sys.executable, str(helper), "inspect", "--mode", "github", "--base", "main", "--story-branch", "story/ST-legacy")
                blocked = command(repo, *args, check=False)
                self.assertNotEqual(0, blocked.returncode)
                self.assertIn("runtime state", blocked.stdout)
                # User-authorized dedicated migration; no history rewrite or local deletion.
                backup = scratch / (surface[1:] + "-memory-backup")
                shutil.copyfile(memory, backup)
                command(repo, "git", "switch", "-c", "maintenance/runtime-migration")
                scripts = repo / surface / "agents/scripts"
                scripts.mkdir()
                for name in inventory:
                    shutil.copyfile(ROOT / ".claude/agents/templates/scripts" / name, scripts / name)
                with (repo / ".gitignore").open("a", encoding="utf-8") as output:
                    output.write(ignore_block.replace("{{AGENT_DIR_PREFIX}}", surface) + "\n")
                self.assertIn("/custom-ignore/", (repo / ".gitignore").read_text())
                self.assertNotIn("Base Branch", story.read_text())
                self.assertEqual(memory.relative_to(repo).as_posix(), command(repo, "git", "ls-files", str(memory.relative_to(repo))).stdout.strip())
                command(repo, "git", "rm", "--cached", "--", memory.relative_to(repo).as_posix())
                self.assertEqual(b"retained local knowledge\n", memory.read_bytes())
                command(repo, "git", "add", ".gitignore", str(scripts.relative_to(repo)))
                command(repo, "git", "commit", "-m", "authorized runtime migration")
                command(repo, "git", "switch", "main")
                command(repo, "git", "merge", "--ff-only", "maintenance/runtime-migration")
                command(repo, "git", "push", "origin", "main")
                # Base synchronization may delete its formerly tracked working file.
                if not memory.exists():
                    memory.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(backup, memory)
                self.assertEqual(backup.read_bytes(), memory.read_bytes())
                self.assertIn("retained local knowledge", command(repo, "git", "show", old_sha + ":" + memory.relative_to(repo).as_posix()).stdout)
                # PO records an operator-confirmed immutable base in the local legacy story.
                story.write_text("**Status:** ready\n**Base Branch:** main\n")
                self.assertEqual("", command(repo, "git", "status", "--porcelain").stdout.strip())
                passed = command(repo, sys.executable, str(scripts / "branch_preflight.py"), *args[2:])
                self.assertIn("Preflight: PASS", passed.stdout)
                sha = command(repo, "git", "rev-parse", "HEAD").stdout.strip()
                command(repo, sys.executable, str(scripts / "branch_preflight.py"), "create", "--mode", "github", "--base", "main", "--story-branch", "story/ST-legacy", "--expected-base-sha", sha, "--expected-remote-sha", sha)
                self.assertEqual(sha, command(repo, "git", "rev-parse", "HEAD").stdout.strip())
                self.assertEqual(b"retained local knowledge\n", memory.read_bytes())
                self.assertEqual("", command(repo, "git", "ls-files", str(memory.relative_to(repo))).stdout.strip())
                self.assertEqual(original_product, (repo / "product.txt").read_bytes())


if __name__ == "__main__":
    unittest.main()
