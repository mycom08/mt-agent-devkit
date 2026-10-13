"""Explicit, fail-closed story read routing; never executes reads or mutations."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / '.mt-agent-devkit/contracts/read-routing.json'
FAMILY = r'^## ([0-9]+[a-z]?\.|Version)'


class Blocked(ValueError):
    pass


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def safe(root, source):
    if not isinstance(source, str) or not source or '\\' in source or ':' in source or any(x in ('', '.', '..') for x in source.split('/')):
        raise Blocked('source requires a canonical confined relative path')
    root = Path(root).resolve()
    path = root / source
    if not path.resolve().is_relative_to(root):
        raise Blocked('source escapes project')
    for part in (path, *path.parents):
        if part == root.parent: break
        if part.exists() and (part.is_symlink() or bool(getattr(part.stat(), 'st_file_attributes', 0) & 0x400)):
            raise Blocked('redirected source: ' + source)
    return path


def covered(root, source, coverage):
    path = safe(root, source)
    if not path.is_file(): raise Blocked('missing source: ' + source)
    data = path.read_bytes()
    if coverage == {'kind': 'full'}: return data
    fact = isinstance(coverage, dict) and set(coverage) == {'kind', 'fact'} and coverage['kind'] == 'fact' and re.fullmatch(r'[1-9][0-9]*', str(coverage['fact']))
    if not fact and (not isinstance(coverage, dict) or set(coverage) != {'kind', 'section'} or coverage['kind'] != 'section' or not re.fullmatch(r'[0-9]+[a-z]?', str(coverage['section']))):
        raise Blocked('invalid section selector: ' + source)
    lines = data.decode('utf-8-sig').splitlines(keepends=True)
    heads = [i for i, line in enumerate(lines) if re.search(r'^### Fact ' if fact else FAMILY, line)]
    selector = r'^### Fact ' + re.escape(str(coverage['fact'])) + r'(?:\s|$)' if fact else r'^## ' + re.escape(str(coverage['section'])) + r'\.'
    matches = [i for i in heads if re.match(selector, lines[i])]
    if len(matches) != 1: raise Blocked('section selector matched ' + str(len(matches)) + ' headings: ' + source)
    start = matches[0]
    end = next((i for i in heads if i > start), len(lines))
    return ''.join(lines[start:end]).encode('utf-8')


def bindings(root, request):
    provider = request.get('provider')
    if provider not in ('claude', 'antigravity', 'codex'): raise Blocked('unknown selected provider')
    actual = request.get('bindings')
    expected = load(safe(root, '.' + provider + '/harness/state-paths.json'))
    if not isinstance(actual, dict) or set(actual) != {'PROVIDER_ROOT', 'RUNTIME_ROOT', 'COMMAND_ROOT'} or actual != expected or actual['PROVIDER_ROOT'] != '.' + provider:
        raise Blocked('missing, unresolved or foreign provider bindings')
    for key, value in actual.items():
        safe(root, value)
        if key != 'PROVIDER_ROOT' and not value.startswith('.' + provider + '/'):
            raise Blocked('foreign ' + key)
    if request.get('layout') not in ('internal', 'target'): raise Blocked('explicit internal/target layout required')
    if request['layout'] == 'internal' and actual['RUNTIME_ROOT'] != '.' + provider + '/agents/working':
        raise Blocked('internal runtime binding mismatch')
    if request['layout'] == 'target':
        receipt = load(safe(root, '.mt-agent-devkit/install-receipt.json'))
        # Bindings are receipt-owned; customized target runtime roots remain valid.
        if receipt.get('providers', {}).get(provider) != actual:
            raise Blocked('target receipt binding mismatch')
    return actual


def context_entries(root, request, task):
    context = request.get('context')
    if not isinstance(context, dict): raise Blocked('bounded story/task context required')
    required = task['context']
    if request.get('session_state') == 'same': required = list(dict.fromkeys(required + ['delta']))
    result = []
    for name in required:
        item = context.get(name)
        if not isinstance(item, dict) or set(item) != {'source', 'coverage', 'reason'} or not isinstance(item['reason'], str) or not item['reason'].strip():
            raise Blocked('missing bounded context requirement: ' + name)
        # Context is an explicit project file, never another provider's state.
        source = item['source']
        for provider in ('claude', 'antigravity', 'codex'):
            if source.startswith('.' + provider + '/') and provider != request['provider']:
                raise Blocked('foreign context: ' + name)
        data = covered(root, source, item['coverage'])
        if not data.strip(): raise Blocked('empty context: ' + name)
        result.append({'id': 'context_' + name, **item, 'after': ['memory']})
    delta = request.get('delta')
    if request.get('session_state') == 'same':
        required_delta = {'findings', 'affected_ac', 'requirements', 'decisions', 'diff', 'reviewed_sha', 'current_sha'}
        if not isinstance(delta, dict) or set(delta) != required_delta or not all(isinstance(v, str) and v.strip() for v in delta.values()):
            raise Blocked('same-session delta fields required; use explicit none when inapplicable')
        for field in ('reviewed_sha', 'current_sha'):
            if delta[field] != 'none' and not re.fullmatch('[0-9a-f]{40}', delta[field]): raise Blocked('invalid ' + field)
        # Values are pointers/identifiers only; actual findings are read from context_delta.
        if any(len(v) > 256 or '\n' in v for v in delta.values()): raise Blocked('delta metadata must be bounded pointers, not raw prompts')
    return result


def routes(root, request, registry):
    allowed = {'provider', 'bindings', 'layout', 'role', 'task', 'stage', 'story', 'session_state', 'session', 'context', 'delta', 'triggers', 'mode'}
    if not isinstance(request, dict) or set(request) - allowed: raise Blocked('invalid request fields; do not store raw prompts')
    bound = bindings(root, request)
    role, task_name = request.get('role'), request.get('task')
    task = registry.get('tasks', {}).get(task_name)
    if not isinstance(task, dict) or role not in task['roles']: raise Blocked('unsupported role/task: ' + str(role) + '/' + str(task_name))
    if request.get('session_state') not in ('fresh', 'expired', 'same'): raise Blocked('invalid session state')
    if not re.fullmatch(r'ST-[0-9]{6}', str(request.get('story', ''))): raise Blocked('canonical story identity required')
    if not isinstance(request.get('stage'), str) or not request['stage'].strip(): raise Blocked('stage required')
    session = request.get('session')
    if session is not None and (not isinstance(session, str) or not session.strip() or len(session) > 256): raise Blocked('invalid session identity')
    mapping = {**bound, 'role': role, 'slug': role.lower(), 'priming': '.mt-agent-devkit/context/Project_Priming_Bootstrap.md' if request['layout'] == 'internal' else '.mt-agent-devkit/context/Project_Priming.md'}
    mapping['bootstrap'] = '.mt-agent-devkit/rules/' + role + ('_Rules.md' if request['layout'] == 'target' and role in ('Business_Analyst', 'UI_UX_Designer') else '_Rules_Bootstrap.md')
    entries = []
    def add(definition):
        item = dict(definition)
        if item.get('roles') and role not in item['roles']: return
        item.pop('roles', None)
        alternatives = item.pop('layouts', {})
        item.update(alternatives.get(request['layout'], {}))
        if item.pop('enabled', True) is False: return
        item['source'] = item['source'].format(**mapping)
        entries.append(item)
    for item in registry['entry']: add(item)
    for item in task['reads']: add(item)
    if task.get('ordinary'):
        for item in registry['ordinary']: add(item)
        for item in registry['roles'][role]: add(item)
        if role in ('Technical_Lead', 'QA'):
            next(x for x in entries if x['id'] == 'bootstrap')['after'] = ['standard']
    entries += context_entries(root, request, task)
    triggers = request.get('triggers', [])
    if not isinstance(triggers, list) or len(set(triggers)) != len(triggers): raise Blocked('triggers must be unique names')
    for trigger in triggers:
        definition = registry['triggers'].get(trigger)
        if definition is None: raise Blocked('unknown observable trigger: ' + str(trigger))
        if definition.get('roles') and role not in definition['roles']: raise Blocked('unsupported trigger for role: ' + trigger)
        if definition.get('layouts') and request['layout'] not in definition['layouts']: raise Blocked('unsupported trigger for layout: ' + trigger)
        if trigger == 'ci_pending' and request.get('mode') != 'github': raise Blocked('CI waiting unavailable in strict mode')
        for item in definition['reads']: add(item)
        if definition.get('context'):
            additions = context_entries(root, request, {'context': definition['context']})
            for item in additions:
                if item['id'] == 'context_delta': continue
                if trigger == 'memory_recall' and (item['source'] != bound['RUNTIME_ROOT'] + '/memory/' + role + '_Memory_Archive.md' or item['coverage'].get('kind') != 'fact'):
                    raise Blocked('memory recall requires exact own archive fact coverage')
                entries.append(item)
    if request.get('mode') not in ('github', 'strict'): raise Blocked('explicit mode required')
    ids = {x['id'] for x in entries}
    if len(ids) != len(entries): raise Blocked('duplicate route entry')
    if 'memory' not in ids: raise Blocked('route missing live memory')
    pending, ordered = list(entries), []
    while pending:
        ready = [x for x in pending if set(x['after']) <= {x['id'] for x in ordered}]
        if not ready: raise Blocked('missing or cyclic ordering prerequisite')
        for item in ready:
            pending.remove(item)
            covered(root, item['source'], item['coverage'])
            item['content_sha256'] = digest(safe(root, item['source']).read_bytes())
            # Unrelated registry edits do not invalidate this read; relevant task/entry edits do.
            item['routing_revision'] = digest({'revision': registry['revision'], 'task': task, 'role': role, 'entry': item, 'layout': request['layout']})
            ordered.append(item)
    return ordered


def receipt_matches(receipt, entry, request):
    expected = {key: entry[key] for key in ('source', 'coverage', 'content_sha256', 'routing_revision')}
    expected.update(provider=request['provider'], session=request.get('session'), returned_coverage='complete', truncation_recovered=True)
    return isinstance(receipt, dict) and all(receipt.get(k) == v for k, v in expected.items()) and bool(request.get('session'))


def build(root, request, receipts=None, registry=None):
    registry = load(REGISTRY) if registry is None else registry
    entries = routes(root, request, registry)
    receipts = receipts if isinstance(receipts, list) else []
    same = request['session_state'] == 'same' and bool(request.get('session'))
    reads, omitted = [], []
    for entry in entries:
        # New story/evidence/delta inputs are always delivered and read.
        can_omit = same and not entry['id'].startswith('context_') and any(receipt_matches(r, entry, request) for r in receipts)
        (omitted if can_omit else reads).append(entry)
    return {'schema_version': 1, 'request': request, 'reads': reads, 'omitted': omitted, 'receipts': receipts,
            'effective_session_state': 'same' if same else ('expired' if request['session_state'] == 'same' else request['session_state'])}


def validate(root, manifest, registry=None):
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1: raise Blocked('manifest schema required')
    expected = build(root, manifest.get('request', {}), manifest.get('receipts'), registry)
    for key in ('reads', 'omitted', 'effective_session_state'):
        if manifest.get(key) != expected[key]: raise Blocked('manifest failed canonical requirement: ' + key)
    return expected


def attest(root, manifest, entry_id, *, returned_complete=False, truncation_recovered=False):
    validate(root, manifest)
    if not returned_complete or not truncation_recovered: raise Blocked('actual complete returned coverage after recovery required')
    request = manifest['request']
    if not request.get('session'): raise Blocked('coverage receipt requires provider/session identity')
    entry = next((x for x in manifest['reads'] if x['id'] == entry_id), None)
    if entry is None: raise Blocked('receipt entry is not a required read')
    return {**{k: entry[k] for k in ('source', 'coverage', 'content_sha256', 'routing_revision')}, 'provider': request['provider'], 'session': request['session'], 'returned_coverage': 'complete', 'truncation_recovered': True}


def extend(root, manifest, triggers, registry=None):
    validate(root, manifest, registry)
    request = dict(manifest['request'])
    request['triggers'] = list(dict.fromkeys(request.get('triggers', []) + triggers))
    return build(root, request, manifest['receipts'], registry)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('build', 'validate', 'inspect', 'extend', 'attest'))
    parser.add_argument('--root', default=str(ROOT))
    parser.add_argument('--input', required=True)
    parser.add_argument('--receipts')
    parser.add_argument('--trigger', action='append', default=[])
    parser.add_argument('--entry')
    parser.add_argument('--returned-complete', action='store_true')
    parser.add_argument('--truncation-recovered', action='store_true')
    args = parser.parse_args()
    try:
        value = load(args.input)
        if args.operation == 'build': result = build(args.root, value, load(args.receipts) if args.receipts else [])
        elif args.operation == 'extend': result = extend(args.root, value, args.trigger)
        elif args.operation == 'attest': result = attest(args.root, value, args.entry, returned_complete=args.returned_complete, truncation_recovered=args.truncation_recovered)
        else:
            result = validate(args.root, value)
            if args.operation == 'inspect': result = {k: result[k] for k in ('reads', 'omitted', 'effective_session_state')}
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print('BLOCKED: ' + str(exc))
        return 2


if __name__ == '__main__': raise SystemExit(main())
