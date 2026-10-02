# WF-002 benchmark readiness review

Date: 2026-10-02. Scope: offline review of PR #210 and its existing five local preparation commits through `3c9d1a3`, followed by integration of `7d44623`. No new Claude workflow or permission probe was run.

## Findings

The findings below describe the initial review. The offline follow-up now implements a separate frozen installed manifest, source-delta/configuration checks, canonical telemetry schema and identity checks, clean-worktree/changelog checks and external SHA-bound review evidence. See `Installed_Benchmark_Contracts.md` for commands and remaining provenance/independent-review limits. The historical pilot inputs are preserved. No fresh installed run has been performed.

| Area | Finding | Required action before measurement |
|---|---|---|
| Source comparison | Installed-run defaults still point to `a30460a` and `e2e700a`. Both precede the agent-ID telemetry discovery fix in PR #216. Updating the runner checkout does not update the devkit exported from those refs. | Freeze new full SHAs: integration `7d44623` as baseline and conflict-resolved FIX-02 `13e1421` as candidate. Inspect their distributed-template delta; it must contain only the three intended FIX-02 guidance files. |
| Manifest ownership | `benchmark_manifest.json` pins the historical local pilot (CLI 2.1.280, different model/tools). The installed runner records current CLI version but does not enforce a frozen installed-run configuration. | Keep historical pilot inputs unchanged. Freeze a separate installed-run configuration with CLI version, observed resolved model, Python version, fixture hashes, source SHAs, runner and permission-handler hashes, tools, appended policy, timeout, budget, repetitions, and installation scope. Reject drift before accepting a pair. |
| Permission path | Existing smoke evidence shows scoped Write/Edit, exact cleanup exceptions, persistence and in-target staging work. It does not establish full installed-run success. | Start with one fresh pair after account availability returns. Retain zero-denial evidence and failed attempts; proceed to repeated measurement only after full quality and telemetry review. |
| Product oracle | `inspect_product_diff` separates the exact pricing change from the required changelog. It accepts any nonempty added changelog line and inspects committed changes only. | Independently review changelog scope and the final working tree; reject unrelated edits, deletions or uncommitted product changes. |
| Telemetry oracle | The checker verifies four stage labels plus integer request/cache-read fields; it does not validate the complete schema, identity, timestamps, role/stage mapping or nonnegative counts. | Validate every row with the canonical collector contract and review raw-source provenance, actual times, unique stage identity and complete usage before any efficiency claim. Preserve unavailable fields as unavailable. |
| Quality and authority | Tests and five checked AC are inspected, but this does not establish independent TL/QA verdicts or absence of unauthorized mutations. | Review separate TL and QA evidence tied to the implementation SHA, PO closure, clean final state, unchanged main, remote absence, runtime-state exclusion and command traces. |
| Gate semantics | Installed runner exits 2 for a complete capture and leaves G2 unassessed. This is appropriately conservative. | Do not promote CLI exit 0, test success, a complete capture, or permission smoke results to G2/G6 acceptance. G5 remains failed under #214. |

## Run checklist when Claude becomes available

1. Freeze the installed configuration and verify the new baseline/candidate template delta. Preserve historical manifests and diagnostics.
2. Verify fixture hashes, strict mode, fresh targets, no remotes, installation/adaptation, clean main base, and exact identical story/AC input. Record hashes of all installed instructions, workflows, rules, scripts and adaptive context, not only the current required-file subset.
3. Run one fresh pair with the same pinned configuration and permission policy. Keep init costs separate from story execution costs, and distinguish stage-only usage from orchestrator totals.
4. Review exact product/changelog scope, six tests, unchanged AC, independent TL/QA verdicts, PO closure, branch/state safety and validated per-stage telemetry. Mark failures non-comparable and retain them.
5. Resolve #214 and obtain independent G5 review before accepting the FIX-02 optimization. Existing P01/P02 failures cannot be replaced by local oracle tests.
6. Collect at least three comparable repetitions per arm for G6; compare role-specific and total medians, slowest runs, requests, tool invocations, cache-read and quality. Record missing fields without estimates.
7. Complete cross-fix and installed regression, independent report review, merge and release gates.

## Offline verification

`python -m unittest discover -s tests/agent-workflows -p test_*.py -q`: 29 tests passed, one directory-symlink case skipped on Windows. `python scripts/validate_templates.py`: passed. Sandbox restrictions initially prevented fixture writes; the same offline suite passed with the required filesystem access. After integration, four pilot tests exposed synthetic final-result events with empty usage objects; their fixtures now provide the complete usage contract required by the merged collector. The suite passed again. No production collector rule was weakened and no paid runs were launched.

The distributed-template comparison `git diff 7d44623..13e1421 --name-only -- .claude/agents/templates` contains exactly the common bootstrap, Create Stories shared workflow and Refine Prototype shared workflow guidance files. Supporting telemetry and preflight code are identical between these proposed arms. Their full commit IDs must be recorded in the installed configuration before execution.

This is a preparation review, not an independent TL/QA approval or a benchmark verdict.
