# Developer Rules

**Applies to:** Developer agent  
**Reference from:** `.claude/agents/developer_instructions.md`

---

## 1. Mandatory Reading Before Any Implementation

Before writing a single line of code on any story, Dev **must** read:

| Document | Path |
|---|---|
| Story Standard (Dev) | `.claude/agents/rules/Story_Standard_Dev.md` |

The key Development Standards rules are already embedded in §4–§6 of this document (naming, testing, git workflow). Only read `docs/wiki/Development_Standards.md` if you encounter a specific convention question not covered here.

> **Gate:** Do not begin implementation until `Story_Standard_Dev.md` has been read in the current session.

---

## 2. Before Starting a Story (Mandatory Pre-Start Steps)

### Step 1 — Read the story in full (required for every status)

Before writing any code, regardless of story status, Dev **must** read:

1. User Story, all Acceptance Criteria, Technical Scope, and any linked technical docs
2. All existing comments on the GitHub Issue — PO and TL may have already added context
3. **If the story modifies or appends to an existing file:** read that file now. While reading, note any stale placeholders, forward references, or superseded instructions that the new implementation will make incorrect — fix them as part of your implementation, not as a separate task.

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

**Clean Code (source code stories only):**

If the story involves writing or modifying source code files, read before writing any code:
- `.claude/agents/rules/Clean_Code_Rules.md`

Skip for documentation, API spec, Dockerfile, docker-compose, migration SQL, or config-only stories.

**For Clean Code or refactor stories** (title or scope contains "Clean Code", "refactor", or "violation"): read `Clean_Code_Rules.md` **in full** before touching any file — do not limit reading to chapters that appear relevant by violation label. Chapter scope is not always obvious from violation names alone.

**Design-first rule — check this before writing any code or tests:**

If the story is complex (8+ points, multiple layers, data model changes, third-party integration, security-sensitive logic, or breaking API contract), draft a design and post it as a GitHub Issue comment for TL review. Tag **TL** in the comment. TL approval is confirmed when TL replies with **"Design approved"**. Do not proceed until that exact phrase appears.

> If the story is complex, follow the design-first rule — refer to `Project_Priming.md` §Design First.

**Mid-implementation consultation (when a question surfaces during implementation):**

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

**Live user instruction conflicts (mandatory rule during implementation):**

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread (by PO, TL, or the user themselves), the live instruction takes precedence. When this happens:

1. Acknowledge the conflict explicitly — state what the prior decision was and what the new instruction is
2. Proceed with the live instruction
3. Document the override in the PR description so the reviewer understands why the prior decision was not followed

Do not silently follow the old decision, and do not block awaiting re-confirmation — the user's live instruction is the authoritative signal.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Update story status by changing the GitHub Issue label at each stage.
- Cannot merge without: TL approval + QA sign-off on dev branch + local tests passing.
- **Do NOT tick Acceptance Criteria** — AC is owned by QA. Ticking AC yourself is a role violation.

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. Code Quality & Naming

**Source files:** Use descriptive names. Do NOT use generic names:
- `utils`, `helpers`, `types`, `errors`, `interface`

✅ Good examples (named after primary responsibility):
- `rule_evaluator` — implements the rule evaluation logic
- `condition_parser` — parses condition expressions
- `policy_validator` — validates policy input
- `auth_errors` — defines auth-specific error types

**Rule:** Name files after their primary interface/struct/responsibility; use the project's naming convention.

**Shared helper scope rule:** When introducing or modifying a helper used by more than one handler or module, identify all callers before writing the change. If the modification alters behavior for existing callers (e.g., stricter validation, new required parameter), document the blast radius in the PR description and confirm with TL before proceeding — do not assume a broader change is safe.

**Caller-trace rule:** Before changing a function/method signature, return type, type name, or extracting a concrete type into an interface, trace all callers first (use `grep -rn "FuncName" .` or Grep tool). Document the affected call sites in the PR description. Do not make any such change without confirming every caller is updated.

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
3. **For rename/refactor stories** (story title or scope contains "rename", "refactor", or changes a function/class/constant name): run `grep -rn "<old-name>" docs/` and update any stale references found before opening the PR
4. PR created with title `[ST-XXXXXX][FEATURE] Story title`
5. TL has reviewed and approved PR
6. QA has tested on the dev branch and ticked all AC
7. Update story label to `status:done` after merge

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

Commit agent memory file changes before signaling stage completion — see `.claude/agents/rules/Agent_Common.md §6`.

---

## 10. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker (tests won't run, sandbox won't start, automation runner cannot connect, script/CI/auth errors), follow the check-memory → fix → record-to-memory protocol in `.claude/agents/rules/Agent_Common.md §3`.

---

## 11. Peer Review (when Dev acts as reviewer for a TL-implemented story)

When the orchestrator assigns Dev as peer reviewer, follow `Story_Standard_Dev.md` §12 Reviewer Gate, then apply this checklist:

**Review checklist:**
- Verify the PR follows naming conventions, commit message format, and test coverage rules from §4–§5
- Check for obvious logic errors, missing error handling at system boundaries, and security issues
- Post inline PR comments for required changes; post a brief notify comment on the GitHub Issue
- When all criteria pass, post approval as a comment on the PR (GitHub blocks self-approval — use `gh pr comment`)

---

## Version

**Version:** 2.6 — §11 Peer Review: removed redundant CI gate line; section now defers to Story_Standard.md §12  
**Previous:** 2.4 — §5 Testing: spec lint and drift check required when API spec changes  
**Created:** 2026-04-24
