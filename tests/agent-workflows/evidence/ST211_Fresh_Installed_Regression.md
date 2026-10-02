# ST-000211 fresh installed functional regression

Date: 2026-10-02. Tested source: `e5de45bd65c5c0048b69c7d28472e076addfc1b8`. Scope: FIX-01, FIX-03, and FIX-04. FIX-02 and G2/G5/G6 efficiency acceptance remain excluded and unassessed.

A single fresh disposable strict-mode WF-002 project ran the normal Claude init workflow followed by the installed Start Story orchestrator. Claude CLI was 2.1.287; Python was 3.12.10. Existing frozen fixture and installed-runner tooling came from `test/wf002-controlled-benchmark` at `6ab46c13d390c3141fb41c1aeabea9f3e5a54b54`; this was one functional capture, with no baseline/candidate comparison. Init and Start Story each had a 600-second timeout and USD 4 budget cap. Both returned CLI success, with no timeout, truncation, permission denial, or blocked text. Raw captures remain outside product history; their SHA-256 digests are in the [sanitized summary](ST211_Fresh_Installed_Regression.json).

## Observed outcomes

- Normal installed init completed in 417,047 ms and passed installation checks. Its displayed devkit version was the frozen `0.1.48` bridge value; source identity is the full tested Git SHA above, independently of that display.
- Installed preflight inspected and created the strict sprint branch, then inspected and created the story branch, each pinned to installed scaffold base `c87bcb567e10194b6022e02d4d3a174986fb9aaf` before implementation. The product implementation commit was `9df66d1b365a7bc55cf6d28d90af010560e07382`.
- The final fixture suite ran six tests and passed. The final orchestrator reported that the threshold test failed before implementation. The observed product delta contains exactly `pricing.py` (`>` to `>=`) and the required single changelog bullet. The working tree is clean, no remote exists, and `main` remains at the scaffold base. Runtime state is absent from the product delta.
- The local story is `done`, with all five frozen acceptance criteria complete. Developer, TL, QA, and PO ran as separate installed stages. These fixture role verdicts concern the shipping correction, not approval of this devkit integration PR.
- The installed collector used `extract --agent-id`, with no manual transcript-path extraction. It emitted one schema-v1 record for each stage. All four usage counters are measured; `session_final_tokens` is explicitly unavailable in every record. Records and models are preserved in [stage telemetry](ST211_Fresh_Installed_Telemetry.jsonl).
- The installed collector aggregate succeeded: four records, 26 requests, 79 tool invocations, and 17,704 output tokens. All cumulative usage counters have complete availability. Memory, working records, retro, and telemetry paths are ignored; no file in those runtime directories is tracked in the fixture. See [aggregate output](ST211_Fresh_Installed_Aggregate.json).

| Stage | Observed model | Requests | Tool invocations | Output tokens |
|---|---|---:|---:|---:|
| Developer implementation | `claude-sonnet-5-5` | 9 | 25 | 4,468 |
| TL review | `claude-opus-5-5` | 6 | 24 | 6,413 |
| QA verification | `claude-sonnet-5-5` | 5 | 17 | 2,943 |
| PO closure | `claude-haiku-4-5-20251001` | 6 | 13 | 3,880 |

These are capture facts, not efficiency savings.

## Preserved runner flags and independent review

The original runner summary reports `story_started: false` and `resolved_model_matches: false`, despite successful CLI completion and passing functional assertions. Its session-level model oracle requires every assistant event to use Sonnet; the stream includes the required Opus TL and Haiku PO subagent events. Top-level orchestrator assistant events use only `claude-sonnet-5-5`, and all observed stage models match the declared role families. The original runner, flags, and capture were not edited or rerun. This report separates the reduced-scope functional observations from that benchmark oracle; G2/G6 remain unassessed.

The runner also reports missing independent benchmark review evidence, so `automated_quality_checks_pass` remains false. Independent integration TL/QA review, including source-transcript provenance, remains a separate gate; this implementer does not self-approve it.

A separate GPT QA assessor independently reconciled all four emitted records with the saved source transcripts and confirmed the top-level/subagent model diagnosis. The assessor also identified two observed workflow deviations: the installed fixture QA explicitly skipped the mandatory scenario document and post-pass commit, judging the existing tests sufficient; the Developer attempted the shared workflow under a rules path and substituted a stub scan after that lookup failed. These are preserved limitations, not passes. Final installed workflow compliance is **not verified**, and delivery acceptance remains pending. The capture verifies the stated product and cross-fix observations; it does not establish universal compliance with every installed role procedure. The fixture TL approved the exact implementation SHA, while scenario/acceptance review for this devkit integration remains independent and separate.

The runner captured `working_tree_clean: true` before its independent final six-test execution. That execution subsequently created untracked Python bytecode directories in the disposable fixture. This does not add runtime files to product commits, but the pre-test cleanliness observation must not be presented as a post-run cleanup verdict. The original capture and its timing remain unchanged.

## Deterministic regression on the tested source

- `bash scripts/test/run.sh`: 42 branch-preflight/telemetry tests passed; fixture matrix reports 10 passed and zero failed (nine validator fixture cases plus the unit-test verdict).
- `python scripts/validate_templates.py`: all Layer-1 invariants passed.
- Reused installed-runner self-tests: 23 passed.
- Syntax: three changed shell scripts passed `bash -n` using LF-normalized scratch copies; two changed PowerShell scripts passed parser checks. No tracked shell changes were required for Windows CRLF checkout conversion.
- `git diff --check`: passed. Manifest completeness: all 34 changed distributable templates are listed in `0.1.50-SNAPSHOT`.

Final evidence commit identity is the containing Git commit, to be reviewed independently. Publishing/release verification has not occurred in this capture.
