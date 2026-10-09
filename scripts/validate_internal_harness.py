"""Live internal harness validation with an optional frozen migration audit."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / ".mt-agent-devkit"

FILE_REF = re.compile(r"(?:\.(?:mt-agent-devkit|claude|antigravity|codex)|\{[A-Z_]+\})/[A-Za-z0-9_./*{}<>-]+\.(?:md|py|sh|ps1|json)")
RUNTIME_BINDINGS = {"RUNTIME_ROOT", "STORY_RUNTIME_ROOT", "COMMAND_ROOT", "RUN_ROOT"}
RUNTIME_DIRECTORIES = {"tmp", "internal", "memory", "retros", "working-record", "token-trace_sprint"}


def reference_errors(text: str, source: str, root=ROOT, target_lifecycle: bool = False) -> list[str]:
    """Check shared/legacy reads and registered runtime/lifecycle bindings.

Only explicit target-output statements are exempt for legacy paths; a shared
instruction read cannot escape resolution through a broad provider allow-list.
"""
    errors = []
    for line in text.splitlines():
        for match in FILE_REF.finditer(line):
            ref = match.group()
            if ref.startswith("{"):
                binding, suffix = ref.split("}/", 1)
                binding = binding[1:]
                if target_lifecycle and binding in ("TARGET_PROJECT", "DEVKIT_RAW_BASE"):
                    continue  # Explicit target-output and release-pinned remote-fetch contracts (Phase 2).
                if binding in RUNTIME_BINDINGS:
                    if suffix.split("/", 1)[0] not in RUNTIME_DIRECTORIES or ".." in suffix.split("/"):
                        errors.append(f"invalid runtime-bound reference: {source} -> {ref}")
                elif binding in ("LIFECYCLE_ROOT", "PROVIDER_ROOT"):
                    # The selected adapter is an exact registered provider-bound read.
                    if binding == "PROVIDER_ROOT" and suffix == "harness/Provider_Adapter.md":
                        if any(not (root / f".{p}" / suffix).is_file() for p in ("claude", "antigravity", "codex")):
                            errors.append(f"dangling provider adapter reference: {source} -> {ref}")
                    # Legacy lifecycle operations exist for both Phase 1 target surfaces.
                    elif "agents/workflows/" in suffix or "agents/working/workflows/" in suffix:
                        if any(not (root / f".{p}" / suffix).is_file() for p in ("claude", "antigravity")):
                            errors.append(f"dangling lifecycle reference: {source} -> {ref}")
                    else:
                        # Emitted skeleton target paths are data, not internal reads.
                        if "/skeletons/" not in source:
                            errors.append(f"unregistered lifecycle reference: {source} -> {ref}")
                else:
                    errors.append(f"unregistered path binding: {source} -> {ref}")
                continue
            if any(token in ref for token in ("<", ">", "*", "{", "ST-XXXXXX")):
                continue  # Clearly marked examples/globs, never a concrete file read.
            if ref.startswith(".mt-agent-devkit/"):
                if target_lifecycle:
                    manifest_path = root / ".mt-agent-devkit/distribution/phase2/bundle/deployment.json"
                    if manifest_path.is_file():
                        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                        destinations = {item["destination"] for item in manifest["files"] if item["phase"] != "retirement"}
                        if ref in destinations:
                            continue  # Exact declared target destination, not a prose exemption.
                if not (root / ref).is_file():
                    errors.append(f"dangling shared reference: {source} -> {ref}")
            elif not (root / ref).is_file():
                # Retained lifecycle bodies describe files emitted into target
                # projects. Their template/shared/working/skill reads are repo
                # inputs, while agents/{context,docs,...} are explicit outputs.
                target_output = target_lifecycle and re.match(
                    r"\.(?:claude|antigravity)/(?:settings\.json$|agents/(?:orchestrator_instructions\.md$|(?:context|docs|instructions|memory|rules|scripts|retros|tmp|workflows|working-record|internal)/))", ref)
                if not target_output:
                    errors.append(f"dangling executable legacy reference: {source} -> {ref}")
    return errors


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def validate(root=ROOT, migration_preservation=False) -> list[str]:
    """Validate live structure; frozen byte checks are an opt-in migration audit."""
    errors = []
    shared = root / ".mt-agent-devkit"
    inventory = json.loads((shared / "contracts/migration-inventory.json").read_text(encoding="utf-8"))
    entries = inventory["files"]
    paths = [e["source"] for e in entries]
    if len(paths) != len(set(paths)):
        errors.append("duplicate inventory source")
    baseline = inventory["source_revision"]
    listed = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", baseline], cwd=root, text=True).splitlines()
    expected = {p for p in listed if p.startswith((".claude/agents/working/", ".antigravity/agents/working/", ".claude/agents/workflows/", ".antigravity/agents/workflows/", ".claude/skills/", ".antigravity/skills/")) or p in ("AGENTS.md", "CLAUDE.md")}
    if set(paths) != expected:
        errors.append("inventory does not account for every baseline internal file")
    wrappers = module("wrappers", shared / "scripts/generate_wrappers.py")
    for entry in entries:
        source, destination = root / entry["source"], root / entry["destination"]
        if not source.exists() or not destination.exists():
            errors.append(f"missing inventory source/destination: {entry['source']}")
            continue
        if entry["ownership"] == "generated-wrapper":
            if source.read_text(encoding="utf-8") != wrappers.render(entry):
                errors.append(f"generated wrapper drift: {entry['source']}")
            if not entry["destination"].startswith(".mt-agent-devkit/"):
                errors.append(f"wrapper outside canonical owner: {entry['source']}")
        if migration_preservation and (entry["ownership"] == "preserved-history" or "scaffold_mechanical" in entry["source"]):
            # Normalize checkout newlines to Git bytes; no other content changes allowed.
            actual = source.read_bytes().replace(b"\r\n", b"\n")
            if hashlib.sha256(actual).hexdigest() != entry["baseline_sha256"]:
                errors.append(f"preserved history/helper changed: {entry['source']}")
    protected = [p for p in listed if p.startswith(".claude/agents/templates/") or p in ("VERSION", "version.txt", "changes.json")]
    for path in protected if migration_preservation else []:
        before = subprocess.check_output(["git", "show", f"{baseline}:{path}"], cwd=root)
        if (root / path).read_bytes().replace(b"\r\n", b"\n") != before:
            errors.append(f"Phase 2/release boundary violated: {path}")
    for path in shared.rglob("*.md"):
        if "distribution" in path.relative_to(shared).parts:
            continue  # Target distribution is verified against rendered target trees by test_phase2_bundle.
        text = path.read_text(encoding="utf-8")
        errors.extend(reference_errors(text, path.relative_to(root).as_posix(), root, target_lifecycle=path.name == "Target_Project_Deployment_Workflow.md"))
        if path.parent.name in ("rules", "instructions") or path.parent.name == "commands":
            if re.search(r"Bash\(gh|\bSendMessage\b|\bagentId\b|^model(?: policy)?:", text, re.M):
                errors.append(f"provider mechanics left in shared source: {path.relative_to(root)}")
            if re.search(r"\.(?:claude|antigravity|codex)/harness/Provider_Adapter", text):
                errors.append(f"shared procedure imports a fixed provider adapter: {path.relative_to(root)}")
    # Target-layout descriptions are explicitly excluded; executable repository
    # reads and runtime bindings in retained lifecycle sources are still checked.
    for entry in entries:
        if entry["ownership"] == "phase2-exclusion" and entry["source"].endswith(".md"):
            path = root / entry["source"]
            errors.extend(reference_errors(path.read_text(encoding="utf-8"), entry["source"], root, target_lifecycle=True))
    for entrypoint in ("AGENTS.md", "CLAUDE.md"):
        text = (root / entrypoint).read_text(encoding="utf-8")
        for required in ("Provider_Contract.md", "only the selected adapter", ".mt-agent-devkit/context/Project_Priming_Bootstrap.md"):
            if required not in text:
                errors.append(f"entrypoint routing missing {required}: {entrypoint}")
    for provider in ("claude", "antigravity", "codex"):
        for name in ("Provider_Adapter.md", "capabilities.json"):
            if not (root / f".{provider}/harness/{name}").is_file():
                errors.append(f"missing provider adapter/discovery: {provider}/{name}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--migration-preservation", action="store_true",
                        help="One-shot migration audit: compare histories/templates/release files to the pinned source revision; do not use for ongoing CI.")
    args = parser.parse_args()
    findings = validate(migration_preservation=args.migration_preservation)
    for finding in findings:
        print(f"[ERROR] {finding}")
    if not findings:
        print("Internal harness inventory, wrappers and references passed (including preservation audit when requested).")
    raise SystemExit(bool(findings))
