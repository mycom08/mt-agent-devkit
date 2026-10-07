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
            "operations": manifests[chosen]["operations"],
            "verification": "tool identity check only; behavioral evidence is separate"}


def runtime_root(provider: str, run_id: str, story_id: str) -> str:
    import re
    if provider not in ("claude", "antigravity", "codex"):
        raise ValueError("unknown provider")
    if not all(re.fullmatch(r"[A-Za-z0-9_-]+", part) for part in (run_id, story_id)):
        raise ValueError("unsafe runtime identity")
    return f".{provider}/agents/runtime/runs/{run_id}/{story_id}"


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
