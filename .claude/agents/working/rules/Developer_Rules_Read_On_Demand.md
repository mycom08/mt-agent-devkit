# Developer Rules — Read On Demand

**Applies to:** Developer agent — devkit's own team only (`.claude/agents/working/`).
**Read this file:** never as part of the Pre-Work Sequence, in whole or in part. Fetch **one section** when its trigger fires — the trigger table in `Developer_Rules_Bootstrap.md` §18 names which. Use the `read-section` skill (`.claude/skills/read-section/`) with `grep -nE "^## [0-9]+\."` to bound the extraction; do not read the whole file.

**Numbering:** §7, §8 and §12–§17 keep the numbers they had before, so every existing citation resolves here unchanged. **§1–§6 have moved to `Developer_Rules_Bootstrap.md` at their original numbers.** §9–§11 are **retired**: they were pointer-only sections, now trigger rows in `Developer_Rules_Bootstrap.md` §18. §12–§17 are the former `Developer_Rules_Extended.md` §1–§6 (old → new: §1→§12, §2→§13, §3→§14, §4→§15, §5→§16, §6→§17). **Numbers in this lineage are never reused** — leave gaps rather than renumbering, so a stale citation resolves to nothing rather than silently to a *different* rule.

---

## 7. Reporting & Blockers

- Post blockers immediately as a comment in the GitHub Issue; tag TL or PO as appropriate

> Working-record write conventions (keep it short and fact-based, 3-entry retention, char cap, snapshot format) are bootstrap-tier — they live in `Developer_Rules_Bootstrap.md` and `Agent_Common_Bootstrap.md §1`, not here.

---

## 8. Document Placement

When you update or create project documents, use the current structure. Refer section `## 6. Internal Project Documents` in the Project Priming document.

---

## 12. Mid-Implementation Consultation (when a question surfaces during implementation)

If you encounter an unclear AC, scope ambiguity, or technical decision point while implementing — and making a judgment call is not appropriate — do NOT use the Blocked Story Procedure and do NOT ask the user. Instead:

1. Identify who owns the question:
   - Scope or AC question → **PO**
   - Technical or design question → **TL**
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
5. When the orchestrator resumes you with the answer: read it, apply it, and continue implementation from where you paused.

> Use this for genuine ambiguities that would otherwise require a judgment call affecting scope or design. Do not use it for implementation details you can reasonably decide yourself.

---

## 13. Live User Instruction Conflicts (mandatory rule during implementation)

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## 14. Peer Review (when Dev acts as reviewer for a TL-implemented story)

When the orchestrator assigns Dev as peer reviewer:
- Verify the PR follows naming conventions and pre-PR gate checks from §4–§5 — except commit subject-line **length**, which is a non-blocking nit per §6: note it in a comment, never request changes over it alone
- Check for obvious logic errors or missing content
- **Confirm the CI check actually executed, not just its conclusion**, confirm the cited run's head SHA matches the PR's current head SHA, and diagnose any red required check from its actual failing log — see `Technical_Lead_Rules_Read_On_Demand.md §5` for the full detail (same rules apply to peer review)
- Post inline PR comments for required changes; post a brief notify comment on the GitHub Issue
- When all criteria pass, post approval as a comment on the PR (GitHub blocks self-approval — use `gh pr comment`)

---

## 15. Refine Sprint Task (only when the orchestrator asks for a Sprint Refinement)

Triggered from `developer_instructions.md`'s Refine Sprint Task heading.

### Step 1 — Fetch Target Stories
1. Run: `gh issue list --repo mycom08/mt-agent-devkit --label "sprint-N" --label "status:backlog" --state open`
2. For each returned issue, read the full body: User Story, AC, Technical Scope

### Step 2 — Identify Open Points Per Story
For each story ask:
- Is every AC criterion specific, testable, and unambiguous? (scope/AC question → tag PO)
- Are there implementation dependencies, design decisions, or workflow questions not answered in the story? (technical question → tag TL)
- Are there acceptance criteria that conflict with or are missing from context? (scope question → tag PO)
- **Step-positioning check:** If an AC describes a position in a multi-step sequence using only outer boundaries (e.g., "after X and before Z"), and the sequence has intermediate steps not named in the AC, flag as an open question to PO — boundary-only positioning is ambiguous when middle steps exist.

If a story has **no open points**, it still needs an explicit **cleared note**: post one GitHub issue comment stating the story was reviewed and no open points were found, with `**Thread Status:** Resolved` and no agent tagged. Do not leave a clear story silent — Stage 4 promotes on the presence of a comment, so a silently-clear story matches Stage 4's "no final comment → leave as `status:backlog`" branch and is never promoted.

### Step 3 — Post Question Comments
For each story with open points, post **one GitHub issue comment** following `Story_Standard_Dev.md` §9 comment format. Set `**Thread Status:** Open`. One comment per story.

### Step 4 — Review Answers and Confirm
After the orchestrator notifies you that TL and PO have answered:
1. Re-read each comment thread where you posted questions
2. If all answers are clear → post: "All open points resolved — story is ready for development. PO please move to ready." Set `**Thread Status:** Resolved`
3. If an answer is insufficient → post a follow-up in the same thread
4. Update your Working Record

---

## 16. Developer as Reviewer (when TL is implementer)

Triggered from `Story_Standard_Dev.md §4/§12`. Only when the orchestrator assigns Developer the Stage 2 peer review role for a TL-implemented story:

1. Review the PR diff via `gh pr diff <number> --repo mycom08/mt-agent-devkit`
2. Post inline PR comments for specific line-level feedback
3. **Always post a brief notify comment on the GitHub Issue** — whether approving or requesting changes:

   ```
   ## PR #NNN peer review — <Approved | Changes Requested>
   **Thread Status:** Open | Resolved
   **Area:** Implementation

   **Developer - YYYY-MM-DD**
   <Summary of findings or approval rationale>

   **Next:** TL to address CR items | None
   ```

4. Use `gh pr comment` for the PR-level verdict (not `gh pr review --approve` — GitHub blocks self-approval)

**Reviewer Gate — before approving:**
- [ ] All CI checks on the PR have **finished**
- [ ] No CI check is in a **failed** state
- [ ] Code review criteria pass (per §14)

---

## 17. Hotfix (post-Done bug)

Triggered from `Story_Standard_Dev.md §6`. When a bug is found after a story is `status:done`, **never fix on main**. Create a fix branch off main, then run the normal review/test cycle:

1. Create `fix/ST-XXXXXX/short-description` from main; set the issue to `status:hotfix`
2. Fix on that branch → open a PR targeting `main` → request TL review
3. After TL approval, merge → set `status:testing` → notify QA to re-validate the affected AC
4. QA reports results → PO ticks AC → `status:done`

---

## Version

**Version:** 2.1 — numbering preamble condensed; the benchmark rationale for the §1–§6 move lives in this footer and the commit log, not in the read path.
**Previous:** 2.0 — §1–§6 moved out to `Developer_Rules_Bootstrap.md` at their original numbers. A full story spawn triggers all six, so fetching them here cost a `read-section` load plus a 7,640-char fetch and saved nothing (2026-08-21 benchmark #148/#149). This file now holds only genuinely conditional rules: §7, §8, §12–§17.
**Previous:** 1.1 — `Developer_Rules_Extended.md` §1–§6 merged in as §12–§17, one on-demand file per role.
**Created:** 2026-08-21
