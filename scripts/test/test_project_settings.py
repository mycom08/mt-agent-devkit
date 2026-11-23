"""ST-000291, ST-000322: po_execution and agent_models resolution from the project-owned settings file."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
RESOLVER = ROOT / ".mt-agent-devkit/distribution/phase2/templates/scripts/project_settings.py"
spec = importlib.util.spec_from_file_location("project_settings", RESOLVER)
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)


class ProjectSettingsTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.path = self.root / settings.SETTINGS_PATH
        self.path.parent.mkdir(parents=True)

    def run_cli(self, *extra):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(settings.main(["po_execution", "--root", str(self.root), *extra]), 0)
        return stdout.getvalue(), stderr.getvalue()

    def test_absent_file_or_key_resolves_to_subagent_silently(self):
        self.assertEqual(settings.resolve(self.root, "po_execution"), ("subagent", None))
        self.path.write_text('{"other": 1}\n', encoding="utf-8")
        self.assertEqual(settings.resolve(self.root, "po_execution"), ("subagent", None))
        self.assertEqual(self.run_cli(), ("subagent\n", ""))

    def test_recognised_values_resolve_as_written(self):
        for value in settings.PO_EXECUTION_VALUES:
            with self.subTest(value=value):
                self.path.write_text(json.dumps({"po_execution": value}), encoding="utf-8")
                self.assertEqual(settings.resolve(self.root, "po_execution"), (value, None))
                self.assertEqual(self.run_cli(), (value + "\n", ""))

    def test_unrecognised_value_resolves_to_subagent_and_is_reported_once(self):
        for raw in ('{"po_execution": "Orchestrator"}', '{"po_execution": "inline"}', '{"po_execution": null}',
                    '{"po_execution": ["orchestrator"]}', "not json", "[]", '"orchestrator"'):
            with self.subTest(raw=raw):
                self.path.write_text(raw, encoding="utf-8")
                value, report = settings.resolve(self.root, "po_execution")
                self.assertEqual(value, "subagent")
                self.assertTrue(report)
                stdout, stderr = self.run_cli()
                self.assertEqual(stdout, "subagent\n")
                self.assertEqual(len(stderr.strip().splitlines()), 1)
                self.assertTrue(stderr.startswith("project_settings: "))

    def test_internal_settings_file_and_working_mirror_resolve(self):
        # The shipped bundle asset holds the default; the devkit's own file is project-owned and may differ.
        manifest = json.loads((ROOT / ".mt-agent-devkit/distribution/phase2/bundle/deployment.json").read_text(encoding="utf-8"))
        [item] = [f for f in manifest["files"] if f["destination"] == settings.SETTINGS_PATH]
        self.assertEqual((item["owner"], item["ownership"], item["renderer"]), ("shared", "project_owned", "create_if_absent"))
        [asset] = [a for a in manifest["assets"] if a["id"] == item["sources"][0]]
        bundle = ROOT / ".mt-agent-devkit/distribution/phase2/bundle" / asset["path"]
        self.assertEqual(json.loads(bundle.read_text(encoding="utf-8")), settings.DEFAULTS)
        result = subprocess.run([sys.executable, str(ROOT / ".mt-agent-devkit/scripts/project_settings.py"), "po_execution", "--root", str(ROOT)],
                                capture_output=True, text=True, check=True)
        # The devkit's own file may legitimately be set to either valid value, never reported.
        self.assertIn(result.stdout, ("subagent\n", "orchestrator\n"))
        self.assertEqual(result.stderr, "")


class AgentModelsTests(unittest.TestCase):
    """ST-000322: per-role and per-policy model and effort overrides."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.path = self.root / settings.SETTINGS_PATH
        self.path.parent.mkdir(parents=True)

    def write(self, value):
        self.path.write_text(value if isinstance(value, str) else json.dumps(value), encoding="utf-8")

    def resolve(self, role="Developer", policy="implementation"):
        return settings.resolve_agent_models(self.root, role, policy)

    def cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(settings.main(["agent_models", "--root", str(self.root), *args]), 0)
        return stdout.getvalue(), stderr.getvalue()

    def test_absent_file_key_or_empty_object_returns_no_override(self):
        self.assertEqual(self.resolve(), ({}, []))
        for value in ({"po_execution": "subagent"}, {"agent_models": {}}):
            with self.subTest(value=value):
                self.write(value)
                self.assertEqual(self.resolve(), ({}, []))
        self.assertEqual(self.cli("--role", "Developer", "--policy", "implementation"), ("{}\n", ""))

    def test_role_and_policy_overrides_resolve(self):
        self.write({"agent_models": {"Developer": {"model": "opus", "effort": "high"}, "closure": {"model": "haiku"}}})
        self.assertEqual(self.resolve("Developer", "implementation"), ({"model": "opus", "effort": "high"}, []))
        self.assertEqual(self.resolve("Product Owner", "closure"), ({"model": "haiku"}, []))
        self.assertEqual(self.resolve("QA", "standard"), ({}, []))
        self.assertEqual(self.cli("--policy", "closure"), ('{"model": "haiku"}\n', ""))

    def test_role_and_policy_merge_per_field_with_role_winning(self):
        self.write({"agent_models": {"Technical Lead": {"model": "opus"}, "design-review": {"model": "sonnet", "effort": "max"}}})
        self.assertEqual(self.resolve("Technical Lead", "design-review"), ({"model": "opus", "effort": "max"}, []))
        self.assertEqual(self.cli("--role", "Technical Lead", "--policy", "design-review"), ('{"effort": "max", "model": "opus"}\n', ""))

    def test_non_object_entry_or_non_string_value_gives_no_override_and_one_report(self):
        for entry in ("opus", ["opus"], None, {"model": 5}, {"model": ""}, {"effort": ["high"]}, {"model": "opus", "effort": 1}):
            with self.subTest(entry=entry):
                self.write({"agent_models": {"Developer": entry, "implementation": {"model": "sonnet"}}})
                override, reports = self.resolve()
                self.assertEqual(override, {"model": "sonnet"})
                self.assertEqual(len(reports), 1)
                stdout, stderr = self.cli("--role", "Developer", "--policy", "implementation")
                self.assertEqual(stdout, '{"model": "sonnet"}\n')
                self.assertEqual(len(stderr.strip().splitlines()), 1)
                self.assertTrue(stderr.startswith("project_settings: "))

    def test_unknown_role_policy_or_field_key_is_ignored_with_one_report(self):
        self.write({"agent_models": {"developer": {"model": "opus"}, "Planner": {"model": "opus"}, "Developer": {"model": "sonnet", "tier": "x"}}})
        override, reports = self.resolve()
        self.assertEqual(override, {"model": "sonnet"})
        self.assertEqual(len(reports), 3)
        self.assertEqual(self.resolve("developer", None), ({}, [r for r in reports if "unknown agent_models key" in r] + ['unknown role "developer"; no role override']))

    def test_unreadable_file_or_non_object_block_gives_no_override_and_one_report(self):
        for raw in ("not json", "[]", '{"agent_models": ["Developer"]}', '{"agent_models": "opus"}'):
            with self.subTest(raw=raw):
                self.write(raw)
                override, reports = self.resolve()
                self.assertEqual((override, len(reports)), ({}, 1))

    def test_precedence_each_tier_wins_over_the_tiers_below(self):
        tiers = ["user", "role", "policy", "adapter", "workflow"]
        for index, name in enumerate(tiers):
            with self.subTest(winner=name):
                supplied = {tier: {"model": tier + "-model", "effort": tier + "-effort"} for tier in tiers[index:]}
                self.assertEqual(settings.precedence(**supplied), {"model": name + "-model", "effort": name + "-effort"})
        self.assertEqual(settings.precedence(), {})
        self.assertEqual(settings.precedence(user={"effort": "low"}, role={"model": "opus", "effort": "high"}), {"model": "opus", "effort": "low"})

    def test_file_tier_composes_with_user_and_adapter_tiers(self):
        self.write({"agent_models": {"Developer": {"model": "opus"}}})
        file_tier, _ = self.resolve()
        self.assertEqual(settings.precedence(user={"effort": "low"}, role=file_tier, adapter={"model": "sonnet", "effort": "medium"}), {"model": "opus", "effort": "low"})

    def test_po_execution_is_unchanged_by_agent_models(self):
        self.write({"po_execution": "orchestrator", "agent_models": {"Developer": {"model": "opus"}}})
        self.assertEqual(settings.resolve(self.root, "po_execution"), ("orchestrator", None))
        self.assertEqual(settings.DEFAULTS, {"po_execution": "subagent"})
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit):
            settings.main(["po_execution", "--role", "Developer", "--root", str(self.root)])
        self.assertEqual(stdout.getvalue(), "")

    def test_devkit_script_mirror_prints_the_same_object(self):
        self.write({"agent_models": {"closure": {"model": "haiku"}}})
        result = subprocess.run([sys.executable, str(ROOT / ".mt-agent-devkit/scripts/project_settings.py"), "agent_models", "--policy", "closure", "--root", str(self.root)],
                                capture_output=True, text=True, check=True)
        self.assertEqual((json.loads(result.stdout), result.stderr), ({"model": "haiku"}, ""))


if __name__ == "__main__":
    unittest.main()
