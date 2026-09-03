# Technical Lead Rules — Bootstrap

**Applies to:** Technical Lead agent — devkit's own team only (`.claude/agents/working/`).
**Reference from:** `.claude/agents/working/instructions/technical_lead_instructions.md`
**Purpose:** The whole of TL's bootstrap-tier rules — everything that is true on *every* TL spawn regardless of what the task is (review, design, or acting as implementer all start here). Read this file in full per the Pre-Work Checklist. Read `Technical_Lead_Rules_Read_On_Demand.md` only when a trigger in §15 actually fires.

> **Numbering gap:** §2 (Code Review & PR Approval, 6,394 chars) was relocated to `Technical_Lead_Rules_Read_On_Demand.md §5` in v1.5 — it loaded on every TL spawn regardless of shape, including spawns that never review a PR. It is fetched via the §15 routing table only when the review shape actually fires. Remaining sections are not renumbered to fill the gap — same convention `Technical_Lead_Memory.md` uses for its pruned-fact gaps.

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any design or review work:

1. **Read Project Priming** — `.claude/agents/working/context/Project_Priming_Bootstrap.md`
2. **Read Story Standard (TL)** — `.claude/agents/working/rules/Story_Standard_TL.md`
3. **Read your Working Record** — `.claude/agents/working/working-record/Technical_Lead_Working_Record.md`
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
- Reference existing patterns in `.claude/agents/templates/` and `.claude/agents/workflows/`
- Focus on current sprint scope; do not over-engineer for future features

**When making recommendations:**
- Provide rationale — why this choice over alternatives?
- Assess trade-offs — what are we gaining vs. losing?
- Flag backward-compatibility and migration risks early

**Template and workflow design:**
- Every new template section must have a clear purpose; avoid adding sections agents won't use
- Every new workflow stage must have a clear completion signal
- Ensure `changes.json` is updated when template files change — this enables `sync devkit` to apply targeted updates
- `changes.json` tracks **template files deployed to target projects only** (under `.claude/agents/templates/`). Devkit-internal workflow files (`.claude/agents/workflows/`) are **not tracked** — edit them in-place with no `changes.json` entry.

**Key design questions for any devkit change:**
- Does this require a `changes.json` entry for `sync devkit` to pick it up?
- Is the change backward compatible — will `sync devkit` handle migration for existing target projects?
- Are there placeholder substitutions that `init project` must apply?
- Does the change affect both GitHub mode and strict mode, or only one?

**Technical constraints (non-negotiable):**
- No breaking changes to template file names without a migration path
- Maintain `_template` suffix for all files under `.claude/agents/templates/`
- Keep `version.txt` and `changes.json` in sync

---

## 5. Git & Commit Standards

- **PR approval:** Approve via GitHub PR review; leave inline comments for required changes
- **Commit messages:** Conventional Commits format
  - Format: `<type>(<scope>): <subject>`
  - Subject: imperative mood, ≤ 50 characters
  - Footer: `Story: ST-XXXXXX`

### When acting as Implementer

Rare — only when the orchestrator assigns TL as story implementer. Procedure in `Technical_Lead_Rules_Read_On_Demand.md §1`.

---

## 6. Document Placement

- Place all new documents in the correct subfolder — see `Project_Priming_Read_On_Demand.md §6`
- Use `Title_Case_With_Underscores` for all document file names
- Context-anchoring notes go under `docs/technical/` or `docs/feature/<feature_name>/questions/`

---

## 7. Story Comment

- Post design decisions, implementation impact, blockers, and follow-up replies as **comments on the GitHub Issue**
- Keep replies in the same thread when responding to an existing Dev, PO, BA, or QA comment

---

## 10. Reporting & Blockers

- Keep working record updates short and fact-based (design decisions, PR links, story IDs)
- Post blockers immediately as a Comment on the GitHub Issue; tag BA or PO as appropriate
- **Working record retention:** Delete entries older than the 3 most recent story entries before writing a new one (see `Agent_Common_Bootstrap.md §1` for the char cap and snapshot format)

---

## 11. Context Anchoring

After each working session on an unfinished story — procedure and note template in `Technical_Lead_Rules_Read_On_Demand.md §2`.

---

## 13. Pre-PR Gate (when acting as Implementer)

Rare — only when acting as Implementer per §5. Checklist in `Technical_Lead_Rules_Read_On_Demand.md §3`.

---

## 12. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/working/rules/Agent_Common_Read_On_Demand.md §5`.

---

## 14. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the check-memory → fix → record-to-memory protocol in `.claude/agents/working/rules/Agent_Common_Read_On_Demand.md §2`.

---

## 15. On-Demand Rules — Routing Table

§1–§14 above are loaded at spawn. Nothing in `Technical_Lead_Rules_Read_On_Demand.md` is. When a trigger below fires, fetch **only** the named section with the `read-section` skill — not the whole file.

| Trigger | Fetch |
|---|---|
| Orchestrator assigns TL as story implementer | `Technical_Lead_Rules_Read_On_Demand.md §1` (branch/PR procedure), `§3` (pre-PR gate), `§4` (status transitions, from `Story_Standard_TL.md §4`) |
| End of a working session on an unfinished story | `Technical_Lead_Rules_Read_On_Demand.md §2` (Context Anchoring) |
| Orchestrator assigns you as Stage 2 reviewer, or you are otherwise reviewing a PR | `Technical_Lead_Rules_Read_On_Demand.md §5` (Code Review & PR Approval) |

> Triggers shared by all six roles that are not restated here — writing a memory fact, the end-of-work retro, credential-gated verification, stage-transition commit, troubleshooting — are routed by `Agent_Common_Bootstrap.md §5` and §12–§14 above.

---

## Version

**Version:** 1.5 — Relocated this file's old §2 (Code Review & PR Approval, 6,394 chars) to `Technical_Lead_Rules_Read_On_Demand.md §5`, gated behind the new §15 review-trigger row — this content loaded on every TL spawn regardless of shape (review, implement, or answer-a-question) even though only the review shape uses it. Reverses v1.3's judgment that §2 was "always relevant to a TL spawn" — that call assumed every TL spawn is a review spawn, which devkit#179 established is false. Bootstrap keeps a §2 numbering gap; §3 onward unrenumbered. Six stale citations elsewhere in `.claude/agents/working/` that pointed at this file's old §2 were updated to `Technical_Lead_Rules_Read_On_Demand.md §5`. See devkit#179.
**Previous:** 1.4 — Renamed `Technical_Lead_Rules.md` → `Technical_Lead_Rules_Bootstrap.md` and `Technical_Lead_Rules_Extended.md` → `Technical_Lead_Rules_Read_On_Demand.md`, matching `Developer_Rules_Bootstrap.md`'s naming convention; added §15 routing table. Content boundary unchanged — the existing §1–§14/Extended split already isolates only the rare "acting as implementer" and post-session context-anchoring scenarios, which was independently verified to satisfy the bootstrap/on-demand axis (see `Bootstrap_OnDemand_Split_Notes.md` open items). Instructions-level "otherwise skip" flagging for the on-demand triggers was added to `technical_lead_instructions.md` in the same pass, closing the gap where these pointers previously lived only inside this file.
**1.3:** Relocated §5's "When acting as Implementer" subsection, §11 Context Anchoring, and §13 Pre-PR Gate (when acting as Implementer) to `Technical_Lead_Rules_Extended.md` (devkit#123 pattern, applied to the devkit's own team first). §2 Code Review & PR Approval deliberately left in place — always relevant to a TL spawn (reversed in v1.5, see above).
**Created:** 2026-06-16
