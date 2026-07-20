<!-- Included by: templates/github/workflows/Sprint_Workflow_template.md, templates/strict/workflows/Sprint_Workflow_template.md -->

<!-- SHARED-START -->
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
**Implementer:** <Developer | Technical Lead | QA | Business Analyst | UI/UX Designer>
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

**Write rules:** Create/overwrite at Stage 0 entry of each new story — carry forward any existing `Observations:` entries when overwriting. **After every stage transition, update both `Stage` and `Updated` — these are mandatory, not optional.** Update `Sessions` on every agent spawn — **write `impl_session: PENDING` (or the relevant session field) to the state file immediately before making the spawn call**; overwrite with the real agentId as soon as the spawn returns. Never leave a session ID empty after spawning. Update loop counts at each retry cycle start. Set `Type` at Stage 0 based on story classification (see Shared Pipeline Stages §Stage 0). Set `Sprint` at Stage 0 by reading the sprint value from the story (`sprint-N` label in GitHub mode; `**Sprint:**` field in strict mode). Set `Sprint Branch` and `Story Branch` at Stage 0 in strict mode (derived per `Strict_Mode_Story_Guide.md` §Branch Naming); write `n/a` in GitHub mode. Set `Docs SHA` at Stage 0 via `git rev-parse --short HEAD`. Append a one-line bullet to `Observations:` (prefixed with agent role if reported by an agent) whenever the orchestrator makes a judgment call not covered by this workflow or an agent reports friction. Delete after workflow review is complete.

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
- **Sprint end** — when no more `status:ready` stories remain:
  1. **Batch Retro Review** — process each story's retro file one by one in story order. For each:
     a. Read `.claude/agents/retros/ST-XXXXXX_retro.md`
     b. Collect all signal-tagged items (`[context]`, `[instruction]`, `[workflow]`, `[failure]`) from every section
     c. Present collected items to the user as proposed improvements; for each approved item, apply the change targeting the right artifact:
        - `[context]` → priming docs or agent memory files
        - `[instruction]` → agent instruction files (`.claude/agents/*_instructions.md`)
        - `[workflow]` → workflow files (`.claude/agents/workflows/`)
        - `[failure]` → rules or guardrail files (`.claude/agents/rules/`)

        **Routing check for `[context]` items:** before applying a `[context]` item as a priming/memory edit, ask explicitly — *does this note describe a missing capability or limitation in the codebase/test setup (not just process friction), with no existing backlog story that will ever close it?* If yes, route it to backlog creation (draft a new story) instead of, or in addition to, the priming/memory edit — a note filed only as context trivia can leave a real capability gap permanently unowned.
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
  3. **Release Decision** — fulfills the PO's Release Gate responsibility (`Product_Owner_Rules.md` §8–9) without requiring a fresh agent spawn, same orchestrator-direct pattern as the other Sprint end steps. Check whether `VERSION` exists at the repo root:
     - **Does not exist** (non-Java repo, or a repo predating this convention) → nothing to do, skip to step 4.
     - **Exists** → read `VERSION` and `CHANGELOG.md`. Find the section whose heading matches `VERSION` with its `-SNAPSHOT` suffix stripped (e.g. `VERSION` is `0.0.2-SNAPSHOT` → look for `## [0.0.2]`). If that section has **no** entries under `### Changes`/`### Bug Fixes`, there's nothing release-worthy yet — skip to step 4 without asking.
     - Otherwise, **ask the user** (never decide this automatically — releasing is not an automatic sprint-end action):
       > "Sprint complete. This repo is at `<the current VERSION value>`. The current CHANGELOG section has these entries: <list them>. Cut a release now? (yes/no)"

       If the roadmap defines Release Gate criteria, add a one-line note on whether Must-Have criteria currently look met (informational only — the user still decides).
     - **If no** → skip to step 4. Not shipping a release every sprint is a normal, expected outcome, not a failure state.
     - **If yes** — **GitHub mode only** (strict mode has no GitHub Actions to trigger `release.yml` against; tell the user releasing isn't available in strict mode and skip to step 4):
       1. Strip the `-SNAPSHOT` suffix from `VERSION` (e.g. `0.0.2-SNAPSHOT` → `0.0.2`), commit and push directly to `main` — a small mechanical change, no story/PR needed (same class of action as other plan-file commits already made directly, see `Product_Owner_Rules.md` §11).
       2. Trigger the release workflow: `gh workflow run release.yml --ref main`.
       3. Report the run back to the user (`gh run list --workflow=release.yml --limit 1`) and note that `release.yml` itself independently validates the tag/CHANGELOG and can still fail — this step only kicks it off, it doesn't guarantee success.
  4. **Devkit Contribution** — optional sharing of sprint retro signals with the devkit team. The sprint pipeline continues regardless of the user's answer.

     a. **Privacy scan** — read `.claude/agents/retros/sprint_N_summary.md` (resolve N from `Sprint` field in the state file). Extract all lines from every `### Findings` section across all story blocks. For each item, apply the Privacy Rule from `Retro_Rules.md`: remove or generalise any remaining project-specific references — no project names, repository names, domain-specific file paths, business logic terms, or client/user identifiers. Retain only the generalised text.

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
        ii. Write the export file to `.claude/agents/retros/devkit_contribution_sprint_N.md`.
        iii. Run `gh auth status` to check authentication:
             - **Authenticated:** run:
               ```bash
               gh issue create --repo mycom08/mt-agent-devkit \
                 --title "Community Retro Contribution — Sprint N (YYYY-MM-DD)" \
                 --label "retro:contribution" \
                 --body-file .claude/agents/retros/devkit_contribution_sprint_N.md
               ```
               Report the Issue URL to the user. Delete the local export file.
             - **Not authenticated or `gh` unavailable:** inform the user that the export file has been written to `.claude/agents/retros/devkit_contribution_sprint_N.md`. Instruct them to open an Issue labeled `retro:contribution` on `mycom08/mt-agent-devkit` with the export file contents, so the `apply retros` workflow can find it.

     d. **If no:** skip to step 5 (Cleanup).

  5. **Cleanup** — delete the state file, then delete any remaining files in `.claude/agents/tmp/` with `rm .claude/agents/tmp/*.md`. Agents must also delete any tmp files they created immediately after the file is no longer needed (e.g., after `gh` call using `--body-file`).
<!-- SHARED-END -->
