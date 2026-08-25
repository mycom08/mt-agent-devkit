# Product Owner Rules — Read On Demand (Scenario-Conditional)

**Applies to:** Product Owner agent — devkit's own team only (`.claude/agents/working/`). Relocated out of `product_owner_instructions.md` and `Product_Owner_Rules_Bootstrap.md` (formerly `Product_Owner_Rules.md`) 2026-08-20, applying the pattern from issue #123 to the devkit's own agent team first (the distributable `.claude/agents/templates/` role rules are unchanged — a separate story). Renamed from `Product_Owner_Rules_Extended.md` to match `Developer_Rules_Read_On_Demand.md`'s naming convention — see `Bootstrap_OnDemand_Split_Notes.md`. PO's instructions file carried three full task blocks (Story Closure, Refine Sprint, Plan Next Sprint) that each apply only when the orchestrator explicitly assigns that stage — none of the three runs on most PO spawns. §4 (Roadmap Story Drain) is the same shape: it only fires when authoring/updating a roadmap doc, which this repo currently does rarely (non-feature sprints only). Read this file **only when the matching scenario actually occurs** — do not read it as part of the standard Pre-Work Sequence. `product_owner_instructions.md`'s three task headings and `Product_Owner_Rules_Bootstrap.md` §11a each still carry a one-line pointer to their relocated section here.

---

## 1. Story Closure Task (Stage 4)

Triggered from `product_owner_instructions.md`'s Story Closure Task heading. When the orchestrator asks you to close a story, read only:
- `.claude/agents/working/rules/Story_Standard_PO.md` (§14 AC rules, §15 PowerShell safety)
- `.claude/agents/working/rules/Product_Owner_Rules_Bootstrap.md`
- `.claude/agents/working/memory/Product_Owner_Memory.md`

Then execute:
1. Read the full story issue body — review all AC checkboxes
2. Read the QA/TL comment threads to confirm all AC have been verified and passing
3. Tick all AC checkboxes `[x]` in the issue body using `--body-file` (`Story_Standard_PO.md §15`)
4. Remove the current status label, add `status:done`
5. Close the issue: `gh issue close <number> --repo mycom08/mt-agent-devkit`
6. Write your retrospective section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` — read `.claude/agents/working/rules/Agent_Common_Read_On_Demand.md §3` for format; overwrite the `## Product Owner` section only
7. Update your Working Record only if there is a durable fact worth recording

---

## 2. Refine Sprint Task

Triggered from `product_owner_instructions.md`'s Refine Sprint Task heading. When the orchestrator asks you to participate in a **Sprint Refinement**, you have two distinct roles depending on the stage.

### Role A — Answer Scope/AC Questions (Stage 2)
The Developer has posted questions tagged to you on one or more sprint stories. For each story:
1. Read the full comment thread on the GitHub issue
2. Answer every question tagged to **PO** in a reply within the **same comment thread**
3. Follow `Story_Standard.md` §9 comment format; update `**Thread Status:**` to `In Progress` while answering
4. Decisions you make here are binding — if you change or clarify an AC, update the issue body to match
5. When all your questions in a story are answered, note it

### Role B — Final Status Update (Stage 4)
After Dev has confirmed all open points are resolved, check each story in the target sprint:
1. Fetch stories: `gh issue list --repo mycom08/mt-agent-devkit --label "sprint-N" --label "status:backlog" --state open`
2. For each story, check: did Dev post a final comment containing "All open points resolved"?
   - **Yes** → remove label `status:backlog`, add label `status:ready`
   - **No** → leave as `status:backlog`; record the story ID and reason in your report
3. Report to orchestrator
4. Update your Working Record

---

## 3. Plan Next Sprint Task

Triggered from `product_owner_instructions.md`'s Plan Next Sprint Task heading. When the orchestrator asks you to run the **Plan Next Sprint** workflow, read `.claude/agents/working/workflows/Plan_Sprint_Workflow.md` for the full pipeline rules before starting. The orchestrator always passes `feature_name`.

> **Status rule — plan sprint does NOT promote to `status:ready`.** After sprint planning, every story must remain `status:backlog`. Promoting stories to `status:ready` is exclusively the responsibility of the `refine sprint` workflow Stage 4, after implementers confirm all questions are resolved. Never change `status:backlog` to `status:ready` during this task.

### Step 1 — Verify Current Sprint Is Done
- Run `gh issue list --repo mycom08/mt-agent-devkit --label "status:in-progress" --label "status:review" --label "status:testing" --state open`
- If any story is NOT done: report the open story IDs to the orchestrator and stop.

### Step 2 — Select Stories for Next Sprint
1. Run `gh issue list --repo mycom08/mt-agent-devkit --label "status:backlog" --state open`
2. Order by priority label: `Must-Have` first, then `Should-Have`, then `Nice-to-Have`

### Step 3 — Identify Open Questions
For each selected story, check if AC is clear and testable. If questions exist, create `.claude/agents/working/tmp/PO_questions.md` and report to the orchestrator.

### Step 4 — Review Answers and Finalize Plan
After the orchestrator confirms all answers are filled in, verify every `A:` field is complete before proceeding.

### Step 5 — Write Sprint Artifacts
1. Create `docs/sprints/Sprint_{N+1}_Overview.md`
2. Update `docs/plan/Product_Backlog.md`
3. For stories without GitHub Issues: create issues following §5 above — use `--body-file`
   - Labels: `status:backlog` + `sprint-N`
4. For stories that already have GitHub Issues: add `sprint-N` label if missing — **do not change `status:backlog` to `status:ready`**
5. Delete `.claude/agents/working/tmp/PO_questions.md` if it exists
6. Update your Working Record

---

## 4. Roadmap Story Drain (mandatory whenever a roadmap doc is authored or updated)

Triggered from `Product_Owner_Rules_Bootstrap.md §11a` — cited by that section number from `Plan_Sprint_Workflow.md` Stage 1, so keep this section's content in sync with that citation even if renumbered here.

**Applies whenever you author or update a roadmap/planning doc that defines stories ahead of pickup — the Implementation Roadmap or any `*Roadmap*.md` under `docs/feature/<feature_name>/plan/` — in a context where a story tracker already exists** (this devkit repo's own tracker, GitHub Issues in `mycom08/mt-agent-devkit`, always exists; this rule doesn't apply to the Analyst workflow's pre-repo `implementation_roadmap.md`, which has no tracker and no real story IDs yet).

Every story the roadmap defines must become a tracked `status:backlog` issue **at this same moment** — do not defer this to sprint planning, and do not wait for `plan next sprint`/`create stories` to notice it.

1. For each story the roadmap defines (each Phase/theme entry), build the idempotency marker: `**Roadmap Source:** <roadmap-file> :: Phase N :: <story title>`.
2. Check whether a tracked issue already carries this exact marker **before creating anything** — this is what makes re-authoring or updating the same roadmap safe against duplicates; run it for every story on every write, not just the ones you think are new: `gh issue list --repo mycom08/mt-agent-devkit --search "\"<marker from step 1>\" in:body" --state all --json number,body`. Treat the result as a **candidate set, not a verdict**: GitHub's phrase search matches a contiguous token subsequence of the body, not an exact line, so a story whose title is a prefix of another already-drained story's title can return a false match. For each candidate, confirm the marker appears as an **exact, full line** in that issue's body before treating this story as already drained — skip creating it only then. Note: GitHub's search index is eventually consistent, so an issue you created moments earlier in this same pass may not be returned yet — track what you just created directly rather than relying on search to re-find it.
3. If no match, create the tracked issue following §5 above's title/label/`--body-file` conventions, with the usual `**Roadmap Phase:** Phase N — <theme>` body line and `phase-N` label already used for roadmap-sourced stories (see `Plan_Sprint_Workflow.md` Stage 4) — those are your phase-reference tag (AC2). Add the new marker line from step 1 verbatim in the body too (alongside `**Phase:**`/`**Story Points:**`/`**Priority:**`/`**Assigned:**`) — that one exists purely for the idempotency check in step 2, not as a human-facing phase tag.
4. **Verification (idempotent re-run):** re-running steps 1–3 against an unchanged roadmap must return an existing match at step 2 for every story and create zero new issues — this is the mechanism that satisfies "re-authoring the same roadmap does not create duplicates."

> This is separate from, and happens earlier than, `Plan_Sprint_Workflow.md` Stage 1's reconciliation backstop. That backstop exists only to catch drift if a roadmap somehow got out of sync with tracked issues despite this rule (e.g. a manual edit made outside your own workflow) — it is not a substitute for draining at authoring time.

---

## 5. Story Creation Template

Triggered from `Story_Standard_PO.md §13`. Read before your first `gh issue create`/`gh issue edit --body-file` of the session.

**Issue title:** `[ST-XXXXXX][DEVKIT] Clear Title`
**GitHub Assignee:** (Optional — a GitHub user account; may be left unset in agent-driven workflows)

**Labels:** `status:backlog`, `sprint-N`
**Labels — bug/defect story:** `status:backlog`, `bug`, `sprint-N`

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

> **Bug/defect stories** (carry the `bug` label): insert a `## Reproduction` section immediately after `## Acceptance Criteria` (before `## Technical Scope`):
> ```markdown
> ## Reproduction
>
> **Repro Command:** [exact command/test to run verbatim, or `unknown`]
> **Expected:** [what should happen]
> **Actual:** [what actually happens — the observed defect]
> ```
> The Bug Reproduction Pre-Flight step (`Shared_Pipeline_Stages.md`, runs ahead of Stage 0) executes `Repro Command` verbatim before any implementer is spawned — it never parses AC prose to derive a command. If `Repro Command` is absent or `unknown`, pre-flight is skipped and Stage 1 proceeds normally (the implementer reproduces as part of its own work, same as before this convention existed).

**Porting an already-validated pattern:** if this story replicates a split, refactor, or pattern already implemented and validated elsewhere in the repo (a prior story, a reference commit), name the exact reference commit SHA and/or file(s) to model in `Technical Scope` — not just the target file names or a prose description of the desired end state. An implementer given only the outcome has to reverse-engineer the actual boundary (which content moved where, section renumbering, deliberate gaps) via git archaeology before writing anything (ST-000132 retro).

**Writing AC for a devkit workflow stage (devkit-internal, no target-project equivalent):**
- **State detection in terms of what's actually on disk at that stage, not a downstream concept.** A stage that runs before a later pipeline boundary exists (e.g. Analyst Stage 2a runs before Build Software's repo-splitting) cannot gate on that downstream concept ("any repo's tech stack") — phrase the AC against the artifacts genuinely available at that point (e.g. "the spec names a UI-bearing surface"), or the Developer has to reword it mid-design.
- **When two same-sprint stories restructure the same workflow section, name the land order in Technical Scope.** Don't rely on a Developer-initiated cross-reference comment to surface the sequencing question — state which story lands first and how the sections compose once both are merged.

---

## Version

**Version:** 1.2 — Renamed from `Product_Owner_Rules_Extended.md` to `Product_Owner_Rules_Read_On_Demand.md`, matching `Developer_Rules_Read_On_Demand.md`'s naming convention (no content change) — see `Bootstrap_OnDemand_Split_Notes.md`.
**Previous:** 1.1 — Added §5 (Story Creation Template), relocated from `Story_Standard_PO.md` §13 per devkit issue #133 (extends the #123 pattern to the Story_Standard views).
**1.0:** (created 2026-08-20, split out of `product_owner_instructions.md` and `Product_Owner_Rules.md` v1.2 per devkit issue #123).
