#!/usr/bin/env python3
"""Resolve project settings from `.mt-agent-devkit/project_settings.json`.

The file is project-owned: `init` creates it with the defaults below and `sync`
never overwrites it. The top-level orchestrator resolves `po_execution` once at
workflow start and pins the result as `**PO Execution:**` in the pipeline state;
a resumed run uses its pinned value, never a re-read.

`po_execution` decides who performs Product Owner activities:

- `subagent` (default): a spawned Product Owner agent, as before.
- `orchestrator`: the top-level orchestrator performs eligible PO activities
  inline, loading the same `po-*` skills, and owns the PO record and memory for
  that activity. Accepted trade-off: one actor then both merges and records
  acceptance. That is acceptable only because the per-AC evidence producer stays
  independent (QA, or a spawned PO when QA is the implementer), Plan Sprint
  always spawns a PO, and every scope change after Stage 1 starts (defer, split
  or any AC body edit) goes to the user. Opt in knowingly.

An absent file or key resolves to `subagent`. An unrecognised value (or an
unreadable file) also resolves to `subagent` and is reported once; the value is
never guessed.

Usage:
  python .mt-agent-devkit/scripts/project_settings.py po_execution [--root .]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

SETTINGS_PATH = ".mt-agent-devkit/project_settings.json"
PO_EXECUTION_VALUES = ("subagent", "orchestrator")
DEFAULTS = {"po_execution": "subagent"}
ALLOWED = {"po_execution": PO_EXECUTION_VALUES}


def load(root: Path) -> tuple[dict, str | None]:
    """Return the settings object and a report for an unreadable file (or None)."""
    path = Path(root) / SETTINGS_PATH
    if not path.is_file():
        return {}, None
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, f"{SETTINGS_PATH} is unreadable ({type(exc).__name__}); using defaults"
    if not isinstance(value, dict):
        return {}, f"{SETTINGS_PATH} is not a JSON object; using defaults"
    return value, None


def resolve(root: Path, key: str) -> tuple[str, str | None]:
    """Resolve one setting to an accepted value, plus at most one report line."""
    if key not in DEFAULTS:
        raise KeyError(key)
    settings, report = load(root)
    if report:
        return DEFAULTS[key], report
    if key not in settings:
        return DEFAULTS[key], None
    value = settings[key]
    if value not in ALLOWED[key]:
        shown = json.dumps(value)[:60]
        return DEFAULTS[key], f"unrecognised {key} value {shown} in {SETTINGS_PATH}; using {DEFAULTS[key]}"
    return value, None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("key", choices=sorted(DEFAULTS))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    value, report = resolve(args.root, args.key)
    if report:
        print("project_settings: " + report, file=sys.stderr)
    print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
