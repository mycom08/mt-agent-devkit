"""Static internal harness migration contract (independent from target templates)."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / ".mt-agent-devkit"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def validate(root=ROOT) -> list[str]:
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
        if entry["ownership"] == "preserved-history" or "scaffold_mechanical" in entry["source"]:
            # Normalize checkout newlines to Git bytes; no other content changes allowed.
            actual = source.read_bytes().replace(b"\r\n", b"\n")
            if hashlib.sha256(actual).hexdigest() != entry["baseline_sha256"]:
                errors.append(f"preserved history/helper changed: {entry['source']}")
    protected = [p for p in listed if p.startswith(".claude/agents/templates/") or p in ("VERSION", "version.txt", "changes.json")]
    for path in protected:
        before = subprocess.check_output(["git", "show", f"{baseline}:{path}"], cwd=root)
        if (root / path).read_bytes().replace(b"\r\n", b"\n") != before:
            errors.append(f"Phase 2/release boundary violated: {path}")
    for path in shared.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for ref in re.findall(r"\.mt-agent-devkit/[A-Za-z0-9_./-]+\.(?:md|py|json)", text):
            if not (root / ref).is_file():
                errors.append(f"dangling shared reference: {path.relative_to(root)} -> {ref}")
        if path.parent.name in ("rules", "instructions") or path.parent.name == "commands":
            if re.search(r"Bash\(gh|\bSendMessage\b|\bagentId\b|^model(?: policy)?:", text, re.M):
                errors.append(f"provider mechanics left in shared source: {path.relative_to(root)}")
            if re.search(r"\.(?:claude|antigravity|codex)/harness/Provider_Adapter", text):
                errors.append(f"shared procedure imports a fixed provider adapter: {path.relative_to(root)}")
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
    findings = validate()
    for finding in findings:
        print(f"[ERROR] {finding}")
    if not findings:
        print("Internal harness inventory, wrappers, references and preservation checks passed.")
    raise SystemExit(bool(findings))
