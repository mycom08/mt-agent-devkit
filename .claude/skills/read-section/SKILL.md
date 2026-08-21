---
name: read-section
description: Extract one section from a Markdown file located by a heading marker — a numbered rule citation ("<File>.md §N" → "## N", "§Na" → "### Na") or any other consistent heading prefix (e.g. "### Fact N" in a memory archive) — without reading the whole file. Use whenever a rule, instruction, or story comment points at one heading-delimited section with no extraction command attached.
---

# Read Section

Rules/instructions files number top-level sections (`## 1. Title`, `## 2. Title`, ...)
and cite them as `<File>.md §N` (`§Na` → `### Na`). Other files use a different but
equally consistent heading prefix instead — e.g. a memory archive's `### Fact N`.
`Read` has no heading-aware partial read, so extract by line number instead:

1. `grep -nE "^<marker>" <file>` — list every heading sharing the target's
   marker, with line numbers. Match the target's **numbering pattern**, not
   merely its heading level: `^## [0-9]+\.` for `§N`, `^### [0-9]+[a-z]\.`
   for `§Na`, `^### Fact ` for archive facts. A bare `^## ` also matches
   *unnumbered* same-level headings, which become false boundaries in step 2
   and truncate the section with no error — see the Example.
2. In that output, the target heading's line is `start`; the next heading's
   line is `end`. If the target is the last heading listed, there is no
   `end` — read to end of file instead.
3. Extract `start` to `end - 1` (exclusive — a plain `start,end` range leaks
   the next heading's line into the output): `sed -n "${start},$((end-1))p" <file>`,
   or `Read` with `offset=start`, `limit=$((end-start))`. Last-section case:
   `sed -n "${start},\$p" <file>`, or `Read` with `offset=start` and no `limit`.

## Example

`Agent_Common_Records.md §1` (`.claude/agents/working/rules/Agent_Common_Records.md`):
`grep -nE "^## [0-9]+\." <file>` shows `§1` (`## 1. Project Memory`) starting at
line 12 and the next numbered heading (`## 2.`) at 69 → `sed -n '12,68p' <file>`.

That file is also the worked case for step 1's warning: a bare `grep -n "^## "`
additionally matches `## Stored Facts` (45) and `## Troubleshooting Facts` (53),
both of which sit *inside* §1. Taking 45 as the boundary gives `sed -n '12,44p'`,
silently dropping §1's format block and its closing two-tier note — a short read,
not an error. Sub-headings inside a numbered section are common; assume nothing
from heading level alone.

> Line numbers above are illustrative and drift as files are edited — always run
> step 1 yourself rather than reusing them. The *shape* of the output is the point.

A memory archive's `### Fact 2` works the same way with a different marker:
`grep -n "^### Fact " <file>`, then extract as above.
