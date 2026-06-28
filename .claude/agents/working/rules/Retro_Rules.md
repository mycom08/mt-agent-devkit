# Retro Rules

**Applies to:** All pipeline agents (Developer, Technical Lead, QA, Product Owner, Business Analyst)

---

## When to Write

At the end of your stage work, **before reporting back to the orchestrator**, write your retrospective section to the story retro file. The orchestrator creates this file at Stage 1 with `*(pending)*` placeholders — overwrite only your own section.

**File path:** `.claude/agents/working/retros/ST-XXXXXX_retro.md` (the story ID is passed in your spawn prompt)

**Your section heading** matches your role:
- Implementer → `## Implementer — <your role>`
- Reviewer → `## Reviewer — <your role>`
- QA validator → `## QA`
- Story closer → `## Product Owner`

---

## Three Fixed Questions

Answer these three questions in your section. Bullet points only. Be specific to this story.

### 1. Impediments & Unclear Points

Things that slowed you down or required an unguided judgement call: missing permissions, incorrect technical design, ambiguous AC, unclear workflow steps.

Prefix each bullet with its signal type:
- `[context]` — gap in priming docs, memory files, or project context
- `[instruction]` — gap or improvement needed in an agent instruction file
- `[workflow]` — gap or improvement needed in a workflow file
- `[failure]` — recurring failure pattern that needs a guardrail or rule

If nothing: write `- None.`

### 2. Process Suggestions

Concrete suggestions to improve the process, workflow files, or instruction files — based only on what you directly encountered this story. Use the same signal-type prefixes.

If nothing: write `- None.`

### 3. What Worked Well

Things that should be explicitly preserved: a rule that caught a real problem, a workflow step that ran smoothly, a pattern that produced good output.

No signal-type prefix needed.

If nothing: write `- None.`

---

## Scope Rule

Only report observations that arose **directly from your work on this story**. Do not carry over observations from other stories worked in the same session.

---

## Privacy Rule

Signal items (`[context]`, `[instruction]`, `[workflow]`, `[failure]`) must be written in **generic, project-neutral language**. Do not reference:

- Project names or repo names
- Domain-specific file paths (e.g., `src/billing/invoices/`, `apps/core/models/user.py`)
- Business logic terms specific to the current project (e.g., "invoice approval flow", "ABAC policy editor")
- Client names, user identifiers, or environment-specific identifiers

**Why:** Retrospective signals feed the devkit improvement process. Domain-specific references make signals non-transferable and may expose client or project details.

**Self-check — before writing a signal item, ask:** "Could this bullet appear unchanged in a retro for a completely different project?"

**Bad (project-specific):**
> `[workflow]` The `src/billing/invoices/` path was missing from the sprint summary — the privacy scan step skipped it

**Good (generic):**
> `[workflow]` A domain-specific subdirectory was absent from the sprint summary — the privacy scan step did not detect it; add an explicit path-enumeration step

---

## Format

Overwrite the `*(pending)*` placeholders in your section only. Do not touch other agents' sections.

Example of a completed section:

    ## Implementer — Developer
    ### Impediments & Unclear Points
    - `[context]` AC listed two alternate resolution paths — required a blocking TL question before starting
    - `[workflow]` Design-first gate too coarse for pure template restructuring

    ### Process Suggestions
    - `[context]` Story author should commit to a single authorised approach at creation time
    - `[workflow]` Clarify that pure rename/restructure does not require a design comment

    ### What Worked Well
    - Caller-trace rule worked as intended — all path references checked before touching any file
    - Pre-PR gate caught a shell syntax error before opening the PR
