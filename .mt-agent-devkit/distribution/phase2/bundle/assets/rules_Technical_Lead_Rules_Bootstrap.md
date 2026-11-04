# Technical Lead Rules — Bootstrap

**Applies to:** Technical Lead agent
**Reference from:** `.mt-agent-devkit/instructions/technical_lead_instructions.md`
**Purpose:** The whole of TL's bootstrap-tier rules — everything that is true on *every* TL spawn regardless of what the task is (review, design, or acting as implementer all start here). Read this file in full per the Pre-Work Checklist. Read `Technical_Lead_Rules_Read_On_Demand.md` only when a trigger in §13 actually fires.

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any design or review work:

1. **Read Project Priming** — `.mt-agent-devkit/context/Project_Priming.md`
2. **Read Story Standard (TL)** — `.mt-agent-devkit/rules/Story_Standard_TL.md`
3. **Read your Working Record** — `{RUNTIME_ROOT}/working-record/Technical_Lead_Working_Record.md`
4. **Read your Memory** — `{RUNTIME_ROOT}/memory/Technical_Lead_Memory.md`
5. **Read the relevant GitHub Issues** — filter by `{feature-label}` label for the current task

---

## 2. Code Review & PR Approval

**Shared reviewer procedure:** load the `pr-review` skill (`.mt-agent-devkit/skills/pr-review/SKILL.md`) first. It owns locating the work, the CI gate (pending-CI wait, the check actually executed, head SHA, red-check diagnosis), naming and stale-reference criteria (deleted or renamed files via `git ls-tree`, the old-path grep), credential evidence, inline change requests ("at minimum these"), the issue notify comment and the `gh pr comment` verdict. The TL-only rules below add to it.

**Review checklist (TL-only):**

For long local verification, use `.mt-agent-devkit/contracts/Local_Verify.md` (local-verify) with the full required command, selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity. Missing completion is not success. Keep provider-local logs and independent verification gates.
- **CI gate (mandatory first step):** See `Story_Standard_TL.md` §12 Reviewer Gate — all CI checks must finish and pass before proceeding. For a test suite, "actually executed" (`pr-review` step 3) means a non-zero test count.
- **Dependency-pin check:** if the story changes or introduces a cross-module/cross-repo version pin, confirm the pinned version is actually resolvable from the shared registry the CI runner uses (not just present in a local build cache) — e.g. check the publish/release job's own run history for that version.
- **Resume-rule branch completeness (state-file / pipeline stories):** if the story adds a new pipeline-state field, status value, or step to a resumable workflow, verify the resume/routing logic has an explicit branch for every value its own write rules can produce — not just the pre-existing ones. A new terminal or interrupted-window state with no matching resume branch silently falls into the nearest existing branch instead of doing the right thing.
- **Citation accuracy:** before citing a rule as `<file> §N`, open the file and confirm N is the section's actual heading number — a `grep -n` result is a *line* number, not a section number, and a wrong-but-existing section number ships silently past casual review.
- Verify compliance with `docs/wiki/Development_Standards.md` and the approved implementation design
- Check: data isolation, error format, test coverage, migration correctness
- **Source code changes only** — verify compliance with the `clean-code` skill (`.mt-agent-devkit/skills/clean-code/SKILL.md`)
- **Approve** when all criteria pass, with the `pr-review` step 7 verdict; leave blocking comments if they do not
- Cannot approve your own work — seek a second reviewer when acting as implementer

**CI/Workflow stories (Technical Scope is `.github/workflows/**` only, no source/schema/entity files):**
When reviewing a story whose Technical Scope lists only workflow YAML files, use this abbreviated checklist instead of the full review checklist above:
- Gate-logic correctness (job-level vs. step-level `if` conditions)
- Secret/credential scope — no widened access beyond what the job needs
- Blast radius on existing triggers/jobs — confirm no unrelated job's behavior changes
- Rollback safety — can this be reverted without side effects
- The `pr-review` CI gate (executed, head SHA, red-check diagnosis) still applies — this checklist only trims what's structurally inapplicable to a YAML-only diff

Skip: naming conventions, entity/DTO conventions, migration correctness, layering, Clean Code review, domain-specific NFR design questions.

**Refactor / Clean Code stories (no API surface change):**
When reviewing a story with no endpoint, spec, or schema changes, use this abbreviated checklist instead of the full review checklist above:
- Old symbol fully removed — no dead code left behind
- All call sites updated to use the new signature or type
- At least one test exercises the changed code path (happy path or error path)
- CI passes cleanly — no unexpected failures

Skip: spec diff, migration risk, backward-compat checks (no public interface changed).

**Documentation stories (no source files, no migrations, no API spec changes):**
Review checklist differs from code review — focus on these, with the `pr-review` stale-reference and deleted-file criteria:
- **Accuracy:** Does the document reflect the current implementation? Cross-check key claims against source files.
- **Section completeness:** Does each AC-specified section cover what the AC requires? Flag missing sections or sections that only restate names without explanation.
- **Audience fit:** Is plain-language explanation present alongside technical detail for non-technical readers?

**UI Prototype PRs (UI-bearing repos only):**
If this repo has (or is paired with) a `-ui-prototype` companion repo, apply `.mt-agent-devkit/rules/UI_Prototype_Rules.md` before approving any PR for a screen with a prototype counterpart.

**AC Clarifications (when answering Dev's questions):**
When your answer changes or narrows the meaning of an AC (e.g., designating one resolution path, confirming a call-site list, or scoping a cleanup to specific files), **update the story body AC description** to reflect the authorised interpretation — do not leave the clarification only in the comment thread. Dev and QA use the story body as their single source of truth.

**Distinguishing this from "TL commenting on scope" (`Story_Standard_TL.md` §7 red flag):** narrowing an AC's *technical* interpretation to reflect an approved design decision is your job and belongs in the story body, per above. If your answer would instead create a **new** deliverable or requirement that the existing AC doesn't already imply (not just narrow one), still document the technical detail in AC/Technical Scope, but flag PO in the same comment to confirm the scope addition — do not silently expand scope on your own authority.

**Change requests and approval notices** follow `pr-review` steps 5–7. TL-only:
- **Do NOT instruct the orchestrator or Dev to merge** — merging is the orchestrator's responsibility and happens only after QA automation passes

**You are the review gate, not the merge gate.** Your approval moves the story to QA testing. The orchestrator merges after QA passes.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Move story to `status:review` when Dev opens a PR and tags you
- Move story to `status:testing` after you approve the PR — **before** it is merged (QA tests the dev branch; merge happens only after QA automation passes)
- AC checkboxes are ticked by **PO at story closure (Stage 4)**, not by QA or TL — do not mark AC complete yourself

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

- **PR approval:** verdict through `gh pr comment`, never `gh pr review --approve`; inline comments for required changes (`pr-review`, via §2)
- **Commit messages:** the `git-workflow` skill (`.mt-agent-devkit/skills/git-workflow/SKILL.md`) owns the commit convention; enforce it on review. TL-only: add a `BREAKING CHANGE:` footer when applicable

### When acting as Implementer

Rare — only when the orchestrator assigns TL as story implementer. Branch, commits and PR follow `git-workflow` (`Technical_Lead_Rules_Read_On_Demand.md §1`).

---

## 6. Document Placement

Before creating, moving or renaming a document, load the `project-docs` skill (`.mt-agent-devkit/skills/project-docs/SKILL.md`). It owns the path list (`context/Document_Index.md`), naming, and the context-anchoring note folders.

---

## 7. Story Comment

- Post design decisions, implementation impact, blockers, and follow-up replies as **comments on the GitHub Issue**; the `comment` skill (`.mt-agent-devkit/skills/comment/SKILL.md`) owns the format and threading
- Do not create standalone review-note files for normal story discussion

---

## 8. Reporting & Blockers

- Working Record writes follow the `working-record` skill (`.mt-agent-devkit/skills/working-record/SKILL.md`); TL entries record design decisions, schema changes and PR links
- Blockers follow `raise-question` section 4 (`.mt-agent-devkit/skills/raise-question/SKILL.md`); TL tags BA or PO

---

## 9. Context Anchoring

After each working session on an unfinished feature, create or update a context-anchoring note so work can resume without losing state — template and placement rule in `Technical_Lead_Rules_Read_On_Demand.md §2`.

---

## 10. Pre-PR Gate (when acting as Implementer)

Rare — only when acting as Implementer per §5. Run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`), the same gate as every implementer (`Technical_Lead_Rules_Read_On_Demand.md §3` points to it).

---

## 11. Runtime-State Handoff (mandatory before handoff)

Keep agent state local and uncommitted before signaling stage completion — the `handoff` skill owns the rule; your route reads its generated copy, `.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md §5`.

---

## 12. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker (tests won't run, sandbox won't start, automation runner cannot connect, script/CI/auth errors), follow the `troubleshooting` skill's check-memory → fix → record-to-memory protocol; your route reads its generated copy, `.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md §2`.

---

## 13. On-Demand Rules — Routing Table

§1–§12 above are loaded at spawn. Nothing in `Technical_Lead_Rules_Read_On_Demand.md` is. When a trigger below fires, fetch **only** the named section with the `read-section` skill — not the whole file.

| Trigger | Fetch |
|---|---|
| Orchestrator assigns TL as story implementer | The `git-workflow` skill (branch/PR procedure; `Technical_Lead_Rules_Read_On_Demand.md §1` points to it) and `Technical_Lead_Rules_Read_On_Demand.md §4` (status transitions, from `Story_Standard_TL.md §4`) |
| End of a working session on an unfinished story | `Technical_Lead_Rules_Read_On_Demand.md §2` (Context Anchoring) |
| TL is acting as Implementer and about to open a PR | The `pre-pr-gate` skill (`Technical_Lead_Rules_Read_On_Demand.md §3` points to it) |

> Triggers shared by all six roles that are not restated here — writing a memory fact, the end-of-work retro, credential-gated verification — are routed by `Agent_Common_Bootstrap.md §5`. Runtime-State Handoff and Troubleshooting Protocol are already resolved directly by §11/§12 above.

---

## Version

**Version:** 3.1 (see `changes.json` for this file's change history)
**Created:** 2026-05-01
