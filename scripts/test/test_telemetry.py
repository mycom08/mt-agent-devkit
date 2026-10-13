"""Deterministic regression tests for the distributed telemetry collector."""

from __future__ import annotations

import json
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
COLLECTOR_PATH = ROOT / ".mt-agent-devkit" / "distribution" / "phase2" / "templates" / "scripts" / "telemetry.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "telemetry"
EVIDENCE = ROOT / "docs" / "reviews" / "Harness_Token_Usage_2026-09-18.json"

SPEC = importlib.util.spec_from_file_location("telemetry", COLLECTOR_PATH)
assert SPEC and SPEC.loader
telemetry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(telemetry)


class TelemetryTests(unittest.TestCase):
    def extract_complete(self) -> dict:
        metadata = telemetry.load_metadata(FIXTURES / "complete_metadata.json")
        return telemetry.build_record(
            metadata,
            "raw_transcript",
            telemetry.extract_transcript_usage(FIXTURES / "streamed_duplicate.jsonl"),
        )

    def test_streamed_messages_deduplicate_and_use_final_output(self) -> None:
        record = self.extract_complete()

        self.assertEqual(record["requests"], 2)
        self.assertEqual(record["tool_invocations"], 3)
        self.assertEqual(record["input_tokens"], 30)
        self.assertEqual(record["cache_creation_input_tokens"], 300)
        self.assertEqual(record["cache_read_input_tokens"], 3000)
        self.assertEqual(record["output_tokens"], 24)
        self.assertEqual(record["usage_source"], "raw_transcript")
        self.assertEqual(record["unavailable_fields"], ["session_final_tokens"])

    def test_final_result_replaces_partial_stream_output(self) -> None:
        usage = telemetry.extract_transcript_usage(FIXTURES / "streamed_with_result.jsonl")
        self.assertEqual(usage["requests"], 2)
        self.assertEqual(usage["tool_invocations"], 3)
        self.assertEqual(usage["input_tokens"], 30)
        self.assertEqual(usage["cache_read_input_tokens"], 3000)
        self.assertEqual(usage["output_tokens"], 240)

    def test_fresh_extraction_matches_the_frozen_legacy_collector(self) -> None:
        legacy_path = ROOT / ".claude/agents/templates/scripts/telemetry.py"
        legacy_spec = importlib.util.spec_from_file_location("legacy_telemetry", legacy_path)
        legacy = importlib.util.module_from_spec(legacy_spec)
        legacy_spec.loader.exec_module(legacy)
        for fixture in ("streamed_duplicate.jsonl", "streamed_with_result.jsonl", "reused_tool_id.jsonl"):
            with self.subTest(fixture=fixture):
                self.assertEqual(telemetry.extract_transcript_usage(FIXTURES / fixture),
                                 legacy.extract_transcript_usage(FIXTURES / fixture))

    def test_final_result_must_agree_with_request_usage(self) -> None:
        fixture = FIXTURES / "streamed_with_result.jsonl"
        with patch.object(Path, "read_text", return_value=fixture.read_text().replace('"input_tokens":30', '"input_tokens":31')):
            with self.assertRaisesRegex(telemetry.TelemetryError, "inconsistent final usage.input_tokens"):
                telemetry.extract_transcript_usage(fixture)

    def test_agent_id_lookup_extracts_only_the_matching_project_transcript(self) -> None:
        with tempfile.TemporaryDirectory(prefix="telemetry-agent-") as directory:
            root = Path(directory)
            project = root / "target"
            project.mkdir()
            config = root / "claude-config"
            key = telemetry.re.sub(r"[^A-Za-z0-9-]", "-", str(project.resolve()))
            folder = config / "projects" / key / "session-1" / "subagents"
            folder.mkdir(parents=True)
            transcript = folder / "agent-a0123456789abcdef.jsonl"
            transcript.write_bytes((FIXTURES / "streamed_with_result.jsonl").read_bytes())
            found = telemetry.find_claude_agent_transcript("a0123456789abcdef", project, config)
            self.assertEqual(found, transcript)
            self.assertEqual(telemetry.extract_transcript_usage(found)["requests"], 2)
            with self.assertRaisesRegex(telemetry.TelemetryError, "not found"):
                telemetry.find_claude_agent_transcript("b0123456789abcdef", project, config)
            with self.assertRaisesRegex(telemetry.TelemetryError, "filename-safe"):
                telemetry.find_claude_agent_transcript("../escape", project, config)
            second = config / "projects" / key / "session-2" / "subagents"
            second.mkdir(parents=True)
            (second / transcript.name).write_bytes(transcript.read_bytes())
            with self.assertRaisesRegex(telemetry.TelemetryError, "ambiguous"):
                telemetry.find_claude_agent_transcript("a0123456789abcdef", project, config)

    def test_extract_command_uses_agent_id_lookup_before_writing_record(self) -> None:
        with tempfile.TemporaryDirectory(prefix="telemetry-cli-") as directory:
            root = Path(directory)
            project = root / "target"
            project.mkdir()
            config = root / "claude-config"
            key = telemetry.re.sub(r"[^A-Za-z0-9-]", "-", str(project.resolve()))
            folder = config / "projects" / key / "session-1" / "subagents"
            folder.mkdir(parents=True)
            (folder / "agent-a0123456789abcdef.jsonl").write_bytes(
                (FIXTURES / "streamed_with_result.jsonl").read_bytes())
            output = root / "record.jsonl"
            argv = ["telemetry.py", "extract", "--agent-id", "a0123456789abcdef",
                    "--project-root", str(project), "--metadata",
                    str(FIXTURES / "complete_metadata.json"), "--output", str(output)]
            with patch.dict(telemetry.os.environ, {"CLAUDE_CONFIG_DIR": str(config)}), \
                    patch.object(telemetry.sys, "argv", argv):
                self.assertEqual(telemetry.main(), 0)
            record = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(record["usage_source"], "raw_transcript")
            self.assertEqual(record["requests"], 2)
            self.assertNotIn(str(config), json.dumps(record))

    def test_harness_only_usage_is_explicitly_unavailable(self) -> None:
        record = telemetry.build_record(
            telemetry.load_metadata(FIXTURES / "harness_only.json"), "harness_report", None
        )

        self.assertEqual(record["session_final_tokens"], 42000)
        self.assertEqual(record["usage_source"], "harness_report")
        self.assertEqual(
            record["unavailable_fields"],
            [
                "requests",
                "tool_invocations",
                "input_tokens",
                "cache_creation_input_tokens",
                "cache_read_input_tokens",
                "output_tokens",
            ],
        )
        for field in record["unavailable_fields"]:
            self.assertIsNone(record[field])

    def test_export_uses_a_strict_allowlist(self) -> None:
        record = self.extract_complete()

        rendered = json.dumps(record)
        self.assertNotIn("C:\\\\Users\\\\Example", rendered)
        self.assertNotIn("sensitive-value-not-exported", rendered)
        self.assertNotIn("prompt", record)
        self.assertNotIn("transcript_path", record)

    def test_malformed_transcript_fails_clearly(self) -> None:
        with self.assertRaisesRegex(telemetry.TelemetryError, "malformed JSON"):
            telemetry.parse_transcript(FIXTURES / "malformed.jsonl")

    def test_sensitive_absolute_path_fixture_is_rejected_before_export(self) -> None:
        with self.assertRaisesRegex(telemetry.TelemetryError, "local path"):
            telemetry.load_metadata(FIXTURES / "unsafe_metadata.json")

    def test_labeled_posix_and_windows_transcript_paths_are_rejected_before_export(self) -> None:
        for fixture in ("unsafe_posix_metadata.json", "unsafe_windows_metadata.json"):
            with self.subTest(fixture=fixture):
                with self.assertRaisesRegex(telemetry.TelemetryError, "local path"):
                    telemetry.load_metadata(FIXTURES / fixture)

    def test_url_notes_are_safe_but_local_windows_and_file_urls_are_rejected(self) -> None:
        telemetry.validate_text("notes", "https://example.com/a/b", allow_empty=True, max_length=280)
        for value in (
            "C:\\Users\\Example\\raw.jsonl",
            "transcript=C:\\Users\\Example\\raw.jsonl",
            "file:///home/example/raw.jsonl",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(telemetry.TelemetryError, "local path"):
                    telemetry.validate_text("notes", value, allow_empty=True, max_length=280)

    def test_writer_appends_one_json_lines_record_per_stage(self) -> None:
        record = self.extract_complete()
        target = Path("ignored.jsonl")
        with patch.object(Path, "mkdir") as mkdir, patch.object(Path, "open", mock_open()) as open_file:
            telemetry.write_record(record, target, append=True)
        mkdir.assert_called_once_with(parents=True, exist_ok=True)
        open_file.assert_called_once_with("a", encoding="utf-8")
        open_file.return_value.__enter__.return_value.write.assert_called_once()

    def test_writer_rejects_duplicate_stage_before_append(self) -> None:
        record = self.extract_complete()
        with patch.object(Path, "exists", return_value=True), patch.object(telemetry, "read_records", return_value=[record]):
            with self.assertRaisesRegex(telemetry.TelemetryError, "duplicate stage record"):
                telemetry.write_record(record, Path("ignored.jsonl"), append=True)

    def test_aggregation_keeps_role_stage_and_model_separate(self) -> None:
        complete = self.extract_complete()
        harness = telemetry.build_record(
            telemetry.load_metadata(FIXTURES / "harness_only.json"), "harness_report", None
        )
        report = telemetry.summarize(telemetry.validate_batch([complete, harness]))["runs"][0]
        groups = {(row["role"], row["stage"], row["model"]) for row in report["by_role_stage_model"]}
        self.assertEqual(groups, {("Developer", "implementation", "fixture-model"), ("QA", "qa", "unknown")})
        self.assertEqual(report["totals"]["requests"]["value"], None)
        self.assertEqual(report["totals"]["requests"]["availability"], "partial")
        self.assertEqual(report["totals"]["missing_field_count"], 7)

    def test_aggregation_never_blends_runs_or_partial_usage(self) -> None:
        complete = self.extract_complete()
        second_stage = dict(complete)
        second_stage.update({"stage": "review", "started_at": "2026-09-21T00:00:13Z", "ended_at": "2026-09-21T00:00:20Z"})
        unavailable_metadata = {**telemetry.load_metadata(FIXTURES / "harness_only.json"), "run_id": "fixture-run-002"}
        unavailable_metadata.pop("session_final_tokens")
        unavailable = telemetry.build_record(unavailable_metadata, "unavailable", None)
        report = telemetry.summarize(telemetry.validate_batch([complete, second_stage, unavailable]))
        self.assertEqual([run["run_id"] for run in report["runs"]], ["fixture-run-001", "fixture-run-002"])
        first_run = report["runs"][0]
        self.assertEqual(first_run["totals"]["requests"]["value"], 4)
        self.assertEqual(first_run["totals"]["requests"]["availability"], "complete")
        self.assertEqual(len(first_run["session_final_context"]), 2)
        self.assertNotIn("session_final_tokens", first_run["totals"])
        second_run = report["runs"][1]
        self.assertEqual(second_run["totals"]["cache_read_input_tokens"]["value"], None)
        self.assertEqual(second_run["totals"]["cache_read_input_tokens"]["availability"], "unavailable")

    def test_metadata_role_aliases_normalize_to_one_canonical_aggregation_role(self) -> None:
        alias_metadata = telemetry.load_metadata(FIXTURES / "harness_only.json")
        alias_metadata.update({"role": "Technical Lead", "stage": "review"})
        alias = telemetry.build_record(alias_metadata, "harness_report", None)
        canonical_metadata = telemetry.load_metadata(FIXTURES / "harness_only.json")
        canonical_metadata.update({"role": "TL", "stage": "approval"})
        canonical = telemetry.build_record(canonical_metadata, "harness_report", None)

        self.assertEqual(alias["role"], "TL")
        report = telemetry.summarize(telemetry.validate_batch([alias, canonical]))["runs"][0]
        self.assertEqual({row["role"] for row in report["by_role_stage_model"]}, {"TL"})
        self.assertEqual({row["role"] for row in report["session_final_context"]}, {"TL"})

    def test_schema_rejects_invalid_types_enums_timestamps_and_unsafe_text(self) -> None:
        record = self.extract_complete()
        cases = [
            ("schema_version", True, "unsupported schema version"),
            ("duration_ms", True, "non-negative integer"),
            ("requests", True, "non-negative integer"),
            ("session_mode", "resume", "session_mode is invalid"),
            ("completion_status", "done", "completion_status is invalid"),
            ("usage_source", "estimated", "usage_source is invalid"),
            ("role", "Untrusted role", "allowed agent role"),
            ("started_at", "2026-09-21T00:00:00+00:00", "ending in Z"),
            ("ended_at", "2026-09-20T00:00:00Z", "earlier"),
            ("notes", "C:\\Users\\Example\\secret.txt", "local path"),
            ("notes", "api_key=secret-value", "sensitive metadata"),
            ("model", "use C:\\local\\model", "local path"),
            ("run_id", "run-1\nignored", "single-line"),
        ]
        for field, value, message in cases:
            with self.subTest(field=field):
                invalid = dict(record)
                invalid[field] = value
                with self.assertRaisesRegex(telemetry.TelemetryError, message):
                    telemetry.validate_record(invalid)

    def test_unavailable_source_and_request_scoped_tool_ids(self) -> None:
        metadata = telemetry.load_metadata(FIXTURES / "harness_only.json")
        metadata.pop("session_final_tokens")
        unavailable = telemetry.build_record(metadata, "unavailable", None)
        self.assertEqual(unavailable["usage_source"], "unavailable")
        self.assertEqual(unavailable["unavailable_fields"], list(telemetry.OPTIONAL_FIELDS))
        usage = telemetry.extract_usage(telemetry.parse_transcript(FIXTURES / "reused_tool_id.jsonl"))
        self.assertEqual(usage["requests"], 2)
        self.assertEqual(usage["tool_invocations"], 2)

    def test_aggregation_rejects_duplicate_stages_and_mixed_schema(self) -> None:
        complete = self.extract_complete()
        with self.assertRaisesRegex(telemetry.TelemetryError, "duplicate stage record"):
            telemetry.validate_batch([complete, complete])
        incompatible = dict(complete)
        incompatible["schema_version"] = 2
        with self.assertRaisesRegex(telemetry.TelemetryError, "mixed schema versions"):
            telemetry.validate_batch([complete, incompatible])

    def test_st_000161_evidence_totals_reproduce_without_exporting_paths(self) -> None:
        report = telemetry.reconstruct_evidence(EVIDENCE, "ST-000161")
        self.assertEqual(report["requests"], 347)
        self.assertEqual(report["tool_invocations"], 374)
        self.assertEqual(report["cache_read_input_tokens"], 49_997_075)
        self.assertNotIn("source", json.dumps(report))


class BoundedTelemetryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="telemetry-bounded-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.path = self.root / "session.jsonl"
        self.lines = (FIXTURES / "bounded_session.jsonl").read_bytes().splitlines(keepends=True)
        self.expected = json.loads((FIXTURES / "bounded_expected.json").read_text())
        self.session = self.expected["session"]
        self.path.write_bytes(b"".join(self.lines[:3]))

    def capture(self) -> dict:
        return telemetry.capture_boundary(self.path, "claude", self.session)

    def interval(self, lines: list[bytes]) -> tuple[dict, dict]:
        start = self.capture()
        with self.path.open("ab") as stream:
            stream.write(b"".join(lines))
        return start, self.capture()

    def usage(self, start: dict, end: dict) -> dict:
        return telemetry.extract_bounded_usage(self.path, start, end, "claude", self.session)

    def test_fresh_and_two_resumes_reconcile_known_session_without_prior_usage(self) -> None:
        measured = [telemetry.extract_transcript_usage(self.path)]
        for left, right in ((3, 7), (7, 9)):
            measured.append(self.usage(*self.interval(self.lines[left:right])))
        self.assertEqual(measured, self.expected["stages"])
        self.assertEqual({field: sum(row[field] for row in measured) for field in measured[0]}, self.expected["whole"])
        # Re-extract an earlier bounded interval after another resume appended:
        first = self.capture()
        self.assertEqual(self.usage(first, first), {field: 0 for field in self.expected["whole"]})

    def test_finalized_request_evidence_deduplicates_streams_without_summary_substitution(self) -> None:
        events = [json.loads(line) for line in self.lines[3:7]]
        for event in events[:-1]:
            if event["message"]["usage"]["output_tokens"] == 6:
                event["message"]["stop_reason"] = "tool_use"
        # Generic session result has no verified cumulative semantics; ignore its totals.
        events[-1].pop("usage_scope")
        start, end = self.interval([(json.dumps(event) + "\n").encode() for event in events])
        usage = self.usage(start, end)
        self.assertEqual(usage["output_tokens"], 6)
        self.assertEqual(usage["requests"], 1)
        self.assertEqual(usage["tool_invocations"], 2)

    def test_equal_validated_bounds_prove_zero_but_empty_or_missing_source_does_not(self) -> None:
        boundary = self.capture()
        self.assertEqual(self.usage(boundary, boundary), {field: 0 for field in self.expected["whole"]})
        self.path.write_bytes(b"")
        with self.assertRaisesRegex(telemetry.TelemetryError, "unknown evidence"):
            self.capture()
        self.path.unlink()
        with self.assertRaisesRegex(telemetry.TelemetryError, "cannot read boundary transcript"):
            self.capture()

    def test_empty_discovery_and_wrong_worker_id_never_search_other_agents(self) -> None:
        project = self.root / "project"
        project.mkdir()
        with self.assertRaisesRegex(telemetry.TelemetryError, "not found"):
            telemetry.find_claude_agent_transcript("missing-agent", project, self.root / "config")
        with self.assertRaisesRegex(telemetry.TelemetryError, "ownership"):
            telemetry.capture_boundary(self.path, "claude", "foreign-session")
        with self.assertRaisesRegex(telemetry.TelemetryError, "only for Claude"):
            telemetry.capture_boundary(self.path, "codex", self.session)

    def test_worker_filename_and_native_checkpoint_identity_are_separate(self) -> None:
        worker = self.root / "agent-worker123.jsonl"
        worker.write_bytes(self.path.read_bytes())
        boundary = telemetry.capture_boundary(worker, "claude", "worker123")
        with worker.open("ab") as stream:
            stream.write(b"".join(self.lines[3:7]))
        end = telemetry.capture_boundary(worker, "claude", "worker123")
        self.assertEqual(telemetry.extract_bounded_usage(worker, boundary, end, "claude", "worker123"), self.expected["stages"][1])

    def test_boundary_rejects_invalid_types_offsets_digests_ownership_and_source(self) -> None:
        boundary = self.capture()
        variants = [("boundary_version", True), ("offset", True), ("offset", -1),
                    ("offset", boundary["offset"] + 1), ("sha256", "x"),
                    ("sha256", "0" * 64), ("session", "0" * 64),
                    ("provider", "codex"), ("source", "0" * 64), ("inode", 0)]
        for field, value in variants:
            with self.subTest(field=field, value=value):
                with self.assertRaises(telemetry.TelemetryError):
                    self.usage({**boundary, field: value}, boundary)
        with self.assertRaisesRegex(telemetry.TelemetryError, "format"):
            self.usage({**boundary, "raw_path": "forbidden"}, boundary)
        start, end = self.interval(self.lines[3:7])
        with self.assertRaisesRegex(telemetry.TelemetryError, "after end"):
            self.usage(end, start)

    def test_truncated_changed_and_replaced_transcripts_are_rejected(self) -> None:
        boundary = self.capture()
        original = self.path.read_bytes()
        for altered, expected in ((original[:-1], "truncated"), (original.replace(b"synthetic", b"different"), "prefix changed")):
            self.path.write_bytes(altered)
            with self.assertRaisesRegex(telemetry.TelemetryError, expected):
                self.usage(boundary, boundary)
        replacement = self.root / "replacement.jsonl"
        replacement.write_bytes(original)
        replacement.replace(self.path)
        with self.assertRaisesRegex(telemetry.TelemetryError, "replaced"):
            self.usage(boundary, boundary)

    def test_capture_rejects_malformed_partial_unicode_and_metric_records(self) -> None:
        bad_inputs = [b'{"type":"assistant"}\n', b'{"type":\n', b'[]\n', b'\xff\n',
                      b'{"type":"user","sessionId":"fixture-session"}',
                      b'{"type":"result","session_id":"fixture-session","usage":{}}\n']
        for data in bad_inputs:
            with self.subTest(data=data):
                self.path.write_bytes(data)
                with self.assertRaises(telemetry.TelemetryError):
                    self.capture()
        malformed = json.loads(self.lines[1])
        malformed["message"]["stop_reason"] = []
        self.path.write_bytes((json.dumps(malformed) + "\n").encode())
        with self.assertRaisesRegex(telemetry.TelemetryError, "completion evidence"):
            self.capture()

    def test_partial_request_without_comparable_checkpoints_is_unknown(self) -> None:
        start, end = self.interval(self.lines[3:6])
        with self.assertRaisesRegex(telemetry.TelemetryError, "finalized requests"):
            self.usage(start, end)

    def test_nonmonotonic_or_inconsistent_cumulative_metrics_fail_all_usage(self) -> None:
        original = self.path.read_bytes()
        for field, value in (("output_tokens", 1), ("input_tokens", 31), ("cache_read_input_tokens", 1)):
            self.path.write_bytes(original)
            events = [json.loads(line) for line in self.lines[3:7]]
            events[-1]["usage"][field] = value
            start, end = self.interval([(json.dumps(event) + "\n").encode() for event in events])
            with self.subTest(field=field):
                with self.assertRaises(telemetry.TelemetryError):
                    self.usage(start, end)

    def test_conflicting_native_checkpoint_sessions_and_definitions_fail(self) -> None:
        original = self.path.read_bytes()
        for field, value in (("session_id", "foreign"), ("usage_definition", "other-definition")):
            self.path.write_bytes(original)
            events = [json.loads(line) for line in self.lines[3:7]]
            events[-1][field] = value
            if field == "session_id":
                with self.path.open("ab") as stream:
                    stream.write(b"".join((json.dumps(event) + "\n").encode() for event in events))
                with self.assertRaisesRegex(telemetry.TelemetryError, "session identities"):
                    self.capture()
            else:
                start, end = self.interval([(json.dumps(event) + "\n").encode() for event in events])
                with self.assertRaisesRegex(telemetry.TelemetryError, "finalized requests"):
                    self.usage(start, end)

    def test_cross_boundary_request_and_conflicting_duplicates_fail(self) -> None:
        original = self.path.read_bytes()
        start, end = self.interval([self.lines[1]])
        with self.assertRaisesRegex(telemetry.TelemetryError, "crosses"):
            self.usage(start, end)
        self.path.write_bytes(original)
        event = json.loads(self.lines[4])
        changed = json.loads(self.lines[4])
        changed["message"]["content"][0]["name"] = "conflict"
        with self.path.open("ab") as stream:
            stream.write((json.dumps(event) + "\n" + json.dumps(changed) + "\n").encode())
        with self.assertRaisesRegex(telemetry.TelemetryError, "conflicting duplicate tool"):
            self.capture()

    def test_unattributed_cumulative_usage_and_nonempty_unknown_stage_do_not_prove_zero(self) -> None:
        start, end = self.interval([self.lines[6]])
        with self.assertRaises(telemetry.TelemetryError):
            self.usage(start, end)
        self.path.write_bytes(b"".join(self.lines[:3]))
        start, end = self.interval([b'{"type":"user","sessionId":"fixture-session"}\n'])
        with self.assertRaisesRegex(telemetry.TelemetryError, "no complete attributable"):
            self.usage(start, end)

    def test_snapshots_and_sanitized_records_exclude_paths_secrets_and_prompts(self) -> None:
        original = self.path.read_bytes().replace(b"synthetic fixture", b"secret-value-not-exported")
        self.path.write_bytes(original)
        start, end = self.interval(self.lines[3:7])
        metadata = telemetry.load_metadata(FIXTURES / "complete_metadata.json")
        metadata["session_mode"] = "same_session_resume"
        record = telemetry.build_record(metadata, "raw_transcript", self.usage(start, end))
        rendered = json.dumps([start, end, record])
        for forbidden in (str(self.root), "secret-value-not-exported", "synthetic fixture", self.session):
            self.assertNotIn(forbidden, rendered)

    def test_boundary_publish_is_atomic_and_interruption_keeps_previous_artifact(self) -> None:
        output = self.root / "boundary.json"
        output.write_text("existing")
        with patch.object(telemetry.os, "replace", side_effect=OSError("interrupted")):
            with self.assertRaisesRegex(telemetry.TelemetryError, "cannot publish"):
                telemetry.write_boundary(self.capture(), output)
        self.assertEqual(output.read_text(), "existing")
        self.assertEqual(list(self.root.glob(".boundary-*")), [])
        telemetry.write_boundary(self.capture(), output)
        self.assertEqual(json.loads(output.read_text()), self.capture())

    def test_extract_cli_requires_both_bounds_and_rejects_unbounded_resume_and_interruption(self) -> None:
        metadata = telemetry.load_metadata(FIXTURES / "complete_metadata.json")
        metadata["session_mode"] = "same_session_resume"
        meta = self.root / "metadata.json"
        meta.write_text(json.dumps(metadata))
        output = self.root / "record.json"
        base = ["telemetry.py", "extract", "--transcript", str(self.path), "--metadata", str(meta), "--output", str(output)]
        with patch.object(telemetry.sys, "argv", base):
            self.assertEqual(telemetry.main(), 1)
        with patch.object(telemetry.sys, "argv", base + ["--provider", "codex"]):
            self.assertEqual(telemetry.main(), 1)
        start, end = self.interval(self.lines[3:7])
        for name, value in (("start", start), ("end", end)):
            telemetry.write_boundary(value, self.root / f"{name}.json")
        bounded = base + ["--provider", "claude", "--session-id", self.session,
                          "--start-boundary", str(self.root / "start.json"), "--end-boundary", str(self.root / "end.json")]
        with patch.object(telemetry.sys, "argv", bounded):
            self.assertEqual(telemetry.main(), 0)
        self.assertEqual(json.loads(output.read_text())["output_tokens"], 60)
        output.unlink()
        with patch.object(telemetry.sys, "argv", bounded[:-2]):
            self.assertEqual(telemetry.main(), 1)
        metadata["completion_status"] = "interrupted"
        meta.write_text(json.dumps(metadata))
        with patch.object(telemetry.sys, "argv", bounded):
            self.assertEqual(telemetry.main(), 1)
        self.assertFalse(output.exists())

    def test_cli_agent_discovery_captures_and_extracts_the_owned_interval(self) -> None:
        project, config = self.root / "project", self.root / "config"
        project.mkdir()
        key = telemetry.re.sub(r"[^A-Za-z0-9-]", "-", str(project.resolve()))
        folder = config / "projects" / key / "native-parent" / "subagents"
        folder.mkdir(parents=True)
        worker = folder / "agent-worker123.jsonl"
        worker.write_bytes(self.path.read_bytes())
        original = worker.read_bytes()
        common = ["--agent-id", "worker123", "--project-root", str(project),
                  "--provider", "claude", "--session-id", "worker123"]
        with patch.dict(telemetry.os.environ, {"CLAUDE_CONFIG_DIR": str(config)}):
            for name in ("start", "end"):
                if name == "end":
                    with worker.open("ab") as stream:
                        stream.write(b"".join(self.lines[3:7]))
                argv = ["telemetry.py", "boundary", *common, "--output", str(self.root / f"{name}.json")]
                with patch.object(telemetry.sys, "argv", argv):
                    self.assertEqual(telemetry.main(), 0)
            metadata = telemetry.load_metadata(FIXTURES / "complete_metadata.json")
            metadata["session_mode"] = "same_session_resume"
            meta = self.root / "metadata.json"
            meta.write_text(json.dumps(metadata))
            output = self.root / "record.json"
            argv = ["telemetry.py", "extract", *common, "--metadata", str(meta), "--output", str(output),
                    "--start-boundary", str(self.root / "start.json"), "--end-boundary", str(self.root / "end.json")]
            with patch.object(telemetry.sys, "argv", argv):
                self.assertEqual(telemetry.main(), 0)
            self.assertEqual(json.loads(output.read_text())["output_tokens"], 60)
            self.assertEqual(worker.read_bytes(), original + b"".join(self.lines[3:7]))
            with patch.object(telemetry.sys, "argv", ["telemetry.py", "boundary", *common, "--output", str(worker)]):
                self.assertEqual(telemetry.main(), 1)
            with patch.object(telemetry.sys, "argv", ["telemetry.py", "boundary", *common[:-1], "foreign", "--output", str(output)]):
                self.assertEqual(telemetry.main(), 1)

    def test_read_race_and_read_interruption_are_actionable_errors(self) -> None:
        identity = self.path.stat()
        changed = SimpleNamespace(**{field: getattr(identity, field) for field in ("st_mode", "st_dev", "st_ino", "st_size", "st_mtime_ns")})
        changed.st_mtime_ns += 1
        with patch.object(telemetry.os, "fstat", side_effect=[identity, changed]):
            with self.assertRaisesRegex(telemetry.TelemetryError, "changed during"):
                self.capture()
        with patch.object(Path, "open", side_effect=OSError("interrupted secret local-path")):
            with self.assertRaisesRegex(telemetry.TelemetryError, "cannot read boundary transcript") as context:
                self.capture()
        self.assertNotIn("secret", str(context.exception))

    def test_finalized_output_conflict_and_late_unbounded_records_are_rejected_or_excluded(self) -> None:
        events = [json.loads(line) for line in self.lines[3:6]]
        for event in events:
            event["message"]["stop_reason"] = "tool_use"
        with self.path.open("ab") as stream:
            stream.write(b"".join((json.dumps(event) + "\n").encode() for event in events))
        with self.assertRaisesRegex(telemetry.TelemetryError, "conflicting finalized"):
            self.capture()
        self.path.write_bytes(b"".join(self.lines[:3]))
        start, end = self.interval(self.lines[3:7])
        with self.path.open("ab") as stream:
            stream.write(b"malformed future stage\n")
        self.assertEqual(self.usage(start, end), self.expected["stages"][1])


if __name__ == "__main__":
    unittest.main()
