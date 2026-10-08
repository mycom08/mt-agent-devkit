# Phase 1 Harness Acceptance Scenarios

**Story:** ST-000220
**QA-SHA:** 4d0087a65fc1d31ca1b45ac4271c672bd8905eba
**Status:** Refreshed for the round-2/3 review fixes. Full harness compliance is NOT certified; native evidence limits are recorded below.

## Happy Path
- Verify live PR head, authoritative independent approval and exact-head successful CI.
- Validate pinned inventory completeness, source-linked generated ownership, canonical routing and history/target baseline preservation.
- Run internal selection, skeleton and section isolation regression cases; inspect existing deployed-output and validator-fixture CI evidence.
- Select Codex from real exposed operation identities; resolve only its adapter.

## Error and Edge Cases
- Reject missing operations, conflicting/ambiguous declarations and unverified Antigravity candidates before state mutation.
- Reject malformed provider/run/story components and foreign, duplicate or missing sprint pointers.
- Reject dangling shared/legacy reads, invalid runtime bindings and internal tokens in distributed templates.
- Compare both legacy providers' rendered skeleton generation fragments; reject Codex target installation without a supported lifecycle target.
- Require canonical full bootstrap reads and triggered sections only for on-demand wrappers.
- Syntax-check changed shell wrappers and inspect explicit target GitHub/strict-mode regression evidence.

## Review-Fix Regression Rows (added at 4d0087a)
| # | Scenario | Expected |
|---|---|---|
| 1 | Edit `VERSION`, one template and one tracked memory file, then run `validate_internal_harness.py` with and without `--migration-preservation` | Default run exits 0; `--migration-preservation` exits 1 naming each violation; unmodified head passes both |
| 2 | Read the Claude adapter and `Agent_Common_Bootstrap` section 6 | Adapter restores: Bash for `gh`, no `cd` prefix, PowerShell backtick corruption, .NET permission prompts; workers must stop when the packet lacks the adapter path |
| 3 | Resume a provider-local singleton command state with a different run ID | Same provider-local root is reused; ownership is verified; ambiguity blocks |
| 4 | `provider_context.py` with a Claude and Codex combined tool set, no matching tools, and a foreign `--provider` | Each exits 2 (blocked); a Claude-only set selects only the Claude adapter |
| 5 | Inspect `validate-templates.yml` path filter | Covers `.mt-agent-devkit/**`, provider `harness/**`, `agents/working/**`, skills, `AGENTS.md`, `CLAUDE.md`; internal validator and unit tests run in CI |

## Native Behavioral Evidence
- Required for each provider: sanitized fresh spawn, same-session fix, expired-session fresh spawn, independent review/QA handoff, permission denial/escalation, pending/failed CI and bounded completion. Mocked selection tests do not prove native behavior.
- **Claude at 4d0087a:** user-launched headless run, fixture head f75b991 (base 60a84d0). Independent QA audit: fixture tests 3/3, diff `calculator.py` only, four distinct workers, same-Developer resume, TL approval and QA pass at one SHA, PO close of the fixture only. Functional PASS; harness compliance INCOMPLETE. No role read another role's working record or memory. Deviations recorded and accepted by the PO decision (issue #220 comment 6052260161) with follow-up stories #226, #227 and #228: Developer, TL and QA skipped their `Story_Standard_<role>.md` read; TL and QA skipped the adapter read; `Retro_Rules.md` unread or partly read; PO section-read `Agent_Common_Bootstrap`; telemetry timestamps are derived and not valid timing evidence; the synthetic local-only fixture has no GitHub, CI or merge steps. Expired-session, permission-denial and CI scenarios were not exercised. Model coverage is sonnet/medium only.
- **Antigravity (2b26111) and Codex (08ae9d1):** older-head evidence stands by PO decision and was not repeated at 4d0087a. Antigravity: representative functional PASS, compliance NOTVERIFIED, private-record reads by QA and PO workers recorded. Codex: local fixture path only; expiry and pending/failed hosted CI unwitnessed.
- Full harness compliance is NOT certified for any provider.

## Acceptance Mapping
- AC1 inventory; AC2 Claude baseline/safety; AC3 adapters and discovery; AC4 owner/references; AC5 state/history/rollback; AC6 static plus complete native story evidence; AC7 unchanged target/release boundary.
- Runtime evidence and per-AC findings live at the provider/run/story QA evidence path and linked PR/issue comments. No AC ticks or merge occur in QA.
