# WF-002 FIX-02 exploratory pilot (2026-09-23)

Status: **local pilot passed; full benchmark and G2/G6 unassessed**. This is one
baseline/candidate pair of four prompted local role sessions, not an installed
devkit orchestrator run. Do not use it to approve or merge FIX-02.

## Frozen inputs and run integrity

- Fixture: `WF-002-business-logic`, canonical content SHA-256
  `26eb3db4264ae84752ac5ad96e8d424a2cd6472efb80e7a24a41008cbfec5d3f`.
- Pilot runner commit: `1fb763d75255ead5a805492ac11ef05b2c1245ff`;
  `VERSION` remained `0.1.50-SNAPSHOT`.
- Compared devkit commits: baseline
  `a30460a87c6d439b1193c45b77cc638a8f237fdb`, candidate
  `e2e700aa2e1014011c07c789458d13501a92f661`.
- Both sides used Claude CLI `2.1.280`, resolved `claude-sonnet-5`, medium effort,
  the same Read/PowerShell/Edit/Write allowlist, Python `3.12.10`, fresh local
  repositories, and a `$0.75` per-stage budget cap. The launch command was
  `python tests/agent-workflows/run_fix02_benchmark.py --max-budget-usd 0.75`;
  the saved run config omitted the cap, a reproducibility defect to fix before
  the full benchmark. Only Common Rule Section 3 varied. The runner does not
  enforce OS-level network isolation.
- Passing pair run ID: `fix02-benchmark-ylmbshwl`. Its exclusive baseline
  report SHA-256 was verified as
  `1a7b8c4b9f3d608f11eee3d0c398f7fa5283f654aeed390a4506cf0429ca8711`.

## Quality and measured pilot signal

Both sides began with the intended one failing test out of six. Both ended with
six passing tests and the exact one-line `pricing.py` fix. Developer test results,
TL diff inspection, and QA test results were observed through matched tool
results; TL and QA approved independently, PO closed, and reviewers made no
product mutations. The harness advanced its own `state.json` between stages.

| Role | Baseline requests / calls | Candidate requests / calls |
|---|---:|---:|
| Developer | 8 / 11 | 5 / 8 |
| Technical Lead | 3 / 7 | 4 / 7 |
| QA | 4 / 6 | 4 / 6 |
| Product Owner | 5 / 7 | 5 / 7 |
| **Total** | **20 / 31** | **18 / 28** |

Elapsed role time was 67,578 ms baseline and 57,640 ms candidate. Cache-read
units were 253,933 and 221,838, respectively. These single-pair changes
(-10% requests, -9.68% tool calls, -14.71% elapsed role time, -12.64%
cache-read) are observations, not a stable savings estimate.
The 10% request reduction is below Phase 6's 20% improvement criterion; this
pilot neither satisfies nor substitutes for that gate.

The canonical FIX-01 transcript collector counted 147 and 160 output tokens,
but Claude's final aggregate usage reported 4,875 and 3,838. Streamed
`message.usage.output_tokens` is therefore incomplete for this CLI format;
do not interpret the collector output-token comparison as actual output usage.
Session-final context counters were unavailable and are not estimated.

Both Product Owners attempted `pytest`, which was unavailable, then passed
`unittest`. Those failed tool attempts remain included in the call counts. Raw
JSONL traces and scratch repositories remain outside Git in the OS temporary
directory; no raw transcript or local absolute artifact path is versioned.

## Invalid first attempt and remaining gate

The first pilot run (`fix02-benchmark-hh11j_tq`) produced a baseline only. Its
final code/tests matched the fixture, but the runner incorrectly required an
exit-code field that successful Claude PowerShell results omit. The PO's raw
response correctly blocked closure because the pilot had not advanced recorded
TL/QA state, but the original parser failed to capture that fenced JSON verdict
(`agent_outcome` was null in the summary). The candidate was skipped; its
immutable baseline-report SHA-256 is
`b922caadb42aaecd24d49f1731622c4b39d3e177fa288af52aafa859a329532a`.
That failure is preserved, not discarded
from the audit trail; the parser and state-transition fixes were committed
before the fresh pair above.

The planned benchmark still needs three comparable repetitions per arm through
the normal installed devkit pipeline, stage telemetry, profile/transition
checks, and all G2/G6 quality gates. PR #209 should remain draft until then.
