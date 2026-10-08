# Phase 2 Migration and Implementation Plan

**Story:** ST-000221  
**Author:** Developer  
**Date:** 2026-10-08  
**Status:** TL design approved; refinement complete; story Ready; implementation proof gates not yet executed  
**Inspected base:** `819c295` on `main`, following Phase 1 PR 222

## 1. Intended result and boundaries

Fresh installations and existing target projects receive one authoritative shared harness under `.mt-agent-devkit/`, plus explicitly selected Claude, Antigravity, or Codex adapters and native discovery files. Init, local update, release sync, and build scaffolding use the same file ownership and transformation contract. Project context, custom instructions, root documentation, wiki content, and provider-local runtime history survive migration.

This document specifies proposed migration behavior and an implementation sequence. It does not make `sync devkit` understand migration by itself: distributed workflows, manifests, helpers, compatibility handling, and tests must implement it. All new filenames and schema fields below are proposals for TL review, rather than claims about existing features.

The user requested a Developer-authored draft document during refinement. That authorizes this documentation before TL approval, overriding the ordinary design-first prohibition for this draft only. No templates, scripts, release files, implementation branch, commits, or PR are created by this refinement stage.

Retain Phase 1's Claude rule organization and independent TL/QA gates. Stage-specific profile restructuring, FIX-02 parallel execution, its benchmark, unrelated enhancements, and moving runtime history into per-run folders are excluded. Phase 1 follow-up findings that affect installed behavior must be traced to a fix, explicit dependency, or evidence limitation.

## 2. Current source findings

| Inspected source | Current behavior | Phase 2 consequence |
|---|---|---|
| `.claude/agents/templates/` | Shared, GitHub/strict, rules, instructions, context, scripts and skills sources still emit provider-local harnesses | Inventory each deployed owner and consumer; do not globally replace all provider paths |
| `.claude/agents/workflows/Init_Project_Workflow.md` and `Update_Project_Workflow.md`, Antigravity equivalents | Provider-local command surfaces and hand-maintained deployment lists | Route to a common installation contract while preserving supported command entrypoints |
| `.claude/agents/working/scripts/scaffold_mechanical.sh` | Emits Claude agents and native skills; combines shared workflow blocks with mode appendices | Reuse assembly semantics with manifest-driven mappings |
| `.antigravity/agents/working/scripts/scaffold_mechanical.ps1` | Emits Antigravity paths; workflow loop extracts shared blocks without the Bash mode appendix step | Compare actual generated behavior and make shell outputs obey one oracle |
| Existing scaffold helpers | Write blank memory/records and strict `story_counter.txt`; copy the frozen `version.txt` into the installed stamp | Runtime initialization must be create-if-absent; stamp source release/revision only after successful apply |
| `templates/workflows/Sync_Devkit_Workflow_template.md` | Selects semver release tag; reads historical manifest formats; falls back to full scan for missing versions; updates itself at end; continues after individual failures | Preserve pinning; introduce old-client handoff and transactional completion before marking migration complete |
| Existing update workflow | Merges instruction/root sections, preserves priming/wiki/runtime; old flat instruction migration and legacy tracked-runtime maintenance exist | Retain preservation rules and explicit index-removal authorization; transactional layout migration is additional behavior |
| `.codex/harness/state-paths.json` | Devkit-internal runtime is `.codex/agents/working`, command root `.codex/agents` | Target legacy paths differ; install concrete target bindings without moving histories |
| `scripts/test/test_upgrade_deployment.py` | Narrow deployment fixtures and Phase 1 byte-preservation comparison against `62349287...` | Keep a frozen legacy oracle; replace Phase 1-only parity assertion with explicit legacy/new-layout tests |

The architecture document contains historical inspection statements, including “No `.codex/` harness exists”; these describe the pre-Phase-1 comparison, not the current base. Use the actual base inventory as implementation input.

Selected retained files under `.worktrees/regression-211/tests/agent-workflows/` include installed-contract checks, fixture hashing and independent review evidence requirements. They can inform installed verification after compatibility review. Their benchmark uses frozen historical refs and provider assumptions; it is not a ready-made Phase 2 test oracle. Preserve that worktree unchanged; access-restricted temporary directories need no traversal.

## 3. Deployment ownership and proposed mappings

Keep existing source templates in `.claude/agents/templates/` during this story. Freeze all sources consumed by supported legacy clients, except a compatible sync bridge. Proposed new-layout sources live in an additive distribution namespace, `.mt-agent-devkit/distribution/phase2/`, with a deployment manifest identifying their source and target ownership. This is a concrete artifact proposal requiring the frozen-client isolation gate below: namespace naming alone does not prove safety. Template names retain `_template`; executable helpers retain their extension. New distribution coverage uses additive release metadata ignored by old parsers, rather than placing incompatible assets in their existing `new`/`modified` update sets.

| Legacy/generated content | Proposed target owner | Migration policy |
|---|---|---|
| `<provider>/agents/rules/*.md` | `.mt-agent-devkit/rules/` | Compare managed baseline and custom differences; install accepted shared rules; retire only individually approved managed sources |
| `<provider>/agents/workflows/*.md` | `.mt-agent-devkit/workflows/` | Assemble shared plus selected mode content once; provider wrappers route to shared owner |
| `<provider>/agents/instructions/*_instructions.md`, older flat files | `.mt-agent-devkit/instructions/` | Preserve project adaptations; extract runtime mechanics into selected adapters |
| `<provider>/agents/orchestrator_instructions.md` and supported historical name | `.mt-agent-devkit/instructions/orchestrator_instructions.md` | Verify surviving shared copy and consumers before retiring old managed file |
| `<provider>/agents/context/Project_Priming.md`, `Document_Index.md` | `.mt-agent-devkit/context/` | Preserve project-authored content; propose explicit path edits; differing provider contexts are conflicts |
| Provider-independent scripts such as branch preflight and telemetry | `.mt-agent-devkit/scripts/` | Deploy once; update consumers and runtime bindings |
| Provider adapter, native discovery wrappers, settings/hooks/skills | Selected provider-native paths | Merge project settings; generate marked wrappers from shared source; do not touch another provider's configuration |
| `CLAUDE.md`, `AGENTS.md`, project-level roots | Existing native entrypoint locations | Merge managed sections only; preserve project overview, roster customizations and non-managed sections |
| Memory, working records, retros, reports, tmp, progress/pipeline state, strict stories/counters | Existing provider-local runtime paths | Preserve bytes and location; never reset counters or recursively substitute runtime content |
| `docs/wiki/`, project docs and README | Existing project-owned paths | Preserve existing content; existing append-only guidance remains applicable |
| `<provider>/agents/devkit_version.txt` | Compatibility stamp plus proposed shared install receipt | Update atomically at completion; preserve old-client readable stamp during supported bridge window |

Do not copy the devkit's own provider state bindings verbatim into a target. For each existing provider, bind `RUNTIME_ROOT` to its real preserved legacy state location, normally `<provider>/agents`; new targets may use that same stable convention for consistency. `PROVIDER_ROOT` identifies configuration ownership and `COMMAND_ROOT` identifies native command locations. Fresh Codex target layout and exact discovery locations require TL confirmation against enabled capabilities. Neither an `AGENTS.md` filename nor a provider directory proves native discovery.

Shared documents contain runtime binding variables where state is referenced; native wrappers pass concrete bindings. Adapters remain distinct. Ambiguous/unsupported capability selection blocks workflow starts before state writes or spawning. Neutral repository tasks remain available.

Projects with several providers get one shared version and mode. Adding a provider reuses compatible shared files and initializes only missing state for that provider. If installed providers require different shared versions, modes, contexts, or authoritative rule customizations, report a conflict; do not select the last provider applied as the winner.

## 4. Common installation/update architecture

TL accepts a standard-library Python deployment engine, distributed with the harness, with thin PowerShell/Bash launchers. Preflight the supported interpreter version before any writes and provide an actionable error if absent. Python already powers deployed preflight and telemetry. No second implementation of file lists, rendering, hashing, or transaction logic remains in shell.

The engine supports `inspect`, `plan`, `apply`, `verify`, `resume`, and `rollback` operations. Workflows supply project-specific/adaptive content and decisions explicitly; the engine performs bounded mechanical operations. It must not use an LLM to silently decide custom-content conflicts. Adaptive generation occurs before apply and its reviewed output becomes part of the staged plan.

A release deployment manifest defines a stable logical file ID, source paths, destination owner/path, assembly/substitution method, mode/provider applicability, ownership class, legacy paths, and permitted retirement/migration action. A target install receipt records schema/layout version, exact release/revision, provider bindings, selected mode/providers, source hashes, final rendered managed hashes and per-file ownership. The migration journal is local runtime state outside product commits, under the initiating provider's preserved runtime root; the manifest/receipt schema must distinguish product configuration from private transaction data.

Validate all paths against the resolved target root, reject absolute/parent escapes and unsafe redirected destinations, and inspect case collisions on Windows. Do not broadly scan a target or follow links into unrelated content. Acquire a target-wide migration lock because shared content is common to providers; an interrupted journal requires resume/rollback rather than concurrent apply. Lock metadata identifies the transaction, initiating provider, process identity and journal. A second operation fails while the owner is live; a stale lock never authorizes a fresh apply. Recovery validates owner termination, transaction/journal identity and current file hashes before reclaiming the lock for that same resume/rollback. Ambiguous liveness, corrupt metadata or missing journal blocks automatic reclamation. Record lock release only after verified completion/rollback; do not use elapsed time alone to break a lock.

All command paths call this contract:

1. **Init:** verify provider/mode, collect project adaptations, plan/render in staging, apply, verify, then stamp. Existing installation invokes migration/update planning rather than blind overwrite.
2. **Update project:** use one immutable local source revision with explicit local/snapshot provenance. Do not falsely mark unreleased files as a released tag. Existing published release version remains distinguishable from local source identity.
3. **Sync devkit:** resolve release once, bind the tag to its commit, obtain manifest/helpers/templates from that same revision, plan migration, apply and verify. Failure to fetch any required artifact stops before changes. Historical `changes.json` formats remain readable.
4. **Build software:** every generated repository uses init through the same contract; root and companion/roster repositories each own their settings and transaction. A failure reports incomplete repositories rather than declaring the complete build ready.

Repeat operations compare recorded rendered hashes and inputs and produce an empty write set where unchanged. Project/provider bindings form part of input identity. Source-template checksums alone cannot prove assembled target bytes are current; include mode appendices, transformations, wrapper generation, and adaptive output in the oracle.

## 5. Legacy detection and custom-content decisions

Inspect without modifying. Classify installation as fresh, legacy provider-local, shared current, interrupted transaction, or mixed/unknown. Detect exact legacy paths, entrypoint version/source/mode, installed stamps and provider state. Do not infer an installation solely from a directory name. Unknown version/missing historical change metadata triggers a complete bounded inventory, never an automatic reset.

Build an exact operation list before apply: create, unchanged, managed update, preserve/adapt, conflict, or retire. Record original hashes, proposed destination hashes, reasons and affected consumers. Snapshot every exact path that will change or retire, including entrypoint/config/ignore edits; also verify runtime preservation hashes without publishing runtime contents.

For receipt-backed installations: unchanged managed file may update; local divergence requires three-way comparison using the recorded source/rendered baseline or a conflict. Project-owned files remain preserved. For legacy installs lacking a trustworthy rendered baseline, a version stamp alone does not prove a generic template matches an adapted installed file. Reconstruct a baseline only when inputs are known; otherwise retain local content and request an explicit resolution.

Custom rules must survive in a reviewed shared customization/extension location or approved merged authoritative document, with shared references updated. Keeping a second editable rule copy active is not an acceptable resolution. Unclassified and unexpected files are preserved and reported. Retirement operates only on a manifest-listed exact file after destination verification and consumer rewrites; no recursive provider-directory deletion.

Multi-provider migration compares candidate shared content from all detected providers. Equal content can converge; conflicting project priming, instruction adaptations, or rules need a named resolution. Preserve each provider's historical runtime independently, including strict-mode story files and counters. Mode switching and active-session translation are excluded. Mixed modes or a nonterminal pipeline block apply without resetting state, altering approved branches or replacing sessions. Resume the existing workflow under its original harness and migrate only after terminal state is confirmed.

## 6. Transaction, recovery and rollback

Proposed state machine: `inspected -> planned -> staged -> backed_up -> applying -> verified -> completed`; conflicts remain at planned. `failed` retains journal, staging and backup for recovery. Every stage records actual completed operations and hashes, rather than relying on the version stamp.

Before mutation, render every required target and verify manifest completeness, supported bindings, bounded references and unresolved placeholders. Backup first. Apply individual files using temporary sibling writes and atomic replacement where supported; persist the journal after each operation. A multi-file migration is not globally atomic, so entrypoints switch only after shared destinations and wrappers validate. Deletions follow switch verification. Completion and compatibility version stamps are last.

On interruption, new operations detect the pending transaction. Resume requires unchanged source identity and hashes matching either journaled before or after state; unexpected user edits stop for conflict resolution. Never re-resolve the latest release during resume. Missing backup or corrupt journal blocks automatic continuation and gives actionable paths/status without claiming success.

Failure injection checkpoints cover lock acquisition/reclamation, complete artifact fetch, staged rendering, each backup, journal persistence before/after replacement, each wrapper/entrypoint switch, each retirement, verification, receipt write and compatibility-stamp finalization. For each checkpoint, assert exact before/after file identity, absence of premature certification, successful same-source recovery or actionable refusal, and preserved runtime hashes. A compatibility stamp failure after a verified receipt reports incomplete compatibility finalization and resumes that operation; no old stamp becomes an independent layout certificate.

Rollback restores exact backed-up bytes and file existence, removes only newly created unchanged managed files, restores entrypoint/settings/ignore edits and old receipt/stamps, and verifies originals. If a user changed a file since apply, stop before overwriting it and report the conflict. Preserve journal/backups until successful verification and an explicit retention policy; no automatic cleanup of user/runtime files. Rollback does not rewrite Git history, reset unrelated files, change story status, or invent a branch.

Tracked runtime maintenance keeps its existing separate authorization flow. Ignore updates alone do not untrack files. `--auto` authorizes the documented update plan, never index removal, commit/push, workflow recovery, or custom conflict choices. Existing custom ignore patterns and settings survive; strict mode must cover the newly shared harness and selected native/runtime footprint, while GitHub mode tracks shared configuration and excludes runtime/transaction artifacts. TL/PO must resolve common shared tracking when providers request differing modes.

## 7. Release metadata and old-client bridge

The critical compatibility risk is that an old installed sync workflow uses old hardcoded destinations and replaces its own workflow only at the end. Publishing new-layout templates alone cannot safely migrate that client.

Support released v0.1.48 through v0.1.50 Claude/Antigravity GitHub/strict installations, including flat instructions, missing stamps and customized variants. Allow at most two documented sync invocations without manual reinstall. Older/unknown layouts receive safe inventory and conflicts, without automatic migration certification. Missing stamps in an otherwise recognized supported layout are not grounds to reset it; inspect its content and require explicit baseline/conflict decisions.

The bridge remains at the existing sync source path. Its first invocation may update only legacy-compatible content and the compatible bridge, retains legacy ownership, and reports migration pending. The second invocation explicitly fetches the additive deployment manifest and engine from the same pinned release, preflights Python, and runs the plan/apply contract. Keep compatibility source paths/stamps for the supported range. Only a verified new-layout receipt certifies migration; old stamps remain compatibility hints. Do not assume the running old workflow changes semantics after fetching its own replacement.

Proposed release artifact contract:

| Artifact | Old-client visibility | New-client behavior |
|---|---|---|
| Existing legacy template/helper paths | Frozen legacy-compatible bytes, except compatible sync bridge | Retained for upgrade entrypoints; never authoritative shared owner after verified migration |
| Existing `changes.json` `files`/`new`/`modified` | Contains only legacy-safe entries consumed by old parsers | Existing history remains readable |
| Additive deployment metadata pointing to `.mt-agent-devkit/distribution/phase2/deployment.json` | Must be proven ignored by each supported old parser | Defines complete new-layout assets, mappings, hashes and retirements |
| Distribution namespace templates, adapters and engine | Must be proven absent from every old-client targeted and full-scan write set | Fetched explicitly by bridge/new engine using pinned identity |
| Target receipt | Old client cannot certify it from a stamp | Engine verifies schema, installed hashes, provider bindings and completion |

Freeze the exact old client behavior at released tags, including helper bytes and enumerated source paths. If a client's “all template files” full scan reaches this proposed namespace or an additive metadata field enters its write set, this artifact strategy fails the gate: change payload location/packaging or the bridge handoff design before approval. A preparatory release does not solve direct upgrades that skip it; the final artifact must isolate payloads for direct v0.1.48/v0.1.49/v0.1.50-to-final upgrades.

Validate this bridge by executing frozen old-client fixtures against a release-shaped artifact, not just checking the current workflow text. Some old implementations cannot support a safe transparent bridge; PO must define the minimum supported versions and any explicit documented upgrade step. The result must satisfy the story's update-without-manual-reinstall requirement within that defined range.

**Implementation proof obligation:** an old client consumes the entire latest `changes.json` update set before replacing itself. The agreed isolation design freezes legacy-consumed sources except the compatible bridge and registers new payload through additive ignored metadata. Retaining the old sync path or requesting two invocations alone is insufficient. Frozen-client targeted/full-scan/checksum-skip/helper and direct-upgrade gates must demonstrate isolation during implementation; failing gates stop incompatible release packaging and all legacy retirement. Refinement approves this design and its stop conditions, without claiming those implementation proofs have passed.

Use existing unreleased `changes.json` `new`/`modified` records and descriptions only for legacy-safe changes. Register new-layout distributed additions/modifications/moves in additive deployment metadata and its complete manifest, preserving discoverability without feeding incompatible payloads to old lists. Retain historical formats and release-owned checksum generation; update validators to verify both ownership sets. Old consumers must demonstrably ignore additive metadata. Missing manifest intervals still trigger a full manifest-based scan in the new engine; supported old full scans remain frozen legacy-safe behavior.

Update CHANGELOG under the existing unreleased heading, user migration/rollback guidance, mode/provider documentation, installer inventories and template test strategy. Never hand-edit `VERSION`, release headings or frozen `version.txt`; the release workflow owns stamping. Tests must prove receipt/stamp updates occur only after success.

## 8. Sequenced implementation tasks and review checkpoints

| Task | Work and deliverable | Gate/dependency |
|---|---|---|
| T1 | Full source-to-target inventory at implementation base; freeze released v0.1.48-50 clients/helpers; explicit provider discovery/runtime bindings | Final TL approval; scope decisions below already set |
| T2 | Manifest/receipt/journal schemas, engine CLI and staged rendering prototype; frozen legacy snapshots and failure injection fixtures | TL reviews schema and preservation boundary before installer rewiring |
| T3 | Prototype isolated new-layout templates, selected adapters and marked discovery wrappers; extract provider mechanics | Preserve role authority/tiering and references; prototypes permitted before T5 proof, but no incompatible release packaging or legacy retirement |
| T4 | Implement inspect/plan/stage/apply/verify with baseline/conflict handling, exact backups, resume/rollback and target lock | Deployment and destructive-operation guards proven in disposable fixtures |
| T5 | Implement legacy sync bridge and isolated additive release artifacts; safe version/source stamping | Frozen-client direct skipped-release, targeted/full-scan/checksum-skip/helper proof passes before incompatible release packaging or any legacy retirement; <=2 invocations; verified handoff precedes retirement |
| T6 | Wire Bash/PowerShell helpers and init/update/sync/build to common contract; create-if-absent runtime | Output equality across supported shells/providers/modes |
| T7 | Validate fresh, legacy, multi-provider, repeat, partial-failure and rollback matrix; representative installed native workflows | Independent TL review and QA; unavailable evidence explicitly unverified |
| T8 | Documentation, dual legacy/additive change metadata, compatibility limitations and rollback instructions; implementation PR and evidence links | Normal pre-PR/CI/exact-head review gates; explicit PO acceptance of native evidence gaps after QA |

Use the story's branch preflight and approved immutable base before implementation writes. Draft documentation can move into that branch after refinement; refinement does not start implementation. PO keeps one story with staged checkpoints; split only if refinement reveals independently deliverable scope. Each task has a demonstrated output, not merely a prose checklist. ST-000226/ST-000227 remain separate release dependencies wherever their closure/compliance contradictions or routing affect distributed output; record exact affected consumers and prevent shipping unresolved affected behavior. ST-000228 is required for timing claims; otherwise report unknown unavailable timing boundaries and make no timing claim.

## 9. AC-linked verification matrix

The six core combinations are Claude/Antigravity/Codex × GitHub/strict. Test supported Bash and PowerShell frontends against identical rendered expectations. Mechanical fixture success does not certify native agent execution.

| Case | Observable oracle | AC |
|---|---|---|
| Fresh init in six combinations | Exact manifest-owned file set; one shared authority; right native adapter; no unresolved required tokens; stable runtime bindings | 1, 2, 5 |
| Local update / release sync / build integration | Same logical layout and rendering inputs; local provenance distinct from release; each generated repository covered | 2, 4 |
| v0.1.48/v0.1.49/v0.1.50 direct skipped-release upgrades, flat instructions, missing stamps/custom variants | Frozen Claude/Antigravity clients in both modes complete <=2 documented invocations; project context survives; no incompatible first-pass payload | 2, 3, 7 |
| Old targeted/full-scan/checksum-skip/helper paths | Old parsers ignore additive metadata; complete old write sets exclude new payload; helper behavior remains legacy-safe; bridge is not skipped incorrectly | 3, 4, 7 |
| Missing/unknown stamp or manifest interval | Bounded full scan and actionable conflict; no reset or silent skip | 3, 4 |
| Divergent managed file/custom root/settings/wiki | Conflict/preservation oracle, exact original bytes; approved customization has one shared owner | 3, 4 |
| Existing memory/records/retros/progress/strict counter | Byte hashes unchanged after every operation; histories remain provider-separated | 3 |
| Two and three providers; add one provider | Existing provider adapter/settings/state hashes unchanged; shared mode/version agrees; divergent shared contexts stop | 4, 5 |
| Repeat init/update/sync | Empty unintended write set; stable hashes; no duplicate ignore entries/hooks/wrappers; unchanged counters | 4 |
| Release advances during sync/resume | All artifacts and resumed operations use initial resolved revision; no `/main` payload mixing | 4 |
| Fetch/render/disk/permission failure; kill at each journal step | No premature stamp; journal reports exact partial state; resume verifies; backup exists before every mutation | 3, 4 |
| Rollback with and without intervening user edit | Exact original tree restored or conflict before overwrite; unrelated/runtime files preserved | 3 |
| Path escape, redirected target, case collision, concurrent/stale-lock operations | Stop before mutation; single target lock; live lock blocks; validated stale recovery resumes same transaction; ambiguous owner/corrupt journal blocks | 3, 4 |
| Mixed modes or nonterminal pipeline | Apply blocks; no mode switch, session translation, state reset or branch replacement | 2, 3, 4 |
| Strict/GitHub ignores and legacy tracked runtime | Custom patterns preserved; correct new shared footprint; no automatic index/history changes | 2, 3 |
| Static/templates/wrapper/provider contract and shell parsing | Corpus refs, section routing, metadata coverage and syntax gates pass; installed output checked separately | 1, 5, 6 |
| Native installed representative story, fresh/resume/expired sessions | Correct selected adapter/context, independent TL/QA, pending/failed CI handling and completed handoffs with sanitized evidence | 5, 6 |
| Release artifact/documentation review | Every distributed path discoverable; safe bridge support range documented; release-owned files unmodified manually | 7 |

Run the repository aggregate `bash scripts/test/run.sh` or Windows `powershell -File scripts/test/run.ps1`, plus the required internal harness/template and wrapper checks where the aggregate does not include them. Parse changed PowerShell scripts and run `bash -n` on changed shell scripts. Extend validator scope for shared target output, provider bindings, manifest retirements and wrapper references; do not just allowlist the new paths. Replace only the Phase 1-specific parity requirement, retaining legacy fixture coverage.

Native evidence uses fixed stories and installed artifact hashes, records observed provider capabilities and exact reviewed implementation SHA, and preserves separate implementer/reviewer/QA sessions. Require native installed evidence for every available provider/mode combination; mechanical coverage always includes all six. Missing runtimes are unverified with reason, tracked follow-up and documented support limitation; no provider inherits another provider's certification. QA reports gaps for explicit PO acceptance. The retained benchmark fixture can supply structure without historical model/ref comparisons. No token-saving or benchmark claim belongs to this migration.

## 10. Refinement disposition and remaining approval gate

**TL-1 resolved:** Standard-library Python common engine and thin shell launchers accepted with interpreter preflight. Existing source templates stay in place; new payload isolation is subject to proof.

**TL-2 condition:** Freeze legacy-consumed sources except compatible bridge; use additive ignored metadata and isolated assets. The proposed namespace/artifact plan in section 7 is implementable only after targeted/full-scan/checksum-skip/helper proof. Preparatory release alone is insufficient. Final TL review must approve the plan and its stop condition; implementation evidence must prove it before retirement.

**TL-3 resolved with native evidence gate:** Preserve existing roots; new Codex proposes `PROVIDER_ROOT=.codex`, `RUNTIME_ROOT=.codex/agents`, `COMMAND_ROOT=.codex/agents`, root `AGENTS.md`. Verify native discovery separately before claiming support. One shared mode/version; mixed modes/nonterminal pipelines block.

**TL-4 resolved:** Hash-backed baselines, explicit conflicts, exact backups, journaled resume/rollback and delayed switch/stamps accepted. Sections 4 and 6 now specify lock recovery and fault checkpoints for final review.

**PO-1 resolved:** Released v0.1.48-50 Claude/Antigravity × GitHub/strict, including flat/missing-stamp/custom variants; <=2 documented sync invocations without reinstall and direct skipped-release proof. Older/unknown layouts get safe inventory/conflicts only.

**PO-2 resolved:** Mechanical six-combination coverage; native every available provider/mode; unavailable reason/follow-up/support limitation and QA report for explicit PO acceptance. Separate ST-000226/227 landing dependencies apply where output is affected; ST-000228 applies to timing claims, otherwise unavailable boundaries remain unknown.

**PO-3 resolved:** Distinct local/snapshot provenance; exclude mode switching and active-session translation; no state resets. One story with staged review checkpoints.

Decisions are recorded in [TL refinement review](https://github.com/mycom08/mt-agent-devkit/issues/221#issuecomment-6055016031) and [PO scope review](https://github.com/mycom08/mt-agent-devkit/issues/221#issuecomment-6055068440). TL recorded [**Design approved** on the corrected plan](https://github.com/mycom08/mt-agent-devkit/issues/221#issuecomment-6055162883). Refinement questions are resolved; PO has moved the story to Ready. The normal story-start/preflight gates precede implementation. No proof gate above has yet been executed for Phase 2; design approval does not certify migration behavior.

## 11. References

- [Accepted architecture](Shared_Harness_Provider_Architecture.md)
- [Stage-specific read profiles proposal](../../reviews/Stage_Specific_Read_Profiles_Proposal.md)
- [Agent workflow test strategy](../../Agent_Workflow_Test_Strategy.md)
- [Template test strategy](../../Template_Test_Strategy.md)
- [Story ST-000221](https://github.com/mycom08/mt-agent-devkit/issues/221)


## User-authorized delivery sequencing

Complete and independently review/QA Phase 2 without publishing a release. Execute #226 and #227 as separate followup stories afterward, then ship one combined release after all release/evidence gates pass. This sequencing does not certify unavailable native support or absorb their compliance changes into ST-000221. PO scope disposition: https://github.com/mycom08/mt-agent-devkit/issues/221#issuecomment-6055775095.
