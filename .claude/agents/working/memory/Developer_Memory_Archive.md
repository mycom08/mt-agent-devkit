# Developer Memory Archive

> Full-text archive for `Developer_Memory.md`'s Keyword Index tier — devkit-internal two-tier memory pilot (`Agent_Common.md §12`, issue #118). Not read every spawn; open only when an index line's keywords match your current task, using the `read-section` skill (`.claude/skills/read-section/`, heading marker `^### Fact `) — never a full-file read.

## Stored Facts

### Fact 1
- **Rule:** Adding an Nth item to any enumerated corpus set (role, rules file, split workflow) ripples into hardcoded counts and lists that a story's AC never names. Grep an existing member of the set across `.claude/agents/` *before* starting — a `{placeholder}` scan will not catch count prose. Known ripple sites: `scaffold_mechanical.sh` (role loops, `SPLIT_WORKFLOWS` array), `Init_Project_Workflow.md`, `Update_Project_Workflow.md`, `Build_Software_Workflow.md`, and `Sync_Devkit_Workflow_template.md` **plus its working mirror** — the last three each carry *two* distinct lists ("Applies to" and "Expected files — …"), and updating only one is the standard miss.
- **Applies when:** any story that adds a role, a rules template, or a split workflow file.
- **Evidence:** ST-000021 (6th role, missed 2 sites), ST-000023 (19th rules file), ST-000028 (Nth split workflow), ST-000037 (20th rules file — AC named only 4 of the 6 real ripple sites; `scaffold_mechanical.sh`'s `VERBATIM_RULES` and `Build_Software_Workflow.md`'s 2 count mentions caught from this fact alone). Role case now also documented in `Project_Priming.md §15a`.
- **Expires when:** the counts become generated rather than hardcoded.

### Fact 2
- **Rule:** Never let a file under `.claude/agents/templates/` reference a devkit-only path as an executable step. Target projects have no `templates/` dir and never receive devkit-internal workflows, so `bash .claude/agents/working/scripts/…` or "follow `Build_Software_Workflow.md`'s Stage N" dead-ends on first real use. `validate_templates.py` cannot catch this — it resolves references inside the devkit repo, where those paths exist. Fix pattern: reuse `Sync_Devkit_Workflow_template.md`'s `{DEVKIT_SOURCE_URL}` fetch (WebFetch + curl fallback). Restating a *content list* is fine; pointing at devkit-internal *automation* is not.
- **Applies when:** writing or editing anything under `templates/`.
- **Evidence:** ST-000028 PR #87 round-1 CHANGES REQUESTED.
- **Expires when:** the validator gains deployment-scoped reference resolution.

### Fact 3
- **Rule:** `scaffold_mechanical.sh`'s awk merge keeps only non-comment lines after line 1 of a thin mode variant. Every current thin variant is comment-only, so **github and strict deploy byte-identical files**. Mode differentiation for a split workflow must live inline in the *shared* file's "**GitHub mode:** / **Strict mode:**" prose.
- **Applies when:** an AC asks for mode-specific behavior in a split workflow.
- **Evidence:** ST-000028, verified by a scratch dry-run of the script.
- **Expires when:** thin variants gain real content or the merge stops stripping.

### Fact 4
- **Rule:** Every value a resume-governing state field can hold needs its own explicit branch, decided when the state file is designed — not just the "still working" value. A file left at a terminal value (`ended`, `done`) with no matching branch falls through to the active branch and silently re-enters the loop.
- **Applies when:** designing or editing any pipeline/loop state file.
- **Evidence:** ST-000028 CR-3 — `refine_prototype_state.md` branched only on empty-path and `active`.
- **Expires when:** never.

### Fact 5
- **Rule:** `scripts/validate_templates.py` is the Layer-1 corpus invariant checker (6 invariants, cross-platform Python 3). `RETIRED_TRIGGERS=[]` by design; use `--test-retired-trigger <token>` for fixture testing. `_is_shared`/`_is_thin_variant` check `path.parts`, not TEMPLATES_DIR-relative paths, so fixtures work outside `templates/`. `RUNTIME_PATH_PREFIXES` covers `.claude/agents/working-record/`, `tmp/`, `docs/`, `retros/`.
- **Applies when:** changing the validator or debugging a reference-integrity failure.
- **Evidence:** ST-000016.
- **Expires when:** the invariant set or path handling changes.

### Fact 6
- **Rule:** `changes.json` uses **newest-first (descending)** key order — add a new entry at the **top**, immediately after the opening `{`. The validator checks semver parseability only, never ordering direction, so a misplaced entry passes CI.
- **Applies when:** adding a version entry.
- **Evidence:** verified against `changes.json` — first key `0.1.40`, last `0.0.1`; `Project_Priming.md §15` states the same.
- **Expires when:** the convention flips.

### Fact 7
- **Rule:** `.github/workflows/validate-templates.yml` triggers on `push: branches: [ci-validation]` **and** `pull_request: paths: [templates/**, workflows/**]`. Per `CICD_Validation_Guide`, a workflow needs `on.push.branches: [ci-validation]` or no branch filter — a PR-only workflow must have the push trigger added permanently to satisfy the ci-validation gate.
- **Applies when:** adding or editing a GitHub Actions workflow in this repo.
- **Evidence:** ST-000016.
- **Expires when:** the CI gate design changes.

### Fact 8
- **Rule:** An AC that schedules a new once-per-sprint orchestrator step without a file pointer ("alongside the existing sprint-end cleanup") means `Sprint_Workflow_Shared_template.md`'s (+ working mirror) "Sprint end" Pipeline Rule sequence: Batch Retro Review → Sprint Consolidated Summary → [Release Decision, template-only] → Devkit Contribution → Cleanup. It is the only home for a once-per-sprint, orchestrator-direct, no-spawn step.
- **Applies when:** implementing a vague scheduling AC.
- **Evidence:** ST-000033 — added "Memory Pruning" there, referenced from `Retro_Rules.md`.
- **Expires when:** the "Sprint end" sequence is restructured or renamed.

### Fact 9
- **Rule:** A rule that lives in `Story_Standard_template.md` is restated in **six** places, not five: the four per-role views (`Story_Standard_Dev/PO/QA/TL_template.md`) *and* `Strict_Mode_Story_Guide_template.md`, which restates the same standard for strict mode's local comment entries. The strict-mode guide is the one an AC's file list reliably omits, and it has no working mirror (`Project_Priming.md §15` carve-out names it). Before editing any `Story_Standard` rule, grep a distinctive phrase from it (e.g. `150–200`) across `.claude/agents/` rather than trusting the AC — this is restatement drift, a different mechanism from Fact 1's count drift.
- **Applies when:** editing any rule in `Story_Standard_template.md` that the role views or strict-mode guide summarise.
- **Evidence:** ST-000038 — AC6 named 4 views; grep found the 5th restatement site.
- **Expires when:** the views stop restating and become pure pointers.

### Fact 10
- **Rule:** Before strengthening a principle into an absolute ("never", "always", "must not") in a shared standard, grep the **same file's gate checklists** for a rule that *mandates* the thing you are about to forbid. A principle tolerates a specific override; an absolute does not. When the two collide, fix it with a **named** carve-out ("gate-mandated CI evidence") rather than a bare scope qualifier — the name is what the per-role views can restate without re-deriving the reasoning, and it survives the next edit to either side.
- **Applies when:** promoting any soft guidance to a hard prohibition, especially in `Story_Standard_template.md` where §9 (writing rules) and §12 (gate checklists) can each mandate opposite things.
- **Evidence:** ST-000038 PR #108 CR-1 — §9 rule 4 "never paste command output" vs §12 Reviewer gate "paste the literal `gh pr checks` output … approval comments without this evidence are incomplete".
- **Expires when:** §9 and §12 stop being separately authored.

### Fact 11
- **Rule:** Splitting a shared devkit config file (e.g. `CLAUDE.md`) ripples three ways beyond the split itself, none caught by the validator: (1) a sync/update workflow's "replace verbatim"/"expected files" list is a second restatement of the file's heading structure that can already be stale — verify each entry against a real heading, don't trust it. (2) **Merge-tier check before moving any section**: if it's project-mutable (edited/preserved locally — role paths, a trimmed roster), moving it into an always-overwritten mechanical file destroys that preservation; grep for workflows editing it in place, not just subagent read-need. (3) A workflow that scaffolds a new repo by **remote fetch** (`{DEVKIT_SOURCE_URL}`, e.g. `Refine_Prototype_Workflow`) cannot use the local `scaffold_mechanical.sh` — a new mechanical-tier file must be added to its own fetch list separately, or the fetched repo silently lacks it. This generalizes to a brand-new mechanical-tier file too (not just a split): the same 4 sites need it — `scaffold_mechanical.sh`, the sync workflow (target-side), the update-project workflow (devkit-side), and the remote-fetch Universal set — plus `Init_Project_Workflow.md`'s own mechanical-tier enumeration (a 5th site, prose-only, not functionally required but left stale otherwise). A file living outside `.claude/agents/` entirely (e.g. a Claude Code skill at `.claude/skills/`) still ripples through all 5 — just as a sibling directory of `.claude/agents/`, not nested under it.
- **Applies when:** restructuring any file that a sync/update-style workflow merges section-by-section, or adding a new mechanical-tier file to the devkit's scaffold set.
- **Evidence:** ST-000043 R1 — stale heading list found via an issue comment. R2 TL review — CR-2: Agent Roster moved into the new mechanical file, breaking the lean-prototype-roster override and flat→subdir path repair (both edit CLAUDE.md's Roster in place); CR-1: `Refine_Prototype_Workflow_Shared_template.md`'s remote-fetch list missed the new file (same class as ST-000037 CR-1, 5th consecutive miss). ST-000044 — new `.claude/skills/read-section/` file threaded through all 5 sites cleanly on first pass using this fact.
- **Expires when:** the validator gains prose-heading + merge-tier-contract checking, or the scaffold-file lists become generated rather than hand-enumerated.

### Fact 12
- **Rule:** `validate_templates.py`'s placeholder check (Invariant #2) scans inline single-backtick code spans, not just fenced code blocks — an ALL-CAPS shell variable reference like `` `${START}` `` in prose trips the "possibly-malformed single-brace placeholder" error exactly like a real `{TOKEN}` would. Use lowercase shell variable names (`${start}`) in inline code/prose to avoid false positives; the check only flags `[A-Z][A-Z0-9_]+`.
- **Applies when:** writing a template file's prose that shows shell variable syntax (`${VAR}`, `{VAR}`) outside a fenced block.
- **Evidence:** ST-000044 — `read-section` skill doc, `{START}`/`{END}` in inline code at 2 lines, caught by CI-equivalent local run before PR.
- **Expires when:** the check is scoped to fenced blocks only, or gains a backtick-span exclusion.
