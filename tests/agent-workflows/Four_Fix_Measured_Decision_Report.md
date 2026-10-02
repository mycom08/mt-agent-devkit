# Four-fix measured decision report — draft

Date: 2026-10-02. Tracks [#211](https://github.com/mycom08/mt-agent-devkit/issues/211). Decision: **hold FIX-02 optimization acceptance and release; controlled measurement remains pending.** No new Claude run was performed for this report because the account session limit blocks execution.

## Gate status

| Gate/work | Current evidence | Disposition |
|---|---|---|
| FIX-01 telemetry | PR #208 merged; fresh installed stage records retained. PR #216 adds agent-ID transcript discovery and passed CI. | Implementation integrated; fresh full comparable workflow verification still required. |
| FIX-03 drift protection | Integrated via PR #208; static validator and fixtures protect mandatory full-read wording. | Implemented; final cross-fix regression pending. |
| FIX-04 / G4 | PR #212 merged; `evidence/FIX04_G4_Installed_Preflight.md` records installed checks. | G4 passed. |
| FIX-02 / G5 | PR #209 guidance and case runner exist. `evidence/FIX02_G5_Parallel_Tool_Execution.md` on that branch records sequential P01/P02 behavior; P03–P08 passed trace review. #214 owns the failure. | Failed/deferred; new behavior runs and independent verdict required. |
| Installed baseline / G2 | Failed headless attempts, non-comparable interactive diagnostics, and permission/telemetry smoke probes are recorded in `Installed_WF002_G2_Findings.md`. Latest fresh pair stopped at the Claude session limit during baseline init; candidate did not run. | Pending; no accepted controlled baseline. |
| Comparison / G6 | No three comparable baseline/candidate repetitions. | Pending/unassessed. |
| Final regression/release | Offline checks provide preparation evidence only. | Pending; no release decision. |

## Measured facts and their limits

The historical local role-simulation pilot recorded 20 baseline versus 18 candidate requests and 31 versus 28 tool calls. Requests fell 10%, below the plan's 20% target. These are exploratory simulation results, not installed-orchestrator G2/G6 evidence; see `WF002_FIX02_Pilot_Report.md` for usage and quality details.

Saved interactive installed diagnostics yielded 31 baseline versus 43 candidate subagent requests through read-only transcript extraction. They used user approval and non-frozen configuration, had invalid/unavailable written stage rows, and are non-comparable. The counts exclude orchestration and approval time. They establish neither an improvement nor a controlled regression. The historical failed/unavailable rows remain unchanged.

P01/P02 G5 traces show sequential operations despite the guidance, including a retry with the bounded shell fallback available. Correct contents and a prose claim of parallel execution do not satisfy the behavior gate. Offline runner tests validate the oracle, not agent compliance.

Permission, cleanup and telemetry publication probes demonstrate preparation capabilities only. They do not substitute for fresh installed workflow completion, independent review or repeated benchmark measurements. Latest account-limit failure had zero permission denials and produced no comparable baseline.

## Pending comparison table

| Metric | Accepted baseline | Accepted candidate | Decision |
|---|---|---|---|
| Comparable repetitions | 0 | 0 | At least 3 per arm required |
| Requests / tool invocations | unavailable | unavailable | Pending |
| Cache creation/read, input/output tokens | unavailable | unavailable | Pending; separate billing/cache counters |
| Session-final tokens / duration | unavailable | unavailable | Pending; no estimated values |
| Equivalent product quality and safety | unassessed | unassessed | Independent TL/QA evidence required |
| Median / slowest-run result | unavailable | unavailable | Pending |

## Next decision

Offline preparation now includes `installed_benchmark_manifest.json` and the checks documented in `Installed_Benchmark_Contracts.md`. They reject configuration drift, malformed/duplicate stage metrics, uncommitted or unrelated product/changelog changes, and absent/stale/shared-session reviewer evidence. This strengthens preparation only; it does not add any comparable run or advance G2/G5/G6.

Use `WF002_Benchmark_Readiness_Review.md` to freeze the installed comparison configuration and supporting-fix parity. Run a fresh pair after Claude availability returns, resolve G5 under #214, then collect repeated comparable evidence and final regression. Accept an optimization only with equivalent quality/safety and independent TL/QA review; revise or revert FIX-02 if it cannot meet those gates. No projection or savings claim is made here.

This draft has not received independent TL/QA review and does not complete any acceptance criterion that requires measurement, merge or release.
