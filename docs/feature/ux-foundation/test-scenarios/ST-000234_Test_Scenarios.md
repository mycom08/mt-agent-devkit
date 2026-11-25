# ST-000234 Test Scenarios — UX Foundation Templates

Scope: PR 358, head `efb30b28a062cfd0290319184d06e0ec1435b751`, github mode devkit. Type: behavioral.

| ID | AC | Scenario | Type | Expected |
|---|---|---|---|---|
| S1 | 1 | Read the standard template against each baseline item | Happy | Validation and inline errors, four states, overflow with long translations, breakpoints, accessibility (labels, focus, keyboard, contrast), motion, consistency, floating elements all present; stack-agnostic; applies to every screen |
| S2 | 2 | Compare the floating elements section with the addendum | Happy | Portalled page-level rendering, popover for click-to-open, solid surface with library tokens, visible/opaque/on-top check in a card, near edges, over next section |
| S3 | 3 | Look for fill-in sections | Happy | Breakpoints, component library, tone and terminology |
| S4 | 4 | Look for design doc sections | Happy | Screens, flows, layouts, shared components, states per screen, standard reference, deviations with reason, promotion candidates |
| S5 | 5, 6 | Read UI/UX rules section; diff workflows | Happy | Both doc types defined, deviation outcomes, promotion with TL and PO acceptance; no workflow file changed |
| S6 | 7 | Read both template headers | Happy | One line with doc type and promotion rule |
| S7 | 8, 9 | Fresh init into scratch targets (providers x modes) | Happy | Both templates byte-equal to bundle assets; index row `not registered` |
| S8 | 9 | Register a standard, edit the index, update and sync from a pre-change install | Edge | Standard and index byte-identical; templates installed |
| S9 | 9 | Re-run update; root (non-repo) profile | Edge | Idempotent; no UX templates in a project-root profile |
| S10 | 9 | Hand-edit an installed blank template, then update | Error | Managed-file drift handled without silent loss |
| S11 | 3, 4 | Unresolved `{{...}}` tokens in installed files | Edge | None; fill-in placeholders are single-brace |
| S12 | 10 | `build_bundle.py --check`, bundle tests, harness gates, `run.sh` | Happy | All exit 0 |
| S13 | 10 | `changes.json` and `CHANGELOG.md` | Happy | Entries in the current unreleased version; bridges unchanged |
