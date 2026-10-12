"""Executable completion-state scenarios, independent of retrospective prose."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / '.mt-agent-devkit/scripts/retro_completion.py'
spec = importlib.util.spec_from_file_location('retro_completion', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name)
        self.root = r.runtime_root(self.target, 'codex', '.codex/agents')
        self.identity = dict(provider='codex', run='run1', story='ST-000253', stage='1', role='Developer')

    def contribution(self, value=None, heading='Implementer — Developer', body='- [workflow] Preserve validated scope.\n'):
        value = value or self.identity
        retro = self.root / 'retros' / (value['story'] + '_retro.md')
        retro.parent.mkdir(parents=True, exist_ok=True)
        retro.write_text('# Story\n\n## ' + heading + '\n' + body, encoding='utf-8')
        evidence = self.root / 'tmp/evidence.md'
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text('Bounded evidence pointer\n', encoding='utf-8')
        return ['retros/' + value['story'] + '_retro.md#' + heading], ['tmp/evidence.md']

    def test_clean_stage_creates_metadata_but_no_retro(self):
        r.write_record(self.root, self.identity, 'clean')
        result = r.check(self.root, 'codex', [self.identity])
        self.assertEqual(result, dict(status='complete', clean=1, required=0, retros=[]))
        self.assertFalse((self.root / 'retros').exists())

    def test_every_independent_trigger_requires_actual_contribution(self):
        for trigger in r.TRIGGERS:
            with self.subTest(trigger=trigger):
                value = {**self.identity, 'stage': trigger}
                r.write_record(self.root, value, 'required', [trigger])
                with self.assertRaisesRegex(ValueError, 'not submitted'):
                    r.check(self.root, 'codex', [value])
                contributions, evidence = self.contribution(value)
                r.write_record(self.root, value, 'required', [trigger], contributions, evidence)
                self.assertEqual(r.check(self.root, 'codex', [value])['required'], 1)

    def test_late_trigger_after_clean_and_clean_resume_cannot_erase_it(self):
        r.write_record(self.root, self.identity, 'clean')
        pointers, evidence = self.contribution()
        before = (self.root / 'retros/ST-000253_retro.md').read_bytes()
        r.write_record(self.root, self.identity, 'required', ['reusable_lesson'], pointers, evidence)
        r.write_record(self.root, self.identity, 'clean')
        r.write_record(self.root, self.identity, 'unknown')
        record = json.loads(r.record_path(self.root, self.identity).read_text())
        self.assertEqual(record['state'], 'required')
        self.assertEqual(record['contributions'], pointers)
        self.assertEqual((self.root / 'retros/ST-000253_retro.md').read_bytes(), before)
        self.assertEqual(r.check(self.root, 'codex', [self.identity])['required'], 1)

    def test_repeat_submission_deduplicates_pointers_and_preserves_history(self):
        pointers, evidence = self.contribution()
        for _ in range(3):
            r.write_record(self.root, self.identity, 'required', ['repeated_fix'], pointers, evidence)
        record = json.loads(r.record_path(self.root, self.identity).read_text())
        self.assertEqual(record['contributions'], pointers)
        self.assertEqual(record['triggers'], ['repeated_fix'])

    def test_unknown_and_missing_evaluation_are_not_clean(self):
        with self.assertRaisesRegex(ValueError, 'missing trigger'):
            r.check(self.root, 'codex', [self.identity])
        r.write_record(self.root, self.identity, 'unknown')
        with self.assertRaisesRegex(ValueError, 'unknown'):
            r.check(self.root, 'codex', [self.identity])

    def test_zero_and_mixed_sprint_aggregation(self):
        clean = {**self.identity, 'story': 'ST-000001'}
        r.write_record(self.root, clean, 'clean')
        self.assertEqual(r.check(self.root, 'codex', [clean])['retros'], [])
        pointers, evidence = self.contribution()
        r.write_record(self.root, self.identity, 'required', ['external_blocker'], pointers, evidence)
        result = r.check(self.root, 'codex', [clean, self.identity])
        self.assertEqual((result['clean'], result['required']), (1, 1))
        self.assertEqual(result['retros'], ['retros/ST-000253_retro.md'])

    def test_existing_file_other_role_empty_or_pending_is_insufficient(self):
        for heading, body in [('QA', '- Lesson\n'), ('Implementer — Developer', '- None.\n'), ('Implementer — Developer', '*(pending)*\n')]:
            with self.subTest(heading=heading, body=body):
                self.contribution(heading=heading, body=body)
                r.write_record(self.root, self.identity, 'required', ['decision_ambiguity'], ['retros/ST-000253_retro.md#Implementer — Developer'], ['tmp/evidence.md'])
                with self.assertRaisesRegex(ValueError, 'unpopulated'):
                    r.check(self.root, 'codex', [self.identity])

    def test_foreign_role_story_provider_and_escaping_pointers_rejected(self):
        for pointer in ['../foreign.md#QA', '/tmp/secret#QA', 'retros/ST-000215_retro.md#Implementer — Developer', 'retros/ST-000253_retro.md#QA']:
            with self.subTest(pointer=pointer), self.assertRaises(ValueError):
                r.write_record(self.root, self.identity, 'required', ['tooling_failure'], [pointer])
        with self.assertRaises(ValueError):
            r.runtime_root(self.target, 'codex', '.claude/agents')
        with self.assertRaises(ValueError):
            r.check(self.root, 'claude', [self.identity])

    def test_missing_evidence_and_symlink_escape_block(self):
        pointers, _ = self.contribution()
        r.write_record(self.root, self.identity, 'required', ['explicit_request'], pointers, ['tmp/missing.md'])
        with self.assertRaisesRegex(ValueError, 'evidence pointer missing'):
            r.check(self.root, 'codex', [self.identity])
        with self.assertRaises(ValueError):
            r.write_record(self.root, self.identity, 'required', ['tooling_failure'], evidence=['../../outside'])

    def test_expected_empty_duplicate_and_unspawned_identity_block(self):
        r.write_record(self.root, self.identity, 'clean')
        for expected in [[], [self.identity, self.identity], [self.identity, {**self.identity, 'role': 'QA'}]]:
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                r.check(self.root, 'codex', expected)

    def test_atomic_metadata_write_and_real_cli_outcomes(self):
        base = [sys.executable, str(SCRIPT), 'record', '--target', str(self.target), '--provider', 'codex', '--runtime-root', '.codex/agents', '--run', 'run1', '--story', 'ST-000253', '--stage', '1', '--role', 'Developer']
        result = subprocess.run(base + ['--state', 'clean'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['state'], 'clean')
        path = r.record_path(self.root, self.identity)
        self.assertEqual(list(path.parent.glob('.completion-*')), [])
        result = subprocess.run(base + ['--state', 'required'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(path.read_text())['state'], 'clean')

    def test_neutral_bootstrap_rewrite_preserves_following_detection_policy(self):
        from scripts.test.test_phase2_bundle import builder
        source = '## 6. Shell Command Rules\nOld shell rules\n## 7. Retrospective Trigger\nDetection before guidance\n## Version\nHistory\n'
        rendered = builder.neutral(source)
        self.assertIn('Detection before guidance', rendered)
        self.assertLess(rendered.index('selected provider adapter'), rendered.index('## 7.'))

    def test_installed_six_layouts_preserve_policy_and_execute_clean_helper(self):
        from scripts.test.test_phase2_bundle import builder, d
        bundle = self.target / 'bundle'
        builder.build(ROOT, bundle)
        manifest = bundle / 'deployment.json'
        source = dict(kind='local', tag=None, commit='a' * 40, snapshot_version='0.1.53-SNAPSHOT', manifest_sha256=d.digest(manifest.read_bytes()))
        canonical = (ROOT / '.mt-agent-devkit/rules/Agent_Common_Bootstrap.md').read_text(encoding='utf-8').split('## 7.', 1)[1].strip()
        for provider in d.PROVIDERS:
            for mode in ['github', 'strict']:
                with self.subTest(provider=provider, mode=mode):
                    target = self.target / (provider + '-' + mode)
                    target.mkdir()
                    runtime = '.' + provider + '/agents'
                    bindings = {provider: dict(PROVIDER_ROOT='.' + provider, RUNTIME_ROOT=runtime, COMMAND_ROOT=runtime)}
                    entry = 'CLAUDE.md' if provider == 'claude' else 'AGENTS.md'
                    adapted = {entry: '# Fixture\n', '.mt-agent-devkit/context/Project_Priming.md': '# Fixture\n', '.mt-agent-devkit/context/Document_Index.md': '# Docs\n', '.gitignore': '.mt-agent-devkit-migration.lock\n'}
                    d.apply(target, d.plan(target, manifest, source, mode, 'repo', bindings, adapted))
                    d.verify(target)
                    bootstrap = (target / '.mt-agent-devkit/rules/Agent_Common_Bootstrap.md').read_text(encoding='utf-8')
                    policy = bootstrap.split('## 7.', 1)[1].split('## Version', 1)[0].strip().removesuffix('---').strip()
                    self.assertEqual(policy, canonical)
                    expected = dict(provider=provider, run='fixture', story='ST-000253', stage='1', role='Developer')
                    helper = target / '.mt-agent-devkit/scripts/retro_completion.py'
                    result = subprocess.run([sys.executable, str(helper), 'record', '--target', str(target), '--provider', provider, '--runtime-root', runtime, '--run', 'fixture', '--story', 'ST-000253', '--stage', '1', '--role', 'Developer', '--state', 'clean'], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout)['state'], 'clean')
                    self.assertFalse((target / runtime / 'retros').exists())
                    pipeline = (target / '.mt-agent-devkit/workflows/Shared_Pipeline_Stages.md').read_text(encoding='utf-8')
                    self.assertNotIn('pre-spawn: create the retro file skeleton', pipeline)
                    self.assertIn('Missing/unknown evaluations or required role contributions block', pipeline)
                    for consumer in ['Start_Story_Workflow.md', 'Sprint_Workflow.md']:
                        content = (target / '.mt-agent-devkit/workflows' / consumer).read_text(encoding='utf-8')
                        self.assertIn('completion helper', content)
                        self.assertNotIn('Delete `{RUNTIME_ROOT}/retros/ST-XXXXXX_retro.md`', content)


if __name__ == '__main__':
    unittest.main()
