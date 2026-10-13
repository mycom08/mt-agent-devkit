# Explicit Story Read Manifests

## 1. Contract

Every story worker spawn/resume in start story, continue sprint, and resume story
uses `.mt-agent-devkit/scripts/read_manifest.py` and the single canonical
`.mt-agent-devkit/contracts/read-routing.json`. This registry selects existing
authoritative guidance; it neither authorizes mutations nor replaces independent
TL/QA/PO gates. Analyst/build/deployment command workflows are outside this scope.

Schema 1 requests identify role, task, stage, story, provider, concrete bindings,
explicit `internal`/`target` layout, `github`/`strict` mode, session state
(`fresh`, `expired`, `same`), and optional provider-owned opaque session identity.
Bindings must exactly match the selected state-path configuration; target layout
also requires the installed receipt's preserved provider bindings. Do not infer
layout or capability from directory names. The provider capability gate remains
required independently before dispatch.

Entries contain `id`, canonical project-relative `source`, `coverage` (`full`,
or `section` with an exact numbered selector, or `fact` with an exact positive
number selecting a `### Fact N` archive heading), `reason`, ordering prerequisites
`after`, source `content_sha256`, and relevant `routing_revision`. Inspection
contains paths/selectors/digests, never file bodies. Context names identify
explicit existing files containing canonical story/decisions, artifact and
verification references, or bounded question/pause/delta inputs. Use exact
section coverage when the file is broader than the task. No recursive discovery,
cross-provider state, raw credentials, raw sensitive prompts, or external
attachment execution. Snapshot creation still obeys external-content authority
and secret handling; the helper does not fetch GitHub or execute file contents.

## 2. Construction and Consumption

Build before the selected adapter's spawn/resume operation; validate the produced
manifest immediately before dispatch. Pass that manifest and the ordinary task
packet plus Worker Entry Read Contract verbatim. Validation reconstructs all
requirements from canonical routing rather than trusting the supplied list.
Missing mandatory entries/sources, unsupported role/task, empty required context,
invalid/ambiguous sections and foreign/unresolved bindings block with a named
diagnostic. Do not spawn or perform the governed action after BLOCKED.

Workers read the adapter first, then canonical role instruction, then full Common
Bootstrap; subsequent reads follow `after`. Use the native reader directly on
original sources when available; otherwise use only the selected adapter's
sanctioned mechanism. Complete every full-file/exact-section read and recover
truncation before dependent reads, commands, discovery or actions. Batch only
independent entries whose prerequisites have successfully completed, where the
runtime supports it; sequential fallback is valid. A manifest or digest is never
read evidence, and a summary never replaces a required source read.

During work, observable triggers extend the manifest before the governed action.
Call `extend --trigger <name>`, validate and read its additions before proceeding.
The initial set cannot suppress newly applicable safety/verification guidance.
Role routing tables remain authoritative for additional scenarios not yet fired;
resolve and register required bounded reads before action, never silently skip.
Completion and runtime state remain local and uncommitted.

## 3. Resume Coverage and Examples

`attest` records an explicit worker attestation only after actual successful
returned coverage, including any truncation recovery. It requires
`--returned-complete --truncation-recovered`, exact entry and nonempty session;
these flags describe observed tool results, not file accessibility. The helper
cannot independently certify that a native tool returned coverage. Retain the
observed tool-result references in the ordinary local stage evidence. Parent and
worker must not fabricate receipts from hashes or preloaded summaries.

Receipts bind provider/session, canonical resolved relative source, source digest,
full/exact selector, relevant routing revision, and completed/recovered status.
Only matching receipts omit unchanged reads on a valid same-session resume.
Missing/unknown identity follows complete fresh/expired reads. Unknown receipts,
changed sources/selectors/routes or new triggers restore affected reads.
Story/evidence/delta inputs are always supplied and read. Resume delta metadata
contains bounded pointers for findings, affected AC, requirements, decisions,
diff, reviewed SHA and current SHA; explicit `none` means inapplicable.

Examples (all also require common identity/bindings and `context` entries):

| Role / task | Context names | Preserved read behavior |
|---|---|---|
| Developer / implementation, fresh | story, decisions | Full Developer Bootstrap; no broad Story Standard |
| Developer / peer_review, fresh | story, decisions, artifact, verification | Developer Bootstrap plus peer-review sections |
| Product_Owner / closure, expired | story, verification, merge | Common/PO Bootstrap, live memory, acceptance/closure sections; no priming/record |
| Technical_Lead / question, fresh | story, question, pause | Common, live memory, TL comment/question sections; no full TL startup |
| Developer / fix, same | story, decisions, findings, diff, delta | New findings/delta always read; receipts gate every omission |

For each context entry: `{"source":"docs/story.md","coverage":{"kind":"full"},"reason":"canonical story"}`.
Internal Codex bindings are PROVIDER_ROOT `.codex`, RUNTIME_ROOT
`.codex/agents/working`, COMMAND_ROOT `.codex/agents`; installed target bindings
come from its receipt and state configuration. Do not copy internal paths into
a target packet. Use `--root` when the working directory differs.

```text
python .mt-agent-devkit/scripts/read_manifest.py build --input request.json --receipts receipts.json
python .mt-agent-devkit/scripts/read_manifest.py validate --input manifest.json
python .mt-agent-devkit/scripts/read_manifest.py inspect --input manifest.json
python .mt-agent-devkit/scripts/read_manifest.py extend --input manifest.json --trigger local_verify
python .mt-agent-devkit/scripts/read_manifest.py attest --input manifest.json --entry bootstrap --returned-complete --truncation-recovered
```

Persist JSON outputs only at concrete provider-local runtime paths; no raw prompt
or credential fields. Read BLOCKED diagnostics and repair the named input/source,
never broaden reads, discover another provider's state or invent completeness.

## 4. Accepted Completion, Telemetry and Waiting Triggers

The canonical registry registers `completion` (Common Bootstrap detection and
completion contract), `retro_required` (only after a real trigger),
`runtime_handoff`, `telemetry`, `ci_pending` (GitHub only), and `local_verify`.
Telemetry's canonical policy remains Shared Pipeline Stages' telemetry collection
and bounded same-session procedure; this registration does not create a second
usage policy. The orchestrator loads that procedure before collection, records
actual unavailable counters as unavailable, and preserves boundary ownership.
Waiting reads point directly at Wait_Work/Local_Verify contracts: retain the
original command/session identity, exact head, true exits, and independent gates.

Deterministic routing and generated provider/mode layout tests do not certify
native Claude/Antigravity/Codex tool execution. No efficiency savings are claimed;
comparisons require measured comparable runs, not file-byte estimates.

## 5. Role and Action Routing Inventory

Ordinary internal story tasks include Priming §3; reduced TL question and PO
closure contracts retain their exceptions. QA validation and PO acceptance include
Story Standard §14. QA implementer tasks include their §1 and §2 procedures.
Installed BA/UI rules use their unsplit authoritative sources.

Conditional reads remain conditional: `source_review` adds Clean Code for TL or
peer review; `context_anchoring` adds TL unfinished-session §2; `pre_pr` adds
TL implementer §3 (installed startup does not). Installed Developer
`clean_code_change`, `development_convention`, `technical_doc_divergence`,
`endpoint_change`, and `behavioral_verification` follow its Bootstrap triggers.
Commenter, body amendment, document update, consultation/live conflict, acceptance,
UI prototype, and blocker actions add their existing bounded guidance.

`memory_recall` requires `context.memory_match` at the role's own archive path
with `{"kind":"fact","fact":"N"}` coverage; a missing match or full-archive
read blocks. Empty/nonmatching indexes never trigger archive reads.
Runtime tests assert these obligations against internal source text and actual
installed sources across all three providers and both modes, rather than deriving
the complete expected contract from synthetic registry fixtures.
