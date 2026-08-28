# UI/UX Designer Rules — Read-On-Demand Tier

**Applies to:** UI/UX Designer agent
**Reference from:** `.antigravity/agents/working/instructions/ui_ux_designer_instructions.md`

Not loaded at spawn. Fetch a section only when its named trigger fires — see `UI_UX_Designer_Rules_Bootstrap.md §10` for the routing table.

---

## 1. Mid-Implementation Consultation (when a question surfaces during implementation)

If you encounter an unclear flow, ambiguous AC, or a technical decision point while building — and making a judgment call is not appropriate — do NOT use the Blocked Story Procedure and do NOT ask the user. Instead:

1. Identify who owns the question:
   - Flow or scope question → **PO**
   - Technical question → **TL**
   - Both → **PO + TL**
2. Post a comment on the GitHub Issue tagging the right role(s). Use the format:
   ```
   **Mid-implementation question — [TL / PO / both]**
   <specific question — one clear sentence>
   **Decision needed:** <what answer would unblock you>
   ```
3. Report back to the orchestrator using this format:
   ```
   Mid-implementation consultation needed — ST-XXXXXX
   Owner: <TL / PO / both>
   Question: <same question as posted on issue>
   Decision needed: <same decision needed>
   Implementation paused at: <brief description of where you stopped>
   Question recorded on story: posted
   ```
4. Do NOT change the story label. The orchestrator will spawn or resume TL and/or PO to answer in the issue thread, then resume you with their response.
5. When the orchestrator resumes you with the answer: read it, apply it, and continue from where you paused.

> Use this for genuine ambiguities that would otherwise require a judgment call affecting scope or design. Do not use it for implementation details you can reasonably decide yourself.

---

## 2. Live User Instruction Conflicts (mandatory rule during implementation)

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## Version

**Version:** 1.0 — Split out of `UI_UX_Designer_Rules.md` (now `_Bootstrap.md`) §2's two conditional sub-blocks, unchanged content, renumbered §1/§2.
**Created:** 2026-08-25
