"""Render lifecycle-target bindings in shared skeleton instructions before generation.

Only legacy Claude/Antigravity target output is supported in Phase 1. The Codex
runtime must explicitly choose one of those targets; it is not the output target.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys


def render(text: str, lifecycle_root: str) -> str:
    if lifecycle_root not in (".claude", ".antigravity"):
        raise ValueError("Phase 1 requires an explicit supported lifecycle target")
    return text.replace("{LIFECYCLE_ROOT}", lifecycle_root)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--lifecycle-root", required=True, choices=(".claude", ".antigravity"))
    args = parser.parse_args()
    print(render(args.source.read_text(encoding="utf-8"), args.lifecycle_root), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
