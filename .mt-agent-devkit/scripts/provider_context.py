"""Resolve an internal provider from explicitly supplied available tool identities.

This checks declarations, not runtime execution. Never infer capabilities from a
directory name or an installed binary. The caller supplies its actual tool list.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = ("spawn", "resume", "message", "completion")


def select_provider(available_tools: set[str], declared: str | None = None,
                    manifests: dict | None = None) -> dict:
    if manifests is None:
        manifests = {p: json.loads((ROOT / f".{p}/harness/capabilities.json").read_text())
                     for p in ("claude", "antigravity", "codex")}
    if not isinstance(manifests, dict) or not manifests or any(p not in ("claude", "antigravity", "codex") for p in manifests):
        raise ValueError("capability manifest must name known providers")
    supported = []
    for provider, manifest in manifests.items():
        if not isinstance(manifest, dict) or not isinstance(manifest.get("operations"), dict):
            raise ValueError("each provider requires an operations object")
        operations = manifest.get("operations", {})
        if all(isinstance(operations.get(op), str) and operations[op] in available_tools for op in REQUIRED):
            supported.append(provider)
    if declared is not None:
        if declared not in manifests or declared not in supported:
            raise ValueError("declared provider lacks required available runtime tools")
        chosen = declared
    elif len(supported) == 1:
        chosen = supported[0]
    else:
        raise ValueError("workflow blocked: declare one capable provider; neutral priming remains available")
    return {"provider": chosen, "adapter": f".{chosen}/harness/Provider_Adapter.md",
            "bindings": state_bindings(chosen),
            "operations": manifests[chosen]["operations"],
            "verification": "tool identity check only; behavioral evidence is separate"}


def run_root(provider: str, run_id: str) -> str:
    """Validate execution identity; run IDs do not partition working state."""
    import re
    if provider not in ("claude", "antigravity", "codex"):
        raise ValueError("unknown provider")
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("unsafe runtime identity")
    return state_bindings(provider)["RUNTIME_ROOT"]


def state_bindings(provider: str) -> dict:
    """Load provider-owned state defaults; no state copying or path discovery."""
    if provider not in ("claude", "antigravity", "codex"):
        raise ValueError("unknown provider")
    config = json.loads((ROOT / f".{provider}/harness/state-paths.json").read_text())
    expected = {"PROVIDER_ROOT": f".{provider}",
                "RUNTIME_ROOT": f".{provider}/agents/working",
                "COMMAND_ROOT": f".{provider}/agents"}
    if config != expected:
        raise ValueError("missing or foreign provider state binding")
    return config


def validate_state_bindings(provider: str, bindings: dict) -> dict:
    """Fail closed on incomplete, unresolved or cross-provider worker packets."""
    expected = state_bindings(provider)
    if not isinstance(bindings, dict) or any(bindings.get(k) != v for k, v in expected.items()):
        raise ValueError("worker state bindings are missing or foreign")
    return expected


def runtime_root(provider: str, run_id: str, story_id: str) -> str:
    import re
    if not isinstance(story_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", story_id):
        raise ValueError("unsafe story identity")
    return run_root(provider, run_id)


def command_root(provider: str, run_id: str, command: str) -> str:
    """Existing command files share a provider root; callers guard ownership."""
    import re
    if not isinstance(command, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", command):
        raise ValueError("unsafe command identity")
    run_root(provider, run_id)
    return state_bindings(provider)["COMMAND_ROOT"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools", required=True, help="JSON file containing actual available tool names")
    parser.add_argument("--provider", choices=("claude", "antigravity", "codex"))
    parser.add_argument("--capabilities", help="JSON object of provider manifests verified against this runtime")
    args = parser.parse_args()
    try:
        tools = json.loads(Path(args.tools).read_text())
        if not isinstance(tools, list) or not all(isinstance(t, str) for t in tools):
            raise ValueError("tools must be an explicit JSON string list")
        manifests = json.loads(Path(args.capabilities).read_text()) if args.capabilities else None
        print(json.dumps(select_provider(set(tools), args.provider, manifests)))
        return 0
    except (ValueError, OSError) as exc:
        print(f"BLOCKED: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
