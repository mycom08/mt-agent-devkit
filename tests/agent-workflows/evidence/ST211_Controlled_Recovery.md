# ST-000211 controlled installed recovery

Date: 2026-10-02. Tested devkit source remains `e5de45bd65c5c0048b69c7d28472e076addfc1b8`. The [initial capture](ST211_Fresh_Installed_Regression.md), its original runner flags, and raw streams were preserved. This separate corrective capture resumed the actual installed orchestrator once, using the same tools and restricted permission policy, a USD 4 cap, and a 600-second timeout. It completed successfully in 405,922 ms with no permission denial, timeout, truncation, or blocked text. No templates were changed to obtain a pass.

## Corrective result

The Developer reread the authoritative `.claude/agents/workflows/Shared_Pipeline_Stages.md` check and ran it: zero stub markers; the legitimate shipping threshold `return 0` branch was reviewed rather than treated as a stub. Installed branch preflight passed before corrective product writes, at base `cf88cf584bf44b696ab04d79ecfa40c299323812`.

Fresh QA authored and committed the required scenario document and executable scenario script at product commit `22f98258262bdff720c87643b6e0bf589d6780a1`. Fresh Opus TL then approved that exact commit; fresh Sonnet QA verified the same commit, running all six original tests, all seven scenario tests, and threshold boundary checks. Fresh Haiku PO closed only after those gates. The corrective artifacts merged into `sprint-1-dev` as `e61e1a4a7ef908023988fb392d55e3fb0cf2100e`.

The final allowed fixture delta contains exactly:

- `pricing.py` and the original required `CHANGELOG.md` bullet;
- `docs/feature/ST-000211/test-scenarios/ST-000211_Test_Scenarios.md`;
- `tests/feature/ST-000211/scripts/test_st_000211_scenarios.py`.

The actual [scenario document](ST211_Recovery_Scenario.md) and [scenario script](ST211_Recovery_Script.py) are copied byte-for-byte for review; their original fixture paths and SHA-256 hashes are in the [assessment](ST211_Recovery_Assessment.json). These copies are evidence, not tests intended to run from the devkit repository.

An independent GPT QA assessor audited source transcripts and confirmed the corrective stage order, exact reviewed SHA, test artifacts, and all five fresh telemetry rows. The fixture tree is clean after subsequent independent test execution with bytecode disabled, `main` remains at the original scaffold base, and runtime directories contain no tracked files. The original four telemetry rows remain unchanged.

## Telemetry and provenance

Five fresh corrective role stages emitted records via new agent IDs under a separate run ID, `ST-000211-recovery1`; see [records](ST211_Recovery_Telemetry.jsonl) and [installed aggregate](ST211_Recovery_Aggregate.json). Developer/QA stages used `claude-sonnet-5-5`, TL used `claude-opus-5-5`, and PO used `claude-haiku-4-5-20251001`. Every stage record has measured transcript usage and explicit unavailable session-final context. Each row reconciles with its actual fresh source transcript. The resumed outer orchestrator's bounded usage is unavailable and is not added to the fresh stage totals.

The CLI final text mistakenly calls these “six stage rows”; there are exactly five. Its session-level `resolved_model_matches: false` flag is retained because the historical runner expects all assistant events to use Sonnet, including required Opus/Haiku subagent events. This is not a G2/G6 acceptance claim.

The fixture repository does not contain the devkit source commit as a Git object; the source was exported into a separate devkit directory. Installed collector and preflight scripts are byte-identical to that pinned source export. Initial fingerprint comparisons normalize CRLF to LF; raw bytes do not match those normalized digest values, while normalized fingerprints and source-export bytes match. The shared installed workflow fingerprint also remains unchanged. There is no semantic helper drift.

## Remaining limitations and delivery gate

The scenario script's docstring recommends unittest discovery with `-t .`, which fails because its nested folders are not Python packages. The working designated direct script and discovery with `-s` both pass all seven tests; fixture TL accepted the docstring issue as nonblocking. It remains recorded rather than changing the approved commit. Fixture artifact paths use the story ID despite `Feature: none`, following the authorized recovery scope.

This capture establishes the stated FIX-01/FIX-03/FIX-04 functional and corrective observations. Independent formal devkit integration TL/QA review of the final evidence commit, its CI, approved merge, and release remain separate gates. FIX-02, G2/G5/G6 benchmarking, efficiency savings, and release success are not claimed.
