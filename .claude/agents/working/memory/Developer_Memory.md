# Developer Memory

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

## Troubleshooting Facts

### Fix 1 — Working-record refs fail CI reference-integrity
- **Problem:** Reference-integrity check fails in CI but passes locally.
- **Symptoms:** `[ERROR]` on `.claude/agents/working-record/…` paths cited in instruction templates.
- **Root Cause:** Those files are gitignored in the devkit, so the CI runner never checks them out and Root-2 resolution fails.
- **Fix:** Add `.claude/agents/working-record/` to `RUNTIME_PATH_PREFIXES` in `validate_templates.py`.
- **Prevention:** Any path that is gitignored or generated at runtime belongs in `RUNTIME_PATH_PREFIXES` before it is cited in a template. Not reproducible locally — only surfaces on a real CI run.
