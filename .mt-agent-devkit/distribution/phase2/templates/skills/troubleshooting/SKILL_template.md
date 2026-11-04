---
name: troubleshooting
description: Tooling and environment blockers for every role - scan your own recorded fixes first, then diagnose, fix and record the fix in the Troubleshooting Facts shape before resuming. Load on any tooling or environment blocker.
---

# Troubleshooting

**Requires:** `agent-memory` (where the memory file lives and how it is read)

Canonical owner. Part `protocol` is also copied into `Agent_Common_Read_On_Demand.md` §2 and `Agent_Common_Troubleshooting.md`, and part `format` into `Agent_Common_Read_On_Demand.md` §1 and `Agent_Common_Memory.md`.

## Protocol

<!-- part: protocol -->
Applies on any tooling/environment blocker: tests fail to run · sandbox fails to start or become healthy · automation runner cannot connect · test script errors · CI YAML errors · auth/credential failures in test scripts.

**Step 1 — Check memory first.** Scan your memory file's `## Troubleshooting Facts` for a matching entry. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix.** If no match, find the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory).** After resolving, record the fix under `## Troubleshooting Facts` in the Troubleshooting Facts shape before resuming.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.
<!-- /part: protocol -->

## Troubleshooting Facts Shape

<!-- part: format -->
`## Troubleshooting Facts` keeps its own shape, distinct from `## Stored Facts`:

```md
## Troubleshooting Facts

### Fix N — <short label>
- **Problem:** Short label (e.g., "Docker sandbox fails to start")
- **Symptoms:** Exact error message or observable behavior
- **Root Cause:** Why it happened
- **Fix:** Exact commands/steps to resolve
- **Prevention:** What to check upfront to avoid this next time
```

> PO and BA record `## Stored Facts` only — the `## Troubleshooting Facts` section applies to roles that run tooling (Developer, Technical Lead, QA). The Stored Facts shape applies uniformly across all six roles; Troubleshooting Facts stays scoped to Dev/TL/QA.
<!-- /part: format -->
