"""Conservative legacy inventory and explicit reviewed shared-content mapping."""
from pathlib import Path
import json
import re

import deployment


SUPPORTED = {"0.1.48", "0.1.49", "0.1.50"}


def provenance(manifest_path=None):
    """Read bridge identities only from the same authenticated bundle as engine."""
    if manifest_path is None:
        home = Path(__file__).absolute().parent
        manifest_path = home.parent / "deployment.json" if home.name == "assets" else home / "bundle/deployment.json"
    manifest_path = Path(manifest_path)
    if not manifest_path.is_file():
        return {"versions": [], "bridges": {}}
    manifest = deployment.load(manifest_path)
    assets = [item for item in manifest["assets"] if item["id"] == "bridge_provenance.json"]
    if len(assets) != 1:
        return {"versions": [], "bridges": {}}
    asset = assets[0]
    content = deployment.safe(manifest_path.parent, asset["path"]).read_bytes()
    if len(content) != asset["bytes"] or deployment.digest(content) != asset["sha256"]:
        raise deployment.Conflict("bridge provenance asset identity mismatch")
    value = json.loads(content)
    deployment.shape(value, ("versions", "bridges"))
    return value


def bridge_digest(content):
    # Legacy Windows clients may change only text line endings during writes.
    return deployment.digest(content.decode("utf-8-sig").replace("\r\n", "\n").encode())


def normalized(content, provider):
    """Comparison text only: original bytes remain the review/backup evidence."""
    text = content.decode("utf-8-sig").replace("\r\n", "\n")
    prefix = "." + provider
    text = re.sub(r"(?<![\w.])" + re.escape(prefix) + r"(?=/|\b)", "{{AGENT_DIR_PREFIX}}", text)
    root = "CLAUDE.md" if provider == "claude" else "AGENTS.md"
    text = re.sub(r"(?<![\w/])" + re.escape(root) + r"(?![\w])", "{{ROOT_FILE}}", text)
    cli = {"claude": "Claude Code", "antigravity": "Antigravity", "codex": "Codex"}[provider]
    text = re.sub(r"\b" + re.escape(cli) + r"\b", "{{AGENT_CLI_NAME}}", text)
    return text.encode()


def inventory(target, providers, manifest_path=None):
    target = Path(target).absolute()
    identities = provenance(manifest_path)
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
        bridge_matches = []
        for logical, relative in content.items():
            allowed = identities["bridges"].get(provider, {}).get(logical, [])
            if allowed:
                bridge_matches.append(bridge_digest(deployment.safe(target, relative).read_bytes()) in allowed)
        bridge = bool(bridge_matches) and all(bridge_matches)
        found[provider] = {"version": version, "stamp_missing": not stamp.exists(), "files": content, "compatible_bridge": bridge}
    if len(modes) > 1:
        raise deployment.Conflict("mixed legacy modes")
    unsupported = {item["version"] for item in found.values() if item["version"] and item["version"] not in SUPPORTED and not (item["version"] in identities["versions"] and item["compatible_bridge"])}
    if unsupported:
        exc = deployment.Conflict("unknown older layout: safe inventory only; version " + ",".join(sorted(unsupported)))
        exc.inventory = {"providers": found, "mode": next(iter(modes), None), "versions": sorted(versions)}
        raise exc
    return {"providers": found, "mode": next(iter(modes), None), "versions": sorted(versions), "certification": "recognized hints only; receipt still required"}


def review_candidates(target, providers, manifest_path=None):
    """Return exact candidate paths and bytes for review; never writes/retires."""
    target = Path(target).absolute()
    report = inventory(target, providers, manifest_path)
    candidates = {}
    for provider, installation in report["providers"].items():
        for logical, relative in installation["files"].items():
            if logical.startswith("scripts/"):
                continue
            proposed = ".mt-agent-devkit/" + logical
            content = deployment.safe(target, relative).read_bytes()
            candidate = candidates.setdefault(proposed, {"legacy_paths": [], "variants": []})
            candidate["legacy_paths"].append(relative)
            candidate["variants"].append({"provider": provider, "version": installation["version"], "path": relative, "bytes": content, "sha256": deployment.digest(content), "normalized_sha256": deployment.digest(normalized(content, provider))})
    for candidate in candidates.values():
        variants = candidate["variants"]
        equivalent = len({item["normalized_sha256"] for item in variants}) == 1
        candidate["equivalent"] = equivalent
        candidate["review_required"] = True
        candidate["bytes"] = variants[0]["bytes"] if len({item["sha256"] for item in variants}) == 1 else None
        candidate["normalized_bytes"] = normalized(variants[0]["bytes"], variants[0]["provider"]) if equivalent else None
    return report, candidates


def candidate_report(candidates):
    result = {}
    for path, value in candidates.items():
        variants = []
        for item in value["variants"]:
            record = {key: item[key] for key in ("provider", "version", "path", "sha256", "normalized_sha256")}
            record["original_text"] = item["bytes"].decode("utf-8-sig")
            variants.append(record)
        result[path] = {
            "legacy_paths": value["legacy_paths"],
            "equivalent": value["equivalent"],
            "review_required": True,
            "proposed_text_for_review": value["bytes"].decode("utf-8-sig") if value["bytes"] is not None else None,
            "normalized_text_for_review": value["normalized_bytes"].decode() if value["normalized_bytes"] is not None else None,
            "variants": variants,
        }
    return result


def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--provider", action="append", choices=sorted(deployment.PROVIDERS), required=True)
    parser.add_argument("--manifest", help="Pinned bundle manifest authenticating compatible bridge identities")
    args = parser.parse_args()
    try:
        report, candidates = review_candidates(args.target, args.provider, args.manifest)
        print(json.dumps({"inventory": report, "candidates": candidate_report(candidates)}, ensure_ascii=True, indent=2))
        return 0
    except deployment.Conflict as exc:
        if hasattr(exc, "inventory"):
            print(json.dumps({"inventory": exc.inventory, "conflict": str(exc)}, indent=2))
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__": raise SystemExit(main())
