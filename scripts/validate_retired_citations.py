"""Reject citations of retired rule files (ST-000288, extended in ST-000290).

The PO rule files below were folded into the `po-*` skills. Any bare-filename,
path or section citation of them is a stale route. The corpus is the internal
harness (both registry layouts route the PO through the skills since ST-000289)
plus, since their retirement in targets (ST-000290), the Phase 2 templates and
every bundle asset. The deployment engine's full-path gate stays as a second net.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RETIRED = ("Product_Owner_Rules_Bootstrap", "Product_Owner_Rules_Read_On_Demand", "Story_Standard_PO")
# A retired stem as a whole filename token (with or without `.md`); `_template`
# legacy names are different files and do not match.
CITATION = re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(RETIRED) + r")(?:\.md)?(?![A-Za-z0-9_])")
# Section citations by the retired files' short names, e.g. "PO Bootstrap §11a".
SHORT_CITATION = re.compile(r"\bPO (?:Rules )?(?:Bootstrap|On-Demand|Read[ _]On[ _]Demand)(?:\.md)?\s*§")
SUFFIXES = (".md", ".json", ".py", ".sh", ".ps1")
LEDGER = ".mt-agent-devkit/contracts/migration-inventory.json"  # Records the retirements themselves.
PHASE2 = ".mt-agent-devkit/distribution/phase2"
# Distribution files that record the target retirements themselves: the builder
# names the retired files, and the manifest lists their retirement entries.
DISTRIBUTION_LEDGERS = (PHASE2 + "/build_bundle.py", PHASE2 + "/bundle/assets/build_bundle.py", PHASE2 + "/bundle/deployment.json")
CORPUS_OWNERSHIP = ("generated-wrapper", "provider-entrypoint")


def distribution(root: Path) -> set[str]:
    """Phase 2 templates (including the shipped Sync workflow) and bundle assets."""
    phase2 = root / PHASE2
    paths = set()
    templates = phase2 / "templates"
    if templates.is_dir():
        paths.update(p.relative_to(root).as_posix() for p in templates.rglob("*") if p.is_file() and p.suffix in SUFFIXES)
    if phase2.is_dir():
        paths.update(p.relative_to(root).as_posix() for p in phase2.glob("*.md") if p.is_file())
    assets = phase2 / "bundle" / "assets"
    if assets.is_dir():
        # Asset names keep no reliable suffix (e.g. `orchestrator_shared`), so every asset is scanned.
        paths.update(p.relative_to(root).as_posix() for p in assets.iterdir() if p.is_file())
    return paths - set(DISTRIBUTION_LEDGERS)


def corpus(root: Path) -> list[str]:
    shared = root / ".mt-agent-devkit"
    paths = {p.relative_to(root).as_posix() for p in shared.rglob("*")
             if p.is_file() and p.suffix in SUFFIXES and "distribution" not in p.relative_to(shared).parts}
    paths.discard(LEDGER)
    paths.update(distribution(root))
    for entrypoint in ("CLAUDE.md", "AGENTS.md"):
        if (root / entrypoint).is_file():
            paths.add(entrypoint)
    for provider in ("claude", "antigravity", "codex"):
        for folder in ("harness", "skills"):
            base = root / f".{provider}" / folder
            if base.is_dir():
                paths.update(p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file() and p.suffix in SUFFIXES)
    inventory = root / LEDGER
    if inventory.is_file():
        for entry in json.loads(inventory.read_text(encoding="utf-8"))["files"]:
            if entry["ownership"] in CORPUS_OWNERSHIP and (root / entry["source"]).is_file():
                paths.add(entry["source"])
    return sorted(paths)


def findings(root: Path = ROOT) -> list[str]:
    errors = []
    for relative in corpus(root):
        text = (root / relative).read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), 1):
            for match in [*CITATION.finditer(line), *SHORT_CITATION.finditer(line)]:
                errors.append(f"citation of retired rule file: {relative}:{number}: {match.group().strip()}")
    return errors


if __name__ == "__main__":
    found = findings()
    for finding in found:
        print(f"[ERROR] {finding}")
    if not found:
        print("No citations of retired rule files in the internal corpus, Phase 2 templates or bundle assets.")
    sys.exit(bool(found))
