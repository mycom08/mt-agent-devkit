# Sprint Workflow

Triggered by: `"continue sprint"` or `"/sprint"` in the selected provider entrypoint

The orchestrator runs the [Shared Pipeline Stages](Shared_Pipeline_Stages.md) for each `status:ready` story in sequence. After Stage 4 of each story, PO promotes the next `status:ready` story if applicable. Pipeline completes when no more `status:ready` stories exist.

---

## Pipeline State

The run-level pointer index is `{RUN_ROOT}/tmp/sprint_story_index.json`; each
indexed story owns `{STORY_RUNTIME_ROOT}/tmp/sprint_pipeline_state.md`.
Bind `{RUNTIME_ROOT}` to the current indexed story only. Use
`provider_context.record_sprint_story` after its preflight PASS, preserving the
ordered prior pointers. The index records provider, run ID and current story;
stage, sessions and loop counts stay in each story's pipeline state.

**On pipeline start — always check the run index first:**
- If the index **exists** → validate provider/run identity, resolve its current
  story with `sprint_story_roots(..., resume=True)`, then read that story's state
  and resume its recorded stage. Missing/mismatched state blocks before writes.
- If the file **does not exist** → start the next `status:ready` story at Story Base Preflight, then Bug Reproduction Pre-Flight, then Stage 0

**State file format:**
```markdown
# Sprint Pipeline State
**Story:** ST-XXXXXX
**Provider:** <selected provider>
**Run ID:** <run-id>
**Runtime Root:** <this indexed story root>
**Stage:** <0 | 1 | 2 | 3 | 4 | 5>
**Implementer:** <Developer | Technical Lead | QA | Business Analyst | UI/UX Designer>
**Type:** <behavioral | non-behavioral>
**Feature:** <feature-name or none>
**Phase:** <phase-number or none>
**Sprint:** sprint-N
**Sprint Branch:** n/a
**Story Branch:** pending
**Docs SHA:** <git short SHA captured at Stage 0>
**Loop Impl→Reviewer:** <count>
**Loop Impl→QA:** <count>
**Repro Skipped:** <comma-separated story IDs not reproduced this run, or empty>
**Sessions:**
- impl_session: <session_handle or empty>
- reviewer_session: <session_handle or empty>
- qa_session: <session_handle or empty>
- po_session: <session_handle or empty>
**Updated:** YYYY-MM-DDTHH:MM
**Observations:**
```

> `Sprint Branch` is strict-mode only; in GitHub mode write `Sprint Branch: n/a`. Record the actual `Story Branch` in either mode after verified creation. On Stage 0 entry, use `Story Branch: pending` until Stage 1 succeeds.

The Story Base Preflight `inspect` PASS in `Shared_Pipeline_Stages.md` verifies the per-story base before Stage 0 state writes. Stage 1 `create` must also succeed before story status or product writes.

**Write rules:** Create/overwrite at Stage 0 entry of each new story — carry forward any existing `Observations:` **and `Repro Skipped:`** entries when overwriting. **After every stage transition, update both `Stage` and `Updated` — these are mandatory, not optional.** Update `Sessions` on every agent spawn — **write `impl_session: PENDING` (or the relevant session field) to the state file immediately before making the spawn call**; overwrite with the real session_handle as soon as the spawn returns. Never leave a session ID empty after spawning. Update loop counts at each retry cycle start. Set `Type` at Stage 0 based on story classification (see Shared Pipeline Stages §Stage 0). Set `Sprint` at Stage 0 by reading the sprint value from the story (`sprint-N` label in GitHub mode; `**Sprint:**` field in strict mode). Set `Sprint Branch` and `Story Branch` at Stage 0 in strict mode (derived per `Strict_Mode_Story_Guide.md` §Branch Naming); write `Sprint Branch: n/a` in GitHub mode and record Story Branch after Stage 1 creation. Set `Docs SHA` at Stage 0 via `git rev-parse --short HEAD`. Append the story ID to `Repro Skipped:` whenever the Bug Reproduction Pre-Flight step (`Shared_Pipeline_Stages.md`) determines a story was not reproduced — this field persists across story transitions within the current run only; it is never carried into a fresh run (a new `continue sprint` after the state file is deleted starts with `Repro Skipped:` empty, so a story a human has since added repro steps to is re-attempted). Append a one-line bullet to `Observations:` whenever the orchestrator makes a judgment call not covered by this workflow or an agent reports friction. Delete after workflow review is complete.

---

## Pipeline Rules

- **ST-XXXXXX stories only** — skip any story whose ID does not match the `ST-XXXXXX` format
- **Skip `status:blocked` stories** — notify the user; do not run the pipeline for it
- **Skip stories already recorded in `Repro Skipped:`** for the current run — do not re-select them; see Bug Reproduction Pre-Flight in `Shared_Pipeline_Stages.md`
- Each stage must complete before the next starts
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles per story before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- Report pipeline status to the user after each stage
- If any agent is blocked, stop and report to the user before continuing
- **Stage 5 (Retrospective)** — after Stage 4's observation check completes, check the Stage 5 heading in `Shared_Pipeline_Stages.md`: if `[BETA: enabled]`, run Stage 5; if `[BETA: disabled]`, skip and proceed to the next story (Stage 0).
- **Sprint end** — when no more `status:ready` stories remain:
  1. **Batch Retro Review** — process each story's retro file one by one in story order. For each:
     a. Iterate the run index in story order. Bind `{STORY_RUNTIME_ROOT}` to
        that entry's validated root and load its own pipeline state for the
        story ID, title, Sprint and loop counts. Read
        `{STORY_RUNTIME_ROOT}/retros/ST-XXXXXX_retro.md`; do not reuse the current
        story's `{RUNTIME_ROOT}` for an earlier story.
     b. Collect all signal-tagged items (`[context]`, `[instruction]`, `[workflow]`, `[failure]`) from every section
     c. Present collected items to the user as proposed improvements; for each approved item, apply the change targeting the right artifact:
        - `[context]` → priming docs or agent memory files
        - `[instruction]` → agent instruction files (`.mt-agent-devkit/instructions/`)
        - `[workflow]` → workflow files (`.mt-agent-devkit/workflows/`)
        - `[failure]` → rules or guardrail files (`.mt-agent-devkit/rules/`)

        **Routing check for `[context]` items:** before applying a `[context]` item as a priming/memory edit, ask explicitly — *does this note describe a missing capability or limitation with no existing backlog story that will ever close it?* If yes, route it to backlog creation instead of, or in addition to, the priming/memory edit.
     d. Append a story section to the run-level sprint summary file. Read `Sprint`
        from this story's saved state: `sprint-N` →
        `{RUN_ROOT}/retros/sprint_N_summary.md`. Create the file if it does not exist:
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
     e. Delete only this processed story's `{STORY_RUNTIME_ROOT}/retros/ST-XXXXXX_retro.md`.
        Retain prior story states until all batch sections have been sourced.
     — Complete all stories before moving to step 2.
  2. **Sprint Consolidated Summary** — read the completed sprint summary file. Append a final `## Sprint Consolidated Summary` section covering: common themes across stories, recurring blockers, what went well, and top 1–3 process improvement suggestions. Present the full file to the user.
  3. **Devkit Contribution** — optional sharing of sprint retro signals with the devkit team. The sprint pipeline continues regardless of the user's answer.

     a. **Privacy scan** — read `{RUN_ROOT}/retros/sprint_N_summary.md` (resolve N
        from the indexed story states). Extract all lines from every `### Findings`
        section across all story blocks and apply the Privacy Rule from `Retro_Rules.md`.
        Remove/generalise project, repository, domain path, business, client and user identifiers.

     b. **Present and prompt** — show the cleaned signal items to the user, grouped by type (`[context]`, `[instruction]`, `[workflow]`, `[failure]`). Then ask:
        > "Share these improvements with the devkit team? (yes/no) — the sprint pipeline continues either way."

     c. **If yes:**
        i. Build the export file content per `community-retros/README.md` format. Use filename pattern `sprint-<N>_<YYYY-MM-DD>.md`. Sections with no items must include `- None.` to keep structure consistent.
           ```markdown
           # Retro Export

           **Sprint:** <N>
           **Date:** <YYYY-MM-DD>

           ## Signal Items

           ### [context]
           - <generalised item, or "None.">

           ### [instruction]
           - <generalised item, or "None.">

           ### [workflow]
           - <generalised item, or "None.">

           ### [failure]
           - <generalised item, or "None.">

           ## What Worked Well
           - <item, or "None.">
           ```
        ii. Write the export file to `{RUNTIME_ROOT}/retros/devkit_contribution_sprint_N.md`.
        iii. Run `gh auth status` to check authentication:
             - **Authenticated:** run:
               ```bash
               gh issue create --repo mycom08/mt-agent-devkit \
                 --title "Community Retro Contribution — Sprint N (YYYY-MM-DD)" \
                 --label "retro:contribution" \
                 --body-file {RUNTIME_ROOT}/retros/devkit_contribution_sprint_N.md
               ```
               Report the Issue URL to the user. Delete the local export file.
             - **Not authenticated or `gh` unavailable:** inform the user that the export file has been written to `{RUNTIME_ROOT}/retros/devkit_contribution_sprint_N.md`. Instruct them to open an Issue labeled `retro:contribution` on `mycom08/mt-agent-devkit` with the export file contents, so the `apply retros` workflow can find it.

     d. **If no:** skip to step 4 (Memory Pruning).

  4. **Memory Pruning** — runs regardless of the Devkit Contribution answer above. Follow `Retro_Rules.md`'s "Sprint-End Memory Pruning" section: glob `{RUNTIME_ROOT}/memory/*_Memory.md`, apply the inclusion test and "Never record" list from `Agent_Common_Read_On_Demand.md §1` to each file's `## Stored Facts` entries, delete/merge what fails it, and report a one-line kept/pruned summary per file to the user. Orchestrator-direct, no agent spawn. This replaces the old per-write-only pruning judgment call with a step that actually runs on a schedule.

  5. **Cleanup** — after all story sections and the consolidated run-level summary
     are written, delete each indexed story's recorded pipeline state and only
     that run's pointer index. Use validated indexed roots and the selected
     adapter's literal-path file operations; preserve legacy state, other runs
     and persistent runtime memory. Agents clean their own temporary bodies after use.
