# ST-000254 Read Manifest Test Scenarios

Scenario created before independent QA execution on 2026-10-13. Canonical story: issue 254; product revision: 723415f7660651e8188d4791a3c9dd087b3bf899; base: 171a4c9ca8908b0d0a83d5b9911c2eb8522fa4b8.

## Happy Paths

| Scenario | Expected result | AC |
|---|---|---|
| Inspect contract and fresh implementation, peer review, closure, fix examples | Identity, concrete bindings, canonical sources, coverage, reasons and prerequisites present | 1, 10 |
| Walk start story, continue sprint and resume dispatch | Each actual role spawn/resume uses shared build/validate routing; question handoff preserves reduced contract | 2 |
| Fresh/expired workers and reduced tasks | Exact mandatory authoritative sources included; unrelated guidance excluded | 3, 8 |
| Valid same-session receipt | Only successfully returned unchanged coverage omitted; delta and evidence always supplied | 4 |
| Worker read gates | Adapter first; native reader where available; complete reads and truncation recovery before dependents; sequential fallback supported | 5 |
| Observed action trigger | Extend and validate required bounded guidance before action; independent gates preserved | 6 |
| Generated three-provider/two-mode installs | Same helper/registry; rendered sources resolve and deployment/init/update/sync regressions pass | 9 |
| Release metadata | Current unreleased changelog and active distribution metadata record change; VERSION unchanged | 11 |

## Error And Edge Cases

Run scripts.test.test_read_manifest against its authoritative internal-source assertions and real installed-layout assertions. Exercise missing mandatory reads/context, empty inputs, unresolved/foreign bindings/state, missing sources, invalid/ambiguous section and fact selectors, unsupported roles/tasks, insufficient TL question context, fabricated or incomplete receipts, changed content/selector/relevant route, unknown session identity, expired sessions, newly fired triggers, strict-mode CI rejection and unrelated route stability. Expect explicit BLOCKED diagnostics and no dispatch or action authorization (AC3/4/6/7/8).

Read changed active-distribution templates and workflow diffs for placeholder/path/strict-mode consistency; active distribution is Phase 2, legacy target templates remain unchanged. Inspect output privacy and documented failure diagnosis; no savings claim inferred from file bytes (AC9/10).

## Regression Commands

- python scripts/validate_internal_harness.py
- python .mt-agent-devkit/scripts/generate_wrappers.py --check
- python -m unittest scripts.test.test_internal_harness
- python scripts/validate_templates.py
- Full canonical bash scripts/test/run.sh via supported local_verify wrapper; includes read-routing, wait, telemetry, retro, branch and deployment tests plus all validator fixtures.
- Bundle drift, changed Bash syntax and PowerShell parser checks; git diff --check.

## Evidence And Scope

Independent completion evidence is provider-local tmp/ST254_QA_Evidence.json and tmp/waits/local/ST254-qa-aggregate/output.log. Generated six-layout coverage does not certify native Claude or Antigravity execution. Codex worker read/exec/wait operations are observed in this QA session. Native provider execution outside this session is unexercised and is distinct from deterministic layout acceptance.

## Independent Results

All eleven canonical AC PASS at corrected product SHA `21f7d69e8b5c3c6e2253e265c793587052dd9937` on 2026-10-13. The earlier AC9 FAIL at `723415f` is retained in provider-local `tmp/ST254_QA_Evidence.json` and issue 254 comment 6146156230 as superseded history.

- Full canonical aggregate: 182 tests in 409.002 seconds plus 10 fixture checks, true exit 0; run `ST254-qa-recheck1-aggregate`, supported session 78265. Evidence: `tmp/ST254_QA_Recheck1_Evidence.json` and `tmp/waits/local/ST254-qa-recheck1-aggregate/output.log`.
- Internal 23 tests (4.758 seconds), internal/template validators, wrappers and bundle drift (168 assets, 528 entries) PASS; changed Bash/PowerShell syntax and whitespace checks PASS.
- Expiry/completion and delayed-discovery fixtures independently PASS with 40ms persistence latency (two cases, 0.378 seconds); deterministic clock assertions retain poll count, deadline, exact SHA, and no-rerun guards.
- Routing acceptance exercises 21 cases, real internal authorities and six generated provider/mode layouts. Installed init/update/sync behavior is deterministic regression evidence; native Claude/Antigravity execution remains unexercised.

The final QA commit adds this scenario and its Document Index entry only; tested product content remains identical. Refreshed TL approval and exact-head CI are separate merge prerequisites owned by the orchestrator.
