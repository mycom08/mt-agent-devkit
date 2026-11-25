# Apply Retros Workflow

Triggered by: `"apply retros"` or `"process retros"` (optional label filter, e.g. `apply retros sprint-3`) in the devkit's CLAUDE.md.

Scans community retro contribution Issues on `mycom08/mt-agent-devkit`, aggregates their signal items into a prioritized list of devkit improvements, lets the user choose which to apply, edits the relevant active templates directly, rebuilds the deployment bundle, and records the whole batch in the current unreleased version's `changes.json` entry and `CHANGELOG.md` section. After the checks pass it archives and closes the processed Issues. The version number itself is never touched — the `release` workflow owns it.

This is a **devkit-internal maintainer workflow** — it is never deployed to target projects and the workflow file itself does not appear in `changes.json`. Only the shipped files it edits during a run are recorded.

---

## Prerequisites

- `gh` must be authenticated (`gh auth status`). If not, stop and tell the user to authenticate — this workflow reads and closes GitHub Issues.
- Target-template edits go under `.mt-agent-devkit/distribution/phase2/templates/` only. `.claude/agents/templates/` is frozen legacy: never edit it, except for a sync bridge change that goes through a reviewed PR. Devkit-internal workflow files (`.mt-agent-devkit/workflows/commands/`) may be improved too, but they ship nothing and are not listed in `changes.json`.

---

## Stage 0 — Resolve Scan Scope

1. **Base filter is always `retro:contribution`.** Retro Issues are identified by this label.
2. If the user supplied an extra label after the trigger (e.g. `apply retros sprint-3`), add it as a second filter — scan only Issues carrying **both** labels.
   If no extra label was given, scan **all** open `retro:contribution` Issues.
3. Fetch the Issues:
   ```bash
   gh issue list --repo mycom08/mt-agent-devkit \
     --label "retro:contribution" [--label "<extra-label>"] \
     --state open --limit 100 \
     --json number,title,body
   ```
4. If zero Issues are returned → notify the user (_"No open retro:contribution issues found for the given scope."_) and stop.
5. Report the scan scope before parsing:
   > _"Scanning N retro contribution issue(s): #A, #B, #C …"_

---

## Stage 1 — Parse & Aggregate Signals

For each Issue body (which follows the `# Retro Export` format from `community-retros/README.md`):

1. Extract every bullet under the four signal sections — `### [context]`, `### [instruction]`, `### [workflow]`, `### [failure]` — and the `## What Worked Well` section. Ignore `- None.` placeholders.
2. Tag each extracted signal with its **source Issue number** and **signal type**.
3. **Cluster** signals that describe the same underlying problem across different Issues into a single item, and record the **frequency** (how many distinct Issues raised it). Recurring signals carry more weight (see Stage 2).
4. Keep `## What Worked Well` notes aside — they are **not** changes to apply, but surface them in the final report so good patterns are not accidentally removed.

---

## Stage 2 — Map & Prioritize

### Map each item to a target file

This table is the routing owner (`community-retros/README.md` points here). Paths are relative to `.mt-agent-devkit/distribution/phase2/templates/`.

| Signal type | Owner in the active layout |
|---|---|
| `[context]` | `context/Project_Priming_template.md` (project root: `context/Project_Root_Priming_template.md`) or `context/Document_Index_template.md` for document paths; memory conventions: `skills/agent-memory/SKILL_template.md` |
| `[instruction]` | a role's identity or load map: `instructions/<role>_instructions_template.md`; the orchestrator: `shared/orchestrator_instructions_shared_template.md` or its `github/` or `strict/` variant; a procedure: the owning skill |
| `[workflow]` | `shared/workflows/*_Shared_template.md` (mode-specific text: `github/workflows/` or `strict/workflows/`) or `workflows/*_template.md`; a step a skill owns: that skill |
| `[failure]` | the skill that owns the activity, `skills/<name>/SKILL_template.md` |

**Owning skill:** role procedures are the `dev-*`, `tl-*`, `qa-*` and `po-*` skills; cross-role procedures have their own skill (for example `pre-pr-gate`, `git-workflow`, `pr-review`, `comment`, `agent-security`). Business Analyst and UI/UX Designer have no role skills: use `rules/Business_Analyst_Rules_template.md` or `rules/UI_UX_Designer_Rules_template.md`. A shared standard stays in its `rules/` template (for example `Story_Standard_template.md`, `Retro_Rules_template.md`). Confirm the owner exists before listing it; never route to a retired file.

Text between `BEGIN GENERATED` and `END GENERATED` markers is a copy: edit the part in the skill it names, then run `python .mt-agent-devkit/scripts/generate_common_blocks.py`.

If an item does not map to any target template (e.g. it only concerns a devkit-internal workflow), still list it but mark its target as `devkit-internal (no changes.json entry)`.

### Priority ordering

Order items **most-worth-applying first**, using this rubric (higher tier wins; within a tier, higher frequency wins):

1. **Critical `[failure]` — missing guardrail.** A clear failure pattern with real consequences (secret/credential leakage, data loss, broken or stuck pipeline, irreversible git operation). A **single occurrence is enough** to rank at the top.
2. **Token / efficiency reductions.** Changes that cut token usage or remove redundant work on every run (trimming bloated instructions, deduplicating rules, flattening repeated gate chains).
3. **Workflow correctness.** `[workflow]` signals fixing incorrect, ambiguous, or contradictory steps.
4. **Recurring signals (≥2 Issues).** Any signal raised in multiple Issues, ranked by frequency.
5. **Instruction / context clarity.** One-off `[instruction]` and `[context]` improvements.

Weak one-off signals with low impact go to the bottom as **"note only"** — listed but not pre-selected.

---

## Stage 3 — Present & User Decision

Present the prioritized items as a numbered table. Do **not** edit any file yet.

```
Retro improvements found across N issue(s):

#  Pri  Type         Freq  Target file                                  Proposed change
1  ★★★  [failure]    1     skills/pre-pr-gate/SKILL_template.md         Add pre-push secret-scan gate; credentials from env, no inline literal
2  ★★   [workflow]   2     shared/workflows/Sprint_Workflow_Shared…     Flag "automation collection update required" when response shapes change
3  ★    [instruction]1     instructions/qa_instructions_template.md     Define "no domain label" test-folder fallback
…
n  –    [context]    1     context/Project_Priming_template.md          (note only) version-qualified library identifiers
```

Then ask:
> _"Which items should I apply? Reply with numbers (e.g. `1,2,5`), `all`, or `none`. Items not selected are skipped this run; their issues stay open unless you also say to close them."_

Only the selected items proceed to Stage 4. If the user replies `none`, skip to Stage 6 (the issues remain open by default).

---

## Stage 4 — Apply Changes (orchestrator applies directly)

For each **accepted** item, the orchestrator edits the target file directly — no agents are spawned.

1. Read the target template, make the minimal edit that addresses the signal, and preserve surrounding style. An item that can only be met by editing a file outside `.mt-agent-devkit/distribution/phase2/templates/` (other than devkit-internal workflows and dual-update copies) is not applied here: report it as needing a story.
2. If a template has a devkit canonical copy under `.mt-agent-devkit/` (the **dual-update pattern**, `Project_Priming_Read_On_Demand.md §15`), update both copies, applying its carve-outs.
3. Group edits by file so each file is touched once.
4. Track a one-line description of every changed shipped file for Stage 5.
5. After editing any bundle source (every active template, plus the other `build_bundle.py` sources), rebuild the bundle and check it:
   ```bash
   python .mt-agent-devkit/distribution/phase2/build_bundle.py --root . --output .mt-agent-devkit/distribution/phase2/bundle
   python .mt-agent-devkit/distribution/phase2/build_bundle.py --root . --output .mt-agent-devkit/distribution/phase2/bundle --check
   ```
   Never hand-edit `bundle/`.

> Never edit a target project's installed copy. Only edit the source templates under `.mt-agent-devkit/distribution/phase2/templates/` (and devkit canonical copies where the dual-update pattern applies).

---

## Stage 5 — Manifest & Changelog (one fold-in for the whole batch)

Record everything from this run against the **current in-progress version** — the `x.y.z-SNAPSHOT` value in the root `VERSION` file.

> **Never edit `VERSION` by hand.** The `release` workflow (`.github/workflows/release.yml`) owns it end to end: it strips the `-SNAPSHOT` suffix, stamps the `CHANGELOG.md` heading and the `changes.json` key, tags the release, then opens the next snapshot in all three files. There is no version-bump step in this pipeline.

1. **Read the current snapshot version** from `VERSION` (e.g. `0.1.49-SNAPSHOT`). Its `changes.json` key and its `## [0.1.49] - Unreleased` `CHANGELOG.md` heading already exist — the release job created both. Read the value; do not predict it.
2. **Record shipped changes as the `change-metadata` skill describes** (`.mt-agent-devkit/skills/change-metadata/SKILL.md`; load it before writing). In short: one line per changed shipped file in `descriptions` of the existing `-SNAPSHOT` entry, with `[Retro #NN]` in place of the story ID:
   ```json
   "descriptions": {
     ".mt-agent-devkit/distribution/phase2/templates/skills/pre-pr-gate/SKILL_template.md": "[Retro #27] Add a pre-push secret-scan gate with env-sourced credentials."
   }
   ```
   - Leave `new`, `modified`, `removed` and `files` alone, and never create a version key.
   - If the path already has a description, append your clause with `; `.
   - Devkit-internal files that ship nothing are not listed. If no shipped file changed, leave `changes.json` untouched.
3. **Update `CHANGELOG.md`** — add the applied changes under the current `## [x.y.z] - Unreleased` heading (`### Changes` / `### Bug Fixes`), referencing the source Issue(s). Never add or edit a version heading by hand.

---

## Stage 6 — Archive & Close Issues

**Check first.** Run every check the `pre-pr-gate` skill (`.mt-agent-devkit/skills/pre-pr-gate/SKILL.md`) lists for the changed paths, including `build_bundle.py --check` (a run that changed no file has none to run). If any check fails or cannot run, fix the cause and re-run. Until all applicable checks pass, archive and close no Issue: stop and report.

For each Issue whose signals were processed this run (applied or explicitly rejected by the user):

1. **Archive** — save the Issue body to `community-retros/archive/sprint-<N>_<YYYY-MM-DD>.md` (resolve `N` and the date from the Retro Export header). Create `community-retros/archive/` if it does not exist. The archived file is the audit trail — never delete it.
2. **Close** — close the Issue with a comment summarizing the outcome and naming the unreleased version it landed in (`VERSION` minus its `-SNAPSHOT` suffix):
   ```bash
   gh issue close <number> --repo mycom08/mt-agent-devkit \
     --comment "Processed for the upcoming v<UNRELEASED_VERSION>. Applied: <list or 'none'>. Skipped: <list or 'none'>. See CHANGELOG.md."
   ```
3. Issues that were in scope but had **no** accepted items remain **open** unless the user said to close them.

---

## Stage 7 — Report

Summarize to the user (concise):

```
apply retros complete — recorded against v<UNRELEASED_VERSION> (unreleased)

Scanned:   N issue(s) [scope]
Applied:   M change(s) across K template file(s)
Skipped:   <count> (note-only or user-declined)
Archived:  <list of archive files written>
Closed:    <issue numbers>   |  Left open: <issue numbers>

What worked well (preserve — do not regress):
  - <surfaced positive patterns>
```

---

## Pipeline Rules

- **Never edit before the user confirms** in Stage 3.
- **Never hand-edit `VERSION`** — the `release` workflow owns it. All accepted changes fold into the current `-SNAPSHOT` key's existing `changes.json` entry; a run never creates a version key.
- **`changes.json` gets `descriptions` lines for shipped files only**, as the `change-metadata` skill describes.
- **Rebuild and check the bundle** after editing any bundle source.
- **No archive or close before the applicable checks pass** (Stage 6).
- **`.claude/agents/templates/` stays unchanged**, except for a reviewed sync bridge.
- **Dual-update pattern** — when a template has a devkit canonical copy, update both (`Project_Priming_Read_On_Demand.md §15`).
- **`gh` required** — the workflow reads and closes GitHub Issues; stop early if `gh` is unauthenticated.
- **Privacy is already enforced upstream** — retro Issues are privacy-filtered at export. If any signal still contains project-specific detail, generalize it before writing it into a template, per `Retro_Rules.md`.
- **No persistent state file** — the run is interactive and short; if interrupted after Stage 4 began, check `git status` and finish or revert the edits before restarting.
