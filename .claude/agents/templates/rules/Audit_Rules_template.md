# Audit Rules — Mode-Adaptation Drift Detection Spec

**Applies to:** the scan subagent spawned by this project's `sync devkit` / `update project` final audit stage.
**Scope:** only the files written **in this run** via a model-generated merge strategy — `rules/` (adapt to mode), `instructions/` (merge), and `{{ORCHESTRATOR_FILE}}` (merge). Never the full `{{AGENT_DIR_PREFIX}}/agents/` tree, never a file written via verbatim overwrite (workflow files, script files), never a project-owned wiki file, and never a file that was resolved but not actually written (checksum skip, failed fetch).

This file defines **what counts as a finding** for a target-project scan. It is the injectable, detect-only counterpart of the devkit's own (devkit-internal) `Audit_Rules.md` — that file's Tier A classes (`D-n`/`RP-n`/`C-n`/`X-n`, cross-file dedup, canonical-block merging) do not apply here and are **not** part of this spec. A target-side scan has no access to `{{AGENT_DIR_PREFIX}}/agents/templates/` — target projects never receive that directory — so it cannot compare a written file against its source template, cannot propose a canonical merge target, and cannot tell duplication from intentional shared structure. This file exists to catch the **one finding class a target-side scan actually can detect with no template access**: damage introduced by the mode-adaptation step itself, visible from the written file's own internal content.

---

## 1. Why This Scan Is Report-Only, Always

Findings from this scan are never applied as edits inside the target project — `## Agent File Integrity` in this project's `{{ORCHESTRATOR_FILE}}` marks `rules/`, `instructions/`, and `{{ORCHESTRATOR_FILE}}` itself as protected paths, writable only by `sync devkit` / `update project`'s normal merge step, not by this audit. Every finding this spec defines is filed upstream as a GitHub Issue against the devkit repository (see the workflow file for the filing mechanics) — the fix, if any, lands in `templates/` and reaches this project on its next sync.

---

## 2. The Only Finding Class: `MA-n` (Mode-Adaptation Artifact)

A finding is a place in a scanned file where the content is only explicable as **incomplete or incorrect adaptation to this project's `**Mode:**`**, not a general writing-quality complaint. Four recognizable shapes, all filed under the same `MA-n` prefix:

| Shape | What it looks like |
|---|---|
| **Orphan heading** | A `#`/`##`/`###` heading whose entire body was mode-specific and got stripped, leaving the heading followed immediately by another heading, an empty line, or near-empty filler with no real instruction content. |
| **Dangling GitHub reference** | In a file written for `Mode: strict` — a surviving reference to `gh` CLI commands, `status:` issue labels, "GitHub Issue"/"GitHub PR" language, or GitHub Actions, that the strict-mode adaptation should have replaced with the local-file/`**Status:**`-field equivalent. |
| **Internal contradiction from partial strip** | The same file states two different procedures for the same subject (same actor, same artifact, same action) because only one branch of a `**GitHub mode:**` / `**Strict mode:**` conditional was removed during adaptation, leaving the other branch's instruction standing alone but now contradicted by a neighboring unconditional statement. |
| **Broken internal cross-reference** | A `§N` / `§Name` section-anchor citation, or a bare file-name reference, pointing at a heading or file that adaptation removed or renamed within the same written file or another file written in this same run. |

### Absolute exclusion

- **`<!-- audit:keep -->`** — any content marked with this comment is never flagged, under any circumstance. Checked before every other rule below.

### Explicitly out of scope

- **Anything not traceable to mode adaptation.** Generic prose quality, phrasing preferences, or content that would read the same regardless of `Mode: strict` vs `Mode: github` is never a finding — this scan is not a style pass.
- **Project-specific customizations.** Content this project's own agents wrote or edited (tech stack references, tooling commands, project conventions preserved by the merge step) is never flagged, even if it looks unusual — it is out of the devkit's control by design.
- **Anything already reachable through normal editing.** If a defect is something the project's own agents could and should fix as ordinary work (a typo, a stale internal doc link the agents maintain), it is not this scan's concern — this scan exists only for damage that traces back to the sync/update pipeline itself.

---

## 3. Report Format

A single flat list, one line per finding, in scan order:

```
- MA-1: <file>:<line-or-line-range> — <one-clause description of the drift and which shape (orphan heading / dangling GitHub reference / internal contradiction / broken cross-reference) it matches>
```

Or `_None found._` if the scan turned up nothing — this is the expected, common case; a scoped run over a handful of freshly-written files with no findings is silence, not a report (see the workflow file's "silent when clean" rule).

**Reviewability over exhaustiveness.** When in doubt whether something is genuinely traceable to mode adaptation versus a general content judgment call, it is not a finding — a report padded with marginal items defeats the purpose of a cheap, rarely-triggered scan.

---

## Version

**Created:** 2026-07-31 (ST-000037) — injectable counterpart of the devkit-internal `Audit_Rules.md` (ST-000035), scoped down to the single finding class a template-blind, detect-only target-side scan can actually support.
