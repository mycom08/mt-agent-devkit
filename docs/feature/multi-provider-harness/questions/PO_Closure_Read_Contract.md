# PO Closure Read Contract

## Decisions

| Decision | Reason | Rejected Alternative |
|---|---|---|
| Stage 4 PO reads the complete Agent_Common_Bootstrap; skips reading and writing its Working Record. | Safety remains active; closure state already belongs to the issue, pipeline and retrospective. | Section-reading the mandatory bootstrap; conditionally writing a record for durable facts. |
| Durable closure facts belong to Project Memory. | Working Records are current-state snapshots, not durable history. | Writing a record only when a durable fact exists. |

## Constraints

The current deployment source is `.mt-agent-devkit/distribution/phase2/templates/`; its generated bundle and deployment manifest carry the target change. Historical `.claude/agents/templates/` remain frozen except compatible sync bridges. The existing `changes.json` snapshot deployment declaration resolves the regenerated manifest, so legacy file lists/checksums remain unchanged. Internal and distributed instruction wording intentionally differs in provider/mode paths and project context.

## Open Questions

None about the chosen contract. Independent review and QA assess the native observation evidence and final candidate.

## State

ST-000226 implementation aligns internal Stage 4, PO instructions, closure rules and the common lightweight-task exception with their current distribution sources. Static and native evidence are reported separately; a native fixture run does not certify other providers or a real GitHub closure.

## Native observation

[Sanitized native PO evidence](../test-scenarios/ST000226_Native_PO_Evidence.json) records a real separate Codex PO worker closing a frozen synthetic story through a command recorder. It read the full common bootstrap, deliberately neither read nor wrote its seeded Working Record, and completed fixture AC/status/closure/retro actions. The parent independently compared the record hash and audited read events.

The original batched full-file read had truncated tool presentation; a standalone same-session full bootstrap read delivered all six sections. The worker also unnecessarily read priming and validated bindings later than the first audit-state write. These deviations remain in the report. An early closure override pointer was added to PO Pre-Work after that observation; the recorded instruction hash is the earlier candidate, while the bootstrap and closure procedure contract remained unchanged. Usage/cost/timing are unavailable; no savings or native support beyond this bounded Codex case are claimed.
