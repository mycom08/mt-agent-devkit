# Product Owner Rules — Read On Demand (Scenario-Conditional)

**Applies to:** Product Owner agent. `Product_Owner_Rules_Bootstrap.md` is read in full on every PO spawn regardless of task. `product_owner_instructions.md` carries three full task blocks (Story Closure, Refine Sprint, Plan Next Sprint) that each apply only when the orchestrator explicitly assigns that stage — none of the three runs on most PO spawns. §4 (Roadmap Story Drain) is the same shape: it only fires when authoring/updating a roadmap doc. Read this file **only when the matching scenario actually occurs** — do not read it as part of the standard Pre-Work Checklist. `product_owner_instructions.md`'s three task headings and `Product_Owner_Rules_Bootstrap.md` §11a each still carry a one-line pointer to their relocated section here.

---

## 1. Story Closure Task (Stage 4)

Triggered from `product_owner_instructions.md`'s Story Closure Task heading. When the orchestrator asks you to close a story, this is a **lightweight task** — do not read Project_Priming or your Working Record. Read only:
- `{{AGENT_DIR_PREFIX}}/agents/rules/Story_Standard_PO.md` (§14 AC rules); `Agent_Common_Bootstrap.md §6` (PowerShell safety)
- `{{AGENT_DIR_PREFIX}}/agents/rules/Product_Owner_Rules_Bootstrap.md`
- `{{AGENT_DIR_PREFIX}}/agents/memory/Product_Owner_Memory.md`

Then execute:
1. Read the full story issue body — review all AC checkboxes
2. Read the QA/TL comment threads to confirm all AC have been verified and passing

**If `Mode: github`:**
3. Tick all AC checkboxes `[x]` in the issue body using `--body-file` (`Agent_Common_Bootstrap.md §6`)
4. Remove the current status label, add `status:done`
5. Close the issue: `gh issue close <number> --repo {github-org}/{repo-name}`

**If `Mode: strict`:**
3. Edit `**Status:** done` in `{{AGENT_DIR_PREFIX}}/agents/docs/stories/ST-XXXXXX.md`
4. Append a closure entry to the story MD `## Comments` section: `"Story accepted — all AC verified. Closed."`

Then (both modes):
- Write your retrospective section to `{{AGENT_DIR_PREFIX}}/agents/retros/ST-XXXXXX_retro.md` — read `{{AGENT_DIR_PREFIX}}/agents/rules/Agent_Common_Read_On_Demand.md §3` for format; overwrite the `## Product Owner` section only
- Update your Working Record only if there is a durable fact worth recording — skip the update entirely if there is nothing new

---

## 2. Refine Sprint Task

Triggered from `product_owner_instructions.md`'s Refine Sprint Task heading. When the orchestrator asks you to participate in a **Sprint Refinement**, you have two distinct roles depending on the stage.

### Role A — Answer Scope/AC Questions (Stage 2)
The Developer has posted questions tagged to you on one or more sprint stories. For each story:
1. Read the full comment thread on the GitHub issue
2. Answer every question tagged to **PO** in a reply within the **same comment thread** — do not open a new comment for the same topic
3. Follow `Story_Standard.md` §9 comment format; update `**Thread Status:**` to `In Progress` while answering
4. Decisions you make here are binding — if you change or clarify an AC, update the issue body to match
5. When all your questions in a story are answered, note it — you will check completeness in Stage 4

### Role B — Final Status Update (Stage 4)
After Dev has confirmed all open points are resolved, check each story in the target sprint:
1. Fetch stories: `gh issue list --repo {github-org}/{repo-name} --label "sprint-N" --label "status:backlog" --state open`
2. For each story, check: did Dev post a final comment containing "All open points resolved"?
   - **Yes** → remove label `status:backlog`, add label `status:ready`
   - **No** → leave as `status:backlog`; record the story ID and reason in your report
3. Report to orchestrator:
   - Stories moved to `status:ready`
   - Stories remaining `status:backlog` with brief reason (open questions, escalated, no Dev confirmation)
4. Update your Working Record

---

## 3. Plan Next Sprint Task

Triggered from `product_owner_instructions.md`'s Plan Next Sprint Task heading. When the orchestrator asks you to run the **Plan Next Sprint** workflow, execute the following steps in order. Read `{{AGENT_DIR_PREFIX}}/agents/workflows/Plan_Sprint_Workflow.md` for the full pipeline rules before starting.

The orchestrator always passes `feature_name` (a feature name such as `payments`, or `none`). Use it to drive all path and label decisions below.

> **Status rule — plan sprint does NOT promote to `status:ready`.** After sprint planning, every story must remain `status:backlog`. Promoting stories to `status:ready` is exclusively the responsibility of the `refine sprint` workflow Stage 4, after implementers confirm all questions are resolved. Never change `status:backlog` to `status:ready` during this task.

### Step 1 — Verify Current Sprint Is Done
- **Feature sprint** (`feature_name` is set):
  1. Read `docs/feature/<feature_name>/plan/Product_Backlog.md` — identify the sprint marked `🔄 In Progress`
  2. Read its `Sprint_N_Overview.md` — check all story statuses
  3. Run `gh issue list --label "status:done"` and cross-reference: every story in the current sprint must be `status:done`
  4. **One-sprint guard:** check whether `Sprint_{N+1}_Overview.md` already exists in `docs/feature/<feature_name>/plan/`. If it does, report to orchestrator and stop.
- **Non-feature sprint** (`feature_name: none`):
  1. Run `gh issue list --label "status:in-progress" --label "status:review" --label "status:testing" --state open` to identify the active sprint stories
  2. Confirm all are `status:done` before proceeding

**If any story is NOT done:** report the open story IDs to the orchestrator and stop.

### Step 2 — Select Stories for Next Sprint
- **Feature sprint**:
  1. Glob `docs/feature/<feature_name>/plan/*Roadmap*.md` to find the roadmap file; read it for the next sprint's candidate stories and dependency graph
  2. Read `docs/feature/<feature_name>/plan/Product_Backlog.md` — note current status of each candidate
  3. Select stories respecting roadmap dependency order; do not include a story whose dependency is not yet `status:done`
- **Non-feature sprint**:
  1. Run `gh issue list --label "status:backlog" --state open` — these are the candidates
  2. Order by priority label: `Must-Have` first, then `Should-Have`, then `Nice-to-Have`
  3. No roadmap dependency check needed

Apply the sprint capacity limit from `{{AGENT_DIR_PREFIX}}/agents/workflows/Plan_Sprint_Workflow.md`. For each selected story note: ID, title, points, priority, assigned agent role, any AC refinement needed.

### Step 3 — Identify Open Questions
For each selected story, check:
- Is the acceptance criteria clear and testable?
- Are there unresolved technical design decisions? (ask TL)
- Are there unclear business requirements? (ask BA)
- Are there implementation feasibility concerns? (ask Dev)
- Are there testability gaps? (ask QA)

If questions exist, create `{{AGENT_DIR_PREFIX}}/agents/tmp/PO_questions.md` using the format in `{{AGENT_DIR_PREFIX}}/agents/workflows/Plan_Sprint_Workflow.md` and report to the orchestrator which agents must answer. If no questions, skip to Step 4.

### Step 4 — Review Answers and Finalize Plan
After the orchestrator confirms all answers are filled in:
1. Re-read `{{AGENT_DIR_PREFIX}}/agents/tmp/PO_questions.md` — verify every `A:` field is complete
2. If anything is still unclear, report to the orchestrator (do not guess)
3. Proceed to Step 5 only when all information is clear

### Step 5 — Write Sprint Artifacts
- **Feature sprint**:
  1. Create `docs/feature/<feature_name>/plan/Sprint_{N+1}_Overview.md` — follow the format of existing Sprint Overview files exactly
  2. Update `docs/feature/<feature_name>/plan/Product_Backlog.md` — add new sprint section; mark sprint status as `🔲 Planned`
- **Non-feature sprint**: no Sprint Overview file — GitHub issue labels are the only artifact
- For stories without GitHub Issues: create issues following `Story_Standard_PO.md` §13 — use `--body-file` (see `Agent_Common_Bootstrap.md §6` for PowerShell safety rule)
  - **Feature story labels:** `status:backlog` + `feature:<feature_name>` + `phase-N` + `sprint-N`
  - **Non-feature story labels:** `status:backlog` + `sprint-N`
- For stories that already have GitHub Issues: add `sprint-N` label if missing — **do not change `status:backlog` to `status:ready`**
- Delete `{{AGENT_DIR_PREFIX}}/agents/tmp/PO_questions.md` if it exists
- Update your Working Record with what was planned

---

## 4. Roadmap Story Drain (mandatory whenever a roadmap doc is authored or updated)

Triggered from `Product_Owner_Rules_Bootstrap.md §11a` — cited by that section number from `Plan_Sprint_Workflow_Shared_template.md` Stage 1, so keep this section's content in sync with that citation even if renumbered here.

**Applies whenever you author or update a roadmap/planning doc that defines stories ahead of pickup — the Implementation Roadmap or any `*Roadmap*.md` under `docs/feature/<feature_name>/plan/` — in a context where a story tracker already exists** (i.e. `init project` has already run; this rule doesn't apply to the Analyst workflow's pre-repo `implementation_roadmap.md`, which has no tracker yet and no real story IDs).

Every story the roadmap defines must become a tracked `status:backlog` issue/story record **at this same moment** — do not defer this to sprint planning, and do not wait for `plan next sprint`/`create stories` to notice it.

1. For each story the roadmap defines (each Phase/theme entry), build the idempotency marker: `**Roadmap Source:** <roadmap-file> :: Phase N :: <story title>`.
2. Check whether a tracked issue/story already carries this exact marker **before creating anything** — this check is what makes re-authoring or updating the same roadmap safe against duplicates; run it for every story on every write, not just the ones you think are new:
   - **Mode: github** — `gh issue list --repo {github-org}/{repo-name} --search "\"<marker from step 1>\" in:body" --state all --json number,body`. Treat the result as a **candidate set, not a verdict**: GitHub's phrase search matches a contiguous token subsequence of the body, not an exact line, so a story whose title is a prefix of another already-drained story's title can return a false match. For each candidate, confirm the marker appears as an **exact, full line** in that issue's body before treating this story as already drained — skip creating it only then. Note: GitHub's search index is eventually consistent, so an issue you created moments earlier in this same pass may not be returned yet — track what you just created directly rather than relying on search to re-find it.
   - **Mode: strict** — grep `{{AGENT_DIR_PREFIX}}/agents/docs/stories/*.md` for the exact marker line using a whole-line match (e.g. `grep -Fxq "<marker>"` per file, not a plain substring grep, which carries the same prefix-title false-positive risk). A match means this story is already drained — skip it.
3. If no match, create the tracked issue/story:
   - **Mode: github** — follow §5 above's title/label/`--body-file` conventions, with the usual `**Roadmap Phase:** Phase N — <theme>` body line and `phase-N` label already used for roadmap-sourced stories (see `Plan_Sprint_Workflow.md` Stage 4, `Create_Stories_Workflow.md` Step 3) — those are your phase-reference tag (AC2). Add the new marker line from step 1 verbatim in the body too (alongside `**Phase:**`/`**Story Points:**`/`**Priority:**`/`**Assigned:**`) — that one exists purely for the idempotency check in step 2, not as a human-facing phase tag.
   - **Mode: strict** — follow `Create_Stories_Workflow.md` Step 4's strict-mode story-creation steps; set `**Feature:**`/`**Phase:**` from the roadmap entry as usual, and include the marker line from step 1 in the body for the same idempotency purpose.
4. **Verification (idempotent re-run):** re-running steps 1–3 against an unchanged roadmap must return an existing match at step 2 for every story and create zero new issues/records — this is the mechanism that satisfies "re-authoring the same roadmap does not create duplicates."

> This is separate from, and happens earlier than, `Plan_Sprint_Workflow.md` Stage 1's reconciliation backstop. That backstop exists only to catch drift if a roadmap somehow got out of sync with tracked issues despite this rule (e.g. a manual edit made outside your own workflow) — it is not a substitute for draining at authoring time.

---

## 5. Story Creation Template

Triggered from `Story_Standard_PO.md` §13. Read before your first `gh issue create`/`gh issue edit --body-file` of the session.

**Issue title:** `[ST-XXXXXX][FEATURE] Clear Title`
**GitHub Assignee:** (Optional — a GitHub user account; may be left unset in agent-driven workflows)

**Labels — feature story:** `status:backlog`, `feature:<name>`, `phase-N`, `sprint-N`
**Labels — non-feature story:** `status:backlog`, `sprint-N`
**Labels — bug/defect story:** `status:backlog`, `bug`, `sprint-N` (add `feature:<name>` and `phase-N` if the bug is tied to a specific feature)

> Omit the sprint label if the story has not been assigned to a sprint yet. Sprint and backlog stories are not scoped to a feature; use `feature:` and `phase-` labels only when the story is part of a named feature.
> Add `bug` to any story that reports a defect, regression, unexpected system behaviour, or infrastructure failure — even if it also carries a `feature:` label.

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

## API Spec Reference

[Affected endpoints and link to spec file, or "N/A"]

## Technical Scope

[Optional: architecture notes, API changes, database migrations]

## Deliverables

[Filled in after work complete: PR links, commits, artifacts]
```

> **Bug/defect stories** (carry the `bug` label): insert a `## Reproduction` section immediately after `## Acceptance Criteria` (before `## API Spec Reference`):
> ```markdown
> ## Reproduction
>
> **Repro Command:** [exact command/test to run verbatim, or `unknown`]
> **Expected:** [what should happen]
> **Actual:** [what actually happens — the observed defect]
> ```
> The Bug Reproduction Pre-Flight step (`Shared_Pipeline_Stages.md`, runs ahead of Stage 0) executes `Repro Command` verbatim before any implementer is spawned — it never parses AC prose to derive a command. If `Repro Command` is absent or `unknown`, pre-flight is skipped and Stage 1 proceeds normally (the implementer reproduces as part of its own work, same as before this convention existed). **Strict mode** has no label mechanism — the presence of a populated `## Reproduction` section in the story MD is itself the bug-story marker pre-flight checks for.

---

## Version

**Version:** 1.2 — New §1 (Story Closure Task), §2 (Refine Sprint Task), §3 (Plan Next Sprint Task), relocated verbatim from `product_owner_instructions_template.md` (each now a one-line trigger pointer there), catching the template up to the boundary already validated on the devkit's own team (`working/rules/Product_Owner_Rules_Read_On_Demand.md`). Former §1/§2 renumbered to §4 (Roadmap Story Drain)/§5 (Story Creation Template); §4's internal citation to the Story Creation Template section updated to "§5 above".
**Previous:** 1.1 — Added §2 (Story Creation Template), relocated from `Story_Standard_PO_template.md` §13 per devkit issue #133 (ST-000134), extending the same trim already validated on the devkit's own team; §1's internal citation to `Story_Standard_PO.md` §13 repointed to "§2 above" since the content is now co-located in this file.
**Previous:** 1.0 — Split out of `Product_Owner_Rules_template.md` v1.9 (former section 11a's full procedure relocated here as §1; the section 11a heading stays in `Product_Owner_Rules_Bootstrap_template.md` as a pointer since it is cited by number externally), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
