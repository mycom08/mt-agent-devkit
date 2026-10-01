"""Run WF-002 through the installed Claude Code strict-mode workflows.

This is a separate G2 evidence path. It does not modify the frozen local pilot
manifest or treat a hand-prompted role simulation as an installed run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/agent-workflows/fixtures/WF-002-business-logic"
STORY_ID = "ST-000211"
REQUIRED_INSTALLED = (
    "CLAUDE.md",
    ".claude/agents/orchestrator_instructions.md",
    ".claude/agents/workflows/Start_Story_Workflow.md",
    ".claude/agents/workflows/Shared_Pipeline_Stages.md",
    ".claude/agents/rules/Agent_Common_Bootstrap.md",
    ".claude/agents/rules/Story_Standard.md",
    ".claude/agents/scripts/branch_preflight.py",
    ".claude/agents/scripts/telemetry.py",
)
ROLES = ("developer", "technical_lead", "qa", "product_owner", "business_analyst",
         "ui_ux_designer")
CLI_TOOLS = "Read,Glob,Grep,Bash,PowerShell,Edit,Write,Agent"
CLI_TIMEOUT_SECONDS = 600
BLOCKED_RESULT = re.compile(
    r"\b(?:I stopped|I did not (?:proceed|finish)|only partly done|"
    r"partly done|cannot (?:proceed|continue)|can't (?:proceed|continue))\b",
    re.IGNORECASE,
)


def command(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def full_ref(ref: str) -> str:
    sha = command(["git", "rev-parse", "--verify", f"{ref}^{{commit}}"], ROOT).stdout.strip()
    if len(sha) != 40:
        raise ValueError(f"Invalid commit ref: {ref}")
    return sha


def export_source(ref: str, target: Path) -> None:
    archive = target.parent / "source.tar"
    command(["git", "archive", "--format=tar", f"--output={archive}", ref], ROOT)
    target.mkdir()
    with tarfile.open(archive) as stream:
        for member in stream.getmembers():
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                raise ValueError("Unsafe source archive entry")
            destination = (target / path).resolve()
            if not destination.is_relative_to(target.resolve()):
                raise ValueError("Source archive entry escapes target")
            stream.extract(member, target, filter="data")
    archive.unlink()
    if not (target / "CLAUDE.md").is_file():
        raise ValueError("Source commit has no Claude Code devkit entry point")


def seed_target(target: Path) -> None:
    shutil.copytree(FIXTURE / "repo", target)
    command(["git", "init", "-q", "-b", "main"], target)
    command(["git", "-c", "user.name=Benchmark", "-c", "user.email=benchmark@example.invalid",
             "add", "."], target)
    command(["git", "-c", "user.name=Benchmark", "-c", "user.email=benchmark@example.invalid",
             "commit", "-qm", "Frozen WF-002 input"], target)
    if command(["git", "remote"], target).stdout.strip():
        raise ValueError("Disposable target unexpectedly has a remote")


def verify_install(target: Path) -> dict[str, str]:
    missing = [name for name in REQUIRED_INSTALLED if not (target / name).is_file()]
    for role in ROLES:
        name = f".claude/agents/{role}_instructions.md"
        if not (target / name).is_file():
            missing.append(name)
    if missing:
        raise ValueError(f"Incomplete installed project: {', '.join(missing)}")
    root = (target / "CLAUDE.md").read_text(encoding="utf-8")
    if "**Mode:** strict" not in root or "{{" in root:
        raise ValueError("Installed CLAUDE.md is not fully adapted to strict mode")
    adaptive = (
        ".claude/agents/context/Project_Priming.md",
        ".claude/agents/context/Document_Index.md",
        *(f".claude/agents/{role}_instructions.md" for role in ROLES),
    )
    unresolved = [name for name in adaptive if not (target / name).is_file() or
                  "{project-name}" in (target / name).read_text(encoding="utf-8")]
    if unresolved:
        raise ValueError(f"Installed adaptive files are incomplete: {', '.join(unresolved)}")
    if command(["git", "remote"], target).stdout.strip():
        raise ValueError("Installed target acquired a remote")
    return {name: hashlib.sha256((target / name).read_bytes()).hexdigest()
            for name in REQUIRED_INSTALLED}


def add_story(target: Path) -> None:
    story = FIXTURE.joinpath("story.md").read_text(encoding="utf-8")
    opening = "## Acceptance criteria\n\n"
    closing = "\n## Decisions and scope"
    before, marker, remainder = story.partition(opening)
    ac_text, end_marker, after = remainder.partition(closing)
    if not marker or not end_marker:
        raise ValueError("WF-002 fixture has no bounded acceptance-criteria section")
    ac_lines = ac_text.strip().splitlines()
    matched = [re.fullmatch(r"(\d+)\. (.+)", line) for line in ac_lines]
    if len(matched) != 5 or any(match is None or int(match.group(1)) != index
                                for index, match in enumerate(matched, start=1)):
        raise ValueError("WF-002 fixture acceptance criteria changed unexpectedly")
    checklist = "\n".join(f"- [ ] {match.group(2)}" for match in matched if match)
    story = before + "## Acceptance Criteria\n\n" + checklist + "\n" + closing + after
    path = target / ".claude/agents/docs/stories" / f"{STORY_ID}.md"
    if path.exists():
        raise ValueError("Installed target already contains benchmark story")
    header = (f"# {STORY_ID} — WF-002 shipping threshold\n\n"
              "**Status:** ready\n**Sprint:** sprint-1\n"
              "**Assigned:** Developer\n**Feature:** none\n**Phase:** none\n"
              "**Project Base Branch:** main\n\n"
              "## Technical Scope\n\n- `pricing.py` shipping threshold comparison.\n\n")
    path.write_text(header + story + "\n## Comments\n\n", encoding="utf-8")


def commit_install_scaffold(target: Path) -> str:
    """Make the installed strict-mode root files a clean, local main base."""
    paths = ("README.md", ".claude/settings.json", ".claude/skills", ".gitignore",
             "CHANGELOG.md", "CLAUDE.md", "VERSION", "docs/wiki")
    command(["git", "add", *paths], target)
    command(["git", "-c", "user.name=Benchmark", "-c",
             "user.email=benchmark@example.invalid", "commit", "-qm",
             "Install strict-mode devkit for WF-002 benchmark"], target)
    status = command(["git", "status", "--porcelain", "--untracked-files=all"], target).stdout
    if status.strip():
        raise ValueError("Installed target is not clean before story execution")
    if command(["git", "branch", "--show-current"], target).stdout.strip() != "main":
        raise ValueError("Installed target is not on main before story execution")
    if command(["git", "remote"], target).stdout.strip():
        raise ValueError("Installed target acquired a remote")
    return command(["git", "rev-parse", "HEAD"], target).stdout.strip()


def run_cli(cwd: Path, stream: Path, prompt: str, budget: float,
            *, add_dir: Path | None = None) -> dict[str, object]:
    argv = ["claude", "--print", "--verbose", "--output-format", "stream-json",
            "--restricted", "--strict-mcp-config", "--no-chrome",
            "--no-session-persistence", "--permission-mode", "acceptEdits",
            "--permission-prompts", "none", "--tools", CLI_TOOLS,
            "--allowedTools", CLI_TOOLS, "--model", "sonnet", "--effort", "medium",
            "--max-budget-usd", str(budget)]
    if add_dir is not None:
        argv += ["--add-dir", str(add_dir)]
    argv += ["-p", prompt]
    started = time.monotonic()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    timed_out = False
    with stream.open("w", encoding="utf-8") as output:
        try:
            finished = subprocess.run(argv, cwd=cwd, env=env, text=True, encoding="utf-8",
                                      errors="replace", stdout=output, stderr=subprocess.PIPE,
                                      timeout=CLI_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            timed_out = True
            finished = subprocess.CompletedProcess(argv, 124, "", "")
    result = None
    assistant_events = 0
    model_ids: set[str] = set()
    truncated_events = 0
    for line in stream.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                truncated_events += 1
                continue
            if event.get("type") == "result":
                result = event
            elif event.get("type") == "assistant":
                assistant_events += 1
                model = event.get("message", {}).get("model")
                if isinstance(model, str):
                    model_ids.add(model)
    blocked = bool(result and BLOCKED_RESULT.search(str(result.get("result", ""))))
    return {"exit_code": finished.returncode, "duration_ms": round((time.monotonic() - started) * 1000),
            "result_present": result is not None, "is_error": result.get("is_error") if result else None,
            "blocked_signal": blocked, "timed_out": timed_out,
            "partial_assistant_events": assistant_events, "partial_model_ids": sorted(model_ids),
            "truncated_events": truncated_events,
            "total_cost_usd": result.get("total_cost_usd") if result else None,
            "stderr_present": bool(finished.stderr.strip()),
            "stream_file": stream.name}


def session_completed(session: dict[str, object]) -> bool:
    """A CLI result event is transport success, not a completed workflow."""
    return (session["exit_code"] == 0 and session["result_present"] is True
            and session["is_error"] is False and session["blocked_signal"] is False
            and session["timed_out"] is False and session.get("truncated_events", 0) == 0)


def inspect_product_diff(target: Path, base_sha: str) -> dict[str, object]:
    """Keep the frozen product oracle separate from required workflow bookkeeping."""
    expected = json.loads(FIXTURE.joinpath("expected.json").read_text(encoding="utf-8"))
    product = expected["expected_diff"]
    changed = command(["git", "diff", "--name-only", f"{base_sha}..HEAD"], target).stdout.splitlines()
    product_paths = sorted(path for path in changed if path != "CHANGELOG.md")
    pricing_diff = command(["git", "diff", "--unified=0", f"{base_sha}..HEAD", "--",
                            "pricing.py"], target).stdout
    removed = [line[1:] for line in pricing_diff.splitlines()
               if line.startswith("-") and not line.startswith("---")]
    added = [line[1:] for line in pricing_diff.splitlines()
             if line.startswith("+") and not line.startswith("+++")]
    changelog_changed = "CHANGELOG.md" in changed
    changelog_diff = (command(["git", "diff", "--unified=0", f"{base_sha}..HEAD", "--",
                                "CHANGELOG.md"], target).stdout if changelog_changed else "")
    changelog_added = [line[1:] for line in changelog_diff.splitlines()
                       if line.startswith("+") and not line.startswith("+++")]
    return {
        "changed_paths": changed,
        "product_paths_match": product_paths == sorted(product["changed_paths_exactly"]),
        "pricing_change_exact": removed == [product["removed_line"]]
        and added == [product["added_line"]],
        "changelog_entry_present": changelog_changed and any(line.strip() for line in changelog_added),
        "unexpected_paths": sorted(set(changed) - set(product["changed_paths_exactly"]) - {"CHANGELOG.md"}),
    }


def inspect_stage_telemetry(target: Path) -> dict[str, object]:
    """Report whether the installed workflow produced usable per-stage measurements."""
    folder = target / ".claude/agents/tmp/token-metrics"
    rows: list[dict[str, object]] = []
    errors: list[str] = []
    for path in sorted(folder.glob("*.jsonl")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"{path.name}:{number}: invalid JSON")
                continue
            if not isinstance(row, dict):
                errors.append(f"{path.name}:{number}: expected object")
                continue
            rows.append(row)
    expected = ("developer_implementation", "technical_lead_review", "qa_verification",
                "product_owner_closure")
    stages = [row.get("stage") for row in rows]
    measured = all(row.get("usage_source") != "unavailable" and
                   isinstance(row.get("requests"), int) and
                   isinstance(row.get("cache_read_input_tokens"), int)
                   for row in rows)
    return {"row_count": len(rows), "stages": stages,
            "required_stages_present_once": len(rows) == len(expected)
            and all(isinstance(stage, str) for stage in stages)
            and sorted(stages) == sorted(expected),
            "measured_usage_for_every_stage": measured and len(rows) == len(expected),
            "errors": errors}


def run_side(label: str, ref: str, artifacts: Path, budget: float) -> dict[str, object]:
    side = artifacts / label
    side.mkdir()
    source, target = side / "devkit", side / "target"
    export_source(ref, source)
    seed_target(target)
    init_prompt = (f"init project {target} in strict mode. This is a disposable WF-002 "
                   "Python repository with no GitHub remote. Complete the normal installed "
                   "devkit init workflow, including adaptive files. Put any temporary "
                   "helper scripts under target/.wf002-tmp/, outside .claude/. Helpers "
                   "may prepare content there; use the normal file tools for final "
                   ".claude/agents/ edits. If a final write needs approval, stop and "
                   "report it rather than routing that write through a helper or shell. "
                   "Remove temporary helpers before completion. Do not use GitHub or "
                   "external services. Do not edit the devkit source checkout.")
    init = run_cli(source, side / "init.jsonl", init_prompt, budget, add_dir=target)
    result: dict[str, object] = {"label": label, "source_sha": ref, "init": init,
                                 "installed": False, "story_started": False,
                                 "gate_g2": "unassessed"}
    if not session_completed(init):
        result["blocked_reason"] = "Init project session failed or reported a blocked outcome"
        return result
    try:
        result["installed_file_sha256"] = verify_install(target)
    except ValueError as exc:
        result["blocked_reason"] = str(exc)
        return result
    result["installed"] = True
    try:
        result["installed_base_sha"] = commit_install_scaffold(target)
    except (subprocess.CalledProcessError, ValueError) as exc:
        result["blocked_reason"] = f"Installed scaffold commit failed: {exc}"
        return result
    add_story(target)
    start = run_cli(target, side / "start-story.jsonl", f"start story {STORY_ID}", budget)
    result["start_story"] = start
    result["story_started"] = session_completed(start)
    result["story_status"] = command(["git", "status", "--porcelain", "--untracked-files=all"], target).stdout.splitlines()
    result["active_branch"] = command(["git", "branch", "--show-current"], target).stdout.strip()
    result["remote"] = command(["git", "remote"], target).stdout.strip() or None
    result["product_diff"] = inspect_product_diff(target, str(result["installed_base_sha"]))
    result["stage_telemetry"] = inspect_stage_telemetry(target)
    if result["active_branch"] == "main":
        result["story_started"] = False
        result["blocked_reason"] = "Start story remained on main; no story branch was created"
    elif not result["story_started"]:
        result["blocked_reason"] = "Start story session failed or reported a blocked outcome"
    return result


def run_exit_code(sides: list[dict[str, object]], expected_count: int) -> int:
    """A complete capture still requires independent G2 quality assessment."""
    return 2 if len(sides) == expected_count and all(side["story_started"] for side in sides) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="a30460a87c6d439b1193c45b77cc638a8f237fdb")
    parser.add_argument("--candidate-ref", default="e2e700aa2e1014011c07c789458d13501a92f661")
    parser.add_argument("--max-budget-usd", type=float, default=2.0,
                        help="Cap for each init or start-story CLI session")
    parser.add_argument("--repetitions", type=int, default=3,
                        help="Fresh baseline/candidate pairs (default: 3)")
    parser.add_argument("--artifacts-dir", type=Path)
    parser.add_argument("--execute", action="store_true", help="Launch paid installed workflow sessions")
    args = parser.parse_args()
    if args.max_budget_usd <= 0:
        parser.error("--max-budget-usd must be positive")
    if args.repetitions <= 0:
        parser.error("--repetitions must be positive")
    refs = {"baseline": full_ref(args.baseline_ref), "candidate": full_ref(args.candidate_ref)}
    cli_version = command(["claude", "--version"], ROOT).stdout.strip()
    config = {"refs": refs, "cli_version": cli_version, "model_alias": "sonnet",
              "effort": "medium", "tools": CLI_TOOLS.split(","),
              "max_budget_usd_per_session": args.max_budget_usd,
              "timeout_seconds_per_session": CLI_TIMEOUT_SECONDS,
              "repetitions_per_arm": args.repetitions,
              "surface": "Claude Code installed strict workflow", "gate_g2": "unassessed"}
    if not args.execute:
        print(json.dumps(config, indent=2))
        return 0
    artifacts = (args.artifacts_dir or Path(tempfile.mkdtemp(prefix="wf002-installed-"))).resolve()
    if artifacts == ROOT or ROOT in artifacts.parents:
        parser.error("Raw artifacts must be outside the devkit repository")
    artifacts.mkdir(parents=True, exist_ok=True)
    if any(artifacts.iterdir()):
        parser.error("Artifacts directory must be empty")
    summary: dict[str, object] = {"config": config, "sides": [], "gate_g2": "unassessed"}
    try:
        for repetition in range(1, args.repetitions + 1):
            for label, ref in refs.items():
                side = run_side(f"{label}-{repetition}", ref, artifacts, args.max_budget_usd)
                summary["sides"].append(side)
                if not side["installed"] or not side["story_started"]:
                    break
            if len(summary["sides"]) != repetition * len(refs):
                break
    finally:
        (artifacts / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"Sanitized summary: {artifacts / 'summary.json'}")
    outcome = run_exit_code(summary["sides"], args.repetitions * len(refs))
    if outcome == 2:
        print("Installed sessions were recorded; G2 quality remains unassessed.")
    return outcome


if __name__ == "__main__":
    raise SystemExit(main())
