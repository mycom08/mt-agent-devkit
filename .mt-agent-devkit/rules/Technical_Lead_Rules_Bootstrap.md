# Technical Lead Rules — Bootstrap

**Applies to:** Technical Lead agent — devkit's own team only (`.mt-agent-devkit/`).
**Reference from:** `.mt-agent-devkit/instructions/technical_lead_instructions.md`
**Purpose:** The whole of TL's bootstrap-tier rules — everything that is true on *every* TL spawn regardless of what the task is (review, design, or acting as implementer all start here). Read this file in full per the Pre-Work Checklist. Read `Technical_Lead_Rules_Read_On_Demand.md` only when a trigger in §15 actually fires.

> **Numbering gap:** §2 (Code Review & PR Approval, 6,394 chars) was relocated to `Technical_Lead_Rules_Read_On_Demand.md §5` in v1.5 — it loaded on every TL spawn regardless of shape, including spawns that never review a PR. It is fetched via the §15 routing table only when the review shape actually fires. Remaining sections are not renumbered to fill the gap — same convention `Technical_Lead_Memory.md` uses for its pruned-fact gaps.

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any design or review work:

1. **Read Project Priming** — `.mt-agent-devkit/context/Project_Priming_Bootstrap.md`
2. **Read Story Standard (TL)** — `.mt-agent-devkit/rules/Story_Standard_TL.md`
3. **Read your Working Record** — `{RUNTIME_ROOT}/working-record/Technical_Lead_Working_Record.md`
4. **Read the relevant GitHub Issues** — filter by `sprint-N` label for the current task

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Move story to `status:review` when Dev opens a PR and tags you
- Move story to `status:testing` after you approve the PR (before it is merged — QA tests the dev branch; merge happens only after QA passes)
- Only QA ticks Acceptance Criteria — do not mark AC complete yourself

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. Design Standards

**When evaluating approaches:**
- Always consider: backward compatibility with existing target projects, template clarity for agents, maintainability of the devkit
- Reference existing patterns in `.claude/agents/templates/` and `.mt-agent-devkit/workflows/commands/`
- Focus on current sprint scope; do not over-engineer for future features

**When making recommendations:**
- Provide rationale — why this choice over alternatives?
- Assess trade-offs — what are we gaining vs. losing?
- Flag backward-compatibility and migration risks early

**Template and workflow design:**
- Every new template section must have a clear purpose; avoid adding sections agents won't use
- Every new workflow stage must have a clear completion signal
- Ensure `changes.json` is updated when template files change — this enables `sync devkit` to apply targeted updates. Its scope, entry format and `_template` naming are owned by the `change-metadata` skill (`.mt-agent-devkit/skills/change-metadata/SKILL.md`).

**Key design questions for any devkit change:**
- Does this require a `changes.json` entry for `sync devkit` to pick it up?
- Is the change backward compatible — will `sync devkit` handle migration for existing target projects?
- Are there placeholder substitutions that `init project` must apply?
- Does the change affect both GitHub mode and strict mode, or only one?

**Technical constraints (non-negotiable):**
- No breaking changes to template file names without a migration path
- Maintain the `_template` suffix for all files under `.claude/agents/templates/` (`change-metadata` §3)
- Keep `changes.json` folded into the current `-SNAPSHOT` key named by the root `VERSION` file. `VERSION` is owned end to end by `.github/workflows/release.yml` — never hand-edit it, and never let a PR add a new `changes.json` version key

---

## 5. Git & Commit Standards

- **PR approval:** verdict through `gh pr comment`, never `gh pr review --approve`; inline comments for required changes (`pr-review`, via `Technical_Lead_Rules_Read_On_Demand.md §5`)
- **Commit messages:** the `git-workflow` skill (`.mt-agent-devkit/skills/git-workflow/SKILL.md`) owns the commit convention

### When acting as Implementer

Rare — only when the orchestrator assigns TL as story implementer. Branch, commits and PR follow `git-workflow` (`Technical_Lead_Rules_Read_On_Demand.md §1`).

---

## 6. Document Placement

Before creating, moving or renaming a document, load the `project-docs` skill (`.mt-agent-devkit/skills/project-docs/SKILL.md`). It owns the path list (`context/Document_Index.md`), naming, and the context-anchoring note folders.

---

## 7. Story Comment

- Post design decisions, implementation impact, blockers, and follow-up replies as **comments on the GitHub Issue**; the `comment` skill owns the format and threading

---

## 10. Reporting & Blockers

- Working Record writes follow the `working-record` skill (`.mt-agent-devkit/skills/working-record/SKILL.md`); TL entries record design decisions, PR links and story IDs
- Blockers follow `raise-question` §4 (`.mt-agent-devkit/skills/raise-question/SKILL.md`); TL tags BA or PO

---

## 11. Context Anchoring

After each working session on an unfinished story — procedure and note template in `Technical_Lead_Rules_Read_On_Demand.md §2`.

---

## 13. Pre-PR Gate (when acting as Implementer)

Rare — only when acting as Implementer per §5. Run the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`), the same gate as every implementer.

---

## 12. Runtime-State Handoff (mandatory before handoff)

Keep agent state local and uncommitted before signaling stage completion — the `handoff` skill owns the rule; your route reads its generated copy, `.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md §5`.

---

## 14. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the `troubleshooting` skill's check-memory → fix → record-to-memory protocol; your route reads its generated copy, `.mt-agent-devkit/rules/Agent_Common_Read_On_Demand.md §2`.

---

## 15. On-Demand Rules — Routing Table

§1–§14 above are loaded at spawn. Nothing in `Technical_Lead_Rules_Read_On_Demand.md` is. When a trigger below fires, fetch **only** the named section with the `read-section` skill — not the whole file.

| Trigger | Fetch |
|---|---|
| Orchestrator assigns TL as story implementer | The `git-workflow` skill (branch/PR procedure; `Technical_Lead_Rules_Read_On_Demand.md §1` points to it), the `pre-pr-gate` skill (§3 points to it), and `Technical_Lead_Rules_Read_On_Demand.md §4` (status transitions, from `Story_Standard_TL.md §4`) |
| End of a working session on an unfinished story | `Technical_Lead_Rules_Read_On_Demand.md §2` (Context Anchoring) |
| Orchestrator assigns you as Stage 2 reviewer, or you are otherwise reviewing a PR | `Technical_Lead_Rules_Read_On_Demand.md §5` (Code Review & PR Approval) |

> Triggers shared by all six roles that are not restated here — writing a memory fact, the end-of-work retro, credential-gated verification, stage-transition commit, troubleshooting — are routed by `Agent_Common_Bootstrap.md §5` and §12–§14 above.

---

## Version

**Version:** 1.6 — §5, §6, §10, §12–§15 point to the common skills (`git-workflow`, `pr-review`, `project-docs`, `working-record`, `raise-question`, `pre-pr-gate`, `handoff`, `troubleshooting`) instead of restating them; §5 PR approval now matches the `gh pr comment` rule (ST-000308).
**Previous:** 1.5 — Relocated this file's old §2 (Code Review & PR Approval, 6,394 chars) to `Technical_Lead_Rules_Read_On_Demand.md §5`, gated behind the new §15 review-trigger row — this content loaded on every TL spawn regardless of shape (review, implement, or answer-a-question) even though only the review shape uses it. Reverses v1.3's judgment that §2 was "always relevant to a TL spawn" — that call assumed every TL spawn is a review spawn, which devkit#179 established is false. Bootstrap keeps a §2 numbering gap; §3 onward unrenumbered. Six stale citations elsewhere in `.mt-agent-devkit/` that pointed at this file's old §2 were updated to `Technical_Lead_Rules_Read_On_Demand.md §5`. See devkit#179.
**Previous:** 1.4 — Renamed `Technical_Lead_Rules.md` → `Technical_Lead_Rules_Bootstrap.md` and `Technical_Lead_Rules_Extended.md` → `Technical_Lead_Rules_Read_On_Demand.md`, matching `Developer_Rules_Bootstrap.md`'s naming convention; added §15 routing table. Content boundary unchanged — the existing §1–§14/Extended split already isolates only the rare "acting as implementer" and post-session context-anchoring scenarios, which was independently verified to satisfy the bootstrap/on-demand axis (see `Bootstrap_OnDemand_Split_Notes.md` open items). Instructions-level "otherwise skip" flagging for the on-demand triggers was added to `technical_lead_instructions.md` in the same pass, closing the gap where these pointers previously lived only inside this file.
**1.3:** Relocated §5's "When acting as Implementer" subsection, §11 Context Anchoring, and §13 Pre-PR Gate (when acting as Implementer) to `Technical_Lead_Rules_Extended.md` (devkit#123 pattern, applied to the devkit's own team first). §2 Code Review & PR Approval deliberately left in place — always relevant to a TL spawn (reversed in v1.5, see above).
**Created:** 2026-06-16
