# Shared Pipeline Stages

Used by [Sprint Workflow](Sprint_Workflow.md) and [Start Story Workflow](Start_Story_Workflow.md). Session IDs are maintained by the orchestrator across stages.

---

---

## Stage 0 — Implementer Routing

**Read the story body** to get `**Assigned:**` and classify the story:

Run `gh issue view <number> --json body,labels` to read the story body and labels.

Store `Implementer` in the pipeline state file. This determines which agent runs Stage 1 and which agent reviews in Stage 2.

| `**Assigned:**` value | Stage 1 agent | Stage 2 reviewer | Stage 3 validator |
|---|---|---|---|
| `Developer` | Developer | Technical Lead | QA |
| `Technical Lead` | Technical Lead | Developer (peer review) | QA |
| `QA` | QA | Technical Lead | Skipped — PO validates AC directly |
| `Business Analyst` | Business Analyst | Technical Lead | QA |

> If the `**Assigned:**` field is missing or contains an unrecognised value, stop and notify the user before proceeding.

**Feature context detection:**

Run `gh issue view <number> --json labels --jq '.labels[].name'` and inspect the labels:
- If a label matching `feature:*` exists → extract the feature name; store as `Feature` in pipeline state
- If a label matching `phase-*` exists → extract the phase number; store as `Phase` in pipeline state
- If neither found → store `Feature: none` and `Phase: none`

Pass `Feature` and `Phase` to all agents spawned in Stages 1–3 so they can route to the correct `docs/feature/<Feature>/` and `tests/feature/<Feature>/` paths.

**Story type classification:** Read the story's **Technical Scope** section and classify:
- `Type: non-behavioral` — all files listed are docs, config, YAML, or Markdown; no source code files, no DB migrations, no behavioral API spec changes
- `Type: behavioral` — any source code file, DB migration, or behavioral API change is listed
- If Technical Scope is absent or ambiguous → default to `Type: behavioral`

Store `Type` in the pipeline state file. It controls fast-path routing in Stages 2 and 3.

---

## Stage 1 — Implementation

**Orchestrator pre-spawn: create the retro file skeleton** before spawning the implementer. Use the story ID and title from Stage 0. Write `.claude/agents/working/retros/ST-XXXXXX_retro.md`:

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

1. **Spawn** the agent matching the `Implementer` role
2. **Immediately write `impl_session: <agentId>` to the state file — do this before any other action after spawning.** Never leave `impl_session` empty after a spawn returns.
3. Agent reads its own instruction files, memory, and rules
4. **Read the story:** Agent reads the assigned story from GitHub (`status:in-progress` or next `status:ready` story via `gh issue view`)
5. **Before writing any code or files** → update story status to `in-progress`: update story label to `status:in-progress`
6. **CI/CD check:** if the story's Technical Scope includes any file under `.github/workflows/`, the implementer **must** follow `.claude/agents/working/rules/CICD_Validation_Guide.md` before opening a PR
7. **Deletion pre-check** — if the story involves deleting files: before executing any `git rm` or file deletion, post a comment on the GitHub Issue listing every file planned for deletion
8. Agent implements and updates working record; commits use the format `[ST-XXXXXX][DEVKIT]: <message>`
9. **After implementation is ready for review** → open PR; update story label to `status:review`
10. Agent writes retro section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
11. **If blocked on external input** → agent follows the **Blocked Story Procedure** below; orchestrator stops the pipeline and notifies the user
12. On completion → proceed to Stage 2

### Mid-Implementation Consultation Procedure (orchestrator executes when Developer reports a question)

When the implementer returns with a mid-implementation consultation report instead of a completion report:

1. **Read the report** — identify `Owner` (TL / PO / both) and the specific `Question`.

2. **Spawn or resume the answering agent(s):**
   - If `Owner` is TL → spawn/resume Technical Lead with the question and story context
   - If `Owner` is PO → spawn/resume Product Owner with the question and story context
   - If `Owner` is both → spawn both in parallel (single orchestrator message)

   Spawn prompt must include:
   - Story ID and GitHub Issue number
   - The Developer's exact question and decision needed (from the report)
   - Where the Developer paused (from the report)
   - Instruction: *"The Developer has already posted the question as a comment on the GitHub Issue. Read that comment, then post your answer as a reply comment on the same issue — this keeps the full decision trail on the story. Then report your answer back to the orchestrator in one clear sentence."*

3. **Collect the answer(s).** If both TL and PO are consulted, wait for both before resuming the Developer.

4. **Resume the implementer** via `SendMessage` to `impl_session` (spawn new if expired). Pass:
   - The answer(s) from TL and/or PO
   - A reminder of where they paused
   - Instruction to continue implementation

5. **Do not change story label** — it remains `status:in-progress` throughout.

6. **Loop limit:** counts toward the story's Impl→Reviewer loop limit if the consultation causes a re-review cycle; does not count otherwise.

> **Distinguish from Blocked Story Procedure:** Use this when the question can be answered by TL or PO from existing context. Use the Blocked Story Procedure only when the answer requires input that no internal agent can provide (external system access, user preference, credentials, etc.).

### Blocked Story Procedure (agent executes when external input is required)

1. Resolve **who to tag** following the lookup order in `.claude/agents/working/rules/Blocked_Request.md` § Step 1 — if no match is found, report back to the orchestrator to ask the user before proceeding
2. Fill in the template with the resolved name, confirmed items, missing items, and helpful commands
3. Write the filled-in content to `.claude/agents/working/tmp/blocked_<story-id>.md`
4. Post the filled-in comment on the story issue; change the story label to `status:blocked`
5. Return to orchestrator: `"Blocked — awaiting external input. Comment posted on story ST-XXXXXX."`

### Orchestrator Observation Check — Stage 1

After the implementer reports completion, append a bullet to `Observations:` for each item that did **not** happen. Prefix each with the category tag.

- `[skipped-step]` Story status updated to `in-progress` before any file was written?
- `[skipped-step]` CHANGELOG.md updated with a bullet entry before opening PR?
- `[skipped-step]` If story deletes files: deletion plan recorded (GitHub Issue comment) before any `git rm` executed?
- `[skipped-step]` Story status updated to `review` after implementation was ready?
- `[skipped-step]` If story touches `.github/workflows/`: passing `ci-validation` run URL present in PR description?
- `[skipped-step]` `impl_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 2 — Review

### Non-behavioral fast path (`Type: non-behavioral`)

**Get the diff:** `gh pr diff <PR-number> --repo mycom08/mt-agent-devkit`

1. Read each reference file listed in the story's Technical Scope using the Read tool
2. Verify each AC against the diff and reference files:
   - **Every AC confirmed from diff + reference files alone** → record approval: post approval as `gh pr comment` on the PR → proceed to Stage 3 without spawning a reviewer agent
   - **Any AC requires domain knowledge not derivable from the diff or reference files** → fall back to the behavioral path below for full TL review
3. If changes are needed, resume Implementer via `impl_session` (spawn new if expired); re-run this fast path on completion

### Behavioral path (`Type: behavioral`)

1. **Spawn** the reviewer agent based on the routing table in Stage 0; save its `agentId` as `reviewer_session`
   - Default: **Technical Lead** reviews
   - Exception: if `Implementer` is `Technical Lead` → **Developer** does peer review
2. Reviewer reads its own instruction files, memory, and rules
3. **Reviewer reviews the PR** (use `gh pr comment` — GitHub blocks self-approval via `gh pr review --approve`)
4. **If changes requested** → resume Implementer via `SendMessage` to `impl_session` with reviewer feedback (spawn new if expired); on Implementer completion **resume Reviewer via `reviewer_session` to re-review** (spawn new if expired)
5. Reviewer writes retro section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
6. **If approved** → proceed to Stage 3

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
3. **If Stage 2 used the behavioral path** → read each AC from the story body and the current state of each file listed in Technical Scope via `gh pr diff` or Read tool:
   - **Every AC confirmed** → record QA sign-off; execute the **Merge Procedure** below; proceed to Stage 4
   - **Any AC requires domain knowledge not derivable from the files** → fall back to the behavioral path below for full QA agent validation
4. If AC issues found, resume Implementer via `impl_session` (spawn new if expired); re-run this fast path on completion

**Record QA sign-off:** post QA sign-off comment on the GitHub Issue

### Behavioral path (`Type: behavioral`)

5. **Spawn** QA agent; save its `agentId` as `qa_session`
6. QA reads `qa_instructions.md` + `QA_Memory.md` + `QA_Rules.md`
7. QA validates story acceptance criteria, runs test scenarios, checks regression risk
8. **If story AC issues found** → resume Implementer via `SendMessage` to `impl_session` with QA findings (spawn new if expired); on Implementer completion **resume QA via `SendMessage` to `qa_session`** to revalidate (spawn new if expired)
9. **If story AC passed** → QA updates automation coverage for the story then runs the full automation suite to check for regressions (see QA Rules §8–§9)
   - **If automation fails** → QA reports regression failures as a story comment → resume Implementer via `impl_session` to fix (spawn new if expired); on completion resume QA to revalidate (counts toward loop limit)
   - **If automation passes** → QA writes retro section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back; orchestrator executes the **Merge Procedure** below
10. On merge confirmed → proceed to Stage 4

### Merge Procedure (orchestrator executes directly — no agent spawn)

1. Get the PR branch name: `gh pr view <PR-number> --repo mycom08/mt-agent-devkit --json headRefName --jq '.headRefName'`
2. Merge the PR: `gh pr merge <PR-number> --repo mycom08/mt-agent-devkit --merge`
3. Delete the remote dev branch: `git push origin --delete <branch-name>`
4. Switch local branch to target: `git checkout main`
5. Pull to sync: `git pull origin main`

### Orchestrator Observation Check — Stage 3

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` If QA agent spawned: `qa_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 4 — PO Story Closure

### Non-behavioral fast path (`Type: non-behavioral`)

1. Orchestrator executes closure directly — no PO agent spawn:
   - Tick all AC checkboxes in the issue body (`gh issue edit` with `--body-file`); update label to `status:done`; close the issue
2. **Sprint Workflow only:** promote next `status:ready` story if applicable
3. **Start Story Workflow:** pipeline ends here

### Behavioral path (`Type: behavioral`)

1. **Spawn** Product Owner agent; save its `agentId` as `po_session` (resume via `po_session` if still active from a previous story in this sprint)
2. PO reads for closure only — **skip Project_Priming and Working Record**:
   - `.claude/agents/working/rules/Story_Standard_PO.md` (§14 AC rules, §15 PowerShell safety)
   - `.claude/agents/working/rules/Product_Owner_Rules.md`
   - `.claude/agents/working/memory/Product_Owner_Memory.md`
3. PO verifies acceptance and closes the story: tick AC checkboxes (`gh issue edit` with `--body-file`); update label to `status:done`; close the issue
4. PO writes retro section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
5. **Sprint Workflow only:** PO updates backlog — promotes next `status:ready` story if applicable: update GitHub Issue label
6. **Start Story Workflow:** pipeline ends here — PO does NOT promote the next story

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

Read `.claude/agents/working/retros/ST-XXXXXX_retro.md`. Check that all expected sections are populated (no remaining `*(pending)*` placeholders).

- **Section still shows `*(pending)*`** → replace with `*(not submitted)*` — do not spawn agents to collect it.
- **Section shows `*(stage skipped)*`** → correct; leave as-is.

### Orchestrator Observation Check — Stage 5

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` Retro file skeleton created at Stage 1 before spawning implementer?
- `[skipped-step]` Orchestrator observations written to `## Orchestrator` section?
- `[skipped-step]` Retro file verified — no remaining `*(pending)*` placeholders?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

After completing Stage 5 → **for `continue sprint`: proceed to next story (Stage 0). For `start story`: proceed to Retro Review.**
