# Apply Retros Workflow

Triggered by: `"apply retros"` or `"process retros"` (optional label filter, e.g. `apply retros sprint-3`) in the devkit's CLAUDE.md.

Scans community retro contribution Issues on `mycom08/mt-agent-devkit`, aggregates their signal items into a prioritized list of devkit improvements, lets the user choose which to apply, edits the relevant templates directly, and records the whole batch against the current unreleased version's `changes.json` entry and `CHANGELOG.md` section. Then archives and closes the processed Issues. The version number itself is never touched — the `release` workflow owns it.

This is a **devkit-internal maintainer workflow** — it is never deployed to target projects and the workflow file itself does not appear in `changes.json`. Only the template files it edits during a run are versioned.

---

## Prerequisites

- `gh` must be authenticated (`gh auth status`). If not, stop and tell the user to authenticate — this workflow reads and closes GitHub Issues.
- All edits target template files under `.claude/agents/templates/` only. Devkit-internal workflow files (`.antigravity/agents/workflows/`) may be improved too, but they do **not** count toward `changes.json`.

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

Using the routing in `community-retros/README.md`:

| Signal type | Usual target template |
|---|---|
| `[context]` | `templates/context/Project_Priming_template.md` or a memory template |
| `[instruction]` | `templates/instructions/{role}_instructions_template.md` |
| `[workflow]` | a workflow template under `templates/shared/workflows/` or `templates/{mode}/workflows/`, or `templates/rules/Agent_Common_Bootstrap_template.md` / `templates/rules/Agent_Common_Read_On_Demand_template.md` |
| `[failure]` | a rules template (e.g. `templates/rules/Developer_Rules_Bootstrap_template.md`) or an instruction template |

If an item does not map to any template file (e.g. it only concerns a devkit-internal workflow), still list it but mark its target as `devkit-internal (no changes.json entry)`.

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
1  ★★★  [failure]    1     rules/Developer_Rules_Bootstrap_template.md            Add pre-push secret-scan gate; credentials from env, no inline literal
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

1. Read the target template, make the minimal edit that addresses the signal, and preserve surrounding style.
2. If a change affects a template that also has a devkit working copy kept in sync (the **dual-update pattern** — e.g. a `shared/workflows/*_Shared_template.md` change that mirrors `.antigravity/agents/working/workflows/*.md`), update both copies.
3. Group edits by file so each file is touched once.
4. Track, for every changed template under `.claude/agents/templates/`, a one-line description for `changes.json`. Separate `new` (first-time files) from `modified` (already existed).

> Never edit a target project's installed copy. Only edit the source templates under `.claude/agents/templates/` (and devkit working copies where the dual-update pattern applies).

---

## Stage 5 — Manifest & Changelog (one fold-in for the whole batch)

Record everything from this run against the **current in-progress version** — the `x.y.z-SNAPSHOT` value in the root `VERSION` file.

> **Never edit `VERSION` by hand.** The `release` workflow (`.github/workflows/release.yml`) owns it end to end: it strips the `-SNAPSHOT` suffix, stamps the `CHANGELOG.md` heading and the `changes.json` key, tags the release, then opens the next snapshot in all three files. There is no version-bump step in this pipeline.

1. **Read the current snapshot version** from `VERSION` (e.g. `0.1.49-SNAPSHOT`). Its `changes.json` key and its `## [0.1.49] - Unreleased` `CHANGELOG.md` heading already exist — the release job created both. Read the value; do not predict it.
2. **Fold this run's changes into that existing `changes.json` entry** — do **not** create a new version key. List every changed **template** file under `new` / `modified`, with a `descriptions` entry per file:
   ```json
   "0.1.49-SNAPSHOT": {
     "new": [],
     "modified": [
       ".claude/agents/templates/rules/Developer_Rules_Bootstrap_template.md"
     ],
     "descriptions": {
       ".claude/agents/templates/rules/Developer_Rules_Bootstrap_template.md": "Retro (#27): add pre-push secret-scan gate — credentials must source from env with no inline literal default"
     }
   }
   ```
   - Reference the source Issue number(s) in each description (e.g. `Retro (#27)`).
   - If a path already has a `descriptions` entry under this key (from earlier work on the same unreleased version), **append** your clause rather than replacing it.
   - Devkit-internal workflow edits (under `.antigravity/agents/workflows/`) are **not** listed in `changes.json`.
   - If **no** template files changed (all accepted items were devkit-internal), leave `changes.json` untouched — there is nothing for `sync devkit` to fetch.
3. **Update `CHANGELOG.md`** — add the applied changes under the current `## [x.y.z] - Unreleased` heading (`### Changes` / `### Bug Fixes`), referencing the source Issue(s). Never add or edit a version heading by hand.

---

## Stage 6 — Archive & Close Issues

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
- **Only `.claude/agents/templates/` files go in `changes.json`** — devkit-internal workflow edits do not.
- **Dual-update pattern** — when a shared template has a synced devkit working copy, update both.
- **`gh` required** — the workflow reads and closes GitHub Issues; stop early if `gh` is unauthenticated.
- **Privacy is already enforced upstream** — retro Issues are privacy-filtered at export. If any signal still contains project-specific detail, generalize it before writing it into a template, per `Retro_Rules.md`.
- **No persistent state file** — the run is interactive and short; if interrupted before Stage 5, nothing has been written, so it restarts cleanly.
