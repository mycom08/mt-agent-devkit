"""Canonical routing, returned-coverage provenance and real installed layout tests."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


m = module('read_manifest', '.mt-agent-devkit/scripts/read_manifest.py')
REGISTRY = m.load(m.REGISTRY)


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bound = {'PROVIDER_ROOT': '.codex', 'RUNTIME_ROOT': '.codex/agents/working', 'COMMAND_ROOT': '.codex/agents'}
        self.write('.codex/harness/state-paths.json', json.dumps(self.bound))
        self.request = dict(provider='codex', bindings=self.bound, layout='internal', role='Developer', task='implementation', stage='implementation', story='ST-000254', session_state='fresh', session='worker-1', mode='github', triggers=[], context={})
        mapping = {**self.bound, 'priming': '.mt-agent-devkit/context/Project_Priming_Bootstrap.md'}
        definitions = REGISTRY['entry'] + REGISTRY['ordinary']
        definitions += [x for role in REGISTRY['roles'].values() for x in role]
        definitions += [x for task in REGISTRY['tasks'].values() for x in task['reads']]
        definitions += [x for trigger in REGISTRY['triggers'].values() for x in trigger['reads']]
        for role in REGISTRY['roles']:
            for entry in definitions:
                self.write(entry['source'].format(**mapping, role=role, slug=role.lower()), '# Fixture\n' + ''.join('## '+str(n)+'. Section\nComplete guidance.\n' for n in range(1,21)))
        for name in ('story','decisions','artifact','verification','merge','findings','diff','delta','question','pause'):
            self.write('docs/'+name+'.md', '# '+name+'\nCanonical bounded context.\n')
            self.request['context'][name] = dict(source='docs/'+name+'.md',coverage={'kind':'full'},reason=name)

    def write(self, path, text):
        path = self.root/path
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text,encoding='utf-8')

    def build(self, **changes):
        request = copy.deepcopy(self.request)
        request.update(changes)
        return m.build(self.root,request,registry=REGISTRY)

    def test_exact_implementation_and_forbidden_reads(self):
        manifest = self.build()
        self.assertEqual({x['id'] for x in manifest['reads']},{'adapter','role','common','priming','record','bootstrap','memory','context_story','context_decisions','story_workflow'})
        self.assertFalse(any('Story_Standard_Dev' in x['source'] or 'Archive' in x['source'] for x in manifest['reads']))

    def test_order_prerequisites(self):
        reads = self.build()['reads']; seen=set()
        for entry in reads:
            self.assertLessEqual(set(entry['after']),seen)
            seen.add(entry['id'])
        self.assertEqual([x['id'] for x in reads[:3]],['adapter','role','common'])

    def test_assigned_role_implementation_requirements(self):
        for role,required in [('Technical_Lead',{'tl_implementation_1','tl_implementation_3','tl_implementation_4'}),('QA',{'qa_implementation'}),('Business_Analyst',{'ba_implementation'})]:
            reads=self.build(role=role)['reads']
            self.assertLessEqual(required,{x['id'] for x in reads})
            if role in ('Technical_Lead','QA'):
                ids=[x['id'] for x in reads]
                self.assertLess(ids.index('standard'),ids.index('bootstrap'))

    def test_peer_review_and_independent_qa(self):
        self.assertIn('review_checklist',{x['id'] for x in self.build(task='peer_review')['reads']})
        self.assertIn('standard',{x['id'] for x in self.build(role='QA',task='qa')['reads']})
        self.assertIn('review',{x['id'] for x in self.build(role='Technical_Lead',task='review')['reads']})

    def test_reduced_question_and_closure(self):
        for role,task in [('Technical_Lead','question'),('Product_Owner','closure')]:
            reads=self.build(role=role,task=task)['reads']; ids={x['id'] for x in reads}
            self.assertFalse({'priming','record','standard'} & ids)
            self.assertIn('memory',ids)
            self.assertIn('common',ids)
            if task=='question': self.assertNotIn('bootstrap',ids)
            else: self.assertIn('acceptance',ids)

    def delta(self):
        return dict(findings='docs/findings.md',affected_ac='AC4',requirements='none',decisions='none',diff='docs/diff.md',reviewed_sha='a'*40,current_sha='b'*40)

    def receipts(self, manifest):
        return [m.attest(self.root,manifest,x['id'],returned_complete=True,truncation_recovered=True) for x in manifest['reads'] if not x['id'].startswith('context_')]

    def test_same_session_omits_only_proven_unchanged_reads(self):
        fresh=self.build(task='fix'); receipts=self.receipts(fresh)
        request=copy.deepcopy(fresh['request']); request.update(session_state='same',delta=self.delta())
        result=m.build(self.root,request,receipts,REGISTRY)
        self.assertTrue(result['omitted'])
        self.assertTrue(all(x['id'].startswith('context_') for x in result['reads']))
        self.assertIn('context_delta',{x['id'] for x in result['reads']})
        m.validate(self.root,result,REGISTRY)

    def test_unknown_provenance_safe_path(self):
        result=self.build(session_state='same',delta=self.delta())
        self.assertIn('adapter',{x['id'] for x in result['reads']})
        self.assertFalse(result['omitted'])

    def test_missing_identity_expired_and_foreign_session_receipts(self):
        fresh=self.build(); receipts=self.receipts(fresh)
        for state,session in [('expired','worker-1'),('same',None),('same','another-worker')]:
            request=copy.deepcopy(fresh['request']); request.update(session_state=state,session=session,delta=self.delta())
            result=m.build(self.root,request,receipts,REGISTRY)
            self.assertFalse(result['omitted'])
            if session is None: self.assertEqual(result['effective_session_state'],'expired')

    def test_changed_source_requires_read(self):
        fresh=self.build(); receipts=self.receipts(fresh)
        self.write('.mt-agent-devkit/rules/Developer_Rules_Bootstrap.md','# Changed\n')
        request=copy.deepcopy(fresh['request']); request.update(session_state='same',delta=self.delta())
        result=m.build(self.root,request,receipts,REGISTRY)
        self.assertIn('bootstrap',{x['id'] for x in result['reads']})
        self.assertNotIn('bootstrap',{x['id'] for x in result['omitted']})

    def test_relevant_route_and_selector_changes(self):
        fresh=self.build(role='Technical_Lead',task='question'); receipts=self.receipts(fresh)
        request=copy.deepcopy(fresh['request']); request.update(session_state='same',delta=self.delta())
        for changed in ('selector','reason','revision'):
            registry=copy.deepcopy(REGISTRY)
            if changed=='selector': registry['tasks']['question']['reads'][1]['coverage']['section']='14'
            elif changed=='reason': registry['tasks']['question']['reads'][1]['reason']='changed obligation'
            else: registry['revision']='next-version'
            result=m.build(self.root,request,receipts,registry)
            self.assertIn('comment',{x['id'] for x in result['reads']})

    def test_unrelated_route_does_not_invalidate(self):
        fresh=self.build(); receipts=self.receipts(fresh)
        request=copy.deepcopy(fresh['request']); request.update(session_state='same',delta=self.delta())
        registry=copy.deepcopy(REGISTRY); registry['tasks']['closure']['reads'][0]['reason']='unrelated'
        self.assertTrue(m.build(self.root,request,receipts,registry)['omitted'])

    def test_attestation_requires_actual_complete_return(self):
        fresh=self.build()
        for complete,recovered in [(False,False),(True,False),(False,True)]:
            with self.assertRaisesRegex(m.Blocked,'returned coverage'): m.attest(self.root,fresh,'bootstrap',returned_complete=complete,truncation_recovered=recovered)
        with self.assertRaisesRegex(m.Blocked,'not a required read'): m.attest(self.root,fresh,'absent',returned_complete=True,truncation_recovered=True)

    def test_trigger_addition_and_strict_wait(self):
        fresh=self.build(); result=m.extend(self.root,fresh,['local_verify','retro_required'],REGISTRY)
        self.assertTrue({'trigger_local_verify','trigger_retro_required'} <= {x['id'] for x in result['reads']})
        self.assertIn('trigger_retro_rules',{x['id'] for x in result['reads']})
        self.assertFalse(any('Retro_Rules' in x['source'] for x in fresh['reads']))
        with self.assertRaisesRegex(m.Blocked,'strict mode'): self.build(mode='strict',triggers=['ci_pending'])
        with self.assertRaisesRegex(m.Blocked,'unknown observable'): self.build(triggers=['invented'])

    def test_validation_independently_rejects_omission_reorder_and_forgery(self):
        fresh=self.build()
        for mutation in ('missing','reorder','digest','omission'):
            value=copy.deepcopy(fresh)
            if mutation=='missing': value['reads'].pop()
            elif mutation=='reorder': value['reads'].reverse()
            elif mutation=='digest': value['reads'][0]['content_sha256']='0'*64
            else: value['omitted'].append(value['reads'].pop())
            with self.assertRaisesRegex(m.Blocked,'canonical requirement'): m.validate(self.root,value,REGISTRY)

    def test_context_empty_missing_foreign_and_insufficient_question(self):
        for context in ({}, {'story':self.request['context']['story']}):
            with self.assertRaisesRegex(m.Blocked,'context requirement'): self.build(role='Technical_Lead',task='question',context=context)
        context=copy.deepcopy(self.request['context']); context['story']['source']='.claude/agents/tmp/story.md'
        with self.assertRaisesRegex(m.Blocked,'foreign context'): self.build(context=context)
        self.write('docs/story.md','')
        with self.assertRaisesRegex(m.Blocked,'empty context'): self.build()

    def test_invalid_bindings_sources_roles_selectors_and_empty_inputs(self):
        with self.assertRaisesRegex(m.Blocked,'bindings'): self.build(bindings={})
        with self.assertRaisesRegex(m.Blocked,'unsupported role/task'): self.build(role='QA',task='closure')
        with self.assertRaisesRegex(m.Blocked,'layout'): self.build(layout='unknown')
        with self.assertRaises(m.Blocked): m.build(self.root,{})
        with self.assertRaises(m.Blocked): m.safe(self.root,'../escape')
        with self.assertRaisesRegex(m.Blocked,'invalid section'): m.covered(self.root,'docs/story.md',{'kind':'section','section':'.*'})
        with self.assertRaisesRegex(m.Blocked,'matched 0'): m.covered(self.root,'docs/story.md',{'kind':'section','section':'99'})
        self.write('docs/ambiguous.md','## 1. First\n## 1. Second\n')
        with self.assertRaisesRegex(m.Blocked,'matched 2'): m.covered(self.root,'docs/ambiguous.md',{'kind':'section','section':'1'})
        with self.assertRaisesRegex(m.Blocked,'missing source'): m.covered(self.root,'absent.md',{'kind':'full'})


class InstalledTests(unittest.TestCase):
    def test_real_all_provider_mode_layouts_use_same_registry_and_helper(self):
        builder=module('manifest_builder','.mt-agent-devkit/distribution/phase2/build_bundle.py')
        deployment=module('manifest_deployment','.mt-agent-devkit/distribution/phase2/deployment.py')
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder); bundle=base/'bundle'; builder.build(ROOT,bundle)
            manifest=bundle/'deployment.json'
            source=dict(kind='local',tag=None,commit='a'*40,snapshot_version='0.1.53-SNAPSHOT',manifest_sha256=deployment.digest(manifest.read_bytes()))
            for provider in ('claude','antigravity','codex'):
                for mode in ('github','strict'):
                    with self.subTest(provider=provider,mode=mode):
                        target=base/(provider+mode); target.mkdir()
                        bound={'PROVIDER_ROOT':'.'+provider,'RUNTIME_ROOT':'.'+provider+'/agents','COMMAND_ROOT':'.'+provider+'/agents'}
                        entrypoint='CLAUDE.md' if provider=='claude' else 'AGENTS.md'
                        adaptations={entrypoint:'# Fixture\n','.mt-agent-devkit/context/Project_Priming.md':'# Fixture\n','.mt-agent-devkit/context/Document_Index.md':'# Docs\n','.gitignore':'# Ignore\n'}
                        plan=deployment.plan(target,manifest,source,mode,'repo',{provider:bound},adaptations)
                        deployment.apply(target,plan); deployment.verify(target)
                        self.assertEqual((target/'.mt-agent-devkit/contracts/read-routing.json').read_bytes(),m.REGISTRY.read_bytes())
                        installed=module('installed_manifest_'+provider+mode,str((target/'.mt-agent-devkit/scripts/read_manifest.py').absolute()))
                        context={}
                        for name in ('story','decisions','artifact','verification','merge','question','pause'):
                            path=target/'docs'/ (name+'.md'); path.parent.mkdir(exist_ok=True); path.write_text('# '+name+'\n',encoding='utf-8')
                            context[name]=dict(source='docs/'+name+'.md',coverage={'kind':'full'},reason=name)
                        for role,task in [('Developer','implementation'),('Developer','peer_review'),('Technical_Lead','review'),('QA','qa'),('Product_Owner','closure'),('Technical_Lead','question')]:
                            request=dict(provider=provider,bindings=bound,layout='target',role=role,task=task,stage=task,story='ST-000254',session_state='fresh',session='fixture',mode=mode,context=context,triggers=[])
                            built=installed.build(target,request)
                            installed.validate(target,built)
                            self.assertEqual(built['reads'][0]['source'],'.'+provider+'/harness/Provider_Adapter.md')


if __name__ == '__main__': unittest.main()
