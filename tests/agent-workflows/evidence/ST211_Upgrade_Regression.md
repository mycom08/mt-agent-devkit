# ST-000211 installer and legacy-upgrade correction

This closes the two blocking findings from the independent Opus review of `35b921560a197ba45c1bf6d8a474da6ad863c04d`. That review is recorded on [PR219](https://github.com/mycom08/mt-agent-devkit/pull/219#issuecomment-5948673822) and [story211](https://github.com/mycom08/mt-agent-devkit/issues/211#issuecomment-5948698235) before correction began. The containing Git commit identifies the corrected review head.

## Changes and exercised contracts

- Claude and Antigravity Init/Update/Build inventories consistently install and retain all four scripts, including `branch_preflight.py`; init ignore documentation includes memory. Project-root sync now selects all four helpers and uses canonical `.claude/agents/templates/` manifest source paths for every owned file, while deployed target paths still adapt to either surface.
- Sync and local update document append-only runtime ignore migration, explicit authorization for index-only untracking on a dedicated maintenance branch, preservation of local bytes and historical commits, and operator/PO confirmation of missing immutable story bases. `--auto` does not authorize untracking or story metadata changes. Existing in-progress branches remain intact. The reference-only working sync mirrors retain their pre-existing intentional audit-stage divergence.
- The temporary-repository regression exposed an important Git behavior: index-only removal preserves local memory immediately, but switching/merging the old tracked base can subsequently delete it. The corrected migration requires a local backup outside the checkout and content-hash verification/restoration after base synchronization. No published history is rewritten.

`scripts/test/test_upgrade_deployment.py` executes four targeted contracts: script inventory parity; project-root manifest selection for both surface substitutions; actual fresh scaffolds for both surfaces in GitHub and strict modes; and legacy GitHub upgrades on both surfaces. Fresh installs compare canonical helper bytes and run Git ignore checks for memory, working records, retros, temporary telemetry, and internal reports. Legacy fixtures begin with tracked memory, preserve custom ignore patterns and product bytes, keep missing Base Branch unresolved until explicit confirmation, verify old history and restored local bytes, then run the installed helper's clean synchronized `inspect` and SHA-pinned `create`. These are deterministic deployment tests, not a claim that a model executed a network sync workflow.

## Verification

The new contracts were written first and failed against the original installer inventories and missing migration guidance. During correction, preserved failures identified a test parser digit omission, incorrect remote-SHA CLI flag, the real base-merge memory deletion edge, and a Windows CRLF assertion. All were resolved before the successful aggregate run.

- Canonical `bash scripts/test/run.sh`: **46 tests passed**, plus all nine validator fixture cases; aggregate reports 10 passed / 0 failed.
- `python scripts/validate_templates.py`: all Layer-1 invariants passed.
- `git diff --check`: passed.
- The branch-preflight and telemetry script sources and shared pipeline behavior are unchanged from the earlier reviewed/canary head. Existing fresh and corrective source-transcript evidence remains preserved; no paid canary was repeated for this inventory/migration correction.

The final integration TL/QA review and CI must cover the containing corrected head. This document does not claim their approval or release completion.

## Observed benefit and limits

The enhancement provides verified correctness and safety benefits: fresh installed role usage reconciles with actual transcripts; numeric full-read drift is rejected while clean exclusions pass; unsafe Git bases fail closed; and legacy targets can upgrade without silently losing local knowledge or guessing story bases. The new deployment tests directly prevent recurrence of missing-helper installation and the memory deletion edge found during review.

No request-count, token, duration, or monetary savings have been verified. The fresh capture and controlled correction are validation costs, not a controlled before/after benchmark. FIX-02 and G2/G5/G6 efficiency measurement remain in story218.
