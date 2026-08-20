---
name: read-section
description: Extract one section from a Markdown file located by a heading marker — a numbered rule citation ("<File>.md §N" → "## N", "§Na" → "### Na") or any other consistent heading prefix (e.g. "### Fact N" in a memory archive) — without reading the whole file. Use whenever a rule, instruction, or story comment points at one heading-delimited section with no extraction command attached.
---

# Read Section

Rules/instructions files number top-level sections (`## 1. Title`, `## 2. Title`, ...)
and cite them as `<File>.md §N` (`§Na` → `### Na`). Other files use a different but
equally consistent heading prefix instead — e.g. a memory archive's `### Fact N`.
`Read` has no heading-aware partial read, so extract by line number instead:

1. `grep -n "^<marker>" <file>` — list every heading sharing the target's
   marker, with line numbers (`^## ` for `§N`, `^### ` for `§Na`,
   `^### Fact ` for archive facts, etc).
2. In that output, the target heading's line is `start`; the next heading's
   line is `end`. If the target is the last heading listed, there is no
   `end` — read to end of file instead.
3. Extract `start` to `end - 1` (exclusive — a plain `start,end` range leaks
   the next heading's line into the output): `sed -n "${start},$((end-1))p" <file>`,
   or `Read` with `offset=start`, `limit=$((end-start))`. Last-section case:
   `sed -n "${start},\$p" <file>`, or `Read` with `offset=start` and no `limit`.

## Example

`Agent_Common.md §5` (`.claude/agents/working/rules/Agent_Common.md`):
`grep -n "^## " <file>` shows `§5` (`## 5. Working Record`) starting at line
106 and the next heading at 134 → `sed -n '106,133p' <file>`.

A memory archive's `### Fact 2` works the same way with a different marker:
`grep -n "^### Fact " <file>`, then extract as above.
