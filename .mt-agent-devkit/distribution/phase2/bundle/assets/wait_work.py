#!/usr/bin/env python3
"""Bounded CI evidence and launch-once local verification. Python 3.10+."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import quote

PROVIDERS = ("claude", "antigravity", "codex")
CODES = {"PASS": 0, "FAIL": 1, "NO RUN": 2, "ERROR": 3, "STALE": 4, "PENDING": 124}
SUCCESS = {"SUCCESS", "NEUTRAL", "SKIPPED"}
PENDING = {"PENDING", "EXPECTED", "QUEUED", "IN_PROGRESS", "WAITING", "REQUESTED"}
RUN_FIELDS = "databaseId,workflowDatabaseId,workflowName,event,attempt,status,conclusion,headSha,url"


class WaitError(ValueError):
    """Sanitized errors: never include command output or credential values."""


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise WaitError("missing or invalid identity/bindings") from exc


def safe(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise WaitError("invalid confined path")
    if Path(relative).is_absolute() or any(part in ("", ".", "..") for part in relative.split("/")):
        raise WaitError("invalid confined path")
    root = Path(root).resolve()
    path = root / relative
    for component in (path, *path.parents):
        if component == root.parent:
            break
        if component.exists() and (component.is_symlink() or getattr(component.stat(), "st_file_attributes", 0) & 0x400):
            raise WaitError("redirected runtime path")
    if not path.resolve().is_relative_to(root):
        raise WaitError("runtime escape")
    return path


def run_directory(root, provider, runtime, identity, kind):
    if provider not in PROVIDERS or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", identity or ""):
        raise WaitError("invalid provider or run identity")
    binding = load(safe(root, "." + provider + "/harness/state-paths.json"))
    if binding.get("PROVIDER_ROOT") != "." + provider or binding.get("RUNTIME_ROOT") != runtime:
        raise WaitError("foreign or unbound runtime")
    expected_prefix = "." + provider + "/agents"
    if runtime != expected_prefix and not runtime.startswith(expected_prefix + "/"):
        raise WaitError("foreign runtime")
    return safe(root, runtime + "/tmp/waits/" + kind + "/" + identity)


def write_json(path, value):
    temporary = path.with_name(path.name + "." + str(os.getpid()) + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def claim(directory, value):
    directory.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        directory.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise WaitError("identity already exists; wait or use a new identity") from exc
    write_json(directory / "identity.json", value)


def result(outcome, **fields):
    return {"outcome": outcome, "exit_code": CODES[outcome], **fields}


def gh_json(arguments, timeout=30, allowed=(0,)):
    try:
        response = subprocess.run(["gh", *arguments], capture_output=True, encoding="utf-8", timeout=max(.01, timeout))
    except subprocess.TimeoutExpired as exc:
        raise WaitError("GitHub request timed out; retry same identity") from exc
    except OSError as exc:
        raise WaitError("GitHub CLI unavailable") from exc
    if response.returncode not in allowed or (response.returncode and not response.stdout.strip() and not re.search(r"no (?:required )?checks reported", response.stderr, re.I)):
        message = response.stderr.lower()
        category = "authentication" if any(word in message for word in ("auth", "login", "401", "403")) else "network/API"
        raise WaitError("GitHub " + category + " error; recover then retry same identity")
    try:
        return json.loads(response.stdout or "[]")
    except ValueError as exc:
        raise WaitError("invalid GitHub response") from exc


def state_of(check):
    if check.get("status") and check["status"].upper() != "COMPLETED":
        return "PENDING"
    value = (check.get("conclusion") or check.get("state") or "PENDING").upper()
    if value in PENDING:
        return "PENDING"
    return "PASS" if value in SUCCESS else "FAIL"


def aggregate(checks, runs, required=()):
    """Conservative all-visible gate, also requiring explicitly expected names."""
    names = {item.get("name", item.get("context")) for item in checks}
    names.update(item.get("workflowName") for item in runs)
    missing = sorted(set(required) - names)
    states = [state_of(check) for check in checks]
    for run in runs:
        states.append("PENDING" if run.get("status") != "completed" else ("PASS" if run.get("conclusion") == "success" else "FAIL"))
    if "FAIL" in states:
        return "FAIL", missing
    if missing or "PENDING" in states:
        return "PENDING", missing
    return ("PASS" if states else "NO RUN"), missing


def latest_runs(runs, sha):
    # A rerun supersedes its older attempt; distinct workflows stay independent.
    if len(runs) >= 100:
        raise WaitError("workflow result limit reached; complete evidence required")
    latest = {}
    for run in sorted(runs, key=lambda item: item.get("databaseId", 0), reverse=True):
        if run.get("headSha") != sha:
            raise WaitError("GitHub returned evidence for another SHA")
        workflow = run.get("workflowDatabaseId", run.get("workflowName", str(run.get("databaseId"))))
        latest.setdefault((workflow, run.get("event")), run)
    return list(latest.values())


def ci_snapshot(repo, pr, sha, request, required=()):
    fields = "headRefOid,statusCheckRollup,commits,baseRefName"
    view = request(["pr", "view", str(pr), "--repo", repo, "--json", fields]) if pr else None
    current = view["headRefOid"] if view else sha
    if sha and current != sha:
        return result("STALE", inspected_sha=sha, current_sha=current, runs=[])
    runs = latest_runs(request(["run", "list", "--repo", repo, "--commit", current, "--limit", "100", "--json", RUN_FIELDS]), current)
    checks = view.get("statusCheckRollup", []) if view else []
    if len(checks) >= 100:
        raise WaitError("check rollup limit reached; complete evidence required")
    if not view:
        # Commit evidence also includes third-party checks and legacy statuses.
        pages = request(["api", "--paginate", "--slurp", "repos/" + repo + "/commits/" + current + "/check-runs?per_page=100&filter=latest"])
        checks.extend(item for page in pages for item in page["check_runs"])
        pages = request(["api", "--paginate", "--slurp", "repos/" + repo + "/commits/" + current + "/statuses?per_page=100"])
        statuses = {}
        for page in pages:
            for item in page:
                statuses.setdefault(item["context"], item)
        checks.extend(statuses.values())
    required_names = set(required)
    if view:
        owner, repository = repo.split("/")
        protection = request(["api", "graphql", "-f", "query=query($owner:String!,$name:String!,$ref:String!){repository(owner:$owner,name:$name){ref(qualifiedName:$ref){branchProtectionRule{requiredStatusCheckContexts}}}}", "-f", "owner=" + owner, "-f", "name=" + repository, "-f", "ref=refs/heads/" + view["baseRefName"]])
        if protection.get("errors"):
            raise WaitError("required-check protection query unavailable")
        reference = protection["data"]["repository"]["ref"]
        if reference is None:
            raise WaitError("base branch protection scope unavailable")
        rule = reference.get("branchProtectionRule") or {}
        required_names.update(rule.get("requiredStatusCheckContexts", []))
        rules = request(["api", "--paginate", "--slurp", "repos/" + repo + "/rules/branches/" + quote(view["baseRefName"], safe="") + "?per_page=100"])
        for page in rules:
            for rule in page:
                if rule.get("type") == "required_status_checks":
                    required_names.update(item["context"] for item in rule["parameters"]["required_status_checks"])
                elif rule.get("type") == "workflows":
                    raise WaitError("required workflow rule needs explicit gate evidence; not certified by this helper")
        # gh's required-check selection incorporates repository protection rules.
        selected = request(["pr", "checks", str(pr), "--repo", repo, "--required", "--json", "name,bucket"], allowed=(0, 1, 8))
        if len(selected) >= 100:
            raise WaitError("required-check result limit reached; complete evidence required")
        required_names.update(item["name"] for item in selected)
        # These selections may not be present yet in a concurrently read rollup.
        for item in selected:
            checks.append({"name": item["name"], "state": {"pass": "SUCCESS", "fail": "FAILURE", "pending": "PENDING", "cancel": "CANCELLED", "skipping": "SKIPPED"}.get(item.get("bucket"), "PENDING")})
    outcome, missing = aggregate(checks, runs, required_names)
    evidence = result(outcome, inspected_sha=current, runs=[{key: run.get(key) for key in ("databaseId", "workflowDatabaseId", "workflowName", "event", "attempt", "status", "conclusion", "headSha")} for run in runs], check_count=len(checks), missing_checks=missing, approval_scope="pr-head" if pr else "commit-only")
    if outcome == "NO RUN" and view:
        # Evidence only. The human zero-check gate must prove suppression/scope.
        for commit in reversed(view.get("commits", [])):
            previous = commit["oid"]
            if previous == current:
                continue
            prior = latest_runs(request(["run", "list", "--repo", repo, "--commit", previous, "--limit", "100", "--json", RUN_FIELDS]), previous)
            if prior:
                comparison = request(["api", "repos/" + repo + "/compare/" + previous + "..." + current])
                files = comparison.get("files", [])
                if len(files) >= 300:
                    raise WaitError("changed-file comparison truncated; zero-check scope requires complete evidence")
                prior_evidence = ci_snapshot(repo, None, previous, request, required_names)
                evidence.update(prior_sha=previous, prior_run_ids=[item["databaseId"] for item in prior], prior_outcome=prior_evidence["outcome"], changed_files=[item["filename"] for item in files], zero_check_gate="required")
                break
    if view:
        final = request(["pr", "view", str(pr), "--repo", repo, "--json", "headRefOid"])["headRefOid"]
        if final != current:
            return result("STALE", inspected_sha=current, current_sha=final, runs=evidence["runs"])
    return evidence


def ci_wait(directory, repo, pr, sha, required, window, interval, request=gh_json, clock=time.monotonic, sleep=time.sleep):
    scope = {"repo": repo, "pr": pr, "sha": sha, "required": sorted(required)}
    path = safe(directory, "identity.json")
    if directory.exists():
        identity = load(path)
        if identity.get("scope") != scope:
            raise WaitError("identity belongs to another CI scope")
    else:
        identity = {"scope": scope, "expected_sha": sha}
        claim(directory, identity)
    deadline = clock() + window
    while True:
        def bounded(arguments, allowed=(0,)):
            return request(arguments, timeout=min(30, max(.01, deadline - clock())), allowed=allowed)
        try:
            snapshot = ci_snapshot(repo, pr, identity.get("expected_sha"), bounded, required)
        except WaitError as exc:
            if clock() >= deadline and "request timed out" in str(exc):
                return result("PENDING", identity=directory.name, inspected_sha=identity.get("expected_sha"), reason="window expired during evidence request; retry same identity")
            raise
        if not identity.get("expected_sha"):
            identity["expected_sha"] = snapshot["inspected_sha"]
            write_json(path, identity)
        snapshot["identity"] = directory.name
        write_json(directory / "evidence.json", snapshot)
        if snapshot["outcome"] not in ("PENDING", "NO RUN") or clock() >= deadline:
            return snapshot
        sleep(min(interval, max(0, deadline - clock())))


def redactor(environment):
    values = sorted({value for name, value in environment.items() if len(value) >= 4 and re.search(r"TOKEN|SECRET|PASSWORD|API_KEY|ACCESS_KEY", name, re.I)}, key=len, reverse=True)
    def clean(line):
        line = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", line)
        for value in values:
            line = line.replace(value, "[REDACTED]")
        return re.sub(r"(https?://)[^/@\s]+:[^/@\s]+@", r"\1[REDACTED]@", line)
    return clean


def summarize(path, exit_code):
    totals, failures = [], []
    clean = redactor(os.environ)
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            line = clean(line).strip()[:300]
            if re.search(r"Test Files|Tests\s|Ran \d+ tests|\b(passed|failed|problems|OK|FAILED)\b|Result \(|Complete!", line):
                totals = (totals + [line])[-10:]
            if exit_code and re.search(r"Error|FAIL|Assertion|Expected|Received|Traceback", line, re.I):
                failures = (failures + [line])[-10:]
    return totals, failures


def local_run(directory, command, cwd):
    if not command:
        raise WaitError("empty verification command")
    # Never persist arguments: commands can include private data. No shell evaluation.
    claim(directory, {"id": directory.name, "runner_pid": os.getpid(), "command_digest": hashlib.sha256(json.dumps(command).encode()).hexdigest(), "started": time.time()})
    log = safe(directory, "output.log")
    clean = redactor(os.environ)
    try:
        with log.open("x", encoding="utf-8", newline="\n") as stream:
            if os.name != "nt":
                os.chmod(log, 0o600)
            process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for chunk in iter(process.stdout.readline, b""):
                stream.write(clean(chunk.decode("utf-8", errors="replace")))
            process.stdout.close()
            exit_code = process.wait()
    except OSError:
        exit_code = 127
    completion = {"process_exit_code": exit_code, "finished": time.time()}
    write_json(directory / "completion.json", completion)
    return local_result(directory, completion)


def local_result(directory, completion):
    code = completion.get("process_exit_code")
    if not isinstance(code, int):
        raise WaitError("invalid process completion")
    log = directory / "output.log"
    totals, failures = summarize(log, code) if log.exists() else ([], [])
    return result("PASS" if code == 0 else "FAIL", identity=directory.name, process_exit_code=code, totals=totals, failures=failures, log="output.log")


def local_wait(directory, window, interval, clock=time.monotonic, sleep=time.sleep):
    identity = load(safe(directory, "identity.json"))
    if identity.get("id") != directory.name:
        raise WaitError("foreign local identity")
    deadline = clock() + window
    while True:
        completion = safe(directory, "completion.json")
        if completion.exists():
            return local_result(directory, load(completion))
        if clock() >= deadline:
            return result("PENDING", identity=directory.name, reason="completion not recorded; retain original command/session identity; do not relaunch")
        sleep(min(interval, max(0, deadline - clock())))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("ci", "local-run", "local-wait"))
    parser.add_argument("--provider", choices=PROVIDERS, required=True)
    parser.add_argument("--runtime-root", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--id", required=True)
    parser.add_argument("--mode", choices=("github", "strict"), required=True)
    parser.add_argument("--repo")
    parser.add_argument("--pr", type=int)
    parser.add_argument("--sha")
    parser.add_argument("--required-check", action="append", default=[])
    parser.add_argument("--window", type=float, default=45)
    parser.add_argument("--interval", type=float, default=5)
    supplied = list(sys.argv[1:] if argv is None else argv)
    command = []
    if "--" in supplied:
        split = supplied.index("--")
        supplied, command = supplied[:split], supplied[split + 1:]
    args = parser.parse_args(supplied)
    try:
        if not 0 <= args.window <= 540 or not .01 <= args.interval <= 60:
            raise WaitError("window must be 0..540 seconds; interval .01..60 seconds")
        if args.operation == "ci":
            if args.mode == "strict":
                raise WaitError("CI watch unavailable in strict mode; use local verification")
            if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo or "") or bool(args.pr) == bool(args.sha):
                raise WaitError("give repository and exactly one PR or full commit SHA")
            if args.pr is not None and args.pr <= 0 or args.sha and not re.fullmatch(r"[0-9a-fA-F]{40}", args.sha):
                raise WaitError("invalid PR/full SHA")
        directory = run_directory(args.root, args.provider, args.runtime_root, args.id, "ci" if args.operation == "ci" else "local")
        if args.operation == "ci":
            evidence = ci_wait(directory, args.repo, args.pr, args.sha, args.required_check, args.window, args.interval)
        elif args.operation == "local-run":
            evidence = local_run(directory, command, Path(args.root).resolve())
        else:
            evidence = local_wait(directory, args.window, args.interval)
    except (WaitError, OSError, KeyError, TypeError, AttributeError, ValueError) as exc:
        evidence = result("ERROR", reason=str(exc) if isinstance(exc, WaitError) else "runtime I/O unavailable", identity=args.id)
    print(json.dumps(evidence, ensure_ascii=True, sort_keys=True))
    return evidence.get("process_exit_code", evidence["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
