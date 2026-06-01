# Story Standard

**Applies to:** All agents (Developer, TL, QA, PO, BA)  
**Location:** GitHub Issues in repository `lhtuwrk/authorization-service`  
**Issue title format:** `[ST-XXXXXX][FEATURE] Story Title`

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
| **Ready** | Assigned, ready to start | PO | After assigning story to Developer | `status:ready` |
| **In Progress** | Active development | Developer | Dev branch created | `status:in-progress` |
| **Review** | Dev complete, awaiting TL code review | Developer | After creating PR | `status:review` |
| **Testing** | Code approved, QA testing | QA | After TL approval & merge | `status:testing` |
| **Done** | Verified complete | PO | After all AC pass and PO ticks | `status:done` |
| **Hotfix** | Bug found after Done; fix in progress | Developer | After hotfix branch created | `status:hotfix` |

**Status is tracked via GitHub Issue labels.** When changing status, remove the old label and add the new one.

---

## 2. Story Structure

Stories live as **GitHub Issues**. The issue body uses this Markdown structure:

> **Rule:** `**Assigned:**` is **mandatory** — the responsible agent role must be set when the story is created. Valid values: `Developer`, `Technical Lead`, `QA`, `Business Analyst`. "TBD" is not permitted. The `**Assigned:**` field must always appear **above** the `## User Story` section.

```markdown
**Phase:** [Phase/Sprint]  **Points:** [1-13]  **Priority:** Must/Should/Nice  
**Assigned:** Developer | Technical Lead | QA | Business Analyst

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

**Status** is tracked via the issue label (e.g., `status:in-progress`), not inside the body.  
**Sprint and phase** are tracked via GitHub Issue labels (e.g., `sprint-5`, `phase-2`) — do NOT use milestones.  
**Discussions** happen as GitHub Issue **comments** — never inside the issue body.

---

## 3. Story Scope: What Belongs IN vs. OUT

### DO Include in Story (Keep Concise)
- **User story statement:** As a..., I want..., so that...
- **High-level acceptance criteria:** WHAT the feature does, not HOW
- **Business value** and constraints
- **Success definition** (testable outcomes)
- **Reference to technical docs:** "See Section 2 of ABAC_Technical_Implementation.md for details"

### DO NOT Include in Story
- Field-by-field struct/database definitions
- Detailed implementation steps
- Code signatures or pseudo-code examples
- Schema diagrams (reference the technical doc instead)
- Algorithm pseudocode or formulas
- Full technical specifications

### Technical Details Live In:
- `docs/feature/[Feature]/technical/` — ABAC_Technical_Implementation.md, ABAC_Database_Schema.md
- Link from story AC: "See Technical Implementation Section 2.1 for field definitions"
- NOT embedded in story body

### Story Length Rules
- **Target:** 2-3 printed pages (clear, focused)
- **[WARNING]** 4+ pages indicates too much technical detail
- **Red Flags:** Field lists, code examples, algorithm pseudocode

### Example: Good vs. Bad AC

**Bad (Too Technical):**
```markdown
- [ ] `Rule` struct defined with 16 fields:
  - `ID` (string, UUID)
  - `TenantID` (string, validated from JWT)
  - `Name` (string, unique per tenant)
  - [... 13 more field specs ...]
```

**Good (Concise & Business-Focused):**
```markdown
- [ ] `Rule` type defined with all required fields (see Technical Implementation Section 2)
- [ ] Supports soft-delete and audit trail
- [ ] Extensible format for multiple rule syntaxes (JSON Phase 1, Casbin Phase 2)
```

---

## 4. Implementer Workflow (applies to all implementer roles: Developer, Technical Lead, QA, Business Analyst)

### Status: Ready → In Progress
**When:** Starting work on the story  
**Action:**
1. Remove label `status:ready`, add label `status:in-progress` on the GitHub Issue
2. Read the full story: User Story, all AC, Technical Scope, and any linked technical docs
3. **Verify the API spec** (`docs/api/`) for every endpoint the story touches — confirm request/response shape, required fields, enums, and constraints match the story AC. If spec is missing or inconsistent, post a Comment tagging **TL** before writing any code
4. Identify open points — post comments tagging **PO** (scope/AC) or **TL** (technical) for any blockers
5. **Read PO and TL answers** — if an answer is insufficient or raises a new concern, post a push-back follow-up before proceeding; wait until all blocking points are fully resolved
6. Create dev branch from the feature branch — **never work directly on the feature branch or master**:
   ```
   git checkout -b ST-XXXXXX/short-description
   ```

### Status: In Progress → Review
**When:** Work complete, ready for review  
**Action:**
1. Self-check all AC locally — confirm each criterion is met (do **NOT** tick checkboxes; only PO ticks)
2. Run integration test script in Git Bash: `bash tests/feature/.../ST-XXXXXX_*.sh` (see `docs/wiki/Testing_Guidelines.md`)
3. Source files follow naming standard (no `interface.go`, `helpers.go`, `types.go`)
4. Create PR from dev branch → **feature branch** (NOT master); title: `[ST-XXXXXX][FEATURE] Story title`
5. Remove label `status:in-progress`, add label `status:review`
6. Request reviewer in issue Comment

### Status: Review → In Progress (if feedback)
**When:** TL requests changes  
**Action:**
1. Address feedback in dev branch
2. Push new commits
3. Re-request review in issue Comment

### Status: Review → Testing (after TL approval)
**When:** TL approves PR  
**Action:**
1. Remove label `status:review`, add label `status:testing`
2. Add PR/commit links in issue Deliverables section (edit issue body)
3. Notify QA in issue Comment

---

## 5. QA Workflow

### Integration Tests

All integration tests (curl scripts) follow the standard defined in **`docs/wiki/Testing_Guidelines.md` — API Integration Test Rule section**.  
Scripts live in `tests/feature/<feature_name>/scripts/ST-XXXXXX_<description>.sh` and are run via **Git Bash**.

---

### Status: Testing
**Action:**
1. **Verify the API spec** (`docs/api/`) for every endpoint being tested — use the spec as the reference, not just live endpoint behaviour. If spec is missing or inconsistent, post a comment tagging **TL** before testing
2. Read story AC from the GitHub Issue body
3. Run the story's integration test script in Git Bash: `bash tests/feature/.../ST-XXXXXX_*.sh` (see `docs/wiki/Testing_Guidelines.md`)
4. Test each criterion against live code, cross-referencing the API spec
5. Report verification results per AC in a comment (do **NOT** tick checkboxes — only PO ticks AC)
6. If AC fails: Add a comment in the issue describing the issue
7. Request dev fix if needed

### Status: Testing → Done
**When:** All AC verified passing  
**Action:**
1. Check dev branch is merged to feature branch. If not, Comment to notify and wait for merge to complete
2. All AC verification results reported in Comment
3. Notify PO that all AC have passed — PO will tick the checkboxes
4. Remove label `status:testing`, add label `status:done`
5. Add final test report link in Deliverables (edit issue body, if available)

---

## 6. Hotfix Workflow (Post-Done)

**Applies when:** A bug is found after the story is already `status:done`.

**Rule: Never fix directly on the feature branch or main. Always create a fix branch.**

### Step 1 — Report
- QA (or whoever finds the bug) posts a Comment on the **original story issue** describing the issue
- Tag Developer and TL

### Step 2 — Branch
- Developer creates a fix branch from the **feature branch**:
  ```
  git checkout -b fix/ST-XXXXXX/short-description
  ```
- Developer removes label `status:done`, adds label `status:hotfix` on the issue

### Step 3 — Fix & Review
- Developer implements the fix on `fix/ST-XXXXXX/...`
- Developer creates a PR targeting the **feature branch**
- Developer requests TL review in the Comment
- TL reviews and approves

### Step 4 — Re-Test
- Developer merges fix branch to feature branch
- Developer removes label `status:hotfix`, adds label `status:testing`
- Developer notifies QA in Comment
- QA re-tests the affected AC against the API spec

### Step 5 — Done
- QA reports results in Comment
- PO ticks affected AC checkboxes
- Remove label `status:testing`, add label `status:done`

**Red Flags:**
- Fixing directly on feature branch or main (no fix branch created)
- Skipping TL review on a fix PR
- QA not re-verifying against API spec after fix

---

## 7. Role Boundaries — Who Does What

**Rule:** Each role has specific responsibilities. Do NOT do other agents' work.

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **PO** | Create stories, define AC, clarify scope in Comment, tick AC checkboxes after QA confirms | Approve code, comment on implementation |
| **Developer** | Implement, write PR, ask for guidance, self-check AC before marking ready | Tick AC, answer scope questions, review code |
| **TL** | Review code, approve PR, discuss technical design | Tick AC, test, clarify scope, implement |
| **QA** | Test AC, report test results in Comment, notify PO when all AC pass | Tick AC, review code, approve stories |
| **BA** | Align requirements with AC, flag scope creep | Tick AC, approve code, implement |

**Red Flags (violations):**
- TL, QA, Dev, or BA ticking AC checkboxes (only PO, after QA confirms)
- Developer answering scope questions (only PO)
- TL commenting as though they're the Developer
- QA commenting on code design instead of AC fitness

---

## 8. Technical Doc Divergence Rule

If during implementation you discover that a **technical document** (e.g., `ABAC_Technical_Implementation.md`, `ABAC_Strategic_Analysis.md`) is **inaccurate, contradictory, or ambiguous**:

1. **Do NOT silently deviate.** Implementing different behavior without flagging the doc gap creates hidden divergence that surfaces late in review.
2. **Post immediately in the story Comment**, tag TL, describe the discrepancy and which doc section is affected.
3. **TL decides:** fix the doc now (if it blocks the story) or log it for fix after the story completes (if non-blocking).

| Severity | Action | Example |
|----------|--------|---------|
| **Blocks correct implementation** | [BLOCKING] Stop. Post issue comment. Wait for TL to fix doc. | "Default decision says ALLOW in §1 but DENY in Strategic Analysis — which is correct?" |
| **Does not affect current story** | [NON-BLOCKING] Post issue comment. Continue work. TL fixes doc after story. | "Flow diagram is simplified but engine evaluates differently — doc needs update" |
| **Ambiguous, not wrong** | [NON-BLOCKING] Post issue comment. Ask TL to clarify before implementing. | "Doc says 'fail-secure' but doesn't define behavior for no_match" |

**Never copy incorrect doc text into code comments.** If the doc is wrong and you know the correct behavior, say so in the thread — don't propagate the error.

---

## 9. Comment Standard

All discussions happen as **GitHub Issue comments** — never inside the issue body.

Each comment follows this format:

```markdown
## [Comment title]
**Thread Status:** Open | In Progress | Resolved  
**Area:** [Endpoint / AC / Section / File]

**Developer - 2026-04-17**
Question or concern.

**TL - 2026-04-17**
Response and decision.

**Decision:** [What we decided and why]  
**Next:** [Owner or "None"]
```

**Thread Status** = status of this discussion thread (independent of the overall story label)  
Use comments for:
- Scope questions
- AC clarifications  
- Technical decisions
- Blocker escalations
- Implementation issues

**Rule for comment**:
- Open a new issue comment only for a new topic.
- Reply in the same comment when continuing the same issue.
- When a comment changes scope, acceptance criteria, status, or delivery expectations, update the issue body (AC, Deliverables) to match the resolved decision.
- Never put discussions inside the issue body. The body is for User Story, AC, and Deliverables only.
- **Never use the `@` prefix** — write role names without it (e.g., `**TL**`, `**PO**`, `**Dev**`). An `@` prefix triggers a GitHub mention notification to a real user account.
- **Never use a bare `#` prefix** to reference anything — use the `ST-XXXXXX` format or plain text instead. A bare `#` causes GitHub to create a cross-reference link to an unrelated issue or PR.

---

## 10. File Naming

**Stories** are GitHub Issues — no file naming needed. Issue title format: `[ST-XXXXXX][FEATURE] Title In Title Case`

✅ Good issue titles:
- `[ST-000001][ABAC] ABAC Policy API Contract`
- `[ST-000004][ABAC] Types And Interfaces`

❌ Bad issue titles:
- `ST-000001` (no title, no feature)
- `ABAC story` (no ID)

**Source code files:** Use descriptive names

❌ Bad:
- `interface.go` — Too generic, which interface?
- `types.go` — Too generic, what types?
- `helpers.go` — Too generic, what helpers?
- `errors.go`, `utils.go`

✅ Good:
- `rule_evaluator.go` — Implements RuleEvaluator interface
- `evaluation_types.go` — Types used in evaluation
- `condition_helpers.go` — Helper functions for conditions
- `validation_errors.go` — Validation error definitions

**Rule:** Name file after its **primary interface/struct**, use snake_case. Avoid generic names.

---

## 11. Key Rules to Remember

### Story Status Gates
- **Can't go to "In Progress"** without being assigned + Ready label
- **Can't go to "Review"** without all AC self-checked locally and tests passing
- **Can't go to "Testing"** without TL approval
- **Can't go to "Done"** without all AC verified by QA and ticked by PO
- **Can't fix a Done story** without creating a `fix/ST-XXXXXX/...` branch first

### Developer Responsibilities
- Update story status as work progresses
- Create PR only after all AC locally complete
- **Wait for TL review** before merging (no skipping!)
- Update story status to Testing after merge
- Use good file naming

### TL Responsibilities
- Review code in PR
- Approve only if meets Development Standard
- Approve only if file naming is good
- Notify story when PR approved

### QA Responsibilities
- Test against AC checklist
- Report verification results per AC in Comment
- Notify PO when all AC pass so PO can tick them
- Mark story Done when all AC confirmed
- Report failures in Comment

### PO Responsibilities
- Create stories with clear AC
- **Set assignee to the responsible agent role when creating the story — valid values: `Developer`, `Technical Lead`, `QA`, `Business Analyst`. "TBD" is not allowed**
- Move story to Ready when assigned
- Clarify AC in Comments if questions arise
- Tick AC checkboxes in issue body after QA confirms each criterion

---

## 12. Gate Checklists

### Implementer — Before Opening a PR

Applies to all implementer roles (Developer, Technical Lead, QA, Business Analyst):

- [ ] Issue label: `status:review`
- [ ] API spec verified — implementation matches spec for all affected endpoints (`docs/api/`)
- [ ] If `docs/api/ABAC_API.yaml` or `.spectral.yaml` changed: spec lint passes and spec drift check passes — see agent-specific rules for exact commands
- [ ] Self-checked all AC locally — each criterion confirmed met (do **NOT** tick checkboxes; PO ticks only)
- [ ] Integration test script exists at `tests/feature/<feature_name>/scripts/ST-XXXXXX_*.sh`
- [ ] Integration test script passes when run via Git Bash
- [ ] Service starts locally (`go run ./cmd/server`)
- [ ] Source files have good names (no `interface.go`, etc.)
- [ ] Code follows Development Standard
- [ ] PR created with story ID in title: `[ST-XXXXXX][FEATURE] ...`
- [ ] PR targets the **feature branch** — NOT master

**Only then:** Open the PR

### Reviewer — Before Approving a PR

Applies to all reviewer roles (Technical Lead, Developer peer review):

- [ ] All CI checks on the PR have **finished** — do not review while CI is still running
- [ ] No CI check is in a **failed** state — if any check failed, post a comment on the PR noting the failing check and ask the implementer to fix it; do not approve until CI is green
- [ ] Code review criteria pass (per agent-specific rules)

**Only then:** Approve the PR

### Merge Gate

- [ ] TL has reviewed and approved PR ✓
- [ ] PR review status shows "Approved"

**Only then:** Merge dev to feature branch

---

## 13. Story Creation Template

When creating a new story, **create a GitHub Issue** in `lhtuwrk/authorization-service` with:

**Issue title:** `[ST-XXXXXX][FEATURE] Clear Title`  
**Labels:** `status:backlog`, feature label (e.g., `feature:abac`), sprint label (e.g., `sprint-5`), phase label (e.g., `phase-2`)  
**Assignee:** TBD (set when moving to Ready)

**Issue body:**

> `**Assigned:**` must be one of the agent roles — not "TBD". Valid values: `Developer`, `Technical Lead`, `QA`, `Business Analyst`. Set it at story creation and place it above `## User Story`.

```markdown
**Phase:** [Phase/Sprint]  
**Story Points:** [1-13]  
**Priority:** Must-Have | Should-Have | Nice-to-Have  
**Assigned:** Developer | Technical Lead | QA | Business Analyst

## User Story

> As a **[persona]**,  
> I want **[feature]**,  
> So that **[benefit]**.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## API Spec Reference

[List affected endpoints and link to spec file, e.g. `docs/api/ABAC_API.yaml` §2.3 — or "N/A" if no API changes]

## Technical Scope

[Optional: architecture notes, API changes, database migrations]

## Deliverables

[Filled in after work complete: PR links, commits, artifacts]
```

> Discussions happen as **issue comments** using the format in §9. Do not add any discussion sections to the issue body.

---

## 14. AC Checkbox Rules

- `- [ ]` = Not yet signed off
- `- [x]` = Signed off by **PO** after QA confirms the criterion passes

**Who ticks:** Only the **PO** edits checkboxes in the GitHub Issue body.

**Developer:** Self-check all AC locally before marking story "Review" — confirm each criterion is met, but do **not** tick the checkboxes.

**QA:** Test each AC criterion and report pass/fail results in a Comment. Do **not** tick checkboxes. Notify PO when all AC have passed.

**PO:** After receiving QA confirmation, tick each AC checkbox `[x]` in the issue body.

**Before marking story "Review":** Developer must have self-checked all AC locally (no checkbox editing required).

**Before marking story "Done":** QA must report all AC verified in Comment; PO must tick all checkboxes `[x]` in issue body.

---

## 15. GitHub Issue CLI Editing — PowerShell Safety Rule

**Applies to:** All agents editing issue bodies or posting comments via `gh` CLI on Windows/PowerShell.

### The Problem

In PowerShell, the backtick ( `` ` `` ) is the escape character. Any `` `r ``, `` `n ``, or `` `t `` sequence inside a `--body "..."` inline string is interpreted as a carriage return, newline, or tab — silently corrupting backtick-fenced code, AC checkboxes, and multi-line content.

Example of what goes wrong:

```
# Intended:  - [ ] `rule_data` field uses `x-go-type: json.RawMessage`
# Actual:    - [ ] `rule_data` field uses `x-go-type: json.RawMessage
#            ule_data` field ...          ← `r treated as carriage return
```

### The Rule: Always Use `--body-file` for Issue Bodies and Comments

**Never** pass multi-line or backtick-containing Markdown via `--body "..."`. Always write to a temp file first:

```powershell
$body = @'
## Acceptance Criteria

- [ ] `oapi-codegen` installed as a Go development tool
- [ ] `rule_data` field uses `x-go-type: json.RawMessage`
'@

$tmp = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($tmp, $body, [System.Text.Encoding]::UTF8)
gh issue edit <number> --body-file $tmp
gh issue comment <number> --body-file $tmp   # same pattern for comments
Remove-Item $tmp
```

**Why `WriteAllText` with explicit UTF-8?** `Set-Content` may add a BOM or alter line endings. `WriteAllText` is reliable.

**Applies to:** `gh issue edit`, `gh issue create`, `gh issue comment` — any call where the body contains backticks, checkboxes, or spans multiple lines.

---

## Version

**Created:** 2026-04-17  
**Version:** 2.1 — §4 renamed to "Implementer Workflow (all roles)"; dev branch + PR target rules apply to TL, QA, BA; §12 adds PR-targets-feature-branch bullet (2026-05-29)

This is the single source of truth for story workflow across all agents.
