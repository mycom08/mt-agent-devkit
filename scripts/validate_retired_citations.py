"""Reject citations of retired rule files (ST-000288, extended in ST-000290 and ST-000309).

The PO rule files below were folded into the `po-*` skills. Any bare-filename,
path or section citation of them is a stale route. The corpus is the internal
harness (both registry layouts route the PO through the skills since ST-000289)
plus, since their retirement in targets (ST-000290), the Phase 2 templates and
every bundle asset. The deployment engine's full-path gate stays as a second net.

The Developer rule files and `Clean_Code_Rules.md` are retired in the internal
harness only (ST-000309): the Phase 2 templates, bundle assets, the registry's
`layouts.target` alternatives and its target `role_sources` keys (ST-000310, which
route those alternatives to the shipped skills) still name them until ST-000311
extends the check.
History mentions on `**Version:**`/`**Previous:**` lines are not citations.
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
INTERNAL_RETIRED = ("Developer_Rules_Bootstrap", "Developer_Rules_Read_On_Demand", "Story_Standard_Dev", "Clean_Code_Rules")
INTERNAL_CITATION = re.compile(r"(?<![A-Za-z0-9_])(?:" + "|".join(INTERNAL_RETIRED) + r")(?:\.md)?(?![A-Za-z0-9_])")
INTERNAL_SHORT_CITATION = re.compile(r"\bDev(?:eloper)? (?:Rules )?(?:Bootstrap|On-Demand|Read[ _]On[ _]Demand)(?:\.md)?\s*§")
HISTORY = re.compile(r"^\s*\*\*(?:Version|Previous):\*\*")
REGISTRY = ".mt-agent-devkit/contracts/read-routing.json"
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


def strip_target_layouts(value, parent=None):
    """Drop `layouts.target` alternatives and target `role_sources` maps: both name the old target files until ST-000311."""
    if isinstance(value, dict):
        if parent == "role_sources":
            return {role: {k: v for k, v in layouts.items() if k != "target"} if isinstance(layouts, dict) else layouts
                    for role, layouts in value.items()}
        return {key: strip_target_layouts({k: v for k, v in item.items() if k != "target"} if key == "layouts" and isinstance(item, dict) else item, key)
                for key, item in value.items()}
    if isinstance(value, list):
        return [strip_target_layouts(item) for item in value]
    return value


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
    shipped = distribution(root)
    for relative in corpus(root):
        text = (root / relative).read_text(encoding="utf-8")
        errors.extend(scan(relative, text, (CITATION, SHORT_CITATION)))
        if relative in shipped:
            continue  # Target-layer files keep the Developer files until ST-000311.
        if relative == REGISTRY:
            text = json.dumps(strip_target_layouts(json.loads(text)), indent=2)
        errors.extend(scan(relative, text, (INTERNAL_CITATION, INTERNAL_SHORT_CITATION)))
    return errors


if __name__ == "__main__":
    found = findings()
    for finding in found:
        print(f"[ERROR] {finding}")
    if not found:
        print("No citations of retired rule files in the internal corpus, Phase 2 templates or bundle assets.")
    sys.exit(bool(found))
