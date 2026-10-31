"""Reject citations of retired rule files in the internal harness corpus (ST-000288).

The PO rule files below were folded into the `po-*` skills. Any bare-filename,
path or section citation of them in the internal corpus is a stale route. Both
registry layouts route the PO through the skills (ST-000289), so every registry
alternative is in scope. The Phase 2 distribution tree still ships the old PO
templates, unused, until their retirement (ST-000290), so it stays outside this
corpus until then.
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
CORPUS_OWNERSHIP = ("generated-wrapper", "provider-entrypoint")


def corpus(root: Path) -> list[str]:
    shared = root / ".mt-agent-devkit"
    paths = {p.relative_to(root).as_posix() for p in shared.rglob("*")
             if p.is_file() and p.suffix in SUFFIXES and "distribution" not in p.relative_to(shared).parts}
    paths.discard(LEDGER)
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
        print("No citations of retired rule files in the internal corpus.")
    sys.exit(bool(found))
