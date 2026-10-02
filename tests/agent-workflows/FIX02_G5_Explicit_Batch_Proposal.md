# G5 explicit batch experiment — proposal

Date: 2026-10-02. Tracks #214 and draft PR #209. Status: offline prototype only; **G5 remains failed**. No new agent run, independent verdict or production template change.

## Diagnosis

The saved P01/P02 traces establish sequential execution with all inputs known, including a retry exposing the shell fallback. They show no dependency requiring that order. Claude's explanation of its choice was inconsistent with the trace and does not establish an internal cause. Merely repeating the generic parallel instruction has not resolved the observed compliance failure.

## Candidate mechanism

Supply one explicit bounded, read-only dependency group as a shell invocation. The test-only `scripts/test/explicit_read_batch.py` prototype supports exactly P01's three known files and P02's two known file/pattern pairs. It submits all jobs before collecting results, emits stable labelled JSON in declaration order, rejects missing/redirected/invalid inputs, caps each file at 4 KiB, each search at 32 matching lines and the JSON result at 16 KiB. Oversized inputs fail rather than silently omitting required content. It exposes no arbitrary commands, paths, mutations, network or recursive discovery.

This is a concrete example of the existing bounded-shell fallback, not a replacement for native parallel calls and not yet an installed capability. Its fixed-file P02 search validates this fixture's known files only; it does not prove general directory search completeness.

## Offline evidence

The unit suite checks exact contents/labels/matches, no fixture mutations, submit-before-await ordering, missing/oversized/non-UTF-8 inputs, match/output bounds, redirected paths and unsupported operations. Existing P01–P08 oracle tests remain unchanged. No offline outcome counts as agent compliance or G5 acceptance.

```text
python -m unittest scripts.test.test_explicit_read_batch scripts.test.test_parallel_tool_execution_runner -v
```

## Controlled live experiment after availability returns

1. Keep historical failures intact. Freeze CLI/resolved model, guidance SHA, helper SHA, Python version, exact prompts and tools in a new experiment artifact.
2. Copy the helper into a fresh P01/P02 disposable fixture. Supply one literal invocation (`python explicit_read_batch.py P01` or `P02`) and require the agent to use it once, inspect its result and summarize all required content. A native parallel run remains a separate control; do not mix strategies in one artifact.
3. Confirm from persisted traces that exactly one read-only shell call executed and completed successfully. Confirm labelled JSON includes every required value and matches the unchanged fixture. Any extra mutation, missed input, denial, missing result or fabricated summary fails. Outcome remains `needs-review` until manual trace review.
4. Keep P03–P08 prompts, tools and dependency/approval/polling safeguards unchanged; rerun them under the same pinned agent configuration before a G5 verdict.
5. A forced invocation tests tool execution and batching feasibility, not autonomous selection under generic guidance. Independently review that distinction. Only after the experiment works should a TL-reviewed installed-workflow routing proposal be considered. No production helper deployment or template rewrite is authorized by this prototype's existence.
6. Obtain independent TL/QA review of installed behavior and update #214's verdict before claiming FIX-02 works or releasing it. If production guidance changes, refresh #210's source comparison/fingerprints; earlier frozen G2/G6 arms cannot silently absorb the change.

## Remaining work

Wire an explicit experimental strategy into the live case harness with an oracle that inspects the helper command and returned JSON; the current oracle requires filenames/patterns in tool inputs, so the short helper invocation must not be passed off as native P01/P02 evidence. Run fresh agent traces after Claude availability, review the candidate mechanism, and decide whether installed integration is justified. This proposal does not infer that time elapsed or the account limit cleared.
