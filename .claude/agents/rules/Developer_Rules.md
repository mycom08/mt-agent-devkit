# Developer Rules

**Applies to:** Developer agent  
**Reference from:** `.claude/agents/developer_instructions.md`

---

## 1. Mandatory Reading Before Any Implementation

Before writing a single line of code on any story, Dev **must** read:

| Document | Path |
|---|---|
| Story Standard (Dev) | `.claude/agents/rules/STORY_STANDARD_DEV.md` |

The key Development Standards rules are already embedded in §4–§6 of this document (naming, testing, git workflow). Only read `docs/wiki/Development_Standards.md` if you encounter a specific convention question not covered here.

> **Gate:** Do not begin implementation until `STORY_STANDARD_DEV.md` has been read in the current session.

---

## 2. Before Starting a Story (Mandatory Pre-Start Steps)

### Step 1 — Read the story in full (required for every status)

Before writing any code, regardless of story status, Dev **must** read:

1. User Story, all Acceptance Criteria, Technical Scope, and any linked technical docs
2. All existing comments on the GitHub Issue — PO and TL may have already added context

### Step 2 — Identify and raise questions

After reading, identify anything unclear: scope gaps, ambiguous AC, technical design uncertainties.

- **If questions exist:** Post a comment on the GitHub Issue and **explicitly tag** the right person:
  - Scope or AC questions → tag **PO** (Product Owner)
  - Technical or design questions → tag **TL** (Technical Lead)
- **Do not assume or invent answers** — wait for a response before proceeding
- If an answer is insufficient or raises a new concern, reply in the same comment thread and tag again
- Non-blocking questions should still be posted but do not require a response before proceeding

> **Gate:** Do not begin implementation until all blocking questions have a confirmed answer from PO or TL.

### Step 3 — Start implementation

Once all blocking questions are resolved:

1. **Update story status** — Remove label `status:ready` (or `status:backlog`), add label `status:in-progress`
2. Create your dev branch: `ST-XXXXXX/short-description` (branch off feature branch)
3. Begin implementation

> If the story is complex, follow the design-first rule — refer to section `Design first before Implementation` in `PROJECT_PRIMING.md`.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Update story status by changing the GitHub Issue label at each stage.
- Cannot merge without: TL approval + QA sign-off on dev branch + local tests passing.
- **Do NOT tick Acceptance Criteria** — AC is owned by QA. Ticking AC yourself is a role violation.

See `STORY_STANDARD.md` §4 for the full workflow and gate conditions.

---

## 4. Code Quality & Naming

**Source files:** Use descriptive names. Do NOT use:
- `interface.go`, `helpers.go`, `types.go`, `errors.go`, `utils.go`

✅ Good examples:
- `rule_evaluator.go` — implements RuleEvaluator interface
- `condition_helpers.go` — helpers for conditions
- `evaluation_types.go` — types used in evaluation
- `validation_errors.go` — validation error definitions

**Rule:** Name files after their primary interface/struct; use `snake_case`.

**Story files:** Stories are GitHub Issues — title format `[ST-XXXXXX][FEATURE] Title In Title Case`. No `.md` story files.

---

## 5. Testing & Verification

**All applicable checks must pass before opening a PR — no exceptions:**

| Check | Applies when | Command | Pass condition |
|---|---|---|---|
| Build | Always | `{build-command}` | Zero errors |
| Unit tests | Always | `{test-command}` | All tests pass |
| API spec lint | Spec changed (`docs/api/{api-spec-file}` or lint config) | `{api-lint-command}` | Zero errors |
| API spec drift check | Spec changed and code generation is used | `{code-gen-command}` then `git diff --exit-code {generated-file-path}` | No diff — generated file matches spec |
| Integration test run | Source code changed | `{integration-test-command}` (start sandbox first) | All assertions pass |

If any applicable check fails, fix it before creating the PR. Do not open a draft PR expecting QA or TL to catch failures — those are Dev's responsibility.

Include a one-line test result note in the PR description (e.g., "`{test-command}` — PASS · integration tests — PASS").

**Pre-merge checklist:**
1. All applicable checks above pass locally
2. Source files follow naming convention above
3. PR created with title `[ST-XXXXXX][FEATURE] Story title`
4. TL has reviewed and approved PR
5. QA has tested on the dev branch and ticked all AC
6. Update story label to `status:done` after merge

---

## 6. Git Workflow

- **Dev branch:** `ST-XXXXXX/short-description` (branch off feature branch)
- **PR title:** `[ST-XXXXXX][FEATURE] Story title`
- **PR description:** Must include `Closes #<issue-number>` (or `Refs #<issue-number>` if not closing) so GitHub links the PR to the story automatically
- **Wait for TL approval** before merging dev branch to feature branch
- No merge without TL code review

**Story comment after opening PR (mandatory):**

After creating the PR, post a short comment on the GitHub Issue to notify the team:

> "PR #XX opened for review — [brief one-line summary of what was implemented]."

Tag **TL** in the comment to request review.

**Post-QA Merge Sync (mandatory after QA passes):**

After QA sign-off, when merging the dev branch PR into the feature branch (or master):

1. Merge the PR: `gh pr merge <number> --merge`
2. Switch local branch to the target branch: `git checkout <feature-branch>`
3. Pull from remote to sync: `git pull origin <feature-branch>`
4. Confirm the merge commit is present locally before reporting completion to the orchestrator

> **Gate:** Do not signal merge completion until the local branch is switched and synced.

**Commit Message Rules:**
- Format: `<type>(<scope>): <subject>` — Conventional Commits
- Subject: imperative mood, ≤ 50 characters (`Add …` not `Added …`)
- Body (when needed): explain *why*, wrap at 72 characters per line
- Footer: always include `Story: ST-XXXXXX`; add `BREAKING CHANGE:` if applicable
- See `docs/wiki/Development_Standards.md §2` for the full type list and a complete example

---

## 7. Reporting & Blockers

- Keep working record updates short and fact-based (file paths, PR #s, story IDs, commits)
- Post blockers immediately as a comment in the GitHub Issue; tag TL or PO as appropriate
- **When starting a session:** Read your working record, then **sync story statuses with GitHub** — check the current label on each in-progress or recently completed story and correct the record before reporting status
- **Working record retention:** Delete entries older than 3 days before writing today's entry — the record must never exceed 3 days of history

---

## 8. Document Placement
- When you update or create project documents, use the current feature-doc structure. Refer section `## 4. Internal Project Documents` in project priming document.

---

## 9. Stage-Transition Commit (mandatory before handoff)

Before signaling completion to the orchestrator and handing off to the next stage, Dev **must** commit any updates to working record or memory files made during the session:

- **What to commit:** Changes to your Working Record or any agent memory files
- **Commit message:** `Agent: <short description>` — total length under 50 characters
- **Examples:** `Agent: Update working record`, `Agent: Update dev memory`
- Push the commit before reporting stage completion to the orchestrator

> **Gate:** Do not signal stage completion until the commit is pushed.

---

## 10. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

When you cannot run tests, start the sandbox, or execute scripts due to an environment or tooling error, follow these steps in order.

**Step 1 — Check memory first**
Before diagnosing, scan `Developer_Memory.md` for a matching entry under `## Troubleshooting Facts`. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix**
If no match, identify the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory)**
After resolving the blocker, record the fix in `Developer_Memory.md` under `## Troubleshooting Facts` before resuming work. Use the format defined in `developer_instructions.md`.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.

**Applies to:** `{test-command}` fails to run · Docker / sandbox fails to start or become healthy · integration test suite cannot connect · test script errors · CI YAML errors · auth/credential failures in test scripts

---

## 11. Peer Review (when Dev acts as reviewer for a TL-implemented story)

When the orchestrator assigns Dev as peer reviewer, follow `STORY_STANDARD.md` §12 Reviewer Gate, then apply this checklist:

**Review checklist:**
- Verify the PR follows naming conventions, commit message format, and test coverage rules from §4–§5
- Check for obvious logic errors, missing error handling at system boundaries, and security issues
- Post inline PR comments for required changes; post a brief notify comment on the GitHub Issue
- When all criteria pass, post approval as a comment on the PR (GitHub blocks self-approval — use `gh pr comment`)

---

## Version

**Version:** 2.6 — §11 Peer Review: removed redundant CI gate line; section now defers to STORY_STANDARD.md §12  
**Previous:** 2.4 — §5 Testing: spec lint and drift check required when API spec changes  
**Created:** 2026-04-24
