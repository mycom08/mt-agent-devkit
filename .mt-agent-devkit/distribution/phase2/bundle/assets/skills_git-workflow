---
name: git-workflow
description: Git workflow for every implementer - branch preflight inspect and create, branch naming, Conventional Commits, [skip ci] by CI path filter, PR title and body, and post-QA merge sync. Load before creating a branch, committing or pushing.
---

# Git Workflow

**Requires:** `shell-rules` (mutation safety), `pre-pr-gate` (before opening a PR)

## 1. Branch

1. Use the immutable `Base Branch` and full Base/Remote Base SHAs from Story Base Preflight `inspect`. Run `python .mt-agent-devkit/scripts/branch_preflight.py create` before any story status or product write; never create a branch directly. Per-story pipeline state may be recorded after `inspect` PASS.
2. A BLOCKED preflight stops for direction: no stash, reset, rebase or repair.
3. Only after a successful `create`: verify the helper reports the requested branch at the recorded full SHA, record the Story Branch, then move the story to `in-progress` (remove `status:ready` or `status:backlog`).
4. Branch name: `ST-XXXXXX/short-description`, off the story's Base Branch (the feature branch).

## 2. Commit

1. **GitHub mode:** Conventional Commits, `<type>(<scope>): <subject>`, subject in imperative mood, ≤ 50 characters for the **entire** header line. Body (when needed) explains *why*, wrapped at 72 characters. Footer: always `Story: ST-XXXXXX`. Full type list: `docs/wiki/Development_Standards.md §2`.
2. **Strict mode:** `<primary-id> [<secondary-id>]: <message>` per `Strict_Mode_Story_Guide.md` (Commit Message Format); no `Story:` footer, no type prefix.
3. Subject-line length is a non-blocking style nit: a reviewer notes it in a PR comment but never requests changes or starts a fix loop over length alone. The rest of the convention is blocking.
4. Never commit runtime state (memory, working records, retros, telemetry, pipeline state): `handoff`.

## 3. `[skip ci]` — decided by the CI path filter, not the file extension

1. Before adding `[skip ci]`, read the `paths:` list of every workflow in `.github/workflows/`. If **any** file in the push matches **any** of those paths, the push must **not** carry `[skip ci]`, whatever the file type.
2. Safe to skip only for non-code changes outside every active filter (for example `docs/**` when no workflow filters it): put `[skip ci]` on its own line in the head commit's message body. Never on a push containing code, config or build-file changes.
3. Why: `[skip ci]` leaves an **empty** check rollup, not a failing one, and the merge gate reads "no checks failed"; a suppressed required check looks like a repo with no CI. An empty commit cannot undo it: path-filtered triggers evaluate changed files, so recovery needs a real change under a filtered path.

## 4. Pull Request

1. Title: `[ST-XXXXXX][FEATURE] Story title`.
2. Description: `Closes #<issue-number>` (or `Refs #<issue-number>` when not closing), the one-line check result note (`pre-pr-gate`) and any live-instruction override (`raise-question`).
3. Wait for TL approval before merging; no merge without TL code review.

**Strict mode:** no PR; follow `Strict_Mode_Story_Guide.md` for review and merge.

## 5. Post-QA Merge Sync (after QA passes)

1. Merge: `gh pr merge <number> --merge`.
2. Sync: `git checkout <feature-branch> && git pull origin <feature-branch>`.
3. Confirm the merge commit is present locally before reporting completion. **Gate:** never signal merge completion until the local branch is switched and synced.
