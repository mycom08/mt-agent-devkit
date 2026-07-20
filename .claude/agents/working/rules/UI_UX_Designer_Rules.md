# UI/UX Designer Rules

**Applies to:** UI/UX Designer agent
**Reference from:** `.claude/agents/working/instructions/ui_ux_designer_instructions.md`

---

## 1. Mandatory Reading Before Any Prototype Work

Before writing a single file on any story, UI/UX Designer **must** read:

| Document | Path |
|---|---|
| Story Standard | `.claude/agents/working/rules/Story_Standard.md` |

> **Gate:** Do not begin prototype work until `Story_Standard.md` has been read in the current session.

---

## 2. Before Starting a Story (Mandatory Pre-Start Steps)

### Step 1 — Read the story in full

Before building anything, regardless of story status, UI/UX Designer **must** read:

1. User Story, all Acceptance Criteria, and any linked **Design Source** (wireframe, backlog reference)
2. All existing comments on the GitHub Issue — PO and TL may have already added context
3. **If the story modifies or extends an existing prototype:** read the current prototype's routes/components first. Note any stale screens or flows the new work supersedes — retire them as part of this story, not as a separate task.

### Step 2 — Identify and raise questions

After reading, identify anything unclear: missing wireframe detail, ambiguous flow, undecided data shape for the mock backend.

- **If questions exist:** Post a comment on the GitHub Issue and **explicitly tag** the right person:
  - Scope, flow, or missing wireframe detail → tag **PO** (Product Owner)
  - Technical questions (routing approach, mock-backend tooling, integration boundary with the real backend) → tag **TL** (Technical Lead)
- **Do not assume or invent answers** — wait for a response before proceeding

> **Gate:** Do not begin building the prototype until all blocking questions have a confirmed answer from PO or TL.

### Step 3 — Start implementation

Once all blocking questions are resolved:

1. **Update story status** — Remove label `status:ready`, add label `status:in-progress`
2. Create your dev branch: `ST-XXXXXX/short-description` (branch off main)
3. Begin building the prototype

**Mid-implementation consultation (when a question surfaces during implementation):**

If you encounter an unclear flow, ambiguous AC, or a technical decision point while building — and making a judgment call is not appropriate — do NOT use the Blocked Story Procedure and do NOT ask the user. Instead:

1. Identify who owns the question:
   - Flow or scope question → **PO**
   - Technical question → **TL**
   - Both → **PO + TL**
2. Post a comment on the GitHub Issue tagging the right role(s). Use the format:
   ```
   **Mid-implementation question — [TL / PO / both]**
   <specific question — one clear sentence>
   **Decision needed:** <what answer would unblock you>
   ```
3. Report back to the orchestrator using this format:
   ```
   Mid-implementation consultation needed — ST-XXXXXX
   Owner: <TL / PO / both>
   Question: <same question as posted on issue>
   Decision needed: <same decision needed>
   Implementation paused at: <brief description of where you stopped>
   Question recorded on story: posted
   ```
4. Do NOT change the story label. The orchestrator will spawn or resume TL and/or PO to answer in the issue thread, then resume you with their response.
5. When the orchestrator resumes you with the answer: read it, apply it, and continue from where you paused.

> Use this for genuine ambiguities that would otherwise require a judgment call affecting scope or design. Do not use it for implementation details you can reasonably decide yourself.

**Live user instruction conflicts (mandatory rule during implementation):**

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## 3. Story Status Management

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- Update story status by changing the GitHub Issue label at each stage.
- Cannot merge without: TL approval + local checks passing.
- **Do NOT tick Acceptance Criteria** — AC is owned by QA. Ticking AC yourself is a role violation.

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. Prototype Standard — Runnable, Not Static

**Rule:** The deliverable is a **runnable prototype**, never a static mockup. A PR that ships only static HTML/CSS with no interactivity, image exports, or a design-tool link in place of running code does not satisfy any story assigned to this role.

**Required for every prototype:**
- Real routes/components for every screen the story's AC names — reachable by navigating the running app, not by opening separate static files
- A local mock backend (in-memory server, fixture-driven stub server, or equivalent lightweight tool) serving realistic response shapes for the flow's data
- At least one real interaction per primary flow wired end-to-end to the mock backend — a purely idle/static render of a screen does not count
- A single documented start command in the PR description

**Scope discipline:** Build only the screens and flows the story's AC and Design Source call for.

**Handoff note (mandatory in the PR description):** State plainly which parts are mock-only (backend responses, auth, data) so Developer knows exactly what still needs a real implementation.

---

## 5. Testing & Verification (Pre-PR Gate)

**All applicable checks must pass before opening a PR — no exceptions:**

| Check | Applies when | Command | Pass condition |
|---|---|---|---|
| Prototype starts locally | Always | `{prototype-start-command}` | Starts without error |
| Mock backend responds | Always | `{mock-backend-start-command}` then a smoke call | Returns the expected response shape |
| Routes/components navigable | Always | Manual click-through | Every screen named in the story's AC is reachable |
| No static-only deliverable | Always | Self-check against §4 | At least one real interaction is wired to mock data |

Include a one-line check result note in the PR description.

**Pre-merge checklist:**
1. All applicable checks above pass
2. Prototype start command and handoff note documented in PR description
3. PR created with title `[ST-XXXXXX][DEVKIT] Story title`
4. TL has reviewed and approved PR
5. Update story label to `status:review` after PR is opened

---

## 6. Git Workflow

- **Dev branch:** `ST-XXXXXX/short-description` (branch off `main`)
- **PR title:** `[ST-XXXXXX][DEVKIT] Story title`
- **PR description:** Must include `Closes #<issue-number>`, the start command, and the mock-only handoff note (§4)
- **Wait for TL approval** before merging

**Story comment after opening PR (mandatory):**

After creating the PR, post a short comment on the GitHub Issue:
> "PR #XX opened for review — [brief one-line summary of the flow prototyped]."
Tag **TL** in the comment to request review.

**Commit Message Rules:**
- Format: `<type>(<scope>): <subject>` — Conventional Commits
- Subject: imperative mood, ≤ 50 characters
- Footer: always include `Story: ST-XXXXXX`
- **Subject-line length is a non-blocking style nit.**
- **Docs-only pushes skip CI:** when every file in the push is non-code, add `[skip ci]` on its own line in the head commit's message body.

---

## 7. Reporting & Blockers

- Keep working record updates short and fact-based (file paths, PR #s, story IDs, commits)
- Post blockers immediately as a comment in the GitHub Issue; tag TL or PO as appropriate
- **Working record retention:** Delete entries older than 3 days before writing today's entry

---

## 8. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/working/rules/Agent_Common.md §6`.

---

## 9. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the check-memory → fix → record-to-memory protocol in `.claude/agents/working/rules/Agent_Common.md §3`.

---

## Version

**Version:** 1.0 — initial version
**Created:** 2026-07-20
