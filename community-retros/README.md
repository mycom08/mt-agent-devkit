# Community Retrospectives

This folder is the landing area for retro export files contributed by teams using mt-agent-devkit in their target projects. Maintainers read these files, identify recurring patterns, and apply improvements back to the devkit templates and workflow files.

---

## Purpose

When a sprint closes in a target project, the QA agent runs a privacy-filtered export of the sprint retrospective signals and deposits a structured Markdown file here (via a pull request or direct push). Over time these files accumulate signals from many different projects and teams — giving maintainers a broad, anonymised view of where the devkit's rules, instructions, and workflows need improvement.

No individual project's context should ever appear in these files. They are a distillation of process observations, not a record of what any team built.

---

## Export File Format

Each export file is a structured Markdown document. The filename must follow this pattern:

```
sprint-<N>_<YYYY-MM-DD>.md
```

Example: `sprint-3_2026-06-28.md`

### Required Sections

```markdown
# Retro Export

**Sprint:** <sprint number>
**Date:** <YYYY-MM-DD>

## Signal Items

### [context]
<!-- Gaps in priming docs, memory files, or project context -->
- <signal item>

### [instruction]
<!-- Gaps or improvements needed in an agent instruction file -->
- <signal item>

### [workflow]
<!-- Gaps or improvements needed in a workflow file -->
- <signal item>

### [failure]
<!-- Recurring failure patterns that need a guardrail or rule -->
- <signal item>

## What Worked Well
- <observation>
```

Sections with no items should be left in place with a single `- None.` entry so the structure stays consistent and machine-readable.

### Complete Filled-in Example

```markdown
# Retro Export

**Sprint:** 4
**Date:** 2026-07-14

## Signal Items

### [context]
- The project priming doc did not specify which model to use for the QA role during regression runs — agents defaulted to sonnet but a lightweight model (haiku) would have been sufficient.

### [instruction]
- The Developer instruction file does not mention what to do when a pre-PR syntax check exits non-zero on Windows vs Unix — the discrepancy caused a delay.
- TL instruction file does not state the maximum number of inline PR comments before switching to a summary comment.

### [workflow]
- The stage-transition commit step in `Agent_Common.md` does not specify whether empty memory files should be committed — agents skipped the commit and the gate blocked unnecessarily.
- Sprint Consolidated Summary workflow step does not state the output file path explicitly; agents wrote to different paths across roles.

### [failure]
- Two consecutive sprints: the privacy scan was run against the wrong input file; the workflow step did not name the exact file to scan.

## What Worked Well
- The mid-implementation consultation procedure worked as intended — blocking questions were posted and answered without stalling the pipeline.
- The pre-PR gate for shell scripts caught a syntax error before the PR was opened.
- Signal-type prefixes (`[context]`, `[instruction]`, `[workflow]`, `[failure]`) made triage fast — each signal routed to the right file without ambiguity.
```

---

## Privacy Requirements

**Export files must contain no project-specific information.**

Before submitting an export file, every signal item must pass this self-check: "Could this bullet appear unchanged in a retro for a completely different project?"

The following must never appear in an export file:

- Project names or repository names
- Domain-specific file paths (e.g., `src/billing/invoices/`, `apps/core/models/user.py`)
- Business logic terms specific to the project (e.g., "invoice approval flow", "ABAC policy editor")
- Client names, user identifiers, or environment-specific identifiers

**Bad (project-specific):**
> `[workflow]` The `src/billing/invoices/` path was missing from the sprint summary — the privacy scan step skipped it

**Good (generic):**
> `[workflow]` A domain-specific subdirectory was absent from the sprint summary — the privacy scan step did not detect it; add an explicit path-enumeration step

Files that contain project-specific information will be rejected at review. If the contributing team is unsure whether an item is generic enough, they should rephrase it until the project context is removed, or omit it.

This requirement mirrors the Privacy Rule in `Retro_Rules.md` that applies to all agents writing retro sections inside a target project.

---

## Maintainer Review Process

### Step 1 — Read and triage incoming files

Open each new export file. Skim the **Signal Items** sections first. For each signal item:

1. Check it passes the privacy rule (no project-specific references).
2. Assign it to a source file: which devkit file would need to change to address this signal?
   - `[context]` signals → usually `Project_Priming.md` or a memory file
   - `[instruction]` signals → usually an agent instruction file (e.g., `developer_instructions.md`)
   - `[workflow]` signals → usually a workflow file (e.g., `Sprint_Workflow.md`) or `Agent_Common.md`
   - `[failure]` signals → usually a rules file (e.g., `Developer_Rules.md`) or an instruction file
3. Note which signals appear in **multiple export files** — recurring signals are higher priority than one-off observations.

### Step 2 — Evaluate signal strength

Not every signal warrants a template change. Apply this threshold:

| Signal frequency | Action |
|---|---|
| Appears in 3 or more export files | Strong signal — draft a template fix |
| Appears in 2 export files | Moderate signal — add to backlog for next sprint |
| Appears once | Weak signal — note for context; no immediate action |

For `[failure]` signals, apply a lower threshold: a single clear failure pattern that describes a missing guardrail is worth acting on immediately.

### Step 3 — Apply improvements

For each approved template change:

1. Edit the relevant file under `.claude/agents/templates/` (or the devkit workflow file if it is a workflow signal).
2. Bump `version.txt` (patch version).
3. Add a `changes.json` entry for any template file changed (devkit-internal workflow files do not go in `changes.json`).
4. Update `CHANGELOG.md` under `[Unreleased]`.
5. Open a PR and tag a second maintainer for review.

### Step 4 — Archive the export file

After processing, move the export file to `community-retros/archive/` so it does not appear in future triage passes. Do not delete it — archived files are the audit trail.

---

## Contributing an Export File

Target project users who want to contribute:

1. Ensure the QA agent has run the sprint privacy scan and produced a filtered export file.
2. Verify the file passes the privacy requirements above.
3. Open a pull request targeting the `main` branch of `mycom08/mt-agent-devkit`, adding the export file under `community-retros/`.
4. The PR description should state the sprint number and date — nothing else about the project.

Maintainers will review and merge the PR within the next triage cycle.
