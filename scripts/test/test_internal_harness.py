"""Adversarial routing/preservation tests, not native provider behavioral evidence."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    path = ROOT / f".mt-agent-devkit/scripts/{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context = load("provider_context")
sections = load("read_section")
wrappers = load("generate_wrappers")


class ProviderSelectionTests(unittest.TestCase):
    def setUp(self):
        self.manifests = {p: {"operations": {op: f"{p}.{op}" for op in context.REQUIRED}}
                          for p in ("claude", "codex", "antigravity")}

    def tools(self, *providers):
        return {tool for p in providers for tool in self.manifests[p]["operations"].values()}

    def test_each_provider_selects_only_its_adapter(self):
        for provider in self.manifests:
            selected = context.select_provider(self.tools(provider), manifests=self.manifests)
            self.assertEqual(provider, selected["provider"])
            self.assertEqual(f".{provider}/harness/Provider_Adapter.md", selected["adapter"])

    def test_none_ambiguous_and_conflicting_declarations_block(self):
        for tools, declared in ((set(), None), (self.tools("claude", "codex"), None),
                                (self.tools("codex"), "claude"), (self.tools("codex"), "unknown")):
            with self.assertRaises(ValueError):
                context.select_provider(tools, declared, self.manifests)

    def test_declared_available_provider_resolves_multiple(self):
        result = context.select_provider(self.tools("claude", "codex"), "codex", self.manifests)
        self.assertEqual("codex", result["provider"])

    def test_each_missing_required_operation_blocks(self):
        for operation in context.REQUIRED:
            tools = self.tools("codex") - {f"codex.{operation}"}
            with self.assertRaises(ValueError):
                context.select_provider(tools, "codex", self.manifests)

    def test_default_antigravity_candidates_are_not_verified_operations(self):
        names = {"define_subagent", "invoke_subagent", "send_message", "conversationId"}
        with self.assertRaises(ValueError):
            context.select_provider(names, "antigravity")

    def test_codex_maps_exposed_collaboration_tools(self):
        tools = {"collaboration.spawn_agent", "collaboration.followup_task", "collaboration.send_message", "collaboration.wait_agent"}
        self.assertEqual("codex", context.select_provider(tools)["provider"])

    def test_runtime_identity_prevents_collision_and_path_escape(self):
        paths = {context.runtime_root(p, r, s) for p in self.manifests for r in ("run1", "run2") for s in ("ST-1", "ST-2")}
        self.assertEqual(12, len(paths))
        for parts in (("codex", "../bad", "ST-1"), ("codex", "run1", "../../bad"), ("unknown", "run1", "ST-1")):
            with self.assertRaises(ValueError):
                context.runtime_root(*parts)


class SectionAndWrapperTests(unittest.TestCase):
    def test_cli_emits_unicode_through_ascii_windows_pipe(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "scripts/test") as tmp:
            path = Path(tmp) / "unicode.md"
            path.write_text("## 1. Unicode\n≤ — résumé\n## 2. Next\n", encoding="utf-8")
            env = dict(os.environ, PYTHONIOENCODING="ascii")
            result = subprocess.run((sys.executable, str(ROOT / ".mt-agent-devkit/scripts/read_section.py"), str(path), r"^## [0-9]+\.", r"^## 1\."), capture_output=True, env=env)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("≤ — résumé", result.stdout.decode("utf-8"))
            self.assertNotIn("## 2.", result.stdout.decode("utf-8"))

    def test_real_canonical_and_legacy_wrapper_extract_only_triggered_section(self):
        canonical = ROOT / ".mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md"
        legacy = ROOT / ".antigravity/agents/working/rules/Agent_Common_Read_On_Demand.md"
        marker = r"^## ([0-9]+[a-z]?\.|Version)"
        a = sections.extract(canonical, marker, r"^## 5\.")
        b = sections.extract(legacy, marker, r"^## 5\.")
        self.assertEqual(a, b)
        self.assertIn("## 5.", a)
        self.assertNotIn("## 6.", a)
        self.assertNotIn("## 1.", a)

    def test_missing_or_ambiguous_section_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "scripts/test") as tmp:
            path = Path(tmp) / "rules.md"
            path.write_text("## 1. First\nA\n## 2. Next\nB\n")
            for target in (r"^## 9\.", r"^## [12]\."):
                with self.assertRaises(ValueError):
                    sections.extract(path, r"^## [0-9]+\.", target)

    def test_bootstrap_wrapper_requires_full_canonical_read(self):
        entry = {"source": ".claude/agents/working/rules/Agent_Common_Bootstrap.md", "destination": ".mt-agent-devkit/rules/Agent_Common_Bootstrap.md"}
        text = wrappers.render(entry)
        self.assertIn("Reading this\nwrapper alone does not satisfy", text)
        self.assertIn("Read the canonical bootstrap in full", text)

    def test_on_demand_wrapper_never_full_loads(self):
        entry = {"source": ".claude/agents/working/rules/Agent_Common_Read_On_Demand.md", "destination": ".mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md"}
        text = wrappers.render(entry)
        self.assertIn("Read only the triggered numbered section", text)
        self.assertIn("Do not load the complete on-demand file", text)
        self.assertNotIn("in full", text)

    def test_all_wrappers_match_generated_owner(self):
        inventory = json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text())
        for entry in inventory["files"]:
            if entry["ownership"] == "generated-wrapper":
                with self.subTest(source=entry["source"]):
                    self.assertEqual(wrappers.render(entry), (ROOT / entry["source"]).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
