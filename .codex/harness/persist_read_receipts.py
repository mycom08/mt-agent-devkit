"""Persist real attestations and canonically rebuild an internal Codex manifest.

The caller owns actual returned-read evidence and must read Shell Safety before
invoking this mutation. No read coverage is inferred or attested here.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "codex_canonical_read_manifest", ROOT / ".mt-agent-devkit/scripts/read_manifest.py")
routing = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routing)


def persist(root, manifest_source, receipts_source):
    root = Path(root).resolve()
    manifest_path = routing.safe(root, manifest_source)
    receipts_path = routing.safe(root, receipts_source)
    if manifest_path == receipts_path:
        raise routing.Blocked("manifest and attestations must be separate files")
    original = manifest_path.read_bytes()
    manifest = json.loads(original.decode("utf-8-sig"))
    request = manifest.get("request", {})
    if request.get("provider") != "codex" or request.get("layout") != "internal":
        raise routing.Blocked("only internal Codex manifests are supported")
    bindings = routing.bindings(root, request)
    runtime = routing.safe(root, bindings["RUNTIME_ROOT"]).resolve()
    if any(not path.resolve().is_relative_to(runtime) for path in (manifest_path, receipts_path)):
        raise routing.Blocked("manifest and attestations must stay within bound Codex runtime")
    canonical = routing.validate(root, manifest)
    incoming = routing.load(receipts_path)
    if not isinstance(incoming, list) or not incoming:
        raise routing.Blocked("nonempty array of actual attestations required")
    entries = canonical["reads"] + canonical["omitted"]
    receipts = list(canonical["receipts"])
    fields = {"source", "coverage", "content_sha256", "routing_revision",
              "provider", "session", "returned_coverage", "truncation_recovered"}
    for index, receipt in enumerate(incoming):
        if (not isinstance(receipt, dict) or set(receipt) != fields
                or not any(routing.receipt_matches(receipt, entry, request) for entry in entries)):
            raise routing.Blocked(f"attestation {index} has stale or mismatched session/source/coverage")
        if receipt not in receipts:
            receipts.append(receipt)
    rebuilt = routing.build(root, request, receipts)
    routing.validate(root, rebuilt)
    data = (json.dumps(rebuilt, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    if data != original:
        # Stage the replacement beside its destination; failures preserve the old file.
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=manifest_path.parent, prefix=".receipts-",
                                             suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            if manifest_path.read_bytes() != original:
                raise routing.Blocked("manifest changed during persistence; reload the owning session state")
            os.replace(temporary, manifest_path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return {"status": "PASS", "receipts": len(receipts),
            "reads": len(rebuilt["reads"]), "omitted": len(rebuilt["omitted"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--receipts", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(persist(ROOT, args.manifest, args.receipts)))
        return 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print("BLOCKED: " + str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
