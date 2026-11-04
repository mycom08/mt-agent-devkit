"""Reject citations of retired rule files (ST-000288, extended in ST-000290, ST-000309 and ST-000311).

The PO rule files were folded into the `po-*` skills, the Developer rule files and
`Clean_Code_Rules.md` into the `dev-*` and common skills. Any bare-filename, path or
section citation of them is a stale route. The corpus is the internal harness
(every registry layout routes both roles through the skills) plus, since their
retirement in targets (ST-000290 PO, ST-000311 Developer), the Phase 2 templates
and every bundle asset. The deployment engine's full-path gate stays as a second net.
History mentions on `**Version:**`/`**Previous:**` lines are not citations.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
RETIRED = ("Product_Owner_Rules_Bootstrap", "Product_Owner_Rules_Read_On_Demand", "Story_Standard_PO",
           "Developer_Rules_Bootstrap", "Developer_Rules_Read_On_Demand", "Story_Standard_Dev", "Clean_Code_Rules")
# A retired stem as a whole filename token (with or without `.md`); `_template`
# legacy names are different files and do not match.
CITATION = re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(RETIRED) + r")(?:\.md)?(?![A-Za-z0-9_])")
# Section citations by the retired files' short names, e.g. "PO Bootstrap §11a", "Dev On-Demand §15".
SHORT_CITATION = re.compile(r"\b(?:PO|Dev(?:eloper)?) (?:Rules )?(?:Bootstrap|On-Demand|Read[ _]On[ _]Demand)(?:\.md)?\s*§")
HISTORY = re.compile(r"^\s*\*\*(?:Version|Previous):\*\*")
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


def scan(relative: str, text: str, patterns) -> list[str]:
    errors = []
    for number, line in enumerate(text.splitlines(), 1):
        if HISTORY.match(line):
            continue
        for pattern in patterns:
            for match in pattern.finditer(line):
                errors.append(f"citation of retired rule file: {relative}:{number}: {match.group().strip()}")
    return errors


def findings(root: Path = ROOT) -> list[str]:
    errors = []
    for relative in corpus(root):
        errors.extend(scan(relative, (root / relative).read_text(encoding="utf-8"), (CITATION, SHORT_CITATION)))
    return errors


if __name__ == "__main__":
    found = findings()
    for finding in found:
        print(f"[ERROR] {finding}")
    if not found:
        print("No citations of retired rule files in the internal corpus, Phase 2 templates or bundle assets.")
    sys.exit(bool(found))
