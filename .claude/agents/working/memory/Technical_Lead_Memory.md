# Technical Lead Memory

> Two-tier memory (devkit-internal pilot, `Agent_Common_Records.md §8`, issue #118). This is the lean, always-read index — titles and grep-able keywords only, no fact bodies. Full text lives in `Technical_Lead_Memory_Archive.md`. Before starting a task, scan the titles/keywords below for a match; if one matches, retrieve just that fact per §8's bounded-read recipe — never read the whole archive. Numbering gaps (6, 13–16) are pruned facts — do not renumber, here or in the archive.

## Standing Checks

*(none yet — no current fact reduces to an unconditional always-do action; entries move here if a future fact qualifies)*

## Keyword Index

### Fact 1 — Template paths must resolve against the deployed target, never the devkit tree
Keywords: `templates/`, deployed target-project inventory, devkit-only automation, `{DEVKIT_SOURCE_URL}`, `Sync_Devkit_Workflow_template.md`, target-side audit, verbatim-overwrite self-heal

### Fact 2 — `validate_templates.py` cannot catch the Fact-1 class — verdicts must be differential
Keywords: `_FILEREF_RE`, `.md`-only, `_resolve_file_ref`, three roots, `SCAN_DIRS`, `working/` file not covered, `changes.json` ordering, `git worktree` differential, `check_shared_integrity`, Windows backslash false positive

### Fact 3 — Thin variants are comment-only; github/strict deploy byte-identical files
Keywords: split workflow, `scaffold_mechanical.sh:88-93`, github mode, strict mode, mode-dependent AC, shared file prose

### Fact 4 — Resume-branch completeness (see `Technical_Lead_Rules.md §2`)
Keywords: resume gap, pipeline/loop state file, instruction change vs warning, unconditional step, file-presence check

### Fact 5 — Phrase CRs and fix menus as non-exhaustive ("at minimum these, plus any site sharing the mechanism")
Keywords: change request, fix menu, enumerated list treated as exhaustive, missed call site

### Fact 7 — `gh issue list --search` is eventually-consistent and phrase-matches; prefer `--json` + exact match
Keywords: `gh issue list --json`, `--search`, eventually-consistent index, contiguous-token phrase matching, prefix-title collision, `grep -Fxq`, `--repo` explicit

### Fact 8 — Narrowing an AC is TL scope; adding a standalone AC is PO scope
Keywords: TL/PO boundary, Technical Scope section, new deliverable, refinement question, `Technical_Lead_Rules.md §2`, `Story_Standard_TL.md §7`

### Fact 9 — Round-2 scope confirmation via `git diff <round1-head> <round2-head> --stat`
Keywords: re-review, CHANGES REQUESTED, round-1 clean findings, own memory commit exclusion, "reuses existing mechanism" verification

### Fact 10 — Write the retro at end of stage work regardless of verdict
Keywords: `Retro_Rules.md`, unconditional, CHANGES REQUESTED, addenda per round

### Fact 11 — Templates and their `working/` mirrors drift silently — verify both
Keywords: `git diff --no-index`, template/mirror drift, `Project_Priming.md §15` carve-outs, `Strict_Mode_Story_Guide_template.md` no-mirror

### Fact 12 — A file-location or renumbering change must update every referrer (grep the final branch, not diff hunks)
Keywords: path-move, scaffold-location, renumbering, Nth-enumerated-item, `git show <branch>:<file>`, self-healing migration, `changes.json` entry

### Fact 17 — Hardening a principle to an absolute: check what elsewhere mandates the now-prohibited act
Keywords: never/always absolute, scoping preamble, per-role view restatement, `Story_Standard.md §9`, `§12`, unqualified prohibition

### Fact 18 — Moving content between files changes its merge/scaffold contract, not just its bytes
Keywords: replace-verbatim list, project-preserved section, Adaptive vs Mechanical tier, relocation clobbers local correction, Agent Roster precedent

## Troubleshooting Facts

No troubleshooting facts recorded yet.
