# mt-agent-devkit — Priming Context (Read On Demand)

> Companion to `Project_Priming_Bootstrap.md`. **Never read as part of the Pre-Work Sequence, in whole or in part.** Fetch one section when its trigger fires; the routing table in the bootstrap file names which.

> **Numbering is shared with the bootstrap file and never reused**, so every pre-split `Project_Priming.md §N` citation still resolves — to whichever of the two files holds that number.

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
| Testing | TL | After TL approval, before merge (merge only after QA passes) |
| Done | PO | After all AC verified and ticked |

**Collaboration rules:**
- Story body contains only: User Story, AC, Deliverables
- All discussions happen as **comments** on the GitHub Issue — never in the body
- One topic per comment thread

For the full workflow: `.mt-agent-devkit/rules/Story_Standard.md`

---

## 4. Design First Before Implementation

For complex changes (new workflow stage, major template restructure, new devkit command), follow design-first:

1. **Developer** drafts a design as a story comment for TL review
2. **TL** approves before any file is written
3. No files changed until design is agreed

---

## 6. Internal Project Documents

`.mt-agent-devkit/context/Document_Index.md` is the single document path list, the planning documents included. Placement and naming rules: the `project-docs` skill.

---

## 10. Core Commands (devkit triggers)

| Command | What it does |
|---------|-------------|
| `init project [path]` | Scaffolds the AI Scrum team into a target project |
| `update project [path]` | Applies current local templates to an already-initialized project |
| `build software <idea>` | Analyzes an idea, plans the repo structure and wires the team (Stages 1–3) |
| `apply retros [label]` | Applies community retro contributions to the templates |
| `audit agent files` | Audits the devkit's own agent files for duplication, contradictions and dead references |
| `workflow help` | Shows this devkit's available commands |

The devkit also runs its own sprint workflows (`continue sprint`, `start story`, `refine sprint`, `plan next sprint`, `create stories`, `resume story`). Trigger routing: "Sprint Workflows (Devkit)" in `.mt-agent-devkit/instructions/orchestrator_instructions.md`.

---

## 15. How to Update a Template

When a rule, skill, workflow, or instruction file shipped to target projects needs to change, edit the active template in `.mt-agent-devkit/distribution/phase2/templates/` — never a target project's installed copy. `.claude/agents/templates/` is frozen legacy: change it only for a reviewed sync bridge. In this section, `templates/` means the active folder.

> **Dual-update + drift check:** Many templates have a devkit canonical copy under `.mt-agent-devkit/` (e.g. `templates/skills/tl-design/SKILL_template.md` ↔ `.mt-agent-devkit/skills/tl-design/SKILL.md`). Update **both** copies in the same change. Before editing, diff the two (`git diff --no-index <template> <canonical>`) and flag any **pre-existing** divergence — fix it in scope or record it as a follow-up story, so the two copies don't silently drift.
>
> **Carve-outs:**
> - **Intentionally-diverged copy:** If the canonical copy was deliberately rewritten for a different operational context (e.g. the devkit runs GitHub-mode-only while the template is target-project-generic), the two are *not* expected to match. Do **not** force them together — note the divergence as intentional (in the PR description and retro) and update the canonical copy only where the change actually applies to the devkit.
> - **No canonical copy exists:** Some templates have none (e.g. `Strict_Mode_Story_Guide_template.md`, which the GitHub-mode devkit never installs for its own agents). Note the absence and proceed; do **not** create a copy the devkit does not use.

**Steps (always in this order):**

1. **Edit the active template** under `.mt-agent-devkit/distribution/phase2/templates/`.
2. **Rebuild the bundle** with `python .mt-agent-devkit/distribution/phase2/build_bundle.py --root . --output .mt-agent-devkit/distribution/phase2/bundle`, then run the same command with `--check`.
3. **Never touch the version.** `.github/workflows/release.yml` owns `VERSION` end to end — do not edit it, and do not create a `changes.json` version key.
4. **Record the change** in the current `-SNAPSHOT` entry of `changes.json` and add a `CHANGELOG.md` bullet, following the `change-metadata` skill.

### Adding a New Agent Role (Nth Role)

Adding a role to the roster is a corpus-wide ripple, not a two-file change. Beyond the role's own instruction/rules template pair, check every existing enumeration of the current role list:

- `Story_Standard_template.md` (+ PO variant) — `**Assigned:**` valid-values list
- `templates/skills/po-write-story/SKILL_template.md` — `**Assigned:**` rule
- `build_bundle.py` — role and skill tuples
- `Create_Stories_Workflow_Shared_template.md`, `Sprint_Workflow_Shared_template.md` — implementer-role enumerations
- `Repo_Root_Shared_template.md` — Agent Roster table
- Devkit-internal file-count tables/prose in `Init_Project_Workflow.md`, `Build_Software_Workflow.md`, `Update_Project_Workflow.md`, `Sync_Devkit_Workflow*` (both the "Applies to" and separate "Expected files — rules/" enumerations — these are two distinct lists, easy to update only one)
- `scaffold_mechanical.sh`'s role loops (memory + working-record)

Grep the existing role list (e.g. `grep -rn "Developer\`, \`Technical Lead\`, \`QA\`, \`Business Analyst\`"`) across `templates/` and `working/` before starting, rather than relying on the AC to name every file.

**Working-record mirror:** a new role's working-record file is never created at scaffold time for the devkit's own team — `{RUNTIME_ROOT}/working-record/` is gitignored (root `.gitignore`). Only `instructions/`, `rules/`, `memory/` mirrors need to exist; the working-record file is created at runtime on first use, never committed.

### Splitting a Shared Rules/Instructions File into Bootstrap/On-Demand Tiers

Porting an already-validated bootstrap/on-demand split (e.g. the devkit-team's own `Agent_Common.md` → `Agent_Common_Bootstrap.md` + `Agent_Common_Read_On_Demand.md`, PR #162) into a new target — the `templates/` tree, a not-yet-split role, the Antigravity mirror — touches more than the two new files. Checklist (ST-000132 retro):

- **The two new files themselves** — same section boundary and numbering as the validated reference (bootstrap = unconditional-before-first-tool-call content; on-demand = everything else). Keep numbering gaps rather than renumbering when a section moves to the companion file — a stale citation should resolve to nothing, not silently to a different rule.
- **Every citing file** — grep the *old* filename with `§` across both `templates/` and `working/` (`grep -rn "OldFile.md §"`) and re-point each hit at the correct tier file and (possibly shifted) section number.
- **Workflow enumerations** — `init project` / `sync devkit` / `update project` workflow files and the scaffold scripts (`scaffold_mechanical.sh`/`.ps1`, both `.claude/` and `.antigravity/` surfaces) that list template files by name.
- **Bundle and `changes.json`** — rebuild and record new, renamed or retired files (see the steps above).
- **`scripts/validate_templates.py`'s `SECTION_REF_ALIAS`** — if the old filename's stem was a valid alias target, confirm it still resolves (or is removed if the old file is deleted) and that the new files' stems are added if anything cites them.
- **The `read-section` skill's own worked example** — if the example cites a file this change deletes or splits, repoint it to the correct successor file/section as part of the *same* change, not as an afterthought discovered later. Update both the template copy (`templates/skills/read-section/SKILL_template.md`) and the working copy (`.mt-agent-devkit/contracts/Read_Section.md`) together — they must not drift to two different examples.
- **Numbering-gap prose vs. the validator:** `validate_templates.py`'s section-ref checker treats any bare `§N` substring as a citation needing a real heading — it cannot tell a real citation from prose *describing* an intentional gap. When documenting a gap in prose (e.g. in a `## Version` footer), write "section N", never "§N" — the glyph is what triggers the check.


### Folding a Role's Rules into Skills (internal layout)

Replacing a role's rules files with canonical skills (ST-000288: the PO rules became the `po-*` skills) ripples beyond the new skill files:

- **Skills** — each canonical `.mt-agent-devkit/skills/<name>/SKILL.md` carries `name`/`description` frontmatter and a `**Requires:**` line naming the skills it depends on, instead of restating their rules. Add one `generated-wrapper`/`skill` inventory entry per provider in `migration-inventory.json`, then run `generate_wrappers.py`.
- **Deleted files** — post the deletion list on the story issue before `git rm`. Move each deleted baseline wrapper from `files` to the inventory's `retired` list, and remap inventory `consumers` that named a deleted file.
- **Routing** — switch the role in `read-routing.json` through the per-layout `bootstrap` mapping and `layouts` alternatives; a layout whose deployed files are unchanged keeps the old sources as its override.
- **Citations** — `scripts/validate_retired_citations.py` rejects any bare-filename or `§`-citation of a retired file in the internal corpus, the Phase 2 templates and the bundle assets (only the retirement ledgers are exempt); extend its list when retiring more files.
- **Spawn sites** — every workflow that spawns the role names the skill for that activity in the assignment.
- **Distribution (target layout, ST-000289)** — add a target-generic, mode-aware `templates/skills/<name>/SKILL_template.md` (same frontmatter and size budget as the canonical skill; `validate_internal_harness.py` checks both), add the name to `SHARED_SKILLS` in `build_bundle.py`, switch the role's `target` entry in the registry `bootstrap` mapping, drop the `layouts.target` overrides that kept the old sources, and rebuild the bundle. The old rules templates keep shipping, unused, until a separate retirement story removes them.
- **Target retirement (ST-000290, ST-000311)** — delete the old rules templates and their bundle assets, add each name with its own survivors to `RETIRED_SURVIVORS` in `build_bundle.py` (explicit shared and per-provider/mode legacy retirement entries with `required: false`; survivors are the shared skill IDs that own the file's rules, plus the role instructions where they load them), drop the registry's target alternatives and `role_sources` keys that named the files, and rebuild the bundle. Sync generates the retirement resolution only for a stock receipt-based file; a customised one raises the porting conflict; legacy installs keep the manual reviewed resolution.
---

## 16. Reference Links

1. **GitHub repo** — https://github.com/mycom08/mt-agent-devkit
2. **Raw content base URL** — derived at use time from the repo URL and pinned to a release tag:
   `https://raw.githubusercontent.com/mycom08/mt-agent-devkit/v<version>`. Never fetch from `/main`;
   it carries post-release work, so its contents do not match any version number.

---

**Document Version:** 1.2 — §3 Testing ownership and §10 command list corrected.
**Previous:** 1.1 — §15a de-numbered to an unnumbered `### Adding a New Agent Role (Nth Role)` sub-heading of §15: it was never wanted without §15, and as a flat `## 15a.` it bounded a §15 extraction and forced a second fetch. Preamble trimmed to drop the section inventory duplicated from the bootstrap file.
**Previous:** 1.0 — created 2026-08-21, split out of `Project_Priming.md` v1.1 (devkit's own team only).
**Audience:** Development team, architects, AI agents

