#!/usr/bin/env python3
"""Collect and aggregate privacy-safe agent-stage telemetry (schema v1).

Usage examples:
  python telemetry.py extract --transcript stage.jsonl --metadata stage.json --output record.json
  python telemetry.py harness --metadata stage.json --output record.json
  python telemetry.py aggregate --input run.jsonl

Only fields in ``TELEMETRY_FIELDS`` are emitted. Raw transcript paths, content,
prompts, tool input, and any unrecognised metadata are deliberately excluded.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
REQUIRED_FIELDS = (
    "schema_version",
    "run_id",
    "story_id",
    "role",
    "stage",
    "session_mode",
    "model",
    "started_at",
    "ended_at",
    "duration_ms",
    "completion_status",
    "usage_source",
    "unavailable_fields",
    "notes",
)
OPTIONAL_FIELDS = (
    "session_final_tokens",
    "requests",
    "tool_invocations",
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)
TELEMETRY_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS
METADATA_FIELDS = tuple(field for field in REQUIRED_FIELDS if field not in {"schema_version", "usage_source", "unavailable_fields"}) + ("session_final_tokens",)
USAGE_FIELDS = OPTIONAL_FIELDS[3:]
ALLOWED_SESSION_MODES = {"fresh", "same_session_resume", "expired_session_resume"}
ALLOWED_COMPLETION_STATUSES = {"completed", "blocked", "failed", "interrupted"}
ALLOWED_USAGE_SOURCES = {"raw_transcript", "harness_report", "unavailable"}
# Schema records use only these six role values. Metadata accepts the familiar
# installed-workflow labels, then normalizes them before a record is written.
CANONICAL_ROLES = {"Developer", "TL", "QA", "PO", "BA", "UI/UX"}
ROLE_ALIASES = {
    "Developer": "Developer", "TL": "TL", "QA": "QA", "PO": "PO", "BA": "BA", "UI/UX": "UI/UX",
    "Technical Lead": "TL", "Product Owner": "PO", "Business Analyst": "BA", "UI/UX Designer": "UI/UX",
}
ALLOWED_ROLES = set(ROLE_ALIASES)
# A Windows drive must start a value or follow a non-alphanumeric delimiter:
# otherwise the `s:/` tail of `https://` would be mistaken for a drive.
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]|\\\\)")
# A local POSIX path can be labelled (for example, "transcript=/home/...").
# The delimiter guard avoids treating URLs and ordinary embedded slash prose as
# local paths, while the familiar root names cover single-component roots.
POSIX_ABSOLUTE_PATH = re.compile(
    r"(?<![A-Za-z0-9_.:/-])/(?:"
    r"(?:home|Users|tmp|var|private|opt|etc|root|mnt|Volumes|workspace|workspaces)(?:/|$)"
    r"|[^\s/]+/[^\s/]+)",
    re.IGNORECASE,
)
LOCAL_FILE_URL = re.compile(r"\bfile://", re.IGNORECASE)
SENSITIVE_TEXT = re.compile(r"(?:api[_-]?key|secret|password|bearer\s+|token\s*[=:])", re.IGNORECASE)


class TelemetryError(ValueError):
    """Raised when source telemetry cannot be measured truthfully."""


def error(message: str) -> "None":
    raise TelemetryError(message)


def is_nonnegative_int(value: Any) -> bool:
    return type(value) is int and value >= 0


def validate_text(field: str, value: Any, *, allow_empty: bool = False, max_length: int = 128) -> None:
    if not isinstance(value, str) or (not allow_empty and not value):
        error(f"{field} must be a {'possibly empty ' if allow_empty else 'non-empty '}string")
    if len(value) > max_length or "\n" in value or "\r" in value:
        error(f"{field} must be a bounded single-line string")
    if WINDOWS_ABSOLUTE_PATH.search(value) or POSIX_ABSOLUTE_PATH.search(value) or LOCAL_FILE_URL.search(value):
        error(f"{field} must not contain a local path")
    if SENSITIVE_TEXT.search(value):
        error(f"{field} must not contain sensitive metadata")


def validate_utc_timestamp(field: str, value: Any) -> datetime:
    validate_text(field, value, max_length=32)
    if not value.endswith("Z"):
        error(f"{field} must be a UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        error(f"{field} must be an ISO-8601 UTC timestamp")
    if parsed.tzinfo != timezone.utc:
        error(f"{field} must be UTC")
    return parsed


def validate_enum(field: str, value: Any, allowed: set[str]) -> None:
    if not isinstance(value, str) or value not in allowed:
        error(f"{field} is invalid" if field != "role" else "role is not an allowed agent role")


def normalize_role(value: Any) -> str:
    validate_enum("role", value, ALLOWED_ROLES)
    return ROLE_ALIASES[value]


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        error(f"cannot read {path.name}: {exc}")
    except json.JSONDecodeError as exc:
        error(f"malformed JSON in {path.name}: line {exc.lineno}, column {exc.colno}")
    if not isinstance(value, dict):
        error(f"metadata in {path.name} must be a JSON object")
    return value


def load_metadata(path: Path) -> dict[str, Any]:
    metadata = read_json(path)
    unknown = sorted(set(metadata) - set(METADATA_FIELDS))
    if unknown:
        error(f"metadata contains unsupported field(s): {', '.join(unknown)}")
    missing = [field for field in METADATA_FIELDS if field not in metadata and field != "session_final_tokens"]
    if missing:
        error(f"metadata missing required field(s): {', '.join(missing)}")
    validate_metadata(metadata)
    return metadata


def validate_metadata(metadata: dict[str, Any]) -> None:
    for field in ("run_id", "story_id", "stage", "model"):
        validate_text(field, metadata[field])
    metadata["role"] = normalize_role(metadata["role"])
    validate_enum("session_mode", metadata["session_mode"], ALLOWED_SESSION_MODES)
    validate_enum("completion_status", metadata["completion_status"], ALLOWED_COMPLETION_STATUSES)
    started_at = validate_utc_timestamp("started_at", metadata["started_at"])
    ended_at = validate_utc_timestamp("ended_at", metadata["ended_at"])
    if ended_at < started_at:
        error("ended_at must not be earlier than started_at")
    validate_text("notes", metadata["notes"], allow_empty=True, max_length=280)
    if not is_nonnegative_int(metadata.get("duration_ms")):
        error("metadata duration_ms must be a non-negative integer")
    if "session_final_tokens" in metadata and (
        not is_nonnegative_int(metadata["session_final_tokens"])
    ):
        error("metadata session_final_tokens must be a non-negative integer")


def parse_transcript(path: Path) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        error(f"cannot read {path.name}: {exc}")
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            error(f"malformed JSON in {path.name} line {number}: {exc.msg}")
        if not isinstance(event, dict):
            error(f"invalid transcript event in {path.name} line {number}: expected object")
        if event.get("type") != "assistant":
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            error(f"invalid assistant event in {path.name} line {number}: missing message object")
        request_id = message.get("id")
        if not isinstance(request_id, str) or not request_id:
            error(f"invalid assistant event in {path.name} line {number}: missing message.id")
        groups[request_id].append(message)
    if not groups:
        error(f"no assistant requests found in {path.name}")
    return groups


def numeric_usage(message: dict[str, Any], field: str, request_id: str) -> int:
    usage = message.get("usage")
    if not isinstance(usage, dict):
        error(f"request {request_id} has no usage object")
    value = usage.get(field)
    if not is_nonnegative_int(value):
        error(f"request {request_id} has invalid usage.{field}")
    return value


def extract_usage(groups: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    totals = {field: 0 for field in USAGE_FIELDS}
    tool_events: set[tuple[str, str]] = set()
    for request_id, messages in groups.items():
        for field in USAGE_FIELDS[:-1]:
            values = [numeric_usage(message, field, request_id) for message in messages]
            if len(set(values)) != 1:
                error(f"request {request_id} has inconsistent usage.{field}")
            totals[field] += values[0]
        totals["output_tokens"] += max(numeric_usage(message, "output_tokens", request_id) for message in messages)
        for message in messages:
            content = message.get("content", [])
            if not isinstance(content, list):
                error(f"request {request_id} has invalid message.content")
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                tool_id = item.get("id")
                if not isinstance(tool_id, str) or not tool_id:
                    error(f"request {request_id} has tool_use without an id")
                tool_events.add((request_id, tool_id))
    totals["requests"] = len(groups)
    totals["tool_invocations"] = len(tool_events)
    return totals


def build_record(metadata: dict[str, Any], usage_source: str, measured: dict[str, int] | None) -> dict[str, Any]:
    metadata = dict(metadata)
    metadata["role"] = normalize_role(metadata["role"])
    record: dict[str, Any] = {"schema_version": SCHEMA_VERSION}
    for field in METADATA_FIELDS:
        if field != "session_final_tokens":
            record[field] = metadata[field]
    record["usage_source"] = usage_source
    record["session_final_tokens"] = metadata.get("session_final_tokens")
    for field in OPTIONAL_FIELDS[1:]:
        record[field] = measured[field] if measured is not None else None
    record["unavailable_fields"] = [field for field in OPTIONAL_FIELDS if record[field] is None]
    record["notes"] = metadata["notes"]
    validate_record(record)
    return record


def validate_record(record: dict[str, Any]) -> None:
    unknown = sorted(set(record) - set(TELEMETRY_FIELDS))
    missing = [field for field in TELEMETRY_FIELDS if field not in record]
    if unknown or missing:
        error(
            "invalid telemetry record fields"
            + (f"; unknown: {', '.join(unknown)}" if unknown else "")
            + (f"; missing: {', '.join(missing)}" if missing else "")
        )
    if type(record["schema_version"]) is not int or record["schema_version"] != SCHEMA_VERSION:
        error(f"unsupported schema version: {record['schema_version']}")
    for field in ("run_id", "story_id", "stage", "model"):
        validate_text(field, record[field])
    validate_enum("role", record["role"], CANONICAL_ROLES)
    validate_enum("session_mode", record["session_mode"], ALLOWED_SESSION_MODES)
    validate_enum("completion_status", record["completion_status"], ALLOWED_COMPLETION_STATUSES)
    validate_enum("usage_source", record["usage_source"], ALLOWED_USAGE_SOURCES)
    started_at = validate_utc_timestamp("started_at", record["started_at"])
    ended_at = validate_utc_timestamp("ended_at", record["ended_at"])
    if ended_at < started_at:
        error("ended_at must not be earlier than started_at")
    validate_text("notes", record["notes"], allow_empty=True, max_length=280)
    if not is_nonnegative_int(record["duration_ms"]):
        error("duration_ms must be a non-negative integer")
    if not isinstance(record["unavailable_fields"], list):
        error("unavailable_fields must be an array")
    expected_unavailable = [field for field in OPTIONAL_FIELDS if record[field] is None]
    if record["unavailable_fields"] != expected_unavailable:
        error("unavailable_fields must list every and only null optional field")
    for field in OPTIONAL_FIELDS:
        value = record[field]
        if value is not None and not is_nonnegative_int(value):
            error(f"{field} must be null or a non-negative integer")
    if record["usage_source"] == "raw_transcript" and any(record[field] is None for field in OPTIONAL_FIELDS[1:]):
        error("raw_transcript records require all cumulative usage fields")
    if record["usage_source"] == "harness_report" and record["session_final_tokens"] is None:
        error("harness_report records require session_final_tokens")
    if record["usage_source"] == "unavailable" and any(record[field] is not None for field in OPTIONAL_FIELDS):
        error("unavailable records must not contain measured usage")


def write_record(record: dict[str, Any], output: Path, append: bool = False) -> None:
    validate_record(record)
    if append and output.exists():
        identity = tuple(record[field] for field in ("run_id", "story_id", "role", "stage"))
        for existing in read_records(output):
            if tuple(existing[field] for field in ("run_id", "story_id", "role", "stage")) == identity:
                error(f"duplicate stage record: {'/'.join(identity)}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a" if append else "w", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def read_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        error(f"cannot read {path.name}: {exc}")
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            error(f"malformed JSON in {path.name} line {number}: {exc.msg}")
        if not isinstance(record, dict):
            error(f"invalid telemetry record in {path.name} line {number}: expected object")
        records.append(record)
    return validate_batch(records, source_name=path.name)


def validate_batch(records: list[dict[str, Any]], source_name: str = "telemetry input") -> list[dict[str, Any]]:
    if not records:
        error(f"no telemetry records found in {source_name}")
    versions = {record.get("schema_version") for record in records}
    if len(versions) != 1:
        error("mixed schema versions in telemetry input")
    for record in records:
        validate_record(record)
    identities: set[tuple[str, str, str, str]] = set()
    for record in records:
        identity = tuple(record[field] for field in ("run_id", "story_id", "role", "stage"))
        if identity in identities:
            error(f"duplicate stage record: {'/'.join(identity)}")
        identities.add(identity)
    return records


def sum_nullable(records: Iterable[dict[str, Any]], field: str) -> int | None:
    values = [record[field] for record in records if record[field] is not None]
    return sum(values) if values else None


def measured_total(records: list[dict[str, Any]], field: str) -> dict[str, Any]:
    available = [record[field] for record in records if record[field] is not None]
    if len(available) == len(records):
        availability = "complete"
        value: int | None = sum(available)
    elif available:
        availability = "partial"
        value = None
    else:
        availability = "unavailable"
        value = None
    return {"value": value, "availability": availability, "available_records": len(available), "records": len(records)}


def summarize_group(records: list[dict[str, Any]]) -> dict[str, Any]:
    totals = {field: measured_total(records, field) for field in OPTIONAL_FIELDS[1:]}
    totals["duration_ms"] = {"value": sum(record["duration_ms"] for record in records), "availability": "complete", "available_records": len(records), "records": len(records)}
    totals["missing_field_count"] = sum(len(record["unavailable_fields"]) for record in records)
    return totals


def summarize_run(run_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["role"], record["stage"], record["model"])].append(record)
    by_role_stage_model = []
    for (role, stage, model), group in sorted(grouped.items()):
        by_role_stage_model.append(
            {
                "role": role,
                "stage": stage,
                "model": model,
                "records": len(group),
                "totals": summarize_group(group),
            }
        )
    final_context = [
        {field: record[field] for field in ("story_id", "role", "stage", "model", "session_final_tokens")}
        for record in records
    ]
    return {
        "run_id": run_id,
        "records": len(records),
        "totals": summarize_group(records),
        "session_final_context": final_context,
        "by_role_stage_model": by_role_stage_model,
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_run: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_run[record["run_id"]].append(record)
    return {"schema_version": SCHEMA_VERSION, "runs": [summarize_run(run_id, by_run[run_id]) for run_id in sorted(by_run)]}


def reconstruct_evidence(path: Path, story_id: str) -> dict[str, Any]:
    evidence = read_json(path)
    try:
        story = evidence["stories"][story_id]
        agents = story["agents"]
    except (KeyError, TypeError):
        error(f"story {story_id} not found in evidence")
    if not isinstance(agents, list):
        error(f"story {story_id} has invalid agents evidence")
    totals = {field: 0 for field in ("requests", "tool_invocations", *USAGE_FIELDS)}
    for agent in agents:
        if not isinstance(agent, dict) or not isinstance(agent.get("usage"), dict):
            error(f"story {story_id} has invalid agent evidence")
        if not is_nonnegative_int(agent.get("requests")):
            error(f"story {story_id} has invalid request evidence")
        totals["requests"] += agent["requests"]
        for field in USAGE_FIELDS:
            value = agent["usage"].get(field)
            if not is_nonnegative_int(value):
                error(f"story {story_id} has invalid {field} evidence")
            totals[field] += value
        tool_calls = agent.get("tool_calls")
        if not isinstance(tool_calls, dict) or not all(is_nonnegative_int(value) for value in tool_calls.values()):
            error(f"story {story_id} has invalid tool call evidence")
        totals["tool_invocations"] += sum(tool_calls.values())
    declared = story.get("totals", {})
    for field in ("requests", *USAGE_FIELDS):
        if declared.get(field) != totals[field]:
            error(f"story {story_id} declared {field} does not match reconstructed total")
    return {"schema_version": SCHEMA_VERSION, "story_id": story_id, **totals}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("extract", "harness"):
        command = commands.add_parser(name)
        command.add_argument("--metadata", required=True, type=Path)
        command.add_argument("--output", required=True, type=Path)
        command.add_argument("--append", action="store_true", help="append one JSON Lines record instead of replacing output")
        if name == "extract":
            command.add_argument("--transcript", required=True, type=Path)
    aggregate = commands.add_parser("aggregate")
    aggregate.add_argument("--input", required=True, type=Path)
    evidence = commands.add_parser("reconstruct-evidence")
    evidence.add_argument("--evidence", required=True, type=Path)
    evidence.add_argument("--story", required=True)
    args = parser.parse_args()
    try:
        if args.command == "extract":
            record = build_record(load_metadata(args.metadata), "raw_transcript", extract_usage(parse_transcript(args.transcript)))
            write_record(record, args.output, args.append)
        elif args.command == "harness":
            metadata = load_metadata(args.metadata)
            source = "harness_report" if metadata.get("session_final_tokens") is not None else "unavailable"
            record = build_record(metadata, source, None)
            write_record(record, args.output, args.append)
        elif args.command == "aggregate":
            print(json.dumps(summarize(read_records(args.input)), sort_keys=True))
        else:
            print(json.dumps(reconstruct_evidence(args.evidence, args.story), sort_keys=True))
    except TelemetryError as exc:
        print(f"telemetry: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
