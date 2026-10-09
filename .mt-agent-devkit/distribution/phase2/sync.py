#!/usr/bin/env python3
"""Pinned release bundle acquisition and deployment; no /main payload reads."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from urllib.request import urlopen

import deployment
import migration
from lifecycle import prepare


def resolve(refs):
    tags = {}
    peeled = {}
    for line in refs.splitlines():
        sha, ref = line.split()
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise deployment.Conflict("invalid release identity")
        if ref.endswith("^{}"):
            peeled[ref[:-3]] = sha
        elif re.fullmatch(r"refs/tags/v\d+\.\d+\.\d+", ref):
            tags[ref] = sha
    if not tags:
        raise deployment.Conflict("no semver release tag")
    ref = max(tags, key=lambda ref: tuple(map(int, ref.split("v")[-1].split("."))))
    return ref.removeprefix("refs/tags/"), peeled.get(ref, tags[ref])


def fetch(url):
    with urlopen(url, timeout=30) as response:
        return response.read()


def release(target, repo, provider, mode, profile, adaptations, resolutions=None, apply=False, acquire=fetch, refs=None):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise deployment.Conflict("expected GitHub owner/repository")
    if refs is None:
        refs = subprocess.check_output(["git", "ls-remote", "--tags", "https://github.com/" + repo + ".git"], timeout=30).decode()
    tag, commit = resolve(refs)
    base = "https://raw.githubusercontent.com/" + repo + "/" + commit + "/"
    metadata = json.loads(acquire(base + "changes.json"))
    entry = metadata.get(tag[1:])
    if not isinstance(entry, dict) or "deployment" not in entry:
        raise deployment.Conflict("release lacks shared migration artifact; legacy-safe update only")
    declaration = entry["deployment"]
    deployment.shape(declaration, ("schema_version", "manifest"))
    if declaration["schema_version"] != 1:
        raise deployment.Conflict("unsupported deployment declaration")
    relative = declaration["manifest"]
    deployment.safe(Path.cwd(), relative)
    manifest_bytes = acquire(base + relative)
    manifest = json.loads(manifest_bytes)
    with tempfile.TemporaryDirectory() as directory:
        bundle = Path(directory)
        manifest_path = bundle / "deployment.json"
        manifest_path.write_bytes(manifest_bytes)
        remote_folder = str(PurePosixPath(relative).parent) + "/"
        # All required assets are downloaded and hashed before target mutation.
        for asset in manifest["assets"]:
            destination = deployment.safe(bundle, asset["path"])
            content = acquire(base + remote_folder + asset["path"])
            if deployment.digest(content) != asset["sha256"] or len(content) != asset["bytes"]:
                raise deployment.Conflict("release asset integrity failure")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
        target = Path(target)
        previous = deployment.inspect(target)["receipt"]
        bound = dict(previous["providers"]) if previous else {}
        bound.setdefault(provider, {"PROVIDER_ROOT": "." + provider, "RUNTIME_ROOT": "." + provider + "/agents", "COMMAND_ROOT": "." + provider + "/agents"})
        adaptations, resolutions = prepare(target, bound, mode, adaptations, resolutions)
        source = {"kind": "release", "tag": tag, "commit": commit, "snapshot_version": None, "manifest_sha256": deployment.digest(manifest_bytes)}
        value = deployment.plan(target, manifest_path, source, mode, profile, bound, adaptations, resolutions)
        return deployment.apply(target, value) if apply else value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--provider", choices=sorted(deployment.PROVIDERS), required=True)
    parser.add_argument("--mode", choices=("github", "strict"), required=True)
    parser.add_argument("--profile", choices=("repo", "project_root"), default="repo")
    parser.add_argument("--adaptations", required=True)
    parser.add_argument("--resolutions")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = release(args.target, args.repo, args.provider, args.mode, args.profile, deployment.load(args.adaptations), deployment.load(args.resolutions) if args.resolutions else None, args.apply)
        if args.output: deployment.jsonwrite(Path(args.output), result)
        print(json.dumps(result))
        return 0
    except deployment.Conflict as exc:
        parser.exit(2, str(exc) + "\n")


if __name__ == "__main__": raise SystemExit(main())
