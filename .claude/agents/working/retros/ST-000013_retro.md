# Retrospective — ST-000013
**Date:** 2026-07-01
**Story:** Add strict-mode gating to shared rules & priming (RF-003/005/006)

## Implementer — Developer
### Impediments & Unclear Points
- `[context]` The dual-update rule requires updating both template and working mirror, but for this story the working mirrors were intentionally diverged from the templates (devkit GitHub-mode-only vs. target-project generic). No guidance existed on what "equivalent update" means when the mirror was deliberately rewritten for a different context. Required a judgement call: skip mirror update and document as intentional divergence.
- `[context]` The `Strict_Mode_Story_Guide.md` working mirror does not exist under `working/rules/` — the devkit operates in GitHub mode only and never installs that guide for its own agents. The story mapped a mirror relationship that doesn't exist in practice.

### Process Suggestions
- `[instruction]` The dual-update rule (CLAUDE.md §15) should add a carve-out: "If the working mirror was intentionally rewritten for a different operational context (e.g., devkit-specific vs. target-project-generic), document the divergence as intentional rather than flagging it as drift requiring a fix."
- `[instruction]` When a template has no working mirror (file absent rather than diverged), the dual-update check should explicitly say "no working mirror exists — note the absence and proceed without creating one if the devkit does not use that mode."

### What Worked Well
- The existing mode-gating precedent in `Developer_Rules_template.md §2` (bullet points with `**GitHub mode:**` / `**Strict mode:**` labels) gave a clear, unambiguous style to follow — no guessing needed.
- `validate_templates.py` ran cleanly (exit 0) on the first pass, confirming the template edits didn't break any invariants.
- Reading all six files before writing any change (templates + working mirrors + Strict_Mode_Story_Guide) surfaced the drift situation upfront, avoiding surprises mid-implementation.

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
