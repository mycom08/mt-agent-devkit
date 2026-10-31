"""Canonical routing, returned-coverage provenance and real installed layout tests."""
import copy
import importlib.util
import json
import shutil
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
# These synthetic fixtures preserve the ST-000254 full-safe compatibility
# oracle. Candidate capability assertions live in test_common_capabilities;
# InstalledTests below still loads the actual deployed canonical registry.
REGISTRY = copy.deepcopy(REGISTRY)
if 'common_capabilities' in REGISTRY:
    REGISTRY['common_capabilities']['verified_providers'] = []


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
        # Per-layout bootstrap mappings (PO -> po-core) are registry sources too.
        definitions += [dict(source=path) for layouts in REGISTRY.get('bootstrap',{}).values() for path in layouts.values()]
        for role in REGISTRY['roles']:
            for entry in definitions:
                self.write(entry['source'].format(**mapping, role=role, slug=role.lower(), bootstrap='.mt-agent-devkit/rules/'+role+'_Rules_Bootstrap.md'), '# Fixture\n' + ''.join('## '+str(n)+'. Section\nComplete guidance.\n' for n in range(1,21)))
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

    def test_authoritative_governed_reads(self):
        # The oracle is the actual contract, never files synthesized from registry entries.
        def sections(role, task, source, text, triggers=()):
            contract=(ROOT/source).read_text(encoding='utf-8')
            self.assertIn(text,contract)
            return {(x['source'],x['coverage'].get('section')) for x in self.build(role=role,task=task,triggers=list(triggers))['reads']}
        master='.mt-agent-devkit/rules/Story_Standard.md'
        self.assertIn((master,'14'),sections('QA','qa','.mt-agent-devkit/rules/QA_Rules_Bootstrap.md','Before validation/sign-off, read `Story_Standard.md §14`'))
        self.assertIn((master,'14'),sections('Product_Owner','closure','.mt-agent-devkit/skills/po-verify-close/SKILL.md','Read `Story_Standard.md §14` and the applicable independent per-AC verification report'))
        self.assertIn((master,'14'),sections('Product_Owner','po_validation','.mt-agent-devkit/skills/po-validate-ac/SKILL.md','Read `Story_Standard.md §14` and the current canonical story scope'))
        self.assertIn(('.mt-agent-devkit/rules/QA_Rules_Read_On_Demand.md','2'),sections('QA','implementation','.mt-agent-devkit/instructions/qa_instructions.md','live user instruction conflicts rule in `§2`'))
        self.assertIn(('.mt-agent-devkit/rules/Clean_Code_Rules.md',None),sections('Technical_Lead','review','.mt-agent-devkit/rules/Technical_Lead_Rules_Read_On_Demand.md','**Source code / script changes only**',('source_review',)))
        self.assertIn(('.mt-agent-devkit/rules/Technical_Lead_Rules_Read_On_Demand.md','2'),sections('Technical_Lead','review','.mt-agent-devkit/instructions/technical_lead_instructions.md','After each working session on an unfinished story',('context_anchoring',)))

    def test_conditional_reads_are_not_startup(self):
        fresh=self.build(role='Technical_Lead',task='review')
        self.assertFalse(any('Clean_Code_Rules' in x['source'] for x in fresh['reads']))
        with self.assertRaisesRegex(m.Blocked,'unsupported trigger'): self.build(role='QA',task='qa',triggers=['context_anchoring'])

    def test_all_internal_tasks_and_triggers_resolve_actual_guidance(self):
        for folder in ('rules','instructions','context','contracts','skills'):
            shutil.copytree(ROOT/'.mt-agent-devkit'/folder,self.root/'.mt-agent-devkit'/folder,dirs_exist_ok=True)
        for task,definition in REGISTRY['tasks'].items():
            for role in definition['roles']:
                for trigger,route in REGISTRY['triggers'].items():
                    if route.get('roles') and role not in route['roles']: continue
                    if route.get('layouts') and 'internal' not in route['layouts']: continue
                    with self.subTest(role=role,task=task,trigger=trigger):
                        context=copy.deepcopy(self.request['context'])
                        if trigger=='memory_recall':
                            source=self.bound['RUNTIME_ROOT']+'/memory/'+role+'_Memory_Archive.md'
                            self.write(source,'### Fact 1 — Matched\nActual selected fact.\n### Fact 2 — Other\nExcluded.\n')
                            context['memory_match']=dict(source=source,coverage={'kind':'fact','fact':'1'},reason='observed keyword match')
                        self.build(role=role,task=task,triggers=[trigger],context=context)

    def test_internal_po_tasks_route_to_po_skills_without_retired_rules(self):
        # ST-000288: every internal PO task builds a valid manifest on po-core without the deleted PO rules.
        for folder in ('rules','instructions','context','contracts','skills'):
            shutil.copytree(ROOT/'.mt-agent-devkit'/folder,self.root/'.mt-agent-devkit'/folder,dirs_exist_ok=True)
        retired=('Product_Owner_Rules_Bootstrap.md','Product_Owner_Rules_Read_On_Demand.md','Story_Standard_PO.md')
        for name in retired: self.assertFalse((ROOT/'.mt-agent-devkit/rules'/name).exists())
        expected={'implementation':{'po-core','po-comment'},'fix':{'po-core','po-comment'},'closure':{'po-core','po-verify-close','po-comment'},
                  'scope_question':{'po-core','po-answer-questions','po-comment'},'po_validation':{'po-core','po-validate-ac','po-comment'}}
        tasks={t for t,d in REGISTRY['tasks'].items() if 'Product_Owner' in d['roles']}
        self.assertEqual(tasks,set(expected))
        for task,skills in expected.items():
            with self.subTest(task=task):
                manifest=self.build(role='Product_Owner',task=task,triggers=['story_body_write'])
                m.validate(self.root,manifest,REGISTRY)
                sources=[x['source'] for x in manifest['reads']]
                self.assertEqual(next(x['source'] for x in manifest['reads'] if x['id']=='bootstrap'),'.mt-agent-devkit/skills/po-core/SKILL.md')
                self.assertEqual(skills|{'po-write-story'},{s.split('/')[2] for s in sources if s.startswith('.mt-agent-devkit/skills/')})
                self.assertFalse([s for s in sources if s.endswith(retired)])
        with self.assertRaisesRegex(m.Blocked,'unsupported role/task'): self.build(role='QA',task='po_validation')

    def test_bootstrap_mapping_is_per_layout_and_confined(self):
        registry=copy.deepcopy(REGISTRY)
        # ST-000289: both layouts now route the PO through po-core.
        self.assertEqual(registry['bootstrap'],{'Product_Owner':{'internal':'.mt-agent-devkit/skills/po-core/SKILL.md','target':'.mt-agent-devkit/skills/po-core/SKILL.md'}})
        registry['bootstrap']['Product_Owner']['internal']='../escape.md'
        request=copy.deepcopy(self.request); request.update(role='Product_Owner',task='closure')
        with self.assertRaisesRegex(m.Blocked,'invalid bootstrap mapping'): m.build(self.root,request,registry=registry)
        # Other roles keep their rules bootstrap.
        self.assertEqual(next(x['source'] for x in self.build()['reads'] if x['id']=='bootstrap'),'.mt-agent-devkit/rules/Developer_Rules_Bootstrap.md')

    def test_memory_recall_requires_exact_own_bounded_fact(self):
        with self.assertRaisesRegex(m.Blocked,'memory_match'): self.build(triggers=['memory_recall'])
        context=copy.deepcopy(self.request['context'])
        context['memory_match']=dict(source='docs/story.md',coverage={'kind':'full'},reason='match')
        with self.assertRaisesRegex(m.Blocked,'exact own archive'): self.build(triggers=['memory_recall'],context=context)
        with self.assertRaisesRegex(m.Blocked,'unsupported trigger for layout'): self.build(triggers=['endpoint_change'])

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
                        # Project-owned wiki inputs are supplied by the project, not installed by the harness.
                        standards=target/'docs/wiki/Development_Standards.md'; standards.parent.mkdir(parents=True,exist_ok=True)
                        standards.write_text((ROOT/'.mt-agent-devkit/distribution/phase2/templates/wiki/Development_Standards_template.md').read_text(encoding='utf-8'),encoding='utf-8')
                        context={}
                        for name in ('story','decisions','artifact','verification','merge','question','pause'):
                            path=target/'docs'/ (name+'.md'); path.parent.mkdir(exist_ok=True); path.write_text('# '+name+'\n',encoding='utf-8')
                            context[name]=dict(source='docs/'+name+'.md',coverage={'kind':'full'},reason=name)
                        cases=[(role,task) for task,definition in REGISTRY['tasks'].items() for role in definition['roles']]
                        for role,task in cases:
                            request=dict(provider=provider,bindings=bound,layout='target',role=role,task=task,stage=task,story='ST-000254',session_state='fresh',session='fixture',mode=mode,context=context,triggers=[])
                            for name in ('findings','diff'):
                                path=target/'docs'/(name+'.md'); path.write_text('# '+name+'\n',encoding='utf-8')
                                context[name]=dict(source='docs/'+name+'.md',coverage={'kind':'full'},reason=name)
                            built=installed.build(target,request)
                            installed.validate(target,built)
                            self.assertEqual(built['reads'][0]['source'],'.'+provider+'/harness/Provider_Adapter.md')
                            selected={(x['source'],x['coverage'].get('section')) for x in built['reads']}
                            if role=='Product_Owner':
                                # ST-000289: target PO manifests resolve to po-core and the installed po-* skills.
                                self.assertEqual(next(x['source'] for x in built['reads'] if x['id']=='bootstrap'),'.mt-agent-devkit/skills/po-core/SKILL.md')
                                self.assertFalse([x['source'] for x in built['reads'] if x['source'].endswith(('Product_Owner_Rules_Bootstrap.md','Product_Owner_Rules_Read_On_Demand.md','Story_Standard_PO.md'))])
                                skills={x['source'].split('/')[2] for x in built['reads'] if x['source'].startswith('.mt-agent-devkit/skills/')}
                                self.assertEqual(skills,{'implementation':{'po-core','po-comment'},'fix':{'po-core','po-comment'},'closure':{'po-core','po-verify-close','po-comment'},
                                                         'scope_question':{'po-core','po-answer-questions','po-comment'},'po_validation':{'po-core','po-validate-ac','po-comment'}}[task])
                                if task in ('closure','po_validation'):
                                    self.assertIn(('.mt-agent-devkit/rules/Story_Standard.md','14'),selected)
                            if task=='qa':
                                authority=(target/'.mt-agent-devkit/rules/QA_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                self.assertIn('read `Story_Standard.md §14`',authority)
                                self.assertIn(('.mt-agent-devkit/rules/Story_Standard.md','14'),selected)
                            if role=='QA' and task in ('implementation','fix'):
                                authority=(target/'.mt-agent-devkit/rules/QA_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                self.assertIn('`QA_Rules_Read_On_Demand.md §2`',authority)
                                self.assertIn(('.mt-agent-devkit/rules/QA_Rules_Read_On_Demand.md','2'),selected)
                            for trigger,route in REGISTRY['triggers'].items():
                                if route.get('roles') and role not in route['roles']: continue
                                if route.get('layouts') and 'target' not in route['layouts']: continue
                                if trigger=='ci_pending' and mode=='strict': continue
                                if trigger=='memory_recall':
                                    own=bound['RUNTIME_ROOT']+'/memory/'+role+'_Memory_Archive.md'
                                    (target/own).write_text('### Fact 1 — Match\nBounded evidence.\n',encoding='utf-8')
                                    context['memory_match']=dict(source=own,coverage={'kind':'fact','fact':'1'},reason='keyword match')
                                extended=installed.extend(target,built,[trigger])
                                installed.validate(target,extended)
                                if trigger=='pre_pr' and role=='Technical_Lead':
                                    authority=(target/'.mt-agent-devkit/rules/Technical_Lead_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                    self.assertIn('about to open a PR',authority)
                                    self.assertIn(('.mt-agent-devkit/rules/Technical_Lead_Rules_Read_On_Demand.md','3'),{(x['source'],x['coverage'].get('section')) for x in extended['reads']})
                                if trigger=='development_convention':
                                    authority=(target/'.mt-agent-devkit/rules/Developer_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                    self.assertIn('Read `docs/wiki/Development_Standards.md`',authority)
                                    self.assertTrue(any(x['source']=='docs/wiki/Development_Standards.md' for x in extended['reads']))
                                if trigger=='clean_code_change':
                                    authority=(target/'.mt-agent-devkit/rules/Developer_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                    self.assertIn('**For Clean Code or refactor stories**',authority)
                                    self.assertTrue(any(x['source'].endswith('/Clean_Code_Rules.md') for x in extended['reads']))
                                if trigger=='source_review':
                                    authority=(target/'.mt-agent-devkit/rules/Technical_Lead_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                    self.assertIn('Clean_Code_Rules.md',authority)
                                    self.assertTrue(any(x['source'].endswith('/Clean_Code_Rules.md') for x in extended['reads']))


if __name__ == '__main__': unittest.main()
