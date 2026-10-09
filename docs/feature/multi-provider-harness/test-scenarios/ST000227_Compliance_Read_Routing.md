# ST-000227 Compliance Read Routing

## Current verdict

AC1–AC3 retain mechanical implementation evidence. **AC4: NOT VERIFIED for the revised candidate.** Independent QA failed the native run on `44ec4af65e1dc5b2eaaef4e6688ba08151cae047`: required files were exposed through Bash, the sole QA `Read` targeted persisted shell output, and every adapter followed the first shell. See [QA verdict](https://github.com/mycom08/mt-agent-devkit/issues/227#issuecomment-6077397139). The revised ordinary entry contract requires the direct native reader before shell-based discovery/loading. Static checks and this plan cannot satisfy AC4; keep PR240 draft until independent review, a fresh native run and QA acceptance on the revised SHA.

## Routing and deployment contract

Developer, Technical Lead and QA instruction Pre-Work tables explicitly require their role-scoped Story Standard and the selected adapter supplied in the worker packet. Internal and installed adapters resolve to `{PROVIDER_ROOT}/harness/Provider_Adapter.md`; the deployment manifest declares `.claude/harness/Provider_Adapter.md`, `.antigravity/harness/Provider_Adapter.md` and `.codex/harness/Provider_Adapter.md`. The adapter is selected once by verified live capabilities; no worker discovers other providers. The Shared Pipeline explicitly routes a full `.mt-agent-devkit/rules/Retro_Rules.md` read at each stage end.

The active Phase 2 templates intentionally retain installer prefixes and target-project wording; bundle compilation resolves shared paths. Historical `.claude/agents/templates/` are frozen. The current `changes.json` deployment declaration already points to the rebuilt bundle manifest, which contains the new asset hashes; legacy bridge lists and checksums stay unchanged.

## Audit scope and isolation

This is a **native internal role-stage read audit**, not a strict-mode run or a full GitHub pipeline execution. The internal Shared Pipeline has mandatory GitHub preflight, issue, PR and comment operations; it has no strict/local substitute. The audit deliberately replaces those external operations with frozen local inputs and prohibits them. Record that limitation in the result. This fixture proves only the candidate internal Pre-Work and stage-end read routing for fresh Developer, TL and QA workers. It does not certify GitHub orchestration, merge gates, a complete story lifecycle or all native provider behavior.

Use the unmodified candidate `.mt-agent-devkit/instructions/`, rules and `.claude/harness/Provider_Adapter.md` from the exact PR240 head. No installed harness is used as a substitute: the original defect concerned internal workers. The active Phase 2 templates and compiled assets receive the same role-standard/adapter rows and stage-end routing, verified mechanically by bundle checks; this is source/deployment equivalence evidence, not a native installed-runtime claim.

The user has a Claude environment available. Use only that live runtime's verified native capabilities; do not launch a paid external CLI from Codex. First validate actual enabled Claude tool identities through the Provider Contract. A CLI binary or directory alone is insufficient. Pin model/version and record real timing before each spawn; missing usage remains null.

## Exact disposable setup

In the native Claude session, open the devkit checkout, fetch the PR branch and resolve its full SHA. Verify it equals the approved PR240 head supplied by the reviewer. Run the following **Bash** setup there; it creates a separate temporary clone, leaves the operational checkout unchanged and requires no GitHub mutations. `git fetch origin ST-000227/compliance-read-routing` is a read-only prerequisite; use `git rev-parse origin/ST-000227/compliance-read-routing` to obtain the candidate SHA.

```bash
export AUDIT_SHA="$(git rev-parse origin/ST-000227/compliance-read-routing)"
python - <<'PY'
import hashlib, json, os, subprocess, tempfile
from pathlib import Path
source = Path.cwd()
sha = os.environ['AUDIT_SHA']
root = Path(tempfile.mkdtemp(prefix='st227-native-')) / 'repo'
def git(*args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
subprocess.run(['git', 'clone', '--no-hardlinks', '--no-checkout', str(source), str(root)], check=True)
git('config', 'core.autocrlf', 'false')
git('checkout', '--detach', sha)
assert git('rev-parse', 'HEAD') == sha
runtime = root / '.claude/agents/working'
fixture = root / '.native-audit'
(fixture / 'bin').mkdir(parents=True)
(root / '.git/info/exclude').open('a').write('\n.native-audit/\n.claude/agents/working/\n')
(root / 'docs/Fixture.md').write_text('# Old Heading\n\nKeep this sentence.\n', encoding='utf-8', newline='\n')
story = '# ST-900227 — Update a documentation heading\n**Assigned:** Developer\n**Base Branch:** fixture-base\n## User Story\nAs a maintainer, I want the fixture heading corrected so readers see its current name.\n## Acceptance Criteria\n- The first heading of docs/Fixture.md changes from Old Heading to Current Heading.\n- The sentence and trailing newline remain unchanged.\n- No unrelated product file changes.\n## Deliverables\nA local candidate diff, independent review and a QA verdict.\n'
(fixture / 'story.md').write_text(story, encoding='utf-8', newline='\n')
for directory in ('working-record', 'memory', 'retros', 'tmp'):
    (runtime / directory).mkdir(parents=True, exist_ok=True)
for role in ('Developer', 'Technical_Lead', 'QA'):
    (runtime / f'working-record/{role}_Working_Record.md').write_text(f'# {role} Working Record\n\nNo previous stories.\n', encoding='utf-8')
    (runtime / f'memory/{role}_Memory.md').write_text(f'# {role} Memory\n\n## Standing Checks\nNone.\n## Keyword Index\nNone.\n## Troubleshooting Facts\nNone.\n', encoding='utf-8')
    (runtime / f'memory/{role}_Memory_Archive.md').write_text('# Fact Archive\nNo facts.\n', encoding='utf-8')
retro = '# Retrospective — ST-900227\n'
for role in ('Implementer — Developer', 'Reviewer — Technical Lead', 'QA'):
    retro += f'\n## {role}\n### Impediments & Unclear Points\n*(pending)*\n### Process Suggestions\n*(pending)*\n### What Worked Well\n*(pending)*\n'
(runtime / 'retros/ST-900227_retro.md').write_text(retro, encoding='utf-8')
# Fail-closed gh recorder: no operation can reach GitHub through this shim.
shim = '#!/usr/bin/env python\nimport json,sys\nfrom pathlib import Path\np=Path(__file__).resolve().parents[1]/"gh-attempts.jsonl"\nwith p.open("a",encoding="utf-8") as out: out.write(json.dumps({"operation":sys.argv[1:3],"outcome":"blocked"})+"\\n")\nprint("AUDIT: GitHub operation blocked; use supplied local input",file=sys.stderr)\nsys.exit(97)\n'
(fixture / 'bin/gh').write_text(shim, encoding='utf-8', newline='\n')
(fixture / 'bin/gh').chmod(0o755)
# Only the local fixture is committed; candidate harness bytes remain at sha.
git('add', 'docs/Fixture.md')
git('-c', 'user.name=Native Audit', '-c', 'user.email=native-audit@example.invalid', 'commit', '-m', 'test: seed native read fixture')
git('branch', 'fixture-base')
git('checkout', '-b', 'ST-900227/native-read-audit')
paths = ['.mt-agent-devkit/instructions/'+r+'_instructions.md' for r in ('developer','technical_lead','qa')]
paths += ['.mt-agent-devkit/workflows/Shared_Pipeline_Stages.md', '.claude/harness/Provider_Adapter.md']
paths += ['.mt-agent-devkit/rules/Story_Standard_'+r+'.md' for r in ('Dev','TL','QA')]
paths += ['.mt-agent-devkit/rules/Retro_Rules.md', '.mt-agent-devkit/rules/Agent_Common_Bootstrap.md', '.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md']
hashes = {p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths}
(fixture/'setup.json').write_text(json.dumps({'candidate_sha':sha,'fixture_base_sha':git('rev-parse','fixture-base'),'source_hashes':hashes,'seed_sha256':hashlib.sha256((root/'docs/Fixture.md').read_bytes()).hexdigest(),'seed_state_paths':git('diff','--name-only').splitlines()}, indent=2), encoding='utf-8')
print(root)
PY
```

Use the printed audit root as every worker's working directory. Report `setup.json` candidate_sha as the audited harness SHA; fixture_base_sha/worker HEAD includes the separate local seed commit and must not be mislabeled as the candidate SHA. Prepend `<audit-root>/.native-audit/bin` to every worker Bash environment's `PATH`; verify `command -v gh` names that shim before spawning. Fresh role-memory seeds may appear as tracked diffs in this historical internal checkout; `setup.json` records those baseline state paths. Treat them as isolated runtime-state seeds, exclude them from the product diff, and never commit/push them. No shell/network tool may invoke real `gh`, an absolute-path GitHub executable or GitHub API calls. The shim records blocked attempts rather than simulating successful GitHub evidence; any attempt is an audit deviation. Do not put operational credentials, memories or records into this clone. Preserve raw native transcripts outside committed files; do not commit or push the audit clone.

## Ordinary role packets and local substitutions

The runner validates Claude using an enabled-tools JSON file through `provider_context.py --provider claude --tools <file>`. Pass the returned adapter and bindings anchored at the audit root: `PROVIDER_ROOT=.claude`, `RUNTIME_ROOT=.claude/agents/working`, `COMMAND_ROOT=.claude/agents`; run `native-read-227`, story `ST-900227`, Feature `multi-provider-harness`, Phase `follow-up`. Save native worker IDs and real start/end timestamps. No operational pipeline state is resumed or overwritten.

For **every fresh worker**, prepend the candidate-owned Worker Entry Read Contract below to the common and role-specific packets. It is the normal Shared Pipeline fresh-worker contract, not a test-only required-files checklist. Extract it verbatim from the pinned `.mt-agent-devkit/workflows/Shared_Pipeline_Stages.md` before spawning and verify equality with the quoted copy; if they differ, stop for guide refresh. This reaches the worker before its first shell, even when the discovered wrapper merely points at an unread canonical role file.

<!-- WORKER-ENTRY-CONTRACT-START -->
```text
Before any shell command, use the runtime's native file-reading tool when
available (Claude: Read) to read the supplied selected provider adapter first,
then the canonical role instruction, directly from their original paths and
in full. Complete successful returned coverage before proceeding; follow up
truncated reads with that same tool. Shell cat/sed/Python output, persisted
tool-output files and preloaded summaries do not substitute for these reads.
Use the same direct native tool for subsequent mandatory full-file reads
routed by the role. This read gate precedes command batching and discovery.
If no native file-reading tool exists, use the selected provider's supported
file-reading mechanism: a shell read of the supplied adapter itself is the
only preparatory shell exception; read it before any other shell command,
then follow its sanctioned mechanism. Do not invent a Read tool or transfer
another provider's procedure. Missing adapter/bindings or unavailable required
file-reading capability blocks before other commands or state access.
```
<!-- WORKER-ENTRY-CONTRACT-END -->

Then send this common packet, followed by its role-specific packet:

```text
Work only in the supplied disposable audit root. Provider Claude; adapter
.claude/harness/Provider_Adapter.md; PROVIDER_ROOT=.claude;
RUNTIME_ROOT=.claude/agents/working; COMMAND_ROOT=.claude/agents.
Run native-read-227; story ST-900227; Feature multi-provider-harness;
Phase follow-up. Follow your canonical role instruction's normal mandatory
Pre-Work. Frozen issue body is .native-audit/story.md; there are no comments.
This user-authorized internal role-stage audit substitutes that local body
for GitHub reads, local diff/verdicts for PR/check/comment evidence, and the
already-created branch for branch creation/preflight. Do not invoke GitHub,
change status/AC, create a PR, commit, push, merge or release. These explicit
isolation substitutions override those external operations only; mandatory
internal instruction/rule reads and owning-role state remain unchanged.
Use the fail-closed gh shim supplied by the runner. Report deviations.
```

| Worker | Fresh role-specific packet | Stage-end instruction from candidate pipeline |
|---|---|---|
| Developer | Load `.mt-agent-devkit/instructions/developer_instructions.md`. Stage 1 implementation: change only the fixture heading to Current Heading; verify the frozen AC and return the local diff and final SHA. | Append the exact Stage 1 step 10 text from the pinned Shared Pipeline, substituting story ST-900227 and bound runtime. |
| TL | Load `.mt-agent-devkit/instructions/technical_lead_instructions.md`. Stage 2 reviewer: independently review the frozen local story and Developer diff; use the normal review-trigger section routed by your role rules. Return a local approval or findings with the inspected SHA; no GitHub approval/check claim. | Append the exact Stage 2 step 5 text from the pinned Shared Pipeline, substituting story and runtime. |
| QA | Load `.mt-agent-devkit/instructions/qa_instructions.md`. Stage 3 validator: independently inspect the frozen story, local diff and TL verdict, and validate the three AC. Treat status:testing and linked local candidate as supplied stage context. Write any scenario/evidence only under bound runtime/tmp; return local results without AC ticks. | Append the exact Stage 3 automation-pass retrospective sentence from the pinned Shared Pipeline, substituting story and runtime; no merge clause. |

Run the three fresh workers sequentially. After Developer completes, save `git diff -- docs/Fixture.md` and changed-path list under `.native-audit/`; give TL those files and the fixture base/head SHAs. Give QA the same candidate evidence and TL's verdict. Required lifecycle verification and GitHub CI gates are **out of scope**, explicitly replaced by local candidate evidence; do not claim a full Stage 1–3 pipeline PASS. The runner must extract stage-end text from the pinned source; it must not add a checklist enumerating desired compliance files or pre-read them into worker context. This tests whether the ordinary canonical role routing causes the workers' own native `Read` calls.

## Pasteable native Claude kickoff

```text
Run the native internal role-stage audit defined in
 docs/feature/multi-provider-harness/test-scenarios/ST000227_Compliance_Read_Routing.md
for the reviewer-approved PR240 head. Read the audit scope/setup/packets first.
Verify actual enabled native Claude capabilities via the Provider Contract;
stop if unavailable. Fetch the story branch read-only and pin the full SHA,
then execute the documented disposable setup. Do not start the production
workflow or use strict mode. Use the isolated fail-closed gh recorder and
explicit local substitutions; no GitHub mutations, commits/pushes by workers,
merge, release or acceptance-checkbox edits. Spawn fresh Developer, TL and QA
workers sequentially using the candidate-owned Worker Entry Read Contract
verbatim plus the documented ordinary packets and candidate
stage-end instructions. Capture each worker's actual native Read requests and
returned coverage, native IDs, timings and available usage. Audit positive and
negative read assertions and fixture outcomes. Preserve raw evidence locally;
return a sanitized evidence table for the exact candidate SHA, deviations and
paths to local transcripts. Do not mark ST-000227 AC4 passed yourself; independent
QA must inspect those transcripts and decide acceptance.
```

## Native execution and transcript audit

1. Start fresh native Developer, TL and QA workers at their respective stages. Capture each worker's actual native `Read` tool requests and returned content, not just orchestrator messages or statements in final reports.
2. Verify successful full reads of `.mt-agent-devkit/rules/Story_Standard_Dev.md`, `Story_Standard_TL.md` or `Story_Standard_QA.md` for the owning role; `.claude/harness/Provider_Adapter.md` before its first shell command; and `.mt-agent-devkit/rules/Retro_Rules.md` before its stage report. Bounded reads must collectively cover the whole required file without truncation; an attempted path or partial response is insufficient.
3. Record per worker the native session identity, stage, exact path, `Read` event identifiers, covered line/byte ranges, file character count, actual available token usage and observed duration. Missing usage remains null. Count read events and covered characters separately from token billing; never infer tokens from characters. Report required and forbidden read results, task result and deviations.
4. Verify the exact heading change and independent review/QA outcomes, no unauthorized mutations, and all three complete read sets. Keep raw transcripts in a gitignored evidence directory; publish only sanitized summaries and stable event pointers. Do not include home paths, credentials or raw sensitive prompts.
5. Independent QA must audit the raw worker transcripts and attach the sanitized evidence to the PR/issue for the exact candidate SHA. Any missing native worker, omitted/partial mandatory file, wrong provider, or absent transcript keeps AC4 pending. Product changes after the audited SHA require a scoped evidence refresh.

## Required evidence handoff

| Worker | Role Standard | Adapter | Full Retro Rules | Current evidence |
|---|---|---|---|---|
| Developer | Story_Standard_Dev.md | .claude/harness/Provider_Adapter.md | .mt-agent-devkit/rules/Retro_Rules.md | Pending fresh rerun; previous SHA failed |
| Technical Lead | Story_Standard_TL.md | .claude/harness/Provider_Adapter.md | .mt-agent-devkit/rules/Retro_Rules.md | Pending fresh rerun; previous SHA failed |
| QA | Story_Standard_QA.md | .claude/harness/Provider_Adapter.md | .mt-agent-devkit/rules/Retro_Rules.md | Pending fresh rerun; previous SHA failed |

The previous failed run remains immutable evidence; do not reuse its worker sessions. The native operator supplies the revised pinned setup, all eleven source hashes, exact entry-contract equality result, successful `Read` coverage/events, timing/usage availability, final product diff, verdicts and deviations. Independent QA records PASS or explicit failures per row and decides AC4. No acceptance checkbox is changed by the implementer.
