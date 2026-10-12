#!/usr/bin/env python3
"""Bounded retrospective completion evidence; never writes retrospective files."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import os
import tempfile

PROVIDERS = {"claude", "antigravity", "codex"}
ROLE_HEADINGS = {
    "Developer": "Developer",
    "Technical_Lead": "Technical Lead",
    "QA": "QA",
    "Product_Owner": "Product Owner",
    "Business_Analyst": "Business Analyst",
    "UI_UX_Designer": "UI/UX Designer",
    "Orchestrator": "Orchestrator",
}
ROLES = set(ROLE_HEADINGS)
TRIGGERS = {"tooling_failure", "external_blocker", "decision_ambiguity", "repeated_fix", "reusable_lesson", "explicit_request"}
FIELDS = {"provider", "run", "story", "stage", "role"}
MAX_RECORDS = 128


def confined(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError("pointer must be a relative forward-slash path")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or any(p in {".", ".."} or ":" in p for p in relative.split("/")):
        raise ValueError("absolute/escaping pointer rejected")
    candidate = root / relative
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise ValueError("pointer escapes bound runtime")
    return candidate


def runtime_root(target, provider, runtime):
    if provider not in PROVIDERS or runtime not in {f".{provider}/agents", f".{provider}/agents/working"}:
        raise ValueError("foreign or unresolved provider runtime binding")
    root = confined(Path(target).resolve(), runtime)
    if root.is_symlink() or any(p.is_symlink() for p in root.parents if p != Path(target).resolve()):
        raise ValueError("redirected runtime root rejected")
    return root


def identity(value, provider):
    if not isinstance(value, dict) or set(value) != FIELDS:
        raise ValueError("expected exact provider/run/story/stage/role identity")
    if value["provider"] != provider or value["role"] not in ROLES:
        raise ValueError("foreign provider or unsupported role")
    if not isinstance(value["story"], str) or not re.fullmatch(r"ST-[0-9]{6}", value["story"]):
        raise ValueError("invalid story identity")
    for key in ("run", "stage"):
        if not isinstance(value[key], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value[key]):
            raise ValueError(f"invalid {key} identity")
    return value


def record_path(root, value):
    return confined(root, f"tmp/retro-completion/{value['run']}/{value['story']}/{value['stage']}_{value['role']}.json")


def load_record(path):
    if path.stat().st_size > 16384:
        raise ValueError("completion record exceeds bounded size")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_record(record, expected, provider):
    if not isinstance(record, dict) or set(record) != FIELDS | {"state", "triggers", "contributions", "evidence"}:
        raise ValueError("invalid completion record fields")
    if identity({k: record[k] for k in FIELDS}, provider) != expected:
        raise ValueError("completion identity mismatch")
    if record["state"] not in {"unknown", "clean", "required"}:
        raise ValueError("invalid trigger evaluation state")
    for field in ("triggers", "contributions", "evidence"):
        values = record[field]
        if not isinstance(values, list) or len(values) > 16 or any(not isinstance(v, str) or len(v) > 240 for v in values) or len(set(values)) != len(values):
            raise ValueError(f"invalid bounded {field}")
    if not set(record["triggers"]) <= TRIGGERS or bool(record["triggers"]) != (record["state"] == "required"):
        raise ValueError("required state must identify real trigger kinds")
    if record["state"] != "required" and (record["contributions"] or record["evidence"]):
        raise ValueError("clean/unknown evaluation cannot claim retro contributions")


def write_record(root, expected, state, triggers=(), contributions=(), evidence=()):
    identity(expected, expected["provider"])
    path = record_path(root, expected)
    record = {**expected, "state": state, "triggers": sorted(set(triggers)), "contributions": sorted(set(contributions)), "evidence": sorted(set(evidence))}
    validate_record(record, expected, expected["provider"])
    if path.exists():
        old = load_record(path)
        validate_record(old, expected, expected["provider"])
        # A later clean/unknown resume cannot erase a prior required contribution.
        if old["state"] == "required":
            record["state"] = "required"
            for key in ("triggers", "contributions", "evidence"):
                record[key] = sorted(set(old[key]) | set(record[key]))
    validate_record(record, expected, expected["provider"])
    validate_pointers(root, record, require_present=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Recheck containment after mkdir, before the atomic write.
    record_path(root, expected)
    fd, temporary = tempfile.mkstemp(prefix=".completion-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as output:
            json.dump(record, output, sort_keys=True)
            output.write("\n")
        os.replace(temporary, path)
    finally:
        if Path(temporary).exists():
            Path(temporary).unlink()
    return record


def validate_pointers(root, record, require_present):
    role = ROLE_HEADINGS[record["role"]]
    for pointer in record["contributions"]:
        path_text, separator, heading = pointer.partition("#")
        if not separator or path_text != f"retros/{record['story']}_retro.md":
            raise ValueError("contribution must name its own story retro and role heading")
        allowed = {role} | {f"{prefix} — {role}" for prefix in ("Implementer", "Reviewer", "Analyst")}
        if heading not in allowed:
            raise ValueError("contribution belongs to another role")
        path = confined(root, path_text)
        if require_present:
            text = path.read_text(encoding="utf-8")
            match = re.search(r"^## " + re.escape(heading) + r"\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
            if not match or not re.search(r"^- (?!None\.?\s*$)\S", match[1], re.M) or "*(pending)*" in match[1]:
                raise ValueError("required role contribution absent or unpopulated")
    for pointer in record["evidence"]:
        path = confined(root, pointer)
        if not pointer.startswith(("tmp/", "retros/")):
            raise ValueError("evidence must remain in provider-local completion/retro state")
        if require_present and not path.is_file():
            raise ValueError("required evidence pointer missing")


def check(root, provider, expected):
    if not isinstance(expected, list) or not expected or len(expected) > MAX_RECORDS:
        raise ValueError("nonempty bounded expected stage identities required")
    seen, clean, required, retros = set(), 0, 0, set()
    for value in expected:
        identity(value, provider)
        key = tuple(value[k] for k in sorted(FIELDS))
        if key in seen:
            raise ValueError("duplicate expected stage identity")
        seen.add(key)
        path = record_path(root, value)
        if not path.is_file():
            raise ValueError("missing trigger evaluation: " + value["story"] + "/" + value["stage"] + "/" + value["role"])
        record = load_record(path)
        validate_record(record, value, provider)
        if record["state"] == "unknown":
            raise ValueError("unknown trigger evaluation blocks completion")
        if record["state"] == "required":
            if not record["contributions"] or not record["evidence"]:
                raise ValueError("required contribution/evidence not submitted")
            validate_pointers(root, record, require_present=True)
            required += 1
            retros.update(pointer.partition("#")[0] for pointer in record["contributions"])
        else:
            clean += 1
    return {"status": "complete", "clean": clean, "required": required, "retros": sorted(retros)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("record", "check"))
    parser.add_argument("--target", default=".")
    parser.add_argument("--provider", required=True, choices=sorted(PROVIDERS))
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--run")
    parser.add_argument("--story")
    parser.add_argument("--stage")
    parser.add_argument("--role")
    parser.add_argument("--state", choices=("unknown", "clean", "required"))
    parser.add_argument("--trigger", action="append", default=[])
    parser.add_argument("--contribution", action="append", default=[])
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--expected", help="confined relative runtime JSON file listing expected identities")
    args = parser.parse_args()
    try:
        root = runtime_root(args.target, args.provider, args.runtime_root)
        if args.command == "record":
            expected = {k: getattr(args, k) for k in FIELDS}
            result = write_record(root, expected, args.state, args.trigger, args.contribution, args.evidence)
        else:
            path = confined(root, args.expected)
            if path.stat().st_size > 65536:
                raise ValueError("expected manifest exceeds bounded size")
            result = check(root, args.provider, json.loads(path.read_text(encoding="utf-8")))
        print(json.dumps(result, sort_keys=True))
    except (ValueError, OSError, TypeError) as error:
        parser.exit(2, f"retro completion blocked: {error}\n")


if __name__ == "__main__":
    main()
