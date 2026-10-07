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


def run_root(provider: str, run_id: str) -> str:
    import re
    if provider not in ("claude", "antigravity", "codex"):
        raise ValueError("unknown provider")
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("unsafe runtime identity")
    return f".{provider}/agents/runtime/runs/{run_id}"


def runtime_root(provider: str, run_id: str, story_id: str) -> str:
    import re
    if not isinstance(story_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", story_id):
        raise ValueError("unsafe story identity")
    return f"{run_root(provider, run_id)}/{story_id}"


def command_root(provider: str, run_id: str, command: str) -> str:
    import re
    if not isinstance(command, str) or not re.fullmatch(r"[a-z][a-z0-9-]*", command):
        raise ValueError("unsafe command identity")
    return f"{run_root(provider, run_id)}/commands/{command}"


def record_sprint_story(index: dict | None, provider: str, run_id: str, story_id: str) -> dict:
    """Build a run-level pointer index; per-story pipeline state remains its owner."""
    root = runtime_root(provider, run_id, story_id)
    if index is None:
        index = {"provider": provider, "run_id": run_id, "current_story": None, "stories": []}
    if not isinstance(index, dict) or index.get("provider") != provider or index.get("run_id") != run_id:
        raise ValueError("sprint index belongs to another provider/run")
    if not isinstance(index.get("stories"), list) or not all(isinstance(item, dict) for item in index["stories"]):
        raise ValueError("sprint story pointers are missing or malformed")
    stories = [dict(item) for item in index["stories"]]
    seen = set()
    for item in stories:
        expected = runtime_root(provider, run_id, item.get("story_id"))
        if item.get("runtime_root") != expected:
            raise ValueError("recorded story root does not match its provider/run identity")
        if item["story_id"] in seen:
            raise ValueError("duplicate story pointer makes resume ambiguous")
        seen.add(item["story_id"])
    if story_id not in [item["story_id"] for item in stories]:
        stories.append({"story_id": story_id, "runtime_root": root})
    return dict(index, current_story=story_id, stories=stories)


def sprint_story_roots(index: dict, provider: str, run_id: str, resume: bool = False) -> list[str]:
    if not isinstance(index, dict) or index.get("provider") != provider or index.get("run_id") != run_id:
        raise ValueError("sprint index belongs to another provider/run")
    current = index.get("current_story")
    if not current or not isinstance(index.get("stories"), list) or not any(isinstance(item, dict) and item.get("story_id") == current for item in index["stories"]):
        raise ValueError("current story has no recorded state pointer; recovery required")
    validated = record_sprint_story(index, provider, run_id, current)
    roots = [item["runtime_root"] for item in validated["stories"]
             if not resume or item["story_id"] == index["current_story"]]
    return roots


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
