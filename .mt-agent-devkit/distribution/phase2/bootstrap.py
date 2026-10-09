#!/usr/bin/env python3
"""Legacy bridge bootstrap: fetch one immutable complete bundle, then plan it."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from urllib.request import urlopen


def acquire_bundle(repo, tag, commit, directory, acquire=None):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo) or not re.fullmatch(r"[0-9a-f]{40}", commit) or not re.fullmatch(r"v\d+\.\d+\.\d+", tag):
        raise ValueError("invalid pinned release identity")
    if acquire is None:
        def acquire(url):
            with urlopen(url, timeout=30) as response: return response.read()
    base = "https://raw.githubusercontent.com/" + repo + "/" + commit + "/"
    metadata = json.loads(acquire(base + "changes.json"))
    declaration = metadata.get(tag[1:], {}).get("deployment")
    if not isinstance(declaration, dict) or declaration.get("schema_version") != 1:
        raise ValueError("release lacks shared migration artifact; legacy-safe update only")
    manifest_relative = declaration["manifest"]
    if not manifest_relative.startswith(".mt-agent-devkit/distribution/phase2/") or ".." in PurePosixPath(manifest_relative).parts or "\\" in manifest_relative:
        raise ValueError("unsafe deployment manifest")
    content = acquire(base + manifest_relative)
    manifest = json.loads(content)
    if manifest["schema_version"] != 1 or manifest["layout_version"] != 2:
        raise ValueError("unsupported bridge manifest")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "deployment.json").write_bytes(content)
    names = set()
    for asset in manifest["assets"]:
        relative = asset["path"]
        if PurePosixPath(relative).is_absolute() or ".." in PurePosixPath(relative).parts or ":" in relative or "\\" in relative or relative.casefold() in names:
            raise ValueError("unsafe/duplicate bundle asset")
        names.add(relative.casefold())
        data = acquire(base + str(PurePosixPath(manifest_relative).parent) + "/" + relative)
        if hashlib.sha256(data).hexdigest() != asset["sha256"] or len(data) != asset["bytes"]:
            raise ValueError("bundle asset identity mismatch")
        destination = directory / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    source = {"kind": "release", "tag": tag, "commit": commit, "snapshot_version": None, "manifest_sha256": hashlib.sha256(content).hexdigest()}
    (directory / "source.json").write_text(json.dumps(source), encoding="utf-8")
    return source


def main():
    if sys.version_info < (3, 10): raise SystemExit("Python 3.10+ required before target writes")
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("repo", "tag", "commit", "target", "mode", "profile", "bindings", "adaptations", "output"):
        parser.add_argument("--" + field, required=True)
    parser.add_argument("--resolutions")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--apply-plan", help="Reacquire the pinned engine and apply a previously reviewed saved plan")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as folder:
        directory = Path(folder)
        identity = acquire_bundle(args.repo, args.tag, args.commit, directory)
        engine = directory / "assets/deployment.py"
        if not engine.is_file(): parser.error("bundle lacks declared deployment engine")
        if args.apply_plan:
            value = json.loads(Path(args.apply_plan).read_text(encoding="utf-8"))
            if value["source"] != identity: parser.error("saved plan differs from pinned release identity")
            return subprocess.run([sys.executable, str(engine), "apply", "--target", args.target, "--plan", args.apply_plan]).returncode
        # Acquired lifecycle uses the same candidate-review and ignore merge
        # gates as local installation; raw engine planning is not a bridge.
        lifecycle = directory / "assets/lifecycle.py"
        if not lifecycle.is_file(): parser.error("bundle lacks lifecycle review helper")
        providers = json.loads(Path(args.bindings).read_text(encoding="utf-8-sig"))
        command = [sys.executable, str(lifecycle), "bundle", "--provider", sorted(providers)[0], "--target", args.target, "--manifest", str(directory / "deployment.json"), "--source", str(directory / "source.json"), "--mode", args.mode, "--profile", args.profile, "--bindings", args.bindings, "--adaptations", args.adaptations, "--output", args.output]
        if args.resolutions: command += ["--resolutions", args.resolutions]
        result = subprocess.run(command)
        if result.returncode: return result.returncode
        if args.apply: return subprocess.run([sys.executable, str(engine), "apply", "--target", args.target, "--plan", args.output]).returncode
    return 0


if __name__ == "__main__": raise SystemExit(main())
