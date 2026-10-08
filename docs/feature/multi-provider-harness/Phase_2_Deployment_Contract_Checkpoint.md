# Phase 2 T1/T2 Deployment Contract Checkpoint

**Story:** ST-000221
**Implementation base:** `811c263e8166fb170fc0cb7094d5410a00d33061`
**Branch:** `ST-000221/shared-harness-target-migration`
**Status:** TL schema checkpoint approved; implementation evidence remains independently reviewable

## 1. Exact inventory and limits

[Source and legacy inventory](Phase_2_Source_and_Legacy_Inventory.json) enumerates every tracked template at the implementation base with SHA-256, source path, proposed target, legacy target, ownership, assembly method, modes and literal-path consumer evidence. It also inventories Phase 1 shared/adapter reference inputs and all tracked legacy template, lifecycle workflow and helper files at released v0.1.48, v0.1.49 and v0.1.50. Each release entry records peeled commit, Git blob, byte count and exact byte hash. These are retrieval identities, not results of executing legacy clients.

The inventory has one row per assembly input, not one row per installed file. GitHub/strict and shared workflow variants converge to one mode-selected installed file; root variants converge to the selected entrypoint. Literal consumer evidence deliberately does not claim wildcard references are exhaustive. The following contract consumers cover wildcard assembly and adaptive generation:

Hash representation is explicit: inventory `sha256` hashes immutable Git blob bytes, while `local_checkout_sha256` hashes actual checkout bytes. At this Windows checkpoint CRLF checkout bytes differ from recorded blob bytes; neither representation may be silently substituted for the other. Release fixtures/assets are acquired from immutable Git blobs or an archive preserving those bytes, then validated against blob hashes. Local mode hashes actual selected source bytes and records revision plus changed-input identity; checkout transformations remain part of that local provenance. Receipt/rendered hashes always describe exact installed bytes.

| Consumer | Input/output responsibility | Checkpoint consequence |
|---|---|---|
| Claude/Antigravity `agents/workflows/Init_Project_Workflow.md` | Mechanical scaffold plus adaptive root/context/instructions/rules/wiki | Replace duplicate lists with engine manifest after TL gate |
| Both `Update_Project_Workflow.md` | Local source versions, merge/skip policies, flat-instruction migration | Preserve policy while routing inspect/plan/apply |
| Both `Build_Software_Workflow.md`, shared skeleton/workflow sources | Root project and individual roster repository scaffolding | Each target owns a distinct transaction; do not reuse root runtime state |
| Both `working/scripts/scaffold_mechanical.sh`, Antigravity `.ps1` | Legacy directories, workflow assembly, seed state, settings and ignores | Freeze old-consumed bytes; new shell launchers call common engine |
| Ordinary `Sync_Devkit_Workflow_template.md` | Release resolution, `changes.json`, current hardcoded target mapping | Compatible bridge only; all other legacy sources frozen |
| `Sync_Devkit_Project_Workflow_template.md` | Project-root rule/workflow/helper selection | Distinct project-root scope; compatible bridge may be needed here as well |
| `Project_Root_template.md`, `Project_Root_Priming_template.md`, `Build_Software_Project_Workflow_template.md` | Project-root orchestration | Root-profile assets, not ordinary repo defaults |
| `.github/workflows/release.yml` | Snapshot/release version and change key stamping | Additive deployment metadata must preserve top-level semver-only manifest shape |
| Template/internal validators and aggregate test runners | Reference aliases, manifest coverage, provider routing, legacy preservation | Extend coverage without weakening existing corpus invariants |

Provider-independent workflow assembly must include mode appendices in both shell frontends. Current scripts unconditionally seed memory/records/counters and copy frozen `version.txt`; Phase 2 engine will create missing seeds only and distinguish release from local/snapshot provenance. Target `check_devkit_version` helpers may remain shared code but their hook registration belongs to provider configuration. Read-section native discovery paths are provider-specific; a template's Claude path is not proof of Antigravity or Codex discovery.

**Explicit exclusions:** executable application skeleton generation content remains a reference/generation consumer, not an unconditional installed harness file; standalone wiki/README content is project-owned; old helpers are compatibility fixtures, not new implementation engines; memory/records/retros/tmp/docs/counters/progress are preserved runtime, not distributable replacements. No hidden provider history is an input to the inventory. Inventory Phase 1 sources are reference candidates, not a promise to deploy every internal command or devkit-specific priming file.

The `project_root` profile is a minimal whitelist: `Project_Root_template.md`, `context/Project_Root_Priming_template.md`, `workflows/Build_Software_Project_Workflow_template.md`, `workflows/Sync_Devkit_Project_Workflow_template.md`, and four version/preflight/telemetry helpers. New required dependencies are the common engine, selected adapter, provider contract/resolver, explicit state bindings and root command contract. Any further dependency requires an explicit transitive logical-ID reference and justification; ordinary repo entrypoints, priming, team instructions/rules/workflows/wiki are not automatically installed into the root profile. Root priming historically maps to `{PROVIDER_ROOT}/agents/context/Project_Priming.md`, and its shared destination is `.mt-agent-devkit/context/Project_Priming.md`. Root and repo priming/renderers are profile-exclusive; root entrypoints likewise use only `Project_Root_template.md` rather than assembling ordinary repo root inputs.

## 2. Legacy isolation finding and revised packaging proposal

Old `changes.json` consumers interpret every top-level key as a version or traverse version intervals. Therefore **do not add a non-semver top-level `deployment` key**. Propose an optional field inside the existing release object:

```json
{
  "0.1.51": {
    "new": [],
    "modified": [".claude/agents/templates/workflows/Sync_Devkit_Workflow_template.md"],
    "descriptions": {},
    "deployment": {
      "schema_version": 1,
      "manifest": ".mt-agent-devkit/distribution/phase2/deployment.json"
    }
  }
}
```

The actual version key remains release-workflow-owned; the example is explanatory. Existing legacy parsers explicitly combine only `files`, `new`, and `modified` and read descriptions/checksums. Frozen-client tests must demonstrate unknown object fields are ignored. Distribution assets stay outside `.claude/agents/templates/`, legacy helpers stay unchanged and no new payload enters legacy update lists. Full scan prose says “all template files”; it does not mechanically constrain enumeration. A parser/fixture simulation proves only its chosen enumeration contract, not actual native interpretation; document that gap and require available native evidence.

The release manifest carries assets and mappings, not its own commit hash: hashing a manifest containing its own release commit is circular. Source identity comes from the resolver envelope (tag resolved once to commit); hash downloaded manifest bytes and record that digest in plan/receipt/journal. Every asset has an exact byte hash in the manifest. Fetch by resolved immutable commit where possible and retain the tag as provenance; if using tag URLs verify the tag binding has not changed. Never combine artifacts from `/main` with release identity.

Fixture snapshot location proposal: `scripts/test/fixtures/phase2/legacy/<tag>/` for consumed workflow/parser/helper text and metadata. Retrieve exact blobs from inventory identities; no historical runtime or secrets. Full legacy template trees can be materialized into disposable tests from archived content; tests must not require a mutable remote or assume CI shallow clones contain tags. Final fixture strategy must make required blob content available offline and verify inventory hashes before use.

Bridge pass one may stamp the latest old-readable version while shared-layout migration remains pending. Pass two must check absence/invalidity of the shared receipt **before any old equal-version early return**. Missing stamps need safe recognized-layout inspection and a documented first-invocation version-discovery path; this is proof-required, not solved by guessing a baseline. Checksum skips on the bridge must distinguish truly identical compatible bridge from a stale client; tests must cover both.

## 3. Installed bindings and ownership boundary

| Provider | Provider root | Default target runtime/command root | Entrypoint | Native status |
|---|---|---|---|---|
| Claude | `.claude` | `.claude/agents` | `CLAUDE.md` | Existing target convention; verify installed wrapper/skill/hook behavior |
| Antigravity | `.antigravity` | `.antigravity/agents` | `AGENTS.md` | Runtime API/discovery must be observed, not inferred |
| Codex | `.codex` | `.codex/agents` | `AGENTS.md` | Proposed target convention; verify actual installed discovery separately |

Existing runtime roots override defaults only when explicitly discovered and recorded; never relocate them to internal `agents/working` defaults. Shared provider resolver accepts concrete target state-path bindings, with containment and selected-provider validation. Existing provider roots own histories independently. The shared receipt records selected bindings; wrappers pass them to role starts. Root `AGENTS.md` can serve Codex and Antigravity through explicit capability selection; it must not load both adapters.

Inventory native discovery mappings are candidates until verified in the corresponding provider. `.claude/skills/read-section/` is the concrete legacy Claude convention; generic `{PROVIDER_ROOT}/skills/` substitution does not certify Codex or Antigravity discovery. Those destinations must be explicitly verified and recorded in provider-owned mappings before installed support claims. Native evidence unavailable means unverified support with the approved follow-up/PO acceptance policy, not a borrowed Claude certification.

Ownership classes:

- `managed`: authoritative shared rules/workflows/helpers and generated wrappers; update only against verified rendered baseline or explicit resolution.
- `project_adapted`: role instructions and root managed sections; adapt before staging and record approved bytes/inputs.
- `project_owned`: project priming, document index, wiki/README and unclassified files; preserve existing bytes unless an exact reviewed path edit is supplied.
- `runtime_seed`: memory/record shape and strict counters; create only when absent, then cease product management.
- `provider_config`: selected provider settings/hooks/native wrapper integration; structured merge of named owned keys/sections, preserve unknown configuration.

No retirement of `project_owned`, `runtime_seed` or unknown content. Shared customizations get one reviewed owner; conflicting provider versions/modes/context block. Nonterminal workflows block apply. Tracked-runtime index removal remains separately authorized maintenance; no deployment command commits, pushes or removes index entries.

## 4. Versioned schema proposal

All schemas use `schema_version: 1`, reject unsupported versions before writes and reject unknown fields in safety-sensitive operation/configuration objects. Paths use normalized relative POSIX syntax, with validated on-disk containment and no redirected path components. JSON hashes are SHA-256 of exact bytes except explicit comparison normalization specified by the rendering contract. Persisted schemas require deterministic serialization for plan identity.

### Release deployment manifest

Required root fields: `schema_version`, `layout_version` (`2`), `minimum_python` (proposal `3.10`), `profiles`, `assets`, `files`, `legacy_support`.

`assets[]`: unique `id`, immutable repository-relative `path`, `sha256`, integer `bytes`, `kind` (`template|script|adapter|contract`). Reject duplicate/case-colliding IDs/paths. All file source references must resolve to an asset ID.

`files[]`: stable `id`, `sources` (ordered asset IDs), `destination`, `owner` (`shared|selected_provider|project`), `ownership`, `profiles` (`repo|project_root`), `modes`, `providers`, `renderer`, `legacy_paths`, `phase` (`content|discovery|retirement|certification`), `required` boolean. Renderer is an allowlisted operation (`copy|tokens|shared_mode|managed_sections|approved_adaptation|create_if_absent`), never an arbitrary command. Destination binding variables are only `PROVIDER_ROOT`, `RUNTIME_ROOT`, `COMMAND_ROOT`; unresolved or foreign-provider bindings fail. Runtime placeholders in shared content are intentional contract inputs, distinct from unresolved init project placeholders.

`legacy_support`: allowed released versions/providers/modes, bridge logical IDs, explicit allowed retirements `{logical_id,path,after_verified_ids}`. No directory/wildcard retirement. Sources/final destinations are unique after rendering; several assembly inputs may compose one destination but independent files may not collide.

### Inspect report and approved plan

Inspect report: `schema_version`, target fingerprint, discovered layout/provider/mode/version hints, runtime bindings, tracked-runtime exact paths, nonterminal state findings, pending journal/lock findings, conflicts and preserved file hashes. Sensitive runtime bodies are never included; report stays provider-local.

Plan: `schema_version`, `plan_id` (canonical plan digest excluding itself), target fingerprint, source `{kind:release|local, tag|null, commit, snapshot_version|null, manifest_sha256}`, shared mode/profile, selected provider bindings, exact ordered operations, preservation hashes, resolutions and conflicts. `operations[]` includes stable `operation_id`, logical file ID, relative path, action (`create|replace|retire|preserve`), before existence/hash, staged content hash or null, ownership, phase and dependency IDs. Explicit resolution records identify exact path, chosen approved bytes and reason; `--auto` supplies no resolution. Plans with unresolved conflicts cannot apply. Source identity is fixed for resume.

### Shared install receipt

Installed product configuration path: `.mt-agent-devkit/install-receipt.json`. Fields: `schema_version`, `layout_version`, `source`, shared `mode/profile`, provider bindings, `manifest_sha256`, `managed_files` (`id,path,source_hashes,rendered_sha256,ownership`), approved adaptation inputs or safe digests, and `status:verified`. No raw transcripts, runtime content, private backup path or host-absolute path. Receipt certification is accepted only after validating its structure, bindings and current managed bytes; a forgeable JSON claim alone is not evidence. Avoid a self-hash cycle: receipt excludes its own hash and compatibility stamps from managed content verification.

If future product edits diverge from receipt hashes, inspect reports conflicts; it does not silently recompute a new baseline. Adding a provider expands bindings without replacing another provider's files. Compatibility stamp text is a release hint and never a certificate. Local installs record commit/snapshot identity separately from published tag/version.

### Provider-local transaction journal

Journal: `{RUNTIME_ROOT}/tmp/devkit-migrations/<transaction_id>/journal.json`. Fields: `schema_version`, `transaction_id`, `plan_id`, source/manifest identity, target fingerprint, initiating provider, `state`, ordered operation records, backup identities, preservation hashes, lock identity, failure/checkpoint details and final verification result. Root target-wide lock proposal: `.mt-agent-devkit-migration.lock`; ignore it in both modes. It is transaction runtime, never product history; it does not imply shared-source certification.

States: `planned|staged|backed_up|applying|verified|completed|failed|rolling_back|rolled_back`. Each operation records `pending|backed_up|applied|verified|restored`, original existence/hash, backup byte hash, expected after hash and last persisted checkpoint. Backup filenames are engine-generated IDs within the provider-local transaction directory; revalidate containment and no redirection on every read. Backups may contain project-private content and are never uploaded/committed. Preserve them until verified success and explicit retention cleanup.

Lock metadata: schema, transaction/plan/provider identity, owner PID plus process-start identity where observable, journal relative path and target fingerprint. A live owner blocks; proven terminated owner plus matching valid journal/hash state permits same-transaction recovery. PID reuse/remote-host/unknown liveness blocks automatic reclamation. Do not remove a lock just because its timestamp is old.

## 5. Proposed CLI and completion contract

```text
deployment.py inspect --target PATH --provider PROVIDER [--report PATH]
deployment.py plan --target PATH --manifest PATH --source-commit SHA --source-kind release|local
                   [--source-tag TAG] --mode github|strict --profile repo|project_root
                   --provider PROVIDER [--provider PROVIDER] --bindings FILE
                   [--adaptations FILE] [--resolutions FILE] --output PLAN
deployment.py apply --target PATH --plan PLAN [--auto]
deployment.py verify --target PATH [--receipt PATH]
deployment.py resume --target PATH --transaction ID
deployment.py rollback --target PATH --transaction ID
```

CLI shell launchers forward arguments without interpreting manifests. Engine uses standard library only. `inspect/plan` never mutate installed product content; their requested local output is the only write. `apply` checks interpreter/provider/path/active-state/plan/source/hash preconditions, locks target, stages all bytes and validates all required references before backing up/applying. Entry point discovery switch follows verified content; retirement follows switch; receipt and compatibility finalization are last. Resume/rollback always acquire or validate the same transaction lock. Exit proposals: `0` verified success/no-op, `2` conflict/unsupported/migration pending, `3` incomplete transaction requiring recovery, `1` invalid input or failure before mutation. Report exact remaining actions and never mark pending as success.

No CLI network trust magic: pinned artifact acquisition and tag resolution are a workflow/helper contract whose result the engine validates. Engine reads an explicit local artifact bundle with source envelope and asset hashes. Future remote fetching must obey the same identity and complete-fetch-before-write rule. No arbitrary remote execution or shell interpolation from a manifest.

## 6. Checkpoint decision and next proof gates

**TL decision requested:** approve these concrete manifest/receipt/journal/path/CLI choices and ownership boundary, especially release-object additive metadata, distinct project-root profile, snapshot identity, target-local receipt and provider-local backups/root lock. Confirm Python minimum 3.10 or specify the supported baseline. The proposed namespace and old-client isolation are still implementation proofs, not achieved behavior.

After approval: implement schema/path validation and staged rendering; add deterministic ownership/conflict/runtime preservation fixtures; prove frozen-client targeted/full-scan/checksum/helper/direct upgrades; only then package incompatible release assets or retire any legacy file. Isolated template prototypes are permitted before that proof. No lifecycle installer is rewired at this checkpoint.

Required schema verification includes unsupported versions, unknown operation fields, duplicate IDs/destinations, unsafe bindings/paths, redirected components, source mismatch, absent assets, inconsistent before/after hashes, malformed lock/journal, and baseline divergence. Fault checkpoints and all six provider/mode mechanical deployment combinations remain the approved plan's later gates. Native availability/evidence and separate closure/compliance dependencies are not certified by schema approval.

## 7. Frozen-client finding during implementation

Exact released parser behavior differs from the current parser described above: v0.1.48/v0.1.49 read only `files`, descriptions and checksums; v0.1.50 combines `files`, `new`, and `modified`. A bridge listed only in new/modified is invisible to the older supported clients. Proposed correction awaiting TL decision: include compatible ordinary/root bridge source paths in a legacy `files` alias as well as current metadata; keep all aliases legacy-safe and deduplicate in newer consumers. Additive deployment metadata remains outside these lists. This is a compatibility exception to the normal new/modified-only authoring convention.

Offline deterministic ZIP fixtures preserve exact released blobs. Frozen scaffold helpers execute in both modes/provider surfaces; these scripts do not execute the Markdown sync workflow. The parser-contract fixture is a mechanical oracle of the historical explicit fields, not native sync interpretation. v0.1.48/49 also predate branch-preflight/telemetry helpers; tests must not demand modern files from those historical outputs. Bridge adoption, full-scan scope, missing-stamp entry and <=2-invocation completion remain unproven at this checkpoint.


Final schema checkpoint: https://github.com/mycom08/mt-agent-devkit/issues/221#issuecomment-6055545039. Narrow bridge-only historical `files` alias approved: https://github.com/mycom08/mt-agent-devkit/issues/221#issuecomment-6055742692. Compatibility stamps are final transaction operations after content/runtime verification; the receipt remains sole certification. Native interpretation remains independently evidence gated.
