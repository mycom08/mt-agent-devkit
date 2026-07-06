# Version & Release Conventions (every component, every language)

**Every repo scaffolded by this devkit — regardless of language — gets a `VERSION` file and a `CHANGELOG.md` at its root, including the project-orchestrator root folder in a multi-repo `build software` build.** These two files are written once, universally, by `working/scripts/scaffold_mechanical.sh` (the same script every `init project` / `build software` repo scaffold runs through) or, for the project-orchestrator root folder specifically (which never runs that script), directly by `Build_Software_Workflow.md`'s Stage 4 Path B.

This is a devkit-wide convention, not a Maven/Gradle artifact-version detail. The `-SNAPSHOT` suffix and "who bumps it, and when" semantics apply the same way whether the repo is Java, Node, Kotlin, or anything else — it just means "this is the current in-progress version; a human deliberately strips the suffix later to cut a release." Java repos additionally wire a real CI-automated release process around these two files (see `java/Java_Skeleton_Conventions.md`'s "Version & Release Management" section) — that automation is language-specific and layered on top; the files and their format below are not.

---

## `VERSION`

A single-line file at the repo root, no trailing whitespace, one of two shapes:
- **Snapshot** (the normal day-to-day state): `x.x.x-SNAPSHOT`.
- **Release** (only momentarily true, set by hand right before cutting a release): `x.x.x`, no suffix.

**Initial value at scaffold time: `0.0.1-SNAPSHOT`** — every repo, every language, no exceptions. Stripping the `-SNAPSHOT` suffix to cut an actual release is a deliberate, manual, later action by a human — scaffolding never produces a non-`-SNAPSHOT` `VERSION`.

## `CHANGELOG.md`

Not [Keep a Changelog](https://keepachangelog.com/)'s two-permanent-section format — this devkit uses a single-next-version-heading style instead:

```markdown
# Changelog

All notable changes to this project are documented in this file.

## Contribution Convention

After merging a PR to main, the implementer adds a bullet entry under the relevant
subsection of the current Unreleased version below. Use the following subsections:

- **Changes** — new features, enhancements, refactors, documentation, CI/tooling
- **Bug Fixes** — defect corrections and hotfixes

Entry format: `- [ST-XXXXXX] Short description of the change.`

---

## [0.0.1] - Unreleased

### Changes

### Bug Fixes
```

The top heading always names the *next* version to be cut (matching `VERSION` once its `-SNAPSHOT` suffix is stripped), suffixed `- Unreleased` until a release process stamps it with the actual release date. `[ST-XXXXXX]` matches this devkit's own story ID convention (`Story_Standard.md`) — target-project developers add one bullet per merged story under `### Changes` or `### Bug Fixes` as they go, so the section is never empty by the time someone wants to release.

## Must not do

- Do not skip `VERSION` or `CHANGELOG.md` for any scaffolded component, regardless of language or whether it has any further release automation.
- Do not generate `VERSION` with any value other than `0.0.1-SNAPSHOT` at scaffold time.
- Do not use the Keep a Changelog two-permanent-section format — use the single-next-version-heading style above. (Java repos additionally have `release.yml` validate directly against this structure — see `java/Java_Skeleton_Conventions.md`.)
- Do not recreate these files if they already exist (idempotent — scaffold once, then leave them for developers/CI to update).
