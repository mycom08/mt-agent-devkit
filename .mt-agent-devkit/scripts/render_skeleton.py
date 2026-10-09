"""Render lifecycle-target bindings in shared skeleton instructions before generation.

Selected Claude, Antigravity and Codex targets use their own provider bindings.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys


def render(text: str, lifecycle_root: str) -> str:
    if lifecycle_root not in (".claude", ".antigravity", ".codex"):
        raise ValueError("An explicit supported target provider is required")
    return text.replace("{LIFECYCLE_ROOT}", lifecycle_root)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--lifecycle-root", required=True, choices=(".claude", ".antigravity", ".codex"))
    args = parser.parse_args()
    print(render(args.source.read_text(encoding="utf-8"), args.lifecycle_root), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
