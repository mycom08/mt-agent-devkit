# Developer Rules — Read On Demand

**Applies to:** Developer agent.
**Read this file:** never as part of the Pre-Work Checklist, in whole or in part. Fetch **one section** when its trigger fires — the trigger table in `Developer_Rules_Bootstrap.md` §12 names which. Use the `read-section` skill (`.mt-agent-devkit/contracts/Read_Section.md`) with `grep -nE "^## [0-9]+\."` to bound the extraction; do not read the whole file.

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

When the orchestrator assigns Dev as peer reviewer, follow `Developer_Rules_Read_On_Demand.md` §12 Reviewer Gate, then apply this checklist:

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

## 12. Developer as Reviewer (when TL is implementer)

Triggered by the peer-review assignment route in `Developer_Rules_Bootstrap.md §12`. Only when the orchestrator assigns Developer the Stage 2 peer review role for a TL-implemented story:

1. Review the PR diff via `gh pr diff <number> --repo {github-org}/{repo-name}`
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
- [ ] All CI checks on the PR have **finished** — do not review while CI is still running
- [ ] No CI check is in a **failed** state — if any failed, comment on the PR and ask for a fix; do not approve until green
- [ ] Code review criteria pass (per §9)

---

## 13. Hotfix (post-Done bug)

Triggered by the post-Done bug route in `Developer_Rules_Bootstrap.md §12`. When a bug is found after a story is `status:done`, **never fix on the feature branch or master**. Create a fix branch off the feature branch, then run the normal review/test cycle:

1. Run `branch_preflight.py inspect` and `create` for `fix/ST-XXXXXX/short-description` from the story's immutable Base Branch, using the verified full Base/Remote Base SHAs. Only after successful branch creation, set the issue to `status:hotfix`.
2. Fix on that branch → open a PR targeting the **feature branch** → request TL review
3. After TL approval, merge → set `status:testing` → notify QA to re-test the affected AC
4. QA reports results → PO ticks AC → `status:done`

---

## 14. Refine Sprint Task (only when the orchestrator asks for a Sprint Refinement)

Triggered from `developer_instructions.md`'s Refine Sprint Task heading. The orchestrator-owned procedure is `Refine_Sprint_Workflow.md` Stages 1 and 3; this section is the Developer's view of it.

When the orchestrator asks you to run a **Sprint Refinement**, execute the following steps.

### Step 1 — Fetch Target Stories
1. Read `docs/feature/{feature-name}/plan/Product_Backlog.md` — find the sprint marked `🔲 Planned` and note its sprint label (e.g., `sprint-5`)
2. Run: `gh issue list --repo {github-org}/{repo-name} --label "sprint-N" --label "status:backlog" --state open`
3. For each returned issue, read the full body: User Story, AC, Technical Scope, API Spec Reference

### Step 2 — Identify Open Points Per Story
For each story ask:
- Is every AC criterion specific, testable, and unambiguous? (scope/AC question → tag PO)
- Are all referenced API endpoints defined in `docs/api/`? (technical question → tag TL)
- Are there implementation dependencies, design decisions, or architecture questions not answered in the story? (technical question → tag TL)
- Are there acceptance criteria that conflict with or are missing from the roadmap? (scope question → tag PO)
- **Step-positioning check:** If an AC describes a position in a multi-step sequence using only outer boundaries (e.g., "after X and before Z"), and the sequence has intermediate steps not named in the AC, flag as an open question to PO — boundary-only positioning is ambiguous when middle steps exist.

If a story has **no open points**, it still needs an explicit **cleared note**: post one GitHub issue comment stating the story was reviewed and no open points were found, with `**Thread Status:** Resolved` and no agent tagged. Do not leave a clear story silent — Stage 4 promotes on the presence of a comment, so a silently-clear story matches Stage 4's "no final comment → leave as `status:backlog`" branch and is never promoted.

### Step 3 — Post Question Comments
For each story with open points, post **one GitHub issue comment** following `Developer_Rules_Read_On_Demand.md` §15 comment format:
- Group technical questions under a `**TL**` heading
- Group scope/AC questions under a `**PO**` heading
- Set `**Thread Status:** Open`
- One comment per story — do not open separate comments for separate questions on the same story

### Step 4 — Review Answers and Confirm
After the orchestrator notifies you that TL and PO have answered:
1. Re-read each comment thread where you posted questions
2. If all answers are clear → post a final reply in the **same comment thread**:
   > "All open points resolved — story is ready for development. PO please move to ready."
   > Set `**Thread Status:** Resolved`
3. If an answer is insufficient or raises a new question → post a follow-up in the **same thread** (do not open a new comment); report back to orchestrator to trigger another TL/PO answer cycle
4. Update your Working Record

---

## 15. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved
**Area:** [Endpoint / AC / Section / File]

**Developer - YYYY-MM-DD**
Question or concern.

**TL - YYYY-MM-DD**
Response and decision.

**Decision:** [What we decided and why]
**Next:** [Owner or "None"]
```

- **One topic per comment** — answer the questions asked and nothing else; a finding that surfaces while answering posts as its own comment with its own thread status. Batching replies to questions asked together is fine; smuggling an unasked finding into an answer is not.
- Reply in the same thread for the same topic
- When a comment resolves a scope/AC question, update the issue body to match
- **Never use the `@` prefix** — write role names without it (e.g., `**TL**`, `**PO**`). An `@` prefix triggers a GitHub mention to a real user account.
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text. A bare `#` creates a GitHub cross-reference to an unrelated issue or PR.
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words, draft to shape rather than trim-and-recount; **never paste command output or check transcripts** — verdict in one line, logs in your working record; carve-out: paste the literal `gh pr checks <PR-number>` output when peer-reviewing (`Developer_Rules_Read_On_Demand.md §12` requires it in the approval comment) — nothing else gets pasted; a body edit made in the same pass is announced, not reproduced; facts already in your memory file are cited, not re-explained; corrections state the delta only; no comments about comments; one close-out line per thread. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rule: `Story_Standard.md §9`.

---

## 16. Technical Doc Divergence Rule

If a technical document is inaccurate, contradictory, or ambiguous during implementation:

1. **Do NOT silently deviate** — post immediately in the story Comment, tag TL
2. **TL decides:** fix now (blocking) or after story (non-blocking)

| Severity | Action |
|----------|--------|
| Blocks implementation | [BLOCKING] Stop. Post comment. Wait for TL fix. |
| Non-blocking | [NON-BLOCKING] Post comment. Continue. TL fixes after story. |
| Ambiguous | [NON-BLOCKING] Post comment. Ask TL to clarify before implementing. |

---

## 17. Touched-Endpoint Verification

When the story touches an endpoint, before writing code verify its API spec (`docs/api/`): shape, required fields, enums and constraints. If missing or inconsistent, post a comment to TL and wait for the blocking decision. Before merge confirm implementation matches the spec for every affected endpoint. This verification is distinct from the spec-first update/codegen procedure in `Developer_Rules_Bootstrap.md §5`.

---

## 18. Behavioral Sandbox and Integration Verification

Before opening a PR, behavioral changes (source code, SQL migrations, config files, Docker files, environment variables or CI pipeline logic) require starting the local docker service with `docker compose` and running requests against the sandbox stack to verify expected behavior end-to-end. An integration test script must exist and pass via Git Bash for behavioral changes.

For any story with an existing integration script, run `bash tests/feature/.../ST-XXXXXX_*.sh`; see `docs/wiki/Testing_Guidelines.md`. This existing-script execution duty also applies to nonbehavioral stories. Docs, README and API-spec names/descriptions with no request/response-shape impact need no local service test. All applicable Bootstrap verification gates still apply.

---

## Version

**Version:** 1.2 — Added §14 (Refine Sprint Task), relocated verbatim from `developer_instructions_template.md`, which now carries a one-line trigger pointer instead of the full procedure; the instruction file is read on every Developer spawn, the refinement procedure applies to one workflow.
**Previous:** 1.1 — Added §12 (Developer as Reviewer) and §13 (Hotfix), relocated from `Story_Standard_Dev_template.md` sections 4, 6, and 12 per devkit issue #133 (ST-000134), extending the same trim already validated on the devkit's own team.
**Previous:** 1.0 — Split out of `Developer_Rules_template.md` v2.11 (§7–§8 relocated as-is; §11 Peer Review relocated as-is, renumbered §9; Mid-Implementation Consultation and Live User Instruction Conflicts extracted from §2's inline text, new §10/§11), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
