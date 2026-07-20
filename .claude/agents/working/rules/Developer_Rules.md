# Developer Rules

**Applies to:** Developer agent  
**Reference from:** `.claude/agents/working/instructions/developer_instructions.md`

---

## 1. Mandatory Reading Before Any Implementation

Before writing a single file on any story, Dev **must** read:

| Document | Path |
|---|---|
| Story Standard (Dev) | `.claude/agents/working/rules/Story_Standard_Dev.md` |

> **Gate:** Do not begin implementation until `Story_Standard_Dev.md` has been read in the current session.

---

## 2. Before Starting a Story (Mandatory Pre-Start Steps)

### Step 1 — Read the story in full

Before writing any file, regardless of story status, Dev **must** read:

1. User Story, all Acceptance Criteria, Technical Scope, and any linked technical docs
2. All existing comments on the GitHub Issue — PO and TL may have already added context
3. **If the story modifies or appends to an existing file:** read that file now. While reading, note any stale placeholders, forward references, or superseded instructions that the new implementation will make incorrect — fix them as part of your implementation, not as a separate task.

### Step 2 — Identify and raise questions

After reading, identify anything unclear: scope gaps, ambiguous AC, technical design uncertainties.

- **If questions exist:** Post a comment on the GitHub Issue and **explicitly tag** the right person:
  - Scope or AC questions → tag **PO** (Product Owner)
  - Technical or design questions → tag **TL** (Technical Lead)
- **Do not assume or invent answers** — wait for a response before proceeding

> **Gate:** Do not begin implementation until all blocking questions have a confirmed answer from PO or TL.

### Step 3 — Start implementation

Once all blocking questions are resolved:

1. **Update story status** — Remove label `status:ready`, add label `status:in-progress`
2. Create your dev branch: `ST-XXXXXX/short-description` (branch off main)
3. Begin implementation

**Design-first rule — check this before writing any files:**

If the story is complex (new workflow stage, major template restructure, new devkit command, or breaking change to `init project` behavior), draft a design and post it as a GitHub Issue comment for TL review. Tag **TL** in the comment. TL approval is confirmed when TL replies with **"Design approved"**. Do not proceed until that exact phrase appears.

**Mid-implementation consultation (when a question surfaces during implementation):**

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

**Live user instruction conflicts (mandatory rule during implementation):**

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Update story status by changing the GitHub Issue label at each stage.
- Cannot merge without: TL approval + QA sign-off + local checks passing.
- **Do NOT tick Acceptance Criteria** — AC is owned by QA. Ticking AC yourself is a role violation.

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. File Naming

**Template files:** Use descriptive names with `_template` suffix for files under `.claude/agents/templates/`. Strip the suffix when writing to target projects.

**Workflow files:** Use `Title_Case_With_Underscores` — `Sprint_Workflow_template.md`, `Sync_Devkit_Workflow_template.md`.

**`changes.json` format:** New version entries must use the `new`/`modified` key format:
```json
"X.Y.Z": {
  "new": ["<relative-path-to-new-file>"],
  "modified": ["<relative-path-to-modified-file>"]
}
```
Older entries in the file use different formats — ignore them. Always use `new`/`modified` for any entry you write.

**Rules files:** `Title_Case_With_Underscores` — `Developer_Rules_template.md`, `Agent_Common_template.md`.

**General rule:** Name files after their primary purpose. No generic names.

---

## 5. Pre-PR Gate

**Missing credential blocks a check — do not substitute a dummy value and call it verified.** If a required secret/credential is unavailable in your environment, follow `Agent_Common.md §7` (Credential-Gated Verification) — stop and report, do not self-approve the skip.

**All applicable checks must pass before opening a PR — no exceptions:**

| Check | Applies when | Command | Pass condition |
|---|---|---|---|
| Shell script syntax | `.sh` files changed | `bash -n <each changed .sh file>` | Zero errors |
| PowerShell syntax | `.ps1` files changed | `powershell -Command "& { $null = [System.Management.Automation.Language.Parser]::ParseFile('<script>', [ref]$null, [ref]$null) }"` | Zero parse errors |
| CI workflow syntax | `.github/workflows/` changed | Validate YAML structure manually | Correct YAML |
| Docs/markdown only | Docs only changed | N/A | Exempt |

Include a one-line check result note in the PR description (e.g., "bash -n check — PASS on all .sh files").

**CHANGELOG.md rule:** Before opening any PR, add a bullet entry to `CHANGELOG.md` under `## [Unreleased]`. If `CHANGELOG.md` does not yet exist, create it using the standard format (see any existing entry as a template). Never skip this step — the first story that touches the repo is responsible for creating the file if absent.

**Pre-merge checklist:**
1. All applicable checks above pass
2. PR created with title `[ST-XXXXXX][DEVKIT] Story title`
3. `CHANGELOG.md` updated with a bullet entry before opening PR
4. TL has reviewed and approved PR
5. QA has validated all AC on the dev branch
6. Update story label to `status:done` after merge

---

## 6. Git Workflow

- **Dev branch:** `ST-XXXXXX/short-description` (branch off `main`)
- **PR title:** `[ST-XXXXXX][DEVKIT] Story title`
- **PR description:** Must include `Closes #<issue-number>` to link the PR to the story
- **Wait for TL approval** before merging

**Story comment after opening PR (mandatory):**

After creating the PR, post a short comment on the GitHub Issue:
> "PR #XX opened for review — [brief one-line summary of what was implemented]."
Tag **TL** in the comment to request review.

**Post-QA Merge Sync (mandatory after QA passes):**
1. Merge the PR: `gh pr merge <number> --merge`
2. Pull to sync: `git checkout main && git pull origin main`
3. Confirm the merge commit is present locally before reporting completion

**Commit Message Rules:**
- Format: `<type>(<scope>): <subject>` — Conventional Commits
- Subject: imperative mood, ≤ 50 characters
- Footer: always include `Story: ST-XXXXXX`
- **Subject-line length is a non-blocking style nit.** The ≤ 50-character limit covers the **entire** header line (`<type>(<scope>): <subject>`). A reviewer notes a violation in a PR comment but must **not** request changes or trigger a fix-loop over length alone; the rest of the convention remains blocking.
- **Docs-only pushes skip CI:** when every file in the push is non-code (`docs/**`, `*.md`, `.claude/agents/**`), add `[skip ci]` on its own line in the head commit's message body — CI cannot be affected by these files and must not run for them. Never use `[skip ci]` on any push that contains code, config, or build-file changes.

---

## 7. Reporting & Blockers

- Keep working record updates short and fact-based (file paths, PR #s, story IDs, commits)
- Post blockers immediately as a comment in the GitHub Issue; tag TL or PO as appropriate
- **Working record retention:** Delete entries older than 3 days before writing today's entry

---

## 8. Document Placement

When you update or create project documents, use the current structure. Refer section `## 6. Internal Project Documents` in the Project Priming document.

---

## 9. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/working/rules/Agent_Common.md §6`.

---

## 10. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the check-memory → fix → record-to-memory protocol in `.claude/agents/working/rules/Agent_Common.md §3`.

---

## 11. Peer Review (when Dev acts as reviewer for a TL-implemented story)

When the orchestrator assigns Dev as peer reviewer:
- Verify the PR follows naming conventions and pre-PR gate checks from §4–§5 — except commit subject-line **length**, which is a non-blocking nit per §6: note it in a comment, never request changes over it alone
- Check for obvious logic errors or missing content
- **Confirm the CI check actually executed, not just its conclusion**, confirm the cited run's head SHA matches the PR's current head SHA, and diagnose any red required check from its actual failing log — see `Technical_Lead_Rules.md §2` for the full detail (same rules apply to peer review)
- Post inline PR comments for required changes; post a brief notify comment on the GitHub Issue
- When all criteria pass, post approval as a comment on the PR (GitHub blocks self-approval — use `gh pr comment`)

---

## Version

**Version:** 1.3 — §6: docs-only pushes append `[skip ci]` so non-code changes stop triggering CI  
**Previous:** 1.1 — §11: CI-execution/SHA/red-diagnosis bullet added; §5: missing-credential cross-reference  
**Created:** 2026-06-16
