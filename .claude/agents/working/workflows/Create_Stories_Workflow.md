# Create Stories Workflow

Triggered by: `"create stories"` or `"/create-stories"` in CLAUDE.md

The orchestrator acts as PO — read `.claude/agents/working/instructions/product_owner_instructions.md` and `.claude/agents/working/rules/Story_Standard_PO.md` before proceeding. **Do not spawn a PO agent.**

---

## Step 1 — Collect Requirements

Ask the user to describe the work they need stories for. Collect until scope is clear:
- What problem or goal each story addresses
- Acceptance criteria for each story
- Which agent role implements it (`Developer`, `Technical Lead`, `QA`, `Business Analyst`)
- Estimated story points (1–13)
- Target sprint (if known)

Ask open questions to resolve any ambiguities before drafting.

---

## Step 2 — Draft Stories

Present a draft story list (titles, user story statement, AC, assignee, points) to the user. Wait for confirmation or revisions before creating issues.

Before finalising each draft, apply these two checks:
- **API surface check:** For every endpoint referenced in the ACs, confirm it exists in the project's API spec (check `docs/api/` or equivalent) or is explicitly scheduled for delivery in the same sprint. If an endpoint does not exist yet, note this in the story and flag it to the user before creating the issue.
- **Unit-test AC check:** If the story introduces new service-layer methods or functions, include an explicit AC: `- [ ] Unit tests added for all new service methods (empty-input guard, error path, happy path)`.

---

## Step 3 — Feature Check

Ask the user: **"Do these stories belong to a feature? If yes, provide the feature name and phase number."**

- **No feature** → feature: `none`, phase: `none`
- **Feature** → record feature name and phase number for each story

Also ask: **"Which sprint should these stories be assigned to? (e.g., sprint-1, or leave blank if not yet scheduled)"**

---

## Step 4 — Create Stories

For each confirmed story, create a GitHub Issue following `Story_Standard_PO.md` §13:
- Labels: `status:backlog`, `feature:<name>` (if feature), `phase-N` (if feature), `sprint-N` (if sprint assigned)
- Use `--body-file` pattern (see §15)
- Report created issue URLs to the user
