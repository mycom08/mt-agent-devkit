"""Deterministic regression tests for the distributed telemetry collector."""

from __future__ import annotations

import json
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch


ROOT = Path(__file__).resolve().parents[2]
COLLECTOR_PATH = ROOT / ".claude" / "agents" / "templates" / "scripts" / "telemetry.py"
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
            telemetry.extract_usage(telemetry.parse_transcript(FIXTURES / "streamed_duplicate.jsonl")),
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


if __name__ == "__main__":
    unittest.main()
