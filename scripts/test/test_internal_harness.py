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
skeletons = load("render_skeleton")
validator_spec = importlib.util.spec_from_file_location("validate_internal", ROOT / "scripts/validate_internal_harness.py")
validator = importlib.util.module_from_spec(validator_spec)
validator_spec.loader.exec_module(validator)


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

    def test_runtime_roots_are_provider_local_and_reject_unsafe_identities(self):
        paths = {context.runtime_root(p, r, s) for p in self.manifests for r in ("run1", "run2") for s in ("ST-1", "ST-2")}
        self.assertEqual(3, len(paths))
        for provider in self.manifests:
            self.assertEqual(context.runtime_root(provider, "run1", "ST-1"),
                             context.runtime_root(provider, "run2", "ST-2"))
        for provider in self.manifests:
            self.assertEqual(f".{provider}/agents/working", context.runtime_root(provider, "run1", "ST-1"))
        for parts in (("codex", "../bad", "ST-1"), ("codex", "run1", "../../bad"), ("unknown", "run1", "ST-1")):
            with self.assertRaises(ValueError):
                context.runtime_root(*parts)


class RuntimeAndSkeletonTests(unittest.TestCase):
    def test_command_roots_preserve_provider_singletons_across_runs(self):
        roots = {context.command_root(p, r, c) for p in ("claude", "codex") for r in ("run1", "run2") for c in ("analyst", "audit-agent-files", "build-software")}
        self.assertEqual(2, len(roots))
        for provider in ("claude", "codex"):
            self.assertEqual(context.command_root(provider, "run1", "analyst"),
                             context.command_root(provider, "run2", "analyst"))
        self.assertEqual(".claude/agents", context.command_root("claude", "run1", "analyst"))
        for command in ("../audit", "/absolute", "audit/other"):
            with self.assertRaises(ValueError):
                context.command_root("codex", "run1", command)

    def test_missing_or_foreign_provider_configuration_blocks(self):
        from unittest.mock import patch
        for configuration in ({}, {"PROVIDER_ROOT": ".codex", "RUNTIME_ROOT": ".claude/agents/working", "COMMAND_ROOT": ".codex/agents"}):
            with patch.object(context.json, "loads", return_value=configuration):
                with self.assertRaises(ValueError):
                    context.state_bindings("codex")
        with patch.object(context.Path, "read_text", side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError):
                context.state_bindings("codex")

    def test_worker_packet_blocks_missing_unresolved_and_foreign_paths(self):
        expected = context.state_bindings("antigravity")
        for bindings in (None, {}, dict(expected, RUNTIME_ROOT="{RUNTIME_ROOT}"),
                         context.state_bindings("codex")):
            with self.assertRaises(ValueError):
                context.validate_state_bindings("antigravity", bindings)
        self.assertEqual(expected, context.validate_state_bindings("antigravity", expected))

    def test_selection_supplies_concrete_provider_bindings(self):
        tools = {"collaboration.spawn_agent", "collaboration.followup_task", "collaboration.send_message", "collaboration.wait_agent"}
        self.assertEqual(context.state_bindings("codex"), context.select_provider(tools)["bindings"])
        sprint = (ROOT / ".mt-agent-devkit/workflows/Sprint_Workflow.md").read_text(encoding="utf-8")
        self.assertIn("{RUNTIME_ROOT}/tmp/sprint_pipeline_state.md", sprint)
        self.assertNotIn("sprint_story_index", sprint)

    def test_rendered_skeleton_ci_matches_each_pinned_legacy_target(self):
        base = "62349287bc9835093a02586d8658993ba8ac685b"
        files = ("shared/CI_Bootstrap_Conventions.md", "java/Java_Skeleton_REST_Service.md", "java/Java_Skeleton_Library.md", "java/Java_Skeleton_Conventions.md")
        import re
        def generation_fragments(text):
            # Compare every fenced emitted artifact and inline CI trigger, not scaffold helpers.
            fences = re.findall(r"```[^\n]*\n(.*?)```", text, re.S)
            inline = [line for line in text.splitlines() if "paths-ignore:" in line]
            return fences, inline
        for provider in ("claude", "antigravity"):
            for relative in files:
                before = subprocess.run(("git", "show", f"{base}:.{provider}/agents/working/skeletons/{relative}"), cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")
                source = (ROOT / ".mt-agent-devkit/skeletons" / relative).read_text(encoding="utf-8")
                rendered = skeletons.render(source, f".{provider}")
                with self.subTest(provider=provider, source=relative):
                    self.assertEqual(generation_fragments(before), generation_fragments(rendered))
                    self.assertNotIn("{LIFECYCLE_ROOT}", rendered)
        self.assertEqual(skeletons.render("paths-ignore: ['{LIFECYCLE_ROOT}/**']", ".codex"), "paths-ignore: ['.codex/**']")
        with self.assertRaises(ValueError):
            skeletons.render("{LIFECYCLE_ROOT}", ".unknown")

    def test_missing_legacy_instruction_and_invalid_runtime_binding_fail(self):
        fixture = ROOT / "scripts/test/fixtures/bad/internal_missing_instruction.md"
        errors = validator.reference_errors(fixture.read_text(encoding="utf-8"), fixture.name)
        self.assertTrue(any("dangling executable legacy reference" in e for e in errors))
        for text in ("Read `{UNKNOWN_ROOT}/tmp/state.md`", "Read `{COMMAND_ROOT}/instructions/missing.md`", "Read `{RUN_ROOT}/tmp/../../other.md`"):
            self.assertTrue(validator.reference_errors(text, "fixture.md"))
        self.assertFalse(validator.reference_errors("Write `{COMMAND_ROOT}/tmp/analyst_workflow_state.md`", "fixture.md"))
        adapter = "Read `{PROVIDER_ROOT}/harness/Provider_Adapter.md`"
        self.assertFalse(validator.reference_errors(adapter, "fixture.md"))
        with tempfile.TemporaryDirectory() as tmp:
            fake_root = Path(tmp)
            for provider in ("claude", "antigravity", "codex"):
                path = fake_root / f".{provider}/harness/Provider_Adapter.md"
                path.parent.mkdir(parents=True)
                path.write_text("adapter", encoding="utf-8")
            self.assertFalse(validator.reference_errors(adapter, "fixture.md", root=fake_root))
            path.unlink()
            self.assertTrue(validator.reference_errors(adapter, "fixture.md", root=fake_root))
        for reference in ("{PROVIDER_ROOT}/harness/Missing.md", "{LIFECYCLE_ROOT}/harness/Provider_Adapter.md"):
            self.assertTrue(validator.reference_errors(reference, "fixture.md"))
        self.assertTrue(validator.reference_errors("Read `.claude/agents/working/instructions/missing.md`", "lifecycle.md", target_lifecycle=True))
        self.assertFalse(validator.reference_errors("Write `{TARGET_PROJECT}/.claude/settings.json`", "lifecycle.md", target_lifecycle=True))
        for marker in ("target paths", "Released target"):
            self.assertTrue(validator.reference_errors(marker + " `.mt-agent-devkit/scripts/nonexistent.py`", "lifecycle.md", target_lifecycle=True))
        self.assertFalse(validator.reference_errors("Released target `.mt-agent-devkit/scripts/sync.py`", "lifecycle.md", target_lifecycle=True))

    def test_internal_bindings_are_rejected_in_distributed_templates(self):
        spec = importlib.util.spec_from_file_location("template_validator", ROOT / "scripts/validate_templates.py")
        template_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(template_validator)
        for source, expected in ((".claude/agents/workflows/Build_Software_Workflow.md", 0),
                                 (".claude/agents/templates/workflows/Fixture_template.md", 1)):
            findings = []
            template_validator.check_placeholders(ROOT / source, ["Write `{COMMAND_ROOT}/tmp/state.md`"], [False], findings)
            self.assertEqual(expected, len(findings))

    def test_real_active_command_sources_use_registered_roots_and_canonical_role(self):
        analyst = (ROOT / ".mt-agent-devkit/workflows/commands/Analyst_Workflow.md").read_text(encoding="utf-8")
        audit = (ROOT / ".mt-agent-devkit/workflows/commands/Audit_Agent_Files_Workflow.md").read_text(encoding="utf-8")
        self.assertIn("{COMMAND_ROOT}/tmp/analyst_workflow_state.md", analyst)
        self.assertIn(".mt-agent-devkit/instructions/business_analyst_instructions.md", analyst)
        self.assertNotIn(".claude/agents/tmp/", analyst)
        self.assertIn("{COMMAND_ROOT}/internal/audit_report_", audit)
        self.assertNotIn(".claude/agents/internal/", audit)


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
        pipeline = (ROOT / ".mt-agent-devkit/workflows/Shared_Pipeline_Stages.md").read_text(encoding="utf-8")
        self.assertIn("## Worker Entry Read Contract", pipeline)
        self.assertIn("include this contract verbatim", pipeline)
        self.assertIn("only preparatory shell exception", pipeline)
        self.assertIn("persisted", pipeline)
        for role in ("developer", "technical_lead", "qa"):
            instruction = (ROOT / f".mt-agent-devkit/instructions/{role}_instructions.md").read_text(encoding="utf-8")
            self.assertIn("before any shell command", instruction)
            self.assertIn("Claude: `Read`", instruction)
            self.assertIn("mandatory full role-scoped read", instruction)
        bootstrap = (ROOT / ".mt-agent-devkit/rules/Agent_Common_Bootstrap.md").read_text(encoding="utf-8")
        self.assertIn("On-demand section extraction remains bounded", bootstrap)
        self.assertIn("preloaded summaries do not satisfy", bootstrap)


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


class MigrationPreservationTests(unittest.TestCase):
    def test_future_release_template_and_history_edits_are_not_frozen_by_ci(self):
        from unittest.mock import patch
        inventory = json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text())
        history = next(e["source"] for e in inventory["files"] if e["ownership"] == "preserved-history")
        template = next(p.relative_to(ROOT).as_posix() for p in (ROOT / ".claude/agents/templates").rglob("*.md"))
        changed = {"VERSION", template, history}
        original = Path.read_bytes
        def changed_bytes(path):
            data = original(path)
            return data + b"\nfuture legitimate update\n" if path.relative_to(ROOT).as_posix() in changed else data
        with patch.object(Path, "read_bytes", changed_bytes):
            self.assertEqual([], validator.validate())
            findings = validator.validate(migration_preservation=True)
        self.assertIn("Phase 2/release boundary violated: VERSION", findings)
        self.assertIn(f"Phase 2/release boundary violated: {template}", findings)
        self.assertIn(f"preserved history/helper changed: {history}", findings)

    def test_live_reference_checks_remain_enabled_without_frozen_audit(self):
        from unittest.mock import patch
        original = Path.read_text
        def broken_reference(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path == ROOT / ".mt-agent-devkit/contracts/Provider_Contract.md":
                text += "\nRead `.mt-agent-devkit/rules/missing_review_fixture.md`\n"
            return text
        with patch.object(Path, "read_text", broken_reference):
            self.assertTrue(any("missing_review_fixture" in e for e in validator.validate()))


if __name__ == "__main__":
    unittest.main()
