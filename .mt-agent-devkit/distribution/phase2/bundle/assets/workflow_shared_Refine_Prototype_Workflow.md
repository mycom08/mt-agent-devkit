<!-- Included by: templates/github/workflows/Refine_Prototype_Workflow_template.md, templates/strict/workflows/Refine_Prototype_Workflow_template.md -->

<!-- SHARED-START -->
# Refine Prototype Workflow

Triggered by: `"refine prototype"` in {ENTRYPOINT}

**Explicit-trigger-only.** This workflow never starts implicitly from a UI-shaped request elsewhere in a session — only this literal trigger starts it.

The orchestrator acts as UI/UX Designer directly for the entire duration of this workflow — read `.mt-agent-devkit/instructions/ui_ux_designer_instructions.md` and `.mt-agent-devkit/rules/UI_UX_Designer_Rules.md` before proceeding. **Do not spawn a UI/UX Designer agent** (or any other agent) at any point in this workflow, including repo setup.

---

## Pipeline State

The orchestrator maintains `{RUNTIME_ROOT}/tmp/refine_prototype_state.md` — **in this target project, never inside the prototype repo** (the prototype repo's commits are pushed in github mode; a log committed there would be noise inside the artifact under design). This file must exist from iteration 0, before Step 1 has produced a prototype repo at all — it is what makes an interruption before repo creation resumable.

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

1. Read `**Mode:**` from this project's `{ENTRYPOINT}` → record as `Mode` in the state file.
2. **Check for an existing companion repo.** Look for a sibling directory named `<this-repo-name>-ui-prototype` next to this project's own root. If found, confirm with the user: "Found `<path>` — is this the prototype repo to use?"
   - **Confirmed** → record its absolute path as `Prototype Repo Path`, then go to step 5 (framework).
   - **Not found, or user says it's the wrong one** → ask the user directly: **"Does a `-ui-prototype` companion repo already exist elsewhere for this project? If yes, give me its absolute path. If no, I'll create one."**
3. **If the user points to an existing repo** → record its absolute path as `Prototype Repo Path`, then go to step 5 (framework).
4. **If no existing repo** → create one:
   - Ask: **"Where should I create the `<this-repo-name>-ui-prototype` folder? Provide an absolute path."** Wait for the answer.
   - Create the folder at that path (if it does not already exist).
   - `git init` inside the folder.
   - **GitHub mode only:** `gh repo create` for the new repo (name: `<this-repo-name>-ui-prototype`; ask the user for visibility — public or private — if not already known). **Strict mode:** skip this sub-step — the folder stays a plain local repo, no remote.
   - **Install the shared harness through the common deployment engine.** Read this project's install receipt and selected provider bindings. Prepare reviewed companion-root/context/index adaptations for the new repository, preserving a lean Agent Roster of UI/UX Designer, Technical Lead and Product Owner. Use the receipt's mode and source identity; never fetch historical templates or reset runtime seeds.
     - For a released receipt, reacquire the exact recorded tag/commit's declared bundle and bootstrap, hash-check every asset, then use the pinned bootstrap's lifecycle plan with `--target <new-repo>` and `--profile repo`. Review the saved plan before apply. Do not resolve a different latest release between planning and application.
     - For a local/snapshot receipt, require the corresponding devkit source checkout and use its shared `lifecycle.py build --devkit-root <source-checkout> --target <new-repo>` contract. Verify the source revision against the receipt; if unavailable, stop for an explicit source choice rather than claiming release provenance.
     - Keep exactly one shared rules/instruction owner, concrete target runtime bindings, canonical provider-selection entrypoint, selected adapters and native surfaces. The full shared corpus may exist with only three active roster roles; dormant runtime seeds create only missing files.
   - **Leave the repo code-empty.** Iteration 1 builds the first screens. Do not invoke Build Software's scaffold-generation agent, which requires documents this standalone flow does not provide.
   - The shared `UI_Prototype_Rules.md` is the companion repository's Definition of Done.
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
   - Commit message: `prototype adaptation: <brief description>` — **never** the `Story:`/Conventional-Commits format used elsewhere in this project (`Developer_Rules_Bootstrap.md §6` / `UI_UX_Designer_Rules.md §6` do not apply to this repo's commits).
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
3. For the changes the user confirms, draft stories reusing `Create_Stories_Workflow.md`'s Step 2 (Draft Stories) and Step 4 (Create Stories) exactly — do not duplicate that logic here. Because this workflow runs from the **paired production repo's own session** (the target project that has `refine prototype` wired into its `{ENTRYPOINT}` — never the prototype repo, which has no story tracker in its lean 3-role roster), reusing `Create_Stories_Workflow.md` unmodified already creates the resulting issues/story files in the **paired production repo's tracker**, never the prototype repo. Nothing is auto-created — the user decides which drafts become real tracked issues, same draft-and-confirm gate `Create_Stories_Workflow.md` already enforces.
4. Report to the user which stories were created (or that none were, if the user declined all drafts).
5. Delete `{RUNTIME_ROOT}/tmp/refine_prototype_state.md`.

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
