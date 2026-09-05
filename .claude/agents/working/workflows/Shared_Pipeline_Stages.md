# Shared Pipeline Stages

Used by [Sprint Workflow](Sprint_Workflow.md) and [Start Story Workflow](Start_Story_Workflow.md). Session IDs are maintained by the orchestrator across stages.

---

---

## Bug Reproduction Pre-Flight (runs immediately ahead of Stage 0 — bug stories only)

Runs once per story, every time this story would enter Stage 0 — Sprint Workflow's per-story loop, and Start Story Workflow's Stage Entry Check routing `status:ready`/`status:in-progress` to Stage 0. Does **not** run when a story enters directly at Stage 2 or Stage 3 (already past implementation).

**1. Is this story subject to pre-flight?** Read the issue's labels (`gh issue view <number> --json labels`) — subject to pre-flight only if the `bug` label is present.
- **Not a bug story** → skip this entire section; proceed directly to Stage 0.

**2. Read the Repro Command.** Parse `**Repro Command:**` from the issue body's `## Reproduction` section.
- **Field absent, empty, or literally `unknown`** → **skip path**: proceed directly to Stage 0 — today's behavior (Stage 1 implementer reproduces as part of its own work) is preserved unchanged. Do not attempt execution.
- **Field present with a real command** → continue to step 3.

**3. Attempt reproduction.** Run the `Repro Command` value **verbatim** — never a command synthesised from AC prose or any other field — in the repo root, using whichever shell tool the command's syntax implies.
- **The tool itself cannot be invoked** (the shell reports the command/binary is missing — e.g. `command not found`, `'X' is not recognized`, `ENOENT` — a tooling-availability error, not a test result) → **skip path**: proceed directly to Stage 0, same as step 2's skip. Record nothing further.
- **The command executes to completion** (regardless of exit code) → continue to step 4.

**4. Evaluate the result** against the story's `**Expected:**` / `**Actual:**` fields:
- **Observed output matches `**Actual:**`** → **Reproduced.**
  - Record a short repro artifact (command run, tool used, observed failure) and pass it directly in the Stage 1 spawn prompt, in addition to the story body, as the implementer's confirmed starting evidence.
  - Proceed to Stage 0 → Stage 1 as normal.
- **Observed output does not match `**Actual:**`** (command passes cleanly, or fails in a way inconsistent with the reported defect) → **Not reproduced.**
  - Do **not** spawn any Stage 1 agent for this story.
  - Report the repro steps and result: post a comment on the issue with the command run, the story's `**Expected:**`/`**Actual:**`, and what was actually observed.
  - Leave the story's status label **unchanged**.
  - **Sprint Workflow:** append the story ID to the `Repro Skipped:` field in the pipeline state file; skip this story and continue to the next `status:ready` story not already recorded in `Repro Skipped:` for this run.
  - **Start Story Workflow:** report the result to the user and **stop** — do not proceed to Stage 0 for this story.

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
| `UI/UX Designer` | UI/UX Designer | Technical Lead | QA |

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

Store `Type` in the pipeline state file. It controls fast-path routing in Stages 3 and 4. **`Type` never routes Stage 2** — in this repo the shipped product is its Markdown (templates, rules, instructions, workflows), so a `non-behavioral` diff is still a change to agent behaviour and always gets a full reviewer.

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

1. **Spawn** the agent matching the `Implementer` role — **Developer → `model: opus`, reasoning effort medium**; any other implementer role → **model: sonnet**
   > **Spawn-prompt reminder (mandatory-reading references):** when the spawn prompt points the agent at a Story Standard file, name only the role-scoped variant already gated by that role's own Rules file (e.g. `Story_Standard_Dev.md` for Developer, `Story_Standard_TL.md` for Technical Lead) — never phrase it as "`Story_Standard.md` (or the role-scoped variant if one exists)". Offering both as options causes the agent to read the full cross-role file needlessly; the role's own Rules file gate already resolves which one to read.
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

### Stub/TODO Scan & Verification-Only Outcome (implementer executes before step 9)

**Stub/TODO scan (mandatory):** For every file in the story's Technical Scope (and any file the diff touches), grep for stub markers (`TODO`, `FIXME`, "left as", "not part of this scope", "extension point") in content the story's own AC describes as functional. Any hit must be either implemented in this story, or explicitly recorded — visibly, in the issue thread, not just a code comment — as deferred to a **named, existing or newly-created** backlog story. A stub with no owning story is a blocking finding, not an accepted risk.

**Verification-only outcome (self-certified):** If your diff against the target branch touches nothing but docs/changelog (no template, workflow, or script files), mark the story `Outcome: verification-only` in the pipeline state file, in addition to your normal completion report. Stage 2/3 still perform one independent spot-check rather than trusting this tag blindly. If a reviewer/QA spot-check contradicts the tag, that is treated as an implementer accuracy issue in retro.

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
   - Instruction: *"The Developer has already posted the question as a comment on the GitHub Issue. Read that comment, then post your answer as a reply comment on the same issue — this keeps the full decision trail on the story. Then report your answer back to the orchestrator in one clear sentence."*
   - For a TL owner on a **fresh spawn** (not a resume): instruct it to use the reduced read set at `Technical_Lead_Rules_Read_On_Demand.md §6` (Answer-a-Question Task) instead of the full Pre-Work Checklist

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

> **No fast path here — every story gets a reviewer agent, whatever its `Type`.** A `Type: non-behavioral` diff in this repo still edits the Markdown that target-project agents execute, so an orchestrator-only diff read is not a substitute for Technical Lead review. Stages 3 and 4 keep their non-behavioral fast paths; Stage 2 does not have one.

### Review (all stories, `Type: behavioral` and `Type: non-behavioral` alike)

1. **Spawn** the reviewer agent based on the routing table in Stage 0; save its `agentId` as `reviewer_session`
   - Default: **Technical Lead** reviews (**model: opus**)
   - Exception: if `Implementer` is `Technical Lead` → **Developer** does peer review (**model: opus**, reasoning effort medium)
   - If Stage 1 reported `Outcome: verification-only` → right-size effort: read the implementer's cited evidence directly and perform **one** targeted spot-check instead of full re-verification; escalate only if there's a specific reason to distrust the evidence. Default to **model: sonnet** instead of opus — Technical Lead reviewer only; a Developer peer reviewer stays on opus/medium.
   - When the reviewer is Technical Lead, the spawn prompt names `Technical_Lead_Rules_Read_On_Demand.md §5` (Code Review & PR Approval) as the section to fetch per its own §15 routing table.
2. Reviewer reads its own instruction files, memory, and rules
3. **Reviewer reviews the PR** (use `gh pr comment` — GitHub blocks self-approval via `gh pr review --approve`); an approval comment cites the current head SHA as `**Approved-SHA:** <sha>` (`gh pr view <PR-number> --json headRefOid --jq '.headRefOid'`) — the Merge Procedure's Approval-scope gate reads this back later
   - **Stub/TODO re-check:** confirm the implementer's Stage 1 scan was actually done — spot-check for stub markers in AC-functional content. A hit with no owning backlog story blocks approval (see `Technical_Lead_Rules_Read_On_Demand.md §5` for the full checklist).
4. **If changes requested** → resume Implementer via `SendMessage` to `impl_session` with reviewer feedback (spawn new if expired); on Implementer completion **resume Reviewer via `reviewer_session` to re-review** (spawn new if expired)
5. Reviewer writes retro section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
6. **If approved** → proceed to Stage 3

### Orchestrator Observation Check — Stage 2

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` `reviewer_session` saved in state file immediately after spawn? (every story — Stage 2 has no fast path)
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 3 — QA Validation

> **Merge gate — behavioral stories:** The Merge Procedure fires only at behavioral path step 9 — after QA confirms automation passes. Do NOT execute it at Stage 3 entry or immediately after Stage 2 approval.

1. **If `Implementer` is `QA`** → skip QA validation; orchestrator executes the **Merge Procedure** below, then proceed to Stage 4

### Non-behavioral fast path (`Type: non-behavioral`)

2. Read each AC from the story body and the current state of each file listed in Technical Scope via `gh pr diff` or Read tool:
   - **Every AC confirmed** → record QA sign-off; execute the **Merge Procedure** below; proceed to Stage 4
   - **Any AC requires domain knowledge not derivable from the files** → fall back to the behavioral path below for full QA agent validation
3. If AC issues found, resume Implementer via `impl_session` (spawn new if expired); re-run this fast path on completion

**Record QA sign-off:** post QA sign-off comment on the GitHub Issue

### Behavioral path (`Type: behavioral`)

5. **Spawn** QA agent (**model: sonnet**); save its `agentId` as `qa_session`
6. QA reads `qa_instructions.md` + `QA_Memory.md` + `QA_Rules_Bootstrap.md`
7. QA validates story acceptance criteria, runs test scenarios, checks regression risk
   - If Stage 1 reported `Outcome: verification-only` → read the implementer's cited evidence and perform **one** targeted spot-check instead of full re-verification; escalate only if there's a specific reason to distrust it. Skip the test-scenario document per `QA_Rules_Bootstrap.md §4`'s verification-only exception.
8. **If story AC issues found** → resume Implementer via `SendMessage` to `impl_session` with QA findings (spawn new if expired); on Implementer completion **resume QA via `SendMessage` to `qa_session`** to revalidate (spawn new if expired)
9. **If story AC passed** → QA updates automation coverage for the story then runs the full automation suite to check for regressions (see QA Rules §8–§9)
   - **If automation fails** → QA reports regression failures as a story comment → resume Implementer via `impl_session` to fix (spawn new if expired); on completion resume QA to revalidate (counts toward loop limit)
   - **If automation passes** → QA writes retro section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back; orchestrator executes the **Merge Procedure** below
10. On merge confirmed → proceed to Stage 4

### Merge Procedure (orchestrator executes directly — no agent spawn)

0. **CI-check gate (mandatory, independent of reviewer sign-off):** run `gh pr checks <PR-number> --repo mycom08/mt-agent-devkit`. Three distinct states at head — resolve each on its own terms, and never treat "no checks reported" as equivalent to "checks passed":
   - **State 1 — checks reported, all `completed`, none `fail`:** gate satisfied against the head SHA.
   - **State 2 — any check `fail`, or any check not yet `completed`:** **abort the merge** — report the failing/pending check(s) to the user instead of proceeding. This runs regardless of what the reviewer's approval comment claims.
   - **State 3 — zero checks reported:** this is **not** State 1. Determine which of two distinct causes applies before proceeding — they resolve differently:
     - **(a) A CI-suppression token (e.g. `[skip ci]`) sits in the head commit's message.** This suppresses the run for the whole push — `validate-templates.yml`'s `paths:` filter is evaluated against the PR's entire changed-file set on every push, not the individually pushed commit, so a bookkeeping-only commit landing last does not by itself explain an empty rollup when the total diff still touches `.claude/agents/templates/**` or `.claude/agents/workflows/**` (tested and disproven — ST-000148: a retro-only push still produced a fresh green run at the new head; there is no commit-ordering hazard). To resolve: walk the branch's commits backward from head and find the most recent SHA that actually has a recorded check-run (`gh api repos/mycom08/mt-agent-devkit/commits/<SHA>/check-runs`) — that SHA is the last push that wasn't suppressed. If its run is `completed` and passing, the gate is satisfied **against that SHA**, not head; record which SHA was used. If no such run exists, or it failed, treat this the same as State 2 and abort.
     - **(b) No commit's push ever produced a run because no path in the PR's whole changed-file set (`gh pr diff <PR-number> --name-only`) matches `validate-templates.yml`'s `paths:` filter.** Nothing was ever eligible. State this outcome explicitly rather than proceeding silently: the merge decision rests entirely on reviewer sign-off, with the absence of any eligible check recorded as a deliberate, evidenced exception — not as a passed check.
   - **Audit requirement (whichever state leads to a merge):** before step 2 below, post a `gh pr comment` recording which state applied (1 / 3a / 3b) and the evidence used.
0a. **Approval-scope gate (mandatory, independent of the CI gate):** find the most recent `**Approved-SHA:**` the reviewer cited at Stage 2 and diff it against the current head: `git diff <Approved-SHA> <head-SHA> --name-only`.
    - **Permitted post-approval additions:** agent memory-file commits (Stage-Transition Commit, `Agent_Common_Read_On_Demand.md §5`), the story's own retro file (`Retro_Rules.md`), and QA's test-scenario document (`QA_Rules_Bootstrap.md §4`) — the pipeline itself schedules these here, not because they are "just docs."
    - **Anything else added or modified since the Approved-SHA** → the sign-off no longer covers the artifact about to merge. Do not merge; resume the reviewer (`reviewer_session`) with just the post-approval delta, and get a refreshed `Approved-SHA` before retrying this gate.
    - Add the outcome (unchanged / bookkeeping-only / re-review triggered) to the same audit comment as step 0.
1. Get the PR branch name: `gh pr view <PR-number> --repo mycom08/mt-agent-devkit --json headRefName --jq '.headRefName'`
2. Merge the PR: `gh pr merge <PR-number> --repo mycom08/mt-agent-devkit --merge`
3. Delete the remote dev branch: `git push origin --delete <branch-name>`
4. Switch local branch to target: `git checkout main`
5. Pull to sync: `git pull origin main`

> **No-branch-protection note:** on a repo without required-status-checks support, steps 0 and 0a above are the *only* enforcement that exists — treat both as non-optional baseline pipeline behavior.

### Orchestrator Observation Check — Stage 3

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` If QA agent spawned: `qa_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 4 — PO Story Closure

> **GitHub mode closure-comment ordering (mandatory pre-check, not a memory item):** before posting any closure comment, run `gh issue view <number> --json state --jq '.state'`. **`CLOSED`** → the merged PR's `Closes #N`-style keyword already auto-closed the issue before Stage 4 ran; post the closure comment via a **separate** `gh issue comment` call — never combine it with `gh issue close --comment`, since `gh issue close` on an already-closed issue errors out and silently drops the comment along with it. **`OPEN`** → the combined `gh issue close --comment` call is safe to use as-is. Checking state first turns this from a rule to remember into a branch to execute — the prose warning alone was insufficient in practice (recurred in ST-000032 after already being documented from ST-000026).

### Non-behavioral fast path (`Type: non-behavioral`)

1. Orchestrator executes closure directly — no PO agent spawn:
   - Tick all AC checkboxes in the issue body (`gh issue edit` with `--body-file`); remove all `status:*` labels and add `status:done`; close the issue
2. **Start Story Workflow:** pipeline ends here

### Behavioral path (`Type: behavioral`)

1. **Spawn** Product Owner agent (**model: haiku**); save its `agentId` as `po_session` (resume via `po_session` if still active from a previous story in this sprint)
2. PO reads for closure only — **skip Project_Priming and Working Record**:
   - `.claude/agents/working/rules/Story_Standard_PO.md` (§14 AC rules); `Agent_Common_Bootstrap.md §6` (PowerShell safety)
   - `.claude/agents/working/rules/Product_Owner_Rules_Bootstrap.md`
   - `.claude/agents/working/memory/Product_Owner_Memory.md`
3. PO verifies acceptance and closes the story:
   - **Elevated verification requirement check:** if the story body contains an explicit elevated/extra QA validation requirement section (distinct from standard AC), confirm QA's sign-off comment specifically addresses that requirement's named conditions before ticking AC — a generic "AC pass / tests green" comment is not sufficient closure evidence for a story that named a higher bar for itself.
   - **Closure signal when implementer = validator:** when the story's routing table (Stage 0) assigned the same role as both implementer and what would otherwise be validator, and that stage was accordingly skipped, the closure signal is the reviewer's final approval plus a confirmed merge — not a separate validator-confirms event.
   - Tick AC checkboxes (`gh issue edit` with `--body-file`); remove all `status:*` labels and add `status:done`; close the issue
4. PO writes retro section to `.claude/agents/working/retros/ST-XXXXXX_retro.md` per `Retro_Rules.md` before reporting back
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

Read `.claude/agents/working/retros/ST-XXXXXX_retro.md`. Check that all expected sections are populated (no remaining `*(pending)*` placeholders).

- **Section still shows `*(pending)*`** → replace with `*(not submitted)*` — do not spawn agents to collect it.
- **Section shows `*(stage skipped)*`** → correct; leave as-is.

### Orchestrator Observation Check — Stage 5

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` Retro file skeleton created at Stage 1 before spawning implementer?
- `[skipped-step]` Orchestrator observations written to `## Orchestrator` section?
- `[skipped-step]` Retro file verified — no remaining `*(pending)*` placeholders?
- `[skipped-step]` Ran `wc -c .claude/agents/working/working-record/*_Working_Record.md`; append one bullet per file over 10,000 chars, naming the file and its size.
- `[skipped-step]` Ran `wc -c .claude/agents/working/memory/*_Memory*.md` (covers both single-file memory and, for Dev/QA/TL, the two-tier live index + `_Archive` file — see `Agent_Common_Read_On_Demand.md §8`); append one bullet per file over 40,000 chars, naming the file and its size.
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

After completing Stage 5 → **for `continue sprint`: proceed to next story (Stage 0). For `start story`: proceed to Retro Review.**
