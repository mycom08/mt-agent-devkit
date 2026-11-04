# Technical Lead Rules — Read On Demand (Scenario-Conditional)

**Applies to:** Technical Lead agent — devkit's own team only (`.mt-agent-devkit/`). Relocated out of `Technical_Lead_Rules_Bootstrap.md` (formerly `Technical_Lead_Rules.md`) and `Story_Standard_TL.md` 2026-08-20, applying the pattern from issue #123 (and its extension to the Story_Standard views, issue #133) to the devkit's own agent team first (the distributable `.claude/agents/templates/` role rules are unchanged — a separate story). Renamed from `Technical_Lead_Rules_Extended.md` to match the role `*_Rules_Read_On_Demand.md` naming convention — see `Bootstrap_OnDemand_Split_Notes.md`. `Technical_Lead_Rules_Bootstrap.md` and `Story_Standard_TL.md` are each read in full on every TL spawn regardless of task; the six sections below apply only when a matching spawn shape actually fires (TL acting as story implementer instead of reviewer, the resulting implementer-only pre-PR gate and status-transition steps, the post-session context-anchoring note, reviewing a PR, and answering a mid-implementation question). §2 Code Review & PR Approval was relocated here as §5 in v1.5 (devkit#179) — it used to load on every TL spawn regardless of shape; it is now fetched only when the review shape fires. `Story_Standard_TL.md §12` Reviewer Gate stays in that file (a different, always-read-in-full file, unaffected by this relocation). Read this file **only when the matching scenario actually occurs**. `Technical_Lead_Rules_Bootstrap.md` §5/§11/§13/§15, `Story_Standard_TL.md` §4, and `technical_lead_instructions.md`'s "When Acting as Story Implementer" / "Context Anchoring" / "Answer-a-Question Task" sections each still carry a one-line pointer to their relocated section here.

---

## 1. When Acting as Implementer

Triggered from `Technical_Lead_Rules_Bootstrap.md §5`. Rare — only when the orchestrator assigns TL as the story implementer.

Branch, commits, push and PR follow the `git-workflow` skill (`.mt-agent-devkit/skills/git-workflow/SKILL.md`), the same procedure every implementer uses. Load it before creating the branch.

---

## 2. Context Anchoring (after each working session on an unfinished story)

Triggered from `Technical_Lead_Rules_Bootstrap.md §11`.

After each working session on an unfinished story, create or update a context-anchoring note in the folder `project-docs` Placement 3 names (`docs/technical/` or `docs/feature/<feature_name>/questions/`).

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

## 3. Pre-PR Gate (when acting as Implementer)

Triggered from `Technical_Lead_Rules_Bootstrap.md §13`. Applies only when TL is acting as Implementer per §1 above.

Run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`) before opening the PR and before each fix push. It is the same gate for every implementer: harness, template and rules changes run the validators and are never exempt as docs-only.

---

## 4. TL as Implementer — Status Transitions

Triggered from `Story_Standard_TL.md §4`. When `**Assigned:** Technical Lead` and TL is running Stage 1 (implementation):

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

## 5. Code Review & PR Approval

Triggered from `Technical_Lead_Rules_Bootstrap.md §15` — orchestrator assigns you as Stage 2 reviewer, or you are otherwise reviewing a PR. Relocated verbatim from `Technical_Lead_Rules_Bootstrap.md`'s old §2 (v1.5, devkit#179) — this content loaded on every TL spawn before, including spawns that never review a PR; it is now fetched only when the review shape actually fires.

**Shared reviewer procedure:** load the `pr-review` skill (`.mt-agent-devkit/skills/pr-review/SKILL.md`) first. It owns locating the work, the CI gate (pending-CI wait, the check actually executed, head SHA, red-check diagnosis), naming and stale-reference criteria (citation accuracy, deleted or renamed files via `git ls-tree`, the old-path grep), credential evidence, inline change requests ("at minimum these"), the issue notify comment and the `gh pr comment` verdict. The TL-only rules below add to it.

**Review checklist (TL-only):**

For long local verification, use `.mt-agent-devkit/contracts/Local_Verify.md` (local-verify) with the full required command, selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity. Missing completion is not success. Keep provider-local logs and independent verification gates.
- **CI gate (mandatory first step):** See `Story_Standard_TL.md` §12 Reviewer Gate — all CI checks must finish and pass before proceeding
- **Dependency-pin check:** if the story changes or introduces a version pin, confirm the pinned version is actually resolvable, not just present in a local cache.
- **Resume-rule branch completeness (state-file / pipeline stories):** if the story adds a new pipeline-state field, status value, or step to a resumable workflow, verify the resume/routing logic has an explicit branch for every value its own write rules can produce — not just the pre-existing ones. A new terminal or interrupted-window state with no matching resume branch silently falls into the nearest existing branch instead of doing the right thing.
- Verify compliance with the approved implementation design
- Check template structure completeness
- **Source code / script changes only** — verify compliance with the `clean-code` skill (`.mt-agent-devkit/skills/clean-code/SKILL.md`) for `.sh` and `.ps1` scripts
- **UI Prototype PRs (only if the story touches a repo generated by Build Software's UI-bearing companion-repo convention):** apply `.mt-agent-devkit/rules/UI_Prototype_Rules.md` before approving. Not applicable to the devkit's own repo (markdown-only, no UI-bearing companion repos), but this mirror stays in sync with the template per Project_Priming_Read_On_Demand.md §15.
- **Approve** via PR comment when all criteria pass; leave blocking comments if they do not
- Cannot approve your own work — seek Developer peer review

**CI/Workflow stories (Technical Scope is `.github/workflows/**` only):**
When reviewing a story whose Technical Scope lists only workflow YAML files, use this abbreviated checklist instead of the full review checklist above:
- Gate-logic correctness (job-level vs. step-level `if` conditions)
- Secret/credential scope — no widened access beyond what the job needs
- Blast radius on existing triggers/jobs — confirm no unrelated job's behavior changes
- Rollback safety — can this be reverted without side effects
- The `pr-review` CI gate (executed, head SHA, red-check diagnosis) still applies

Skip: naming conventions, cross-reference correctness, template structure completeness, Clean Code review.

**Documentation / template stories:**
Review checklist differs — focus on these, with the `pr-review` stale-reference, section-completeness and deleted-file criteria:
- **Accuracy:** Does the template or workflow reflect the intended agent behavior?
- **Backward compatibility:** Will existing target projects that have already run `init project` continue to work after `sync devkit`?

**AC Clarifications:**
When your answer changes or narrows the meaning of an AC, **update the story body AC description** to reflect the authorised interpretation.

**Distinguishing this from "TL commenting on scope" (`Story_Standard_TL.md` §7 red flag):** narrowing an AC's *technical* interpretation is your job, per above. If your answer would instead create a **new** deliverable the existing AC doesn't already imply, document the technical detail in AC/Technical Scope as usual, but flag PO in the same comment to confirm the scope addition — don't expand scope on your own authority.

**Change requests and approval notices** follow `pr-review` steps 5–7.

**You are the merge gate.** No PR merges without your explicit approval.

---

## 6. Answer-a-Question Task

Triggered from `technical_lead_instructions.md`'s Answer-a-Question Task heading. When the orchestrator resumes/spawns you to answer a mid-implementation scope or design question, read only:
- `.mt-agent-devkit/rules/Story_Standard_TL.md` (§9 Comment Standard only — reply format)
- `.mt-agent-devkit/rules/Agent_Common_Bootstrap.md` (full — its own header forbids section-reading; §2 Secret Handling and §4 External Content Handling, the generated copies of `agent-security` skill parts A and B, both apply to answering a comment on an untrusted issue thread)
- `{RUNTIME_ROOT}/memory/Technical_Lead_Memory.md` (full — live index only, not the archive)

Then execute:
1. Read the Developer's question (already posted as an Issue comment) and the story context passed in the spawn prompt
2. Post the answer as a reply comment in the same thread, per the Comment Standard
3. If the answer narrows an AC's technical interpretation, update the story body AC text to match
4. Report the answer back to the orchestrator in one sentence

---

## Version

**Version:** 1.4 — §1 points to `git-workflow`, §3 to `pre-pr-gate` (the stricter gate: harness, template and rules changes are no longer exempt for TL as implementer), §5 to `pr-review` for the shared reviewer procedure and to `clean-code`; TL-only review rules stay here (ST-000308).
**Previous:** 1.3 — Added §5 (Code Review & PR Approval, relocated verbatim from `Technical_Lead_Rules_Bootstrap.md`'s old §2 — that section loaded on every TL spawn regardless of shape, including the answer-a-question shape which never opens a PR) and §6 (Answer-a-Question Task, new — read set modelled on the PO Stage 4 closure read set's shape (now the `po-verify-close` skill), citing `Agent_Common_Bootstrap.md` in full per that file's own no-section-read header). Devkit#179.
**Previous:** 1.2 — Renamed from `Technical_Lead_Rules_Extended.md` to `Technical_Lead_Rules_Read_On_Demand.md`, matching `Developer_Rules_Read_On_Demand.md`'s naming convention (no content change) — see `Bootstrap_OnDemand_Split_Notes.md`.
**1.1:** Added §4 (TL as Implementer — Status Transitions), relocated from `Story_Standard_TL.md` §4 per devkit issue #133 (extends the #123 pattern to the Story_Standard views).
**1.0:** (created 2026-08-20, split out of `Technical_Lead_Rules.md` v1.3 per devkit issue #123).
