"""PermissionRequest handler for a disposable installed-workflow target only."""
from __future__ import annotations

import json
from pathlib import Path
import sys


def cleanup_command(target: Path) -> str:
    return 'rm -- ' + ' '.join('"' + (target.resolve() / name).as_posix() + '"' for name in (
        '.claude/agents/retros/ST-000211_retro.md', '.claude/agents/tmp/pipeline_state.md'))


def init_cleanup_command(target: Path) -> str:
    return 'rm -- "' + (target.resolve() / '.claude/agents/tmp/init_project_state.md').as_posix() + '"'


def decision(event: dict, target: Path) -> str:
    if not isinstance(event, dict) or not isinstance(event.get("tool_input", {}), dict):
        return "deny"
    if event.get("hook_event_name") != "PermissionRequest":
        return "deny"
    root = target.resolve()
    protected = root / ".claude"
    # A redirected .claude directory must not enlarge the authorized boundary.
    if protected.resolve() != protected:
        return "deny"
    if event.get("tool_name") == "Bash":
        command = event.get("tool_input", {}).get("command")
        if command == init_cleanup_command(root):
            paths = [root / '.claude/agents/tmp/init_project_state.md']
        elif command == cleanup_command(root):
            paths = [root / name for name in ('.claude/agents/retros/ST-000211_retro.md',
                                             '.claude/agents/tmp/pipeline_state.md')]
        else:
            return "deny"
        return "allow" if all(path.resolve() == path and not path.is_dir() for path in paths) else "deny"
    if event.get("tool_name") not in ("Write", "Edit"):
        return "deny"
    raw = event.get("tool_input", {}).get("file_path")
    if not isinstance(raw, str) or not raw:
        return "deny"
    path = Path(raw)
    if not path.is_absolute():
        path = Path(event.get("cwd", str(root))) / path
    resolved = path.resolve()
    return "allow" if resolved.is_relative_to(protected) and resolved != protected else "deny"


def main() -> None:
    try:
        behavior = decision(json.load(sys.stdin), Path(sys.argv[1]))
    except (ValueError, TypeError, KeyError, IndexError, OSError):
        behavior = "deny"
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PermissionRequest", "decision": {"behavior": behavior}}}))


if __name__ == "__main__":
    main()
