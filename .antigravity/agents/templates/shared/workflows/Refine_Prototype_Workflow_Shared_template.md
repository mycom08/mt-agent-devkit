<!-- Included by: templates/github/workflows/Refine_Prototype_Workflow_template.md, templates/strict/workflows/Refine_Prototype_Workflow_template.md -->

<!-- SHARED-START -->
# Refine Prototype Workflow

Triggered by: `"refine prototype"` in CLAUDE.md

**Explicit-trigger-only.** This workflow never starts implicitly from a UI-shaped request elsewhere in a session — only this literal trigger starts it.

The orchestrator acts as UI/UX Designer directly for the entire duration of this workflow — read `.antigravity/agents/ui_ux_designer_instructions.md` and `.antigravity/agents/rules/UI_UX_Designer_Rules.md` before proceeding. **Do not spawn a UI/UX Designer agent** (or any other agent) at any point in this workflow, including repo setup.

---

## Pipeline State

The orchestrator maintains `.antigravity/agents/tmp/refine_prototype_state.md` — **in this target project, never inside the prototype repo** (the prototype repo's commits are pushed in github mode; a log committed there would be noise inside the artifact under design). This file must exist from iteration 0, before Step 1 has produced a prototype repo at all — it is what makes an interruption before repo creation resumable.

**On trigger — always check this file first:**
- If the file **exists** → read it and resume from the recorded state:
  - Empty `Prototype Repo Path:` → resume at Step 1
  - `Loop Status: active` → resume at Step 3 (mid-loop)
  - `Loop Status: ended` → resume at Step 4 (the loop itself already ended — the user already said stop; only the story-drafting handoff remains, and skipping straight back into the iteration loop here would silently drop it)
- If the file **does not exist** → create it now and start fresh at Step 1

**State file format:**
```markdown
# Refine Prototype Pipeline State
**Prototype Repo Path:** <absolute path, or empty if not yet created>
**Mode:** <github | strict>
**Framework:** <framework name, or empty if not yet decided>
**Loop Status:** <active | ended>
**Iteration Count:** <N>
**Iterations:**
- #1 — Asked: <what the user requested> | Changed: <what was actually changed> | Outcome: <kept | reverted | superseded by #N> | Commit: <sha>
- #2 — ...
**Updated:** YYYY-MM-DDTHH:MM
```

**Write rules:** Create at trigger time with `Loop Status: active` and every other field empty. Update `Prototype Repo Path`, `Mode`, `Framework` once Step 1 resolves them. Append one `Iterations` entry per completed iteration in Step 3, with its commit SHA. Set `Loop Status: ended` when the user chooses to stop (Step 3g). Delete the file only after Step 4 (story drafting) completes — a resume during story drafting still needs the full iteration log.

---

## Step 1 — Locate or Create the Prototype Repo

Skip this step entirely on resume if `Prototype Repo Path:` is already populated.

1. Read `**Mode:**` from this project's `CLAUDE.md` → record as `Mode` in the state file.
2. **Check for an existing companion repo.** Look for a sibling directory named `<this-repo-name>-ui-prototype` next to this project's own root. If found, confirm with the user: "Found `<path>` — is this the prototype repo to use?"
   - **Confirmed** → record its absolute path as `Prototype Repo Path`, then go to step 5 (framework).
   - **Not found, or user says it's the wrong one** → ask the user directly: **"Does a `-ui-prototype` companion repo already exist elsewhere for this project? If yes, give me its absolute path. If no, I'll create one."**
3. **If the user points to an existing repo** → record its absolute path as `Prototype Repo Path`, then go to step 5 (framework).
4. **If no existing repo** → create one:
   - Ask: **"Where should I create the `<this-repo-name>-ui-prototype` folder? Provide an absolute path."** Wait for the answer.
   - Create the folder at that path (if it does not already exist).
   - `git init` inside the folder.
   - **GitHub mode only:** `gh repo create` for the new repo (name: `<this-repo-name>-ui-prototype`; ask the user for visibility — public or private — if not already known). **Strict mode:** skip this sub-step — the folder stays a plain local repo, no remote.
   - **Scaffold the new repo's agent files by fetching from the devkit source — never from a local devkit checkout.** A target project's own file tree has no `templates/` directory and no `.antigravity/agents/working/scripts/scaffold_mechanical.sh` — those exist only inside the devkit repository itself, not here. Read `{DEVKIT_SOURCE_URL}` (`**Devkit source:**`) and `{DEVKIT_VERSION}` (`**Devkit version:**`) from **this project's own** `CLAUDE.md` — the new repo is scaffolded at the same devkit version this project already has installed. Fetch every file below from `{DEVKIT_SOURCE_URL}/.antigravity/agents/templates/...`, using the exact fetch mechanics this project's own `.antigravity/agents/workflows/Sync_Devkit_Workflow.md` already documents (WebFetch, curl fallback on truncated content; rules files adapted to `Mode` per its "Rules files — Adapt to mode" section; split workflow files combined shared+mode-specific per its "Workflow files — Overwrite" section) — every file below is written as new, not merged into an existing install:
     - **Directories:** `.antigravity/agents/{context,memory,rules,working-record,workflows,scripts,retros,tmp,docs}`. Strict mode also: `.antigravity/agents/docs/{stories,sprints,reviews}` and `.antigravity/agents/docs/story_counter.txt` containing `0`.
     - **Universal set (every devkit-scaffolded repo gets these, `-ui-prototype` or not):** all 10 workflow files; the 10 verbatim-tier rules files — `Agent_Common`, `Audit_Rules`, `Blocked_Request`, `CICD_Validation_Guide`, `Clean_Code_Rules`, `Product_Owner_Rules`, `Retro_Rules`, `Story_Standard_TL`, `Strict_Mode_Story_Guide` (strict mode only), `UI_Prototype_Rules` — with `{github-org}/{repo-name}` substituted to the **new repo's own** slug in github mode (never this project's slug); both version-check scripts; `devkit_version.txt` = `{DEVKIT_VERSION}`; blank memory/working-record files for all 6 roles (harmless orphans for the 3 roles this repo's lean roster doesn't use — the roster below is the source of truth for which roles are actually active); the two mode-specific `.gitignore` blocks any scaffolded repo gets; `VERSION` (`0.0.1-SNAPSHOT`); `CHANGELOG.md` (standard single-next-version header); and the `.antigravity/settings.json` `SessionStart` hook.
     - **Lean 3-role adaptive tier only — never the full 6-role set.** Fetch and adapt `CLAUDE.md` (from `templates/shared/CLAUDE_Shared_template.md`'s `SHARED-START`/`SHARED-END` block), `README.md`, `Project_Priming.md`, `Document_Index.md` — substitute `{{PROJECT_NAME}}` = `<this-repo-name>-ui-prototype`, `{{PROJECT_DESCRIPTION}}` = "Runnable UI/UX prototype for `<this-repo-name>`", `{{MODE}}` = this loop's `Mode`, `{{DEVKIT_SOURCE_URL}}`/`{{DEVKIT_VERSION}}` = the values read above. `CLAUDE.md`'s Agent Roster lists only 3 roles. Then only these 3 roles' instruction/rules files — same lean roster Build Software's own `-ui-prototype` companion repos use, for the same reason (UI/UX Designer builds it, TL is the only role that can approve a PR, PO is the only role that owns stories/ticks AC): `ui_ux_designer_instructions.md`, `technical_lead_instructions.md`, `product_owner_instructions.md`; `UI_UX_Designer_Rules.md`, `Technical_Lead_Rules.md`, `Product_Owner_Rules.md`, `Story_Standard.md`, `Story_Standard_PO.md`.
   - **Leave the repo code-empty.** Iteration 1 of Step 3 below builds the first screens — this workflow never invokes Build Software's own repo-scaffolding automation (its "UI Prototype Scaffold Generation" agent reads `repo_structure.md` and hard-blocks without `ui_design.md`, neither of which exists here), only restates the file-set conventions above.
   - `UI_Prototype_Rules.md` (already fetched verbatim above) is this repo's Definition of Done, same as any `-ui-prototype` repo.
   - Record the new repo's absolute path as `Prototype Repo Path` in the state file.
5. **Framework:**
   - If the prototype repo already has code (an existing repo reused in step 2/3) → leave `Framework` to be auto-detected in Step 2 below.
   - If the repo was just created code-empty (step 4) → check whether this project (the paired production repo) has a known frontend stack (Stage 1 scan / `Project_Priming.md §8 Tech Stack`). If it does, use that framework family. If there is no paired frontend stack to read, ask the user once: **"What framework should the prototype use?"** Record the answer as `Framework` in the state file — this is asked only once per loop, not per iteration.

---

## Step 2 — Serve the Prototype Locally

Auto-detect the prototype's project type and start/serve it locally using the same detection convention as the built-in `run` skill (package manager / framework detection, dev-server start command, surfaced local URL). If the repo is still code-empty at this point (first-ever run, iteration 0), skip serving until iteration 1 has produced something to run.

---

## Step 3 — Iteration Loop

Each iteration:

1. **Ask** the user what change they want (skip this on the very first iteration if the user already stated it as part of the trigger).
2. **Apply the change directly** to the prototype repo's working tree, acting as UI/UX Designer. Follow `UI_UX_Designer_Rules.md §4`'s runnable-prototype standard (real routes/components, wired interaction against the mock backend — not a static render) for anything genuinely new; a small visual/copy tweak to an existing screen does not need to re-satisfy the full standard from scratch.
3. **User reviews** — (re-)serve locally per Step 2 if needed, and wait for the user's feedback.
4. **Commit directly to the prototype repo — no PR, no review gate.** This no-review exception applies only to the prototype repo, never to any production repo:
   - Commit message: `prototype adaptation: <brief description>` — **never** the `Story:`/Conventional-Commits format used elsewhere in this project (`Developer_Rules.md §6` / `UI_UX_Designer_Rules.md §6` do not apply to this repo's commits).
   - **GitHub mode:** push the commit live immediately after committing (`git push`).
   - **Strict mode:** commit locally only — do **not** push. Leave it for the user to decide whether and when to push.
5. **Update the state file:** append an `Iterations` entry recording what was asked, what changed, the outcome (`kept` for now, `reverted`/`superseded by #N` if a later iteration undoes or replaces it — go back and correct the earlier entry's outcome when that happens), and the commit SHA. Increment `Iteration Count`.
6. **Stop and ask the user explicitly:** **"Continue iterating, or stop here?"** There is no fixed iteration cap.
   - **Continue** → loop back to sub-step 1.
   - **Stop** → set `Loop Status: ended` in the state file, proceed to Step 4.

---

## Step 4 — End Loop: Draft Stories

1. Read back the full `Iterations` log from the state file.
2. Present the log to the user and ask which changes are worth turning into real tracked work.
3. For the changes the user confirms, draft stories reusing `Create_Stories_Workflow.md`'s Step 2 (Draft Stories) and Step 4 (Create Stories) exactly — do not duplicate that logic here. Because this workflow runs from the **paired production repo's own session** (the target project that has `refine prototype` wired into its `CLAUDE.md` — never the prototype repo, which has no story tracker in its lean 3-role roster), reusing `Create_Stories_Workflow.md` unmodified already creates the resulting issues/story files in the **paired production repo's tracker**, never the prototype repo. Nothing is auto-created — the user decides which drafts become real tracked issues, same draft-and-confirm gate `Create_Stories_Workflow.md` already enforces.
4. Report to the user which stories were created (or that none were, if the user declined all drafts).
5. Delete `.antigravity/agents/tmp/refine_prototype_state.md`.

---

## Pipeline Rules

- **Check state file first** — always read `refine_prototype_state.md` before doing anything; it must exist from before a prototype repo does, so resumability branches three ways: empty `Prototype Repo Path:` → Step 1, `Loop Status: active` → Step 3, `Loop Status: ended` → Step 4 (never re-enter the iteration loop once the user has already said stop)
- **No agent spawn, ever, in this workflow** — the orchestrator acts as UI/UX Designer directly for repo setup and every iteration
- **Explicit trigger only** — never enter this workflow implicitly from a UI-shaped request elsewhere in a session
- **No fixed iteration cap** — every iteration ends with an explicit continue/stop question to the user
- **Prototype-repo commits are the only no-review-gate exception in this project** — it never extends to a production repo
- **Mode-dependent push** — github mode pushes every iteration's commit immediately; strict mode never pushes from this repo, leaving that decision to the user
- **Drafted stories always land in the paired production repo's tracker** — reusing `Create_Stories_Workflow.md` from this session already guarantees this; never create stories inside the prototype repo
<!-- SHARED-END -->
