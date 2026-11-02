<!-- Included by: templates/github/workflows/Shared_Pipeline_Stages_template.md, templates/strict/workflows/Shared_Pipeline_Stages_template.md -->

<!-- SHARED-START -->
# Shared Pipeline Stages

Used by [Sprint Workflow](Sprint_Workflow.md) and [Start Story Workflow](Start_Story_Workflow.md). Session IDs are maintained by the orchestrator across stages.

---

---

## Explicit Manifest Dispatch — Every Worker Assignment

Before every story worker spawn or resume, build and validate a manifest with `.mt-agent-devkit/scripts/read_manifest.py` using the single `.mt-agent-devkit/contracts/read-routing.json`; follow `.mt-agent-devkit/contracts/Read_Manifest.md`. This applies to implementation, independent TL/Developer review, QA, PO closure, all fix/recheck resumes, and triggered specialist questions. Supply concrete provider/layout/bindings, role/task/stage/session identity, bounded canonical story/evidence inputs and new delta pointers. Select the registry task; do not maintain another startup list in this workflow. Unsupported or insufficient specialist context blocks rather than broadening startup.

Immediately before the selected adapter dispatch, validate against current sources and routing. BLOCKED stops before spawning. Pass the validated manifest and Worker Entry Read Contract below verbatim with the ordinary assignment. Successful returned-coverage receipts are explicit worker attestations after truncation recovery; a live session, summary, digest, or build PASS never proves a read. Missing identity follows fresh/expired reads; omission requires matching provider/session/source/coverage/relevant-route provenance. Fresh and expired specialist/closure tasks retain their reduced contracts.

During work extend and validate for observable triggers before governed actions. Register accepted completion, telemetry and waiting triggers through the canonical registry only; preserve their existing authoritative policies. No initial manifest suppresses a new safety rule, authorizes a mutation, or removes independent review/QA. Record manifest/receipt pointers in bound runtime handoffs; never commit them. Sequential supported reads remain valid when batching is unavailable.

---

## Worker Entry Read Contract

For every fresh worker spawn or expired-session restart, include this contract verbatim in the ordinary role packet, together with the selected adapter, concrete bindings and canonical role instruction path. It applies before discovery commands or shell-based context loading; a rule inside an unread role file cannot enforce that boundary by itself. A valid same-session resume retains only unchanged reads with successful returned-coverage provenance; the validated manifest supplies new task/evidence deltas and all invalidated or unknown reads.

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

For each new Stage 0 entry, verify the story base **before any per-story pipeline-state, retro, issue-comment, status, or product write**. Strict mode first completes its Sprint/Start Story pre-flight without writing per-story state, so `sprint-N-dev` is the checked-out, verified execution base. Read the story's immutable `Base Branch` (GitHub) or use that verified sprint branch (strict); a missing legacy value blocks for explicit user selection. Derive the intended story-branch name using `Story_Standard.md` or `Strict_Mode_Story_Guide.md`, then run `branch_preflight.py inspect --mode <github|strict> --base <base> --story-branch <story-branch>`. Keep the full Base SHA and, in GitHub mode, the full Remote Base SHA in the current invocation until Stage 1. A BLOCKED result stops the workflow without a per-story write or recovery action. Stage 1 uses `create`, which repeats every check before branch creation.

Stories entering directly at Stage 2 or 3 use their existing branch and stage state; this new-branch preflight does not create another branch for them.

---

## Bug Reproduction Pre-Flight (runs immediately ahead of Stage 0 — bug stories only)

Runs once for each new `status:ready` story entering Stage 0 — Sprint Workflow's per-story loop or Start Story Workflow's ready entry. A resumed `status:in-progress` story continues from its recorded stage without rerunning this check. Does **not** run when a story enters directly at Stage 2 or Stage 3 (already past implementation). Not to be confused with the per-mode "Strict-Mode Pre-Flight" sprint/branch setup step in `Sprint_Workflow.md` / `Start_Story_Workflow.md` — this is a separate, per-story check.

**1. Is this story subject to pre-flight?**
- **GitHub mode:** read the issue's labels (`gh issue view <number> --json labels`) — subject to pre-flight only if the `bug` label is present.
- **Strict mode:** read `{{AGENT_DIR_PREFIX}}/agents/docs/stories/ST-XXXXXX.md` — subject to pre-flight only if the body contains a `## Reproduction` section (strict mode has no label mechanism; the section's presence is the bug-story marker — see the `po-write-story` skill).
- **Not a bug story** → skip this entire section; proceed directly to Stage 0.

**2. Read the Repro Command.** Parse `**Repro Command:**` from the story's `## Reproduction` section (GitHub: issue body; strict: story MD body).
- **Field absent, empty, or literally `unknown`** → **skip path**: proceed directly to Stage 0 — today's behavior (Stage 1 implementer reproduces as part of its own work) is preserved unchanged. Do not attempt execution.
- **Field present with a real command** → continue to step 3.

**3. Attempt reproduction.** Run the `Repro Command` value **verbatim** — never a command synthesised from AC prose or any other field — in the project root, using whichever shell tool the command's syntax implies.
- **The tool itself cannot be invoked** (the shell reports the command/binary is missing — e.g. `command not found`, `'X' is not recognized`, `ENOENT` — a tooling-availability error, not a test result) → **skip path**: proceed directly to Stage 0, same as step 2's skip. Record nothing further.
- **The command executes to completion** (regardless of exit code) → continue to step 4.

**4. Evaluate the result** against the story's `**Expected:**` / `**Actual:**` fields:
- **Observed output matches `**Actual:**`** → **Reproduced.**
  - Record a short repro artifact (command run, tool used, observed failure) and pass it directly in the Stage 1 spawn prompt, in addition to the story body, as the implementer's confirmed starting evidence.
  - Proceed to Stage 0 → Stage 1 as normal.
- **Observed output does not match `**Actual:**`** (command passes cleanly, or fails in a way inconsistent with the reported defect) → **Not reproduced.**
  - Do **not** spawn any Stage 1 agent for this story.
  - Report the repro steps and result:
    - **GitHub mode:** post a comment on the issue with the command run, the story's `**Expected:**`/`**Actual:**`, and what was actually observed
    - **Strict mode:** append a comment entry to the story MD `## Comments` section with the same content
  - Leave the story's status label/field **unchanged**.
  - **Sprint Workflow:** append the story ID to the `Repro Skipped:` field in the pipeline state file; skip this story and continue to the next `status:ready` story not already recorded in `Repro Skipped:` for this run.
  - **Start Story Workflow:** report the result to the user and **stop** — do not proceed to Stage 0 for this story.

---

## Stage 0 — Implementer Routing

Enter Stage 0 only after Story Base Preflight passed. All pipeline-state writes below use the verified result; no story status or product write occurs until Stage 1 creates and verifies the story branch.

**Read the story body** to get `**Assigned:**` and classify the story:

**If `Mode: github`:** Run `gh issue view <number> --json body,labels` to read the story body and labels.

**If `Mode: strict`:** Read `{{AGENT_DIR_PREFIX}}/agents/docs/stories/ST-XXXXXX.md` directly.

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
QA re-check and consultation resume. Explicit read manifests consume these
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


## Waiting for CI and long verification

In GitHub mode, pending CI routes to `.mt-agent-devkit/contracts/Wait_Work.md` (ci-watch); keep its wait ID and native command/session identity. PENDING cannot advance review or merge; FAIL/cancel/timeout routes to fixes. NO RUN uses the existing explicit zero-check evidence gate, never automatic PASS. After waiting, revalidate exact head and approval scope. Strict mode uses local verification without GitHub.

For long local verification, use `.mt-agent-devkit/contracts/Local_Verify.md` (local-verify) with the full required command, selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity. Missing completion is not success. Keep provider-local logs and independent verification gates.

These observable triggers route to the shared waiting contracts; Canonical read routing registers them once. Do not create another startup read list. Selected adapters own command lifecycle support; unverified native wakeup remains unavailable.

---

## Stage 1 — Implementation

**Orchestrator pre-spawn:** initialize `Retro Contract: exception-v1` and carry an explicit expected completion identity list at the bound runtime path before each actual stage/actor executes. Follow `Agent_Common_Bootstrap.md §7`; do not create a retro skeleton. Observe trigger events throughout work. Already-started legacy runs explicitly keep their prior contract and existing history.

1. **Spawn** the agent matching the `Implementer` role (**model: sonnet**)
2. Agent reads its own instruction files, memory, and rules
3. **Read the story:**
   - **GitHub mode:** Agent reads the assigned story from GitHub (`status:in-progress` or next `status:ready` story via `gh issue view`)
   - **Strict mode:** Agent reads `{{AGENT_DIR_PREFIX}}/agents/docs/stories/ST-XXXXXX.md` directly
4. **New `status:ready` entry that has not passed interrupted Stage 1 recovery, before the first story status or product write** → run `branch_preflight.py create` for the branch named in Story Base Preflight, passing its full verified Base SHA and, in GitHub mode, its full Remote Base SHA as `--expected-remote-sha`. `create` repeats inspection; a BLOCKED result stops for direction without stash, reset, rebase, or auto-repair. Record the story branch only after successful full-SHA verification. **Resumed `status:in-progress` entry:** use the recorded stage, story branch, and session; do not call `create` again. If the recorded branch or state cannot be verified, stop for state recovery before any write.
5. **Strict mode:** its one story branch is `story/<external-id>-<slug>` (or `story/ST-XXXXXX-<slug>`) from the verified `sprint-N-dev` base. Do not create or switch to a second story branch.
6. **After successful branch creation on a new entry** → write `impl_session: <agentId>` to state, then update story status to `in-progress`:
   - **GitHub mode:** update story label to `status:in-progress`
   - **Strict mode:** edit `**Status:** in-progress` in the story MD file
7. **CI/CD check:**
   - **GitHub mode:** if the story's Technical Scope includes any file under `.github/workflows/`, the implementer **must** follow `{{AGENT_DIR_PREFIX}}/agents/rules/CICD_Validation_Guide.md` before opening a PR
   - **Strict mode:** CI gate is skipped entirely — no CI validation required
8. **Deletion pre-check** — if the story involves deleting files (housekeeping, cleanup, or any story whose scope lists files to remove): before executing any `git rm` or file deletion, record the planned deletions, then proceed immediately. This gives the reviewer and user a visible record of what was removed and why.
   - **GitHub mode:** post a comment on the GitHub Issue listing every file planned for deletion
   - **Strict mode:** append a comment entry to the story MD `## Comments` section listing every file planned for deletion
9. Agent implements and updates working record; commits use the format `<external-id> [ST-XXXXXX]: <message>` or `ST-XXXXXX: <message>` (see `Strict_Mode_Story_Guide.md` §Commit Message Format)
10. **After implementation is ready for review** → update story status to `review`:
    - **GitHub mode:** open PR; update story label to `status:review`
    - **Strict mode:** create `{{AGENT_DIR_PREFIX}}/agents/docs/reviews/ST-XXXXXX_review.md` (see `Strict_Mode_Story_Guide.md` §Local Review Record); edit `**Status:** review` in the story MD; append comment entry to `## Comments` noting branch is ready for review
11. Agent evaluates/completes its bound metadata under `Agent_Common_Bootstrap.md §7`; only required triggers load/write its contribution before handoff.
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
   - If `Owner` is PO → spawn/resume Product Owner (**model: sonnet**) with the question and story context; the assignment names the `po-answer-questions` skill (manifest task `scope_question`)
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

1. Resolve **who to tag** following the lookup order in `{{AGENT_DIR_PREFIX}}/agents/rules/Blocked_Request.md` § Step 1 — if no match is found, report back to the orchestrator to ask the user before proceeding
2. Fill in the template with the resolved name, confirmed items, missing items, and helpful commands
3. Write the filled-in content to `{{AGENT_DIR_PREFIX}}/agents/tmp/blocked_<story-id>.md`
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
- `[skipped-step]` **Strict mode only:** Review-record MD created at `{{AGENT_DIR_PREFIX}}/agents/docs/reviews/ST-XXXXXX_review.md`?
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
     - **GitHub mode:** post approval as `gh pr comment` on the PR, citing the current head SHA as `**Approved-SHA:** <sha>` (`gh pr view <PR-number> --json headRefOid --jq '.headRefOid'`) — the Merge Procedure's Approval-scope gate reads this back later
     - **Strict mode:** update review-record MD `**Status:** approved` and `## Verdict` section, recording `**Approved-SHA:** <sha>` (`git rev-parse HEAD` on the story branch); append approval comment entry to story MD `## Comments`
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
   - **GitHub mode:** reviewer reviews PR (use `gh pr comment` — GitHub blocks self-approval via `gh pr review --approve`); an approval comment cites the current head SHA as `**Approved-SHA:** <sha>` (`gh pr view <PR-number> --json headRefOid --jq '.headRefOid'`) — the Merge Procedure's Approval-scope gate reads this back later
   - **Strict mode:** reviewer reads review-record MD + runs `git diff sprint-N-dev...story/<branch>` + reads changed files; writes notes and verdict to review-record MD, recording `**Approved-SHA:** <sha>` (`git rev-parse HEAD` on the story branch) on approval; appends summary comment entry to story MD `## Comments`
   - **Stub/TODO re-check:** confirm the implementer's Stage 1 scan was actually done — spot-check for stub markers/trivial-return patterns in AC-functional methods. A hit with no owning backlog story blocks approval (see `Technical_Lead_Rules_Bootstrap.md §2` for the full review checklist, including the CI-execution/SHA/red-diagnosis and dependency-pin checks).
4. **If changes requested** → resume Implementer via `SendMessage` to `impl_session` with reviewer feedback (spawn new if expired); on Implementer completion **resume Reviewer via `reviewer_session` to re-review** (spawn new if expired)
5. Reviewer evaluates/completes its own metadata under `Agent_Common_Bootstrap.md §7`; only required triggers load/write its contribution before handoff.
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

**Acceptance gate — every route:** Before recording testing-pass or invoking Merge Procedure, read and apply `Story_Standard.md §14` to the current canonical scope. Require the applicable independent validation report with a verdict/evidence for every remaining AC. Any FAIL, NOT VERIFIED, absent verdict, or insufficient evidence stops advancement; neither green automation, reviewer approval, skipped validation nor a non-behavioral fast path overrides this gate. Record the reason and missing evidence, retain the unresolved testing/open state, and use the existing external-blocker procedure when needed. Scope splits must be approved, tracked and linked in revised story bodies before renewed QA sign-off; never reinterpret prior NOT VERIFIED as PASS.

> **Merge gate — behavioral stories:** The Merge Procedure fires only at behavioral path step 9 — after QA confirms automation passes. Do NOT execute it at Stage 3 entry or immediately after Stage 2 approval.

1. **If `Implementer` is `QA`** → skip a separate QA agent; always **spawn** Product Owner (**model: sonnet**, manifest task `po_validation`) and name the `po-validate-ac` skill (`.mt-agent-devkit/skills/po-validate-ac/SKILL.md`) in the assignment. PO validates each AC independently and records the applicable per-AC report under the acceptance gate before the orchestrator executes the **Merge Procedure** below, then proceed to Stage 4

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
6. QA reads `qa_instructions.md` + `QA_Memory.md` + `QA_Rules_Bootstrap.md`
7. QA validates story acceptance criteria, runs test scenarios, checks regression risk
   - If Stage 1 reported `Outcome: verification-only` → read the implementer's cited evidence and perform **one** targeted spot-check instead of a full environment re-verification; escalate to full re-verification only if there's a specific reason to distrust the evidence. Skip the test-scenario document per `QA_Rules_Bootstrap.md §4`'s verification-only exception.
8. **If story AC issues found** → resume Implementer via `SendMessage` to `impl_session` with QA findings (spawn new if expired); on Implementer completion **resume QA via `SendMessage` to `qa_session`** to revalidate (spawn new if expired)
9. **If story AC passed** → QA updates automation coverage for the story then runs the full automation suite to check for regressions (see QA Rules §8–§9)
   - **If automation fails** → QA reports regression failures:
     - **GitHub mode:** as a story comment
     - **Strict mode:** append to story MD `## Comments`
     → resume Implementer via `impl_session` to fix (spawn new if expired); on completion resume QA to revalidate (counts toward loop limit)
   - **If automation passes** → QA evaluates/completes its bound metadata under `Agent_Common_Bootstrap.md §7`, loading/writing only triggered contributions; orchestrator executes the **Merge Procedure** below
10. On merge confirmed → proceed to Stage 4

### Merge Procedure (orchestrator executes directly — no agent spawn)

**Acceptance evidence pre-check (both modes, before any merge command):** Re-read the current story scope and the applicable independent per-AC validation report under `Story_Standard.md §14`. Confirm every remaining AC is PASS with sufficient evidence against the artifact being merged. A missing report, stale scope, FAIL, or NOT VERIFIED aborts merge even if CI/review passed. For an approved split, verify the tracked follow-up/body links and renewed QA confirmation after the scope update. Existing CI and approval-SHA gates remain independent and required where applicable.

**If `Mode: github`:**
0. **CI-check gate (mandatory, independent of reviewer sign-off):** run `gh pr checks <PR-number> --repo {github-org}/{repo-name}`. This mechanical backstop recognizes three distinct states at head — resolve each on its own terms, and never treat "no checks reported" as equivalent to "checks passed":
   - **State 1 — checks reported, all `completed`, none `fail`:** gate satisfied against the head SHA.
   - **State 2 — pending or failed evidence:** both block advancement, but waiting is distinct from failure. Pending/in-progress checks route to ci-watch using a bounded supported wait; window expiry remains PENDING. Failed, cancelled or timed-out checks route to fixes or a truthful blocked report. Re-run the gate at the exact current head after completion; reviewer approval does not override it.
   - **State 3 — zero checks reported:** this is **not** State 1. Determine which of two distinct causes applies before proceeding — they resolve differently:
     - **(a) A CI-suppression token (e.g. `[skip ci]`) sits in the head commit's message.** This suppresses the run for the whole push, not for a specific path — a `pull_request`-triggered `paths:` filter is evaluated against the PR's entire changed-file set on every push, not the individually pushed commit, so a bookkeeping-only commit landing last does not by itself explain an empty rollup when the total diff still contains a CI-eligible path (tested and disproven — ST-000148: a retro-only push still produced a fresh green run at the new head; there is no commit-ordering hazard). To resolve: walk the branch's commits backward from head and find the most recent SHA that actually has a recorded check-run (e.g. `gh api repos/{github-org}/{repo-name}/commits/<SHA>/check-runs`) — that SHA is the last push that wasn't suppressed. If its run is `completed` and passing, the gate is satisfied **against that SHA**, not head; record which SHA was used. If no such run exists, or it failed, treat this the same as State 2 and abort.
     - **(b) No commit's push ever produced a run because no path in the PR's whole changed-file set (`gh pr diff <PR-number> --name-only`) matches any workflow's `paths:` filter.** Nothing was ever eligible — there is no run to find at any SHA, and none will appear. State this outcome explicitly rather than proceeding silently: the merge decision rests entirely on reviewer sign-off, with the absence of any eligible check recorded as a deliberate, evidenced exception — not as a passed check.
   - **Prior-run scope:** record the prior evidence SHA, current head and every file changed between them; verify the suppression cause and that the permitted exception covers that scope. Helper prior candidates remain NO RUN until this explicit decision.
   - **Audit requirement (whichever state leads to a merge):** before step 2 below, post a `gh pr comment` recording which state applied (1 / 3a / 3b) and the evidence used — the head SHA for State 1, the resolved SHA and its run for 3(a), or the `paths:` non-match determination for 3(b). This is what makes the merge decision auditable after the fact.
0a. **Approval-scope gate (mandatory, independent of the CI gate):** find the most recent `**Approved-SHA:**` the reviewer cited at Stage 2 and diff it against the current head: `git diff <Approved-SHA> <head-SHA> --name-only`.
    - **No post-approval exception for agent runtime state:** Memory, Working Records, retrospectives, telemetry, and pipeline state are uncommitted. Any tracked change since `Approved-SHA`, including a test-scenario document, requires a refreshed review.
    - **Anything else added or modified since the Approved-SHA** (any AC-functional, template, workflow, or code content the reviewer did not see) → the sign-off no longer covers the artifact about to merge. Do not merge; resume the reviewer (`reviewer_session`) with just the post-approval delta for a fresh look, and get a refreshed `Approved-SHA` before retrying this gate.
    - Add the outcome (unchanged / bookkeeping-only / re-review triggered) to the same audit comment as step 0.
1. Get the PR branch name: `gh pr view <PR-number> --repo {github-org}/{repo-name} --json headRefName --jq '.headRefName'`
2. Merge the PR: `gh pr merge <PR-number> --repo {github-org}/{repo-name} --merge`
3. Delete the remote dev branch: `git push origin --delete <branch-name>`
4. Switch local branch to target: `git checkout <target-branch>`
5. Pull to sync: `git pull origin <target-branch>`

> **No-branch-protection note:** on a repo without required-status-checks support (e.g. a private repo without a paid plan), steps 0 and 0a above are the *only* enforcement that exists — there is no platform backstop to fall back on if either is skipped. Treat both as non-optional baseline pipeline behavior, not best-effort guidance.

**If `Mode: strict`:**
1. Get the story branch name from the pipeline state file (`Story Branch:` field)
2. `git checkout sprint-N-dev`
3. `git merge story/<branch-name> --no-ff -m "Merge ST-XXXXXX: <story title>"`
4. `git branch -d story/<branch-name>`
5. Append comment entry to story MD `## Comments`: `"[YYYY-MM-DD] Orchestrator — merged into sprint-N-dev. Awaiting PO acceptance."`
6. Notify user: `"ST-XXXXXX merged into sprint-N-dev — awaiting PO acceptance"`
   - Do NOT touch the user's branch
   - Do NOT push to remote

> **Strict mode has no CI concept** — State 1/2/3 and the CI-check gate are GitHub-mode only, since strict mode never runs CI checks at all. The Approval-scope gate's underlying principle still applies (the review-record MD's `**Approved-SHA:**` names a specific commit) but is documented here as a principle, not a mechanically enforced step, since strict-mode merges are a direct `git merge` with no PR object to gate.

### Orchestrator Observation Check — Stage 3

Append a bullet to `Observations:` for each item that did **not** happen:

- `[skipped-step]` If QA agent spawned: `qa_session` saved in state file immediately after spawn?
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

---

## Stage 4 — PO Story Closure

**Acceptance pre-check — both paths and modes:** Before any checkbox, done-status or closure write, apply `Story_Standard.md §14`: confirm merge and current independent PASS evidence for every remaining AC. FAIL, NOT VERIFIED, missing verdicts or insufficient evidence stop closure; a previous testing-pass summary is insufficient when its scope/evidence is stale. An auto-closed issue is not acceptance evidence; reopen it if unresolved verification remains. An approved tracked split requires updated linked bodies and renewed QA of the remaining scope before advancement. Fast-path and skipped-validator exceptions do not waive per-AC verification.

> **GitHub mode closure-comment ordering (mandatory pre-check on both paths, not a memory item):** before posting any closure comment, apply the closure-comment ordering in the `po-verify-close` skill (`.mt-agent-devkit/skills/po-verify-close/SKILL.md`, Close step 1): check `gh issue view <number> --json state --jq '.state'` first, and on `CLOSED` post the comment with a separate `gh issue comment`. Checking state first turns this from a rule to remember into a branch to execute — the prose warning alone was insufficient in practice (recurred in ST-000032 after already being documented from ST-000026).

### Non-behavioral fast path (`Type: non-behavioral`)

1. Orchestrator executes closure directly — no PO agent spawn:
   - **GitHub mode:** tick all AC checkboxes in the issue body (`gh issue edit` with `--body-file`); remove all `status:*` labels and add `status:done`; close the issue
   - **Strict mode:** edit AC checkboxes to `[x]` directly in the story MD file; edit `**Status:** done`
2. **Start Story Workflow:** pipeline ends here

### Behavioral path (`Type: behavioral`)

1. **Spawn** Product Owner agent (**model: haiku**, manifest task `closure`); save its `agentId` as `po_session` (resume via `po_session` if still active from a previous story in this sprint); name the `po-verify-close` skill in the assignment
2. PO reads for closure only — **skip Project_Priming and reading/writing the Working Record**: `Agent_Common_Bootstrap.md` (full file, every section mandatory), `{{AGENT_DIR_PREFIX}}/agents/memory/Product_Owner_Memory.md`, and the `po-core`, `po-verify-close` and `po-comment` skills
3. PO verifies acceptance and closes the story per `po-verify-close` (`.mt-agent-devkit/skills/po-verify-close/SKILL.md`): acceptance questions, evidence check including the elevated-verification and implementer = validator closure signals, AC ticking (`--body-file` in github mode; the story MD in strict mode), `status:done` and close (strict mode: `**Status:** done` plus a closure comment entry in the story MD `## Comments`)
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
- `[skipped-step]` Ran `wc -c {{AGENT_DIR_PREFIX}}/agents/working-record/*_Working_Record.md`; append one bullet per file over the `**Working record cap:**` value in `{{ROOT_FILE}}` (default 4,000 if absent), naming the file and its size.
- `[skipped-step]` Ran `wc -c {{AGENT_DIR_PREFIX}}/agents/memory/*_Memory.md`; append one bullet per file over the `**Memory file cap:**` value in `{{ROOT_FILE}}` (default 10,000 if absent), naming the file and its size.
- `[skipped-step]` `Stage` and `Updated` refreshed in state file after this transition?

After completing Stage 5 → **for `continue sprint`: proceed to next story (Stage 0). For `start story`: proceed to Retro Review.**
<!-- SHARED-END -->
