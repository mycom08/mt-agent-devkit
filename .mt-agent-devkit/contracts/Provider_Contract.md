# Internal Provider Contract

This contract applies to this devkit only. Target templates and installation
output retain their existing contract until Phase 2.

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
documented in its existing devkit skill, not verified tools in this Codex session.
The Antigravity manifest intentionally leaves operations unset until the live
runtime supplies a verified mapping. Codex mappings match tools exposed in this
session. Tool identity checks alone never establish behavioral success.

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

Before a workflow starts, pass an explicit provider, run ID, story ID, feature,
phase, adapter path and bindings to every spawned worker. Bind `{RUNTIME_ROOT}`
to `.<provider>/agents/runtime/runs/<run-id>/<story-id>` using validated path
components (`provider_context.runtime_root`). This directory is gitignored.
Pipeline state, telemetry, Working Records, and story retrospectives are owned
by that provider/run/story; do not overwrite another active run. Persist and
pass the state path when resuming; if unavailable, list only this provider's
run state candidates and stop on ambiguity. Never create new state over an
unverified interrupted story.

Bind `{RUN_ROOT}` with `provider_context.run_root(provider, run_id)`. Commands
without a story bind `{COMMAND_ROOT}` with `command_root(provider, run_id,
command)` (`analyst`, `audit-agent-files`, or `build-software`); state/reports
live inside that command's root. Command role agents bind their `{RUNTIME_ROOT}`
to this command root for local records/memory/retro state. Nested Build → Analyst delegates with its own
Analyst command binding and restores the caller's Build binding afterwards.
Resume receives the exact saved provider/run/command identity, never a Claude
singleton path. Legacy command state remains untouched for explicit recovery.

Sprint runs keep `{RUN_ROOT}/tmp/sprint_story_index.json`: provider, run ID,
current story ID and ordered story-ID/root pointers. Use `record_sprint_story`
to append/validate pointers after Story Base Preflight PASS; the index never
duplicates per-story stage/session/loop state. On resume use `sprint_story_roots`
with `resume=True` and load that story's pipeline state. Batch retro processing
uses each indexed story root (`{STORY_RUNTIME_ROOT}`) and its saved state; the
run-level sprint summary is `{RUN_ROOT}/retros/sprint_N_summary.md`. Retain each
story's state until its retro is processed; never use the current story root for
all earlier stories, and never automatically move/delete legacy singleton state.

Before a fresh role read, copy its existing provider-local memory index/archive
to this run's `memory/` if no runtime copy exists; preserve legacy files and
histories byte-for-byte. For durable facts, retain the latest provider-local
runtime memory in `.<provider>/agents/runtime/memory/`, and seed from that before
legacy history. Only the owning role updates its memory/record. Copies are
runtime state, not independent editable harness instructions. Never merge
Claude and Antigravity histories. New Codex memory starts empty and records no
invented provider history. Do not commit any new state or raw transcripts.

`{PROVIDER_ROOT}` resolves to the selected provider's directory. Existing
template references to `.claude/agents/templates/` describe unchanged Phase 2
source/output and are not adapter imports. The operational legacy lifecycle
commands retain their selected provider's output contract and helpers.

Bind `{LIFECYCLE_ROOT}` to `.claude` or `.antigravity`, selecting the existing
target-output provider for init/update/build/sync. For those providers it normally
matches `{PROVIDER_ROOT}`. Codex's internal harness is supported in Phase 1, but
Codex target installation is not: its lifecycle command must require an explicit
Claude/Antigravity target choice and use that provider's existing lifecycle file.
Without that choice, block the lifecycle command; do not construct a nonexistent
`.codex/agents/workflows/` path. This loads lifecycle content, not another adapter.

Before any skeleton generation, render every shared skeleton instruction through
`python .mt-agent-devkit/scripts/render_skeleton.py <source> --lifecycle-root
<LIFECYCLE_ROOT>` and pass that rendered content to the generation agent. This
binds emitted CI filters and target scaffold paths to the chosen legacy target,
including Codex execution with an explicit target choice. Unrendered lifecycle
tokens must never reach generated target files. The target templates/scaffold
functional code are unchanged.

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
