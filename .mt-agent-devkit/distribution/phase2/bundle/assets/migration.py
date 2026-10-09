"""Conservative legacy inventory and explicit reviewed shared-content mapping."""
from pathlib import Path
import re

import deployment


SUPPORTED = {"0.1.48", "0.1.49", "0.1.50"}


def inventory(target, providers):
    target = Path(target)
    found, modes, versions = {}, set(), set()
    for provider in providers:
        root = deployment.safe(target, "." + provider + "/agents")
        if not root.exists():
            continue
        entrypoint = target / ("CLAUDE.md" if provider == "claude" else "AGENTS.md")
        text = entrypoint.read_text(encoding="utf-8-sig") if entrypoint.exists() else ""
        mode = re.search(r"\*\*Mode:\*\*\s*(github|strict)\b", text)
        if mode:
            modes.add(mode[1])
        stamp = root / "devkit_version.txt"
        version = stamp.read_text().strip() if stamp.exists() else None
        if not version:
            match = re.search(r"\*\*Devkit version:\*\*\s*v?(\d+\.\d+\.\d+)", text)
            version = match[1] if match else None
        if version:
            versions.add(version)
        content = {}
        def register(logical, item):
            relative = item.relative_to(target).as_posix()
            checked = deployment.safe(target, relative)
            if logical in content and deployment.safe(target, content[logical]).read_bytes() != checked.read_bytes():
                raise deployment.Conflict("divergent legacy aliases require review: " + logical)
            content[logical] = relative
        for folder in ("rules", "workflows", "instructions", "context", "scripts"):
            directory = root / folder
            if directory.exists():
                for item in directory.iterdir():
                    checked = deployment.safe(target, item.relative_to(target).as_posix())
                    if checked.is_file(): register(folder + "/" + item.name, checked)
        for item in root.glob("*_instructions.md"):
            deployment.safe(target, item.relative_to(target).as_posix())
            register("instructions/" + item.name, item)
        for name in ("orchestrator_instructions.md", "Orchestrator_Guide.md"):
            if (root / name).exists(): register("instructions/orchestrator_instructions.md", root / name)
        found[provider] = {"version": version, "stamp_missing": not stamp.exists(), "files": content}
    if len(modes) > 1:
        raise deployment.Conflict("mixed legacy modes")
    if len(versions) > 1:
        raise deployment.Conflict("mixed legacy shared versions")
    unsupported = versions - SUPPORTED
    if unsupported:
        raise deployment.Conflict("unknown older layout: safe inventory only; version " + ",".join(sorted(unsupported)))
    return {"providers": found, "mode": next(iter(modes), None), "versions": sorted(versions), "certification": "recognized hints only; receipt still required"}


def review_candidates(target, providers):
    """Return exact candidate paths and bytes for review; never writes/retires."""
    target = Path(target)
    report = inventory(target, providers)
    candidates = {}
    for provider, installation in report["providers"].items():
        for logical, relative in installation["files"].items():
            if logical.startswith("scripts/"):
                continue
            proposed = ".mt-agent-devkit/" + logical
            content = deployment.safe(target, relative).read_bytes()
            if proposed in candidates and candidates[proposed]["bytes"] != content:
                raise deployment.Conflict("divergent provider shared content: " + proposed)
            candidates.setdefault(proposed, {"bytes": content, "legacy_paths": []})["legacy_paths"].append(relative)
    return report, candidates


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--provider", action="append", choices=sorted(deployment.PROVIDERS), required=True)
    args = parser.parse_args()
    try:
        report, candidates = review_candidates(args.target, args.provider)
        print(json.dumps({"inventory": report, "candidates": {path: {"legacy_paths": value["legacy_paths"], "before_sha256": deployment.digest(value["bytes"]), "proposed_text_for_review": value["bytes"].decode("utf-8-sig")} for path, value in candidates.items()}}, ensure_ascii=True, indent=2))
        return 0
    except deployment.Conflict as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__": raise SystemExit(main())
