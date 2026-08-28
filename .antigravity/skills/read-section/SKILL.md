---
name: read-section
description: Extract one section from a Markdown file located by a heading marker — a numbered rule citation ("<File>.md §N" or "§Na" → "## N." / "## Na.", both flat `##`) or any other consistent heading prefix (e.g. "### Fact N" in a memory archive) — without reading the whole file. Use whenever a rule, instruction, or story comment points at one heading-delimited section with no extraction command attached.
---

# Read Section

Rules/instructions/context files number **every** cited section flat at `##`
(`## 1. Title`, `## 2. Title`, `## 11a. Title`, ...) and cite them as
`<File>.md §N` / `§Na`. `###` is reserved for *unnumbered* prose sub-headings,
which are never citation targets. Other files use a different but equally
consistent heading prefix instead — e.g. a memory archive's `### Fact N`.
`Read` has no heading-aware partial read, so extract by line number instead:

1. `grep -nE "^<marker>" <file>` — list every heading that can bound the
   target, with line numbers. Use **one marker for the whole family**:

   | Citation | Marker |
   |---|---|
   | `§N` or `§Na` in a rules/instructions/context file | `^## ([0-9]+[a-z]?\.\|Version)` |
   | `### Fact N` in a memory archive | `^### Fact ` |

   Match the **numbering pattern**, never merely the heading level. A bare
   `^## ` also matches *unnumbered* same-level headings, which become false
   boundaries in step 2 and truncate the section with no error — see the
   Example. The `|Version` alternative catches the `## Version` footer that
   terminates the last numbered section in most rules files; it is a harmless
   no-op in the files that have no such footer.

   **Do not narrow the marker to the target's own shape.** Grepping
   `^## [0-9]+[a-z]\.` for a `§Na` citation matches only the sub-numbered
   headings, so a file with exactly one of them returns a single hit, step 2
   falls into its "last heading" branch, and the extraction runs to EOF —
   swallowing every following section. One family, one marker.

2. In that output, the target heading's line is `start`; the **next line in
   the grep output** is `end` — regardless of whether it is `§N`, `§Na`, or
   `## Version`. If the target is the last heading listed, there is no `end`
   — read to end of file instead.
3. Extract `start` to `end - 1` (exclusive — a plain `start,end` range leaks
   the next heading's line into the output): `sed -n "${start},$((end-1))p" <file>`,
   or `Read` with `offset=start`, `limit=$((end-start))`. Last-section case:
   `sed -n "${start},\$p" <file>`, or `Read` with `offset=start` and no `limit`.

## Example

`Product_Owner_Rules.md §11b` (`.antigravity/agents/working/rules/Product_Owner_Rules.md`):
`grep -nE "^## ([0-9]+[a-z]?\.|Version)" <file>` lists §1 (8), §2 (33), ... §11 (129),
§11a (142), **§11b (148)**, §12 (154), `## Version` (160). Target `start=148`, next
heading `end=154` → `sed -n '148,153p' <file>`.

That file is also the worked case for step 1's warning. Narrowing the marker to
the target's own shape — `grep -nE "^## [0-9]+[a-z]\."` — matches only §11a and
§11b. §11b is the last of those two, so step 2 takes its "last heading" branch
and produces `sed -n '148,$p'`: lines 148–164, swallowing §12 and the Version
footer. A silent over-read, no error. The same class of failure in the other
direction: a bare `^## ` on a file whose numbered section contains unnumbered
`##` sub-headings takes the first sub-heading as the boundary and returns a
**short** read. Assume nothing from heading level alone — match the numbering
pattern, and match the whole family.

> Line numbers above are illustrative and drift as files are edited — always run
> step 1 yourself rather than reusing them. The *shape* of the output is the point.

A memory archive's `### Fact 2` works the same way with a different marker:
`grep -n "^### Fact " <file>`, then extract as above.
