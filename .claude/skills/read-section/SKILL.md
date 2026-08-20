---
name: read-section
description: Extract one section from a Markdown file located by a heading marker — a numbered rule/instruction citation ("<File>.md §N" → "## N", or "§Na" → "### Na"), or any other consistently-formatted heading prefix (e.g. "### Fact N" entries in an archive file) — without reading the whole file. Use this whenever a rule, instruction, story comment, or index entry points at one heading-delimited section with no attached extraction command.
---

# Read Section

Every rules/instructions file in this project numbers its top-level sections
(`## 1. Title`, `## 2. Title`, ...) and cites them elsewhere as `<File>.md §N`.
Other files use a different but equally consistent heading prefix instead of
numbering — a memory archive's `### Fact N` entries, for example. `Read` has
no heading-aware partial read — only a full read or a line `offset`/`limit`
— so a bare pointer to one heading gives no way to compute a range on its
own. This skill is that recipe: two small commands, no whole-file read.

## Recipe

1. **List every heading that shares the target's marker, with line numbers.**
   - Top-level section (`§N`, e.g. `§5`): `grep -n "^## " <file>`
   - Lettered subsection (`§Na`, e.g. `§15a`): `grep -n "^### " <file>`
   - Any other consistent prefix (e.g. memory-archive facts): `grep -n "^### Fact " <file>`
2. **Find the boundary.** In that output, the line for the target heading is
   `start`. The next heading line *after* it is `end`. If the target is the
   last heading listed, there is no `end` — read to end of file instead.
3. **Extract `start` through `end - 1`** (excludes the next heading line —
   see "Why not a fixed one-liner" below for why the boundary must be
   exclusive):
   - `sed -n "${start},$((end-1))p" <file>`
   - or with the `Read` tool: `offset=start`, `limit=$((end-start))`
   - last-section case (no `end`): `sed -n "${start},\$p" <file>`, or `Read`
     with `offset=start` and no `limit`.

## Example — numbered rule citation

Citation: `Agent_Common.md §5` (this project's working copy lives at
`.claude/agents/working/rules/Agent_Common.md`).

```bash
grep -n "^## " .claude/agents/working/rules/Agent_Common.md
```
```
8:## 1. Pre-Work Sequence
26:## 2. Project Memory
81:## 3. Troubleshooting Protocol
95:## 4. End-of-Work Retrospective
106:## 5. Working Record
134:## 6. Stage-Transition Commit (implementer & reviewer roles)
```

`§5` starts at line 106; the next heading is at 134 → extract 106–133:

```bash
sed -n '106,133p' .claude/agents/working/rules/Agent_Common.md
```

## Example — non-numbered heading prefix

A two-tier memory archive's keyword index points at a fact by number, not by
`§N` — the same recipe applies with a different grep pattern:

```bash
grep -n "^### Fact " .claude/agents/working/memory/Technical_Lead_Memory_Archive.md
```
```
7:### Fact 1
13:### Fact 2
19:### Fact 3
25:### Fact 4
```

`Fact 2` starts at line 13; the next heading is at 19 → extract 13–18.

## Why not a fixed one-liner

A hand-rolled `sed -n '/^## N\./,/^## N+1\./p'` form needs the caller to
already know `N+1`, and its range is inclusive at *both* ends — so it always
prints the next section's heading line too, one line past the intended
boundary. That bug is easy to miss (the leaked line is just a heading, no
body) and easy to reintroduce every time the pattern is hand-rolled again at
a new citation site. The two-step recipe above only needs the target's own
number; it derives the boundary from the file itself and is exact.
