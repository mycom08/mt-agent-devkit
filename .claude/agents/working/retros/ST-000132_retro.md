# Retrospective — ST-000132
**Date:** 2026-08-25
**Story:** Carry Agent_Common bootstrap/on-demand split into templates/ (Claude + Antigravity)

## Implementer — Developer
### Impediments & Unclear Points
- `[instruction]` The story pointed at two "your model to copy from" reference files but the split's numbering scheme (which sections stay bootstrap vs move on-demand, and whether the historical numbering gap is preserved) had to be reverse-engineered from a `git show` of the reference commit rather than being stated directly — cost a full research pass before any file could be written.
- `[workflow]` Validating a bare `§N` citation against real headings has no carve-out for a file whose own prose *describes* an intentional numbering gap (e.g. "section 4 is skipped") — the validator's section-ref check treats any `§4`-shaped substring as a citation needing a real heading 4, so the gap had to be described in prose without the `§` glyph. Worth a documented convention (or a validator carve-out) so the next split doesn't rediscover this by trial and error.
- `[context]` `changes.json` only ever tracks `.claude/agents/templates/...` paths — never `.antigravity/...` — so the antigravity mirror's new/split files have no manifest coverage today; that's a pre-existing gap in how `sync devkit` would serve antigravity target projects, not something this story introduced, but it means the antigravity template split has no automated integrity check the way the Claude side does via `validate_templates.py`.

### Process Suggestions
- `[workflow]` A "splitting a shared rules file" checklist (rules citations, instructions citations, workflow enumerations, scaffold script arrays, `validate_templates.py`'s `SECTION_REF_ALIAS`/allowlists, `changes.json`) would have turned this story's multi-hour discovery pass into a lookup. This story's own diff is a reasonable first draft of that checklist.
- `[instruction]` Confirm the dev branch is created **before** the first file write, not just before the first commit — the Pre-Work Checklist enforces "branch off main" but nothing stops an agent from writing files first and discovering the wrong base branch only at commit time.

### What Worked Well
- `python scripts/validate_templates.py` caught the numbering-gap false-positive immediately and precisely (file:line), turning a subtle Markdown-prose issue into a two-line fix.
- Reading the reference commit (`git show e691bd9 --stat` + diffing a few citing files) gave an exact, unambiguous model for the split boundary and section renumbering — far more reliable than re-deriving the boundary from first principles.
- `git stash push -u` / branch-recreate-off-main / `git stash pop` cleanly recovered from having started work on the wrong base branch, with zero lost work.

## Reviewer — Technical Lead
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## QA
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Product Owner
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Orchestrator
### Observations
*(pending)*
