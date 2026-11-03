# Agent Common Troubleshooting

## 2. Troubleshooting Protocol

<!-- BEGIN GENERATED troubleshooting part protocol: edit .mt-agent-devkit/skills/troubleshooting/SKILL.md, then regenerate -->
Applies on any tooling/environment blocker: `gh` CLI auth failures · script syntax errors · shell script fails to run · CI YAML errors.

**Step 1 — Check memory first.** Scan your memory file's `## Troubleshooting Facts` for a matching entry. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix.** If no match, find the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory).** After resolving, record the fix under `## Troubleshooting Facts` in the Troubleshooting Facts shape before resuming.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.
<!-- END GENERATED troubleshooting part protocol -->

---

