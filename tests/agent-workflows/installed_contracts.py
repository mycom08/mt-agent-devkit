"""Offline contracts for the installed WF-002 benchmark; never accept G2/G6."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("fixtures") / "WF-002-business-logic"
MANIFEST = Path(__file__).with_name("installed_benchmark_manifest.json")
STAGE_ROLES = {"developer_implementation": "Developer", "technical_lead_review": "TL",
               "qa_verification": "QA", "product_owner_closure": "PO"}
GUIDANCE_FILES = [".claude/agents/templates/rules/Agent_Common_Bootstrap_template.md",
                  ".claude/agents/templates/shared/workflows/Create_Stories_Workflow_Shared_template.md",
                  ".claude/agents/templates/shared/workflows/Refine_Prototype_Workflow_Shared_template.md"]
spec = importlib.util.spec_from_file_location(
    "installed_contract_telemetry", ROOT / ".claude/agents/templates/scripts/telemetry.py")
telemetry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(telemetry)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def fixture_hashes() -> dict[str, str]:
    # Match the historical manifest's LF-normalized source hashes, not host checkout EOLs.
    return {path.relative_to(FIXTURE).as_posix(): hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        for path in sorted(FIXTURE.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}


def validate_configuration(config: dict, frozen: dict) -> None:
    if json.dumps(config, sort_keys=True) != json.dumps(frozen, sort_keys=True):
        changed = sorted(key for key in set(config) | set(frozen) if config.get(key) != frozen.get(key))
        raise ValueError("Installed configuration drift: " + ", ".join(changed))


def validate_template_delta(command, refs: dict[str, str]) -> None:
    changed = command(["git", "diff", "--name-only", refs["baseline"], refs["candidate"],
                       "--", ".claude/agents/templates"], ROOT).stdout.splitlines()
    if sorted(changed) != sorted(GUIDANCE_FILES):
        raise ValueError("Source arms do not isolate the three FIX-02 guidance files")


def inspect_telemetry(target: Path, expected_model: str | None = None) -> dict:
    rows, errors = [], []
    for path in sorted((target / ".claude/agents/tmp/token-metrics").glob("*.jsonl")):
        try:
            rows.extend(telemetry.read_records(path))
        except (ValueError, TypeError, OSError):
            errors.append(f"{path.name}: invalid telemetry schema or duplicate record")
    if rows:
        try:
            telemetry.validate_batch(rows)
        except ValueError:
            errors.append("Invalid combined telemetry batch")
    stages = [row["stage"] for row in rows]
    present = len(rows) == 4 and sorted(stages) == sorted(STAGE_ROLES)
    if not present:
        errors.append("Expected exactly four distinct stage records")
    if len({row["run_id"] for row in rows}) != 1:
        errors.append("Expected one run identity")
    for row in rows:
        if (row["story_id"] != "ST-000211" or row["role"] != STAGE_ROLES.get(row["stage"])
                or row["session_mode"] != "fresh" or row["completion_status"] != "completed"):
            errors.append("Stage identity, role, session or completion mismatch")
        if expected_model is not None and row["model"] != expected_model:
            errors.append("Stage model differs from frozen configuration")
        start = telemetry.validate_utc_timestamp("started_at", row["started_at"])
        end = telemetry.validate_utc_timestamp("ended_at", row["ended_at"])
        if abs(round((end - start).total_seconds() * 1000) - row["duration_ms"]) > 1:
            errors.append("Stage duration differs from timestamps")
    return {"row_count": len(rows), "stages": stages,
            "required_stages_present_once": present and not errors,
            "schema_and_identity_valid": not errors,
            "measured_usage_for_every_stage": present and not errors and all(
                row["usage_source"] == "raw_transcript" for row in rows),
            "errors": sorted(set(errors)),
            "provenance_review": "pending independent source-transcript review"}


def inspect_review_evidence(path: Path, target: Path, implementation_sha: str) -> dict:
    """Validate externally assessed trace evidence; missing evidence is never approval.

    JSON lives beside the raw capture, outside the agent-writable target. Artifact
    names are relative to that directory. Distinct sessions and immutable transcript
    hashes make a claim reviewable; an independent human still assesses the traces.
    """
    errors = []
    if not path.is_file():
        return {"evidence_valid": False, "errors": ["Missing independent review evidence"]}
    if path.resolve().is_relative_to(target.resolve()):
        return {"evidence_valid": False, "errors": ["Review evidence must be outside target"]}
    try:
        evidence = json.loads(path.read_text(encoding="utf-8"))
        if set(evidence) != {"schema_version", "implementation_sha", "developer_session_id", "reviews"}:
            raise ValueError()
        if type(evidence["schema_version"]) is not int or evidence["schema_version"] != 1:
            raise ValueError()
        if evidence["implementation_sha"] != implementation_sha or not re.fullmatch(r"[0-9a-f]{40}", implementation_sha):
            raise ValueError()
        developer = evidence["developer_session_id"]
        if not isinstance(developer, str) or not developer.strip():
            raise ValueError()
        reviews = evidence["reviews"]
        if not isinstance(reviews, dict) or set(reviews) != {"TL", "QA"}:
            raise ValueError()
        sessions = {developer}
        artifacts = set()
        for role in ("TL", "QA"):
            review = reviews[role]
            if set(review) != {"verdict", "reviewed_sha", "session_id", "transcript", "transcript_sha256"}:
                raise ValueError()
            if review["verdict"] != "approved" or review["reviewed_sha"] != implementation_sha:
                raise ValueError()
            session = review["session_id"]
            if not isinstance(session, str) or not session.strip() or session in sessions:
                raise ValueError()
            sessions.add(session)
            relative = Path(review["transcript"])
            transcript = (path.parent / relative).resolve()
            if (relative.is_absolute() or ".." in relative.parts
                    or not transcript.is_relative_to(path.parent.resolve())
                    or transcript.is_relative_to(target.resolve()) or transcript in artifacts
                    or not transcript.is_file() or digest(transcript) != review["transcript_sha256"]):
                raise ValueError()
            artifacts.add(transcript)
    except (ValueError, KeyError, TypeError, OSError):
        errors.append("Invalid review evidence, SHA, session independence or transcript hash")
    return {"evidence_valid": not errors, "errors": errors,
            "verdict": "pending independent trace assessment; never auto-approval"}
