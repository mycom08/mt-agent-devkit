# Story Standard — Technical Lead View

> Technical Lead working rules for story work. This is your day-to-day reference. `.antigravity/agents/working/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When |
|--------|-------------|------|
| Backlog | PO | After creation |
| Ready | PO | After assigning |
| In Progress | Implementer | Dev branch created |
| **Review** | Implementer | After PR created — **TL reviews here** |
| **Testing** | TL (notifies QA) | After TL approval & merge |
| Done | PO | After all AC pass |

---

## 2. Story Structure (reference)

Story body contains: `**Assigned:**` field above `## User Story`, `## Acceptance Criteria`, `## Deliverables`. All discussions happen as **comments** on the issue.

---

## 4. TL as Implementer

When `**Assigned:** Technical Lead` and TL is running Stage 1 (implementation):

### Status: In Progress → Review
1. Remove `status:in-progress`, add `status:review`
2. Create PR with title: `[ST-XXXXXX][DEVKIT] Story title`
3. **Add PR link to issue Deliverables section** — edit the issue body to include the PR URL under `## Deliverables` (use `gh issue edit --body-file`)
4. Post a brief comment on the story notifying the Developer reviewer:

   ```
   ## PR ready for peer review
   **Thread Status:** Open
   **Area:** Implementation

   **TL - YYYY-MM-DD**
   PR #NNN opened for peer review. <one-line summary of changes>

   **Next:** Developer
   ```

### Status: Review → In Progress (Developer feedback)
1. Address all CR items in the branch
2. Push new commits
3. Re-request review via issue comment

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **TL** | Review code, approve PR, discuss technical design, implement when assigned | Tick AC, test, clarify scope |

**Red Flags:** TL ticking AC checkboxes; TL commenting on scope (PO only) — see `Technical_Lead_Rules.md §2` for how this differs from a routine AC-clarification edit; TL self-approving PR (GitHub blocks it — use `gh pr comment` instead).

---

## 9. Comment Standard

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Workflow / Template / AC / File]

**TL - YYYY-MM-DD**
Technical decision or review feedback.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

- Post code review changes as **inline PR comments** + a brief notify comment on the GitHub Issue
- Reply in the same thread for the same topic
- **Never use the `@` prefix** — write role names without it (e.g., `**Dev**`, `**PO**`)
- **Never use a bare `#` prefix** — use `ST-XXXXXX` format or plain text
- **One topic per comment** — answer the questions asked and nothing else. A finding that surfaces *while* reviewing — however relevant — posts as its own comment with its own thread status; a bundled thread cannot be resolved while any of its topics stays open. Batching replies to questions asked together is fine.
- **Writing standard:** decision-first (first line = the decision/outcome), rationale ≤ 2–3 sentences per point, cap ~150–200 words — draft to shape (one short paragraph per topic: decision, one-line why, pointer) so the `wc -w` check is a backstop, not a trim-and-recount loop; evidence by pointer — **never paste command output, check transcripts, or verification logs**, state the verdict in one line and cite your working record; the single carve-out is **gate-mandated CI evidence** — the literal `gh pr checks <PR-number>` output the §12 Reviewer gate requires in a PR approval comment, which you must paste and nothing else; facts already recorded in your memory file are cited, not re-explained (`Agent_Common.md §2` rule 4); corrections state the delta only (never re-derive unchanged conclusions); no comments about comments; one close-out line per thread. When a refinement decision goes into the story body: the decision itself, ≤ 5 lines, pointer to the resolving comment — announce the edit, never reproduce the resulting body text. Run the **Commenter gate** (`Story_Standard.md §12`) before posting. Full rules: `Story_Standard.md §3 (Body Amendments), §9`.

---

## 12. Reviewer Gate — before approving a PR

- [ ] All CI checks on the PR have **finished**
- [ ] No CI check is in a **failed** state
- [ ] **Zero checks reported ≠ CI failing.** Check whether the head commit is path-filtered/`[skip ci]` (docs-only) — if so, that's "nothing runnable changed," proceed. If the commit touched CI-relevant paths and still shows zero checks, CI is genuinely missing — do not approve without a real run or an explicit deviation note
- [ ] Code review criteria pass (per `Technical_Lead_Rules.md §2`)

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Always use Bash (not PowerShell) for all `gh` CLI calls.** Never prepend `cd /path` to a command; the working directory is already set.

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:

```bash
gh issue edit <number> --repo mycom08/mt-agent-devkit --body-file /tmp/body.md
gh issue comment <number> --repo mycom08/mt-agent-devkit --body-file /tmp/comment.md
```

Delete the temp file immediately after the `gh` call completes.
