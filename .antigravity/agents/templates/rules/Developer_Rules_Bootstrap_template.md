# Developer Rules — Bootstrap

**Applies to:** Developer agent
**Reference from:** `.antigravity/agents/developer_instructions.md`
**Purpose:** The whole of the Developer's bootstrap-tier rules — everything that is true on *every* Dev spawn regardless of what the task is. Read this file in full at step 3 of `Agent_Common_Bootstrap.md §1`. Read nothing else from the Developer rules set until a trigger in §12 actually fires.

---

## 1. Mandatory Reading Before Any Implementation

Before writing a single line of code on any story, Dev **must** read:

| Document | Path |
|---|---|
| Story Standard (Dev) | `.antigravity/agents/rules/Story_Standard_Dev.md` |

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
3. **Verify the branch switch before committing anything** — run `git branch --show-current` and confirm it prints the dev branch name, not `main`/`master`/the feature branch. Do not make the first commit until this check passes.
4. Begin implementation

**Clean Code (source code stories only):**

If the story involves writing or modifying source code files, read before writing any code:
- `.antigravity/agents/rules/Clean_Code_Rules.md`

Skip for documentation, API spec, Dockerfile, docker-compose, migration SQL, or config-only stories.

**Logging Standard (source code stories only):**

If the story involves writing or modifying log statements, read before writing any code:
- `.antigravity/agents/rules/Logging_Standard.md`

Skip for documentation, API spec, Dockerfile, docker-compose, migration SQL, or config-only stories.

**UI Prototype reference (UI-bearing repos only):**

If this repo has (or is paired with) a `-ui-prototype` companion repo, read `.antigravity/agents/rules/UI_Prototype_Rules.md` before implementing any screen with a prototype counterpart — it governs what may (and must not) be reused from the prototype.

**For Clean Code or refactor stories** (title or scope contains "Clean Code", "refactor", or "violation"): read `Clean_Code_Rules.md` **in full** before touching any file — do not limit reading to chapters that appear relevant by violation label. Chapter scope is not always obvious from violation names alone.

**Design-first rule — check this before writing any code or tests:**

If the story is complex (8+ points, multiple layers, data model changes, third-party integration, security-sensitive logic, or breaking API contract), draft a design and post it as a GitHub Issue comment for TL review. Tag **TL** in the comment. TL approval is confirmed when TL replies with **"Design approved"**. Do not proceed until that exact phrase appears.

> If the story is complex, follow the design-first rule — refer to `Project_Priming.md` §Design First.

Scenario-conditional rules — mid-implementation consultation and live user instruction conflicts — are `Developer_Rules_Read_On_Demand.md` §10 and §11. Fetch only if that scenario actually occurs.

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

**Story files:**
- **GitHub mode:** Stories are GitHub Issues — title format `[ST-XXXXXX][FEATURE] Title In Title Case`. No `.md` story files are created or tracked.
- **Strict mode:** Stories are `.md` files under `.antigravity/agents/docs/stories/` (filename: `ST-XXXXXX.md`). No GitHub Issues. See `Strict_Mode_Story_Guide.md` for the full format and lifecycle.

---

## 5. Testing & Verification

**Missing credential blocks a check — do not substitute a dummy value and call it verified.** If a required secret/credential is unavailable in your environment, follow `Agent_Common_Read_On_Demand.md §6` (Credential-Gated Verification) — stop and report, do not self-approve the skip.

**All applicable checks must pass before opening a PR — no exceptions:**

| Check | Applies when | Command | Pass condition |
|---|---|---|---|
| Build | Always | `{build-command}` | Zero errors |
| Unit tests | Always | `{test-command}` | All tests pass |
| Lint / format | Any source or test file changed — **including test files you just authored yourself**, not only production source | `{lint-command}` | Zero errors |
| API spec lint | Spec changed (`docs/api/{api-spec-file}` or lint config) | `{api-lint-command}` | Zero errors |
| API spec drift check | Spec changed and code generation is used | `{code-gen-command}` then `git diff --exit-code {generated-file-path}` | No diff — generated file matches spec |
| Integration test run | Source code changed | `{integration-test-command}` (start sandbox first) | All assertions pass |

**Spec-first rule — when story has an API Spec Reference section:**
When the story's **API Spec Reference** section names one or more endpoints, update the API spec **before** writing any implementation code. Run codegen immediately after the spec update and commit both as the first working commit on the branch. This ensures the spec is the source of truth and prevents a spec-update CR cycle.

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
- **GitHub mode:** Format: `<type>(<scope>): <subject>` (Conventional Commits). Subject: imperative mood, ≤ 50 characters. Body (when needed): explain *why*, wrap at 72 characters. Footer: always include `Story: ST-XXXXXX`. See `docs/wiki/Development_Standards.md §2` for the full type list.
- **Strict mode:** Format: `<primary-id> [<secondary-id>]: <message>` — see `Strict_Mode_Story_Guide.md §Commit Message Format` for the complete spec. No `Story:` footer, no Conventional Commits type prefix.
- **Subject-line length is a non-blocking style nit.** The ≤ 50-character limit covers the **entire** header line (`<type>(<scope>): <subject>`), not just the text after the colon. A reviewer who finds a length violation notes it in a PR comment but must **not** withhold approval, request changes, or trigger a fix-loop over length alone. Everything else in the commit-message convention (type/scope format, imperative mood, `Story:` footer, body wrap) remains blocking.
- **Docs-only pushes skip CI (github mode):** when every file in the push is non-code (`docs/**`, `*.md`, `.antigravity/agents/**`), add `[skip ci]` on its own line in the head commit's message body — CI cannot be affected by these files and must not run for them. Never use `[skip ci]` on any push that contains code, config, or build-file changes.

---

## 12. On-Demand Rules — Routing Table

§1–§6 above are loaded at spawn. Nothing in `Developer_Rules_Read_On_Demand.md` is. When a trigger below fires, fetch **only** the named section — locate it with grep, not the whole file.

| Trigger | Fetch |
|---|---|
| Blocked on a story and reporting it | `Developer_Rules_Read_On_Demand.md §7` (Reporting & Blockers) |
| Creating or updating a project document | `Developer_Rules_Read_On_Demand.md §8` (Document Placement) |
| Orchestrator assigns you as peer reviewer for a TL-implemented story | `Developer_Rules_Read_On_Demand.md §9` (checklist) and `§12` (full reviewer procedure) |
| A question surfaces mid-implementation | `Developer_Rules_Read_On_Demand.md §10` (Mid-Implementation Consultation) |
| A live user instruction contradicts a prior decision recorded in the issue thread | `Developer_Rules_Read_On_Demand.md §11` (Live User Instruction Conflicts) |
| A post-Done bug (hotfix) | `Developer_Rules_Read_On_Demand.md §13` |
| Signaling stage completion to the orchestrator, or you changed a memory file this session | `Agent_Common_Read_On_Demand.md §5` (Stage-Transition Commit) — mandatory before handoff |
| A tooling/environment blocker | First scan your own `## Troubleshooting Facts` for a recorded fix; fetch `Agent_Common_Read_On_Demand.md §2` only for the diagnose-and-record-back procedure |

> Triggers shared by all six roles that are not restated here — writing a memory fact, the end-of-work retro, credential-gated verification — are routed by `Agent_Common_Bootstrap.md §5`.

---

## 13. Always-On

- Keep working record updates short and fact-based (file paths, PR #s, story IDs, commits)
- **When starting a session:** Read your working record, then **sync story statuses with GitHub** — check the current label on each in-progress or recently completed story and correct the record before reporting status
- **Working record retention:** Delete entries older than the 3 most recent story entries before writing a new one — the record must never exceed 3 story entries (see `Agent_Common_Bootstrap.md §1` for the char cap and snapshot format)

---

## Version

**Version:** 3.1 — §12 routing table: peer-reviewer row now also cites `Developer_Rules_Read_On_Demand.md §12` (full reviewer procedure), and a new hotfix row cites `§13` — both sections added there by the `Story_Standard_Dev_template.md` trim (devkit issue #133 / ST-000134).
**Previous:** 3.0 — Split into a bootstrap tier (this file: §1–§6, unconditional content read on every spawn) and an on-demand tier (`Developer_Rules_Read_On_Demand.md`: §7 through §11, scenario-conditional content fetched only on trigger), mirroring the boundary already validated on the devkit's own team (`working/rules/Developer_Rules_Bootstrap.md` / `Developer_Rules_Read_On_Demand.md`). Mid-implementation consultation and live user instruction conflicts (previously inline in §2) and Peer Review (previously section 11) moved out; sections 9/10's prior pointer-only content (Stage-Transition Commit, Troubleshooting Protocol) retired in favor of the routing table above, since `Agent_Common_Bootstrap.md §5` already covers both universally.
**Previous:** 2.11 — §2: one-line trigger pointer to `Logging_Standard.md` for source code stories (ST-000023)
**Created:** 2026-04-24
