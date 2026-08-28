# Business Analyst Rules — Read-On-Demand Tier

**Applies to:** Business Analyst agent
**Reference from:** `.antigravity/agents/working/instructions/business_analyst_instructions.md`

Not loaded at spawn. Fetch a section only when its named trigger fires — see `Business_Analyst_Rules_Bootstrap.md §6` for the routing table.

---

## 1. Pre-PR Gate (when acting as Implementer)

When BA is the story Implementer, run the applicable local checks before opening a PR:

| Change type | Required local check |
|---|---|
| `.sh` files changed | `bash -n <each changed .sh file>` — zero errors |
| `.ps1` files changed | PowerShell syntax check — zero parse errors |
| `.github/workflows/` changed | Validate YAML syntax; verify job structure and step ordering |
| Docs / template / workflow only | Exempt |

> **Gate:** Do not open a PR until all applicable checks pass.

---

## Version

**Version:** 1.0 — Split out of `Business_Analyst_Rules.md` (now `_Bootstrap.md`) §2, unchanged content, renumbered §1.
**Created:** 2026-08-25
