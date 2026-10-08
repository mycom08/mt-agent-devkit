"""Target provider selection: explicit live tools plus preserved path bindings."""
import json
from pathlib import Path

PROVIDERS = ("claude", "antigravity", "codex")
OPERATIONS = ("spawn", "resume", "message", "completion")


def select_provider(target, available_tools, declared=None):
    target = Path(target)
    candidates = {}
    for provider in PROVIDERS:
        config = target / ("." + provider) / "harness"
        if not (config / "capabilities.json").is_file():
            continue
        manifest = json.loads((config / "capabilities.json").read_text())
        operations = manifest.get("operations", {})
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
        if not path.resolve().is_relative_to(target.resolve()) or path.is_symlink():
            raise ValueError("unsafe runtime binding")
    return {"provider": declared, "bindings": bound, "operations": candidates[declared], "adapter": "." + declared + "/harness/Provider_Adapter.md", "verification": "tool identity only; native behavior evidence separate"}
