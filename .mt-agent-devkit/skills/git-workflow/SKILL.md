---
name: git-workflow
description: Git workflow for every implementer - branch preflight inspect and create, branch naming, Conventional Commits, [skip ci] by CI path filter, standard PR-create form and post-QA merge sync. Load before branching, committing, pushing or opening a PR.
---

# Git Workflow

**Requires:** `shell-rules` (mutation safety), `pre-pr-gate` (before opening a PR)

## 1. Branch

1. Use the immutable `Base Branch` and full Base/Remote Base SHAs from Story Base Preflight `inspect`. Run `python .mt-agent-devkit/scripts/branch_preflight.py create` before any story status or product write; per-story pipeline state may be recorded after `inspect` PASS.
2. A BLOCKED preflight stops for direction: no stash, reset, rebase or repair.
3. Only after a successful `create`: record the Story Branch, move the story to `in-progress`, and verify `git branch --show-current` prints the new branch.
4. Branch name: `ST-XXXXXX/short-description`, off `main`.

## 2. Commit

1. Conventional Commits: `<type>(<scope>): <subject>`, subject in imperative mood, ≤ 50 characters for the **entire** header line.
2. Footer: always `Story: ST-XXXXXX`.
3. Subject-line length is a non-blocking style nit: a reviewer notes it in a PR comment but never requests changes or starts a fix loop over length alone. The rest of the convention is blocking.
4. Never commit runtime state (memory, working records, retros, telemetry, pipeline state): `handoff`.

## 3. `[skip ci]` — decided by the CI path filter, not the file extension

1. Before adding `[skip ci]`, read the `paths:` list of every workflow in `.github/workflows/`. If **any** file in the push matches **any** of those paths, the push must **not** carry `[skip ci]`, whatever the file type.
2. In this repo, `.claude/agents/templates/**`, `.claude/agents/workflows/**`, `.mt-agent-devkit/**`, provider `harness/**`, internal working wrappers/skills, root entrypoints, `scripts/**` and the validation workflow are all filtered: never `[skip ci]` there, even for Markdown-only pushes. Tracked retros, working records and memory under CI-filtered working directories also need CI.
3. Safe to skip only for non-code changes outside every active filter, such as `docs/**`. Never on a push containing code, config or build-file changes.
4. Why: `[skip ci]` leaves an **empty** check rollup, not a failing one, and the merge gate reads "no checks failed"; a suppressed required check looks like a repo with no CI. An empty commit cannot undo it: path-filtered triggers evaluate changed files, so recovery needs a real change under a filtered path.

## 4. Pull Request

The only way any role, or the orchestrator, creates a PR:

1. With the file tool, write the body to `{RUNTIME_ROOT}/tmp/<story>/pr_body.md`: `Closes #<issue-number>` (or `Refs #<issue-number>` when not closing), the one-line check result note (`pre-pr-gate`) and any live-instruction override (`raise-question`).
2. Fill every placeholder and run it. No variables, `$(...)` or `cd`.

   ```bash
   gh pr create --base main --title "[ST-XXXXXX][DEVKIT] Story title" --body-file {RUNTIME_ROOT}/tmp/<story>/pr_body.md
   ```

3. Wait for TL approval before merging.

**Hook:** on a story-ID branch, `gh pr create` is denied for a wrong or missing story title, a body without `Closes #N`/`Refs #N`, or an unreadable body ("cannot read body"). PR bodies are exempt from the bare-number ban.

## 5. Post-QA Merge Sync (after QA passes)

1. Merge: `gh pr merge <number> --merge`.
2. Sync: `git checkout main && git pull origin main`.
3. Confirm the merge commit is present locally before reporting completion.
