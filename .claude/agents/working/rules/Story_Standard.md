# Story Standard

**Applies to:** All agents (Developer, TL, QA, PO, BA, UI/UX Designer)  
**Location:** GitHub Issues in repository `mycom08/mt-agent-devkit`  
**Issue title format:** `[ST-XXXXXX][DEVKIT] Story Title`

---

## 1. Story Status Workflow

```
Backlog → Ready → In Progress → Review → Testing → Done
                                                     ↓ (if bug found after Done)
                                                  Hotfix → Review → Testing → Done
```

| Status | Meaning | Who Changes | When | GitHub Label |
|--------|---------|-------------|------|--------------|
| **Backlog** | Story planned; assignee must be set at creation | PO | After creation | `status:backlog` |
| **Ready** | Assigned, ready to start | PO | After assigning story to implementer | `status:ready` |
| **In Progress** | Active development | Implementer | Dev branch created | `status:in-progress` |
| **Review** | Dev complete, awaiting TL code review | Implementer | After creating PR | `status:review` |
| **Testing** | Code approved, QA testing | TL | After TL PR approval | `status:testing` |
| **Done** | Verified complete | PO | After all AC pass and PO ticks | `status:done` |
| **Hotfix** | Bug found after Done; fix in progress | Implementer | After hotfix branch created | `status:hotfix` |

**Status is tracked via GitHub Issue labels.** When changing status, remove the old label and add the new one.

---

## 2. Story Structure

Stories live as **GitHub Issues**. The issue body uses this Markdown structure:

> **Rule:** `**Assigned:**` is **mandatory** — the responsible agent role must be set when the story is created. Valid values: `Developer`, `Technical Lead`, `QA`, `Business Analyst`, `UI/UX Designer`. "TBD" is not permitted. The `**Assigned:**` field must always appear **above** the `## User Story` section.
>
> **Note — two separate "assignee" concepts:** The `**Assigned:**` field in the issue body (an agent role) drives pipeline routing and must always be set. It is distinct from the **GitHub Issue Assignee** (a GitHub user account set in the sidebar), which may be left unset in agent-driven workflows.

```markdown
**Phase:** [Phase/Sprint]  **Points:** [1-13]  **Priority:** Must/Should/Nice  
**Assigned:** Developer | Technical Lead | QA | Business Analyst | UI/UX Designer

## User Story
> As a **[who]**, I want **[what]**, so that **[why]**.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [x] Criterion 3 (checked when signed off by PO after QA confirms)

## Deliverables
- PR #123
- Merged commit abc123
```

**Optional sections** (pointer-style, one line per item): **API Spec Reference**, **Technical Scope** (pointers to technical docs, not embedded detail), **Design Source**. Do not invent other sections.

**One list per concern:** a body may reference related stories in **one** place only — never in both a Background section and a Related section.

**Status** is tracked via the issue label (e.g., `status:in-progress`), not inside the body.  
**Sprint** is tracked via GitHub Issue labels (e.g., `sprint-5`) — do NOT use milestones.  
**Discussions** happen as GitHub Issue **comments** — never inside the issue body.

---

## 3. Story Scope: What Belongs IN vs. OUT

### DO Include in Story (Keep Concise)
- **User story statement:** As a..., I want..., so that...
- **High-level acceptance criteria:** WHAT the change does, not HOW
- **Business value** and constraints
- **Success definition** (testable outcomes)
- **Reference to technical docs:** "See docs/technical/..."

### DO NOT Include in Story
- File-by-file content specifications
- Implementation walkthroughs
- Exact file content to write
- Algorithm pseudocode

### Specifying Test/Fixture-Coverage AC
When an AC requires "one negative fixture (or test) per check/invariant," distinguish **per-file checks** (which scan each file and can be exercised by a single bad fixture) from **global/aggregate checks** (which read a single shared manifest or evaluate the corpus as a whole). A global check cannot be isolated to one per-file fixture — exempt it explicitly, or require a parameter-override hook so it stays testable. Say which checks are per-file and which are global so a missing per-file fixture for a global check is not flagged as a coverage gap at review.

**AC hygiene:** an AC states the **testable requirement only**. Rationale, history, and precedent references go in a comment or linked doc — never inside the AC item.

### Body Amendments (edit-time rules)

These rules govern **editing an existing story body** (refinement outcomes, corrections):

1. **Decisions, not derivations.** A refinement/correction outcome is written into the body as the decision itself — target **≤ 5 lines per decision** — with a pointer to the resolving comment for the full rationale. Never copy the argument into the body.
2. **The body is always current truth.** No supersession notes, no "*(corrected on \<date\>, replacing…)*" narration — GitHub issue edit history is the audit trail. Rewrite the affected section cleanly.
3. **Scope rules apply to amendments too.** An edit may not introduce implementation detail (file paths, type/member signatures, algorithm choices) that a fresh body would not be allowed to contain.

---

## 4. Implementer Workflow (applies to all implementer roles: Developer, Technical Lead, QA, Business Analyst, UI/UX Designer)

### Status: Ready → In Progress
**When:** Starting work on the story  
**Action:**
1. Remove label `status:ready`, add label `status:in-progress`
2. Read the full story: User Story, all AC, Technical Scope, and any linked technical docs
3. Identify open points — post comments tagging **PO** (scope/AC) or **TL** (technical) for any blockers
4. **Read PO and TL answers** — push back in the same thread if insufficient; wait until all blocking points are fully resolved
5. Create dev branch from main: `git checkout -b ST-XXXXXX/short-description`

### Status: In Progress → Review
**When:** Work complete, ready for review  
**Action:**
1. Self-check all AC locally — confirm each criterion is met (do **NOT** tick checkboxes; only PO ticks)
2. Run applicable pre-PR checks (see Developer_Rules.md §5 or role-specific rules)
3. Create PR from dev branch → `main`; title: `[ST-XXXXXX][DEVKIT] Story title`
4. Remove label `status:in-progress`, add label `status:review`
5. Request reviewer in issue Comment

### Status: Review → In Progress (if feedback)
**When:** TL requests changes  
**Action:**
1. Address feedback in dev branch
2. Push new commits
3. Re-request review in issue Comment

> **Note:** Moving the story to `status:testing` is **TL's action** — TL sets the label immediately after approving the PR (see `Technical_Lead_Rules.md §3`). The Implementer does not change the label after opening the PR.

---

## 5. QA Workflow

### Status: Testing
**Action:**
1. Read story AC from the GitHub Issue body
2. Validate each criterion against the changed files or behavior described in the PR
3. Report verification results per AC in a comment (do **NOT** tick checkboxes — only PO ticks)
4. If AC fails: Add a comment in the issue describing the issue
5. Request dev fix if needed

### Status: Testing → Done
**When:** All AC verified passing  
**Action:**
1. Check dev branch is merged to main. If not, Comment to notify and wait
2. All AC verification results reported in Comment
3. Notify PO that all AC have passed — PO will tick the checkboxes
4. Remove label `status:testing`, add label `status:done`

---

## 6. Hotfix Workflow (Post-Done)

**Rule: Never fix directly on main. Always create a fix branch.**

### Step 1 — Report
- QA (or whoever finds the issue) posts a Comment on the **original story issue**
- Tag Developer and TL

### Step 2 — Branch
- Developer creates a fix branch from `main`:
  ```
  git checkout -b fix/ST-XXXXXX/short-description
  ```
- Developer removes label `status:done`, adds label `status:hotfix`

### Step 3 — Fix & Review
- Developer implements the fix
- Developer creates a PR targeting `main`
- Developer requests TL review in the Comment
- TL reviews and approves

### Step 4 — Re-Test
- Developer merges fix branch to main
- Developer removes label `status:hotfix`, adds label `status:testing`
- Developer notifies QA in Comment
- QA re-validates the affected AC

### Step 5 — Done
- QA reports results in Comment
- PO ticks affected AC checkboxes
- Remove label `status:testing`, add label `status:done`

---

## 7. Role Boundaries — Who Does What

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **PO** | Create stories, define AC, clarify scope in Comment, tick AC checkboxes after QA confirms | Approve code, comment on implementation |
| **Developer** | Implement, write PR, ask for guidance, self-check AC before marking ready | Tick AC, answer scope questions, review code |
| **TL** | Review code, approve PR, discuss technical design | Tick AC, test, clarify scope |
| **QA** | Test AC, report test results in Comment, notify PO when all AC pass | Tick AC, review code, approve stories |
| **BA** | Align requirements with AC, flag scope creep | Tick AC, approve code, implement |
| **UI/UX Designer** | Turn a wireframe/backlog story into a runnable prototype, write PR, ask for guidance, self-check AC before marking ready | Tick AC, answer scope questions, review code, ship a static-only mockup as the final deliverable |

---

## 9. Comment Standard

All discussions happen as **GitHub Issue comments** — never inside the issue body.

Each comment follows this format:

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Workflow / Template / AC / File]

**Developer - 2026-04-17**
Question or concern.

**TL - 2026-04-17**
Response and decision.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

**Comment-writing standard (all roles):**

1. **Decision-first.** The first line states the decision/outcome. Rationale follows, capped at ~2–3 sentences per point.
2. **One topic per comment.** A comment answers the questions asked and nothing else. A finding that surfaces while answering — however relevant — posts as its own comment with its own thread status. Bundling makes a thread unresolvable: it cannot be closed while any of its topics stays open, so a multi-topic comment leaves `Thread Status` with no coherent value.
   > Replying to several questions **that were genuinely asked together** in one comment is fine and expected — this is not a one-reply-per-question rule. What it prohibits is an *unasked* finding smuggled into an answer.
3. **Length cap: ~150–200 words per comment**, checked with `wc -w` at the Commenter gate (§12). Exemption: QA validation reports (per-AC evidence) may be longer — thoroughness there is high-signal.
   > **Draft to the shape, not to the counter.** Before writing, decide the shape: **one short paragraph per topic** — decision first, one-line why, pointer to the evidence. A comment drafted that way lands near the cap without anyone counting. The `wc -w` check is a **backstop that should almost never fire**, not the drafting method: a long draft cut down to 200 words costs several full re-reads of your context and produces worse prose than 200 words written deliberately. If the check fails by more than a little, the fix is usually that you bundled a second topic (rule 2) — split it, don't compress it.
4. **Evidence by pointer, not transcript.** Applies to issue comments and PR comments alike. Cite what was checked (file/doc name + one-line result). Full check logs go in your own working record, not the thread. **Never paste command output, check transcripts, or verification logs into a comment** — state the verdict in one line and cite the working record. A reader who needs the transcript can open it; a reader who does not pays for it on every read of the thread.
   > **Single carve-out — gate-mandated CI evidence.** The literal `gh pr checks <PR-number>` output that the §12 Reviewer gate requires in a **PR approval comment** is a mandated audit artifact and is exempt from this rule. It is the *only* exemption: no other output, transcript, or log may be pasted, in any comment, by any role.
5. **Body edits are announced, not reproduced.** When a comment's decision is written into the story body in the same pass, the comment states which section changed, what kind of change, and why — never the resulting body text. The body is current truth; the comment is the reason it changed. Reproducing the new wording creates a second copy that goes stale on the next edit and then contradicts the body.
6. **Corrections state the delta only.** What changed, what didn't, one-line why. Never re-derive conclusions that didn't change.
7. **No comments about comments.** If a prior comment lacked substance, put the substance in your working record and post one pointer line.
8. **One close-out per thread.** Post the "resolved / ready" hand-off line once; never restate it in later comments.
9. **Recommended default format** — compact bullets: claim → source checked → verdict. Not a license for thinner review.

**Rules for comments:**
- Reply in the same comment when continuing the same issue; a new topic gets its own comment (rule 2).
- When a comment changes AC or delivery expectations — including a **design-first approval comment that narrows or supersedes an AC** — update the issue body in the **same pass** so later-stage reviewers never have to reconcile the body AC against a separate design thread.
- **Never use the `@` prefix** — write role names without it (e.g., `**TL**`, `**PO**`, `**Dev**`).
- **Never use a bare `#` prefix** — use the `ST-XXXXXX` format or plain text instead.

---

## 11. Key Rules to Remember

### Story Status Gates
- **Can't go to "In Progress"** without being assigned + Ready label
- **Can't go to "Review"** without pre-PR checks passing
- **Can't go to "Testing"** without TL approval
- **Can't go to "Done"** without all AC verified by QA and ticked by PO
- **Can't fix a Done story** without creating a `fix/ST-XXXXXX/...` branch first

---

## 12. Gate Checklists

### Implementer — Before Opening a PR

- [ ] Issue label: `status:review`
- [ ] Self-checked all AC locally (do **NOT** tick checkboxes; PO ticks only)
- [ ] Applicable pre-PR checks pass (see role-specific rules §5/§13)
- [ ] PR created with story ID in title: `[ST-XXXXXX][DEVKIT] ...`
- [ ] PR targets `main`

### Reviewer — Before Approving a PR

- [ ] All CI checks on the PR have **finished**
- [ ] No CI check is in a **failed** state
- [ ] Review criteria pass (per agent-specific rules)
- [ ] **Paste the literal `gh pr checks <PR-number>` output into the approval comment** — turns "I confirmed CI was green" into an auditable artifact instead of a self-report. This paste is the single carve-out to §9 rule 4 (gate-mandated CI evidence); nothing else in the approval comment may be a transcript.

> **Pre-existing vs PR-introduced problems:** A defect or contradiction **introduced by this PR** blocks approval — request changes. A **pre-existing** problem found in a file **outside the PR's scope** does not block — approve and record it as a follow-up story instead.

### Commenter — Before Posting an Issue Comment

Applies to every role, on every issue comment.

**Before you draft** — one line, and it is what makes the rest of this gate cheap:

- [ ] Shape chosen: one short paragraph per topic — decision, one-line why, pointer (§9 rule 3)

**Before you post:**

- [ ] Answers only the questions asked — a new finding gets its own comment (§9 rule 2)
- [ ] No command output, check transcript, or verification log pasted inline — verdict in one line, cite the working record (§9 rule 4). The `gh pr checks` carve-out belongs to PR approval comments only; it never applies here
- [ ] A decision written into the story body in this same pass is announced, not reproduced (§9 rule 5)
- [ ] Facts already recorded in your memory file are cited, not re-explained (`Agent_Common_Records.md §1` rule 4)
- [ ] Word count checked — `wc -w` ≤ 200, or a stated exception

> **Stated exception:** QA per-AC validation evidence (§9 rule 3) may exceed the cap. Note the exception in the comment; do not silently skip the check.
>
> **If the count fails, don't start truncating.** Re-check the first item instead: an over-length draft is usually a bundled second topic (rule 2) or a pasted transcript (rule 4), and both are fixed by removing something whole rather than by compressing everything. Iterative trim-and-recount is the most expensive way to reach 200 words — each pass re-reads your entire context.

**Only then:** Post the comment

### Merge Gate

- [ ] TL has reviewed and approved PR ✓
- [ ] QA has signed off on all AC ✓

**Only then:** Merge dev branch to main

---

## 13. Story Creation Template

When creating a new story, **create a GitHub Issue** in `mycom08/mt-agent-devkit` with:

**Issue title:** `[ST-XXXXXX][DEVKIT] Clear Title`  
**Labels:** `status:backlog`, `sprint-N`  
**GitHub Assignee:** (Optional — a GitHub user account; may be left unset in agent-driven workflows)

**Issue body:**

```markdown
**Phase:** [Phase/Sprint]  
**Story Points:** [1-13]  
**Priority:** Must-Have | Should-Have | Nice-to-Have  
**Assigned:** Developer | Technical Lead | QA | Business Analyst | UI/UX Designer

## User Story

> As a **[persona]**,  
> I want **[feature]**,  
> So that **[benefit]**.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Technical Scope

[Optional: design notes, template changes, workflow changes]

## Deliverables

[Filled in after work complete: PR links, commits, artifacts]
```

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms the criterion passes

**Who ticks:** Only the **PO** edits checkboxes in the GitHub Issue body.

**QA:** Test each AC criterion and report pass/fail results in a Comment. Do **not** tick checkboxes. Notify PO when all AC have passed.

**PO:** After receiving QA confirmation, tick each AC checkbox `[x]` in the issue body.

---

## 15. Shell Command Rules — Permissions and Tool Choice

**Applies to:** All agents running shell commands (Bash or PowerShell tool).

### Rule 1 — Never prepend `cd` to a command

The working directory is automatically set to the project root for every tool call. Prepending `cd "/path/to/project"` to a command creates a compound command that breaks allow-list matching.

### Rule 2 — Always use Bash for all `gh` CLI calls

**Never** use PowerShell for `gh` commands. `Bash(gh issue *)`, `Bash(gh pr *)`, and `Bash(gh label *)` are pre-approved in the project allow-list.

### Posting a Comment or Editing an Issue Body

For short, single-line bodies with no backticks:
```bash
gh issue comment <number> --repo mycom08/mt-agent-devkit --body "Simple text"
```

For multi-line or backtick-containing Markdown, write to a temp file first using the Write tool, then reference it:
```bash
gh issue comment <number> --repo mycom08/mt-agent-devkit --body-file /tmp/comment.md
gh issue edit <number> --repo mycom08/mt-agent-devkit --body-file /tmp/body.md
```

Delete the temp file immediately after the `gh` call completes.

### Changing Labels

```bash
gh issue edit <number> --repo mycom08/mt-agent-devkit --add-label "status:done" --remove-label "status:testing"
```

---

## Version

**Created:** 2026-06-16  
**Version:** 1.3 — §9: one-topic-per-comment promoted to a numbered writing rule, transcript prohibition made explicit with a single named carve-out for gate-mandated CI evidence, "body edits are announced, not reproduced" added; §12: new **Commenter** gate makes the ~150–200 word cap a `wc -w` self-check, split into a before-you-draft shape target and before-you-post checks so the count is a backstop rather than a trim-and-recount loop (ST-000038)  
**Previous:** 1.2 — §2, §4, §7, §13: adds `UI/UX Designer` as a sixth valid `**Assigned:**` role and role-boundary row (ST-000021)  
**Previous:** 1.1 — §3 adds per-file vs global fixture-coverage AC guidance; §9 requires same-pass body-AC reconciliation when a design-first approval narrows an AC (ST-000016 retro)
