# FIX-01 fresh installed-stage verification

Run date: 2026-09-29. Devkit: `fda5d18` (FIX-01/FIX-03 branch). Scenario: frozen WF-002 shipping fixture from `test/wf002-controlled-benchmark`. Claude CLI: 2.1.284, resolved model: `claude-sonnet-5-5`, Python: 3.12.10.

The strict-mode devkit was installed into a fresh local project using `scaffold_mechanical.sh` plus project-specific agent files. A local runner started four fresh role sessions in sequence and invoked the **installed** `.antigravity/agents/scripts/telemetry.py extract --append` immediately after each completed role. The runner handled stage transitions. It did not run the full installed Start Story orchestrator, so G2 remains unassessed. The project had no remote or external product service.

| Stage | Role verdict | Requests | Output tokens | Collector equals Claude final usage |
|---|---|---:|---:|---|
| Developer implementation | completed | 6 | 1,778 | yes, all four usage counters |
| Technical Lead review | approved | 3 | 1,083 | yes, all four usage counters |
| QA verification | approved | 3 | 1,367 | yes, all four usage counters |
| Product Owner closure | closed | 4 | 1,214 | yes, all four usage counters |

The collector produced [four Schema v1 records](FIX01_WF002_Fresh_Installed_Stages.jsonl) with four unique role/stage identities and `usage_source: raw_transcript`. `aggregate` succeeded; total output was 5,442 tokens. The seeded suite had one expected failure before implementation; the final six tests passed. The only product diff was the `>` to `>=` shipping threshold correction. Raw streams were kept outside product history during the run and are not committed.

This verifies the output-token reconciliation and record emission for fresh installed role stages. The complete orchestrator path and baseline-versus-candidate release gates remain separate work in issue #211.
