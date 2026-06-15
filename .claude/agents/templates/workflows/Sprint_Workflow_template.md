# Sprint Workflow

Triggered by: `"continue sprint"` or `"/sprint"` in CLAUDE.md

The orchestrator runs the [Shared Pipeline Stages](Shared_Pipeline_Stages.md) for each `status:ready` story in sequence. After Stage 4 of each story, PO promotes the next `status:ready` story if applicable. Pipeline completes when no more `status:ready` stories exist.

---

## Pipeline State

The orchestrator maintains `.claude/agents/tmp/sprint_pipeline_state.md` to support resumption after unexpected termination.

**On pipeline start — always check this file first:**
- If the file **exists** → read it and resume from the recorded story and stage
- If the file **does not exist** → start fresh from Stage 0 of the next `status:ready` story

**State file format:**
```markdown
# Sprint Pipeline State
**Story:** ST-XXXXXX
**Stage:** <0 | 1 | 2 | 3 | 4 | 5>
**Implementer:** <Developer | Technical Lead | QA | Business Analyst>
**Type:** <behavioral | non-behavioral>
**Feature:** <feature-name or none>
**Phase:** <phase-number or none>
**Sprint:** sprint-N
**Sprint Branch:** sprint-N-dev
**Story Branch:** story/<id>-<slug>
**Docs SHA:** <git short SHA captured at Stage 0>
**Loop Impl→Reviewer:** <count>
**Loop Impl→QA:** <count>
**Sessions:**
- impl_session: <agentId or empty>
- reviewer_session: <agentId or empty>
- qa_session: <agentId or empty>
- po_session: <agentId or empty>
**Updated:** YYYY-MM-DDTHH:MM
**Observations:**
```

> `Sprint Branch` and `Story Branch` are strict-mode only fields. In GitHub mode write `Sprint Branch: n/a` and `Story Branch: n/a`.

**Write rules:** Create/overwrite at Stage 0 entry of each new story — carry forward any existing `Observations:` entries when overwriting. **After every stage transition, update both `Stage` and `Updated` — these are mandatory, not optional.** Update `Sessions` on every agent spawn — **write `impl_session: PENDING` (or the relevant session field) to the state file immediately before making the spawn call**; overwrite with the real agentId as soon as the spawn returns. Never leave a session ID empty after spawning. Update loop counts at each retry cycle start. Set `Type` at Stage 0 based on story classification (see Shared Pipeline Stages §Stage 0). Set `Sprint` at Stage 0 by reading the sprint value from the story (`sprint-N` label in GitHub mode; `**Sprint:**` field in strict mode). Set `Sprint Branch` and `Story Branch` at Stage 0 in strict mode (derived per `Strict_Mode_Story_Guide.md` §Branch Naming); write `n/a` in GitHub mode. Set `Docs SHA` at Stage 0 via `git rev-parse --short HEAD`. Append a one-line bullet to `Observations:` whenever the orchestrator makes a judgment call not covered by this workflow or an agent reports friction. Delete after workflow review is complete.

---

## Strict-Mode Pre-Flight (run once before first story — strict mode only)

1. Identify the sprint name from the first `status:ready` story's `**Sprint:**` field (e.g., `sprint-1`)
2. Check if the sprint dev branch exists: `git branch --list sprint-N-dev`
   - Exists → `git checkout sprint-N-dev`
   - Missing → `git checkout -b sprint-N-dev` (from the user's current branch at invocation time)
3. Store `Sprint Branch: sprint-N-dev` in the pipeline state file

**Story discovery (strict mode):** Glob `.claude/agents/docs/stories/*.md`, read each file, filter by `**Status:** ready`. Sort by `**Sprint:**` field then by story ID (ascending). Process in that order.

**Story discovery (GitHub mode):** `gh issue list --label "status:ready"` as before.

---

## Pipeline Rules

- **ST-XXXXXX stories only** — skip any story whose ID does not match the `ST-XXXXXX` format
- **Skip `status:blocked` stories** — notify the user; do not run the pipeline for it
- Each stage must complete before the next starts
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles per story before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- Report pipeline status to the user after each stage
- If any agent is blocked, stop and report to the user before continuing
- **Stage 5 (Retrospective)** — after Stage 4's observation check completes, check the Stage 5 heading in `Shared_Pipeline_Stages.md`: if `[BETA: enabled]`, run Stage 5; if `[BETA: disabled]`, skip and proceed to the next story (Stage 0).
- **Strict-mode sprint complete notification** — when no more `status:ready` stories remain and before Batch Retro Review: notify the user: `"Sprint N complete. All stories merged into sprint-N-dev. Review and merge that branch into your own branch when ready — agents will not push or merge further."` Then proceed to Batch Retro Review.
- **Sprint end** — when no more `status:ready` stories remain:
  1. **Batch Retro Review** — process each story's retro file one by one in story order. For each:
     a. Read `.claude/agents/retros/ST-XXXXXX_retro.md`
     b. Collect all signal-tagged items (`[context]`, `[instruction]`, `[workflow]`, `[failure]`) from every section
     c. Present collected items to the user as proposed improvements; for each approved item, apply the change targeting the right artifact:
        - `[context]` → priming docs or agent memory files
        - `[instruction]` → agent instruction files (`.claude/agents/*_instructions.md`)
        - `[workflow]` → workflow files (`.claude/agents/workflows/`)
        - `[failure]` → rules or guardrail files (`.claude/agents/rules/`)
     d. Append a story section to the sprint summary file. Read `Sprint` from the state file: `sprint-N` → `.claude/agents/retros/sprint_N_summary.md`. Create the file if it does not exist:
        ```markdown
        # Sprint N — Retro Summary
        **Sprint:** sprint-N
        **Last Updated:** YYYY-MM-DD
        ```
        Then append:
        ```markdown
        ---

        ## ST-XXXXXX — <story title>
        **Date:** YYYY-MM-DD
        **Loop counts:** Impl→Reviewer: N | Impl→QA: N

        ### Findings
        - `[signal-type]` <item> *(role)*

        ### What Worked Well
        - <item> *(role)*

        ### Actions Applied
        - `<file-path>` — <one-line description of change>
        ```
        Source findings and "what worked well" from the retro file. Source loop counts from the state file. List every file changed under "Actions Applied"; write `*(none)*` if no changes were applied. Update `**Last Updated:**` at the top after each story section is appended.
     e. Delete `.claude/agents/retros/ST-XXXXXX_retro.md`
     — Complete all stories before moving to step 2.
  2. **Sprint Consolidated Summary** — read the completed sprint summary file. Append a final `## Sprint Consolidated Summary` section covering: common themes across stories, recurring blockers, what went well, and top 1–3 process improvement suggestions. Present the full file to the user.
  3. **Cleanup** — delete the state file, then delete any remaining files in `.claude/agents/tmp/` with `rm .claude/agents/tmp/*.md`. Agents must also delete any tmp files they created immediately after the file is no longer needed (e.g., after `gh` call using `--body-file`).
