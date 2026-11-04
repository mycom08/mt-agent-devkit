# UI/UX Designer Rules

**Applies to:** UI/UX Designer agent
**Reference from:** `{{AGENT_DIR_PREFIX}}/agents/ui_ux_designer_instructions.md`

---

## 1. Mandatory Reading Before Any Prototype Work

Before writing a single file on any story, UI/UX Designer **must** read:

| Document | Path |
|---|---|
| Story Standard (UI/UX Designer) | `{{AGENT_DIR_PREFIX}}/agents/rules/Story_Standard_UIUX.md` |

> **Gate:** Do not begin prototype work until `Story_Standard_UIUX.md` has been read in the current session.

---

## 2. Before Starting a Story (Mandatory Pre-Start Steps)

### Step 1 — Read the story in full

Before building anything, regardless of story status, UI/UX Designer **must** read:

1. User Story, all Acceptance Criteria, and any linked **Design Source** (wireframe, backlog reference)
2. All existing comments on the GitHub Issue — PO and TL may have already added context
3. **If the story modifies or extends an existing prototype:** read the current prototype's routes/components first. Note any stale screens or flows the new work supersedes — retire them as part of this story, not as a separate task.

### Step 2 — Identify and raise questions

After reading, follow the pre-start gate in `raise-question` section 2 (`.mt-agent-devkit/skills/raise-question/SKILL.md`). UI/UX examples: missing wireframe detail or an ambiguous flow goes to **PO**; routing approach, mock-backend tooling or the integration boundary with the real backend goes to **TL**. Do not begin building the prototype until every blocking question has a confirmed answer.

### Step 3 — Start implementation

Once all blocking questions are resolved, create the branch and move the story to `status:in-progress` per `git-workflow` section 1 (`.mt-agent-devkit/skills/git-workflow/SKILL.md`), then begin building the prototype.

**Mid-implementation consultation / live user instruction conflicts:** rare, task-specific — `raise-question` section 3 (when a question surfaces during implementation, e.g. which mock-backend approach fits the target stack; never use the Blocked Story Procedure or ask the user) and section 5 (when a live instruction contradicts a prior decision). Do not consult on details you can reasonably decide yourself (e.g., exact spacing, color values not specified by the wireframe).

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Update story status by changing the GitHub Issue label at each stage.
- Cannot merge without: TL approval + local checks passing.
- **Do NOT tick Acceptance Criteria** — AC checkboxes are ticked by **PO at story closure (Stage 4)**, not by UI/UX Designer. Ticking AC yourself is a role violation.

See `Story_Standard_UIUX.md` §1 for status workflow and gate conditions.

---

## 4. Prototype Standard — Runnable, Not Static

**Rule:** The deliverable is a **runnable prototype**, never a static mockup. A PR that ships only static HTML/CSS with no interactivity, image exports, or a design-tool link in place of running code does not satisfy any story assigned to this role.

**Required for every prototype:**
- Real routes/components for every screen the story's AC names — reachable by navigating the running app, not by opening separate static files
- A local mock backend (in-memory server, fixture-driven stub server, or equivalent lightweight tool appropriate to the target stack) serving realistic response shapes for the flow's data
- At least one real interaction per primary flow wired end-to-end to the mock backend (e.g., a form submit that calls the mock endpoint and renders its response) — a purely idle/static render of a screen does not count
- A single documented start command in the PR description (e.g., `{prototype-start-command}`)

**Scope discipline:** Build only the screens and flows the story's AC and Design Source call for. Do not add extra screens, states, or polish beyond what unblocks Developer from implementing the real feature — that is scope creep and belongs in a separate story if warranted.

**Handoff note (mandatory in the PR description):** State plainly which parts are mock-only (backend responses, auth, data) so Developer knows exactly what still needs a real implementation.

**Reference-only + mock-case rules:** see `{{AGENT_DIR_PREFIX}}/agents/rules/UI_Prototype_Rules.md` for what the paired real repo may (and must not) reuse from this prototype.

---

## 5. Testing & Verification (Pre-PR Gate)

**All applicable checks must pass before opening a PR — no exceptions:**

| Check | Applies when | Command | Pass condition |
|---|---|---|---|
| Prototype starts locally | Always | `{prototype-start-command}` | Starts without error |
| Mock backend responds | Always | `{mock-backend-start-command}` then a smoke call against it | Returns the expected response shape |
| Routes/components navigable | Always | Manual click-through (or an automated route list) | Every screen named in the story's AC is reachable |
| No static-only deliverable | Always | Self-check against §4 | At least one real interaction is wired to mock data, not just idle renders |

Include a one-line check result note in the PR description (e.g., "prototype start — PASS · mock backend smoke call — PASS · all AC screens reachable").

If any applicable check fails, fix it before creating the PR.

**Pre-merge checklist:**
1. All applicable checks above pass
2. Prototype start command documented in PR description
3. Handoff note (mock-only parts) included in PR description
4. PR created with title `[ST-XXXXXX][FEATURE] Story title`
5. TL has reviewed and approved PR
6. Update story label to `status:done` after merge (or `status:testing` first, if the story requires QA validation of the prototype's flows)

---

## 6. Git Workflow

Branch name, commits, `[skip ci]`, PR title and description, and merge sync follow the `git-workflow` skill (`.mt-agent-devkit/skills/git-workflow/SKILL.md`). UI/UX additions:

- **PR description** also carries the start command and the mock-only handoff note (§4)

**Story comment after opening PR (mandatory):**

After creating the PR, post a short comment on the GitHub Issue:
> "PR #XX opened for review — [brief one-line summary of the flow prototyped]."
Tag **TL** in the comment to request review.

---

## 7. Document Placement

Place the prototype source under the project's standard feature-doc/source structure — before creating, moving or renaming a document, load the `project-docs` skill (`.mt-agent-devkit/skills/project-docs/SKILL.md`), which owns the path list (`{{AGENT_DIR_PREFIX}}/agents/context/Document_Index.md`) and naming. Link the wireframe/design source in the story's **Design Source** field (see `Story_Standard_UIUX.md §2`) rather than pasting it into the story body.

---

## 8. Reporting & Blockers

- Working Record writes follow the `working-record` skill (`.mt-agent-devkit/skills/working-record/SKILL.md`)
- Blockers follow `raise-question` section 4; UI/UX tags TL or PO

---

## 9. Runtime-State Handoff (mandatory before handoff)

Keep agent state local and uncommitted before signaling stage completion — the `handoff` skill owns the rule; your route reads its generated copy, `{{AGENT_DIR_PREFIX}}/agents/rules/Agent_Common_Read_On_Demand.md §5`.

---

## 10. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker (prototype won't start, mock backend won't run, script/CLI errors), follow the `troubleshooting` skill's check-memory → fix → record-to-memory protocol; your route reads its generated copy, `{{AGENT_DIR_PREFIX}}/agents/rules/Agent_Common_Read_On_Demand.md §2`.

---

## Version

**Version:** 1.2 (see `changes.json` for this file's change history) — not yet split into Bootstrap/Read-On-Demand tiers (tracked separately as issue #143).
**Created:** 2026-07-20
