"""Positive/negative Common routing and safety-order regression contracts."""
import copy
import shutil
import json
import re
import subprocess
import sys
import hashlib
from unittest.mock import patch
from pathlib import Path
import unittest
from scripts.test import test_read_manifest as existing

ROOT, m, REGISTRY = existing.ROOT, existing.m, existing.REGISTRY


class CommonCapabilitiesTests(unittest.TestCase):
    write = existing.RoutingTests.write
    delta = existing.RoutingTests.delta

    def setUp(self):
        existing.RoutingTests.setUp(self)
        shutil.copytree(ROOT / '.mt-agent-devkit/rules', self.root / '.mt-agent-devkit/rules', dirs_exist_ok=True)
        self.registry = copy.deepcopy(REGISTRY)
        self.registry['common_capabilities']['verified_providers'] = ['codex']
        for role in ('Developer', 'Technical_Lead', 'QA'):
            self.write(self.bound['RUNTIME_ROOT'] + '/memory/' + role + '_Memory.md', '# Memory\n\n## Standing Checks\nAlways preserve independent gates.\n\n## Keyword Index\nNone yet.\n\n## Troubleshooting Facts\nKnown fix.\n')

    def candidate(self, **changes):
        request = copy.deepcopy(self.request)
        request.update(changes)
        return m.build(self.root, request, registry=self.registry)

    def test_clean_required_and_forbidden_capabilities(self):
        result = self.candidate()
        ids = {x['id'] for x in result['reads']}
        self.assertIn('standing_checks', ids)
        self.assertNotIn('record', ids)
        selected = {x['source'] for x in result['reads']}
        self.assertIn('.mt-agent-devkit/rules/Agent_Common_Core.md', selected)
        self.assertIn('.mt-agent-devkit/rules/Developer_Rules_Bootstrap.md', selected)
        self.assertFalse(any(x.endswith(('Agent_Common_Bootstrap.md', 'Agent_Common_Retro.md', 'Agent_Common_Memory.md')) for x in selected))
        memory = next(x for x in result['reads'] if x['id'] == 'memory')
        self.assertEqual(memory['coverage'], {'kind': 'memory_section', 'heading': 'Keyword Index'})
        self.assertNotIn(b'Known fix', m.covered(self.root, memory['source'], memory['coverage']))

    def test_shell_and_record_precede_governed_reads(self):
        result = self.candidate(triggers=['shell_safety', 'working_record'])
        ids = [x['id'] for x in result['reads']]
        self.assertLess(ids.index('common'), ids.index('trigger_shell_safety'))
        self.assertLess(ids.index('trigger_working_record'), ids.index('record'))
        seen = set()
        for x in result['reads']:
            self.assertLessEqual(set(x['after']), seen)
            seen.add(x['id'])

    def test_failure_credential_retro_and_handoff_exact_owners(self):
        result = self.candidate(triggers=['tooling_failure', 'credential_gate', 'retro_required', 'runtime_handoff'])
        ids = [x['id'] for x in result['reads']]
        self.assertLess(ids.index('troubleshooting_facts'), ids.index('trigger_tooling_failure'))
        for module in ('Troubleshooting', 'Credential_Gate', 'Retro', 'Stage_Transition'):
            self.assertIn('.mt-agent-devkit/rules/Agent_Common_' + module + '.md', {x['source'] for x in result['reads']})
        self.assertIn('trigger_retro_rules', ids)
        self.assertNotIn('record', ids)

    def test_unknown_and_expired_restore_safe_selected_entry(self):
        for state in ('same', 'expired'):
            result = self.candidate(session_state=state, delta=self.delta())
            self.assertFalse(result['omitted'])
            self.assertTrue({'adapter', 'role', 'common', 'standing_checks', 'memory'} <= {x['id'] for x in result['reads']})

    def test_candidate_same_session_omits_only_actual_unchanged_receipts(self):
        fresh = self.candidate(task='fix')
        registry_path = self.root / '.mt-agent-devkit/contracts/read-routing.json'
        registry_path.write_text(json.dumps(self.registry), encoding='utf-8')
        with patch.object(m, 'REGISTRY', registry_path):
            receipts = [m.attest(self.root, fresh, x['id'], returned_complete=True, truncation_recovered=True) for x in fresh['reads'] if not x['id'].startswith('context_')]
        request = copy.deepcopy(fresh['request'])
        request.update(session_state='same', delta=self.delta())
        resumed = m.build(self.root, request, receipts, self.registry)
        self.assertTrue(resumed['omitted'])
        self.assertTrue(all(x['id'].startswith('context_') for x in resumed['reads']))
        self.write('.mt-agent-devkit/rules/Agent_Common_Core.md', '# Changed safety obligation\n')
        changed = m.build(self.root, request, receipts, self.registry)
        self.assertIn('common', {x['id'] for x in changed['reads']})
        self.assertNotIn('common', {x['id'] for x in changed['omitted']})

    def test_expired_continuation_requires_record_before_role_rules(self):
        reads = self.candidate(session_state='expired')['reads']
        ids = [x['id'] for x in reads]
        self.assertLess(ids.index('trigger_working_record'), ids.index('record'))
        self.assertLess(ids.index('record'), ids.index('bootstrap'))

    def test_unverified_provider_keeps_full_safe_bootstrap(self):
        result = m.build(self.root, self.request, registry={**self.registry, 'common_capabilities': {**self.registry['common_capabilities'], 'verified_providers': []}})
        selected = {x['source'] for x in result['reads']}
        self.assertIn('.mt-agent-devkit/rules/Agent_Common_Bootstrap.md', selected)
        self.assertIn('record', {x['id'] for x in result['reads']})
        self.assertEqual(next(x for x in result['reads'] if x['id'] == 'memory')['coverage'], {'kind': 'full'})

    def test_bounded_heading_rejects_ambiguous_missing_and_unknown(self):
        source = self.bound['RUNTIME_ROOT'] + '/memory/Developer_Memory.md'
        with self.assertRaisesRegex(m.Blocked, 'invalid bounded memory'):
            m.covered(self.root, source, {'kind': 'memory_section', 'heading': 'Stored Facts'})
        self.write(source, '## Standing Checks\nA\n## Standing Checks\nB\n')
        with self.assertRaisesRegex(m.Blocked, 'exactly one'):
            self.candidate()

    def test_core_retains_exception_completion_and_safety(self):
        core = (ROOT / '.mt-agent-devkit/rules/Agent_Common_Core.md').read_text(encoding='utf-8')
        for clause in ('required', 'unknown', 'sticky', 'late', 'retro_completion.py', 'secret', 'authorAssociation', 'truncation', 'independent TL/QA', 'NOT VERIFIED'):
            self.assertIn(clause, core)
        self.assertIn('Never `git add`, commit, or push', (ROOT / '.mt-agent-devkit/rules/Agent_Common_Stage_Transition.md').read_text(encoding='utf-8'))

    def test_legacy_memory_preserves_full_safe_authority_without_conversion(self):
        source = self.bound['RUNTIME_ROOT'] + '/memory/Developer_Memory.md'
        self.write(source, 'durable user fact\n')
        result = self.candidate()
        selected = {x['id']: x for x in result['reads']}
        self.assertEqual(selected['common']['source'], '.mt-agent-devkit/rules/Agent_Common_Bootstrap.md')
        self.assertEqual(selected['memory']['coverage'], {'kind': 'full'})
        self.assertIn('record', selected)
        self.assertNotIn('standing_checks', selected)
        self.assertEqual((self.root / source).read_text(encoding='utf-8'), 'durable user fact\n')
        self.assertFalse(result['receipts'])

    def test_partial_memory_format_blocks_even_without_failure_trigger(self):
        source = self.bound['RUNTIME_ROOT'] + '/memory/Developer_Memory.md'
        self.write(source, '## Standing Checks\nA\n## Keyword Index\nB\n')
        with self.assertRaisesRegex(m.Blocked, 'exactly one'):
            self.candidate()

    def test_ownership_inventory_has_every_rule_and_no_duplicate_identity(self):
        rows = json.loads((ROOT / 'docs/reviews/ST-000264_Common_Ownership.json').read_text(encoding='utf-8'))['rows']
        keys = [(x['source'], x['section']) for x in rows]
        self.assertEqual(len(keys), len(set(keys)))
        for source in {x['source'] for x in rows}:
            headings = re.findall(r'^## ([0-9]+[a-z]?)\.', (ROOT / source).read_text(encoding='utf-8'), re.M)
            self.assertEqual(set(headings), {x['section'] for x in rows if x['source'] == source})
        for row in rows:
            for key in ('current_owner', 'future_owner', 'trigger_stage', 'migrated_consumers', 'compatibility', 'retirement_condition'):
                self.assertTrue(row[key])

    def test_frozen_adapter_amendment_records_real_json_lines(self):
        fixture = ROOT / 'scripts/test/fixtures/common_264'
        amendment = json.loads((fixture / 'adapter_amendment.json').read_text(encoding='utf-8'))
        for name, key in [('gh.py', 'original_sha256'), ('gh_normalized.py', 'amended_sha256')]:
            self.assertEqual(hashlib.sha256((fixture / name).read_bytes()).hexdigest(), amendment[key])
        for args in (['issue', 'view', '999264'], ['pr', 'checks', 'fixture']):
            result = subprocess.run([sys.executable, str(fixture / 'gh_normalized.py'), *args], cwd=self.root, capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(result.stdout), {'state': 'mocked'})
        lines = (self.root / 'gh-events.jsonl').read_text(encoding='utf-8').splitlines()
        self.assertEqual([json.loads(x) for x in lines], [['issue', 'view', '999264'], ['pr', 'checks', 'fixture']])
        self.assertEqual(set(amendment['arm_adapter_hashes']), {'baseline', 'candidate'})
        self.assertTrue(all(x == amendment['amended_sha256'] for x in amendment['arm_adapter_hashes'].values()))
        self.assertEqual(len(amendment['cases']), 6)


if __name__ == '__main__':
    unittest.main()
