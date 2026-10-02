# ST-000211 Final Regression Test Scenarios

## Scope and acceptance

Validate FIX-01 telemetry, FIX-03 mandatory-section drift protection, and FIX-04 branch preflight/runtime isolation before integration and release. FIX-02, parallel execution, G2/G5/G6 benchmarking, and efficiency-savings claims belong to story 218 and are excluded.

Source under functional test: `e5de45bd65c5c0048b69c7d28472e076addfc1b8`. An independent reviewer must check the final committed evidence head before sign-off. The scenario author is a GPT QA session; this document does not claim a Claude role-model review.

## Deterministic and deployment scenarios

| Scenario | Input / action | Required result | Evidence |
|---|---|---|---|
| Telemetry happy path | Streamed duplicate requests and a consistent final usage result | Requests deduplicated; final output reconciled; one schema-v1 record per stage; role/stage/model remain separate | `scripts/test/test_telemetry.py` |
| Telemetry errors | Malformed JSON, inconsistent final usage, unsafe metadata, duplicate stage, mixed schema, ambiguous/missing agent ID | Clear rejection without unsafe export or duplicate append | `scripts/test/test_telemetry.py` |
| Telemetry unavailable edge | Harness-only and unavailable sources; partial usage; repeated tool ID in distinct requests | Explicit null/unavailable fields; no estimates or blended runs; session context is not cumulative consumption | `scripts/test/test_telemetry.py` |
| Drift rejection | Mandatory, required, and passive necessary numeric full-read ranges | Exact expected validator errors | `scripts/test/fixtures/bad/inv5_bad_full_read_*.md` |
| Drift exclusions | Negation, separated list/heading boundaries, indented code fence | No false-positive validator errors | `scripts/test/fixtures/good/inv5_full_read_exclusions.md` |
| Branch happy path | Clean synchronized base; inspect followed by create at recorded full SHAs | Exactly the requested branch at the verified base; strict mode needs no remote mutation | `scripts/test/test_branch_preflight.py` B01/B08/B10 |
| Branch errors | Dirty/untracked/ahead/behind/diverged/wrong base, tracked runtime state, SHA drift after inspect | Fail closed; no automatic stash, reset, switch, repair, or new story writes | `scripts/test/test_branch_preflight.py` B02-B07/B09 and drift tests |
| Branch resume edges | Strict sprint setup/resume, interrupted ready story and in-progress routing | Branch created once before status/product write; existing stage resumed; unverifiable state stops | `scripts/test/test_branch_preflight.py` workflow ordering cases |
| Deployment / sync | Fresh GitHub and strict scaffolds; helper mappings and changed-template manifest | Installed canonical scripts; runtime ignored; no product-history leakage; both sync workflows include both helpers; current manifest lists every changed template | Fresh deployment record and `changes.json` |

## Fresh installed functional and cross-fix canary

Use the frozen WF-002 shipping-threshold fixture and a clean disposable strict-mode project. Run the actual installed init and Start Story workflows from the pinned source. Observe the seeded failing test, implementation, independent installed TL/QA stages, PO closure, per-stage telemetry, branch ordering, product diff, and final state. Run the installed collector aggregate and drift fixtures alongside branch/runtime assertions.

Required result: six final fixture tests pass; shipping threshold changes only as allowed; required role gates and closure are observed; runtime remains ignored and outside product commits; collected stages have unique schema-v1 identities and truthful source/availability; aggregate succeeds. Report any missing or failed observation as failed or not verified. A hand-prompted role simulation or helper-only scaffold check does not substitute for installed orchestration.

The final canary evidence document must record source SHA, final evidence SHA, model/configuration, outcome, and limitations. The initial fresh capture completed with product and telemetry observations verified, but mandatory QA scenario/post-pass commit and authoritative stub-scan recovery were omitted. See 	ests/agent-workflows/evidence/ST211_Fresh_Installed_Regression.md; final installed workflow compliance and acceptance remain not verified until controlled recovery and independent review. Historical evidence at `tests/agent-workflows/evidence/FIX01_WF002_Fresh_Installed_Stages.md` and `FIX04_G4_Installed_Preflight.md` establishes earlier limited stage/helper checks only.

## Merge and release gate

Both aggregate regression and the corpus validator must pass. The scenario and fresh evidence must be committed and pushed, then independent reviewers must cover that exact head and its CI. Release verification occurs after approved integration; publishing or release success cannot be inferred from a pre-merge canary.
