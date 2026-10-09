# ST-000226 PO Closure Read Contract — QA Scenarios

Implementation: b513dc209bdf9a3ad611fb6580e7e230c57c8c8c; provider Codex.

| Case | Expected result |
|---|---|
| AC1 closure happy path | Stage 4 and PO instructions skip reading and writing the Working Record. |
| AC2 bootstrap safety | All six bootstrap sections are mandatory; no closure section-read. |
| AC3 deployment | Internal, Phase 2 templates, bundle and manifest agree; validators pass. |
| AC4 native behavior | Measured Codex fixture closes; unchanged seeded record and zero audited record reads; full bootstrap delivered. |
| Edge ordinary PO session | Own Working Record still updated outside closure; durable closure facts go to Memory. |
| Error invalid provider bindings | Resolver blocks unsupported tools before operational state access. |
| Regression modes | GitHub and strict share closure read contract; init/update regression suites pass. |

Preserved native limitations: unnecessary priming, late binding validation, original truncated presentation corrected by a same-session standalone full bootstrap read, and later early routing-note addition. This is not a fresh clean routing run, real GitHub closure, efficiency benchmark or other-provider certification.

## QA Results

All four acceptance criteria passed against implementation b513dc209bdf9a3ad611fb6580e7e230c57c8c8c.

- AC1: Stage 4, PO role instructions and closure rules consistently skip Working Record reads and writes; ordinary PO sessions retain their record duties.
- AC2: The complete common bootstrap remains mandatory, including safety and provider shell rules; the reduced state sequence never overrides its full read.
- AC3: Internal sources, active Phase 2 templates, generated assets and deployment manifest agree. Template/internal validators, generated-wrapper check and 23 internal tests passed. Historical template sources remain frozen; the existing changes.json snapshot resolves the regenerated manifest.
- AC4: Raw isolated Codex read and command audits corroborate zero Working Record reads, two full bootstrap reads and synthetic fixture closure with all AC checked/status done. The sanitized parent before/after hash assertion supports no record write. Limitations above remain material: no clean fresh routing rerun after the early override pointer, real external closure or other-provider certification.

Independent regression: 94 tests passed in 411.813 seconds; all 10 fixture checks passed. This covers GitHub/strict deployment and sync contracts. Exact implementation-head CI run 37883054582 passed.

Recovery note: the first sandboxed internal suite emitted 19 completed tests then stalled at its subprocess case; it produced no final verdict and was interrupted. A supported elevated verbose retry completed all 23 tests successfully. The aggregate suite was not repeated. Raw logs and runtime state remain provider-local and uncommitted.
