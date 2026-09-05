# Audit Agent Files Workflow

Triggered by: `"audit agent files"` in the devkit's `CLAUDE.md`.

**Devkit-internal maintainer workflow.** Scans the devkit's own agent instruction/rules/workflow corpus for Tier A findings (cross-file duplication, contradictions, dead references) per `.claude/agents/working/rules/Audit_Rules.md`, and — only after explicit per-finding user approval — applies the corresponding edits on a dedicated branch with a git-scoped revert path.

**This is a workflow, not an agent role.** There is no `auditor_instructions.md` and no roster entry — the scan is performed by an anonymous general-purpose subagent, spawned fresh on every run, the same pattern `Analyst_Workflow.md` and `Build_Software_Workflow.md`'s Java-skeleton/UI-prototype/CI-bootstrap generation steps already use. Do not add `audit agent files` or an "Auditor" role to `Story_Standard*`, `Product_Owner_Rules`, `Create_Stories_Workflow*`, `Sprint_Workflow*`, or the `CLAUDE.md` Agent Roster table — none of those enumerations apply to this workflow.

**Scope note (this story, ST-000035):** this workflow is built and its apply/branch/revert mechanism is exercised by running it, but the devkit corpus's actual first real audit pass is a separate story (ST-000036). A run of this workflow today is expected to find few or zero findings above Tier A's thresholds; that is a property of the corpus, not a defect in the workflow.

---

## Report File

**Path:** `.claude/agents/internal/audit_report_YYYYMMDD_HHMMSS.md` — timestamp, not a run ID, so staleness is self-evident from the filename alone. Only **one** report is ever in flight; `.claude/agents/internal/` is gitignored (never committed).

**Header block:**
```markdown
# Audit Report — YYYYMMDD_HHMMSS
**Devkit Version:** <VERSION contents at scan time>
**Scanned:** <count> files across .claude/agents/templates, .claude/agents/workflows, .claude/agents/working
**Status:** pending-approval | applying | complete
```

**Body — four fixed-order sections, present even when empty (`_None found._`):**
```markdown
## Duplication - byte-identical
- D-1: <file:line-range>, <file:line-range>, ... → target: <target file:§section> — <one-clause rationale>

## Duplication - role-parallel
- RP-1: <file:line-range>, <file:line-range>, <file:line-range>, ... → target: <target file:§section> — <one-clause rationale>

## Contradictions (report-only)
- C-1: <file:line-range> vs <file:line-range> → report-only — <one-clause rationale>

## Dead references
- X-1: <file:line-range> → <proposed fix, or "remove — ambiguous target"> — <one-clause rationale>
```

Every finding ID (`D-n`/`RP-n`/`C-n`/`X-n`) is stable for the lifetime of the report — the approval and apply stages below refer to findings by these IDs.

---

## Stage 0 — Startup Crash Check (always runs first, before anything else)

Before doing anything else, glob `.claude/agents/internal/audit_report_*.md`.

**No file found** → proceed to Stage 1.

**File found** → read its `**Status:**` header and branch. Every value the header can hold has an explicit branch below — none of them fall through to another:

| Status found | Meaning | Action |
|---|---|---|
| `pending-approval` | A prior run's report was never approved or cancelled through to completion — nothing was edited. | Report the stale timestamp to the user. Delete the file silently. Continue to Stage 1 (fresh scan). |
| `applying` | A prior run crashed mid-batch. Files may be half-edited. | **Halt.** Print the report's full path and the finding IDs it lists. Tell the user to run `git status` / `git diff` and resolve manually (commit, or revert with `git checkout -- <files>`). **Do not** delete the report — it is the only record of what the partial batch was doing. **Do not** scan. Stop the workflow entirely; this is not a "continue after reporting" case like the other two rows. |
| `complete` | Should be unobservable — both normal exits (applied, cancelled) delete the file. If seen, it means a prior run's final delete step didn't run. | Delete the file. Continue to Stage 1. |

---

## Stage 1 — Spawn Scan Subagent

Spawn **one general-purpose agent** (**model: sonnet**) with a fully self-contained inline prompt (the agent has no memory of this conversation):

```
Scan the mt-agent-devkit corpus for Tier A audit findings and return a compact finding list — never the raw file contents you read.

Step 1 — read the detection spec in full before scanning anything:
.claude/agents/working/rules/Audit_Rules.md

This file is the complete and only behavior spec for this scan: the four finding classes (D-n, RP-n, C-n, X-n), the duplication-matching normalization rules, the >=15-line + mandatory-read-list gate, the closed role-alias table, the N>=2/N>=3 thresholds, the three-condition contradiction test and its carve-outs, the <!-- audit:keep --> absolute exclusion, and the dead-reference resolution rule. Do not invent detection criteria beyond what that file states — if something is ambiguous under the spec, do not report it as a finding.

Step 2 — scan these paths only:
- .claude/agents/templates/   (EXCLUDING .claude/agents/templates/github/** and .claude/agents/templates/strict/** entirely — Audit_Rules.md §3 carve-out)
- .claude/agents/workflows/
- .claude/agents/working/     (EXCLUDING .claude/agents/working/tmp/, .claude/agents/working/working-record/, .claude/agents/working/retros/, .claude/agents/internal/ — these are runtime/output paths, not corpus)

Step 3 — for each finding class, apply Audit_Rules.md's rules exactly:
- D-n: byte-identical after whitespace-collapse only, >=15 contiguous lines, N>=2, target file already on the consuming agent's mandatory read list (Agent_Common_Bootstrap.md §1's Project Priming/Rules/Memory sequence plus that role's own Rules file's own "Mandatory Reading" section — not a conditional trigger pointer).
- RP-n: whitespace-collapse + closed role-alias substitution, uniform substitution within each instance, N>=3, same >=15-line + mandatory-read-list gate, never YAML frontmatter or "## Your Role" sections.
- C-n: same-subject + both-unconditional + co-reachable, with every carve-out in Audit_Rules.md §3 applied (mode bifurcation, template-vs-working mirrors, role-scoped views, lifecycle phases, audit:keep). Report-only — do not propose an edit or pick a side.
- X-n: dead file-path or section-anchor references (per Audit_Rules.md §4's three-root resolution), and orphaned files. State a proposed fix only when the intended target is unambiguous; otherwise propose removal and say so.

Step 4 — return your findings as a single compact Markdown block, grouped in this exact order, using this exact section-header and per-line format (this becomes the body of the report file — do not add commentary outside it):

## Duplication - byte-identical
- D-1: <file:line-range>, <file:line-range> → target: <target file:§section> — <one-clause rationale>
(or "_None found._" if empty)

## Duplication - role-parallel
- RP-1: <file:line-range>, <file:line-range>, <file:line-range> → target: <target file:§section> — <one-clause rationale>
(or "_None found._" if empty)

## Contradictions (report-only)
- C-1: <file:line-range> vs <file:line-range> → report-only — <one-clause rationale>
(or "_None found._" if empty)

## Dead references
- X-1: <file:line-range> → <proposed fix or "remove — ambiguous target"> — <one-clause rationale>
(or "_None found._" if empty)

Also report: total file count scanned (for the report header).

Do not edit any file. Do not write the report file yourself — return the finding list as your final response; the orchestrator persists it. Report back your findings block plus the scanned-file count (max 5 bullets is not required here — return the full findings block verbatim, that is the deliverable).
```

The subagent's return value is the finding list only — never the corpus text it read to produce it. This is the context-isolation mechanism: the orchestrator's own session never ingests ~300 KB of corpus Markdown, regardless of how large the devkit grows.

---

## Stage 2 — Write Report

1. Orchestrator takes the subagent's returned finding block verbatim and writes it into a new report file at `.claude/agents/internal/audit_report_YYYYMMDD_HHMMSS.md` (create `.claude/agents/internal/` if it does not exist), with the header block filled in (`VERSION` contents, scanned file count from the subagent, `**Status:** pending-approval`).
2. If **all four** sections are `_None found._` → report to the user that the scan found no Tier A findings, delete the report file immediately (nothing to hold state for), and stop — do not proceed to Stage 3.

---

## Stage 3 — Present & Approval Gate

Present the report's findings to the user, grouped by class, in report order. State plainly: **`RP-n` findings default to NOT selected** — the user must opt in to each one individually by ID.

**Approval semantics per class:**

- **`D-n`** — may be approved individually by ID, or in a batch (e.g. "approve all D-n," or a list of IDs).
- **`RP-n`** — **individual, per-finding approval only.** Never accept a batch phrase like "approve all duplication" or "approve all RP" as approving every `RP-n` finding — require each ID named explicitly (naming several IDs in one reply, e.g. "approve RP-1, RP-3," is fine; an unqualified "approve all" never includes `RP-n`).
- **`C-n`** — never an edit target. Ask the user to state the resolution for each `C-n` finding they want to address; record their stated resolution as a note appended under that finding in the report (for the audit trail) and move on — no file in the corpus changes because of a `C-n` finding by itself.
- **`X-n`** — same as `D-n`: individual or batch approval.

Any finding not explicitly approved is skipped this run. The report stays as the record of what was found even for skipped findings — nothing is lost, the user can re-run `audit agent files` later and get a fresh scan.

If **no** `D-n`/`RP-n`/`X-n` finding was approved (only `C-n` resolutions were recorded, or the user declined everything) → skip Stage 4 entirely, go to Stage 5.

---

## Stage 4 — Apply Batch

Runs only when at least one `D-n`/`RP-n`/`X-n` finding was approved.

1. **Set `Status: applying`** in the report file — this is the crash marker described in Stage 0's table. Do this before touching any corpus file.
2. **Create a dedicated branch**: `audit/apply-YYYYMMDDHHMMSS` (same timestamp as the report), branched from the current branch.
3. **Capture baseline:** `git diff --stat` (expected empty — confirms a clean start on the new branch) and a baseline validator run:
   ```
   python scripts/validate_templates.py .claude/agents/templates .claude/agents/workflows .claude/agents/working
   ```
   Explicit path arguments, not the bare default scan — this is the only way `working/` gets real per-file Invariant #1B/#2/#6 coverage; the bare default only scans `templates/`+`workflows/`. Record the baseline `[ERROR]`/`[KNOWN_ISSUE]` lines verbatim.
4. **Apply each approved finding's edit** directly to the corpus files, per `Audit_Rules.md`'s proposed-edit description for that class (`D-n`/`RP-n`: canonical block in the target file, pointer left behind in the others; `X-n`: fix or remove the dead reference).
5. **Capture post-edit state:** `git diff --stat` (now non-empty — this is the scoped file list for a possible revert) and a second validator run with the **same explicit paths** as step 3.
6. **Compare validator runs.** Any `[ERROR]` line present after the batch that was not present in the baseline is a **new finding** — regardless of which file it's in or whether it looks related to this batch's edits.
   - **New finding found → revert the whole batch.** `git checkout -- <every file listed in the post-edit git diff --stat>`. This restores those files to their pre-batch state. Do not attempt a partial keep — the whole batch reverts together, since a new validator finding cannot be reliably attributed to only one of the applied edits.
   - **No new finding → keep the batch.** Stage the changed files and commit them on the dedicated branch, message: `audit: apply <N> finding(s) from audit_report_YYYYMMDD_HHMMSS.md` listing the applied finding IDs in the body.
7. **Update `changes.json` for any applied edit under `.claude/agents/templates/`** — target-project `update project`/`sync devkit` diff against `changes.json` by version, so a template fix left out of it is silently invisible to already-initialized projects. Add each touched template path to the `modified` array of the **current** `-SNAPSHOT` key in `changes.json` (the key named by the root `VERSION` file — the `release` workflow already created it) and append a one-line cause note to that path's `descriptions` entry (append to an existing description if the path already has one this version, e.g. from other same-version work) — the same fold-in pattern used for any other small fix landed against the current unreleased version. **Never create a new version key and never edit `VERSION` by hand** — `.github/workflows/release.yml` owns the version end to end. Edits confined to `.claude/agents/workflows/` or `.claude/agents/working/` are devkit-internal and never touch `changes.json` (same rule `Apply_Retros_Workflow.md` and the `CLAUDE.md` Apply Retros section already state). Include this file in the same commit as step 6.
8. **Git is the primary revert mechanism, not the validator verdict** — the validator comparison in step 6 is what *triggers* a revert decision, but the actual undo is `git checkout --`, scoped to exactly the files this batch touched (from step 5's diff --stat), never a wider `git reset`/`git clean`. If a revert happens after `changes.json` was already updated in step 7, `git checkout --` the `changes.json` edit too — it's part of the same batch and reverts with it.

---

## Stage 5 — Completion & Cleanup

1. Update the report's `**Status:**` to `complete`.
2. **Delete the report file** — both on a successful apply and on a cancelled/no-op run. The one exception is the Stage 0 `applying`-crash case, which is never reached from this stage (that path halts before Stage 5 and leaves cleanup to the user).
3. Report to the user (concise):
   ```
   audit agent files complete
   Scanned:   N files
   Findings:  D-n: X | RP-n: X | C-n: X | X-n: X
   Applied:   M finding(s) — branch audit/apply-YYYYMMDDHHMMSS (or "none — no findings approved")
   Reverted:  <finding IDs, if step 4's validator comparison caught a new finding — or "none">
   C-n resolutions recorded: <count, or "none">
   ```
   If a branch was created and kept, tell the user it is ready for their own review/merge — this workflow does not merge it automatically.

---

## Pipeline Rules

- **No persistent state file across runs.** The report file itself is the only state — its `Status` header is both the report and the crash marker. There is nothing else to resume; a fresh `audit agent files` invocation always starts at Stage 0's check.
- **Corpus text isolation.** The scan subagent (Stage 1) is the only place the full corpus is read. Its return value to the orchestrator is the compact finding list only, never raw file contents — this holds regardless of corpus size.
- **Per-finding approval, never whole-report accept.** Stage 3 requires explicit selection; there is no single "approve everything" action that also covers `RP-n`.
- **`RP-n` is always opt-in, individually.** This is a hard rule, not a suggestion — see Stage 3's approval semantics.
- **`C-n` never produces a file edit.** Its "approval" is the user's stated resolution, recorded for the audit trail only.
- **Dedicated branch, git-scoped revert.** Stage 4 never edits directly on the branch the workflow was invoked from; revert is always `git checkout -- <files>` scoped to the batch's own `git diff --stat`, never a broader destructive command.
- **Validator gate uses explicit paths.** Always `python scripts/validate_templates.py .claude/agents/templates .claude/agents/workflows .claude/agents/working` in Stage 4 — the bare default scan omits `working/` and would silently drop the only real coverage this workflow's edits get there.
- **Accepted gap, not fixed here:** `working/` coverage under the validator's Invariant #1A remains weaker than `templates/`/`workflows/` (see `Audit_Rules.md §4`) — git diff/revert is the actual safety net for that gap, not the validator verdict alone.
- **`changes.json` update is mandatory for applied `templates/` edits, not optional.** Stage 4 step 7 — a kept batch that touches `.claude/agents/templates/` and skips `changes.json` is invisible to target-project `update project`/`sync devkit` runs, which diff by version. Fold into the current `-SNAPSHOT` key; never create a version key and never hand-edit `VERSION` — the `release` workflow owns it.
- **This is a workflow, not a role.** No `**Assigned:**` value, no roster row, no memory file, no working record. See the header note above for the full list of enumerations this workflow is deliberately absent from.
