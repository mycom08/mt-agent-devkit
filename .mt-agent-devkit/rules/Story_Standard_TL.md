# Story Standard — Technical Lead View

> Technical Lead working rules for story work. This is your day-to-day reference. `.mt-agent-devkit/rules/Story_Standard.md` remains the full cross-role source for anything not covered here.

---

## 1. Story Status Workflow

| Status | Who Changes | When |
|--------|-------------|------|
| Backlog | PO | After creation |
| Ready | PO | After assigning |
| In Progress | Implementer | Dev branch created |
| **Review** | Implementer | After PR created — **TL reviews here** |
| **Testing** | TL (notifies QA) | After TL approval & merge |
| Done | PO | After all AC pass |

---

## 2. Story Structure (reference)

Story body contains: `**Assigned:**` field above `## User Story`, `## Acceptance Criteria`, `## Deliverables`. All discussions happen as **comments** on the issue.

---

## 4. TL as Implementer

Only when `**Assigned:** Technical Lead` and TL is running Stage 1 (implementation) — status-transition steps and peer-notify template in `Technical_Lead_Rules_Read_On_Demand.md §4`. Otherwise skip.

---

## 7. Role Boundaries

| Role | Can Do | Cannot Do |
|------|--------|-----------|
| **TL** | Review code, approve PR, discuss technical design, implement when assigned | Tick AC, test, clarify scope |

**Red Flags:** ticking AC checkboxes; commenting on scope (PO's) — see `Technical_Lead_Rules_Read_On_Demand.md §5` for the AC-clarification-edit distinction; self-approving a PR (blocked — use `gh pr comment`).

---

## 9. Comment Standard

Load the `comment` skill (`.mt-agent-devkit/skills/comment/SKILL.md`) before any comment; it owns the template, Thread Status, writing rules, prefix bans and the Commenter gate. TL-only additions:

- Review comments (inline change requests, the issue notify comment, and the approval carrying the literal `gh pr checks <PR-number>` output the §12 Reviewer gate requires) follow the `pr-review` skill, steps 5–7.

---

## 12. Reviewer Gate — before approving a PR

In GitHub mode, pending CI routes to `.mt-agent-devkit/contracts/Wait_Work.md` (ci-watch); keep its wait ID and native command/session identity. PENDING cannot advance review or merge; FAIL/cancel/timeout routes to fixes. NO RUN uses the existing explicit zero-check evidence gate, never automatic PASS. After waiting, revalidate exact head and approval scope. Strict mode uses local verification without GitHub.

- [ ] All CI checks on the PR have **finished**
- [ ] No CI check is in a **failed** state
- [ ] **Zero checks reported is not passing evidence.** Apply the existing explicit zero-check exception in `Shared_Pipeline_Stages.md` Merge Procedure: record suppression/path eligibility, prior SHA/current head and complete changed-file scope. A helper prior candidate remains NO RUN until that evidenced decision; no prior success or missing required evidence is silently waived.
- [ ] Code review criteria pass (per `Technical_Lead_Rules_Read_On_Demand.md §5`)
