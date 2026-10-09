"""Target provider selection: explicit live tools plus preserved path bindings."""
import json
from pathlib import Path

PROVIDERS = ("claude", "antigravity", "codex")
OPERATIONS = ("spawn", "resume", "message", "completion")


def select_provider(target, available_tools, declared=None, manifests=None):
    target = Path(target)
    candidates = {}
    for provider in PROVIDERS:
        config = target / ("." + provider) / "harness"
        if not (config / "capabilities.json").is_file():
            continue
        manifest = (manifests or {}).get(provider, json.loads((config / "capabilities.json").read_text()))
        operations = manifest.get("operations", {})
        if not isinstance(operations, dict):
            raise ValueError("provider operations must be an object")
        if all(isinstance(operations.get(key), str) and operations[key] in available_tools for key in OPERATIONS):
            candidates[provider] = operations
    if declared is None:
        if len(candidates) != 1:
            raise ValueError("declare one capable provider; neutral priming remains available")
        declared = next(iter(candidates))
    if declared not in candidates:
        raise ValueError("provider lacks observed available tools")
    config = target / ("." + declared) / "harness"
    bound = json.loads((config / "state-paths.json").read_text())
    if set(bound) != {"PROVIDER_ROOT", "RUNTIME_ROOT", "COMMAND_ROOT"} or bound["PROVIDER_ROOT"] != "." + declared:
        raise ValueError("invalid provider binding")
    for field in ("RUNTIME_ROOT", "COMMAND_ROOT"):
        value = bound[field]
        if not value.startswith("." + declared + "/") or ".." in value.split("/") or "\\" in value:
            raise ValueError("foreign runtime binding")
        path = target / value
        if not path.resolve().is_relative_to(target.resolve()) or any(component.exists() and (component.is_symlink() or bool(getattr(component.stat(), "st_file_attributes", 0) & 0x400)) for component in (path, *path.parents)):
            raise ValueError("unsafe runtime binding")
    return {"provider": declared, "bindings": bound, "operations": candidates[declared], "adapter": "." + declared + "/harness/Provider_Adapter.md", "verification": "tool identity only; native behavior evidence separate"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".")
    parser.add_argument("--tools", required=True, help="JSON list of actual enabled tool identities")
    parser.add_argument("--provider", choices=PROVIDERS)
    parser.add_argument("--capabilities", help="JSON provider manifests verified against the active runtime")
    args = parser.parse_args()
    try:
        tools = json.loads(Path(args.tools).read_text(encoding="utf-8-sig"))
        if not isinstance(tools, list) or not all(isinstance(t, str) for t in tools):
            raise ValueError("tools must be an explicit JSON string list")
        manifests = json.loads(Path(args.capabilities).read_text(encoding="utf-8-sig")) if args.capabilities else None
        if manifests is not None and (not isinstance(manifests, dict) or set(manifests) - set(PROVIDERS)):
            raise ValueError("capability manifests must name known providers")
        print(json.dumps(select_provider(args.target, set(tools), args.provider, manifests)))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, "BLOCKED: " + str(exc) + "\n")


if __name__ == "__main__": raise SystemExit(main())
