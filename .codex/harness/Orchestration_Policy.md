# Codex Internal Orchestration Policy

Scope: this devkit's story orchestrator only. Root `AGENTS.md` loads this policy
after verified Codex selection. The shared provider/read-manifest contracts,
task ownership and independent TL/QA/PO gates remain authoritative. This file
and `persist_read_receipts.py` are not target deployment inputs.

## Dispatch and task ownership

Set `fork_turns: "none"` explicitly on every fresh role-worker spawn, including
expired-session replacements. Do not omit it and inherit the default parent
history. A history-inheritance exception requires an explicit user request and
a recorded reason. If the runtime cannot isolate fresh context, report that
capability gap before dispatch rather than claiming bounded context.

Pass a self-contained assignment: owning role and canonical instruction path;
selected provider, adapter and concrete bindings; run/story identity, feature,
phase, stage/task, mode/layout and worktree; canonical story/decision pointers;
base/reviewed/current SHAs as applicable; bounded findings, affected AC, diff and
verification references; validated manifest and verbatim Worker Entry Read
Contract. State missing values explicitly. Required original-source reads still
execute; a packet summary does not replace them. Do not paste parent transcripts,
full logs, other roles' records or unrelated fixture material into the packet.

Use `followup_task` for valid idle workers and deltas for the same live session.
Keep its opaque identity and matching read receipts; check liveness when unknown,
not before every message. A worker status update is not completion. Missing or
expired identities require fresh entry reads and a new bounded spawn.

Route role-addressed requests to their owner. The orchestrator handles stage
transitions, dispatch and gate decisions. Implementers own fixes, fixtures and
self-checks; the assigned validator owns independent validation. An evidence gate
does not authorize extra native workers or orchestrator implementation. Diagnose
failures with the owning worker before another attempt; preserve failed evidence.

## Bounded recovery and evidence reuse

Start interrupted-story recovery at the exact bound singleton checkpoint:
`{RUNTIME_ROOT}/tmp/sprint_pipeline_state.md`. Verify provider, story, stage,
branch/worktree and current SHA before proceeding. Read only referenced evidence;
the resumed worker reads its own required record under the shared access rules.
Missing or conflicting state stops with
the exact mismatch; do not recursively search runtime runs, installed fixtures,
archives or other providers for substitute state. A status request does not
authorize additional validation work.

Keep evidence pointers with their existing handoff/checkpoint, using a compact
entry: evidence kind, owning role, artifact path or URL, full SHA, tested scope,
command/result, observation time and invalidation reason. Record unknown fields
as unknown. Link to canonical evidence instead of copying its contents into
multiple records. Existing evidence without sufficient provenance needs checking;
do not manufacture metadata to make it reusable.

Reuse discovery and completed verification only while SHA, scope, inputs and
relevant environment remain applicable. Code/test changes, changed AC/decisions,
new findings, stale or absent provenance and failed/incomplete results invalidate
the affected evidence. Gate-time exact-head CI, approval-SHA and per-AC checks
still run when required. Developer results can inform QA planning but cannot
replace independent judgment or a mandated aggregate run. Do not rerun an
unchanged suite merely to rediscover a saved result outside those requirements.

## Read receipts without manual manifest edits

After actual successful returned coverage and truncation recovery, use canonical
`read_manifest.py attest` for each completed entry and retain tool-result
references in local stage evidence. Collect those emitted receipt objects into
a JSON array at a bound runtime path. For internal Codex manifests only, use:

```text
python .codex/harness/persist_read_receipts.py --manifest <runtime-manifest.json> --receipts <actual-attestations.json>
```

Read Shell Safety before any receipt/evidence persistence, including preparation
of the input array. Pass canonical project-relative paths within the bound
runtime root. The helper validates the old manifest and incoming receipts,
deduplicates incoming receipts, rebuilds through the canonical router, validates the result
and atomically replaces that manifest. It never performs or certifies reads.
It does not turn a fresh/expired session into a same-session resume. New task
deltas still require the normal build with real session identity and receipts.
Do not append receipts manually to a same-session manifest: the receipt can move
an entry from `reads` to `omitted`, making the old lists invalid.

On BLOCKED, repair only the named path/session/source/coverage problem. After an
approval-review rejection, inspect its reason and the actual returned-read
evidence once; do not repeat unchanged writes or invent completeness. If safe
recovery remains unavailable, report the blocker under the runtime's approval
rules and preserve state. A helper PASS is not native behavioral certification.

## Waiting, reporting and telemetry

Launch each required check once and retain its process/session identity. Resume
that identity using supported waits; batch independent read-only queries and
summarize only the needed log tail/result. Use waits up to 60 seconds or the
runtime's stricter limit, and send progress updates at the required cadence.
Do not poll status or message workers repeatedly while a supported wait is
pending. Report a material finding, blocker, transition or useful check status;
avoid repeating an unchanged plan.

Capture actual worker stage start/end times around dispatch and returned
completion, including each resumed stage. A missed boundary is unavailable, not
a zero-duration stage. Emit the existing required telemetry with unavailable
token counters as null; do not investigate unrelated sessions or estimate quota
savings from text size, final context or elapsed time. Consolidation never skips
required completion, retrospective contributions or independent acceptance.
