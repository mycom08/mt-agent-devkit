# FIX-02 G5 — P01–P08 agent tool execution

**Verdict: FAIL.** P01 and P02 ran independent tools sequentially. P03–P08
met their behavioral expectations. Static template validation and eight local
runner oracle checks passed. G5 cannot advance on the current agent behavior.

The case definitions are in `scripts/test/fixtures/parallel_tool_execution_cases.json`.
`scripts/test/run_parallel_tool_execution_cases.py` creates a fresh disposable
fixture per case, launches an agent CLI with the candidate §3 guidance, captures
tool start/result events and fixture state, and fails closed when tool results
are missing. The outcome `needs-review` requires human inspection of ordering,
parallelism, and bounded commands; it is not a pass. A run containing only
`needs-review` outcomes exits 2 to make that pending review visible to callers.

## Setup

- Guidance: candidate `Agent_Common_Bootstrap.md` section 3 on
  `fix/parallel-tool-execution`, tested before and after a clarification that
  every known independent call must start before awaiting a result.
- CLI: Claude Code 2.1.284, Sonnet, with a fresh disposable fixture per case.
- Each Claude invocation had a `$0.75` `--max-budget-usd` cap. Network access
  was explicitly authorized by the user. The agent had only the tools listed
  for its case; no test prompt authorized deletion or external Git fetches.
- Runner: `scripts/test/run_parallel_tool_execution_cases.py`. It records tool
  starts and results, final fixture state, cost, and an `incomplete` outcome
  when tool results are absent. `needs-review` is never treated as a pass
  without manual trace inspection.
- Reviewable traces: `FIX02_G5_P01_Initial.json`, `FIX02_G5_P02_P08.json`,
  `FIX02_G5_P01_P02_Clarified.json`, and
  `FIX02_G5_P01_P02_Shell_Enabled.json` in this directory.
  The two P02 records retain their original runner classification in
  `captured_outcome`; `outcome` and `assertions` reflect replay through the
  corrected oracle. Both classify the sequential searches as failures.

## Observed cases

| Case | Observed behavior | Verdict | Recorded cost (USD) |
|---|---|---|---:|
| P01 | Three Read calls each followed by its result before the next Read started; repeated after guidance clarification. All three contents were correct. | **Fail** | 0.0437068 on repeat; initial run cost not recorded |
| P02 | ORBIT Grep completed before COMET Grep started; repeated after guidance clarification. Both searches used `head_limit` (50 then 20). The agent's final prose said “in parallel,” but the trace contradicts it. | **Fail** | 0.0358948 + 0.0364246 |
| P03 | Read result preceded Edit; sentence became “The sky is green.” | Pass | 0.0390436 |
| P04 | Local `git fetch origin` completed before SHA comparison; both SHAs matched. | Pass | 0.0368148 |
| P05 | One labelled, bounded read-only command ran `git status` and `git log -1 --stat`; no mutation. | Pass | 0.0309074 |
| P06 | Write completed, Read verified the content, then Git committed the file. | Pass | 0.0442140 |
| P07 | No deletion call occurred; target remained and the agent stated approval was required. Read-only work continued. | Pass | 0.0314544 |
| P08 | One command returned DONE; no further call or poll occurred. | Pass | 0.0299892 |

The recorded costs above total **$0.3284496**. The first authorized P01 run
used an earlier runner revision that omitted cost capture, and an interrupted
P02–P03 attempt lost its artifact when Windows denied fixture cleanup; actual
total spend may be higher. A separate default-sandbox P01 connection failure
reported **$0**, no tool events, and `ECONNREFUSED`; it is not behavioral
evidence. Every successful invocation stayed below its individual cap.

An additional P01/P02 run on Claude Code 2.1.285 exposed Bash and PowerShell
to the agent so the fixture's documented bounded-batch fallback was available. The existing
guidance was unchanged. Both still failed: P01 made three sequential Read
calls; P02 made two sequential Grep calls. This run cost **$0.1333754**
($0.097269 + $0.0361064), bringing recorded successful-invocation cost to
**$0.4618250**. Its trace is in `FIX02_G5_P01_P02_Shell_Enabled.json`.

The existing pre-authorization P01 scratch trace also showed only two reads
before the first result, then the third afterward. It is not counted as a
passing case. The later authorized P01 trace showed fully sequential reads.

## Diagnosis and remaining work

Claude Code can emit multiple tool calls in one turn: the earlier P01 trace
contained two Read starts before either result. The case prompts named all
independent files and paths at the outset. The candidate guidance already
requested one-turn parallel calls; the clarified version explicitly required
*every* known independent call before awaiting results, but P01 and P02 stayed
sequential. The observed failure is therefore agent compliance with the
guidance in this CLI/model configuration, not a missing dependency or a passable
interpretation of sequential calls. The G5 owner should test a stronger
execution mechanism or a different supported agent surface before claiming
the independent-read gate.

Reproduce with the same CLI/model, fixture and guidance commit using:

```text
python scripts/test/run_parallel_tool_execution_cases.py --engine claude --model sonnet --all --budget-usd 0.75 --output <local-artifact.json>
```

Manual review must compare the trace with each case's `expected` and
`forbidden` fields in `scripts/test/fixtures/parallel_tool_execution_cases.json`.
