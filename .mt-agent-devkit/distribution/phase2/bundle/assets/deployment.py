#!/usr/bin/env python3
"""Standard-library, offline deployment transactions. Python 3.10+.

Release acquisition and native discovery evidence are separate contracts.
This module never runs commands supplied by manifests or changes Git history.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import uuid

PROVIDERS = {"claude", "antigravity", "codex"}
RECEIPT = ".mt-agent-devkit/install-receipt.json"
LOCK = ".mt-agent-devkit-migration.lock"


class Conflict(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def safe(root, relative):
    if not isinstance(relative, str) or "\\" in relative or ":" in relative:
        raise Conflict("invalid relative path")
    parts = PurePosixPath(relative)
    if parts.is_absolute() or not parts.parts or any(p in ("..", ".") for p in relative.split("/")):
        raise Conflict("path escape or noncanonical path")
    root = Path(root).absolute()
    path = root.joinpath(*parts.parts)
    for component in [root, *path.parents, path]:
        if component.exists() and (component.is_symlink() or bool(getattr(component.stat(), "st_file_attributes", 0) & 0x400)):
            raise Conflict("redirected path component")
    if not path.resolve().is_relative_to(root.resolve()):
        raise Conflict("path outside target")
    return path


def filehash(path):
    if not path.exists():
        return None
    if not path.is_file():
        raise Conflict("expected file destination")
    return digest(path.read_bytes())


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def jsonwrite(path, value):
    write(path, canonical(value) + b"\n")


def shape(value, required, optional=()):
    if not isinstance(value, dict) or set(value) - set(required) - set(optional) or set(required) - set(value):
        raise Conflict("invalid object fields")


def bindings(provider, value, target):
    shape(value, ("PROVIDER_ROOT", "RUNTIME_ROOT", "COMMAND_ROOT"))
    if provider not in PROVIDERS or value["PROVIDER_ROOT"] != "." + provider:
        raise Conflict("foreign provider binding")
    for field in ("RUNTIME_ROOT", "COMMAND_ROOT"):
        if not value[field].startswith("." + provider + "/"):
            raise Conflict("foreign runtime binding")
        safe(target, value[field])
    return value


def substituted(text, values):
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    if re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", text):
        raise Conflict("unresolved deployment token")
    return text


def managed_sections(project, template):
    """Preserve project prose while publishing the canonical routing block."""
    start, end = "<!-- MT-AGENT-DEVKIT-START -->", "<!-- MT-AGENT-DEVKIT-END -->"
    if project.count(start) != project.count(end) or project.count(start) > 1:
        raise Conflict("invalid managed entrypoint markers")
    project = re.sub(re.escape(start) + r".*?" + re.escape(end), "", project, flags=re.S).rstrip()
    return project + ("\n\n" if project else "") + start + "\n" + template.strip() + "\n" + end + "\n"


def provider_settings(existing, required):
    """Merge known Claude surfaces; retain unrelated settings and deny rules."""
    result = json.loads(existing) if existing else {}
    required = json.loads(required)
    permissions = result.setdefault("permissions", {})
    allow = permissions.setdefault("allow", [])
    for permission in required["permissions"]["allow"]:
        if permission not in allow: allow.append(permission)
    sessions = result.setdefault("hooks", {}).setdefault("SessionStart", [])
    legacy_scripts = ".claude" + "/agents/scripts/"
    commands = {"powershell -File " + legacy_scripts + "check_devkit_version.ps1", "bash " + legacy_scripts + "check_devkit_version.sh"}
    for session in sessions:
        session["hooks"] = [hook for hook in session.get("hooks", []) if hook.get("command") not in commands]
    wanted = required["hooks"]["SessionStart"][0]
    if not any(wanted == session for session in sessions): sessions.append(wanted)
    return json.dumps(result, indent=2) + "\n"


def inspect(target):
    target = Path(target)
    providers = {}
    runtime = {}
    active = []
    for provider in sorted(PROVIDERS):
        root = safe(target, "." + provider + "/agents")
        if root.exists():
            providers[provider] = {"PROVIDER_ROOT": "." + provider, "RUNTIME_ROOT": "." + provider + "/agents", "COMMAND_ROOT": "." + provider + "/agents"}
            for directory in ("memory", "working-record", "retros", "tmp", "internal", "docs"):
                folder = safe(target, "." + provider + "/agents/" + directory)
                if folder.exists():
                    for item in folder.rglob("*"):
                        relative = item.relative_to(target).as_posix()
                        checked = safe(target, relative)
                        if checked.is_file():
                            runtime[relative] = filehash(checked)
                            if item.name.endswith("pipeline_state.md"):
                                state = item.read_text(encoding="utf-8-sig")
                                if not re.search(r"\*\*Stage:\*\*\s*(?:completed|done|terminal)\b", state, re.I):
                                    active.append(relative)
    return {"schema_version": 1, "providers": providers, "runtime_hashes": runtime, "nonterminal": active, "locked": safe(target, LOCK).exists(), "receipt": load(safe(target, RECEIPT)) if safe(target, RECEIPT).exists() else None}


def plan(target, manifest_path, source, mode, profile, provider_bindings, adaptations=None, resolutions=None):
    if sys.version_info < (3, 10):
        raise Conflict("Python 3.10 required")
    manifest_path = Path(manifest_path)
    manifest = load(manifest_path)
    shape(manifest, ("schema_version", "layout_version", "minimum_python", "profiles", "assets", "files", "legacy_support"))
    if manifest["schema_version"] != 1 or manifest["layout_version"] != 2:
        raise Conflict("unsupported manifest version")
    minimum = tuple(int(part) for part in manifest["minimum_python"].split("."))
    if sys.version_info[:len(minimum)] < minimum:
        raise Conflict("bundle requires newer Python")
    shape(source, ("kind", "tag", "commit", "snapshot_version", "manifest_sha256"))
    if source["kind"] not in ("release", "local") or not re.fullmatch("[0-9a-f]{40}", source["commit"]):
        raise Conflict("invalid immutable source identity")
    if source["kind"] == "release" and not re.fullmatch(r"v\d+\.\d+\.\d+", source["tag"] or ""):
        raise Conflict("release requires tag")
    if digest(manifest_path.read_bytes()) != source["manifest_sha256"]:
        raise Conflict("manifest identity mismatch")
    if mode not in ("github", "strict") or profile not in manifest["profiles"] or not provider_bindings:
        raise Conflict("unsupported mode/profile/providers")
    bound = {p: bindings(p, b, target) for p, b in provider_bindings.items()}
    report = inspect(target)
    if report["locked"] or report["nonterminal"]:
        raise Conflict("pending transaction or nonterminal workflow")
    previous = report["receipt"]
    if previous:
        shape(previous, ("schema_version", "layout_version", "source", "mode", "profile", "providers", "status", "managed_files"))
        if previous["schema_version"] != 1 or previous["layout_version"] != 2 or previous["status"] != "verified":
            raise Conflict("invalid installed receipt baseline")
        paths = [record["path"].casefold() for record in previous["managed_files"]]
        if len(paths) != len(set(paths)):
            raise Conflict("duplicate receipt baseline path")
        for record in previous["managed_files"]:
            safe(target, record["path"])
    if previous and (previous.get("mode") != mode or previous.get("profile") != profile):
        raise Conflict("mode/profile switching excluded")
    if previous and not set(previous["providers"]).issubset(bound):
        raise Conflict("cannot remove an installed provider")
    known = {f["path"]: f["rendered_sha256"] for f in previous.get("managed_files", [])} if previous else {}
    baselines = {f["path"]: f for f in previous.get("managed_files", [])} if previous else {}
    assets = {}
    names = set()
    for asset in manifest["assets"]:
        shape(asset, ("id", "path", "sha256", "bytes", "kind"))
        if asset["id"] in assets or asset["path"].casefold() in names:
            raise Conflict("duplicate asset")
        names.add(asset["path"].casefold())
        content = safe(manifest_path.parent, asset["path"]).read_bytes()
        if digest(content) != asset["sha256"] or len(content) != asset["bytes"]:
            raise Conflict("asset bytes mismatch")
        assets[asset["id"]] = content
    operations = []
    destinations = set()
    ids = set()
    adaptations = adaptations or {}
    resolutions = resolutions or {}
    for item in manifest["files"]:
        shape(item, ("id", "sources", "destination", "owner", "ownership", "profiles", "modes", "providers", "renderer", "legacy_paths", "phase", "required"))
        if item["id"] in ids:
            raise Conflict("duplicate logical ID")
        ids.add(item["id"])
        if profile not in item["profiles"] or mode not in item["modes"]:
            continue
        if not set(bound).intersection(item["providers"]):
            continue
        contexts = [None] if item["owner"] in ("shared", "project") else [p for p in bound if p in item["providers"]]
        if item["owner"] not in ("shared", "project", "selected_provider"):
            raise Conflict("invalid owner")
        for provider in contexts:
            values = {"MODE": mode, "PYTHON_COMMAND": "python" if os.name == "nt" else "python3", "DEVKIT_VERSION": source["tag"][1:] if source["kind"] == "release" else source["snapshot_version"], **(bound[provider] if provider else {})}
            destination = substituted(item["destination"], values)
            safe(target, destination)
            if destination.casefold() in destinations:
                raise Conflict("destination collision")
            destinations.add(destination.casefold())
            contents = [assets[s] for s in item["sources"]]
            content = b"".join(contents)
            renderer = item["renderer"]
            if renderer == "shared_mode":
                if len(contents) != 2:
                    raise Conflict("shared_mode requires shared and mode inputs")
                shared = contents[0].decode("utf-8-sig")
                match = re.search(r"<!-- SHARED-START -->(.*?)<!-- SHARED-END -->", shared, re.S)
                if not match or shared.count("<!-- SHARED-START -->") != 1 or shared.count("<!-- SHARED-END -->") != 1:
                    raise Conflict("invalid shared assembly markers")
                appendix = re.sub(r"<!--.*?-->", "", contents[1].decode("utf-8-sig"), flags=re.S).strip()
                text = match.group(1).strip() + ("\n\n---\n\n" + appendix if appendix else "") + "\n"
                content = substituted(text, values).encode()
            if renderer == "tokens":
                content = substituted(content.decode("utf-8"), values).encode()
            elif renderer == "provider_settings":
                existing = safe(target, destination)
                project_settings = adaptations.get(destination, existing.read_text(encoding="utf-8-sig") if existing.exists() else None)
                content = provider_settings(project_settings, substituted(content.decode("utf-8-sig"), values)).encode()
            elif renderer == "managed_sections":
                existing = safe(target, destination)
                project = adaptations.get(destination, existing.read_text(encoding="utf-8-sig") if existing.exists() else "")
                if any(declared != mode for declared in re.findall(r"\*\*Mode:\*\*\s*(github|strict)\b", project)):
                    raise Conflict("entrypoint mode differs from deployment mode")
                content = managed_sections(project, substituted(content.decode("utf-8-sig"), values)).encode()
            elif renderer == "approved_adaptation":
                existing = safe(target, destination)
                if item["ownership"] == "project_owned" and existing.exists():
                    content = existing.read_bytes()
                elif destination not in adaptations:
                    raise Conflict("approved adaptation required: " + destination)
                else:
                    content = substituted(adaptations[destination], values).encode()
            elif renderer not in ("copy", "create_if_absent", "shared_mode"):
                raise Conflict("renderer not implemented: " + renderer)
            stock_hash = digest(content)
            if renderer not in ("managed_sections", "provider_settings") and destination in adaptations and item["ownership"] in ("managed", "project_adapted", "provider_config"):
                content = substituted(adaptations[destination], values).encode()
            baseline = baselines.get(destination, {})
            if baseline.get("adapted") and destination not in adaptations and renderer not in ("managed_sections", "approved_adaptation", "provider_settings"):
                if baseline.get("stock_sha256") != stock_hash:
                    raise Conflict("review adapted content against changed source: " + destination)
                if filehash(safe(target, destination)) != baseline["rendered_sha256"]:
                    raise Conflict("divergent adapted baseline: " + destination)
                content = safe(target, destination).read_bytes()
            path = safe(target, destination)
            protected_runtime = any(destination.startswith(value["RUNTIME_ROOT"] + "/" + folder + "/") for value in bound.values() for folder in ("memory", "working-record", "retros", "tmp", "internal", "docs"))
            if protected_runtime and item["phase"] != "retirement" and item["ownership"] != "runtime_seed":
                raise Conflict("runtime content accepts create-if-absent seeds only")
            before = filehash(path)
            if item["phase"] == "retirement" and before is None and not item["required"]:
                continue
            after = digest(content)
            ownership = item["ownership"]
            if ownership not in ("managed", "project_adapted", "project_owned", "runtime_seed", "provider_config"):
                raise Conflict("invalid ownership")
            if item["phase"] not in ("content", "discovery", "retirement", "compatibility"):
                raise Conflict("unknown operation phase")
            if item["phase"] == "retirement":
                if ownership != "managed" or before is None or any(destination.startswith(value["RUNTIME_ROOT"] + "/" + folder + "/") for value in bound.values() for folder in ("memory", "working-record", "retros", "tmp", "internal", "docs")):
                    raise Conflict("retirement of project/runtime/unknown content forbidden")
                records = manifest["legacy_support"].get("retirements", [])
                approved = next((record for record in records if record.get("logical_id") == item["id"] and substituted(record.get("path", ""), values) == destination), None)
                resolution = resolutions.get(destination)
                if not approved or not approved.get("after_verified_ids") or not resolution or resolution.get("before_sha256") != before or resolution.get("after_sha256") is not None or not resolution.get("reason"):
                    raise Conflict("exact reviewed retirement and surviving dependencies required")
                action, content, after = "retire", b"", None
            elif before is not None and (ownership in ("project_owned", "runtime_seed") or renderer == "create_if_absent"):
                action, content, after = "preserve", path.read_bytes(), before
            elif before == after:
                action = "preserve"
            elif renderer == "provider_settings":
                action = "replace" if before else "create"
            elif before is not None and (known.get(destination) != before or (baseline and "stock_sha256" not in baseline)):
                resolution = resolutions.get(destination)
                if not resolution:
                    raise Conflict("divergent or unknown baseline: " + destination)
                shape(resolution, ("before_sha256", "after_sha256", "reason"))
                if resolution["before_sha256"] != before or resolution["after_sha256"] != after or not resolution["reason"]:
                    raise Conflict("resolution identity mismatch")
                action = "replace"
            else:
                action = "replace" if before else "create"
            operations.append({"operation_id": item["id"] + (":" + provider if provider else ""), "path": destination, "action": action, "before_sha256": before, "after_sha256": after, "content_hex": content.hex(), "ownership": ownership, "phase": item["phase"], "dependencies": approved["after_verified_ids"] if item["phase"] == "retirement" else [], "stock_sha256": stock_hash, "adapted": after != stock_hash or bool(baseline.get("adapted") and destination not in adaptations)})
    operation_ids = {op["operation_id"] for op in operations if op["action"] != "retire"}
    if any(not set(op["dependencies"]).issubset(operation_ids) for op in operations):
        raise Conflict("retirement dependency missing")
    retired_paths = {op["path"] for op in operations if op["action"] == "retire"}
    for op in operations:
        if op["action"] != "retire" and op["ownership"] != "runtime_seed":
            text = bytes.fromhex(op["content_hex"]).decode("utf-8", errors="replace")
            stale = [path for path in retired_paths if path in text]
            if stale:
                raise Conflict("review adaptation references retired paths: " + op["path"] + " -> " + ", ".join(sorted(stale)))
    operations.sort(key=lambda op: ({"content": 0, "discovery": 1, "retirement": 2, "compatibility": 3}[op["phase"]], op["path"]))
    value = {"schema_version": 1, "target": str(Path(target).resolve()), "source": source, "mode": mode, "profile": profile, "providers": bound, "operations": operations, "preservation_hashes": report["runtime_hashes"]}
    value["plan_id"] = digest(canonical(value))
    return value


def validate_plan(value, target):
    shape(value, ("schema_version", "target", "source", "mode", "profile", "providers", "operations", "preservation_hashes", "plan_id"))
    expected = dict(value)
    expected.pop("plan_id")
    if value["schema_version"] != 1 or value["target"] != str(Path(target).resolve()) or digest(canonical(expected)) != value["plan_id"]:
        raise Conflict("plan identity mismatch")
    seen = set()
    for op in value["operations"]:
        shape(op, ("operation_id", "path", "action", "before_sha256", "after_sha256", "content_hex", "ownership", "phase", "dependencies"), ("stock_sha256", "adapted"))
        safe(target, op["path"])
        protected_runtime = any(op["path"].startswith(bound["RUNTIME_ROOT"] + "/" + folder + "/") for bound in value["providers"].values() for folder in ("memory", "working-record", "retros", "tmp", "internal", "docs"))
        if protected_runtime and op["action"] != "retire" and (op["ownership"] != "runtime_seed" or op["action"] not in ("create", "preserve")):
            raise Conflict("planned runtime content modification forbidden")
        if op["phase"] not in ("content", "discovery", "retirement", "compatibility") or op["ownership"] not in ("managed", "project_adapted", "project_owned", "runtime_seed", "provider_config"):
            raise Conflict("invalid planned ownership/phase")
        if op["action"] == "retire":
            if op["ownership"] != "managed" or op["phase"] != "retirement" or op["before_sha256"] is None or op["after_sha256"] is not None or op["content_hex"] or not op["dependencies"]:
                raise Conflict("invalid retirement boundary")
            for bound in value["providers"].values():
                if any(op["path"].startswith(bound["RUNTIME_ROOT"] + "/" + folder + "/") for folder in ("memory", "working-record", "retros", "tmp", "internal", "docs")):
                    raise Conflict("runtime retirement forbidden")
        if op["path"].casefold() in seen or op["action"] not in ("create", "replace", "preserve", "retire") or (op["action"] != "retire" and digest(bytes.fromhex(op["content_hex"])) != op["after_sha256"]):
            raise Conflict("invalid planned operation")
        seen.add(op["path"].casefold())
    survivors = {op["operation_id"] for op in value["operations"] if op["action"] != "retire"}
    if any(not set(op["dependencies"]).issubset(survivors) for op in value["operations"]):
        raise Conflict("missing retirement survivor")
    retired = {op["path"] for op in value["operations"] if op["action"] == "retire"}
    for op in value["operations"]:
        if op["action"] != "retire" and op["ownership"] != "runtime_seed" and any(path in bytes.fromhex(op["content_hex"]).decode("utf-8", errors="replace") for path in retired):
            raise Conflict("planned surviving content references retired path")
    for provider, values in value["providers"].items():
        bindings(provider, values, target)


def unchanged(target, hashes):
    for path, expected in hashes.items():
        if filehash(safe(target, path)) != expected:
            raise Conflict("preservation hash changed: " + path)


def checkpoint(name, fail_at):
    if fail_at == name:
        raise OSError("injected failure: " + name)


def process_identity(pid):
    """Return process creation identity, None only for proven termination."""
    if not isinstance(pid, int) or pid <= 0:
        raise Conflict("invalid lock process")
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        api = ctypes.WinDLL("kernel32", use_last_error=True)
        api.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        api.OpenProcess.restype = wintypes.HANDLE
        api.CloseHandle.argtypes = (wintypes.HANDLE,)
        api.GetProcessTimes.argtypes = (wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4))
        api.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        handle = api.OpenProcess(0x1000, False, pid)
        if not handle:
            if ctypes.get_last_error() == 87:
                return None
            raise Conflict("lock owner liveness unavailable")
        try:
            code = wintypes.DWORD()
            if not api.GetExitCodeProcess(handle, ctypes.byref(code)):
                raise Conflict("lock owner status unavailable")
            if code.value != 259:
                return None
            times = [wintypes.FILETIME() for _ in range(4)]
            if not api.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
                raise Conflict("lock owner creation identity unavailable")
            return str((times[0].dwHighDateTime << 32) | times[0].dwLowDateTime)
        finally:
            api.CloseHandle(handle)
    return posix_process_identity(pid)


def posix_process_identity(pid):
    if not Path("/proc").is_dir():
        import subprocess
        try:
            result = subprocess.run(["ps", "-p", str(pid), "-o", "lstart="], capture_output=True, text=True, timeout=10, env={**os.environ, "LC_ALL": "C"})
        except (OSError, subprocess.TimeoutExpired):
            raise Conflict("lock owner creation identity unavailable") from None
        identity = result.stdout.strip()
        if result.returncode == 0 and identity:
            return "ps:" + identity
        if result.returncode == 1 and not identity and not result.stderr.strip():
            return None
        raise Conflict("lock owner liveness unavailable")
    proc = Path("/proc") / str(pid) / "stat"
    try:
        # Process name may contain spaces and parentheses.
        return proc.read_text().rsplit(")", 1)[1].split()[19]
    except FileNotFoundError:
        if Path("/proc").is_dir():
            return None
        raise Conflict("lock recovery needs observable process creation identity") from None
    except (OSError, IndexError):
        raise Conflict("lock owner liveness unavailable") from None


def apply(target, value, fail_at=None):
    validate_plan(value, target)
    if inspect(target)["nonterminal"]:
        raise Conflict("nonterminal workflow")
    existing_receipt = load(safe(target, RECEIPT)) if safe(target, RECEIPT).exists() else None
    if all(op["action"] == "preserve" for op in value["operations"]) and existing_receipt and existing_receipt["source"] == value["source"] and existing_receipt["providers"] == value["providers"]:
        unchanged(target, value["preservation_hashes"])
        verify(target)
        return {"status": "verified", "written": [], "no_op": True}
    target = Path(target)
    lock = safe(target, LOCK)
    provider = sorted(value["providers"])[0]
    transaction = uuid.uuid4().hex
    journal_path = safe(target, value["providers"][provider]["RUNTIME_ROOT"] + "/tmp/devkit-migrations/" + transaction + "/journal.json")
    # Prepare complete recovery data before atomically publishing ownership.
    journal = {"schema_version": 1, "transaction_id": transaction, "plan": value, "state": "backed_up", "operations": [], "receipt_before": safe(target, RECEIPT).read_bytes().hex() if safe(target, RECEIPT).exists() else None}
    unchanged(target, value["preservation_hashes"])
    for op in value["operations"]:
        path = safe(target, op["path"])
        if filehash(path) != op["before_sha256"]:
            raise Conflict("target changed after plan: " + op["path"])
        journal["operations"].append({"operation": op, "backup_hex": path.read_bytes().hex() if path.exists() else None, "status": "backed_up"})
    jsonwrite(journal_path, journal)
    checkpoint("journal_prepared", fail_at)
    prepared = lock.with_name(lock.name + "." + transaction + ".prepared")
    try:
        jsonwrite(prepared, {"schema_version": 1, "transaction_id": transaction, "plan_id": value["plan_id"], "pid": os.getpid(), "process_identity": process_identity(os.getpid()), "journal": journal_path.relative_to(target).as_posix()})
        try:
            os.link(prepared, lock)  # Exclusive publication of an already complete file.
        except FileExistsError:
            raise Conflict("target migration locked") from None
    finally:
        prepared.unlink(missing_ok=True)
    try:
        checkpoint("locked", fail_at)
        unchanged(target, value["preservation_hashes"])
        unchanged(target, {op["path"]: op["before_sha256"] for op in value["operations"]})
        receipt_unchanged(target, journal)
        checkpoint("backed_up", fail_at)
        return finish(target, journal_path, journal, fail_at)
    except Exception:
        journal["state"] = "failed"
        jsonwrite(journal_path, journal)
        raise


def receipt_unchanged(target, journal):
    before = bytes.fromhex(journal["receipt_before"]) if journal["receipt_before"] is not None else None
    allowed = {digest(before) if before is not None else None}
    if journal.get("receipt_after_sha256") is not None:
        allowed.add(journal["receipt_after_sha256"])
    if filehash(safe(target, RECEIPT)) not in allowed:
        raise Conflict("intervening receipt edit")


def finish(target, journal_path, journal, fail_at=None):
    value = journal["plan"]
    validate_plan(value, target)
    receipt_unchanged(target, journal)
    for number, entry in enumerate(journal["operations"]):
        op = entry["operation"]
        path = safe(target, op["path"])
        if filehash(path) not in (op["before_sha256"], op["after_sha256"]):
            raise Conflict("intervening edit: " + op["path"])
        journal["state"] = "applying"
        if op["phase"] == "compatibility":
            unchanged(target, value["preservation_hashes"])
            unchanged(target, {other["path"]: other["after_sha256"] for other in value["operations"] if other["phase"] != "compatibility"})
            checkpoint("before_compatibility", fail_at)
        if op["action"] == "retire":
            surviving = {e["operation"]["operation_id"]: e["operation"] for e in journal["operations"]}
            for dependency in op["dependencies"]:
                expected = surviving[dependency]
                if expected["action"] == "retire" or filehash(safe(target, expected["path"])) != expected["after_sha256"]:
                    raise Conflict("retirement survivor not verified")
            path.unlink(missing_ok=True)
        elif op["action"] != "preserve" and filehash(path) != op["after_sha256"]:
            write(path, bytes.fromhex(op["content_hex"]))
        entry["status"] = "applied"
        jsonwrite(journal_path, journal)
        checkpoint("applied:" + str(number), fail_at)
    unchanged(target, value["preservation_hashes"])
    for op in value["operations"]:
        if filehash(safe(target, op["path"])) != op["after_sha256"]:
            raise Conflict("installed verification failed")
    checkpoint("verified", fail_at)
    receipt = {"schema_version": 1, "layout_version": 2, "source": value["source"], "mode": value["mode"], "profile": value["profile"], "providers": value["providers"], "status": "verified", "managed_files": [{"id": op["operation_id"], "path": op["path"], "rendered_sha256": op["after_sha256"], "ownership": op["ownership"], "stock_sha256": op.get("stock_sha256"), "adapted": op.get("adapted", False)} for op in value["operations"] if op["ownership"] != "runtime_seed" and op["action"] != "retire"]}
    journal["receipt_after_sha256"] = digest(canonical(receipt) + b"\n")
    jsonwrite(journal_path, journal)
    receipt_unchanged(target, journal)
    jsonwrite(safe(target, RECEIPT), receipt)
    checkpoint("receipt", fail_at)
    journal["state"] = "completed"
    jsonwrite(journal_path, journal)
    safe(target, LOCK).unlink()
    return {"transaction_id": journal["transaction_id"], "status": "verified", "written": [op["path"] for op in value["operations"] if op["action"] != "preserve"]}


def verify(target):
    receipt = load(safe(target, RECEIPT))
    shape(receipt, ("schema_version", "layout_version", "source", "mode", "profile", "providers", "status", "managed_files"))
    if receipt.get("schema_version") != 1 or receipt.get("layout_version") != 2 or receipt.get("status") != "verified":
        raise Conflict("invalid receipt")
    seen = set()
    for entry in receipt["managed_files"]:
        shape(entry, ("id", "path", "rendered_sha256", "ownership"), ("stock_sha256", "adapted"))
        if entry["path"].casefold() in seen:
            raise Conflict("duplicate receipt path")
        seen.add(entry["path"].casefold())
    unchanged(target, {f["path"]: f["rendered_sha256"] for f in receipt["managed_files"]})
    for provider, values in receipt["providers"].items():
        bindings(provider, values, target)
    return receipt


def _recover(target, transaction, rollback=False):
    lock = load(safe(target, LOCK))
    shape(lock, ("schema_version", "transaction_id", "plan_id", "pid", "process_identity", "journal"))
    if lock["transaction_id"] != transaction:
        raise Conflict("transaction lock mismatch")
    identity = process_identity(lock["pid"])
    if lock["pid"] != os.getpid() and identity == lock["process_identity"]:
        raise Conflict("migration lock owner still live")
    path = safe(target, lock["journal"])
    journal = load(path)
    if journal["transaction_id"] != transaction or journal["plan"]["plan_id"] != lock["plan_id"]:
        raise Conflict("journal identity mismatch")
    validate_plan(journal["plan"], target)
    receipt_unchanged(target, journal)
    lock["pid"] = os.getpid()
    lock["process_identity"] = process_identity(os.getpid())
    jsonwrite(safe(target, LOCK), lock)
    if not rollback:
        if len(journal["operations"]) != len(journal["plan"]["operations"]):
            raise Conflict("backup incomplete")
        return finish(Path(target), path, journal)
    for entry in journal["operations"]:
        op = entry["operation"]
        if filehash(safe(target, op["path"])) not in (op["before_sha256"], op["after_sha256"]):
            raise Conflict("rollback would overwrite intervening edit")
        if entry["backup_hex"] is not None and digest(bytes.fromhex(entry["backup_hex"])) != op["before_sha256"]:
            raise Conflict("corrupt backup")
    receipt_unchanged(target, journal)
    for entry in reversed(journal["operations"]):
        op = entry["operation"]
        destination = safe(target, op["path"])
        if entry["backup_hex"] is None:
            destination.unlink(missing_ok=True)
        else:
            write(destination, bytes.fromhex(entry["backup_hex"]))
        entry["status"] = "restored"
        jsonwrite(path, journal)
    receipt_unchanged(target, journal)
    receipt = safe(target, RECEIPT)
    if journal["receipt_before"] is None:
        receipt.unlink(missing_ok=True)
    else:
        write(receipt, bytes.fromhex(journal["receipt_before"]))
    unchanged(target, journal["plan"]["preservation_hashes"])
    journal["state"] = "rolled_back"
    jsonwrite(path, journal)
    safe(target, LOCK).unlink()
    return {"status": "rolled_back", "transaction_id": transaction}


def recover(target, transaction, rollback=False):
    guard = safe(target, LOCK + ".recovering")
    try:
        descriptor = os.open(guard, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise Conflict("another recovery owns the target; stale recovery guard requires explicit inspection") from None
    try:
        os.write(descriptor, canonical({"pid": os.getpid(), "transaction_id": transaction}))
        os.fsync(descriptor)
        return _recover(target, transaction, rollback)
    finally:
        os.close(descriptor)
        guard.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "plan", "apply", "verify", "resume", "rollback"))
    parser.add_argument("--target", required=True)
    for option in ("manifest", "source", "bindings", "adaptations", "resolutions", "output", "plan", "transaction"):
        parser.add_argument("--" + option)
    parser.add_argument("--mode", choices=("github", "strict"))
    parser.add_argument("--profile", choices=("repo", "project_root"), default="repo")
    args = parser.parse_args()
    try:
        if args.command == "inspect": result = inspect(args.target)
        elif args.command == "plan": result = plan(args.target, args.manifest, load(args.source), args.mode, args.profile, load(args.bindings), load(args.adaptations) if args.adaptations else None, load(args.resolutions) if args.resolutions else None)
        elif args.command == "apply": result = apply(args.target, load(args.plan))
        elif args.command == "verify": result = verify(args.target)
        else: result = recover(args.target, args.transaction, args.command == "rollback")
        if args.output: jsonwrite(Path(args.output), result)
        print(json.dumps(result))
        return 0
    except Conflict as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 3 if safe(args.target, LOCK).exists() else 1


if __name__ == "__main__":
    raise SystemExit(main())
