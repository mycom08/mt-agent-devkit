# mt-agent-devkit — Priming Context (Read On Demand)

> Companion to `Project_Priming_Bootstrap.md`. **Never read as part of the Pre-Work Sequence, in whole or in part.** Fetch one section when its trigger fires — the routing table in the bootstrap file names which. Use the `read-section` skill bound on `^## [0-9]+\.`; §15a is a `### ` sub-heading *inside* §15, so a §15 extraction correctly includes it.

> **Numbering is shared with the bootstrap file and never reused.** This file holds §3, §4, §6, §10, §15, §15a, §16; §1, §2, §5, §7, §8, §9, §11–§14 are in `Project_Priming_Bootstrap.md`. Every pre-split `Project_Priming.md §N` citation therefore still resolves — to whichever of the two files holds that number.

---

## 3. Story Workflow

Stories are **GitHub Issues** in `mycom08/mt-agent-devkit` (title format: `[ST-XXXXXX][DEVKIT] Title`).

**Status flow:**

```
Backlog → Ready → In Progress → Review → Testing → Done
                                                     ↓ (if bug found after Done)
                                                  Hotfix → Review → Testing → Done
```

| Status | Who Moves It | When |
|--------|-------------|------|
| Backlog | PO | After story creation |
| Ready | PO | After assigning to implementer |
| In Progress | Implementer | Work branch created |
| Review | Implementer | PR created, reviewer requested |
| Testing | QA | After TL approval and merge |
| Done | PO | After all AC verified and ticked |

**Collaboration rules:**
- Story body contains only: User Story, AC, Deliverables
- All discussions happen as **comments** on the GitHub Issue — never in the body
- One topic per comment thread

For the full workflow: `.claude/agents/working/rules/Story_Standard.md`

---

## 4. Design First Before Implementation

For complex changes (new workflow stage, major template restructure, new devkit command), follow design-first:

1. **Developer** drafts a design as a story comment for TL review
2. **TL** approves before any file is written
3. No files changed until design is agreed

---

## 6. Internal Project Documents

| Document | Path |
|----------|------|
| Business Requirements | `docs/requirements/Business_Requirements.md` |
| Implementation Roadmap | `docs/plan/Implementation_Roadmap.md` |
| Product Backlog | `docs/plan/Product_Backlog.md` |
| Sprint Overviews | `docs/sprints/Sprint_N_Overview.md` |

---

## 10. Core Commands (devkit triggers)

| Command | What it does |
|---------|-------------|
| `analyze <requirement>` | Runs the Analyst pipeline — produces docs in `result/analyst/` |
| `init project [path]` | Scaffolds the AI Scrum team into a target project |
| `update project [path]` | Applies current local templates to an already-initialized project |
| `workflow help` | Shows this devkit's available commands |

Sprint execution commands (`continue sprint`, `start story`, etc.) live in the **target project** CLAUDE.md, not here.

---

## 15. How to Update a Template

When a rule, workflow, or instruction file needs to change, update the source template in `.claude/agents/templates/` — never edit a target project's installed copy directly.

> **Dual-update + drift check:** Many templates have a devkit working mirror under `.claude/agents/working/` (e.g. `templates/rules/Story_Standard_template.md` ↔ `working/rules/Story_Standard.md`). Update **both** copies in the same change. Before editing, diff the mirror against its template (`git diff --no-index <template> <mirror>`, or read them side by side) and flag any **pre-existing** divergence — fix it in scope or record it as a follow-up story, so the two copies don't silently drift.
>
> **Carve-outs:**
> - **Intentionally-diverged mirror:** If the working mirror was deliberately rewritten for a different operational context (e.g. the devkit runs GitHub-mode-only while the template is target-project-generic), the two copies are *not* expected to match. Do **not** force the mirror to mirror the template edit — instead note the divergence as intentional (in the PR description and retro) and update the mirror only where the change actually applies to the devkit's context.
> - **No working mirror exists:** Some templates have no mirror under `.claude/agents/working/` (the file is absent, not merely diverged — e.g. `Strict_Mode_Story_Guide_template.md`, which the GitHub-mode devkit never installs for its own agents). In that case there is nothing to dual-update: note the absence and proceed; do **not** create a mirror the devkit does not use.

**Steps (always in this order):**

1. **Edit the template file** under `.claude/agents/templates/` (e.g., `.claude/agents/templates/rules/QA_Rules_template.md`)
2. **Bump the patch version** in `version.txt` (e.g., `0.1.5` → `0.1.6`)
3. **Add a new entry** to `changes.json` — place it **first**, at the **top** of the object, immediately after the opening `{`. This file is ordered **newest-first (descending)**: the current first key is the latest version and the last key is `0.0.1`:

```json
"0.1.6": {
  "new": [],
  "modified": [
    ".claude/agents/templates/rules/QA_Rules_template.md"
  ],
  "descriptions": {
    ".claude/agents/templates/rules/QA_Rules_template.md": "Fix: one-line summary of what changed and why"
  }
}
```

Use `"new"` for files added for the first time; `"modified"` for files that already existed. Both can be non-empty in the same entry.

> Target projects running `sync devkit` compare their installed version against `version.txt` and fetch only the files listed in every version entry between their current version and the latest. Keep the file's **newest-first (descending)** order — inserting out of order will cause `sync devkit` to skip or double-apply changes. `validate_templates.py` checks semver parseability only, never ordering direction, so a misplaced entry will not be caught by CI.

### 15a. Adding a New Agent Role (Nth Role)

Adding a role to the roster is a corpus-wide ripple, not a two-file change. Beyond the role's own instruction/rules template pair, check every existing enumeration of the current role list:

- `Story_Standard_template.md` (+ PO variant) — `**Assigned:**` valid-values list
- `Product_Owner_Rules_template.md` — roadmap `**Assigned:**` rule
- `Create_Stories_Workflow_Shared_template.md`, `Sprint_Workflow_Shared_template.md` — implementer-role enumerations
- `CLAUDE_Shared_template.md` — Agent Roster table
- Devkit-internal file-count tables/prose in `Init_Project_Workflow.md`, `Build_Software_Workflow.md`, `Update_Project_Workflow.md`, `Sync_Devkit_Workflow*` (both the "Applies to" and separate "Expected files — rules/" enumerations — these are two distinct lists, easy to update only one)
- `scaffold_mechanical.sh`'s role loops (memory + working-record)

Grep the existing role list (e.g. `grep -rn "Developer\`, \`Technical Lead\`, \`QA\`, \`Business Analyst\`"`) across `templates/` and `working/` before starting, rather than relying on the AC to name every file.

**Working-record mirror:** a new role's working-record file is never created at scaffold time for the devkit's own team — `.claude/agents/working/working-record/` is gitignored (root `.gitignore`). Only `instructions/`, `rules/`, `memory/` mirrors need to exist; the working-record file is created at runtime on first use, never committed.

---

## 16. Reference Links

1. **GitHub repo** — https://github.com/mycom08/mt-agent-devkit
2. **Raw content base URL** — https://raw.githubusercontent.com/mycom08/mt-agent-devkit/main

---

**Document Version:** 1.0 — created 2026-08-21, split out of `Project_Priming.md` v1.1 (devkit's own team only).
**Audience:** Development team, architects, AI agents
