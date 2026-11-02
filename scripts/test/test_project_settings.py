"""ST-000291: po_execution resolution from the project-owned settings file."""
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
        # The devkit's own file holds the default, byte-identical to the bundle asset.
        manifest = json.loads((ROOT / ".mt-agent-devkit/distribution/phase2/bundle/deployment.json").read_text(encoding="utf-8"))
        [item] = [f for f in manifest["files"] if f["destination"] == settings.SETTINGS_PATH]
        self.assertEqual((item["owner"], item["ownership"], item["renderer"]), ("shared", "project_owned", "create_if_absent"))
        [asset] = [a for a in manifest["assets"] if a["id"] == item["sources"][0]]
        bundle = ROOT / ".mt-agent-devkit/distribution/phase2/bundle" / asset["path"]
        self.assertEqual(bundle.read_bytes(), (ROOT / settings.SETTINGS_PATH).read_bytes())
        self.assertEqual(json.loads(bundle.read_text(encoding="utf-8")), settings.DEFAULTS)
        result = subprocess.run([sys.executable, str(ROOT / ".mt-agent-devkit/scripts/project_settings.py"), "po_execution", "--root", str(ROOT)],
                                capture_output=True, text=True, check=True)
        self.assertEqual((result.stdout, result.stderr), ("subagent\n", ""))


if __name__ == "__main__":
    unittest.main()
