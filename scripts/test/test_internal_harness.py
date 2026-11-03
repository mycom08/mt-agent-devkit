"""Adversarial routing/preservation tests, not native provider behavioral evidence."""
import hashlib
import importlib.util
import json
import re
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
            if role == "developer":
                self.assertNotIn("| Story Standard (Dev)", instruction)
                self.assertIn("Developer_Rules_Bootstrap.md", instruction)
                self.assertIn("Standing Checks", instruction)
            else:
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


class CodexReceiptPersistenceTests(unittest.TestCase):
    def setUp(self):
        # Reuse the bounded routing fixture, not an operational worker's state.
        from scripts.test import test_read_manifest as fixtures
        fixture = fixtures.RoutingTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.root = fixture.root
        helper_spec = importlib.util.spec_from_file_location(
            "codex_receipts", ROOT / ".codex/harness/persist_read_receipts.py")
        self.helper = importlib.util.module_from_spec(helper_spec)
        helper_spec.loader.exec_module(self.helper)
        self.routing = self.helper.routing
        self.manifest = fixture.build(session_state="same", delta=fixture.delta())
        self.manifest_source = ".codex/agents/working/tmp/manifest.json"
        self.receipts_source = ".codex/agents/working/tmp/attestations.json"
        self.path = self.root / self.manifest_source
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.write(self.manifest_source, self.manifest)
        self.receipt = self.routing.attest(
            self.root, self.manifest, "bootstrap",
            returned_complete=True, truncation_recovered=True)
        self.write(self.receipts_source, [self.receipt])

    def write(self, source, value):
        path = self.root / source
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def persist(self):
        return self.helper.persist(self.root, self.manifest_source, self.receipts_source)

    def test_same_session_receipt_rebuilds_omissions_and_keeps_context_reads(self):
        self.assertEqual("PASS", self.persist()["status"])
        result = self.routing.validate(self.root, self.routing.load(self.path))
        self.assertIn("bootstrap", {entry["id"] for entry in result["omitted"]})
        self.assertNotIn("bootstrap", {entry["id"] for entry in result["reads"]})
        self.assertTrue({"context_story", "context_decisions", "context_delta"}
                        <= {entry["id"] for entry in result["reads"]})

    def test_fresh_and_expired_sessions_keep_mandatory_reads(self):
        for state in ("fresh", "expired"):
            with self.subTest(state=state):
                self.manifest["request"]["session_state"] = state
                fresh = self.routing.build(self.root, self.manifest["request"])
                self.write(self.manifest_source, fresh)
                self.persist()
                result = self.routing.validate(self.root, self.routing.load(self.path))
                self.assertEqual([], result["omitted"])
                self.assertIn("bootstrap", {entry["id"] for entry in result["reads"]})

    def test_retry_is_idempotent_without_replacing_manifest_again(self):
        from unittest.mock import patch
        self.persist()
        before = self.path.read_bytes()
        with patch.object(self.helper.os, "replace") as replace:
            self.persist()
        replace.assert_not_called()
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(1, len(self.routing.load(self.path)["receipts"]))

    def test_invalid_attestations_preserve_original_manifest(self):
        before = self.path.read_bytes()
        for field, value in (("session", "another-worker"), ("provider", "claude"),
                             ("content_sha256", "0" * 64),
                             ("coverage", {"kind": "section", "section": "1"}),
                             ("returned_coverage", "partial"),
                             ("truncation_recovered", False)):
            with self.subTest(field=field):
                self.write(self.receipts_source, [{**self.receipt, field: value}])
                with self.assertRaises(self.routing.Blocked):
                    self.persist()
                self.assertEqual(before, self.path.read_bytes())
        self.write(self.receipts_source, [self.receipt, {**self.receipt, "session": "other"}])
        with self.assertRaises(self.routing.Blocked):
            self.persist()
        self.assertEqual(before, self.path.read_bytes())

    def test_outside_runtime_or_other_layout_is_rejected(self):
        before = self.path.read_bytes()
        self.write("docs/receipts.json", [self.receipt])
        for source in ("docs/receipts.json", "../outside.json"):
            with self.subTest(source=source), self.assertRaises(self.routing.Blocked):
                self.helper.persist(self.root, self.manifest_source, source)
        with self.assertRaises(self.routing.Blocked):
            self.helper.persist(self.root, self.manifest_source, self.manifest_source)
        self.assertEqual(before, self.path.read_bytes())
        for field, value in (("layout", "target"), ("provider", "claude")):
            candidate = json.loads(json.dumps(self.manifest))
            candidate["request"][field] = value
            self.write(self.manifest_source, candidate)
            original = self.path.read_bytes()
            with self.assertRaises(self.routing.Blocked):
                self.persist()
            self.assertEqual(original, self.path.read_bytes())

    def test_replace_failure_preserves_manifest_and_cleans_temporary_file(self):
        from unittest.mock import patch
        before = self.path.read_bytes()
        with patch.object(self.helper.os, "replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                self.persist()
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual([], list(self.path.parent.glob(".receipts-*.tmp")))

    def test_manual_stale_lists_and_changed_sources_block_before_persistence(self):
        stale = {**self.manifest, "receipts": [self.receipt]}
        self.write(self.manifest_source, stale)
        before = self.path.read_bytes()
        with self.assertRaisesRegex(self.routing.Blocked, "canonical requirement"):
            self.persist()
        self.assertEqual(before, self.path.read_bytes())
        self.write(self.manifest_source, self.manifest)
        source = self.root / self.receipt["source"]
        source.write_bytes(source.read_bytes() + b"\nChanged guidance.\n")
        before = self.path.read_bytes()
        with self.assertRaises(self.routing.Blocked):
            self.persist()
        self.assertEqual(before, self.path.read_bytes())


class MigrationPreservationTests(unittest.TestCase):
    def test_untracked_agent_memory_may_be_absent_but_other_sources_may_not(self):
        from unittest.mock import patch
        inventory = json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text())
        memory = [e["source"] for e in inventory["files"] if validator.local_only(e)]
        other = next(e["source"] for e in inventory["files"] if e["ownership"] == "preserved-history" and not validator.local_only(e))
        self.assertTrue(memory)
        absent = {*memory, other}
        original = Path.exists
        def exists(path):
            return False if path.is_relative_to(ROOT) and path.relative_to(ROOT).as_posix() in absent else original(path)
        with patch.object(Path, "exists", exists):
            findings = validator.validate()
        self.assertEqual([f"missing inventory source/destination: {other}"], [f for f in findings if f.startswith("missing inventory")])

    def test_future_release_template_and_history_edits_are_not_frozen_by_ci(self):
        from unittest.mock import patch
        inventory = json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text())
        history = next(e["source"] for e in inventory["files"] if e["ownership"] == "preserved-history" and not validator.local_only(e))
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


class AgentSecuritySkillTests(unittest.TestCase):
    """ST-000287: shared agent-security skill, generated Common copies, orchestrator load."""
    blocks = load("generate_common_blocks")
    SKILL = ".mt-agent-devkit/skills/agent-security/SKILL.md"

    def skill(self):
        return (ROOT / self.SKILL).read_text(encoding="utf-8")

    def test_skill_has_frontmatter_three_parts_and_size_budget(self):
        text = self.skill()
        self.assertEqual(wrappers.skill_frontmatter(text)["name"], "agent-security")
        for heading in ("## A. Secret Handling", "## B. External Content Handling", "## C. Orchestrator Shell Authority"):
            self.assertIn(heading, text)
        self.assertEqual(["A", "B"], sorted(self.blocks.parts(text)))
        self.assertIn(".mt-agent-devkit/rules/Agent_Common_Shell_Safety.md", text)
        self.assertLessEqual(len(text.encode("utf-8")), 2500)

    def test_common_copies_match_parts_a_and_b_and_never_inline_part_c(self):
        parts = self.blocks.parts(self.skill())
        rows = [b for b in self.blocks.BLOCKS if b.skill == "agent-security"]
        self.assertEqual(8, len(rows))  # Core and Bootstrap, internal and Phase 2, parts A and B.
        self.assertEqual({"internal", "phase2"}, {b.layer for b in rows})
        self.assertEqual([], self.blocks.findings(ROOT))
        for row in rows:
            target = (ROOT / row.target).read_text(encoding="utf-8")
            with self.subTest(target=row.target, part=row.part):
                self.assertIn(self.blocks.begin(row) + parts[row.part] + self.blocks.end(row), target)
                self.assertIn("edit " + self.SKILL, self.blocks.begin(row))
            self.assertNotIn("Orchestrator Shell Authority", target)
            self.assertNotIn("part C", target)

    def test_skill_renderer_emits_frontmatter_and_single_pointer(self):
        entry = {"source": ".codex/skills/agent-security/SKILL.md", "destination": self.SKILL, "renderer": "skill"}
        text = wrappers.render(entry)
        self.assertEqual(wrappers.skill_frontmatter(text), wrappers.skill_frontmatter(self.skill()))
        self.assertEqual(1, text.count(self.SKILL))
        self.assertNotIn("Secret Handling", text)
        with self.assertRaises(ValueError):
            wrappers.render({**entry, "source": ".codex/skills/other/SKILL.md"})
        with self.assertRaises(ValueError):
            wrappers.skill_frontmatter("---\nname: x\n---\n")

    def test_every_provider_has_internal_and_bundle_wrapper(self):
        inventory = json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text())
        self.assertEqual([], validator.skill_errors(ROOT, inventory["files"], wrappers))
        manifest = json.loads((ROOT / ".mt-agent-devkit/distribution/phase2/bundle/deployment.json").read_text())
        files = {f["destination"]: f for f in manifest["files"]}
        self.assertEqual((files[self.SKILL]["owner"], files[self.SKILL]["ownership"]), ("shared", "managed"))
        for provider in ("claude", "antigravity", "codex"):
            wrapper = f".{provider}/skills/agent-security/SKILL.md"
            self.assertTrue((ROOT / wrapper).is_file())
            self.assertEqual(files[wrapper]["providers"], [provider])
        broken = [e for e in inventory["files"] if e["source"] != ".codex/skills/agent-security/SKILL.md"]
        self.assertIn("missing generated skill wrapper inventory entry: .codex/skills/agent-security/SKILL.md",
                      validator.skill_errors(ROOT, broken, wrappers))

    def test_orchestrator_loads_skill_before_first_issue_or_pr_read(self):
        self.assertEqual([], validator.orchestrator_security_errors(ROOT))
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        for relative in validator.ORCHESTRATOR_SOURCES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_text("Run `gh issue view 1` first.\n" + text, encoding="utf-8")
        errors = validator.orchestrator_security_errors(root)
        self.assertEqual(len(validator.ORCHESTRATOR_SOURCES), len(errors))
        self.assertTrue(all("before the first issue/PR read" in e for e in errors))


class CommonSkillsTests(unittest.TestCase):
    """ST-000307: common skills own the absorbed Common text; generate_common_blocks.py keeps the copies."""
    blocks = load("generate_common_blocks")
    RULES = ".mt-agent-devkit/rules/"

    def fixture(self):
        """Both skill layers and every mapped target, copied into a temporary root."""
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        files = {b.target for b in self.blocks.BLOCKS}
        for layer in (self.blocks.INTERNAL_SKILLS, self.blocks.PHASE2_SKILLS):
            files |= {p.relative_to(ROOT).as_posix() for p in (ROOT / layer).glob("*/SKILL*.md")}
        for relative in files:
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_bytes((ROOT / relative).read_bytes())
        return root

    def edit(self, root, relative, old, new):
        path = root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def test_seventeen_skills_frontmatter_budget_requires_and_wrappers(self):
        self.assertEqual(17, len(validator.COMMON_SKILLS))
        inventory = {e["source"]: e for e in json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text())["files"]}
        for name in validator.COMMON_SKILLS:
            with self.subTest(skill=name):
                text = (ROOT / f".mt-agent-devkit/skills/{name}/SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(name, wrappers.skill_frontmatter(text)["name"])
                self.assertLessEqual(len(text.encode("utf-8")), 4000)
                self.assertEqual(1, len(validator.REQUIRES.findall(text)))
                for provider in validator.PROVIDERS:
                    entry = inventory[f".{provider}/skills/{name}/SKILL.md"]
                    self.assertEqual(("skill", f".mt-agent-devkit/skills/{name}/SKILL.md"), (entry["renderer"], entry["destination"]))
        self.assertEqual([], validator.skill_reference_errors(ROOT))

    def test_every_design_7b_target_holds_its_generated_blocks(self):
        self.assertEqual([], self.blocks.findings(ROOT))
        internal = {(b.target.removeprefix(self.RULES), b.block) for b in self.blocks.BLOCKS if b.layer == "internal"}
        expected = {
            "Agent_Common_Bootstrap.md": {"pre-work part read-order", "working-record part format", "pre-work part resume", "agent-security part A",
                                          "token-efficiency part conventions", "agent-security part B", "shell-rules part rules",
                                          "retro part detection", "retro-contribution part orchestration"},
            "Agent_Common_Read_On_Demand.md": {"agent-memory part facts", "troubleshooting part format", "troubleshooting part protocol",
                                               "retro-contribution part writing", "handoff part state", "credential-gate part gate", "agent-memory part two-tier"},
            "Agent_Common_Core.md": {"agent-security part A", "agent-security part B", "token-efficiency part conventions",
                                     "retro part detection", "retro-contribution part orchestration"},
            "Agent_Common_Shell_Safety.md": {"shell-rules part safety"},
            "Agent_Common_Working_Record.md": {"working-record part format"},
            "Agent_Common_Memory.md": {"agent-memory part facts", "troubleshooting part format", "agent-memory part two-tier"},
            "Agent_Common_Retro.md": {"retro-contribution part writing"},
            "Agent_Common_Troubleshooting.md": {"troubleshooting part protocol"},
            "Agent_Common_Credential_Gate.md": {"credential-gate part gate"},
            "Agent_Common_Stage_Transition.md": {"handoff part state"},
        }
        self.assertEqual({(f, b) for f, names in expected.items() for b in names}, internal)
        for row in self.blocks.BLOCKS:
            if row.layer == "internal":
                self.assertTrue(self.blocks.source(row.skill, "internal").startswith(".mt-agent-devkit/skills/"))

    def test_generated_sections_hold_no_leftover_text_and_balanced_fences(self):
        """Text outside the blocks of a generated section is a second owner (fix round 1)."""
        allowed = {"Interruption, blocking, multi-session continuation or explicit status snapshot activates this capability."}
        for target in sorted({b.target for b in self.blocks.BLOCKS}):
            text = (ROOT / target).read_text(encoding="utf-8")
            self.assertEqual(0, len(re.findall(r"^```", text, re.M)) % 2, target)
            for section in re.split(r"(?m)^(?=## [0-9]+[a-z]?\.)", text)[1:]:
                if "BEGIN GENERATED" not in section:
                    continue
                rest = re.sub(r"(?s)<!-- BEGIN GENERATED (.+?):.*?<!-- END GENERATED \1 -->\n", "", section)
                leftover = [line for line in rest.splitlines()[1:] if line.strip() not in ("", "---")
                            and not any(line.startswith(a) for a in allowed)]
                self.assertEqual([], leftover, f"{target}: {section.splitlines()[0]}")

    def test_check_fails_on_differing_block_and_write_repairs_it(self):
        root = self.fixture()
        target = self.RULES + "Agent_Common_Read_On_Demand.md"
        self.edit(root, target, "Do not resume the blocked task", "Resume the blocked task")
        self.assertEqual([f"{target}: generated block differs from its part: troubleshooting part protocol"], self.blocks.findings(root))
        self.assertEqual([], self.blocks.findings(root, write=True))
        self.assertEqual((ROOT / target).read_bytes(), (root / target).read_bytes())

    def test_check_fails_on_missing_block(self):
        root = self.fixture()
        target = self.RULES + "Agent_Common_Stage_Transition.md"
        row = next(b for b in self.blocks.BLOCKS if b.target == target)
        text = (root / target).read_text(encoding="utf-8")
        start, end = text.index(self.blocks.begin(row)), text.index(self.blocks.end(row)) + len(self.blocks.end(row))
        (root / target).write_text(text[:start] + text[end:], encoding="utf-8")
        self.assertEqual([f"{target}: generated block missing: handoff part state"], self.blocks.findings(root))
        self.assertEqual([f"{target}: generated block missing: handoff part state"], self.blocks.findings(root, write=True))

    def test_check_fails_on_duplicated_block(self):
        root = self.fixture()
        target = self.RULES + "Agent_Common_Credential_Gate.md"
        row = next(b for b in self.blocks.BLOCKS if b.target == target)
        text = (root / target).read_text(encoding="utf-8")
        block = text[text.index(self.blocks.begin(row)):text.index(self.blocks.end(row)) + len(self.blocks.end(row))]
        (root / target).write_text(text + "\n" + block, encoding="utf-8")
        self.assertEqual([f"{target}: generated block duplicated: credential-gate part gate"], self.blocks.findings(root))

    def test_check_fails_on_part_with_no_target(self):
        root = self.fixture()
        skill = ".mt-agent-devkit/skills/clean-code/SKILL.md"
        self.edit(root, skill, "## 1. Meaningful Names\n", "## 1. Meaningful Names\n\n<!-- part: names -->\nUnmapped.\n<!-- /part: names -->\n")
        self.assertEqual([f"{skill}: part names has no target"], self.blocks.findings(root))

    def test_check_fails_on_unmapped_block_doubly_marked_part_and_template_copy_drift(self):
        root = self.fixture()
        target = self.RULES + "Agent_Common_Retro.md"
        stray = self.blocks.row("clean-code", "names", "internal", target)
        self.edit(root, target, "---\n", "---\n" + self.blocks.begin(stray) + "x\n" + self.blocks.end(stray))
        skill = ".mt-agent-devkit/skills/handoff/SKILL.md"
        self.edit(root, skill, "<!-- /part: state -->\n", "<!-- /part: state -->\n<!-- part: state -->\nx\n<!-- /part: state -->\n")
        template = self.blocks.source("agent-security", "phase2")
        (root / template).write_text((root / template).read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
        errors = self.blocks.findings(root)
        self.assertIn(f"{target}: generated block clean-code part names is not in the mapping table", errors)
        self.assertIn(f"{skill}: part marked more than once: state", errors)
        self.assertIn(f"{template}: differs from {self.blocks.source('agent-security', 'internal')}", errors)

    def test_old_generator_is_gone_and_callers_use_the_new_one(self):
        self.assertFalse((ROOT / ".mt-agent-devkit/scripts/generate_security_blocks.py").exists())
        for relative in ("scripts/validate_internal_harness.py", ".github/workflows/validate-templates.yml"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("generate_common_blocks.py", text)
            self.assertNotIn("generate_security_blocks", text)

    def test_undistributed_skills_are_exempt_only_from_distribution_checks(self):
        self.assertEqual(frozenset(validator.COMMON_SKILLS), validator.UNDISTRIBUTED_SKILLS)
        self.assertEqual([], validator.skill_template_errors(ROOT, wrappers))
        inventory = json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text())["files"]
        broken = [e for e in inventory if e["source"] != ".claude/skills/retro/SKILL.md"]
        self.assertIn("missing generated skill wrapper inventory entry: .claude/skills/retro/SKILL.md",
                      validator.skill_errors(ROOT, broken, wrappers))


class PoSkillsTests(unittest.TestCase):
    """ST-000288: ten po-* skills replace the internal PO rules files."""
    citations_spec = importlib.util.spec_from_file_location("retired_citations", ROOT / "scripts/validate_retired_citations.py")
    citations = importlib.util.module_from_spec(citations_spec)
    citations_spec.loader.exec_module(citations)
    RETIRED = (".mt-agent-devkit/rules/Product_Owner_Rules_Bootstrap.md",
               ".mt-agent-devkit/rules/Product_Owner_Rules_Read_On_Demand.md",
               ".mt-agent-devkit/rules/Story_Standard_PO.md")

    def inventory(self):
        return json.loads((ROOT / ".mt-agent-devkit/contracts/migration-inventory.json").read_text(encoding="utf-8"))

    def fixture(self, *relatives):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        for relative in relatives:
            for source in ([ROOT / relative] if (ROOT / relative).is_file() else (ROOT / relative).rglob("*")):
                if source.is_file():
                    target = root / source.relative_to(ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(source.read_bytes())
        return root

    def test_ten_canonical_skills_with_internal_wrappers_and_budgets(self):
        self.assertEqual(10, len(validator.PO_SKILLS))
        self.assertEqual([], validator.skill_errors(ROOT, self.inventory()["files"], wrappers))
        self.assertEqual([], validator.skill_reference_errors(ROOT))
        for name in validator.PO_SKILLS:
            canonical = ROOT / f".mt-agent-devkit/skills/{name}/SKILL.md"
            text = canonical.read_text(encoding="utf-8")
            self.assertEqual(wrappers.skill_frontmatter(text)["name"], name)
            self.assertLessEqual(len(text.encode("utf-8")), 1500 if name == "po-core" else 4000)
            for provider in validator.PROVIDERS:
                wrapper = (ROOT / f".{provider}/skills/{name}/SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(wrappers.skill_frontmatter(wrapper), wrappers.skill_frontmatter(text))
                self.assertIn(f".mt-agent-devkit/skills/{name}/SKILL.md", wrapper)
        self.assertIn("`agent-security`", (ROOT / ".mt-agent-devkit/skills/po-core/SKILL.md").read_text(encoding="utf-8"))
        story = (ROOT / ".mt-agent-devkit/skills/po-write-story/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("zero-padded to six digits", story)
        self.assertIn("Create the issue first", story)

    def test_requires_and_budget_failures_are_reported(self):
        root = self.fixture(".mt-agent-devkit/skills")
        skill = root / ".mt-agent-devkit/skills/po-comment/SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8").replace("**Requires:** `po-core`", "**Requires:** `po-missing`, `po-comment`"), encoding="utf-8")
        core = root / ".mt-agent-devkit/skills/po-core/SKILL.md"
        core.write_text(core.read_text(encoding="utf-8") + "x" * 400, encoding="utf-8")
        errors = validator.skill_reference_errors(root)
        self.assertIn("unresolved skill reference po-missing: .mt-agent-devkit/skills/po-comment/SKILL.md", errors)
        self.assertIn("skill requires itself: .mt-agent-devkit/skills/po-comment/SKILL.md", errors)
        self.assertIn("skill exceeds its 1500-byte budget: .mt-agent-devkit/skills/po-core/SKILL.md", errors)
        (root / ".mt-agent-devkit/skills/po-validate-ac/SKILL.md").unlink()
        self.assertIn("missing canonical PO skill: .mt-agent-devkit/skills/po-validate-ac/SKILL.md", validator.skill_reference_errors(root))

    def bundle(self):
        return json.loads((ROOT / ".mt-agent-devkit/distribution/phase2/bundle/deployment.json").read_text(encoding="utf-8"))

    def test_bundle_ships_po_skills_and_retires_old_po_templates(self):
        # ST-000289: shared canonical skill plus one wrapper per provider. ST-000290: old PO rules retire.
        manifest = self.bundle()
        live = {f["destination"]: f for f in manifest["files"] if f["phase"] != "retirement"}
        assets = {a["id"]: a for a in manifest["assets"]}
        for name in validator.PO_SKILLS:
            canonical = live[f".mt-agent-devkit/skills/{name}/SKILL.md"]
            self.assertEqual((canonical["owner"], canonical["ownership"], canonical["providers"]), ("shared", "managed", list(validator.PROVIDERS)))
            asset = assets[canonical["sources"][0]]
            template = ROOT / validator.SKILL_TEMPLATES / name / "SKILL_template.md"
            self.assertEqual(asset["sha256"], hashlib.sha256(template.read_bytes()).hexdigest())
            for provider in validator.PROVIDERS:
                wrapper = live[f".{provider}/skills/{name}/SKILL.md"]
                self.assertEqual((wrapper["owner"], wrapper["providers"], wrapper["phase"]), ("selected_provider", [provider], "discovery"))
        survivors = [f"skills/{name}" for name in validator.PO_SKILLS] + ["instructions/product_owner_instructions.md"]
        for survivor in survivors:  # Shared IDs carry no provider suffix, so they exist in every plan.
            self.assertEqual(live[".mt-agent-devkit/" + survivor + ("/SKILL.md" if survivor.startswith("skills/") else "")]["id"], survivor)
        records = {r["path"]: r for r in manifest["legacy_support"]["retirements"]}
        retiring = {f["destination"]: f for f in manifest["files"] if f["phase"] == "retirement"}
        for retired in self.RETIRED:
            name = Path(retired).name
            self.assertNotIn(retired, live)
            self.assertFalse((ROOT / ".mt-agent-devkit/distribution/phase2/templates/rules" / name.replace(".md", "_template.md")).exists())
            self.assertFalse(any(name.removesuffix(".md") in a["id"] for a in manifest["assets"]), name)
            shared = retiring[retired]
            self.assertEqual((shared["owner"], shared["ownership"], shared["providers"], shared["modes"], shared["required"]),
                             ("shared", "managed", list(validator.PROVIDERS), ["github", "strict"], False))
            self.assertEqual(records[retired]["after_verified_ids"], survivors)
            for provider in ("claude", "antigravity"):
                legacy = f".{provider}/agents/rules/{name}"
                self.assertEqual(sorted(f["modes"][0] for f in manifest["files"] if f["destination"] == legacy and f["phase"] == "retirement"), ["github", "strict"])
                self.assertEqual(records[legacy]["after_verified_ids"], survivors)
        for item in manifest["files"]:  # Every retirement entry sets `required` explicitly to False.
            if item["phase"] == "retirement":
                self.assertIs(item["required"], False, item["id"])
        self.assertEqual([], validator.skill_template_errors(ROOT, wrappers))

    def test_target_skill_templates_are_generic_and_mode_aware(self):
        for name in validator.PO_SKILLS:
            text = (ROOT / validator.SKILL_TEMPLATES / name / "SKILL_template.md").read_text(encoding="utf-8")
            self.assertNotIn("mycom08/mt-agent-devkit", text, name)
            self.assertNotIn("[DEVKIT]", text, name)
            self.assertNotIn("Project_Priming_Read_On_Demand", text, name)
            self.assertLessEqual(len(text.encode("utf-8")), 1500 if name == "po-core" else 4000)
        for name in ("po-comment", "po-plan-docs", "po-write-story", "po-roadmap-drain", "po-answer-questions", "po-promote-ready", "po-verify-close", "po-validate-ac"):
            self.assertIn("trict mode", (ROOT / validator.SKILL_TEMPLATES / name / "SKILL_template.md").read_text(encoding="utf-8"), name)
        instructions = (ROOT / ".mt-agent-devkit/distribution/phase2/templates/instructions/product_owner_instructions_template.md").read_text(encoding="utf-8")
        self.assertIn("Load `po-core`", instructions)
        self.assertIn("then the skill named in your assignment", instructions)
        for retired in ("Product_Owner_Rules_Bootstrap", "Product_Owner_Rules_Read_On_Demand", "Story_Standard_PO"):
            self.assertNotIn(retired, instructions)

    def test_bundle_and_template_skill_failures_are_reported(self):
        manifest = self.bundle()
        broken = json.loads(json.dumps(manifest))
        broken["files"] = [f for f in broken["files"] if f["destination"] not in (".codex/skills/po-core/SKILL.md", ".mt-agent-devkit/skills/po-comment/SKILL.md")]
        root = self.fixture(".mt-agent-devkit/skills", ".claude/skills", ".antigravity/skills", ".codex/skills",
                            ".mt-agent-devkit/distribution/phase2/bundle", validator.SKILL_TEMPLATES)
        (root / ".mt-agent-devkit/distribution/phase2/bundle/deployment.json").write_text(json.dumps(broken), encoding="utf-8")
        errors = validator.skill_errors(root, self.inventory()["files"], wrappers)
        self.assertIn("bundle lacks provider skill wrapper: .codex/skills/po-core/SKILL.md", errors)
        self.assertIn("bundle lacks shared managed canonical skill: .mt-agent-devkit/skills/po-comment/SKILL.md", errors)
        templates = root / validator.SKILL_TEMPLATES
        (templates / "po-validate-ac/SKILL_template.md").unlink()
        story = templates / "po-write-story/SKILL_template.md"
        story.write_text(story.read_text(encoding="utf-8").replace("name: po-write-story", "name: po-story") + "x" * 1000, encoding="utf-8")
        errors = validator.skill_template_errors(root, wrappers)
        self.assertIn(f"missing target skill template: {validator.SKILL_TEMPLATES}/po-validate-ac/SKILL_template.md", errors)
        self.assertIn(f"skill exceeds its 4000-byte budget: {validator.SKILL_TEMPLATES}/po-write-story/SKILL_template.md", errors)
        self.assertTrue(any(e.startswith(f"invalid target skill template: {validator.SKILL_TEMPLATES}/po-write-story") for e in errors), errors)
        self.assertTrue(any("unresolved skill reference po-validate-ac" in e for e in errors), errors)

    def test_fresh_install_per_provider_receives_po_skills(self):
        builder = validator.module("bundle_builder_289", ROOT / ".mt-agent-devkit/distribution/phase2/build_bundle.py")
        deployment = validator.module("bundle_deployment_289", ROOT / ".mt-agent-devkit/distribution/phase2/deployment.py")
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); bundle = base / "bundle"; builder.build(ROOT, bundle)
            manifest = bundle / "deployment.json"
            source = dict(kind="local", tag=None, commit="a" * 40, snapshot_version="0.1.53-SNAPSHOT", manifest_sha256=deployment.digest(manifest.read_bytes()))
            for provider in validator.PROVIDERS:
                with self.subTest(provider=provider):
                    target = base / provider; target.mkdir()
                    bound = {"PROVIDER_ROOT": "." + provider, "RUNTIME_ROOT": "." + provider + "/agents", "COMMAND_ROOT": "." + provider + "/agents"}
                    entrypoint = "CLAUDE.md" if provider == "claude" else "AGENTS.md"
                    adaptations = {entrypoint: "# Fixture\n", ".mt-agent-devkit/context/Project_Priming.md": "# Fixture\n", ".mt-agent-devkit/context/Document_Index.md": "# Docs\n", ".gitignore": "# Ignore\n"}
                    plan = deployment.plan(target, manifest, source, "github", "repo", {provider: bound}, adaptations)
                    deployment.apply(target, plan); deployment.verify(target)
                    for name in validator.PO_SKILLS:
                        canonical = f".mt-agent-devkit/skills/{name}/SKILL.md"
                        self.assertEqual((target / canonical).read_bytes(), (ROOT / validator.SKILL_TEMPLATES / name / "SKILL_template.md").read_bytes())
                        wrapper = (target / f".{provider}/skills/{name}/SKILL.md").read_text(encoding="utf-8")
                        self.assertEqual(wrappers.skill_frontmatter(wrapper)["name"], name)
                        self.assertIn(canonical, wrapper)
                        for other in set(validator.PROVIDERS) - {provider}:
                            self.assertFalse((target / f".{other}/skills/{name}/SKILL.md").exists())

    def test_retired_files_and_wrappers_are_deleted_and_ledgered(self):
        inventory = self.inventory()
        retired = {item["source"] for item in inventory["retired"]}
        self.assertEqual(6, len(retired))
        for source in retired | set(self.RETIRED):
            self.assertFalse((ROOT / source).exists(), source)
        self.assertFalse(retired & {e["source"] for e in inventory["files"]})
        for entry in inventory["files"]:
            self.assertFalse(set(entry["consumers"]) & set(self.RETIRED), entry["source"])
        instructions = (ROOT / ".mt-agent-devkit/instructions/product_owner_instructions.md").read_text(encoding="utf-8")
        self.assertIn("Load `po-core`", instructions)
        self.assertIn("then the skill named in your assignment", instructions)
        self.assertIn("## Selected Common Routing", instructions)

    def test_retired_citation_validator_scope(self):
        self.assertEqual([], self.citations.findings(ROOT))
        root = self.fixture(".mt-agent-devkit/rules/Agent_Common_Core.md", ".mt-agent-devkit/contracts/read-routing.json",
                            ".mt-agent-devkit/contracts/migration-inventory.json", ".claude/skills/po-core/SKILL.md", "CLAUDE.md")
        self.assertEqual([], self.citations.findings(root))  # The retirement ledger is out of scope.
        core = root / ".mt-agent-devkit/rules/Agent_Common_Core.md"
        core.write_text(core.read_text(encoding="utf-8") + "\nSee `Story_Standard_PO.md` §14 and PO Bootstrap §11a.\n"
                        "Legacy `Story_Standard_PO_template.md` stays frozen.\n", encoding="utf-8")
        wrapper = root / ".claude/skills/po-core/SKILL.md"
        wrapper.write_text(wrapper.read_text(encoding="utf-8") + "Product_Owner_Rules_Read_On_Demand §5\n", encoding="utf-8")
        registry = root / ".mt-agent-devkit/contracts/read-routing.json"
        data = json.loads(registry.read_text(encoding="utf-8"))
        data["tasks"]["closure"]["reads"][0]["source"] = ".mt-agent-devkit/rules/Product_Owner_Rules_Bootstrap.md"
        # ST-000289: target-layout alternatives are in scope too now both layouts route to the skills.
        data["tasks"]["closure"]["reads"][1]["layouts"] = {"target": {"source": ".mt-agent-devkit/rules/Story_Standard_PO.md"}}
        registry.write_text(json.dumps(data, indent=2), encoding="utf-8")
        found = self.citations.findings(root)
        self.assertEqual(5, len(found), found)
        self.assertTrue(any("Agent_Common_Core.md" in f and "Story_Standard_PO.md" in f for f in found))
        self.assertTrue(any("PO Bootstrap" in f for f in found))
        self.assertTrue(any(".claude/skills/po-core/SKILL.md" in f for f in found))
        self.assertTrue(any("read-routing.json" in f for f in found))
        self.assertFalse(any("_template" in f for f in found))

    def test_retired_citation_validator_covers_phase2_templates_and_bundle(self):
        # ST-000290: Phase 2 templates and every bundle asset are in scope; retirement ledgers are not.
        phase2 = ".mt-agent-devkit/distribution/phase2"
        root = self.fixture(phase2 + "/templates/rules/Story_Standard_template.md", phase2 + "/Sync_Devkit_Workflow_template.md",
                            phase2 + "/build_bundle.py", phase2 + "/bundle/deployment.json",
                            phase2 + "/bundle/assets/orchestrator_shared", phase2 + "/bundle/assets/build_bundle.py")
        self.assertEqual([], self.citations.findings(root))
        for relative in ("/templates/rules/Story_Standard_template.md", "/Sync_Devkit_Workflow_template.md", "/bundle/assets/orchestrator_shared"):
            path = root / (phase2 + relative)
            path.write_text(path.read_text(encoding="utf-8") + "\nSee `Story_Standard_PO.md` §14.\n", encoding="utf-8")
        found = self.citations.findings(root)
        self.assertEqual(3, len(found), found)
        self.assertTrue(any("bundle/assets/orchestrator_shared" in f for f in found))
        self.assertFalse(any("build_bundle.py" in f or "deployment.json" in f for f in found))

    def test_retired_inventory_source_must_be_gone(self):
        root = self.fixture(".mt-agent-devkit/contracts/migration-inventory.json")
        source = self.inventory()["retired"][0]["source"]
        (root / source).parent.mkdir(parents=True, exist_ok=True)
        (root / source).write_text("stale\n", encoding="utf-8")
        inventory = self.inventory()
        self.assertEqual([], validator.retired_errors(ROOT, inventory))
        inventory["files"].append({**inventory["files"][0], "source": inventory["retired"][1]["source"]})
        inventory["retired"][2].pop("reason")
        errors = validator.retired_errors(root, inventory)
        self.assertIn(f"retired inventory source still exists: {source}", errors)
        self.assertIn(f"retired inventory source is still a live entry: {inventory['retired'][1]['source']}", errors)
        self.assertIn(f"retired inventory entry lacks story/reason: {inventory['retired'][2]['source']}", errors)


class PoExecutionSettingTests(unittest.TestCase):
    """ST-000291: the po_execution setting and the contracts that let the orchestrator act as PO."""
    PHASE2 = ".mt-agent-devkit/distribution/phase2/templates/"
    ACTOR = "the orchestrator acting as PO under `po_execution: orchestrator`"

    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_init_creates_subagent_default_and_sync_never_overwrites(self):
        builder = validator.module("bundle_builder_291", ROOT / ".mt-agent-devkit/distribution/phase2/build_bundle.py")
        deployment = validator.module("bundle_deployment_291", ROOT / ".mt-agent-devkit/distribution/phase2/deployment.py")
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); bundle = base / "bundle"; builder.build(ROOT, bundle)
            manifest = bundle / "deployment.json"
            items = [f for f in json.loads(manifest.read_text(encoding="utf-8"))["files"] if f["destination"] == ".mt-agent-devkit/project_settings.json"]
            self.assertEqual([("project_owned", "create_if_absent", "content")], [(f["ownership"], f["renderer"], f["phase"]) for f in items])
            source = dict(kind="local", tag=None, commit="a" * 40, snapshot_version="0.1.55-SNAPSHOT", manifest_sha256=deployment.digest(manifest.read_bytes()))
            target = base / "target"; target.mkdir()
            bound = {"claude": {"PROVIDER_ROOT": ".claude", "RUNTIME_ROOT": ".claude/agents", "COMMAND_ROOT": ".claude/agents"}}
            adaptations = {"CLAUDE.md": "# Fixture\n", ".mt-agent-devkit/context/Project_Priming.md": "# Fixture\n", ".mt-agent-devkit/context/Document_Index.md": "# Docs\n", ".gitignore": "# Ignore\n"}
            deployment.apply(target, deployment.plan(target, manifest, source, "github", "repo", bound, adaptations))
            settings = target / ".mt-agent-devkit/project_settings.json"
            self.assertEqual(json.loads(settings.read_text(encoding="utf-8")), {"po_execution": "subagent"})
            settings.write_text('{"po_execution": "orchestrator"}\n', encoding="utf-8")
            deployment.apply(target, deployment.plan(target, manifest, source, "github", "repo", bound, adaptations))
            deployment.verify(target)
            self.assertEqual(settings.read_text(encoding="utf-8"), '{"po_execution": "orchestrator"}\n')
            # No entrypoint mirror: the managed CLAUDE.md block never states the setting.
            self.assertNotIn("po_execution", (target / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_orchestrator_pins_setting_and_documents_the_trade_off(self):
        for relative in (".mt-agent-devkit/instructions/orchestrator_instructions.md", self.PHASE2 + "shared/orchestrator_instructions_shared_template.md"):
            with self.subTest(relative=relative):
                text = self.read(relative)
                for required in ("project_settings.py po_execution", "**PO Execution:**", "A resumed run uses its pinned value",
                                 "resolves to `subagent` and the script reports it once", "**Accepted trade-off:**", "one actor both merges and records acceptance"):
                    self.assertIn(required, text)
        for relative in (".mt-agent-devkit/workflows/Sprint_Workflow.md", self.PHASE2 + "shared/workflows/Sprint_Workflow_Shared_template.md"):
            self.assertIn("**PO Execution:** <subagent | orchestrator>", self.read(relative))

    def test_story_standard_and_record_access_contracts_are_amended(self):
        for relative in (".mt-agent-devkit/rules/Story_Standard.md", self.PHASE2 + "rules/Story_Standard_template.md"):
            with self.subTest(relative=relative):
                text = self.read(relative)
                done = next(line for line in text.splitlines() if line.startswith("| **Done** |"))
                role = next(line for line in text.splitlines() if line.startswith("| **PO** |"))
                section = text[text.index("## 14."):text.index("## 15.")]
                self.assertIn(self.ACTOR, done)
                self.assertIn(self.ACTOR, role)
                self.assertEqual(3, section.count(self.ACTOR))
                self.assertIn("In `orchestrator` mode, the scope decision is the user's.", section)
        for relative in (".mt-agent-devkit/rules/Agent_Common_Bootstrap.md", ".mt-agent-devkit/rules/Agent_Common_Working_Record.md",
                         self.PHASE2 + "rules/Agent_Common_Bootstrap_template.md", self.PHASE2 + "rules/Agent_Common_Working_Record_template.md"):
            self.assertIn(self.ACTOR + " owns the PO record and memory for that activity", self.read(relative), relative)


class OrchestratorPoModeTests(unittest.TestCase):
    """ST-000292: every design section 5 row in the devkit workflows and their Phase 2 templates."""
    PHASE2 = ".mt-agent-devkit/distribution/phase2/templates/"
    ORCH = (".mt-agent-devkit/instructions/orchestrator_instructions.md", PHASE2 + "shared/orchestrator_instructions_shared_template.md")
    ROWS = {
        "Create Stories": ("Inline (already)", "Inline", "`po-core`, `po-write-story`"),
        "Plan Sprint Stages 1, 2, 4": ("Spawn/resume `po_session`", "**Spawn/resume (forced)**", "`po-plan-sprint`"),
        "Refine Sprint Stage 2 (after TL)": ("Spawn/resume", "Inline; TL still answers first", "`po-answer-questions`"),
        "Refine Sprint Stage 4": ("Resume", "Inline", "`po-promote-ready`"),
        "Pipeline Stage 2: Developer question with owner PO": ("Spawn/resume", "Inline", "`po-answer-questions`"),
        "Scope change after Stage 1 starts": ("PO decides", "**Escalate to the user**", "none"),
        "Pipeline Stage 3, QA is the implementer": ("Spawn", "**Spawn (forced)**", "`po-validate-ac`"),
        "Pipeline Stage 4 non-behavioral": ("Inline (already)", "Inline (unchanged)", "none"),
        "Pipeline Stage 4 behavioral": ("Spawn (`closure` policy)", "Inline", "`po-verify-close`"),
        "Sprint Workflow next-story promotion": ("PO", "Inline", "`po-promote-ready`"),
    }

    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def pair(self, devkit, template):
        return ((".mt-agent-devkit/workflows/" + devkit, self.read(".mt-agent-devkit/workflows/" + devkit)),
                (self.PHASE2 + template, self.read(self.PHASE2 + template)))

    def test_orchestrator_instructions_carry_the_full_behavior_matrix(self):
        for relative in self.ORCH:
            text = self.read(relative)
            table = [line for line in text[text.index("## PO Touchpoints by `PO Execution`"):].splitlines() if line.startswith("| ")]
            for touchpoint, (subagent, orchestrator, skill) in self.ROWS.items():
                with self.subTest(relative=relative, touchpoint=touchpoint):
                    row = next(line for line in table if line.startswith("| " + touchpoint))
                    cells = [cell.strip() for cell in row.strip("|").split("|")]
                    self.assertEqual((cells[1], cells[2]), (subagent, orchestrator))
                    self.assertIn(skill, cells[3])

    def test_inline_procedure_state_telemetry_and_retro_follow_section_7(self):
        for relative in self.ORCH:
            text = self.read(relative)
            for required in (".mt-agent-devkit/skills/<name>/SKILL.md", "verified native skill discovery", "`po_session: inline`", "`**PO Skills:**`",
                             "Product_Owner_Memory.md` in full and record `**PO Memory:** read`", "`## Stored Facts`", "Product_Owner_Working_Record.md",
                             "Stage 4 closure skips it", "role is `Orchestrator`", "`role: PO`, `session_mode: orchestrator_inline`",
                             "`usage_source: unavailable`", "Never extract, capture boundaries or estimate inline usage",
                             "`po_session: inline` with a matching `PO Skills` entry satisfies it"):
                with self.subTest(relative=relative, required=required):
                    self.assertIn(required, text)

    def test_inline_skills_load_at_point_of_use_with_explicit_checks(self):
        """ST-000303: point-of-use loading, numbered per-action checks and one Working Record timing, in both layers."""
        for relative in self.ORCH:
            text = self.read(relative)
            for required in ("not a bulk-load list", "**Skills, at the point of use.** Load each skill immediately before the action it governs",
                             "`po-comment` (with `comment`) before each post", "`po-write-story` only when an AC",
                             "`po-promote-ready` before each promotion", "at the start and end of each inline activity"):
                self.assertIn(required, text, relative)
            self.assertNotIn("Before acting, load each listed skill", text, relative)
        for name, required in (("po-promote-ready", ("1. **Open points.**", "2. **AC against the decided approach.**", "TL refinement answers",
                                                     "design-first approval", "3. **Dependencies.**", "`**Depends on:**`", "4. **Promote.**")),
                               ("po-comment", ("## Before Each Post", "2. Run the word count before posting", "start and end (`po-core`)")),
                               ("po-write-story", ("**AC states the testable requirement only, no rationale.**",)),
                               ("po-core", ("start and end of each PO activity (a spawned PO session or one inline activity)", "Stage 4 closure skips"))):
            for relative in (f".mt-agent-devkit/skills/{name}/SKILL.md", f"{self.PHASE2}skills/{name}/SKILL_template.md"):
                text = self.read(relative)
                for phrase in required:
                    with self.subTest(relative=relative, phrase=phrase):
                        self.assertIn(phrase, text)

    def test_forced_spawns_hold_in_both_modes(self):
        for relative, text in self.pair("Plan_Sprint_Workflow.md", "shared/workflows/Plan_Sprint_Workflow_Shared_template.md"):
            self.assertIn("**forced spawn:** Plan Sprint always spawns a PO in both `PO Execution` modes and never runs inline", text, relative)
            self.assertIn("**Forced PO spawn**", text, relative)
        for relative, text in self.pair("Shared_Pipeline_Stages.md", "shared/workflows/Shared_Pipeline_Stages_Shared_template.md"):
            self.assertIn("always **spawn** Product Owner (**forced spawn** in both `PO Execution` modes, never inline", text, relative)
            self.assertIn("manifest task `po_validation`", text, relative)

    def test_scope_change_after_stage_1_escalates_to_the_user(self):
        for relative in self.ORCH:
            text = self.read(relative)
            self.assertIn("a defer, a split or **any** AC body edit is never decided inline", text)
            self.assertIn("Blocked Story Procedure in `Shared_Pipeline_Stages.md` addressed to the user", text)
        for relative, text in self.pair("Shared_Pipeline_Stages.md", "shared/workflows/Shared_Pipeline_Stages_Shared_template.md"):
            section = text[text.index("### Scope-Change Escalation (`PO Execution: orchestrator`)"):text.index("### Blocked Story Procedure")]
            for required in ("**any** AC body edit is never decided inline", "Every AC body edit counts, whatever its direction",
                             "with the **user** as the owner to tag", "`subagent` mode is unchanged: the PO decides"):
                self.assertIn(required, section, relative)
            self.assertIn("run the Scope-Change Escalation below instead", text, relative)
            self.assertIn("approved (by the user under `PO Execution: orchestrator`, through the Scope-Change Escalation)", text, relative)
        for relative, text in self.pair("Resume_Story_Workflow.md", "shared/workflows/Resume_Story_Workflow_Shared_template.md"):
            self.assertIn("the user's recorded decision is the scope decision", text, relative)
            self.assertIn("resume the recorded stage from the pipeline state file instead of restarting at Stage 0", text, relative)
        for skill in ("po-answer-questions", "po-verify-close"):
            for relative in (f".mt-agent-devkit/skills/{skill}/SKILL.md", f"{self.PHASE2}skills/{skill}/SKILL_template.md"):
                self.assertIn("`po_execution: orchestrator`", self.read(relative), relative)

    def test_each_workflow_touchpoint_routes_on_the_pinned_value(self):
        for relative, text in self.pair("Create_Stories_Workflow.md", "shared/workflows/Create_Stories_Workflow_Shared_template.md"):
            self.assertIn("**Do not spawn a PO agent.**", text, relative)
            self.assertIn("this is the Create Stories row of the PO touchpoint table", text, relative)
        for relative, text in self.pair("Refine_Sprint_Workflow.md", "shared/workflows/Refine_Sprint_Workflow_Shared_template.md"):
            stage2 = text[text.index("## Stage 2"):text.index("## Stage 3")]
            stage4 = text[text.index("## Stage 4"):text.index("## Pipeline Rules")]
            self.assertIn("**`PO Execution: subagent`:** spawn or resume PO", stage2, relative)
            self.assertIn("**`PO Execution: orchestrator`:** after TL completes, the orchestrator answers inline as PO", stage2, relative)
            self.assertIn("`po-core`, `po-answer-questions` and `po-comment`", stage2, relative)
            self.assertIn("**`PO Execution: subagent`:** resume the PO agent via `po_session`", stage4, relative)
            self.assertIn("load `po-core` and `po-promote-ready`", stage4, relative)
            for field in ("**PO Execution:**", "**PO Skills:**", "**PO Memory:**", "inline (`orchestrator` mode)"):
                self.assertIn(field, text, relative)
        for relative, text in self.pair("Shared_Pipeline_Stages.md", "shared/workflows/Shared_Pipeline_Stages_Shared_template.md"):
            consultation = text[text.index("### Mid-Implementation Consultation Procedure"):text.index("### Scope-Change Escalation")]
            self.assertIn("(manifest task `scope_question`). **`PO Execution: orchestrator`:** do not spawn; the orchestrator answers inline as PO", consultation, relative)
            self.assertIn("spawn TL only, then answer the PO part inline", consultation, relative)
            stage4 = text[text.index("## Stage 4 — PO Story Closure"):text.index("## Stage 5")]
            fast = stage4[stage4.index("### Non-behavioral fast path"):stage4.index("### Behavioral path")]
            self.assertIn("Orchestrator executes closure directly — no PO agent spawn", fast, relative)
            self.assertNotIn("PO Execution", fast, relative)  # unchanged in both modes
            behavioral = stage4[stage4.index("### Behavioral path"):stage4.index("### Orchestrator Observation Check")]
            self.assertIn("**`PO Execution: orchestrator`:** do not spawn. The orchestrator closes the story inline as PO", behavioral, relative)
            self.assertIn("load `po-core`, `po-verify-close` and `po-comment`", behavioral, relative)
            self.assertIn("Skip the PO Working Record, record the completion identity with role `Orchestrator`", behavioral, relative)
            self.assertIn("**`PO Execution: subagent`:** steps 1–5 below, unchanged.", behavioral, relative)
            self.assertIn("manifest task `closure`", behavioral, relative)
            self.assertIn("`po_session: inline` with a `stage4-closure` entry in `PO Skills` satisfies this", stage4, relative)
            self.assertIn("`Orchestrator` story-total telemetry row written after Stage 4", stage4, relative)
        for relative, text in self.pair("Sprint_Workflow.md", "shared/workflows/Sprint_Workflow_Shared_template.md"):
            self.assertIn("Under `PO Execution: orchestrator` the orchestrator performs this promotion inline as PO", text, relative)
            self.assertIn("**PO Skills:**", text, relative)
            self.assertIn("A forced PO spawn (Stage 3 with QA as the implementer) still records its real session handle", text, relative)

    def test_r1_comparison_rule_is_documented_with_the_collector(self):
        for relative in self.ORCH:
            text = self.read(relative)
            self.assertIn("telemetry.py compare --subagent", text)
            self.assertIn("is reported as **unmeasured**, never estimated", text)
            self.assertIn("(`usage_source: harness_report`)", text)


if __name__ == "__main__":
    unittest.main()
