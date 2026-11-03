# Business Analyst Rules — Read-On-Demand Tier

**Applies to:** Business Analyst agent
**Reference from:** `.mt-agent-devkit/instructions/business_analyst_instructions.md`

Not loaded at spawn. Fetch a section only when its named trigger fires — see `Business_Analyst_Rules_Bootstrap.md §6` for the routing table.

---

## 1. Pre-PR Gate (when acting as Implementer)

When BA is the story Implementer, run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`) before opening a PR. It is the same gate for every implementer: harness, template and workflow changes run the validators and are never exempt as docs-only.

---

## Version

**Version:** 1.1 — §1 points to `pre-pr-gate`, the stricter gate (ST-000308).
**Previous:** 1.0 — Split out of `Business_Analyst_Rules.md` (now `_Bootstrap.md`) §2, unchanged content, renumbered §1.
**Created:** 2026-08-25
