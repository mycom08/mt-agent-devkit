# Shared Pipeline Stages

Used by [Sprint Workflow](Sprint_Workflow.md) and [Start Story Workflow](Start_Story_Workflow.md). Session IDs are maintained by the orchestrator across stages.

---

---

## Worker Entry Read Contract

For every fresh worker spawn or expired-session restart, include this contract verbatim in the ordinary role packet, together with the selected adapter, concrete bindings and canonical role instruction path. It applies before discovery commands or shell-based context loading; a rule inside an unread role file cannot enforce that boundary by itself. A valid same-session resume retains its prior reads and receives only the new task/evidence delta.

```text
Before any shell command, use the runtime's native file-reading tool when
available (Claude: Read) to read the supplied selected provider adapter first,
then the canonical role instruction, directly from their original paths and
in full. Complete successful returned coverage before proceeding; follow up
truncated reads with that same tool. Shell cat/sed/Python output, persisted
tool-output files and preloaded summaries do not substitute for these reads.
Use the same direct native tool for subsequent mandatory full-file reads
routed by the role. This read gate precedes command batching and discovery.
If no native file-reading tool exists, use the selected provider's supported
file-reading mechanism: a shell read of the supplied adapter itself is the
only preparatory shell exception; read it before any other shell command,
then follow its sanctioned mechanism. Do not invent a Read tool or transfer
another provider's procedure. Missing adapter/bindings or unavailable required
file-reading capability blocks before other commands or state access.
```

---

## Story Base Preflight (before Bug Reproduction and Stage 0)

**Interrupted Stage 1 recovery for a `status:ready` story:** Before new-story `inspect`, check whether the intended local story branch already exists. If it does, read the pipeline state without writing. Resume after branch creation only when state names this story at Stage 0 or 1, records a full Verified Base SHA, the checked-out branch is the intended story branch, its full tip SHA equals that recorded base SHA, and `git status --porcelain` is empty. Then record Story Branch, continue Stage 1 after `create`, and update status; do not repeat Bug Reproduction, Stage 0, `inspect`, or `create`. If any check fails or state is missing, stop and report the exact mismatch for explicit state recovery; do not switch, delete, reset, or recreate a branch. A fresh Sprint run with no state uses the same fail-closed rule.

For each new Stage 0 entry, read the story's immutable `Base Branch`, derive its intended story branch per `Story_Standard.md`, and run `branch_preflight.py inspect --mode github --base <Base Branch> --story-branch <story-branch>` **before any pipeline-state, retro, issue-comment, status, or product write**. Keep the full Base SHA and Remote Base SHA in the current invocation for Stage 1. A missing Base Branch or BLOCKED result stops without a write or recovery action. Stage 1 uses `create`, which repeats inspection. Stories entering directly at Stage 2 or 3 use their existing branch and state; do not create another branch.

---

## Bug Reproduction Pre-Flight (runs immediately ahead of Stage 0 — bug stories only)

Runs once for each new `status:ready` story entering Stage 0 — Sprint Workflow's per-story loop or Start Story Workflow's ready entry. A resumed `status:in-progress` story continues from its recorded stage without rerunning this check. Does **not** run when a story enters directly at Stage 2 or Stage 3 (already past implementation).

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

Enter Stage 0 only after Story Base Preflight passed. State writes below use that verified result; story status and product writes wait for Stage 1 branch creation.

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

An explicit Feature/Phase passed by the user or orchestrator is authoritative.
Use the current story's explicit Feature/Phase; never supply a fixed feature or
phase from a previous story. Do not require a `feature:` prefix on a user-selected
plain kebab-case label. If an
explicit feature and tracker metadata conflict, stop for clarification.


Run `gh issue view <number> --json labels --jq '.labels[].name'` and inspect the labels:
- If a label matching `feature:*` exists → extract the feature name; store as `Feature` in pipeline state
- If a label matching `phase-*` exists → extract the phase number; store as `Phase` in pipeline state
- If neither found → retain explicit Feature/Phase when supplied; otherwise store `Feature: none` and `Phase: none`

Pass `Feature` and `Phase` to all agents spawned in Stages 1–3 so they can route to the correct `docs/feature/<Feature>/` and `tests/feature/<Feature>/` paths.

**Story type classification:** Read the story's **Technical Scope** section and classify:
- `Type: non-behavioral` — all files listed are docs, config, YAML, or Markdown; no source code files, no DB migrations, no behavioral API spec changes
- `Type: behavioral` — any source code file, DB migration, or behavioral API change is listed
- If Technical Scope is absent or ambiguous → default to `Type: behavioral`

Store `Type` in the pipeline state file. It controls fast-path routing in Stages 3 and 4. **`Type` never routes Stage 2** — in this repo the shipped product is its Markdown (templates, rules, instructions, workflows), so a `non-behavioral` diff is still a change to agent behaviour and always gets a full reviewer.

---

## Telemetry collection — mandatory after every completed stage

After every completed agent stage (including a non-behavioral fast path), write exactly one Schema v1 JSON Lines record to `{RUNTIME_ROOT}/tmp/token-metrics/<run-id>.jsonl`; this runtime directory is gitignored and never committed.

Create metadata containing only `run_id`, `story_id`, `role`, `stage`, `session_mode`, `model`, `started_at`, `ended_at`, `duration_ms`, `completion_status`, and `notes`. Never include transcript paths, prompt content, secrets, issue tokens, tool input, or full tool output.

Use the selected adapter's telemetry procedure through `.mt-agent-devkit/scripts/telemetry.py`.
Fresh native usage extraction and same-session resume bounds are provider-specific.
With only a real final-context counter use `harness`; without supported data use
`harness` with explicit unavailable/null fields and a factual note. Never estimate
usage or label final-context tokens as cumulative consumption. Aggregate with
`aggregate --input {RUNTIME_ROOT}/tmp/token-metrics/<run-id>.jsonl`; malformed
input, duplicate stage identities and mixed schemas stop the run.

### Bounded same-session resume

This is the single boundary handoff procedure for every fix, review re-check,
QA re-check and consultation resume. ST-000254 read manifests consume these
handoff fields; they do not define another telemetry policy. The orchestrator
owns capture and collection; workers receive the ordinary task/evidence delta.

1. Before invoking the selected adapter's resume operation, capture a start
   boundary for the intended worker while that session is idle. Use its exact
   Claude worker handle for both `--agent-id` and `--session-id`; discovery is
   confined to this project and this worker. Save a distinct runtime-local
   `<stage>-start.boundary.json` for each completed stage identity.
2. Invoke the adapter's supported resume operation. After its actual completion,
   capture `<stage>-end.boundary.json` against the same provider/session/source
   before any further reuse of that session. Preserve start/end filenames in
   the stage handoff alongside provider, worker handle and completion evidence.
3. Extract with both snapshots and sanitized metadata using
   `session_mode: same_session_resume`. Only successful bounded extraction may
   label that resumed stage `usage_source: raw_transcript`. Never retry it as
   whole-session extraction. Fresh or expired sessions keep compatible fresh
   extraction; do not apply a previous worker's boundary to a new session.
4. Capture/extraction failures, missing discovery, unproven coverage or an
   interrupted stage cannot prove zero. Report the collector's actionable error,
   retain the snapshots as local evidence and collect explicit unavailable
   usage through `harness` with a short factual reason. Preserve the actual
   lifecycle `session_mode`; omit `session_final_tokens` for wholly unavailable
   output. A real independently reported final-context counter may instead use
   the existing `harness_report` fallback. Do not estimate any usage metric.

Supported Claude discovery example (substitute concrete bound runtime paths):

```bash
python .mt-agent-devkit/scripts/telemetry.py boundary --provider claude --session-id <worker-id> --agent-id <worker-id> --project-root . --output <RUNTIME_ROOT>/tmp/token-metrics/<run-id>/<stage>-start.boundary.json
# Invoke the selected adapter's resume operation and wait for actual completion.
python .mt-agent-devkit/scripts/telemetry.py boundary --provider claude --session-id <worker-id> --agent-id <worker-id> --project-root . --output <RUNTIME_ROOT>/tmp/token-metrics/<run-id>/<stage>-end.boundary.json
python .mt-agent-devkit/scripts/telemetry.py extract --provider claude --session-id <worker-id> --agent-id <worker-id> --project-root . --start-boundary <RUNTIME_ROOT>/tmp/token-metrics/<run-id>/<stage>-start.boundary.json --end-boundary <RUNTIME_ROOT>/tmp/token-metrics/<run-id>/<stage>-end.boundary.json --metadata <stage-metadata.json> --output <RUNTIME_ROOT>/tmp/token-metrics/<run-id>.jsonl --append
```

For an explicitly supplied transcript, replace `--agent-id <worker-id>
--project-root .` in all three commands with `--transcript <selected-transcript>`.
Use the worker handle for a recognized `agent-<worker-id>.jsonl` filename;
otherwise `--session-id` must match positive consistent native `sessionId` or
`session_id` evidence. The worker handle and native parent session ID are
separate identities. Never discover another transcript when ownership fails.

Snapshots contain version 1, provider, hashed session/source identity, stable
filesystem identity, complete-line byte offset and prefix digest. Both snapshots
are verified before counting; replacement, truncation, prefix edits, malformed
records and read races fail. Only the selected interval contributes request IDs
and request-scoped tool IDs; a request crossing its start fails attribution.
Exact streaming duplicates within the interval count once; conflicting usage
or tool evidence fails. An unchanged validated interval proves zero only with
established session evidence; an empty file or missing discovery remains unknown.

All schema 1 usage fields require complete finalized request evidence or
comparable endpoint-aligned session checkpoints. Request evidence uses a
supported terminal `message.stop_reason`, consistent input/cache values and the
final streamed output for each request. Cumulative checkpoints additionally
require existing `type: result`, matching native `session_id`,
`usage_scope: session`, `usage_definition: claude-token-usage-v1`, all four
nonnegative token counters, complete attributable request/tool evidence and
monotonic counters throughout the interval. Their input/cache deltas must agree
with request evidence; bounded output is the validated output delta. Do not add
markers to a source transcript or infer cumulative semantics from a generic
result. Without these checkpoint markers, complete finalized requests remain
the alternative; a whole-session output summary never substitutes for bounded
output. Any missing metric makes the entire usage unavailable or errors.

Codex and Antigravity retain their explicit `harness` fallback; generated layouts
and synthetic checkpoint fixtures do not certify native transcript support.

---

## Stage 1 — Implementation

**Orchestrator pre-spawn:** initialize `Retro Contract: exception-v1` and carry an explicit expected completion identity list at the bound runtime path before each actual stage/actor executes. Follow `Agent_Common_Bootstrap.md §7`; do not create a retro skeleton. Observe trigger events throughout work. Already-started legacy runs explicitly keep their prior contract and existing history.

1. **Spawn** the agent matching the `Implementer` role — **Developer → `model policy: implementation`, reasoning effort medium**; any other implementer role → **model policy: standard**
   > **Spawn-prompt reminder (mandatory-reading references):** name the exact mandatory read set in the role instruction. Developer reads its full Bootstrap and observable routes, not `Story_Standard_Dev.md`; never offer the full cross-role Story Standard as a startup alternative. Preserve the selected adapter, role instruction and Common/role Bootstrap full-read gates.
2. Agent reads its own instruction files, memory, and rules
3. **Read the story:** Agent reads the assigned story from GitHub (`status:in-progress` or next `status:ready` story via `gh issue view`)
4. **New `status:ready` entry that has not passed interrupted Stage 1 recovery, before the first story status or product write** → run `branch_preflight.py create` for the branch named in Story Base Preflight, passing its full verified Base SHA and Remote Base SHA (`--expected-remote-sha`). `create` repeats inspection. Record Story Branch only after successful full-SHA verification; a block stops without stash, reset, rebase, or auto-repair. **Resumed `status:in-progress` entry:** use the recorded stage, story branch, and session; do not call `create` again. If the recorded branch or state cannot be verified, stop for state recovery before any write.
5. **After successful branch creation on a new entry** → write `impl_session: <session_handle>` to state, then update story status to `in-progress`.
6. **CI/CD check:** if the story's Technical Scope includes any file under `.github/workflows/`, the implementer **must** follow `.mt-agent-devkit/rules/CICD_Validation_Guide.md` before opening a PR
7. **Deletion pre-check** — if the story involves deleting files: before executing any `git rm` or file deletion, post a comment on the GitHub Issue listing every file planned for deletion
8. Agent implements and updates working record; commits use the format `[ST-XXXXXX][DEVKIT]: <message>`
9. **After implementation is ready for review** → open PR; update story label to `status:review`
10. Agent evaluates/completes its bound retrospective metadata under `Agent_Common_Bootstrap.md §7`; only required triggers load/write retrospective guidance and contributions before reporting back.
11. **If blocked on external input** → agent follows the **Blocked Story Procedure** below; orchestrator stops the pipeline and notifies the user
12. On completion → proceed to Stage 2

### Stub/TODO Scan & Verification-Only Outcome (implementer executes before step 9)

**Stub/TODO scan (mandatory):** For every file in the story's Technical Scope (and any file the diff touches), grep for stub markers (`TODO`, `FIXME`, "left as", "not part of this scope", "extension point") in content the story's own AC describes as functional. Any hit must be either implemented in this story, or explicitly recorded — visibly, in the issue thread, not just a code comment — as deferred to a **named, existing or newly-created** backlog story. A stub with no owning story is a blocking finding, not an accepted risk.

**Verification-only outcome (self-certified):** If your diff against the target branch touches nothing but docs/changelog (no template, workflow, or script files), mark the story `Outcome: verification-only` in the pipeline state file, in addition to your normal completion report. Stage 2/3 still perform one independent spot-check rather than trusting this tag blindly. If a reviewer/QA spot-check contradicts the tag, that is treated as an implementer accuracy issue in retro.

### Mid-Implementation Consultation Procedure (orchestrator executes when Developer reports a question)

When the implementer returns with a mid-implementation consultation report instead of a completion report:

1. **Read the report** — identify `Owner` (TL / PO / both) and the specific `Question`.

2. **Spawn or resume the answering agent(s):**
   - If `Owner` is TL → spawn/resume Technical Lead (**model policy: standard**) with the question and story context
   - If `Owner` is PO → spawn/resume Product Owner (**model policy: standard**) with the question and story context
   - If `Owner` is both → spawn both in parallel (**model policy: standard** for each) (single orchestrator message)

   Spawn prompt must include:
   - Story ID and GitHub Issue number
   - The Developer's exact question and decision needed (from the report)
   - Where the Developer paused (from the report)
   - Instruction: *"The Developer has already posted the question as a comment on the GitHub Issue. Read that comment, then post your answer as a reply comment on the same issue — this keeps the full decision trail on the story. Then report your answer back to the orchestrator in one clear sentence."*
   - For a TL owner on a **fresh spawn** (not a resume): instruct it to use the reduced read set at `Technical_Lead_Rules_Read_On_Demand.md §6` (Answer-a-Question Task) instead of the full Pre-Work Checklist

3. **Collect the answer(s).** If both TL and PO are consulted, wait for both before resuming the Developer.

4. **Resume the implementer** via `the selected adapter's resume operation` to `impl_session` (spawn new if expired). Pass:
   - The answer(s) from TL and/or PO
   - A reminder of where they paused
   - Instruction to continue implementation

5. **Do not change story label** — it remains `status:in-progress` throughout.

6. **Loop limit:** counts toward the story's Impl→Reviewer loop limit if the consultation causes a re-review cycle; does not count otherwise.

> **Distinguish from Blocked Story Procedure:** Use this when the question can be answered by TL or PO from existing context. Use the Blocked Story Procedure only when the answer requires input that no internal agent can provide (external system access, user preference, credentials, etc.).

### Blocked Story Procedure (agent executes when external input is required)

1. Resolve **who to tag** following the lookup order in `.mt-agent-devkit/rules/Blocked_Request.md` § Step 1 — if no match is found, report back to the orchestrator to ask the user before proceeding
2. Fill in the template with the resolved name, confirmed items, missing items, and helpful commands
3. Write the filled-in content to `{RUNTIME_ROOT}/tmp/blocked_<story-id>.md`
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

1. **Spawn** the reviewer agent based on the routing table in Stage 0; save its `session_handle` as `reviewer_session`
   - Default: **Technical Lead** reviews (**model policy: design-review**)
   - Exception: if `Implementer` is `Technical Lead` → **Developer** does peer review (**model policy: design-review**)
   - If Stage 1 reported `Outcome: verification-only` → right-size effort: read the implementer's cited evidence directly and perform **one** targeted spot-check instead of full re-verification; escalate only if there's a specific reason to distrust the evidence. Default to **model policy: standard** instead of design-review — Technical Lead reviewer only; a Developer peer reviewer stays on design-review policy.
   - When the reviewer is Technical Lead, the spawn prompt names `Technical_Lead_Rules_Read_On_Demand.md §5` (Code Review & PR Approval) as the section to fetch per its own §15 routing table.
2. Reviewer reads its own instruction files, memory, and rules
3. **Reviewer reviews the PR** (use `gh pr comment` — GitHub blocks self-approval via `gh pr review --approve`); an approval comment cites the current head SHA as `**Approved-SHA:** <sha>` (`gh pr view <PR-number> --json headRefOid --jq '.headRefOid'`) — the Merge Procedure's Approval-scope gate reads this back later
   - **Stub/TODO re-check:** confirm the implementer's Stage 1 scan was actually done — spot-check for stub markers in AC-functional content. A hit with no owning backlog story blocks approval (see `Technical_Lead_Rules_Read_On_Demand.md §5` for the full checklist).
4. **If changes requested** → resume Implementer via `the selected adapter's resume operation` to `impl_session` with reviewer feedback (spawn new if expired); on Implementer completion **resume Reviewer via `reviewer_session` to re-review** (spawn new if expired)
5. Reviewer evaluates/completes its own metadata under `Agent_Common_Bootstrap.md §7`; only required triggers load/write its contribution before handoff.
6. **If approved** → proceed to Stage 3

### Orchestrator Observation Check — Stage 2

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` `reviewer_session` saved in state file immediately after spawn? (every story — Stage 2 has no fast path)
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 3 — QA Validation

**Acceptance gate — every route:** Before recording testing-pass or invoking Merge Procedure, read and apply `Story_Standard.md §14` to the current canonical scope. Require the applicable independent validation report with a verdict/evidence for every remaining AC. Any FAIL, NOT VERIFIED, absent verdict, or insufficient evidence stops advancement; neither green automation, reviewer approval, skipped validation nor a non-behavioral fast path overrides this gate. Record the reason and missing evidence, retain the unresolved testing/open state, and use the existing external-blocker procedure when needed. Scope splits must be approved, tracked and linked in revised story bodies before renewed QA sign-off; never reinterpret prior NOT VERIFIED as PASS.

> **Merge gate — behavioral stories:** The Merge Procedure fires only at behavioral path step 9 — after QA confirms automation passes. Do NOT execute it at Stage 3 entry or immediately after Stage 2 approval.

1. **If `Implementer` is `QA`** → skip a separate QA agent; PO validates each AC independently and records the applicable report under the acceptance gate before the orchestrator executes the **Merge Procedure** below, then proceed to Stage 4

### Non-behavioral fast path (`Type: non-behavioral`)

2. Read each AC from the story body and the current state of each file listed in Technical Scope via `gh pr diff` or Read tool:
   - **Every AC confirmed** → record QA sign-off; execute the **Merge Procedure** below; proceed to Stage 4
   - **Any AC requires domain knowledge not derivable from the files** → fall back to the behavioral path below for full QA agent validation
3. If AC issues found, resume Implementer via `impl_session` (spawn new if expired); re-run this fast path on completion

**Record QA sign-off:** post QA sign-off comment on the GitHub Issue

### Behavioral path (`Type: behavioral`)

5. **Spawn** QA agent (**model policy: standard**); save its `session_handle` as `qa_session`
6. QA reads `qa_instructions.md` + `QA_Memory.md` + `QA_Rules_Bootstrap.md`
7. QA validates story acceptance criteria, runs test scenarios, checks regression risk
   - If Stage 1 reported `Outcome: verification-only` → read the implementer's cited evidence and perform **one** targeted spot-check instead of full re-verification; escalate only if there's a specific reason to distrust it. Skip the test-scenario document per `QA_Rules_Bootstrap.md §4`'s verification-only exception.
8. **If story AC issues found** → resume Implementer via `the selected adapter's resume operation` to `impl_session` with QA findings (spawn new if expired); on Implementer completion **resume QA via `the selected adapter's resume operation` to `qa_session`** to revalidate (spawn new if expired)
9. **If story AC passed** → QA updates automation coverage for the story then runs the full automation suite to check for regressions (see QA Rules §8–§9)
   - **If automation fails** → QA reports regression failures as a story comment → resume Implementer via `impl_session` to fix (spawn new if expired); on completion resume QA to revalidate (counts toward loop limit)
   - **If automation passes** → QA evaluates/completes its bound metadata under `Agent_Common_Bootstrap.md §7`, loading/writing only triggered contributions; orchestrator executes the **Merge Procedure** below
10. On merge confirmed → proceed to Stage 4

### Merge Procedure (orchestrator executes directly — no agent spawn)

**Acceptance evidence pre-check (both modes, before any merge command):** Re-read the current story scope and the applicable independent per-AC validation report under `Story_Standard.md §14`. Confirm every remaining AC is PASS with sufficient evidence against the artifact being merged. A missing report, stale scope, FAIL, or NOT VERIFIED aborts merge even if CI/review passed. For an approved split, verify the tracked follow-up/body links and renewed QA confirmation after the scope update. Existing CI and approval-SHA gates remain independent and required where applicable.

0. **CI-check gate (mandatory, independent of reviewer sign-off):** run `gh pr checks <PR-number> --repo mycom08/mt-agent-devkit`. Three distinct states at head — resolve each on its own terms, and never treat "no checks reported" as equivalent to "checks passed":
   - **State 1 — checks reported, all `completed`, none `fail`:** gate satisfied against the head SHA.
   - **State 2 — any check `fail`, or any check not yet `completed`:** **abort the merge** — report the failing/pending check(s) to the user instead of proceeding. This runs regardless of what the reviewer's approval comment claims.
   - **State 3 — zero checks reported:** this is **not** State 1. Determine which of two distinct causes applies before proceeding — they resolve differently:
     - **(a) A CI-suppression token (e.g. `[skip ci]`) sits in the head commit's message.** This suppresses the run for the whole push — `validate-templates.yml`'s `paths:` filter is evaluated against the PR's entire changed-file set on every push, not the individually pushed commit, so a bookkeeping-only commit landing last does not by itself explain an empty rollup when the total diff still touches `.claude/agents/templates/**` or `.claude/agents/workflows/**` (tested and disproven — ST-000148: a retro-only push still produced a fresh green run at the new head; there is no commit-ordering hazard). To resolve: walk the branch's commits backward from head and find the most recent SHA that actually has a recorded check-run (`gh api repos/mycom08/mt-agent-devkit/commits/<SHA>/check-runs`) — that SHA is the last push that wasn't suppressed. If its run is `completed` and passing, the gate is satisfied **against that SHA**, not head; record which SHA was used. If no such run exists, or it failed, treat this the same as State 2 and abort.
     - **(b) No commit's push ever produced a run because no path in the PR's whole changed-file set (`gh pr diff <PR-number> --name-only`) matches `validate-templates.yml`'s `paths:` filter.** Nothing was ever eligible. State this outcome explicitly rather than proceeding silently: the merge decision rests entirely on reviewer sign-off, with the absence of any eligible check recorded as a deliberate, evidenced exception — not as a passed check.
   - **Audit requirement (whichever state leads to a merge):** before step 2 below, post a `gh pr comment` recording which state applied (1 / 3a / 3b) and the evidence used.
0a. **Approval-scope gate (mandatory, independent of the CI gate):** find the most recent `**Approved-SHA:**` the reviewer cited at Stage 2 and diff it against the current head: `git diff <Approved-SHA> <head-SHA> --name-only`.
    - **No post-approval exception for agent runtime state:** memory, working records, retrospectives, telemetry, and pipeline state stay uncommitted. Any tracked change since `Approved-SHA`, including a test-scenario document, requires refreshed review.
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

**Acceptance pre-check — both paths and modes:** Before any checkbox, done-status or closure write, apply `Story_Standard.md §14`: confirm merge and current independent PASS evidence for every remaining AC. FAIL, NOT VERIFIED, missing verdicts or insufficient evidence stop closure; a previous testing-pass summary is insufficient when its scope/evidence is stale. An auto-closed issue is not acceptance evidence; reopen it if unresolved verification remains. An approved tracked split requires updated linked bodies and renewed QA of the remaining scope before advancement. Fast-path and skipped-validator exceptions do not waive per-AC verification.

> **GitHub mode closure-comment ordering (mandatory pre-check, not a memory item):** before posting any closure comment, run `gh issue view <number> --json state --jq '.state'`. **`CLOSED`** → the merged PR's `Closes #N`-style keyword already auto-closed the issue before Stage 4 ran; post the closure comment via a **separate** `gh issue comment` call — never combine it with `gh issue close --comment`, since `gh issue close` on an already-closed issue errors out and silently drops the comment along with it. **`OPEN`** → the combined `gh issue close --comment` call is safe to use as-is. Checking state first turns this from a rule to remember into a branch to execute — the prose warning alone was insufficient in practice (recurred in ST-000032 after already being documented from ST-000026).

### Non-behavioral fast path (`Type: non-behavioral`)

1. Orchestrator executes closure directly — no PO agent spawn:
   - Tick all AC checkboxes in the issue body (`gh issue edit` with `--body-file`); remove all `status:*` labels and add `status:done`; close the issue
2. **Start Story Workflow:** pipeline ends here

### Behavioral path (`Type: behavioral`)

1. **Spawn** Product Owner agent (**model policy: closure**); save its `session_handle` as `po_session` (resume via `po_session` if still active from a previous story in this sprint)
2. PO reads for closure only — **skip Project_Priming and reading/writing the Working Record**:
   - `.mt-agent-devkit/rules/Story_Standard_PO.md` (§14 AC rules); `Agent_Common_Bootstrap.md` (full file, every section mandatory)
   - `.mt-agent-devkit/rules/Product_Owner_Rules_Bootstrap.md`
   - `{RUNTIME_ROOT}/memory/Product_Owner_Memory.md`
3. PO verifies acceptance and closes the story:
   - **Elevated verification requirement check:** if the story body contains an explicit elevated/extra QA validation requirement section (distinct from standard AC), confirm QA's sign-off comment specifically addresses that requirement's named conditions before ticking AC — a generic "AC pass / tests green" comment is not sufficient closure evidence for a story that named a higher bar for itself.
   - **Closure signal when implementer = validator:** when the story's routing table (Stage 0) assigned the same role as both implementer and what would otherwise be validator, and that stage was accordingly skipped, the closure signal includes the applicable independent per-AC validation report required by the acceptance gate plus a confirmed merge; reviewer approval alone cannot verify an unexercised AC.
   - Tick AC checkboxes (`gh issue edit` with `--body-file`); remove all `status:*` labels and add `status:done`; close the issue
4. PO evaluates/completes its own metadata under `Agent_Common_Bootstrap.md §7`; only required triggers load/write its contribution before handoff.
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

Stage 5 validates completion evidence, not placeholder completeness; it never invents lessons or spawns clean roles for retros.

### 5.1 — Evaluate orchestrator observations

Evaluate the authoritative trigger policy in `Agent_Common_Bootstrap.md §7` against actual observations, not the mere presence of a bookkeeping list. Record the actual Orchestrator identity; write its contribution only when triggered. Independent review/QA fix counts share the policy's repeated-round threshold. Late triggers update the same role identity and preserve earlier lessons.

### 5.2 — Validate expected contributions

Run the bound retro-completion helper `check` against the explicit completed stage/actor identity list. Missing/unknown evaluations or required role contributions block story completion; do not convert placeholders to “not submitted” and continue. A clean-only result completes without reading or creating a story retro. A mixed result reads only the helper's required source paths. Preserve all source history for later review and aggregation. Explicit legacy-started state follows its prior owned-section completion path; new-contract runs never infer evaluation from old retro files.

### Orchestrator Observation Check — Stage 5

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` Exact expected completion identities recorded before actual stages, with no clean retro skeleton?
- `[skipped-step]` Orchestrator trigger evaluation recorded, with populated contribution only if required?
- `[skipped-step]` All expected evaluations known and required contributions/evidence verified before completion?
- `[skipped-step]` Ran `wc -c {RUNTIME_ROOT}/working-record/*_Working_Record.md`; append one bullet per file over 10,000 chars, naming the file and its size.
- `[skipped-step]` Ran `wc -c {RUNTIME_ROOT}/memory/*_Memory*.md` (covers both single-file memory and, for Dev/QA/TL, the two-tier live index + `_Archive` file — see `Agent_Common_Read_On_Demand.md §8`); append one bullet per file over 40,000 chars, naming the file and its size.
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

After completing Stage 5 → **for `continue sprint`: proceed to next story (Stage 0). For `start story`: proceed to Retro Review.**

