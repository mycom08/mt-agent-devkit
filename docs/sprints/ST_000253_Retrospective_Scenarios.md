# ST-000253 Exception-Driven Retrospective Scenarios

## Scope and fixture contract

The authoritative trigger policy is Common Bootstrap section 7, available before conditional writing guidance. Fixtures exercise the real retro-completion helper; installed producer/consumer walkthroughs separately verify when agents should load/write. No native provider certification or token-saving estimate is claimed.

The expected manifest is a confined runtime JSON list of actual identities, for example:

```json
[{"provider":"codex","run":"fixture1","story":"ST-000253","stage":"1","role":"Developer"}]
```

Run `python .mt-agent-devkit/scripts/retro_completion.py record --provider codex --runtime-root .codex/agents --run fixture1 --story ST-000253 --stage 1 --role Developer --state clean`, then `check --provider codex --runtime-root .codex/agents --expected tmp/expected.json`. The target fixture must contain that expected JSON at the bound runtime path. A triggered stage first records required plus its trigger kind, loads writing guidance, writes only its role section, then resubmits confined contribution/evidence pointers. Pending required records intentionally block completion.

## Frozen walkthrough inputs and outcomes

| Case | Input | Required behavior and forbidden behavior |
|---|---|---|
| Clean | Successful checks, no lesson or exception | Record clean completion; do not load Common on-demand retro section or Retro_Rules; no retro file, skeleton, role section or no-op entry. Preserve ordinary reports, telemetry and verification. |
| Failure/blocker | Runner cannot connect or external owner/credential blocks work | Record tooling_failure/external_blocker before guidance; require actual populated role contribution and evidence; missing contribution blocks. ST-000215 unverified AC remains unaccepted. |
| Decision ambiguity | Conflicting requirements need a PO/TL decision | Record decision_ambiguity and the reusable decision/lesson with evidence; retain independent authority. |
| Routine first fix | First review correction alone | Clean unless a separate exception occurred. Tooling failure during the first fix still triggers independently. |
| Repeated fixes | Second combined review/QA correction cycle | Record repeated_fix; preserve prior required state on later clean resume. |
| Expected seeded failure | A deliberate negative fixture proves a guard rejects invalid input | Do not mistake the expected result for environment failure; clean if no independent lesson/exception. |
| Explicit request | User requests story/sprint retrospective | Record explicit_request for actual actor/scope, including sprint_retro Orchestrator identity on the last real story; no invented worker or story. |
| Late trigger | Stage previously recorded clean, later resumed work learns a new lesson | Update same identity to required; create only its contribution on demand; subsequent clean/unknown cannot erase required state or history. |
| Zero retros | All actual stages evaluated clean | Helper reports complete/zero source paths; no missing-file read, no placeholder filling or invented summary. Memory pruning and other independent sprint duties still run. |
| Mixed retros | Clean story plus required populated story | Return only required source paths; aggregate actual lessons, preserve source/history and reviewed-source identities. Missing/unknown evaluation blocks. |
| Insufficient file | Retro exists but only another role, pending placeholders or None bullets | Required role is unsubmitted; existing file alone cannot certify contribution. |
| Legacy transition | ST-000253 began before exception-v1 with a pre-created skeleton | Explicit legacy-started state preserves the prior owned sections/history for this already-started run; new runs require exact expected metadata and cannot infer clean from legacy files. |

## Verification evidence

Executable helper fixtures are `scripts/test/test_retro_completion.py`; canonical Bash/PowerShell aggregate runners include them. Tests execute real record/check state transitions and CLI outcomes, provider/path identity rejection, missing/unknown blocking, contribution/evidence validation, sticky required state, deduplication and zero/mixed aggregation. Required negative cases are expected successful tests, not retrospective failure triggers.

Installed guidance walkthrough: apply each row to internal guidance and rendered Claude/Antigravity/Codex GitHub/strict repository layouts. Verify detection remains in full Common Bootstrap, conditional routes precede Retro_Rules reads, new Stage 1 creates no skeleton, actual fast/skipped actors appear in expected identities, Stage 5 checks metadata, and story/sprint consumers preserve historical sources. Inspect unchanged ST-000215 acceptance guards at every route. Independent QA records its own observed result at the reviewed head.
