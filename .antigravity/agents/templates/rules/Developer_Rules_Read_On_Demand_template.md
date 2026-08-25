# Developer Rules — Read On Demand

**Applies to:** Developer agent.
**Read this file:** never as part of the Pre-Work Checklist, in whole or in part. Fetch **one section** when its trigger fires — the trigger table in `Developer_Rules_Bootstrap.md` §12 names which. Locate it with `grep -nE "^## [0-9]+\."` to bound the extraction; do not read the whole file.

**Numbering:** shares one numbering space with `Developer_Rules_Bootstrap.md` — sections 1–6 live there; §7–§11 live here. Numbers are never reused across the pair.

---

## 7. Reporting & Blockers

- Post blockers immediately as a comment in the GitHub Issue; tag TL or PO as appropriate

> Working-record write conventions (keep it short and fact-based, 3-entry retention, char cap, snapshot format) are bootstrap-tier — they live in `Developer_Rules_Bootstrap.md` §13 and `Agent_Common_Bootstrap.md §1`, not here.

---

## 8. Document Placement

- When you update or create project documents, use the current feature-doc structure. Refer section `## 4. Internal Project Documents` in project priming document.

---

## 9. Peer Review (when Dev acts as reviewer for a TL-implemented story)

When the orchestrator assigns Dev as peer reviewer, follow `Story_Standard_Dev.md` §12 Reviewer Gate, then apply this checklist:

**Review checklist:**
- Verify the PR follows naming conventions, commit message format, and test coverage rules from `Developer_Rules_Bootstrap.md` §4 and §5 — except commit subject-line **length**, which is a non-blocking nit per `Developer_Rules_Bootstrap.md` §6: note it in a comment, never request changes over it alone
- Check for obvious logic errors, missing error handling at system boundaries, and security issues
- **Confirm the CI check actually executed, not just its conclusion**, confirm the cited run's head SHA matches the PR's current head SHA, and diagnose any red required check from its actual failing log — see `Technical_Lead_Rules_Bootstrap.md §2` for the full detail of these checks (same rules apply to peer review)
- **Stub/TODO re-check:** confirm stub markers/trivial-return patterns in AC-functional methods were scanned and any hit has an owning backlog story
- Post inline PR comments for required changes; post a brief notify comment on the GitHub Issue
- When all criteria pass, post approval as a comment on the PR (GitHub blocks self-approval — use `gh pr comment`)

---

## 10. Mid-Implementation Consultation (when a question surfaces during implementation)

If you encounter an unclear AC, scope ambiguity, or technical decision point while implementing — and making a judgment call is not appropriate — do NOT use the Blocked Story Procedure and do NOT ask the user. Instead:

1. Identify who owns the question:
   - Scope or AC question → **PO**
   - Technical or design question → **TL**
   - Both → **PO + TL**
2. Record the question on the story:
   - **GitHub mode:** post a comment on the GitHub Issue tagging the right role(s)
   - **Strict mode:** append a comment entry to the story MD `## Comments` section tagging the right role(s)

   Use the format:
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
5. When the orchestrator resumes you with the answer: read it, apply it, and continue implementation from where you paused.

> Use this for genuine ambiguities that would otherwise require a judgment call affecting scope or design. Do not use it for implementation details you can reasonably decide yourself.

---

## 11. Live User Instruction Conflicts (mandatory rule during implementation)

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread (by PO, TL, or the user themselves), the live instruction takes precedence. When this happens:

1. Acknowledge the conflict explicitly — state what the prior decision was and what the new instruction is
2. Proceed with the live instruction
3. Document the override in the PR description so the reviewer understands why the prior decision was not followed

Do not silently follow the old decision, and do not block awaiting re-confirmation — the user's live instruction is the authoritative signal.

---

## Version

**Version:** 1.0 — Split out of `Developer_Rules_template.md` v2.11 (§7–§8 relocated as-is; §11 Peer Review relocated as-is, renumbered §9; Mid-Implementation Consultation and Live User Instruction Conflicts extracted from §2's inline text, new §10/§11), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
