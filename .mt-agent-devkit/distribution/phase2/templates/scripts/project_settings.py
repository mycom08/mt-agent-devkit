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

`agent_models` overrides the model and effort per agent role or model policy:

    {"agent_models": {"Developer": {"model": "sonnet", "effort": "high"},
                      "closure": {"model": "haiku"}}}

Keys are roles (`Developer`, `Technical Lead`, `QA`, `Product Owner`,
`Business Analyst`, `UI/UX Designer`) or model policies (`implementation`,
`design-review`, `standard`, `closure`); each value has an optional string
`model` and an optional string `effort`. Names match exactly, case-sensitive.
For a spawn the file tier merges per field and the role's field wins over the
policy's. A non-object entry or a non-string value gives no override for that
entry, and an unknown role, policy or field key is ignored; each is reported on
stderr, never guessed. The wider precedence is: explicit user instruction, role
override, policy override, adapter policy, workflow default (`precedence`); the
user-instruction and adapter-policy tiers are supplied by the orchestrator, never
read here. The orchestrator resolves once at workflow start and pins the result.

Usage:
  python .mt-agent-devkit/scripts/project_settings.py po_execution [--root .]
  python .mt-agent-devkit/scripts/project_settings.py agent_models --role "<Role>" --policy <policy> [--root .]
    prints one JSON object of the set fields; {} means no override
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
AGENT_ROLES = ("Developer", "Technical Lead", "QA", "Product Owner", "Business Analyst", "UI/UX Designer")
MODEL_POLICIES = ("implementation", "design-review", "standard", "closure")
OVERRIDE_FIELDS = ("model", "effort")


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


def _entry_override(name: str, entry: object) -> tuple[dict, list[str]]:
    """Validate one role or policy entry: all of it applies, or none of it does."""
    if not isinstance(entry, dict):
        return {}, [f"agent_models.{name} is not an object in {SETTINGS_PATH}; no override"]
    reports = [f"unknown field {json.dumps(key)[:60]} in agent_models.{name}; ignored" for key in entry if key not in OVERRIDE_FIELDS]
    override = {}
    for field in OVERRIDE_FIELDS:
        if field not in entry:
            continue
        value = entry[field]
        if not isinstance(value, str) or not value.strip():
            return {}, [f"agent_models.{name}.{field} is not a non-empty string in {SETTINGS_PATH}; no override"]
        override[field] = value
    return override, reports


def resolve_agent_models(root: Path, role: str | None = None, policy: str | None = None) -> tuple[dict, list[str]]:
    """Return the file tier for a spawn, role over policy per field, plus report lines."""
    settings, report = load(root)
    if report:
        return {}, [report]
    block = settings.get("agent_models")
    if block is None:
        return {}, []
    if not isinstance(block, dict):
        return {}, [f"agent_models is not an object in {SETTINGS_PATH}; no override"]
    known = AGENT_ROLES + MODEL_POLICIES
    reports = [f"unknown agent_models key {json.dumps(key)[:60]} in {SETTINGS_PATH}; ignored" for key in block if key not in known]
    tiers = {}
    for kind, name, names in (("role", role, AGENT_ROLES), ("policy", policy, MODEL_POLICIES)):
        if name is None:
            continue
        if name not in names:
            reports.append(f"unknown {kind} {json.dumps(name)[:60]}; no {kind} override")
        elif name in block:
            tiers[kind], found = _entry_override(name, block[name])
            reports.extend(found)
    return precedence(**tiers), reports


def precedence(user=None, role=None, policy=None, adapter=None, workflow=None) -> dict:
    """Merge the five tiers per field: user instruction, role, policy, adapter policy, workflow default."""
    merged = {}
    for tier in (user, role, policy, adapter, workflow):
        for field in OVERRIDE_FIELDS:
            if field not in merged and isinstance(tier, dict) and field in tier:
                merged[field] = tier[field]
    return merged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("key", choices=sorted([*DEFAULTS, "agent_models"]))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--role", help="agent_models only: the exact role name")
    parser.add_argument("--policy", help="agent_models only: the exact model policy name")
    args = parser.parse_args(argv)
    if args.key == "agent_models":
        override, reports = resolve_agent_models(args.root, args.role, args.policy)
        for line in reports:
            print("project_settings: " + line, file=sys.stderr)
        print(json.dumps(override, sort_keys=True))
        return 0
    if args.role or args.policy:
        parser.error("--role and --policy apply to agent_models only")
    value, report = resolve(args.root, args.key)
    if report:
        print("project_settings: " + report, file=sys.stderr)
    print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
