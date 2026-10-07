"""Extract exactly one Markdown heading family section, resolving generated wrappers."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]


def resolve_source(path: Path) -> Path:
    manifest = ROOT / ".mt-agent-devkit/contracts/migration-inventory.json"
    if not manifest.exists():
        return path
    relative = path.resolve().relative_to(ROOT.resolve()).as_posix() if path.resolve().is_relative_to(ROOT.resolve()) else None
    for entry in json.loads(manifest.read_text())["files"]:
        if entry["source"] == relative and entry["ownership"] == "generated-wrapper":
            return ROOT / entry["destination"]
    return path


def extract(path: Path, marker: str, target: str) -> str:
    lines = resolve_source(path).read_text(encoding="utf-8").splitlines(keepends=True)
    headings = [i for i, line in enumerate(lines) if re.search(marker, line)]
    matches = [i for i in headings if re.search(target, lines[i])]
    if len(matches) != 1:
        raise ValueError(f"target matched {len(matches)} headings, expected exactly one")
    start = matches[0]
    end = next((i for i in headings if i > start), len(lines))
    return "".join(lines[start:end])


def main() -> int:
    # Markdown rules contain Unicode even when a Windows pipe defaults to cp1252.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("marker")
    parser.add_argument("target")
    args = parser.parse_args()
    try:
        print(extract(args.file, args.marker, args.target), end="")
        return 0
    except (OSError, ValueError, re.error) as exc:
        print(f"read_section: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
