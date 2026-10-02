"""Adversarial installed benchmark contract checks; no agent sessions."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location("contracts_test", Path(__file__).with_name("installed_contracts.py"))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def records():
    return [c.telemetry.build_record({"run_id": "wf002-test", "story_id": "ST-000211",
        "role": role, "stage": stage, "session_mode": "fresh", "model": "pinned-model",
        "started_at": "2026-10-02T00:00:00Z", "ended_at": "2026-10-02T00:00:01Z",
        "duration_ms": 1000, "completion_status": "completed", "notes": ""}, "raw_transcript",
        {"requests": 2, "tool_invocations": 3, "input_tokens": 10,
         "cache_creation_input_tokens": 0, "cache_read_input_tokens": 100, "output_tokens": 5})
        for stage, role in c.STAGE_ROLES.items()]


class ContractTests(unittest.TestCase):
    def test_frozen_configuration_rejects_each_changed_field_and_extra_keys(self):
        frozen = {"cli": "pinned", "refs": {"baseline": "a", "candidate": "b"}, "budget": 4}
        c.validate_configuration(copy.deepcopy(frozen), frozen)
        for key in frozen:
            actual = copy.deepcopy(frozen)
            actual[key] = "changed"
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "drift"):
                c.validate_configuration(actual, frozen)
        with self.assertRaises(ValueError):
            c.validate_configuration(dict(frozen, extra=True), frozen)

    def test_source_delta_rejects_missing_or_extra_distributed_changes(self):
        for changed in (c.GUIDANCE_FILES, c.GUIDANCE_FILES[:-1], c.GUIDANCE_FILES + ["telemetry.py"]):
            command = Mock(return_value=Mock(stdout="\n".join(changed)))
            if changed == c.GUIDANCE_FILES:
                c.validate_template_delta(command, {"baseline": "a", "candidate": "b"})
            else:
                with self.assertRaises(ValueError):
                    c.validate_template_delta(command, {"baseline": "a", "candidate": "b"})

    def test_telemetry_rejects_schema_identity_timing_and_model_corruption(self):
        mutations = [("requests", -1), ("requests", True), ("schema_version", 2), ("schema_version", []),
                     ("role", "QA"), ("story_id", "ST-other"), ("run_id", "other-run"),
                     ("duration_ms", 0), ("ended_at", "2026-10-01T00:00:00Z"),
                     ("model", "other-model"), ("completion_status", "blocked"),
                     ("session_mode", "same_session_resume"), ("unavailable_fields", [])]
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            metrics = target / ".claude/agents/tmp/token-metrics"
            metrics.mkdir(parents=True)
            path = metrics / "run.jsonl"
            def write(rows):
                path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
            write(records())
            self.assertTrue(c.inspect_telemetry(target, "pinned-model")["measured_usage_for_every_stage"])
            for key, value in mutations:
                rows = records()
                rows[0][key] = value
                write(rows)
                with self.subTest(key=key, value=value):
                    self.assertFalse(c.inspect_telemetry(target, "pinned-model")["schema_and_identity_valid"])
            rows = records()
            del rows[0]["notes"]
            write(rows)
            self.assertFalse(c.inspect_telemetry(target)["schema_and_identity_valid"])
            write(records())
            (metrics / "duplicate.jsonl").write_text(json.dumps(records()[0]), encoding="utf-8")
            self.assertFalse(c.inspect_telemetry(target)["measured_usage_for_every_stage"])

    def test_valid_unavailable_record_stays_valid_but_unmeasured(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            path = target / ".claude/agents/tmp/token-metrics/run.jsonl"
            path.parent.mkdir(parents=True)
            rows = records()
            for field in c.telemetry.OPTIONAL_FIELDS:
                rows[0][field] = None
            rows[0]["unavailable_fields"] = list(c.telemetry.OPTIONAL_FIELDS)
            rows[0]["usage_source"] = "unavailable"
            path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
            result = c.inspect_telemetry(target)
            self.assertTrue(result["schema_and_identity_valid"])
            self.assertFalse(result["measured_usage_for_every_stage"])

    def test_review_evidence_requires_exact_sha_distinct_sessions_and_hashed_traces(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "target"
            target.mkdir()
            path = root / "quality-review.json"
            sha = "a" * 40
            self.assertFalse(c.inspect_review_evidence(path, target, sha)["evidence_valid"])
            evidence = {"schema_version": 1, "implementation_sha": sha,
                        "developer_session_id": "developer", "reviews": {}}
            for role in ("TL", "QA"):
                transcript = root / (role + ".jsonl")
                transcript.write_text(role + " trace", encoding="utf-8")
                evidence["reviews"][role] = {"verdict": "approved", "reviewed_sha": sha,
                    "session_id": role, "transcript": transcript.name,
                    "transcript_sha256": c.digest(transcript)}
            def inspect(data):
                path.write_text(json.dumps(data), encoding="utf-8")
                return c.inspect_review_evidence(path, target, sha)["evidence_valid"]
            self.assertTrue(inspect(evidence))
            for key, value in (("reviewed_sha", "b" * 40), ("session_id", "developer"),
                               ("verdict", "pending"), ("transcript_sha256", "0" * 64),
                               ("transcript", "../escape.jsonl")):
                invalid = copy.deepcopy(evidence)
                invalid["reviews"]["TL"][key] = value
                with self.subTest(key=key):
                    self.assertFalse(inspect(invalid))
            invalid = copy.deepcopy(evidence)
            invalid["reviews"]["TL"] = copy.deepcopy(invalid["reviews"]["QA"])
            self.assertFalse(inspect(invalid))


if __name__ == "__main__":
    unittest.main()
