"""Controlled, local WF-002 comparison for FIX-02 (WP-04A/WP-05).

Run explicitly; this script never launches paid Claude sessions on import. Raw
streams and scratch repositories live under an OS temporary directory, outside
the product repository. The output is a sanitized summary, not a G2 verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/agent-workflows/fixtures/WF-002-business-logic"
RULE = ".claude/agents/templates/rules/Agent_Common_Bootstrap_template.md"
BASE_REF = "a30460a"
CANDIDATE_REF = "e2e700a"
TEST_COMMAND = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
ROLES = ("developer", "technical_lead", "qa", "product_owner")
STAGES = ("developer_implementation", "technical_lead_review", "qa_verification",
          "product_owner_closure")
SUCCESS_OUTCOMES = {"developer": "completed", "technical_lead": "approved",
                    "qa": "approved", "product_owner": "closed"}
USAGE_KEYS = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
TELEMETRY_PATH = ROOT / ".claude/agents/templates/scripts/telemetry.py"
_telemetry_spec = importlib.util.spec_from_file_location("fix02_canonical_telemetry", TELEMETRY_PATH)
if _telemetry_spec is None or _telemetry_spec.loader is None:
    raise RuntimeError("Cannot load canonical telemetry extractor")
telemetry = importlib.util.module_from_spec(_telemetry_spec)
_telemetry_spec.loader.exec_module(telemetry)


def command(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(args, cwd=cwd, env=env, text=True, encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def source_rule(ref: str) -> tuple[str, str]:
    source = command(["git", "show", f"{ref}:{RULE}"], ROOT).stdout
    match = re.search(r"(?ms)^## 3\. Token-Efficiency Conventions\s*$.*?(?=^## 4\.|\Z)", source)
    if not match:
        raise ValueError(f"Section 3 missing at {ref}")
    section = match.group(0).strip() + "\n"
    return section, hashlib.sha256(section.encode()).hexdigest()


def fixture_bytes(path: Path) -> bytes:
    """Hash text fixture content consistently across Git's Windows line endings."""
    return path.read_bytes().replace(b"\r\n", b"\n")


def fixture_hash() -> str:
    digest = hashlib.sha256()
    for path in sorted(FIXTURE.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(FIXTURE).as_posix().encode())
            digest.update(b"\0")
            digest.update(fixture_bytes(path))
            digest.update(b"\0")
    return digest.hexdigest()


def validate_manifest(manifest: dict[str, Any], model: str, effort: str) -> dict[str, Any]:
    actual_files = {path.relative_to(FIXTURE).as_posix() for path in FIXTURE.rglob("*")
                    if path.is_file()}
    frozen_files = set(manifest["fixture"]["content_sha256"])
    if actual_files != frozen_files:
        raise ValueError(f"Frozen fixture file set differs: missing={sorted(frozen_files - actual_files)}, "
                         f"extra={sorted(actual_files - frozen_files)}")
    for name, frozen_hash in manifest["fixture"]["content_sha256"].items():
        actual = hashlib.sha256(fixture_bytes(FIXTURE / name)).hexdigest()
        if actual != frozen_hash:
            raise ValueError(f"Frozen fixture hash mismatch: {name}")
    configured = manifest["agent_configuration"]
    if model != configured["model_alias"] or effort != configured["reasoning_effort"]:
        raise ValueError("Model alias and effort must match frozen manifest")
    if list(ROLES) != list(configured["role_models"]):
        raise ValueError("Role roster differs from frozen manifest")
    if configured["tool_allowlist"] != ["Read", "PowerShell", "Edit", "Write"]:
        raise ValueError("Tool allowlist differs from runner")
    if manifest["execution"]["stage_order"] != list(STAGES):
        raise ValueError("Stage order differs from runner")
    cli_version = command(["claude", "--version"], ROOT).stdout.strip()
    if configured["cli_version"] not in cli_version:
        raise ValueError(f"Claude CLI version differs: {cli_version}")
    python_version = command([sys.executable, "--version"], ROOT).stdout.strip()
    if configured["python_version"] not in python_version:
        raise ValueError(f"Python version differs: {python_version}")
    return {"cli_version": cli_version, "python_version": python_version,
            "expected_resolved_model": configured["expected_resolved_model"]}


def prepare_repo(root: Path, section: str) -> Path:
    repo = root / "repo"
    shutil.copytree(FIXTURE / "repo", repo)
    shutil.copy2(FIXTURE / "story.md", repo / "story.md")
    shutil.copy2(FIXTURE / "state.json", repo / "state.json")
    (repo / "COMMON_RULE_SECTION_3.md").write_text(section, encoding="utf-8")
    command(["git", "init", "-q"], repo)
    command(["git", "-c", "user.name=Benchmark", "-c", "user.email=benchmark@example.invalid",
             "add", "."], repo)
    command(["git", "-c", "user.name=Benchmark", "-c", "user.email=benchmark@example.invalid",
             "commit", "-qm", "Frozen WF-002 benchmark input"], repo)
    if command(["git", "status", "--porcelain", "--untracked-files=all"], repo).stdout:
        raise ValueError("Fixture repository is dirty before benchmark stage")
    return repo


def prompt_for(role: str, prior: dict[str, Any]) -> str:
    common = (
        "You are in an isolated strict/local benchmark repository. Read "
        "COMMON_RULE_SECTION_3.md and apply its tool-execution guidance. "
        "Read story.md and state.json. The fixture has no repository remote, GitHub, "
        "product-task credentials, or product-task external services. Do not edit "
        "story.md, state.json, the common rule, "
        "tests, or README. Do not mark acceptance criteria complete. "
        "Keep all evidence local. Finish with one JSON object with keys outcome, "
        "evidence (short string), and checks_run (list of exact commands you ran). "
        "Developer outcome must be 'completed' or 'blocked'; Technical Lead and "
        "QA outcomes must be 'approved' or 'rejected'; Product Owner outcome "
        "must be 'closed' or 'blocked'. Do not claim a check you did not run.\n"
    )
    if role == "developer":
        return common + (
            "Act as Developer at implementation stage. Inspect README.md, pricing.py, "
            "and tests/test_pricing.py. Implement only the story's fee-rule correction. "
            "Run python -m unittest discover -s tests -v and report its result. "
            "Report 'completed' only when implementation and tests are complete. "
            "Do not approve your own review or close the story."
        )
    if role == "technical_lead":
        return common + (
            "Act as an independent Technical Lead reviewer in a fresh session. "
            "Inspect pricing.py, tests/test_pricing.py, and git diff. Check the story, "
            "scope, and safety. Do not edit files or rely on Developer's verdict. "
            "Record your own 'approved' or 'rejected' outcome."
        )
    if role == "qa":
        return common + (
            "Act as independent QA in a fresh session. Inspect pricing.py and "
            "tests/test_pricing.py; run python -m unittest discover -s tests -v. "
            "Verify every acceptance criterion against observed behavior and record "
            "your own 'approved' or 'rejected' outcome. Do not edit files."
        )
    return common + (
        "Act as Product Owner in a fresh session. Inspect story.md, pricing.py, and "
        "tests/test_pricing.py. The recorded independent verdicts are "
        f"Technical Lead={prior.get('technical_lead')}, QA={prior.get('qa')}. "
        "Close only if both were approved and the story requirements are met. "
        "Do not edit files. Use 'closed' for closure, 'blocked' otherwise."
    )


def tool_result_success(block: dict[str, Any], *, require_tests: bool = False) -> bool:
    """Require CLI success, any reported exit code zero, and clean test output."""
    if block.get("is_error") is not False:
        return False
    content = block.get("content")
    fragments: list[str] = []
    exit_codes: list[int] = []

    def visit(value: Any) -> None:
        if isinstance(value, str):
            fragments.append(value)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        elif isinstance(value, dict):
            for key in ("exit_code", "exitCode"):
                if type(value.get(key)) is int:
                    exit_codes.append(value[key])
            for key in ("text", "output", "stdout", "content"):
                if key in value:
                    visit(value[key])

    visit(content)
    output = "\n".join(fragments)
    exit_codes += [int(code) for code in re.findall(
        r"(?:exit\s*code\s*[:=]?|exited\s+with\s+code)\s*(\d+)", output, re.I)]
    if any(code != 0 for code in exit_codes):
        return False
    if require_tests:
        return bool(re.search(r"Ran 6 tests?", output)
                    and re.search(r"(?m)^OK\s*$", output))
    return True


def parse_stream(path: Path) -> dict[str, Any]:
    # This is the same extractor used by FIX-01 telemetry. In particular, it
    # groups duplicate assistant events by message.id, keys tool IDs by request,
    # requires stable input/cache usage, and takes max streamed output usage.
    groups = telemetry.parse_transcript(path)
    measured = telemetry.extract_usage(groups)
    tool_uses: dict[tuple[str, str], dict[str, Any]] = {}
    pending: dict[str, list[tuple[str, str]]] = {}
    tool_results: dict[tuple[str, str], dict[str, Any]] = {}
    result: dict[str, Any] | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid stream JSON at line {line_number}") from exc
        if event.get("type") == "assistant":
            msg = event["message"]
            request_id = msg["id"]
            for block in msg.get("content") or []:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                key = (request_id, block["id"])
                if key not in tool_uses:
                    tool_uses[key] = block
                    pending.setdefault(block["id"], []).append(key)
        elif event.get("type") == "user":
            message = event.get("message") or {}
            for block in message.get("content") or []:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                tool_id = block.get("tool_use_id")
                queue = pending.get(tool_id) or []
                if queue:
                    tool_results[queue.pop(0)] = block
        elif event.get("type") == "result":
            result = event
    if result is None:
        raise ValueError("Claude stream has no final result event")
    if len(tool_uses) != measured["tool_invocations"]:
        raise ValueError("Tool detail count differs from canonical telemetry count")
    tool_counts: dict[str, int] = {}
    for block in tool_uses.values():
        name = block.get("name", "unknown")
        tool_counts[name] = tool_counts.get(name, 0) + 1

    def confirmed_command(command_text: str, *, require_tests: bool = False) -> bool:
        return any(
            block.get("name") == "PowerShell"
            and command_text in json.dumps(block.get("input") or {}, ensure_ascii=False).lower()
            and key in tool_results
            and tool_result_success(tool_results[key], require_tests=require_tests)
            for key, block in tool_uses.items()
        )

    aggregate = result.get("usage") or {}
    final_aggregate_usage = {key: aggregate.get(key) if type(aggregate.get(key)) is int else None
                             for key in USAGE_KEYS}
    raw_answer = result.get("result")
    outcome = None
    if isinstance(raw_answer, str):
        for found in re.finditer(r"\{", raw_answer):
            try:
                parsed, _ = json.JSONDecoder().raw_decode(raw_answer[found.start():])
                if isinstance(parsed, dict) and parsed.get("outcome") in {
                        "completed", "approved", "closed", "blocked", "rejected"}:
                    outcome = parsed["outcome"]
                    break
            except json.JSONDecodeError:
                pass
    return {
        "requests": measured["requests"], "tool_invocations": measured["tool_invocations"],
        "tools_by_name": tool_counts,
        "usage": {key: measured[key] for key in USAGE_KEYS},
        "result_aggregate_usage": final_aggregate_usage,
        "result_aggregate_comparison": {
            key: (measured[key] == final_aggregate_usage[key])
            if final_aggregate_usage[key] is not None else None for key in USAGE_KEYS},
        "test_command_confirmed": confirmed_command("python -m unittest discover -s tests -v",
                                                     require_tests=True),
        "git_diff_command_confirmed": confirmed_command("git diff"),
        "powershell_results_unverified": sum(
            1 for key, block in tool_uses.items() if block.get("name") == "PowerShell"
            and (key not in tool_results or not tool_result_success(tool_results[key]))),
        "final_counter_num_turns": result.get("num_turns"),
        "session_final_tokens": None,
        "unavailable_fields": ["session_final_tokens"],
        "model_ids": sorted({str(msg.get("model")) for messages in groups.values()
                             for msg in messages if msg.get("model")}),
        "agent_outcome": outcome, "is_error": result.get("is_error"),
    }


def run_tests(repo: Path) -> dict[str, Any]:
    finished = command(TEST_COMMAND, repo, check=False)
    output = finished.stdout + finished.stderr
    match = re.search(r"Ran (\d+) tests?", output)
    return {"exit_code": finished.returncode,
            "tests_run": int(match.group(1)) if match else None,
            "failures": int(re.search(r"failures=(\d+)", output).group(1)) if "failures=" in output else 0,
            "errors": int(re.search(r"errors=(\d+)", output).group(1)) if "errors=" in output else 0}


def product_diff(repo: Path, expected: dict[str, Any]) -> dict[str, Any]:
    changed = command(["git", "status", "--porcelain", "--untracked-files=all"], repo).stdout
    paths = sorted(line[3:].replace("\\", "/") for line in changed.splitlines())
    diff = command(["git", "diff", "--", "pricing.py"], repo).stdout
    removed = expected["expected_diff"]["removed_line"]
    added = expected["expected_diff"]["added_line"]
    lines = [line for line in diff.splitlines() if line.startswith(("+", "-"))
             and not line.startswith(("+++", "---"))]
    return {"changed_paths": paths,
            "matches_expected": paths == sorted(expected["expected_diff"]["changed_paths_exactly"]
                                                + ["state.json"])
            and lines == ["-" + removed, "+" + added]}


def advance_state(repo: Path, role: str) -> dict[str, Any]:
    """Record harness-owned stage transitions before the next fresh role starts."""
    path = repo / "state.json"
    state = json.loads(path.read_text(encoding="utf-8"))
    if role == "developer":
        state["current_stage"] = "technical_lead_review"
        state["story_status"] = "implemented"
    elif role == "technical_lead":
        state["current_stage"] = "qa_verification"
        state["technical_lead_verdict"] = "approved"
    elif role == "qa":
        state["current_stage"] = "product_owner_closure"
        state["qa_verdict"] = "approved"
    else:
        state["current_stage"] = "complete"
        state["story_status"] = "closed"
        state["product_owner_closure"] = "closed"
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state


def run_stage(repo: Path, raw: Path, role: str, prior: dict[str, Any], model: str,
              effort: str, max_budget: float, expected_model: str) -> dict[str, Any]:
    argv = ["claude", "--print", "--verbose", "--output-format", "stream-json",
            "--safe-mode", "--restricted", "--strict-mcp-config", "--no-chrome",
            "--no-session-persistence", "--permission-mode", "acceptEdits",
            "--permission-prompts", "none", "--tools=Read,PowerShell,Edit,Write",
            "--allowedTools=Read,PowerShell,Edit,Write", "--model", model,
            "--effort", effort, "--max-budget-usd", str(max_budget),
            "-p", prompt_for(role, prior)]
    start = time.monotonic()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with raw.open("w", encoding="utf-8") as stream:
        finished = subprocess.run(argv, cwd=repo, env=env, text=True, encoding="utf-8",
                                  errors="replace", stdout=stream, stderr=subprocess.PIPE)
    metrics = parse_stream(raw)
    duration_ms = round((time.monotonic() - start) * 1000)
    if finished.returncode or metrics["is_error"] or metrics["agent_outcome"] is None:
        completion_status = "failed"
    elif metrics["agent_outcome"] == "blocked":
        completion_status = "blocked"
    else:
        completion_status = "completed"
    metrics.update({"role": role, "cli_exit_code": finished.returncode,
                    "stage": STAGES[ROLES.index(role)], "session_mode": "fresh",
                    "duration_ms": duration_ms, "completion_status": completion_status,
                    "usage_source": "raw_transcript",
                    "model": metrics["model_ids"][0] if len(metrics["model_ids"]) == 1 else None,
                    "raw_stream_file": raw.name,
                    "stderr_present": bool(finished.stderr.strip())})
    metrics.update(metrics["usage"])
    metrics["resolved_model_matches_manifest"] = metrics["model_ids"] == [expected_model]
    return metrics


def run_side(label: str, ref: str, root: Path, expected: dict[str, Any],
             model: str, effort: str, budget: float, expected_model: str) -> dict[str, Any]:
    section, section_hash = source_rule(ref)
    side_root = root / label
    side_root.mkdir()
    repo = prepare_repo(side_root, section)
    preflight = {"mode": "strict/local", "clean": True,
                 "head_sha": command(["git", "rev-parse", "HEAD"], repo).stdout.strip(),
                 "remote": None}
    seeded = run_tests(repo)
    if seeded != {"exit_code": 1, "tests_run": 6, "failures": 1, "errors": 0}:
        raise ValueError(f"Unexpected seeded test result for {label}: {seeded}")
    stages = []
    prior: dict[str, Any] = {}
    reviewer_mutation = False
    state_transitions = []
    for role in ROLES:
        if role == "product_owner" and (prior.get("technical_lead") != "approved"
                                         or prior.get("qa") != "approved"):
            break
        before = (command(["git", "status", "--porcelain", "--untracked-files=all"], repo).stdout,
                  command(["git", "diff", "--binary"], repo).stdout)
        metrics = run_stage(repo, side_root / f"{role}.jsonl", role, prior,
                            model, effort, budget, expected_model)
        stages.append(metrics)
        prior[role] = metrics["agent_outcome"]
        snapshot = (command(["git", "status", "--porcelain", "--untracked-files=all"], repo).stdout,
                    command(["git", "diff", "--binary"], repo).stdout)
        if role != "developer" and snapshot != before:
            reviewer_mutation = True
        if (metrics["cli_exit_code"] or metrics["is_error"]
                or not metrics["resolved_model_matches_manifest"]
                or metrics["agent_outcome"] != SUCCESS_OUTCOMES[role]):
            break
        state_transitions.append({"after_role": role, "state": advance_state(repo, role)})
    final_tests = run_tests(repo)
    diff = product_diff(repo, expected)
    final_state = json.loads((repo / "state.json").read_text(encoding="utf-8"))
    expected_state = json.loads((FIXTURE / "state.json").read_text(encoding="utf-8"))
    expected_state.update({"current_stage": "complete", "story_status": "closed",
                           "technical_lead_verdict": "approved", "qa_verdict": "approved",
                           "product_owner_closure": "closed"})
    return {"label": label, "ref": command(["git", "rev-parse", ref], ROOT).stdout.strip(),
            "section_3_sha256": section_hash, "preflight": preflight,
            "seeded_tests": seeded,
            "final_tests": final_tests, "product_diff": diff, "stages": stages,
            "reviewer_mutation_detected": reviewer_mutation,
            "state_transitions": state_transitions,
            "final_state": final_state,
            "local_quality_pass": len(stages) == len(ROLES)
            and all(stage["agent_outcome"] == SUCCESS_OUTCOMES[stage["role"]]
                    and stage["cli_exit_code"] == 0
                    and stage["resolved_model_matches_manifest"] for stage in stages)
            and stages[0]["test_command_confirmed"]
            and stages[1]["git_diff_command_confirmed"]
            and stages[2]["test_command_confirmed"]
            and not reviewer_mutation
            and final_tests == {"exit_code": 0, "tests_run": 6, "failures": 0, "errors": 0}
            and final_state == expected_state
            and diff["matches_expected"]}


def compare_sides(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    fields = ("requests", "tool_invocations", "duration_ms") + USAGE_KEYS
    rows: dict[str, Any] = {}
    for field in fields:
        def value(side: dict[str, Any]) -> float | None:
            if len(side["stages"]) != len(ROLES):
                return None
            samples = [stage.get(field) for stage in side["stages"]]
            return sum(samples) if all(isinstance(sample, (int, float)) for sample in samples) else None

        before, after = value(baseline), value(candidate)
        rows[field] = {"baseline": before, "candidate": after,
                       "absolute_change": after - before if before is not None and after is not None else None,
                       "percentage_change": round((after - before) / before * 100, 2)
                       if before and after is not None else None}
    return {"totals": rows, "quality_equivalent": baseline["local_quality_pass"]
            and candidate["local_quality_pass"]}


def write_exclusive_json(path: Path, data: dict[str, Any]) -> str:
    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with path.open("xb") as output:
        output.write(payload)
        output.flush()
        os.fsync(output.fileno())
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref", default=BASE_REF)
    parser.add_argument("--candidate-ref", default=CANDIDATE_REF)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--effort", default="medium", choices=("low", "medium", "high"))
    parser.add_argument("--max-budget-usd", type=float, default=2.0,
                        help="Per Claude role stage cap (default: 2)")
    parser.add_argument("--artifacts-dir", type=Path,
                        help="Existing directory outside this Git worktree for raw artifacts")
    parser.add_argument("--inspect-only", action="store_true",
                        help="Validate inputs and print configuration without paid sessions")
    args = parser.parse_args()
    expected = json.loads((FIXTURE / "expected.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "tests/agent-workflows/benchmark_manifest.json")
                          .read_text(encoding="utf-8"))
    environment = validate_manifest(manifest, args.model, args.effort)
    frozen_refs = manifest["comparison"]
    if frozen_refs.get("exploratory_pilot_repetitions_per_arm") != 1:
        raise ValueError("Runner implements exactly one pilot repetition per arm")
    for supplied, key in ((args.base_ref, "baseline_harness_commit"),
                          (args.candidate_ref, "candidate_harness_commit")):
        resolved = command(["git", "rev-parse", supplied], ROOT).stdout.strip()
        if resolved != frozen_refs[key]:
            raise ValueError(f"{key} differs from frozen benchmark manifest")
    base_section, base_hash = source_rule(args.base_ref)
    candidate_section, candidate_hash = source_rule(args.candidate_ref)
    if base_hash == candidate_hash:
        parser.error("The compared common-rule sections are identical")
    if args.max_budget_usd <= 0:
        parser.error("--max-budget-usd must be positive")
    config = {"fixture_sha256": fixture_hash(), "environment": environment,
              "base_ref": args.base_ref,
              "candidate_ref": args.candidate_ref, "base_rule_sha256": base_hash,
              "candidate_rule_sha256": candidate_hash, "model": args.model,
              "effort": args.effort, "max_budget_usd_per_stage": args.max_budget_usd,
              "tools": ["Read", "PowerShell", "Edit", "Write"],
              "mode": "strict/local", "stages": list(STAGES),
              "pilot_repetitions_per_arm": 1,
              "full_benchmark_planned_repetitions_per_arm": frozen_refs["planned_repetitions_per_arm"],
              "scope": "one-pair exploratory local pilot; not the full orchestrator pipeline"}
    if args.inspect_only:
        print(json.dumps(config, indent=2))
        return 0
    artifacts = args.artifacts_dir or Path(tempfile.mkdtemp(prefix="fix02-benchmark-"))
    artifacts = artifacts.resolve()
    if ROOT == artifacts or ROOT in artifacts.parents:
        parser.error("Raw artifacts must be outside the product Git worktree")
    artifacts.mkdir(parents=True, exist_ok=True)
    if any(artifacts.iterdir()):
        parser.error("Artifacts directory must be empty")
    config["run_id"] = artifacts.name
    (artifacts / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    summary = {"config": config, "sides": [], "gate_g2": "unassessed",
               "limitation": "Local role simulation does not execute the installed orchestrator pipeline or remote CI."}
    try:
        for label, ref in (("baseline", args.base_ref), ("candidate", args.candidate_ref)):
            side = run_side(label, ref, artifacts, expected, args.model, args.effort,
                            args.max_budget_usd, environment["expected_resolved_model"])
            summary["sides"].append(side)
            if label == "baseline":
                baseline_file = artifacts / "baseline-report.json"
                baseline_hash = write_exclusive_json(baseline_file,
                                                     {"config": config, "baseline": side,
                                                      "gate_g2": "unassessed"})
                summary["baseline_report"] = {"file": baseline_file.name,
                                              "sha256": baseline_hash}
                if not side["local_quality_pass"]:
                    summary["candidate_skipped_reason"] = "Baseline local quality check failed"
                    break
        if len(summary["sides"]) == 2:
            summary["comparison"] = compare_sides(*summary["sides"])
    finally:
        (artifacts / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Sanitized summary: {artifacts / 'summary.json'}")
    return 0 if len(summary["sides"]) == 2 and all(
        side["local_quality_pass"] for side in summary["sides"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
