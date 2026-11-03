# ST-000303 Test Scenarios

Story: ST-000303 (PR 314, head 1db4c68). Type: behavioral. Method: read both layers at the head in a separate worktree, run all gates.

## Happy path

| ID | AC | Scenario | Expected |
|---|---|---|---|
| S1 | AC1 | Inline procedure step 1 in `orchestrator_instructions.md` and the shared template | Each skill loads immediately before its action; touchpoint table column renamed "Skills an inline activity may need"; no "Before acting, load each listed skill" |
| S2 | AC2 | `po-promote-ready` Readiness Test (internal and template) | Numbered steps: AC diffed against decided approach (TL answers, design-first approval) with re-sync; `Depends on` check; promote last. Stage 4 and next-story paths call the steps |
| S3 | AC3 | `po-comment` | "Before Each Post" numbered list with the word count as step 2 |
| S4 | AC4 | `po-write-story` Content Rules | Requirement-only AC rule stated inline |
| S5 | AC5 | `po-core`, `po-comment`, step 4 in both layers | One timing: start and end of each PO activity; Stage 4 closure skips |
| S6 | AC6 | Phase 2 shared orchestrator template, four skill templates, bundle | Same changes, target placeholders, bundle `--check` exit 0 |
| S7 | AC7 | All gates | Exit 0 |

## Error and edge cases

- Template placeholders stay `{{AGENT_DIR_PREFIX}}` in the shared template (not the internal `{RUNTIME_ROOT}`).
- Strict-mode post path present in the po-comment template (github-only wording would be a defect).
- Stale phrases absent from source and bundle assets.
- `changes.json` descriptions use the compact `[ST-NNNNNN]` clause form; CHANGELOG bullet present.
- Out-of-AC scope: "each at its point of use" added to Refine/Shared stage load lines and shared templates; consistent with AC1.
