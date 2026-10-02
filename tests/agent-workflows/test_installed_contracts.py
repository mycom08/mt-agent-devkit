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
    def test_workflow_models_accept_opus_tl_and_haiku_po_but_reject_wrong_family(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            path = target / ".claude/agents/tmp/token-metrics/run.jsonl"
            path.parent.mkdir(parents=True)
            rows = records()
            for row in rows:
                row["model"] = "claude-" + c.STAGE_MODEL_FAMILIES[row["stage"]] + "-test"
            path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            self.assertTrue(c.inspect_telemetry(target, c.STAGE_MODEL_FAMILIES)["measured_usage_for_every_stage"])
            rows[1]["model"] = "claude-sonnet-test"
            path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            self.assertFalse(c.inspect_telemetry(target, c.STAGE_MODEL_FAMILIES)["schema_and_identity_valid"])

    def test_snapshot_rejects_context_role_and_extra_file_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / "CLAUDE.md").write_text("strict", encoding="utf-8")
            for name in ("developer_instructions.md", "context/Project_Priming.md", "rules/extra.md"):
                path = target / ".claude/agents" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("frozen", encoding="utf-8")
            reference = c.installed_snapshot(target)
            for name in ("developer_instructions.md", "context/Project_Priming.md", "rules/extra.md"):
                path = target / ".claude/agents" / name
                path.write_text("changed", encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(ValueError):
                    c.validate_installation_parity(c.installed_snapshot(target), reference)
                path.write_text("frozen", encoding="utf-8")
            (target / ".claude/agents/extra.md").write_text("extra", encoding="utf-8")
            with self.assertRaises(ValueError):
                c.validate_installation_parity(c.installed_snapshot(target), reference)

    def test_only_exact_source_guidance_is_canonicalized(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            snapshots = []
            for arm in ("baseline", "candidate"):
                target, source = root / arm / "target", root / arm / "source"
                installed = target / ".claude/agents/rules/Agent_Common_Bootstrap.md"
                installed.parent.mkdir(parents=True)
                template = source / c.GUIDANCE_FILES[0]
                template.parent.mkdir(parents=True)
                template.write_text("# " + arm + "\n{{AGENT_DIR_PREFIX}}\n", encoding="utf-8")
                installed.write_text("# " + arm + "\n.claude\n", encoding="utf-8")
                snapshots.append(c.installed_snapshot(target, source))
                installed.write_text("unapproved guidance", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "pinned source"):
                    c.installed_snapshot(target, source)
            c.validate_installation_parity(*snapshots)

    def test_shared_guidance_matches_scaffold_combination_and_substitutions(self):
        with tempfile.TemporaryDirectory() as folder:
            target, source = Path(folder) / "target", Path(folder) / "source"
            shared = source / c.GUIDANCE_FILES[1]
            shared.parent.mkdir(parents=True)
            shared.write_text("<!-- header -->\n<!-- SHARED-START -->\n# Shared\n{{ROOT_FILE}}\n<!-- SHARED-END -->\n", encoding="utf-8")
            mode = source / ".claude/agents/templates/strict/workflows/Create_Stories_Workflow_template.md"
            mode.parent.mkdir(parents=True)
            mode.write_text("<!-- Shared logic -->\n\n<!-- comment -->\n# Strict\n{{AGENT_DIR_PREFIX}}\n\n", encoding="utf-8")
            installed = target / ".claude/agents/workflows/Create_Stories_Workflow.md"
            installed.parent.mkdir(parents=True)
            installed.write_text("# Shared\nCLAUDE.md\n\n---\n\n# Strict\n.claude\n", encoding="utf-8")
            c.installed_snapshot(target, source)
            installed.write_text(installed.read_text(encoding="utf-8") + "extra", encoding="utf-8")
            with self.assertRaises(ValueError):
                c.installed_snapshot(target, source)

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
