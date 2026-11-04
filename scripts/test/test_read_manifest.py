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
        # ST-000309: per-role Common skill lists and role-source substitutions are registry sources too.
        definitions += [dict(source=path) for layouts in REGISTRY.get('common',{}).values() for paths in layouts.values() for path in paths]
        definitions += [dict(source=path) for layouts in REGISTRY.get('role_sources',{}).values() for table in layouts.values() for paths in table.values() for path in paths]
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
        self.assertEqual({x['id'] for x in manifest['reads']},{'adapter','role','common','common_agent_security','common_token_efficiency','common_shell_rules','common_retro',
                                                              'priming','record','bootstrap','memory','dev_implementation','context_story','context_decisions','story_workflow'})
        self.assertFalse(any('Story_Standard_Dev' in x['source'] or 'Archive' in x['source'] for x in manifest['reads']))
        # Other roles keep the full Common bootstrap and their rules bootstrap.
        tl={x['id']:x['source'] for x in self.build(role='Technical_Lead')['reads']}
        self.assertEqual((tl['common'],tl['bootstrap']),('.mt-agent-devkit/rules/Agent_Common_Bootstrap.md','.mt-agent-devkit/rules/Technical_Lead_Rules_Bootstrap.md'))

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
        # ST-000308: internal QA/TL rows read the common skills their rule files now point to.
        self.assertIn(('.mt-agent-devkit/skills/raise-question/SKILL.md',None),sections('QA','implementation','.mt-agent-devkit/instructions/qa_instructions.md','live user instruction conflicts: `raise-question` §5'))
        self.assertIn(('.mt-agent-devkit/skills/clean-code/SKILL.md',None),sections('Technical_Lead','review','.mt-agent-devkit/rules/Technical_Lead_Rules_Read_On_Demand.md','**Source code / script changes only** — verify compliance with the `clean-code` skill',('source_review',)))
        self.assertIn(('.mt-agent-devkit/rules/Technical_Lead_Rules_Read_On_Demand.md','2'),sections('Technical_Lead','review','.mt-agent-devkit/instructions/technical_lead_instructions.md','After each working session on an unfinished story',('context_anchoring',)))

    def test_conditional_reads_are_not_startup(self):
        fresh=self.build(role='Technical_Lead',task='review')
        self.assertFalse(any('Clean_Code_Rules' in x['source'] or '/clean-code/' in x['source'] for x in fresh['reads']))
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
        # ST-000304: po-comment requires the shared comment skill, so every PO task also reads it.
        expected={'implementation':{'po-core','po-comment','comment'},'fix':{'po-core','po-comment','comment'},'closure':{'po-core','po-verify-close','po-comment','comment'},
                  'scope_question':{'po-core','po-answer-questions','po-comment','comment'},'po_validation':{'po-core','po-validate-ac','po-comment','comment'}}
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

    def test_every_role_comment_route_resolves_to_comment_skill(self):
        # ST-000304: the shared comment skill owns the comment standard and Commenter gate for every role.
        for folder in ('rules','instructions','context','contracts','skills'):
            shutil.copytree(ROOT/'.mt-agent-devkit'/folder,self.root/'.mt-agent-devkit'/folder,dirs_exist_ok=True)
        skill='.mt-agent-devkit/skills/comment/SKILL.md'
        roles=('Developer','Technical_Lead','QA','Product_Owner','Business_Analyst','UI_UX_Designer')
        self.assertEqual(REGISTRY['triggers']['commenter']['roles'],[])
        for role in roles:
            with self.subTest(role=role):
                manifest=self.build(role=role,task='implementation',triggers=['commenter'])
                m.validate(self.root,manifest,REGISTRY)
                entry=next(x for x in manifest['reads'] if x['id']=='trigger_commenter')
                self.assertEqual((entry['source'],entry['coverage']),(skill,{'kind':'full'}))
        # ST-000309: the internal Developer routing row loads only the comment skill.
        manifest=self.build(triggers=['story_comment'])
        reads={x['id']:x for x in manifest['reads']}
        self.assertEqual(reads['trigger_story_comment_standard']['source'],skill)
        self.assertNotIn('trigger_story_comment',reads)
        # Comment-bearing PO and TL question tasks read the skill without a trigger.
        for role,task in (('Product_Owner','closure'),('Product_Owner','scope_question'),('Product_Owner','po_validation'),('Technical_Lead','question')):
            with self.subTest(role=role,task=task):
                self.assertIn(skill,[x['source'] for x in self.build(role=role,task=task)['reads']])
        # Role rules point at the skill instead of restating it.
        for name in ('Story_Standard.md','Story_Standard_TL.md','Story_Standard_QA.md','Story_Standard_UIUX.md'):
            self.assertIn(skill,(ROOT/'.mt-agent-devkit/rules'/name).read_text(encoding='utf-8'),name)
        self.assertIn('**Requires:** `po-core`, `comment`',(ROOT/'.mt-agent-devkit/skills/po-comment/SKILL.md').read_text(encoding='utf-8'))

    def test_non_developer_rows_point_to_common_skills_in_both_layouts(self):
        # ST-000308 re-pointed the non-Developer rows to the common skills internally;
        # ST-000312 removed their target overrides, so targets read the shipped skills too.
        for folder in ('rules','instructions','context','contracts','skills'):
            shutil.copytree(ROOT/'.mt-agent-devkit'/folder,self.root/'.mt-agent-devkit'/folder,dirs_exist_ok=True)
        cases=[('Technical_Lead','implementation',[],'tl_implementation_1','git-workflow'),
               ('Technical_Lead','fix',[],'tl_implementation_3','pre-pr-gate'),
               ('Technical_Lead','implementation',['pre_pr'],'trigger_tl_pre_pr','pre-pr-gate'),
               ('Technical_Lead','review',['source_review'],'trigger_clean_code','clean-code'),
               ('Technical_Lead','review',[],'review_procedure','pr-review'),
               ('QA','implementation',[],'qa_implementation','pre-pr-gate'),
               ('QA','fix',[],'qa_implementation_conflict','raise-question'),
               ('QA','implementation',['live_conflict'],'trigger_qa_conflict','raise-question'),
               ('Business_Analyst','implementation',[],'ba_implementation','pre-pr-gate'),
               ('UI_UX_Designer','implementation',['consultation'],'trigger_ui_consultation','raise-question'),
               ('UI_UX_Designer','fix',['live_conflict'],'trigger_ui_live_conflict','raise-question')]
        definitions=[x for t in REGISTRY['tasks'].values() for x in t['reads']]+[x for t in REGISTRY['triggers'].values() for x in t['reads']]
        for role,task,triggers,entry_id,skill in cases:
            with self.subTest(role=role,task=task,entry=entry_id):
                manifest=self.build(role=role,task=task,triggers=triggers)
                m.validate(self.root,manifest,REGISTRY)
                entry=next(x for x in manifest['reads'] if x['id']==entry_id)
                self.assertEqual((entry['source'],entry['coverage']),('.mt-agent-devkit/skills/'+skill+'/SKILL.md',{'kind':'full'}))
                for definition in (x for x in definitions if x['id']==entry_id):
                    # tl_implementation_3 stays off in targets: their pre_pr trigger delivers the same skill.
                    expected={'target':{'enabled':False}} if entry_id=='tl_implementation_3' else {}
                    self.assertEqual(definition.get('layouts',{}),expected,entry_id)
        for definition in (x for x in definitions if x['id'] in ('trigger_document_paths','trigger_ui_consultation','trigger_ui_live_conflict')):
            self.assertNotIn('layouts',definition,definition['id'])
        for role in REGISTRY['roles']:
            with self.subTest(role=role,entry='trigger_document_paths'):
                entry=next(x for x in self.build(role=role,triggers=['document_update'])['reads'] if x['id']=='trigger_document_paths')
                self.assertEqual((entry['source'],entry['coverage']),('.mt-agent-devkit/context/Document_Index.md',{'kind':'full'}))
        # The rule files point at the skills instead of restating them.
        rules=ROOT/'.mt-agent-devkit/rules'
        for name,skills in (('Technical_Lead_Rules_Read_On_Demand.md',('git-workflow','pre-pr-gate','pr-review','clean-code')),
                            ('QA_Rules_Read_On_Demand.md',('pre-pr-gate','raise-question')),('Business_Analyst_Rules_Read_On_Demand.md',('pre-pr-gate',)),
                            ('UI_UX_Designer_Rules_Read_On_Demand.md',('raise-question',))):
            text=(rules/name).read_text(encoding='utf-8')
            for skill in skills: self.assertIn('.mt-agent-devkit/skills/'+skill+'/SKILL.md',text,name)
            self.assertNotIn('| Change type | Required local check |',text,name)
        self.assertNotIn('Clean_Code_Rules.md',(rules/'Technical_Lead_Rules_Read_On_Demand.md').read_text(encoding='utf-8'))

    def test_bootstrap_mapping_is_per_layout_and_confined(self):
        registry=copy.deepcopy(REGISTRY)
        # ST-000289: both layouts now route the PO through po-core.
        # ST-000309/ST-000310: the Developer switches to dev-core internally, then in targets.
        self.assertEqual(registry['bootstrap'],{'Product_Owner':{'internal':'.mt-agent-devkit/skills/po-core/SKILL.md','target':'.mt-agent-devkit/skills/po-core/SKILL.md'},
                                                'Developer':{'internal':'.mt-agent-devkit/skills/dev-core/SKILL.md','target':'.mt-agent-devkit/skills/dev-core/SKILL.md'}})
        registry['bootstrap']['Product_Owner']['internal']='../escape.md'
        request=copy.deepcopy(self.request); request.update(role='Product_Owner',task='closure')
        with self.assertRaisesRegex(m.Blocked,'invalid bootstrap mapping'): m.build(self.root,request,registry=registry)
        # Other roles keep their rules bootstrap.
        self.assertEqual(next(x['source'] for x in self.build()['reads'] if x['id']=='bootstrap'),'.mt-agent-devkit/skills/dev-core/SKILL.md')
        self.assertEqual(next(x['source'] for x in self.build(role='QA')['reads'] if x['id']=='bootstrap'),'.mt-agent-devkit/rules/QA_Rules_Bootstrap.md')

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
        self.write('.mt-agent-devkit/skills/dev-core/SKILL.md','# Changed\n')
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


SKILL = '.mt-agent-devkit/skills/{}/SKILL.md'.format
ON_DEMAND = '.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md'
DEV_RETIRED = ('Developer_Rules_Bootstrap.md', 'Developer_Rules_Read_On_Demand.md', 'Story_Standard_Dev.md', 'Clean_Code_Rules.md')


class DeveloperSkillRoutingTests(unittest.TestCase):
    """ST-000309: the internal Developer route reads skills: common and bootstrap overrides, role_sources."""
    write = RoutingTests.write
    build = RoutingTests.build

    def setUp(self):
        RoutingTests.setUp(self)

    def real(self):
        for folder in ('rules','instructions','context','contracts','skills'):
            shutil.copytree(ROOT/'.mt-agent-devkit'/folder,self.root/'.mt-agent-devkit'/folder,dirs_exist_ok=True)

    def built(self, registry, **changes):
        request=copy.deepcopy(self.request); request.update(changes)
        return m.build(self.root,request,registry=registry)

    def test_common_override_keeps_the_common_anchor_and_orders_the_rest_after_it(self):
        reads=self.build()['reads']; by={x['id']:x for x in reads}
        expected=[('common','pre-work',['role']),('common_agent_security','agent-security',['common']),('common_token_efficiency','token-efficiency',['common']),
                  ('common_shell_rules','shell-rules',['common']),('common_retro','retro',['common'])]
        for entry_id,skill,after in expected:
            self.assertEqual((by[entry_id]['source'],by[entry_id]['coverage'],by[entry_id]['after']),(SKILL(skill),{'kind':'full'},after))
        self.assertEqual(by['priming']['after'],['common'])
        self.assertEqual(by['bootstrap']['source'],SKILL('dev-core'))
        self.assertFalse(any(x['source'].startswith('.mt-agent-devkit/rules/Agent_Common_') for x in reads))
        # The override is per layout: a layout the registry does not name keeps the Common file.
        registry=copy.deepcopy(REGISTRY); registry['common']['Developer']={'target':registry['common']['Developer']['internal']}
        self.assertEqual(next(x for x in self.built(registry)['reads'] if x['id']=='common')['source'],'.mt-agent-devkit/rules/Agent_Common_Bootstrap.md')

    def test_role_sources_map_to_a_list_with_full_coverage(self):
        registry=copy.deepcopy(REGISTRY)
        registry['role_sources']['Developer']['internal'][ON_DEMAND+' §3']=[SKILL('retro-contribution'),SKILL('troubleshooting')]
        by={x['id']:x for x in self.built(registry,triggers=['retro_required'])['reads']}
        first,second=by['trigger_retro_required'],by['trigger_retro_required_2']
        self.assertEqual((first['source'],first['coverage'],first['after']),(SKILL('retro-contribution'),{'kind':'full'},['common']))
        self.assertEqual((second['source'],second['coverage'],second['after']),(SKILL('troubleshooting'),{'kind':'full'},['common']))
        self.assertEqual(by['trigger_retro_rules']['after'],['trigger_retro_required'])
        # Every section-scoped shared Common read becomes a full skill read.
        for trigger,entry_id,skill in (('tooling_failure','trigger_tooling_failure','troubleshooting'),('credential_gate','trigger_credential_gate','credential-gate'),
                                       ('runtime_handoff','trigger_runtime_handoff','handoff'),('memory_fact','trigger_memory_fact','agent-memory'),
                                       ('working_record','trigger_working_record','working-record')):
            with self.subTest(trigger=trigger):
                entry=next(x for x in self.build(triggers=[trigger])['reads'] if x['id']==entry_id)
                self.assertEqual((entry['source'],entry['coverage']),(SKILL(skill),{'kind':'full'}))

    def test_duplicate_skill_sources_are_dropped_and_after_rewritten(self):
        # completion -> [retro, handoff]: retro is already read at spawn, so only handoff is added.
        by={x['id']:x for x in self.build(triggers=['completion'])['reads']}
        self.assertNotIn('trigger_completion',by)
        self.assertEqual((by['trigger_completion_2']['source'],by['trigger_completion_2']['after']),(SKILL('handoff'),['common']))
        # Both memory_fact reads resolve to agent-memory: the first is kept.
        ids=[x['id'] for x in self.build(triggers=['memory_fact'])['reads']]
        self.assertIn('trigger_memory_fact',ids); self.assertNotIn('trigger_memory_shape',ids)
        # shell_safety resolves to shell-rules, already read at spawn.
        self.assertNotIn('trigger_shell_safety',{x['id'] for x in self.build(triggers=['shell_safety'])['reads']})
        # An `after` naming a dropped entry is rewritten to the kept one.
        registry=copy.deepcopy(REGISTRY)
        registry['role_sources']['Developer']['internal'][ON_DEMAND+' §3']=[SKILL('retro')]
        reads=self.built(registry,triggers=['retro_required'])['reads']; by={x['id']:x for x in reads}
        self.assertNotIn('trigger_retro_required',by)
        self.assertEqual(by['trigger_retro_rules']['after'],['common_retro'])
        self.assertEqual(len({x['source'] for x in reads if x['source'].startswith('.mt-agent-devkit/skills/')}),
                         len([x for x in reads if x['source'].startswith('.mt-agent-devkit/skills/')]))
        # Roles without a skill-based route keep duplicate sources as before.
        self.assertIn('trigger_shell_safety',{x['id'] for x in self.build(role='Technical_Lead',triggers=['shell_safety'])['reads']})

    def test_invalid_overrides_block(self):
        for key,value in (('common',{'Developer':{'internal':['../escape.md']}}),('common',{'Developer':{'internal':[]}}),
                          ('role_sources',{'Developer':{'internal':{ON_DEMAND+' §2':SKILL('troubleshooting')}}}),('role_sources',{'Developer':{'internal':[]}})):
            with self.subTest(key=key,value=value):
                registry=copy.deepcopy(REGISTRY); registry[key]=value
                with self.assertRaisesRegex(m.Blocked,'invalid'): self.built(registry)
        with self.assertRaisesRegex(m.Blocked,'route has no memory entry'): m.entry([],'memory','two-tier memory route')

    def test_every_developer_task_and_trigger_resolves_to_skills(self):
        self.real()
        for name in DEV_RETIRED: self.assertFalse((ROOT/'.mt-agent-devkit/rules'/name).exists(),name)
        allowed={'.codex/harness/Provider_Adapter.md','.mt-agent-devkit/instructions/developer_instructions.md','.mt-agent-devkit/context/Project_Priming_Bootstrap.md',
                 '.mt-agent-devkit/context/Project_Priming_Read_On_Demand.md','.mt-agent-devkit/context/Document_Index.md','.mt-agent-devkit/rules/UI_Prototype_Rules.md',
                 '.mt-agent-devkit/rules/Retro_Rules.md','.mt-agent-devkit/contracts/Wait_Work.md','.mt-agent-devkit/contracts/Local_Verify.md','.mt-agent-devkit/contracts/Read_Manifest.md'}
        task_skill={'implementation':'dev-implement','fix':'dev-deliver','peer_review':'pr-review'}
        self.assertEqual({t for t,d in REGISTRY['tasks'].items() if 'Developer' in d['roles']},set(task_skill))
        for task,skill in task_skill.items():
            for trigger,route in REGISTRY['triggers'].items():
                if route.get('roles') and 'Developer' not in route['roles']: continue
                if route.get('layouts') and 'internal' not in route['layouts']: continue
                with self.subTest(task=task,trigger=trigger):
                    context=copy.deepcopy(self.request['context'])
                    if trigger=='memory_recall':
                        source=self.bound['RUNTIME_ROOT']+'/memory/Developer_Memory_Archive.md'
                        self.write(source,'### Fact 1 — Matched\nActual selected fact.\n')
                        context['memory_match']=dict(source=source,coverage={'kind':'fact','fact':'1'},reason='observed keyword match')
                    manifest=self.build(task=task,triggers=[trigger],context=context)
                    m.validate(self.root,manifest,REGISTRY)
                    sources=[x['source'] for x in manifest['reads'] if not x['id'].startswith('context_')]
                    self.assertIn(SKILL(skill),sources)
                    other=[s for s in sources if not s.startswith(('.mt-agent-devkit/skills/',self.bound['RUNTIME_ROOT']+'/')) and s not in allowed]
                    self.assertEqual([],other)
                    self.assertFalse([s for s in sources if s.endswith(DEV_RETIRED)])
        # Point-of-use triggers each add their skill.
        for trigger,skills in (('pre_pr',('change-metadata','pre-pr-gate')),('consultation',('raise-question',)),('live_conflict',('raise-question',)),
                               ('report_blocker',('raise-question',)),('document_update',('project-docs',)),('technical_doc_divergence',('dev-verify',)),
                               ('clean_code_change',('clean-code',)),('source_review',('clean-code',)),('retro_required',('retro-contribution',))):
            with self.subTest(trigger=trigger):
                sources=[x['source'] for x in self.build(triggers=[trigger])['reads']]
                for skill in skills: self.assertIn(SKILL(skill),sources)
        reads=[x['id'] for x in self.build(triggers=['pre_pr'])['reads']]
        self.assertLess(reads.index('trigger_pre_pr'),reads.index('trigger_pre_pr_gate'))

    def test_developer_target_rows_read_the_shipped_skills_directly(self):
        """ST-000311: the old Developer target sources and their role_sources keys are gone; each row reads its skill."""
        expected={('peer_review','review_checklist'):'pr-review',('peer_review','review'):'pr-review',('document_update','trigger_document_update'):'project-docs',
                  ('consultation','trigger_consultation'):'raise-question',('live_conflict','trigger_live_conflict'):'raise-question',
                  ('pre_pr','trigger_pre_pr'):'pre-pr-gate',('report_blocker','trigger_report_blocker'):'raise-question',
                  ('technical_doc_divergence','trigger_technical_doc_divergence'):'dev-verify',('endpoint_change','trigger_endpoint_change'):'dev-verify',
                  ('behavioral_verification','trigger_behavioral_verification'):'dev-verify',('clean_code_change','trigger_clean_code_change'):'clean-code'}
        routes={**REGISTRY['tasks'],**REGISTRY['triggers']}
        sources=REGISTRY['role_sources']['Developer']['target']
        templates=ROOT/'.mt-agent-devkit/distribution/phase2/templates/skills'
        for (route,entry_id),skill in expected.items():
            with self.subTest(entry=entry_id):
                definition=next(x for x in routes[route]['reads'] if x['id']==entry_id)
                target={**definition,**definition.get('layouts',{}).get('target',{})}
                self.assertIs(target.get('enabled',True),True)
                self.assertEqual((target['source'],target['coverage']),(SKILL(skill),{'kind':'full'}))
        # Only pre_pr keeps a target alternative: change-metadata stays internal, so targets read pre-pr-gate once.
        self.assertEqual([e for r,e in expected if 'target' in next(x for x in routes[r]['reads'] if x['id']==e).get('layouts',{})],['trigger_pre_pr'])
        self.assertIs(next(x for x in routes['pre_pr']['reads'] if x['id']=='trigger_pre_pr_gate')['layouts']['target']['enabled'],False)
        # The Dev-only comment notes row is gone; story_comment reads the comment skill in both layouts.
        self.assertEqual([x['id'] for x in routes['story_comment']['reads']],['trigger_story_comment_standard'])
        self.assertFalse([key for key in sources if key.split(' §')[0].endswith(DEV_RETIRED)])
        self.assertNotIn('Developer_Rules',json.dumps(REGISTRY)); self.assertNotIn('Clean_Code_Rules',json.dumps(REGISTRY))
        for entry_id in ('dev_implementation','dev_fix','trigger_clean_code'):
            self.assertNotIn('layouts',next(x for r in routes.values() for x in r['reads'] if x['id']==entry_id))
        self.assertEqual(REGISTRY['common']['Developer']['target'],REGISTRY['common']['Developer']['internal'])
        self.assertEqual(REGISTRY['bootstrap']['Developer']['target'],SKILL('dev-core'))
        self.assertEqual(sources,REGISTRY['role_sources']['Developer']['internal'])
        # Every target skill the Developer can read ships as a Phase 2 template; change-metadata never does.
        shipped={p.parent.name for p in templates.glob('*/SKILL_template.md')}
        for path in [*REGISTRY['common']['Developer']['target'],REGISTRY['bootstrap']['Developer']['target'],*[s for skills in sources.values() for s in skills],*map(SKILL,expected.values())]:
            self.assertIn(path.split('/')[2],shipped,path)
        self.assertNotIn('change-metadata',shipped)


# Point-of-use skills each installed target Developer trigger must add (ST-000310).
TARGET_TRIGGER_SKILLS = {'pre_pr':('pre-pr-gate',),'consultation':('raise-question',),'live_conflict':('raise-question',),'report_blocker':('raise-question',),
                         'document_update':('project-docs',),'technical_doc_divergence':('dev-verify',),'endpoint_change':('dev-verify',),
                         'behavioral_verification':('dev-verify',),'clean_code_change':('clean-code',),'source_review':('clean-code',),
                         'story_comment':('comment',),'retro_required':('retro-contribution',),'tooling_failure':('troubleshooting',),
                         'credential_gate':('credential-gate',),'runtime_handoff':('handoff',),'memory_fact':('agent-memory',),
                         'working_record':('working-record',),'completion':('handoff',)}


# Target TL, QA and UI/UX routes that read the shipped skills since ST-000312, with each trigger's skill.
NON_DEV_SKILL_ROLES = ('Technical_Lead', 'QA', 'UI_UX_Designer')
NON_DEV_TRIGGER_SKILLS = {('Technical_Lead','pre_pr'):('pre-pr-gate',),('Technical_Lead','source_review'):('clean-code',),
                          ('QA','live_conflict'):('raise-question',),('UI_UX_Designer','consultation'):('raise-question',),
                          ('UI_UX_Designer','live_conflict'):('raise-question',)}


class InstalledTests(unittest.TestCase):
    @staticmethod
    def retired_non_developer_sources(reads):
        """Target TL, QA and UI/UX reads that ST-000312 replaced with skills: TL On-Demand §3 and Clean_Code_Rules.md."""
        return sorted(r for r in reads if r[0].endswith('/Clean_Code_Rules.md') or r==('.mt-agent-devkit/rules/Technical_Lead_Rules_Read_On_Demand.md','3'))

    @staticmethod
    def old_developer_sources(sources):
        """Old Developer rules, Common files and the internal-only change-metadata: never read by a target Developer."""
        return [s for s in sources if s.endswith(DEV_RETIRED) or s.startswith('.mt-agent-devkit/rules/Agent_Common_') or '/change-metadata/' in s]

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
                            if role=='Developer':
                                # ST-000310: target Developer manifests resolve to the installed skills.
                                by={x['id']:x['source'] for x in built['reads']}
                                self.assertEqual((by['common'],by['bootstrap']),(SKILL('pre-work'),SKILL('dev-core')))
                                self.assertIn(SKILL({'implementation':'dev-implement','fix':'dev-deliver','peer_review':'pr-review'}[task]),by.values())
                                self.assertEqual(self.old_developer_sources(by.values()),[])
                            if role=='Product_Owner':
                                # ST-000289: target PO manifests resolve to po-core and the installed po-* skills.
                                self.assertEqual(next(x['source'] for x in built['reads'] if x['id']=='bootstrap'),'.mt-agent-devkit/skills/po-core/SKILL.md')
                                self.assertFalse([x['source'] for x in built['reads'] if x['source'].endswith(('Product_Owner_Rules_Bootstrap.md','Product_Owner_Rules_Read_On_Demand.md','Story_Standard_PO.md'))])
                                skills={x['source'].split('/')[2] for x in built['reads'] if x['source'].startswith('.mt-agent-devkit/skills/')}
                                self.assertEqual(skills,{'implementation':{'po-core','po-comment','comment'},'fix':{'po-core','po-comment','comment'},'closure':{'po-core','po-verify-close','po-comment','comment'},
                                                         'scope_question':{'po-core','po-answer-questions','po-comment','comment'},'po_validation':{'po-core','po-validate-ac','po-comment','comment'}}[task])
                                if task in ('closure','po_validation'):
                                    self.assertIn(('.mt-agent-devkit/rules/Story_Standard.md','14'),selected)
                            if task=='qa':
                                authority=(target/'.mt-agent-devkit/rules/QA_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                self.assertIn('read `Story_Standard.md §14`',authority)
                                self.assertIn(('.mt-agent-devkit/rules/Story_Standard.md','14'),selected)
                            if role=='QA' and task in ('implementation','fix'):
                                # ST-000312: the QA rules point to the skills and the route reads them.
                                authority=(target/'.mt-agent-devkit/rules/QA_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                self.assertIn('`raise-question` section 5',authority)
                                self.assertIn(SKILL('pre-pr-gate'),authority)
                                self.assertTrue({(SKILL('pre-pr-gate'),None),(SKILL('raise-question'),None)}<=selected)
                            if role=='Technical_Lead' and task=='review':
                                self.assertIn(SKILL('pr-review'),(target/'.mt-agent-devkit/rules/Technical_Lead_Rules_Bootstrap.md').read_text(encoding='utf-8'))
                                self.assertIn((SKILL('pr-review'),None),selected)
                            if role=='Technical_Lead' and task in ('implementation','fix'):
                                self.assertIn((SKILL('git-workflow'),None),selected)
                            if role=='Business_Analyst' and task in ('implementation','fix'):
                                self.assertIn(SKILL('pre-pr-gate'),(target/'.mt-agent-devkit/rules/Business_Analyst_Rules.md').read_text(encoding='utf-8'))
                                self.assertIn((SKILL('pre-pr-gate'),None),selected)
                            if role in NON_DEV_SKILL_ROLES:
                                self.assertEqual(self.retired_non_developer_sources(selected),[])
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
                                if role=='Developer':
                                    sources=[x['source'] for x in extended['reads']]
                                    self.assertEqual(self.old_developer_sources(sources),[],trigger)
                                    for skill in TARGET_TRIGGER_SKILLS.get(trigger,()): self.assertIn(SKILL(skill),sources,trigger)
                                reads={(x['source'],x['coverage'].get('section')) for x in extended['reads']}
                                if role in NON_DEV_SKILL_ROLES:
                                    # ST-000312: no target TL, QA or UI/UX manifest reads TL On-Demand §3 or Clean_Code_Rules.md.
                                    self.assertEqual(self.retired_non_developer_sources(reads),[],trigger)
                                    for skill in NON_DEV_TRIGGER_SKILLS.get((role,trigger),()): self.assertIn((SKILL(skill),None),reads,trigger)
                                if trigger=='pre_pr' and role=='Technical_Lead':
                                    authority=(target/'.mt-agent-devkit/rules/Technical_Lead_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                    self.assertIn('about to open a PR',authority)
                                    self.assertIn(SKILL('pre-pr-gate'),authority)
                                if trigger=='development_convention':
                                    authority=(target/SKILL('clean-code')).read_text(encoding='utf-8')
                                    self.assertIn('read `docs/wiki/Development_Standards.md`',authority)
                                    self.assertTrue(any(x['source']=='docs/wiki/Development_Standards.md' for x in extended['reads']))
                                if trigger=='clean_code_change':
                                    authority=(target/SKILL('clean-code')).read_text(encoding='utf-8')
                                    self.assertIn('**Clean Code or refactor stories**',authority)
                                    self.assertTrue(any(x['source']==SKILL('clean-code') for x in extended['reads']))
                                if trigger=='source_review' and role=='Technical_Lead':
                                    authority=(target/'.mt-agent-devkit/rules/Technical_Lead_Rules_Bootstrap.md').read_text(encoding='utf-8')
                                    self.assertIn(SKILL('clean-code'),authority)
                                    self.assertNotIn('Clean_Code_Rules.md',authority)


if __name__ == '__main__': unittest.main()
