<!-- Included by: templates/github/workflows/Shared_Pipeline_Stages_template.md, templates/strict/workflows/Shared_Pipeline_Stages_template.md -->

<!-- SHARED-START -->
# Shared Pipeline Stages

Used by [Sprint Workflow](Sprint_Workflow.md) and [Start Story Workflow](Start_Story_Workflow.md). Session IDs are maintained by the orchestrator across stages.

---

---

## Stage 0 — Implementer Routing

**Read the story body** to get `**Assigned:**` and classify the story:

**If `Mode: github`:** Run `gh issue view <number> --json body,labels` to read the story body and labels.

**If `Mode: strict`:** Read `.claude/agents/docs/stories/ST-XXXXXX.md` directly.

Store `Implementer` in the pipeline state file. This determines which agent runs Stage 1 and which agent reviews in Stage 2.

| `**Assigned:**` value | Stage 1 agent | Stage 2 reviewer | Stage 3 validator |
|---|---|---|---|
| `Developer` | Developer | Technical Lead | QA |
| `Technical Lead` | Technical Lead | Developer (peer review) | QA |
| `QA` | QA | Technical Lead | Skipped — PO validates AC directly |
| `Business Analyst` | Business Analyst | Technical Lead | QA |

> If the `**Assigned:**` field is missing or contains an unrecognised value, stop and notify the user before proceeding.

**Feature context detection:**

**If `Mode: github`:** Run `gh issue view <number> --json labels --jq '.labels[].name'` and inspect the labels:
- If a label matching `feature:*` exists → extract the feature name; store as `Feature` in pipeline state
- If a label matching `phase-*` exists → extract the phase number; store as `Phase` in pipeline state
- If neither found → store `Feature: none` and `Phase: none`

**If `Mode: strict`:** Read `**Feature:**` and `**Phase:**` fields directly from the story MD. Store both in pipeline state. Also read `**Sprint:**` field and store as `Sprint` in pipeline state.

Pass `Feature` and `Phase` to all agents spawned in Stages 1–3 so they can route to the correct `docs/feature/<Feature>/` and `tests/feature/<Feature>/` paths.

**Story type classification:** Read the story's **Technical Scope** section and classify:
- `Type: non-behavioral` — all files listed are docs, config, YAML, or Markdown; no source code files, no DB migrations, no behavioral API spec changes
- `Type: behavioral` — any source code file, DB migration, or behavioral API change is listed
- If Technical Scope is absent or ambiguous → default to `Type: behavioral`

Store `Type` in the pipeline state file. It controls fast-path routing in Stages 2 and 3.

---

## Stage 1 — Implementation

**Orchestrator pre-spawn: create the retro file skeleton** before spawning the implementer. Use the story ID and title from Stage 0. Write `.claude/agents/retros/ST-XXXXXX_retro.md`:

```markdown
# Retrospective — ST-XXXXXX
**Date:** YYYY-MM-DD
**Story:** <story title>

## Implementer — <role>
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Reviewer — <role>
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## QA
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Product Owner
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Orchestrator
### Observations
*(pending)*
```

Fill in `<role>` from the routing table in Stage 0. If a stage is skipped for this story (e.g., QA is the implementer so no separate QA validation), replace the section body with `*(stage skipped)*`.

1. **Spawn** the agent matching the `Implementer` role (**model: sonnet**)
2. **Immediately write `impl_session: <agentId>` to the state file — do this before any other action after spawning.** Never leave `impl_session` empty after a spawn returns.
3. Agent reads its own instruction files, memory, and rules
4. **Read the story:**
   - **GitHub mode:** Agent reads the assigned story from GitHub (`status:in-progress` or next `status:ready` story via `gh issue view`)
   - **Strict mode:** Agent reads `.claude/agents/docs/stories/ST-XXXXXX.md` directly
5. **Before writing any code or files** → update story status to `in-progress`:
   - **GitHub mode:** update story label to `status:in-progress`
   - **Strict mode:** edit `**Status:** in-progress` in the story MD file
6. **Strict mode — create story branch:**
   Derive branch name from story fields (see `Strict_Mode_Story_Guide.md` §Branch Naming):
   - `git checkout sprint-N-dev` (sprint dev branch must exist — created by Sprint/Start Story workflow pre-step)
   - `git checkout -b story/<external-id>-<slug>` (or `story/ST-XXXXXX-<slug>` if no External ID)
7. **CI/CD check:**
   - **GitHub mode:** if the story's Technical Scope includes any file under `.github/workflows/`, the implementer **must** follow `.claude/agents/rules/CICD_Validation_Guide.md` before opening a PR
   - **Strict mode:** CI gate is skipped entirely — no CI validation required
8. **Deletion pre-check** — if the story involves deleting files (housekeeping, cleanup, or any story whose scope lists files to remove): before executing any `git rm` or file deletion, record the planned deletions, then proceed immediately. This gives the reviewer and user a visible record of what was removed and why.
   - **GitHub mode:** post a comment on the GitHub Issue listing every file planned for deletion
   - **Strict mode:** append a comment entry to the story MD `## Comments` section listing every file planned for deletion
9. Agent implements and updates working record; commits use the format `<external-id> [ST-XXXXXX]: <message>` or `ST-XXXXXX: <message>` (see `Strict_Mode_Story_Guide.md` §Commit Message Format)
10. **After implementation is ready for review** → update story status to `review`:
    - **GitHub mode:** open PR; update story label to `status:review`
    - **Strict mode:** create `.claude/agents/docs/reviews/ST-XXXXXX_review.md` (see `Strict_Mode_Story_Guide.md` §Local Review Record); edit `**Status:** review` in the story MD; append comment entry to `## Comments` noting branch is ready for review
11. Agent writes retro section to `.claude/agents/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
12. **If blocked on external input** → agent follows the **Blocked Story Procedure** below; orchestrator stops the pipeline and notifies the user
13. On completion → proceed to Stage 2

### Stub/TODO Scan & Verification-Only Outcome (implementer executes before step 10)

**Stub/TODO scan (mandatory):** For every file in the story's Technical Scope (and any file the diff touches), grep for stub markers (`TODO`, `FIXME`, "left as", "not part of this scope", "extension point") and unconditional trivial-return patterns (`return Optional.empty()`, `return null`, `return List.of()`, etc.) in methods the story's own AC describes as functional. Any hit must be either implemented in this story, or explicitly recorded — visibly, in the issue thread, not just a code comment — as deferred to a **named, existing or newly-created** backlog story. A stub with no owning story is a blocking finding, not an accepted risk.

**Verification-only outcome (self-certified):** If your diff against the target branch touches nothing but docs/changelog (no source, schema, config, or test files), mark the story `Outcome: verification-only` in the pipeline state file, in addition to your normal completion report. Stage 2/3 still perform one independent spot-check rather than trusting this tag blindly — it must never be used to shortcut a genuine gap. If a reviewer/QA spot-check contradicts the tag, that is treated as an implementer accuracy issue in retro, the same as any other missed AC.

### Mid-Implementation Consultation Procedure (orchestrator executes when Developer reports a question)

When the implementer returns with a mid-implementation consultation report instead of a completion report:

1. **Read the report** — identify `Owner` (TL / PO / both) and the specific `Question`.

2. **Spawn or resume the answering agent(s):**
   - If `Owner` is TL → spawn/resume Technical Lead (**model: sonnet**) with the question and story context
   - If `Owner` is PO → spawn/resume Product Owner (**model: sonnet**) with the question and story context
   - If `Owner` is both → spawn both in parallel (**model: sonnet** for each) (single orchestrator message)

   Spawn prompt must include:
   - Story ID and GitHub Issue number
   - The Developer's exact question and decision needed (from the report)
   - Where the Developer paused (from the report)
   - Instruction: *"The Developer has already recorded the question on the story. Read it, then post your answer on the same story to keep the full decision trail:*
     - ***GitHub mode:** reply as a comment on the GitHub Issue*
     - ***Strict mode:** append a comment entry to the story MD `## Comments` section*
     
     *Then report your answer back to the orchestrator in one clear sentence."*

3. **Collect the answer(s).** If both TL and PO are consulted, wait for both before resuming the Developer.

4. **Resume the implementer** via `SendMessage` to `impl_session` (spawn new if expired). Pass:
   - The answer(s) from TL and/or PO
   - A reminder of where they paused
   - Instruction to continue implementation

5. **Do not change story label** — it remains `status:in-progress` throughout.

6. **Loop limit:** counts toward the story's Impl→Reviewer loop limit if the consultation causes a re-review cycle; does not count otherwise.

> **Distinguish from Blocked Story Procedure:** Use this when the question can be answered by TL or PO from existing context. Use the Blocked Story Procedure only when the answer requires input that no internal agent can provide (external system access, user preference, credentials, etc.).

### Blocked Story Procedure (agent executes when external input is required)

1. Resolve **who to tag** following the lookup order in `.claude/agents/rules/Blocked_Request_Template.md` § Step 1 — if no match is found, report back to the orchestrator to ask the user before proceeding
2. Fill in the template with the resolved name, confirmed items, missing items, and helpful commands
3. Write the filled-in content to `.claude/agents/tmp/blocked_<story-id>.md`
4. Record the block:
   - **GitHub mode:** post the filled-in comment on the story issue; change the story label to `status:blocked`
   - **Strict mode:** append the filled-in content as a comment entry to the story MD `## Comments` section; edit `**Status:** blocked` in the story MD
5. Return to orchestrator: `"Blocked — awaiting external input. Comment posted on story ST-XXXXXX."`

### Orchestrator Observation Check — Stage 1

After the implementer reports completion, append a bullet to `Observations:` for each item that did **not** happen. Prefix each with the category tag.

- `[skipped-step]` Story status updated to `in-progress` before any file was written?
- `[skipped-step]` CHANGELOG.md updated with a bullet entry before opening PR / marking ready for review?
- `[skipped-step]` If story deletes files: deletion plan recorded (GitHub Issue comment or story MD comment) before any `git rm` executed?
- `[skipped-step]` Story status updated to `review` after implementation was ready?
- `[skipped-step]` **Strict mode only:** Story branch created from sprint dev branch before implementation started?
- `[skipped-step]` **Strict mode only:** Review-record MD created at `.claude/agents/docs/reviews/ST-XXXXXX_review.md`?
- `[skipped-step]` **GitHub mode only:** If story touches `.github/workflows/`: passing `ci-validation` run URL present in PR description?
- `[skipped-step]` `impl_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 2 — Review

### Non-behavioral fast path (`Type: non-behavioral`)

**Get the diff:**
- **GitHub mode:** `gh pr diff <PR-number> --repo {github-org}/{repo-name}`
- **Strict mode:** `git diff sprint-N-dev...story/<branch-name>` (branch name from pipeline state)

1. Read each reference file listed in the story's Technical Scope using the Read tool
2. Verify each AC against the diff and reference files:
   - **Every AC confirmed from diff + reference files alone** → record approval:
     - **GitHub mode:** post approval as `gh pr comment` on the PR
     - **Strict mode:** update review-record MD `**Status:** approved` and `## Verdict` section; append approval comment entry to story MD `## Comments`
     → proceed to Stage 3 without spawning a reviewer agent
   - **Any AC requires domain knowledge not derivable from the diff or reference files** (runtime behaviour, architecture, external system specifics) → fall back to the behavioral path below for full TL review
3. If changes are needed, resume Implementer via `impl_session` (spawn new if expired); re-run this fast path on completion

### Behavioral path (`Type: behavioral`)

1. **Spawn** the reviewer agent based on the routing table in Stage 0; save its `agentId` as `reviewer_session`
   - Default: **Technical Lead** reviews (**model: opus**)
   - Exception: if `Implementer` is `Technical Lead` → **Developer** does peer review (**model: sonnet**)
   - If Stage 1 reported `Outcome: verification-only` → right-size effort: read the implementer's cited evidence directly and perform **one** targeted spot-check instead of a full environment re-verification; escalate to full re-verification only if there's a specific reason to distrust the evidence. Default to **model: sonnet** instead of opus for verification-only reviews.
2. Reviewer reads its own instruction files, memory, and rules
3. **Reviewer reviews the implementation:**
   - **GitHub mode:** reviewer reviews PR (use `gh pr comment` — GitHub blocks self-approval via `gh pr review --approve`)
   - **Strict mode:** reviewer reads review-record MD + runs `git diff sprint-N-dev...story/<branch>` + reads changed files; writes notes and verdict to review-record MD; appends summary comment entry to story MD `## Comments`
   - **Stub/TODO re-check:** confirm the implementer's Stage 1 scan was actually done — spot-check for stub markers/trivial-return patterns in AC-functional methods. A hit with no owning backlog story blocks approval (see `Technical_Lead_Rules.md §2` for the full review checklist, including the CI-execution/SHA/red-diagnosis and dependency-pin checks).
4. **If changes requested** → resume Implementer via `SendMessage` to `impl_session` with reviewer feedback (spawn new if expired); on Implementer completion **resume Reviewer via `reviewer_session` to re-review** (spawn new if expired)
5. Reviewer writes retro section to `.claude/agents/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
6. **If approved:**
   - **GitHub mode:** update the story label to `status:testing` — do this immediately, before proceeding to Stage 3. QA tests on the dev branch before merge; the label signals QA to begin
   - **Do NOT execute the Merge Procedure here** — it fires only after QA automation passes (Stage 3 behavioral path step 9). TL approval is not a merge signal
   → proceed to Stage 3

### Orchestrator Observation Check — Stage 2

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` If behavioral path: `reviewer_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 3 — QA Validation

> **Merge gate — behavioral stories:** The Merge Procedure fires only at behavioral path step 9 — after QA confirms automation passes. Do NOT execute it at Stage 3 entry or immediately after Stage 2 approval.

1. **If `Implementer` is `QA`** → skip QA validation; orchestrator executes the **Merge Procedure** below, then proceed to Stage 4

### Non-behavioral fast path (`Type: non-behavioral`)

2. **If Stage 2 fast path approved all ACs** → skip re-verification; record QA sign-off; execute the **Merge Procedure** below; proceed to Stage 4
3. **If Stage 2 used the behavioral path** → read each AC from the story body and the current state of each file listed in Technical Scope:
   - **GitHub mode:** use `gh pr diff` or Read tool
   - **Strict mode:** use `git diff sprint-N-dev...story/<branch>` and Read tool
   - **Every AC confirmed** → record QA sign-off; execute the **Merge Procedure** below; proceed to Stage 4
   - **Any AC requires domain knowledge not derivable from the files** (runtime behaviour, architecture, external system specifics) → fall back to the behavioral path below for full QA agent validation
4. If AC issues found, resume Implementer via `impl_session` (spawn new if expired); re-run this fast path on completion

**Record QA sign-off:**
- **GitHub mode:** post QA sign-off comment on the GitHub Issue
- **Strict mode:** append QA sign-off comment entry to the story MD `## Comments` section; update story `**Status:** testing` → leave as-is until merge completes

### Behavioral path (`Type: behavioral`)

5. **Spawn** QA agent (**model: sonnet**); save its `agentId` as `qa_session`
6. QA reads `qa_instructions.md` + `QA_Memory.md` + `QA_Rules.md`
7. QA validates story acceptance criteria, runs test scenarios, checks regression risk
   - If Stage 1 reported `Outcome: verification-only` → read the implementer's cited evidence and perform **one** targeted spot-check instead of a full environment re-verification; escalate to full re-verification only if there's a specific reason to distrust the evidence. Skip the test-scenario document per `QA_Rules.md §4`'s verification-only exception.
8. **If story AC issues found** → resume Implementer via `SendMessage` to `impl_session` with QA findings (spawn new if expired); on Implementer completion **resume QA via `SendMessage` to `qa_session`** to revalidate (spawn new if expired)
9. **If story AC passed** → QA updates automation coverage for the story then runs the full automation suite to check for regressions (see QA Rules §8–§9)
   - **If automation fails** → QA reports regression failures:
     - **GitHub mode:** as a story comment
     - **Strict mode:** append to story MD `## Comments`
     → resume Implementer via `impl_session` to fix (spawn new if expired); on completion resume QA to revalidate (counts toward loop limit)
   - **If automation passes** → QA writes retro section to `.claude/agents/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back; orchestrator executes the **Merge Procedure** below
10. On merge confirmed → proceed to Stage 4

### Merge Procedure (orchestrator executes directly — no agent spawn)

**If `Mode: github`:**
0. **CI-check gate (mandatory, independent of reviewer sign-off):** run `gh pr checks <PR-number> --repo {github-org}/{repo-name}`. If any check is `fail`, or any check has not yet reached a `completed` state, **abort the merge** — report the failing/pending check(s) to the user/PO instead of proceeding. This runs regardless of what the reviewer's approval comment claims; it is a mechanical backstop, not a re-trust of the reviewer.
1. Get the PR branch name: `gh pr view <PR-number> --repo {github-org}/{repo-name} --json headRefName --jq '.headRefName'`
2. Merge the PR: `gh pr merge <PR-number> --repo {github-org}/{repo-name} --merge`
3. Delete the remote dev branch: `git push origin --delete <branch-name>`
4. Switch local branch to target: `git checkout <target-branch>`
5. Pull to sync: `git pull origin <target-branch>`

> **No-branch-protection note:** on a repo without required-status-checks support (e.g. a private repo without a paid plan), step 0 above is the *only* enforcement that exists — there is no platform backstop to fall back on if it's skipped. Treat it as non-optional baseline pipeline behavior, not best-effort guidance.

**If `Mode: strict`:**
1. Get the story branch name from the pipeline state file (`Story Branch:` field)
2. `git checkout sprint-N-dev`
3. `git merge story/<branch-name> --no-ff -m "Merge ST-XXXXXX: <story title>"`
4. `git branch -d story/<branch-name>`
5. Append comment entry to story MD `## Comments`: `"[YYYY-MM-DD] Orchestrator — merged into sprint-N-dev. Story closed."`
6. Notify user: `"ST-XXXXXX done — merged into sprint-N-dev"`
   - Do NOT touch the user's branch
   - Do NOT push to remote

### Orchestrator Observation Check — Stage 3

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` If QA agent spawned: `qa_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 4 — PO Story Closure

### Non-behavioral fast path (`Type: non-behavioral`)

1. Orchestrator executes closure directly — no PO agent spawn:
   - **GitHub mode:** tick all AC checkboxes in the issue body (`gh issue edit` with `--body-file`); remove all `status:*` labels and add `status:done`; close the issue
   - **Strict mode:** edit AC checkboxes to `[x]` directly in the story MD file; edit `**Status:** done`
2. **Start Story Workflow:** pipeline ends here

### Behavioral path (`Type: behavioral`)

1. **Spawn** Product Owner agent (**model: haiku**); save its `agentId` as `po_session` (resume via `po_session` if still active from a previous story in this sprint)
2. PO reads for closure only — **skip Project_Priming and Working Record**:
   - `.claude/agents/rules/Story_Standard_PO.md` (§14 AC rules, §15 PowerShell safety)
   - `.claude/agents/rules/Product_Owner_Rules.md`
   - `.claude/agents/memory/Product_Owner_Memory.md`
3. PO verifies acceptance and closes the story:
   - **Elevated verification requirement check:** if the story body contains an explicit elevated/extra QA validation requirement section (distinct from standard AC), confirm QA's sign-off comment specifically addresses that requirement's named conditions before ticking AC — a generic "AC pass / tests green" comment is not sufficient closure evidence for a story that named a higher bar for itself.
   - **Closure signal when implementer = validator:** when the story's routing table (Stage 0) assigned the same role as both implementer and what would otherwise be validator, and that stage was accordingly skipped, the closure signal is the reviewer's final approval plus a confirmed merge — not a separate validator-confirms event.
   - **GitHub mode:** tick AC checkboxes (`gh issue edit` with `--body-file`); remove all `status:*` labels and add `status:done`; close the issue
   - **Strict mode:** edit AC checkboxes to `[x]` in the story MD; edit `**Status:** done`; append PO closure comment entry to story MD `## Comments`
4. PO writes retro section to `.claude/agents/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
5. **Start Story Workflow:** pipeline ends here

### Orchestrator Observation Check — Stage 4

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` If behavioral: `po_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after every stage transition (verify all 4)?
- `[skipped-step]` All spawned session IDs recorded immediately (impl, reviewer if spawned, qa if spawned, po if spawned)?

After completing this check → **proceed to Stage 5**.

---

## Stage 5 — Story Retrospective [BETA: enabled]

> **Beta toggle:** If this heading reads `[BETA: disabled]`, skip this stage entirely — for `continue sprint` proceed to next story (Stage 0); for `start story` proceed to Retro Review.

Each agent wrote their retro section inline at the end of their stage work. Stage 5 is a bookkeeping step only — no agent spawning.

### 5.1 — Write orchestrator observations

Read `Observations:` from the state file:
- **Not empty** → overwrite the `*(pending)*` in the `## Orchestrator / ### Observations` section of the retro file with the bullet list.
- **Empty** → replace `*(pending)*` with `*(none)*`.

### 5.2 — Verify retro file

Read `.claude/agents/retros/ST-XXXXXX_retro.md`. Check that all expected sections are populated (no remaining `*(pending)*` placeholders).

- **Section still shows `*(pending)*`** → replace with `*(not submitted)*` — do not spawn agents to collect it.
- **Section shows `*(stage skipped)*`** → correct; leave as-is.

### Orchestrator Observation Check — Stage 5

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` Retro file skeleton created at Stage 1 before spawning implementer?
- `[skipped-step]` Orchestrator observations written to `## Orchestrator` section?
- `[skipped-step]` Retro file verified — no remaining `*(pending)*` placeholders?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

After completing Stage 5 → **for `continue sprint`: proceed to next story (Stage 0). For `start story`: proceed to Retro Review.**
<!-- SHARED-END -->
