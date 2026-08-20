# Developer Rules — Extended (Scenario-Conditional)

**Applies to:** Developer agent — devkit's own team only (`.claude/agents/working/`). Relocated out of `Developer_Rules.md`, `developer_instructions.md`, and `Story_Standard_Dev.md` 2026-08-20, applying the pattern from issue #123 (and its extension to the Story_Standard views, issue #133) to the devkit's own agent team first (the distributable `.claude/agents/templates/` role rules are unchanged — a separate story). `Developer_Rules.md`, `developer_instructions.md`, and `Story_Standard_Dev.md` are each read in full on every Dev spawn regardless of story content; the six sections below apply only in scenarios that don't arise on most stories (a mid-implementation ambiguity, a live user override, Dev acting as reviewer instead of implementer, a sprint-refinement task the orchestrator explicitly assigns, a post-Done hotfix). Read this file **only when the matching scenario actually occurs** — do not read it as part of the standard Pre-Work Sequence. `Developer_Rules.md` §2/§11, `developer_instructions.md`'s Refine Sprint Task heading, and `Story_Standard_Dev.md` §4/§6/§12 each still carry a one-line pointer to their relocated section here.

---

## 1. Mid-Implementation Consultation (when a question surfaces during implementation)

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

## 2. Live User Instruction Conflicts (mandatory rule during implementation)

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## 3. Peer Review (when Dev acts as reviewer for a TL-implemented story)

When the orchestrator assigns Dev as peer reviewer:
- Verify the PR follows naming conventions and pre-PR gate checks from `Developer_Rules.md` §4–§5 — except commit subject-line **length**, which is a non-blocking nit per §6: note it in a comment, never request changes over it alone
- Check for obvious logic errors or missing content
- **Confirm the CI check actually executed, not just its conclusion**, confirm the cited run's head SHA matches the PR's current head SHA, and diagnose any red required check from its actual failing log — see `Technical_Lead_Rules.md §2` for the full detail (same rules apply to peer review)
- Post inline PR comments for required changes; post a brief notify comment on the GitHub Issue
- When all criteria pass, post approval as a comment on the PR (GitHub blocks self-approval — use `gh pr comment`)

---

## 4. Refine Sprint Task (only when the orchestrator asks for a Sprint Refinement)

Triggered from `developer_instructions.md`'s Refine Sprint Task heading.

### Step 1 — Fetch Target Stories
1. Run: `gh issue list --repo mycom08/mt-agent-devkit --label "sprint-N" --label "status:backlog" --state open`
2. For each returned issue, read the full body: User Story, AC, Technical Scope

### Step 2 — Identify Open Points Per Story
For each story ask:
- Is every AC criterion specific, testable, and unambiguous? (scope/AC question → tag PO)
- Are there implementation dependencies, design decisions, or workflow questions not answered in the story? (technical question → tag TL)
- Are there acceptance criteria that conflict with or are missing from context? (scope question → tag PO)

If a story has **no open points**, mark it as clear — do not post a comment.

### Step 3 — Post Question Comments
For each story with open points, post **one GitHub issue comment** following `Story_Standard.md` §9 comment format. Set `**Thread Status:** Open`. One comment per story.

### Step 4 — Review Answers and Confirm
After the orchestrator notifies you that TL and PO have answered:
1. Re-read each comment thread where you posted questions
2. If all answers are clear → post: "All open points resolved — story is ready for development. PO please move to ready." Set `**Thread Status:** Resolved`
3. If an answer is insufficient → post a follow-up in the same thread
4. Update your Working Record

---

## 5. Developer as Reviewer (when TL is implementer)

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
- [ ] Code review criteria pass (per `Developer_Rules.md §11`)

---

## 6. Hotfix (post-Done bug)

Triggered from `Story_Standard_Dev.md §6`. When a bug is found after a story is `status:done`, **never fix on main**. Create a fix branch off main, then run the normal review/test cycle:

1. Create `fix/ST-XXXXXX/short-description` from main; set the issue to `status:hotfix`
2. Fix on that branch → open a PR targeting `main` → request TL review
3. After TL approval, merge → set `status:testing` → notify QA to re-validate the affected AC
4. QA reports results → PO ticks AC → `status:done`

---

## Version

**Version:** 1.1 — Added §5 (Developer as Reviewer) and §6 (Hotfix), relocated from `Story_Standard_Dev.md` §4/§6/§12 per devkit issue #133 (extends the #123 pattern to the Story_Standard views).
**Previous:** 1.0 (created 2026-08-20, split out of `Developer_Rules.md` v1.5 and `developer_instructions.md` per devkit issue #123).
