# Internal Provider Contract

This contract applies to this devkit only. Target templates and installation
output use the Phase 2 shared distribution and selected provider adapters.

## Selection and discovery

`AGENTS.md` explicitly routes to this contract; `.codex/` is not assumed to load
automatically. `CLAUDE.md` declares Claude, but its declaration still requires
matching enabled capabilities. Inspect the actual enabled tools, then use
`scripts/provider_context.py` with their explicit identities. Load exactly the
returned adapter, never all adapters. A directory, CLI binary, or prose claim is
not runtime evidence. External provider binaries are not invoked by this check.

| Available capability mappings | Declaration | Outcome |
|---|---|---|
| Exactly one complete provider mapping | None | Select that provider |
| Multiple complete mappings | None | Block workflow before state write or spawn |
| Multiple complete mappings | One available provider | Select only declared provider |
| No complete mapping | Any | Block workflow; neutral project priming remains available |
| Complete mapping for another provider | Conflicting provider | Block before state write or spawn |
| Mapping missing spawn, resume, message, or completion | That provider | Block; do not invent tools |

Claude tool aliases come from the baseline. Antigravity aliases are candidates
documented in its existing devkit skill; they require verification in the active runtime.
The Antigravity manifest intentionally leaves operations unset until the live
runtime supplies a verified mapping. Codex mappings must match tools exposed in
the active runtime. Tool identity checks alone never establish behavioral success.

## Execution and handoff

Shared workflow verbs `spawn`, `resume`, `message`, and `complete` mean the
selected adapter's operations. `session_handle` is opaque and provider-qualified.
Record PENDING before a spawn and its returned identity afterwards. Reuse valid
sessions; a missing or expired session requires a fresh spawn with the canonical
role instructions, bootstrap, stage context, reviewed/base/head SHAs, decisions,
and evidence. Do not send a native identity to a different provider.

The shared pipeline retains implementation, independent reviewer, QA, and PO
gates. TL implementation requires Developer peer review. Completion is a bounded
final report with outcome, artifacts, exact SHA, verification and limitations;
end the worker turn after reporting. A status message is not stage completion.
Pending CI blocks advancement, failed CI routes to fixes, and absent checks
follow the existing shared zero-checks gate. Waiting uses the selected runtime's
supported command lifecycle; never assume a background command wakes the agent.

## Path bindings and state ownership

Each provider adapter owns `.<provider>/harness/state-paths.json`. The shared
resolver validates it and returns concrete `PROVIDER_ROOT`, `RUNTIME_ROOT` and
`COMMAND_ROOT` bindings with provider selection. Normal `RUNTIME_ROOT` is
`.<provider>/agents/working`; `COMMAND_ROOT` is `.<provider>/agents`, preserving
existing command tmp/report locations. Run/story IDs identify execution, not a
new storage layout. Do not copy or migrate records or memory into per-run roots.

Before every spawn/resume, pass these concrete bindings plus provider, run ID,
story ID, feature, phase and adapter path. Workers must stop before state access
when a binding is missing, foreign or unresolved. Never recursively search for
another provider/run's record as a substitute. Initialize missing own records
only at the bound provider path; retain existing files and owning-role access.
Reports, retrospectives, memory, archives, Working Records, telemetry, temporary
files and progress remain provider-local with their existing lifecycle. No
histories are merged, moved or deleted. New Codex state starts empty without
invented history. Do not commit new state or raw transcripts.

Sprint workflows retain the provider-local singleton pipeline state and
story-named retrospectives. Verify interrupted story/branch/provider identity
before resuming; ambiguous or concurrent ownership blocks rather than overwrites.
Commands retain their existing provider-local tmp/internal paths. Nested Build
and Analyst use distinct command filenames without rebinding role memory.
`RUN_ROOT` and `STORY_RUNTIME_ROOT`, if used by compatibility callers, resolve to
the same provider working root, not separate story storage. Disposable native
validation fixtures/evidence may use isolated `agents/runtime/runs/` directories;
those test paths are not the default for operational records or durable memory.

`{PROVIDER_ROOT}` resolves to the selected provider's directory. Historical
`.claude/agents/templates/` sources are frozen inputs for compatible released
clients. New target output comes from the isolated shared deployment artifact.

Init/update and the harness stages of build software read
`.mt-agent-devkit/workflows/commands/Target_Project_Deployment_Workflow.md` and
invoke its common Python engine with the selected Claude, Antigravity or Codex
provider. Codex no longer requires a different provider's installation choice.
Do not construct nonexistent provider-local workflow paths. Existing Claude and
Antigravity command surfaces route their installation stages to this shared
workflow while retaining architecture/application generation stages.

`{LIFECYCLE_ROOT}` binds the selected target provider (`.claude`, `.antigravity`
or `.codex`) for application skeleton CI filters. Render skeleton instructions
through `python .mt-agent-devkit/scripts/render_skeleton.py <source>
--lifecycle-root <LIFECYCLE_ROOT>` before generation. Target runtime defaults
remain `<selected-provider>/agents`; internal provider working-state bindings
are separate and must never be copied into target receipts. Native discovery
and execution support remain evidence gated, independently of mechanical
layout generation. No native certification follows from directory names.

## Models, permissions, and telemetry

Shared model policies (`implementation`, `design-review`, `standard`, `closure`)
describe workload; exact native model names/effort belong to the adapter. Runtime
availability and higher-priority user constraints govern selection. Preserve all
safety rules; permission allow-lists never carry across providers. Do not bypass
the sandbox, weaken checks, or invoke paid external runtimes to simulate support.

Collect one sanitized schema-v1 telemetry row per completed stage through
`.mt-agent-devkit/scripts/telemetry.py`. The collector delegates to the unchanged
distributed schema implementation. Adapter-specific extraction is allowed only
for real supported data. Missing usage is explicit unavailable/null; final
context counters are not cumulative usage or a cost proxy. Whole-session
extracts must not double-count resumed stages.
