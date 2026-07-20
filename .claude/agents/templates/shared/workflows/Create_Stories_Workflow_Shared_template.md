<!-- Included by: templates/github/workflows/Create_Stories_Workflow_template.md, templates/strict/workflows/Create_Stories_Workflow_template.md -->

<!-- SHARED-START -->
# Create Stories Workflow

Triggered by: `"create stories"` or `"/create-stories"` in CLAUDE.md

The orchestrator acts as PO — read `.claude/agents/product_owner_instructions.md` and `.claude/agents/rules/Story_Standard_PO.md` before proceeding. **Do not spawn a PO agent.**

---

## Step 1 — Collect Requirements

Ask the user to describe the work they need stories for. Collect until scope is clear:
- What problem or goal each story addresses
- Acceptance criteria for each story
- Which agent role implements it (`Developer`, `Technical Lead`, `QA`, `Business Analyst`, `UI/UX Designer`)
- Estimated story points (1–13)
- Target sprint (if known). If the user says "next sprint" without a number, resolve it:
  - **GitHub mode:** run `gh issue list --state closed --limit 5 --json labels,closedAt --jq 'sort_by(.closedAt) | reverse | [.[].labels[].name | select(startswith("sprint-"))] | sort_by(ltrimstr("sprint-") | tonumber) | last'` to find the highest sprint on recently closed issues, then add 1. **Do not use `gh label list` — it sorts alphabetically, making `sprint-3` appear higher than `sprint-13`.**
  - **Strict mode:** glob `.claude/agents/docs/stories/*.md`, collect all unique `**Sprint:**` field values, parse the trailing number from each (e.g. `sprint-3` → 3), take the highest, then add 1.

Ask open questions to resolve any ambiguities before drafting.

---

## Step 2 — Draft Stories

Present a draft story list (titles, user story statement, AC, assignee, points) to the user. Wait for confirmation or revisions before creating issues.

Before finalising each draft, apply these two checks:
- **API surface check:** For every endpoint referenced in the ACs, confirm it exists in the project's API spec (check `docs/api/` or equivalent) or is explicitly scheduled for delivery in the same sprint. If an endpoint does not exist yet, note this in the story and flag it to the user before creating the issue.
  - **Multi-repo only — contract-review completeness, not just existence:** if the endpoint lives in a sibling contract repo, path-existence in the spec file is not enough. Confirm a **closed, review-scoped** story in the owning repo actually covers that endpoint's schema against this story's needs — not just a same-named "API contract design" dependency. If no such story exists, or an existing one's AC scope doesn't cover the referenced endpoint, flag it to the user before creating the issue — either as a noted blocking dependency or by drafting the missing contract-review story in the owning repo first.
- **Unit-test AC check:** If the story introduces new service-layer methods or functions, include an explicit AC: `- [ ] Unit tests added for all new service methods (empty-input guard, error path, happy path)`.

---

## Step 3 — Feature Check

Ask the user: **"Do these stories belong to a feature? If yes, provide the feature name and phase number."**

- **No feature** → feature: `none`, phase: `none`
- **Feature** → record feature name and phase number for each story

Also ask: **"Which sprint should these stories be assigned to? (e.g., sprint-1, or leave blank if not yet scheduled)"**

> **Roadmap phase vs sprint label:** if the stories come from a roadmap doc, its `Phase:` numbers are a global, cross-repo thematic sequence — independent of this repo's `sprint-N` labels, which count this repo's own executed sprints starting at 1. When drafting from a roadmap, echo the source phase as a `**Roadmap Phase:** Phase N — <theme>` line in the story body; never copy the roadmap phase number into the sprint label.

---

## Step 4 — Create Stories

**If `Mode: github`:**

For each confirmed story, create a GitHub Issue following `Story_Standard_PO.md` §13:
- Labels: `status:backlog`, `feature:<name>` (if feature), `phase-N` (if feature), `sprint-N` (if sprint assigned)
- Use `--body-file` pattern (see §15)
- Report created issue URLs to the user

**If `Mode: strict`:**

For each confirmed story:
1. Read `.claude/agents/docs/story_counter.txt`, increment by 1, write back — derive the new `ST-XXXXXX` ID
2. Ask the user (once, not per story): **"Does your project use an external story ID system (e.g. Jira, Linear)? If yes, provide the external ID for each story now, or leave blank to skip."**
3. Write `.claude/agents/docs/stories/ST-XXXXXX.md` using the format from `Strict_Mode_Story_Guide.md` §Story MD Format:
   - `**Status:** backlog`
   - `**External ID:**` — set if provided, omit the line if blank
   - `**Sprint:**` — set if user provided a sprint, omit the line if blank
   - `**Feature:**` / `**Phase:**` — set from Step 3
4. Report created story file paths to the user (e.g., `.claude/agents/docs/stories/ST-000001.md`)
<!-- SHARED-END -->
