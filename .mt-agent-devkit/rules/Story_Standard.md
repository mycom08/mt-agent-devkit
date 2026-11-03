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
| **Done** | Verified complete | PO, or the orchestrator acting as PO under `po_execution: orchestrator` | After all AC pass and the PO, or the orchestrator acting as PO under `po_execution: orchestrator`, ticks | `status:done` |
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
1. Read the full story: User Story, all AC, Technical Scope, the immutable Base Branch, and any linked technical docs.
2. Create the dev branch through `branch_preflight.py create` from the explicit Base Branch, verified full SHA, and Remote Base SHA before changing status or product files; record the Story Branch only after create succeeds.
3. After successful branch verification, remove label `status:ready` and add `status:in-progress`.
4. Identify open points — post comments tagging **PO** (scope/AC) or **TL** (technical) for any blockers.
5. **Read PO and TL answers** — push back in the same thread if insufficient; wait until all blocking points are fully resolved.

### Status: In Progress → Review
**When:** Work complete, ready for review  
**Action:**
1. Self-check all AC locally — confirm each criterion is met (do **NOT** tick checkboxes; only PO ticks)
2. Run applicable pre-PR checks (see `Developer_Rules_Read_On_Demand.md` §5 or role-specific rules)
3. Create PR from dev branch → `main`; title: `[ST-XXXXXX][DEVKIT] Story title`
4. Remove label `status:in-progress`, add label `status:review`
5. Request reviewer in issue Comment

### Status: Review → In Progress (if feedback)
**When:** TL requests changes  
**Action:**
1. Address feedback in dev branch
2. Push new commits
3. Re-request review in issue Comment

> **Note:** Moving the story to `status:testing` is **TL's action** — TL sets the label immediately after approving the PR (see `Technical_Lead_Rules_Bootstrap.md §3`). The Implementer does not change the label after opening the PR.

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
- Developer creates the fix branch only through `branch_preflight.py create`, from the story's explicit `Base Branch` and verified full SHA.
- Developer removes label `status:done`, adds label `status:hotfix`

### Step 3 — Fix & Review
- Developer implements the fix
- Developer creates a PR targeting `main`
- Developer requests TL review in the Comment
- TL reviews and approves

### Step 4 — Re-Test
**Before any hotfix merge:** affected AC must be exercised on the fix branch and current independent verification must satisfy the acceptance contract in section 14. FAIL or NOT VERIFIED stops merge; post-merge rechecks do not replace this pre-merge gate.

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
| **PO** | Create stories, define AC, clarify scope in Comment, tick AC checkboxes after QA confirms. Acceptance (tick, done, close) is done by the PO, or the orchestrator acting as PO under `po_execution: orchestrator` | Approve code, comment on implementation |
| **Developer** | Implement, write PR, ask for guidance, self-check AC before marking ready | Tick AC, answer scope questions, review code |
| **TL** | Review code, approve PR, discuss technical design | Tick AC, test, clarify scope |
| **QA** | Test AC, report test results in Comment, notify PO when all AC pass | Tick AC, review code, approve stories |
| **BA** | Align requirements with AC, flag scope creep | Tick AC, approve code, implement |
| **UI/UX Designer** | Turn a wireframe/backlog story into a runnable prototype, write PR, ask for guidance, self-check AC before marking ready | Tick AC, answer scope questions, review code, ship a static-only mockup as the final deliverable |

---

## 9. Comment Standard

All discussions happen as **GitHub Issue comments**, never inside the issue body. The `comment` skill (`.mt-agent-devkit/skills/comment/SKILL.md`) owns the comment template and Thread Status, the writing rules, the `@` and bare `#` prefix bans, announcing body edits and the Commenter gate; load it before posting any comment. Role-only additions live in each role's rules (`Story_Standard_TL.md`, `Story_Standard_QA.md`, `Developer_Rules_Read_On_Demand.md §20`, `po-comment`).

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

In GitHub mode, pending CI routes to `.mt-agent-devkit/contracts/Wait_Work.md` (ci-watch); keep its wait ID and native command/session identity. PENDING cannot advance review or merge; FAIL/cancel/timeout routes to fixes. NO RUN uses the existing explicit zero-check evidence gate, never automatic PASS. After waiting, revalidate exact head and approval scope. Strict mode uses local verification without GitHub.

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
- [ ] **Paste the literal `gh pr checks <PR-number>` output into the approval comment** — turns "I confirmed CI was green" into an auditable artifact instead of a self-report. This paste is the single carve-out to the `comment` skill's rule 4 (gate-mandated CI evidence); nothing else in the approval comment may be a transcript.

> **Pre-existing vs PR-introduced problems:** A defect or contradiction **introduced by this PR** blocks approval — request changes. A **pre-existing** problem found in a file **outside the PR's scope** does not block — approve and record it as a follow-up story instead.

### Commenter — Before Posting an Issue Comment

Applies to every role, on every issue comment: run the Commenter gate in the `comment` skill before posting.

### Merge Gate

- [ ] TL has reviewed and approved PR ✓
- [ ] Applicable independent QA evidence confirms PASS for every current AC under `Story_Standard.md §14`; no FAIL, NOT VERIFIED, absent verdict, or stale-scope sign-off ✓

**Only then:** Merge dev branch to main

---

## 13. Story Creation Template

When creating a new story, **create a GitHub Issue** in `mycom08/mt-agent-devkit` with:

**Issue title:** `[ST-XXXXXX][DEVKIT] Clear Title`  
**Labels:** `status:backlog`, `sprint-N`  
**Body field:** `**Base Branch:** <existing branch selected during story creation>` — immutable; required before `status:ready` or execution.
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

> **Porting an already-validated pattern:** if this story replicates a split, refactor, or pattern already implemented and validated elsewhere in the repo (a prior story, a reference commit), name the exact reference commit SHA and/or file(s) to model in `Technical Scope` — not just the target file names or a prose description of the desired end state. An implementer given only the outcome has to reverse-engineer the actual boundary (which content moved where, section renumbering, deliberate gaps) via git archaeology before writing anything (ST-000132 retro).

---

## 14. AC Verdicts and Acceptance Disposition

This is the authoritative acceptance contract in GitHub and strict modes, including fast paths and skipped-validator routes. Role views and pipeline consumers must apply it before sign-off, merge advancement, checkbox acceptance, or done status.

### Per-AC verdict and evidence

Report every current AC separately: criterion identity, verdict, evidence pointer, tested scope/revision, and any reason or missing evidence. Use the current canonical story body; a prior report for different scope is not sign-off for revised scope.

| Verdict | Meaning | Required report |
|---|---|---|
| PASS | The criterion was exercised using its required method and sufficient evidence confirms the expected result | What was exercised and its evidence |
| FAIL | An executed check contradicts the required result | Observed failure and evidence |
| NOT VERIFIED | The criterion was not exercised or available evidence is insufficient | Reason, missing evidence, and dependency/owner needed to verify |

An unperformed check is NOT VERIFIED, not FAIL. If infrastructure/setup fails before the required behavior can be exercised, report the tooling failure separately and mark the AC NOT VERIFIED. When the behavior is exercised and its observed result contradicts the criterion, its verdict is FAIL even when the cause is environmental. Documentation of a dependency, a waiver to continue other work, or passing unrelated tests never makes an unexercised criterion PASS.

Examples:
- A required hostname request succeeds against the deployed hostname: PASS with request/result evidence. An executed request fails its expected response: FAIL. The hostname/go-live check is deferred or awaits DNS ownership: NOT VERIFIED; documenting the deferral is not PASS.
- A credential-gated flow has not run because its credential is unavailable: NOT VERIFIED, naming the missing credential by variable/name only. A stub, dummy credential, or different flow does not verify it.
- A guidance-only AC can PASS after the required inspection exercises the instruction against its specified scenarios. That inspection does not verify a separately required external or native-runtime behavior.

### Sign-off and closure gates

Testing-pass requires PASS with sufficient evidence for every remaining current AC and all applicable verification gates. Any FAIL, NOT VERIFIED, absent verdict, or insufficient evidence blocks testing-pass and merge advancement, even if an overall summary says PASS or CI is green. Retain the testing/open state and report the blocker; apply the existing blocked-story procedure when external input is required. No new verdict status label is needed.

The applicable independent QA sign-off must identify the scope/revision and per-AC evidence. Existing fast-path and skipped-validator routes still require their documented independent validation evidence for every AC; a skipped stage or reviewer approval alone cannot stand in for unperformed verification. Do not fabricate a QA-agent report when no QA agent ran.

- `- [ ]` = not accepted, including FAIL or NOT VERIFIED.
- `- [x]` = accepted by the PO, or the orchestrator acting as PO under `po_execution: orchestrator`, only after the applicable independent verification confirms PASS.

The PO, or the orchestrator acting as PO under `po_execution: orchestrator`, must locate that verification report, compare it with the current AC, and confirm merge before ticking checkboxes, closing, or setting done. Developer/TL assurances alone are not QA sign-off. A merged PR, auto-closed issue, or pre-ticked checkbox is not acceptance evidence. If auto-closure occurred with missing verification, reopen the story and retain/report its unresolved state; never mark it done.

### Explicit tracked scope split

An unverified requirement may leave the original scope only through this sequence:
1. Record an explicit PO/user scope decision; never silently delete or weaken the requirement. In `orchestrator` mode, the scope decision is the user's.
2. Create a named tracked follow-up preserving the requirement, dependency, and missing verification evidence (a story MD in strict mode).
3. Update the canonical original body to link the follow-up and define the remaining scope; link the original from the follow-up. Preserve the earlier NOT VERIFIED report as history, not a converted PASS.
4. Obtain renewed independent QA confirmation of every remaining original AC against that revised scope before testing-pass or merge advancement. Recheck any changed artifact under the existing review/SHA gates.
5. Only after applicable verification passes and merge is confirmed may the PO, or the orchestrator acting as PO under `po_execution: orchestrator`, accept the remaining original AC and close it. The follow-up remains open and unaccepted until its own verification succeeds.

A decision alone, an untracked deferral, or a follow-up link without an updated original scope cannot satisfy this sequence. Any remaining NOT VERIFIED AC still blocks advancement.


---

## 15. Shell Command Rules — Permissions and Tool Choice

Read and follow the selected provider adapter supplied in the worker packet
before issuing shell commands; it owns native shell and permission mechanics.
Write multiline or backtick-containing issue/PR bodies to a temporary file and
use `--body-file`; clean it after use. Do not assume another provider's Bash
allow-list is available.

---

## Version

**Created:** 2026-06-16  
**Version:** 1.5 — §9 and the §12 Commenter gate point to the shared `comment` skill, which now owns the comment standard (ST-999001)  
**Previous:** 1.4 — §1 Done row, §7 and §14: acceptance by the PO, or the orchestrator acting as PO under `po_execution: orchestrator`; §14 tracked split: in `orchestrator` mode the scope decision is the user's (ST-000291)  
**Previous:** 1.3 — §9: one-topic-per-comment promoted to a numbered writing rule, transcript prohibition made explicit with a single named carve-out for gate-mandated CI evidence, "body edits are announced, not reproduced" added; §12: new **Commenter** gate makes the ~150–200 word cap a `wc -w` self-check, split into a before-you-draft shape target and before-you-post checks so the count is a backstop rather than a trim-and-recount loop (ST-000038)  
**Previous:** 1.2 — §2, §4, §7, §13: adds `UI/UX Designer` as a sixth valid `**Assigned:**` role and role-boundary row (ST-000021)  
**Previous:** 1.1 — §3 adds per-file vs global fixture-coverage AC guidance; §9 requires same-pass body-AC reconciliation when a design-first approval narrows an AC (ST-000016 retro)
