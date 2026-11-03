# UI/UX Designer Rules — Read-On-Demand Tier

**Applies to:** UI/UX Designer agent
**Reference from:** `.mt-agent-devkit/instructions/ui_ux_designer_instructions.md`

Not loaded at spawn. Fetch a section only when its named trigger fires — see `UI_UX_Designer_Rules_Bootstrap.md §10` for the routing table.

---

## 1. Mid-Implementation Consultation (when a question surfaces during implementation)

An unclear flow, ambiguous AC or technical decision point while building follows `raise-question` §3 (`.mt-agent-devkit/skills/raise-question/SKILL.md`): post the question, report the consultation to the orchestrator, and never use the Blocked Story Procedure or ask the user.

---

## 2. Live User Instruction Conflicts (mandatory rule during implementation)

The rule is `raise-question` §5 (`.mt-agent-devkit/skills/raise-question/SKILL.md`).

---

## Version

**Version:** 1.1 — §1 and §2 point to `raise-question` §3 and §5 (ST-000308).
**Previous:** 1.0 — Split out of `UI_UX_Designer_Rules.md` (now `_Bootstrap.md`) §2's two conditional sub-blocks, unchanged content, renumbered §1/§2.
**Created:** 2026-08-25
