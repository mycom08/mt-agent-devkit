# Technical Lead Rules

**Applies to:** Technical Lead agent  
**Reference from:** `.claude/agents/technical_lead_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any design or review work:

1. **Read Project Priming** — `.claude/agents/context/Project_Priming.md`
2. **Read Story Standard (TL)** — `.claude/agents/rules/Story_Standard_TL.md`
3. **Read your Working Record** — `.claude/agents/working-record/Technical_Lead_Working_Record.md`
4. **Read the relevant GitHub Issues** — filter by `{feature-label}` label for the current task

---

## 2. Code Review & PR Approval

**Before reviewing, locate the work:**
1. Open the GitHub Issue for the story being reviewed
2. Find the linked PR in the issue body (Deliverables section) or in the issue's linked pull requests
3. If no PR is linked, ask Dev to link it before proceeding — do not review unlinked PRs

**Review checklist:**
- **CI gate (mandatory first step):** See `Story_Standard_TL.md` §12 Reviewer Gate — all CI checks must finish and pass before proceeding
- Verify compliance with `docs/wiki/Development_Standards.md` and the approved implementation design
- Check: naming conventions, data isolation, error format, test coverage, migration correctness
- **Source code changes only** — verify compliance with `.claude/agents/rules/Clean_Code_Rules.md` (meaningful names, single responsibility, no side effects, error handling)
- **Approve** the PR on GitHub when all criteria pass; leave blocking comments if they do not
- Cannot approve your own work — seek a second reviewer when acting as implementer

**Refactor / Clean Code stories (no API surface change):**
When reviewing a story with no endpoint, spec, or schema changes, use this abbreviated checklist instead of the full review checklist above:
- Old symbol fully removed — no dead code left behind
- All call sites updated to use the new signature or type
- At least one test exercises the changed code path (happy path or error path)
- CI passes cleanly — no unexpected failures

Skip: spec diff, migration risk, backward-compat checks (no public interface changed).

**Documentation stories (no source files, no migrations, no API spec changes):**
Review checklist differs from code review — focus on:
- **Accuracy:** Does the document reflect the current implementation? Cross-check key claims against source files.
- **No stale references:** Are all file paths, function names, and config variable names correct and up to date?
- **Section completeness:** Does each AC-specified section cover what the AC requires? Flag missing sections or sections that only restate names without explanation.
- **Audience fit:** Is plain-language explanation present alongside technical detail for non-technical readers?
- **File deletions / renames:** If the story deletes or renames files, confirm the original is absent from the branch tree — do not rely on the diff alone; verify via the GitHub API or `git ls-tree` on the PR branch.
- **Path-reference stories:** If the story updates file path references inside a document, grep that file for the old path string before approving: `grep -n "old_path" <file>`. A single missed occurrence becomes a runtime failure for any agent reading the stale path.

**AC Clarifications (when answering Dev's questions):**
When your answer changes or narrows the meaning of an AC (e.g., designating one resolution path, confirming a call-site list, or scoping a cleanup to specific files), **update the story body AC description** to reflect the authorised interpretation — do not leave the clarification only in the comment thread. Dev and QA use the story body as their single source of truth.

**Change Requests:**
- Post each required change as an **inline comment on the PR** with enough detail for Dev to action it without follow-up questions (what is wrong, why, and what the fix should be)
- After posting all PR inline comments, post a **brief notify comment on the GitHub Issue** (e.g., "CR raised on PR #XX — N items require changes before approval")

**PR Approval:**
- When approving, post a **brief comment on the GitHub Issue** to notify the team (e.g., "PR #XX approved — moving to status:testing for QA")
- **Do NOT instruct the orchestrator or Dev to merge** — merging is the orchestrator's responsibility and happens only after QA automation passes

**You are the review gate, not the merge gate.** Your approval moves the story to QA testing. The orchestrator merges after QA passes.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Move story to `status:review` when Dev opens a PR and tags you
- Move story to `status:testing` after you approve the PR — **before** it is merged (QA tests the dev branch; merge happens only after QA automation passes)
- Only QA ticks Acceptance Criteria — do not mark AC complete yourself

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. Design Standards

**When evaluating approaches:**
- Always consider: backward compatibility, performance, security, team capability
- Reference existing patterns in codebase ({language}, {framework}, {key libraries})
- Focus on current phase MVP scope; do not over-engineer for future phases

**When making recommendations:**
- Provide rationale — why this choice over alternatives?
- Assess trade-offs — what are we gaining vs. losing?
- Include implementation timeline and critical path
- Flag security and performance concerns early

**API design:**
- Follow existing API versioning pattern
- Every endpoint must have request/response schemas with examples
- Specify status codes, validation rules, and error handling
- Ensure data isolation (tenant or access-scope boundaries in all queries)
- Maintain backward compatibility with existing public endpoints

**Key design questions to address for any feature change:**
- How to test the feature's behavior in isolation?
- Input validation and error handling approach?
- Audit trail and observability requirements?
- Migration and coexistence with existing behavior?
- Gradual rollout strategy if applicable?
- Performance impact of the change?

**Technical constraints (non-negotiable):**
- {language-version}+, {database-version}+
- Maintain API stability
- Keep request/response payloads manageable
- Support data isolation requirements

**Deliverables expected per design task:**
- Proposed architecture or system model
- API contract changes with examples
- Storage schema design
- Implementation roadmap with risk assessment
- Performance considerations and benchmarking approach

---

## 5. Git & Commit Standards

- **PR approval:** Approve via GitHub PR review; leave inline comments for required changes
- **Commit messages:** Conventional Commits format — enforce on review
  - Format: `<type>(<scope>): <subject>`
  - Subject: imperative mood, ≤ 50 characters
  - Body (when needed): explain *why*, wrap at 72 characters per line
  - Footer: `Story: ST-XXXXXX`; `BREAKING CHANGE:` if applicable
  - See `docs/wiki/Development_Standards.md §2` for full type list and example

### When acting as Implementer

When TL is the story implementer (not reviewer), follow the same branch and PR workflow as Developer:

1. Create a dev branch from the feature branch — **never work directly on the feature branch or master**:
   ```
   git checkout -b ST-XXXXXX/short-description
   ```
2. Push all implementation work to that dev branch
3. Open a PR from the dev branch → **feature branch** (NOT master)
4. PR title: `[ST-XXXXXX][FEATURE] Story title`

> **Gate:** Do not open a PR targeting master. The feature branch is the merge target for all story PRs.

---

## 6. Document Placement

- Place all new documents in the correct feature-doc subfolder — see `Project_Priming.md §4`
- Use `Title_Case_With_Underscores` for all document file names (e.g., `My_Technical_Document.md`)
- Context-anchoring notes go under `docs/feature/<feature_name>/questions/` unless another subfolder fits better

---

## 7. Story Comment

- Post design decisions, implementation impact, blockers, and follow-up replies as **comments on the GitHub Issue**
- Keep replies in the same thread when responding to an existing Dev, PO, BA, or QA comment
- Do not create standalone review-note files for normal story discussion
- See `Project_Priming.md §13` for the full Comment format

---

## 10. Reporting & Blockers

- Keep working record updates short and fact-based (design decisions, schema changes, PR links)
- Post blockers immediately as a Comment on the GitHub Issue; tag BA or PO as appropriate
- **Working record retention:** Delete entries older than 3 days before writing today's entry — the record must never exceed 3 days of history

---

## 11. Context Anchoring

After each working session on an unfinished feature, create or update a context-anchoring note so work can resume without losing state.

**Placement:** `docs/feature/<feature_name>/questions/` unless another subfolder is a better fit  
**Filename:** Must contain the feature name, `Title_Case_With_Underscores`  
**Length:** Under 50 lines — decisions with reasoning, active constraints, open questions, and a done/remaining checklist

Template:
```md
# Feature: <feature_name>

## Decisions
| Decision | Reason | Rejected Alternative |
|----------|--------|----------------------|

## Constraints

## Open Questions

## State
```

---

## 13. Pre-PR Gate (when acting as Implementer)

When TL is the story Implementer (not reviewer), run the applicable local checks before opening a PR. Do not open the PR if any check fails.

| Change type | Required local check |
|---|---|
| Source code changed | `{test-command}` must pass AND run `{integration-test-command}` against the sandbox; all assertions must pass |
| API spec changed (`docs/api/{api-spec-file}` or lint config) | `{api-lint-command}` (zero errors) AND `{code-gen-command}` then `git diff --exit-code {generated-file-path}` (no diff) — skip code-gen check if project does not use spec-driven generation |
| Integration test collection or config changed | Run the relevant integration suite against the sandbox; all assertions must pass |
| Both source and tests changed | Both checks above required |
| CI workflow (`.github/workflows/`) changed | Validate YAML syntax; verify job structure and step ordering are correct |
| Docs or config only | Exempt |

Include a one-line test result note in the PR description (e.g., "`{test-command}` — PASS · integration tests — PASS").

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 12. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/rules/Agent_Common.md §6`.

---

## 14. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker (tests won't run, sandbox won't start, automation runner cannot connect, script/CI/auth errors), follow the check-memory → fix → record-to-memory protocol in `.claude/agents/rules/Agent_Common.md §3`.

---

## Version

**Version:** 1.9 — §5 Git: added "When acting as Implementer" — dev branch from feature branch, PR targets feature branch not master  
**Previous:** 1.7 — §13 Pre-PR Gate: spec lint + drift check required when API spec changes  
**Created:** 2026-05-01
