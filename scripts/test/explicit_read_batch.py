"""Experimental P01/P02 read-only batch; not a distributed devkit capability.

One shell invocation collects a fixed dependency group. No arbitrary commands,
user-supplied paths, writes, recursive discovery or network operations exist.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path


MAX_FILE_BYTES = 4096
MAX_RESULT_BYTES = 16384
JOBS = {
    "P01": (("alpha", "notes/alpha.txt", None), ("beta", "notes/beta.txt", None),
            ("gamma", "notes/gamma.txt", None)),
    "P02": (("orbit", "data/east.txt", "ORBIT"), ("comet", "notes/west.txt", "COMET")),
}


def read_job(root: Path, job: tuple) -> dict:
    label, relative, pattern = job
    path = root / relative
    if any(part.is_symlink() for part in (path, *path.parents) if part != root.parent):
        raise ValueError("Redirected input is not allowed")
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("Expected regular in-fixture file")
    with path.open("rb") as stream:
        content = stream.read(MAX_FILE_BYTES + 1)
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Input exceeds batch bound; no truncated success")
    text = content.decode("utf-8")
    result = {"label": label, "path": relative}
    if pattern is None:
        result["content"] = text
    else:
        result["pattern"] = pattern
        result["matches"] = [{"line": number, "text": line} for number, line in
                             enumerate(text.splitlines(), 1) if pattern in line]
        if len(result["matches"]) > 32:
            raise ValueError("Search matches exceed batch bound")
    return result


def execute(case: str, root: Path) -> dict:
    if case not in JOBS:
        raise ValueError("Only fixed P01/P02 read-only groups are supported")
    root = root.resolve()
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(read_job, root, job) for job in JOBS[case]]
        results = [future.result() for future in futures]
    record = {"schema_version": 1, "case": case, "results": results}
    if len(json.dumps(record, ensure_ascii=True).encode("utf-8")) > MAX_RESULT_BYTES:
        raise ValueError("Result exceeds batch bound")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=sorted(JOBS))
    args = parser.parse_args()
    try:
        result = execute(args.case, Path.cwd())
    except (ValueError, OSError, UnicodeError):
        print(json.dumps({"case": args.case, "outcome": "incomplete", "reason": "Batch input or output contract failed"}))
        return 1
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
