---
name: read-section
description: Extract one section from a Markdown file located by a heading marker — a numbered rule citation ("<File>.md §N" or "§Na" → "## N." / "## Na.", both flat `##`) or any other consistent heading prefix (e.g. "### Fact N" in a memory archive) — without reading the whole file. Use whenever a rule, instruction, or story comment points at one heading-delimited section with no extraction command attached.
---

# Read Section

Run the bundled script — do not hand-compute the line range yourself:

```
.antigravity/skills/read-section/scripts/read_section.sh <file> <marker-regex> <target-regex>
```

Build the two regexes from the citation:

| Citation | marker-regex | target-regex (example) |
|---|---|---|
| `§N` or `§Na` | `^## ([0-9]+[a-z]?\.\|Version)` | `^## 11b\.` |
| `### Fact N` | `^### Fact ` | `^### Fact 2\b` |

`marker-regex` must match the **whole heading family**, never narrowed to the
target's own shape and never a bare `^## ` — either mistake silently
over-reads or under-reads the section, and the script cannot detect it
(it can only catch an ambiguous `target-regex`, which it rejects instead of
guessing).
