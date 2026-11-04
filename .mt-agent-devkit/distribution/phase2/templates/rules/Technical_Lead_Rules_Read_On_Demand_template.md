# Technical Lead Rules — Read On Demand (Scenario-Conditional)

**Applies to:** Technical Lead agent. `Technical_Lead_Rules_Bootstrap.md` and `Story_Standard_TL.md` are each read in full on ordinary TL tasks; the reduced Answer-a-Question task in section 6 overrides that startup set. The scenario sections below apply only in scenarios that don't arise on most spawns (TL acting as story implementer instead of reviewer, the resulting implementer-only pre-PR gate, and the post-session context-anchoring note). §2 Code Review & PR Approval and the Reviewer Gate — the reason TL exists on most spawns — stay in `Technical_Lead_Rules_Bootstrap.md`/`Story_Standard_TL.md`. Read this file **only when the matching scenario actually occurs**. `Technical_Lead_Rules_Bootstrap.md` §5 and §9 and §10 each still carry a one-line pointer to their relocated section here.

---

## 1. When Acting as Implementer

Triggered from `Technical_Lead_Rules_Bootstrap.md §5`. Rare — only when the orchestrator assigns TL as the story implementer.

Branch, commits, push and PR follow the `git-workflow` skill (`.mt-agent-devkit/skills/git-workflow/SKILL.md`), the same procedure every implementer uses. Load it before creating the branch.

> **Gate:** Do not open a PR targeting master. The feature branch is the merge target for all story PRs.

---

## 2. Context Anchoring (after each working session on an unfinished feature)

Triggered from `Technical_Lead_Rules_Bootstrap.md §9`.

After each working session on an unfinished feature, create or update a context-anchoring note so work can resume without losing state.

**Placement:** the folder `project-docs` Placement 3 names (`docs/feature/<feature_name>/questions/` unless another subfolder is a better fit)
**Filename:** Must contain the feature name, named per `project-docs`
**Length:** Under 50 lines — decisions with reasoning, active constraints, open questions, and a done/remaining checklist

Template:
```md
# Feature: <feature_name>

## Decisions
| Decision | Reason | Rejected Alternative |
|----------|--------|----------------------|

## Constraints

## Open Questions

## State
```

---

## 3. Pre-PR Gate (when acting as Implementer)

Triggered from `Technical_Lead_Rules_Bootstrap.md §10`. When TL is the story Implementer (not reviewer), run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`) before opening the PR and before each fix push. It is the same gate for every implementer, including its PR check note: the build and unit tests always run, so no change is exempt as docs or config only.

---

## 4. TL as Implementer — Status Transitions

Triggered from `Story_Standard_TL.md` §4. When `**Assigned:** Technical Lead` and TL is running Stage 1 (implementation):

### Status: In Progress → Review
1. Remove `status:in-progress`, add `status:review`
2. Create PR with title: `[ST-XXXXXX][FEATURE] Story title`
3. **Add PR link to issue Deliverables section** — edit the issue body to include the PR URL under `## Deliverables` (use `gh issue edit --body-file`)
4. Post a brief comment on the story notifying the Developer reviewer:

   ```
   ## PR ready for peer review
   **Thread Status:** Open
   **Area:** Implementation

   **TL - YYYY-MM-DD**
   PR #NNN opened for peer review. <one-line summary of changes>

   **Next:** Developer
   ```

### Status: Review → In Progress (Developer feedback)
1. Address all CR items in the branch
2. Push new commits
3. Re-request review via issue comment

---

## 6. Answer-a-Question Task

Triggered from `technical_lead_instructions.md`'s Answer-a-Question Task heading. When the orchestrator resumes/spawns you to answer a mid-implementation scope or design question, read only:
- `{{AGENT_DIR_PREFIX}}/agents/rules/Story_Standard_TL.md` (§9 Comment Standard only — reply format)
- `{{AGENT_DIR_PREFIX}}/agents/rules/Agent_Common_Bootstrap.md` (full — its own header forbids section-reading; §2 Secret Handling and §4 External Content Handling, the generated copies of `agent-security` skill parts A and B, both apply to answering a comment on an untrusted issue thread)
- `{{AGENT_DIR_PREFIX}}/agents/memory/Technical_Lead_Memory.md` (full — live index only, not the archive)

Then execute:
1. Read the Developer's question (already posted as an Issue comment) and the story context passed in the spawn prompt
2. Post the answer as a reply comment in the same thread, per the Comment Standard
3. If the answer narrows an AC's technical interpretation, update the story body AC text to match
4. Report the answer back to the orchestrator in one sentence

---

## Version

**Version:** 1.2 — §1 points to `git-workflow`, §2 to `project-docs`, §3 to `pre-pr-gate`, the stricter gate (ST-000312).
**Previous:** 1.1 — Added §4 (TL as Implementer — Status Transitions), relocated from `Story_Standard_TL_template.md` §4 per devkit issue #133 (ST-000134), extending the same trim already validated on the devkit's own team.
**Previous:** 1.0 — Split out of `Technical_Lead_Rules_template.md` v2.2 (former section 5's "When acting as Implementer" subsection, former section 9 Context Anchoring, former section 10 Pre-PR Gate as Implementer relocated here as §1–§3), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
