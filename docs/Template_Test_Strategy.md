# Template Test Strategy

**Scope:** mt-agent-devkit — devkit-internal guide  
**Audience:** Devkit maintainers and AI agents implementing template stories  
**Layer-1 tool:** `scripts/validate_templates.py`  
**CI gate:** `.github/workflows/validate-templates.yml`

---

## 1. Purpose and Scope

Template and instruction files in this devkit are *executable specifications* —
the markdown that an LLM agent reads and runs. A regression in a template is a
workflow bug: agents act on stale, contradictory, or broken instructions.
Because there is no compiled artifact and no conventional unit-test suite,
template correctness requires a dedicated validation strategy.

This guide defines:
- The 3-layer model (Layer-1 through Layer-3) for testing template files.
- The 6 Layer-1 corpus invariants enforced by `validate_templates.py`.
- Risk tiers A/B/C for behavioral testing priority.
- A coverage model linking invariants to files.
- The AC-as-oracle pattern for change-scoped doc stories.
- How this relates to `Project_Priming §8` pre-PR gates and the `refactor templates` workflow.

**What Layer-1 gates and what it deliberately does not:**
- Gates: deterministic, corpus-wide invariants that can be checked mechanically
  on every PR that touches templates or workflows.
- Does NOT gate: @-mention style, bare-# reference style, or any heuristic check
  that requires an unbounded allowlist to avoid false positives. Those belong to
  the `refactor templates` exploratory scan.

---

## 2. Templates as Executable Specifications

| Analogy | Template Layer | What breaks |
|---|---|---|
| Source code | Instruction/rules markdown | Wrong agent behavior |
| Library | Shared workflow blocks | Drift across modes |
| Config | Placeholder substitution | Broken init/sync |

Unlike source code, templates cannot be compiled or linked. Testing must be:
- **Deterministic (Layer-1):** regex-level checks that never produce false
  positives given a correctly maintained allowlist.
- **Deployment (Layer-2):** run `init project` and `update project` in a scratch
  directory and assert the expected file set, placeholder substitution, and
  idempotency. *Deferred — defined here, implemented as a follow-up story.*
- **Behavioral (Layer-3):** agent-in-the-loop tests on the highest-risk files.
  *Deferred — defined here, implemented as a follow-up story.*

---

## 3. The 3-Layer Model

| Layer | Analogy | What it catches | Current automation |
|---|---|---|---|
| Layer-1 static | Unit test | Broken refs, malformed placeholders, shared-block drift, retired triggers, manifest gaps, Markdown syntax | Automated (`validate_templates.py` + CI gate) |
| Layer-2 deployment | Integration test | Wrong file count after init/update, placeholder substitution failures, update idempotency, mode bifurcation correctness | Defined here; not yet automated |
| Layer-3 behavioral | E2E / agent-in-the-loop | Agent misreads AC, follows wrong rule, produces wrong output | Defined here; not yet automated |

### Layer-2 roadmap (deferred)

Smoke-test script `init project` and `update project` into a temporary scratch
directory for both github and strict modes, asserting:
- Expected file set and count (per `Init_Project_Workflow.md`).
- All `{{PLACEHOLDER}}` tokens substituted (no raw double-brace in output).
- `update project` idempotent: running twice produces identical output.
- Mode-specific files present (e.g., `Strict_Mode_Story_Guide.md` in strict mode only).

Catches the RF-016/017 install class (init writes wrong path or wrong content).

### Layer-3 roadmap (deferred)

Agent-in-the-loop harness for Tier-A files (see §5). Spawns a test agent,
gives it a synthetic story, and asserts the agent follows the correct procedure.
Requires a test harness with observable outputs.

---

## 4. Layer-1 Corpus Invariants

**Scan scope:** `.claude/agents/templates/**/*.md` and `.claude/agents/workflows/**/*.md`.

**Output contract:** one `[ERROR] file:line -- <issue>` line per hard violation.
Known-issue notes print as `[KNOWN_ISSUE]` and do not affect exit code.
Exit non-zero on any `[ERROR]`.

**Cross-cutting rule:** The validator parses each file into fenced-code regions
first (tracking ` ``` ` and `~~~` fences). Invariants #2 and #4 skip fenced
regions so code examples are not falsely flagged.

### #1 Reference integrity

**(A) File-path refs.** Candidates matching `\.claude/agents/[\w./ -]+\.md`.
Discard candidates containing `<`, `>`, `*`, `{`, `}`, `XXXXX`, or
`ST-XXXXXX` (example/placeholder markers). Three resolution roots (in order):
1. Repo root verbatim.
2. Devkit working mirror: `.claude/agents/<rest>` → `.claude/agents/working/<rest>`.
3. Template source: map the deployed filename stem to `<stem>_template.md`
   anywhere under `.claude/agents/templates/`.

Paths under `.claude/agents/tmp/`, `.claude/agents/docs/`, and
`.claude/agents/retros/` are runtime-generated and skipped.

Known-wrong references (tracked for `refactor templates`) are printed as
`[KNOWN_ISSUE]` and do not exit non-zero. See `KNOWN_ISSUE_REFS` in the script.

**(B) Section refs.** Pattern `§N` where N is a digit sequence.
- **Bare `§N`** (no file name on the same reference): only checked if the
  current file uses numbered-section style (`## N.` headings). If the file has
  no numbered sections, bare §N references are skipped (they are prose notation
  in non-numbered files).
- **Qualified `<Name> §N`** or **`<Name>.md §N`**: look up `<Name>` (the
  stem) in `SECTION_REF_ALIAS`; if mapped, verify heading N exists in that
  file; if not mapped, skip (prevents false positives on prose).

### #2 Placeholder well-formedness

Legal grammar for double-brace: `{{[A-Z][A-Z0-9_]*}}`.

The validator maintains `KNOWN_DOUBLE_BRACE_TOKENS` (all names currently used)
and `KNOWN_SINGLE_BRACE_TOKENS` (legitimate single-brace ALL-CAPS tokens such
as `{DEVKIT_SOURCE_URL}` and `{CURRENT_VERSION}` used in workflow instructions).

Checks (in fenced regions skipped for #2):
- **a.** Unbalanced `{{` / `}}` on a line.
- **b.** Malformed inner token (not `[A-Z][A-Z0-9_]*`).
- **c.** Triple-brace run `{{{` or `}}}`.
- **d.** Well-formed `{{TOKEN}}` not in the registry → `unknown placeholder`.
- **e.** All-caps single-brace `{TOKEN}` not in the single-brace allowlist.
  (Mixed-case and lowercase single-brace tokens like `{github-org}` and
  `{Language}` are not checked — they are prose notation in workflow files.)

To add a new placeholder: add it to `KNOWN_DOUBLE_BRACE_TOKENS` and document
the init/sync substitution behavior in the relevant workflow file.

### #3 Shared-block include integrity

Pointer paths are relative to `.claude/agents/` (e.g.
`templates/shared/workflows/X_Shared_template.md`).

The validator detects shared files (any file under a directory named `shared`)
and thin variant files (under `github` or `strict`).

- **a. Balanced markers** — within each shared file, `<!-- SHARED-START -->`
  count equals `<!-- SHARED-END -->` count, alternating START-before-END
  (stack check). Violation at the offending marker line.
- **b. Pointer resolves** — every thin variant file with
  `<!-- Shared logic: <path> -->` → `<path>` (from `.claude/agents/`) exists.
- **c. Bidirectional consistency** — each shared file's `<!-- Included by: ... -->`
  header lists files that (i) exist and (ii) carry a `Shared logic:` pointer
  back to this shared file; and every thin variant pointing to a shared file
  appears in that file's `Included by:` list.
- **d. No inline duplication** — thin variants must not contain `SHARED-START`/
  `SHARED-END` (shared content belongs only in `shared/**`).

### #4 Retired-trigger check

`RETIRED_TRIGGERS` is an explicit constant (currently **empty**). Populate it
only when a trigger command is confirmed retired. Occurrences of any string in
the list are flagged outside fenced regions.

`update agents` is a **live** target-project operation — it must **never** be
seeded into `RETIRED_TRIGGERS` for the templates scope.

**Fixture testing:** because the seed is empty in production, `run.sh` uses
`--test-retired-trigger TEST_RETIRED_TRIGGER_DO_NOT_USE` to exercise the check
against `fixtures/bad/inv4_bad_trigger.md`. This proves the check fires without
contaminating the real constant.

### #5 Manifest integrity (git-free)

Checks `changes.json` (the version-tracking manifest for target-project sync):
- Every path in every `new`/`modified` array exists on disk, unless listed in
  `ALLOWLIST_REMOVED_PATHS` (paths legitimately deleted/moved in ST-000006 when
  templates were split into the github/strict/shared layout).
- Every file under `.claude/agents/templates/**` appears in at least one
  `changes.json` entry, unless listed in `ALLOWLIST_UNTRACKED_TEMPLATES` (files
  that predate changes.json tracking — see that constant for the list).
- Every version key parses as valid semver (`N.N.N`).

Note: `changes.json` uses newest-first (descending) key order by convention.
The validator checks semver parseability but not ordering direction.

**Backlog item:** Add a `v0.0.0` baseline entry covering all files in
`ALLOWLIST_UNTRACKED_TEMPLATES` so the allowlist can eventually be emptied.

### #6 Markdown well-formedness (regex, not full CommonMark)

- **Heading continuity** — when heading level increases, it must not jump by
  more than 1 (`#` → `###` skipping `##` is a violation). Decreases are fine.
  Skip headings inside fenced regions.
- **Balanced code fences** — every opened fence must be closed. Violation
  points to the unclosed opening line.
- **Table pipe-count consistency** — within a contiguous table block (header +
  `---` separator + rows), each data row's unescaped `|` count equals the
  header's. Inline code spans are stripped before counting.

---

## 5. Risk Tiers A/B/C

Behavioral-test priority for Layer-3 (when the harness is built):

### Tier A — Behavioral test on change (highest risk)

Changes to these files affect agent decision-making in every sprint:

| File | Why high risk |
|---|---|
| `rules/Story_Standard_template.md` | Source of truth for story lifecycle; all agents reference it |
| `rules/Story_Standard_*_template.md` (5 role variants) | Role-specific view of the story lifecycle |
| `rules/Agent_Common_template.md` | Pre-work sequence, memory format, retro format — read by all agents |
| `shared/workflows/Shared_Pipeline_Stages_Shared_template.md` | Pipeline stage logic — governs sprint execution |
| `rules/Developer_Rules_template.md` | Dev implementation gate rules |
| `rules/Technical_Lead_Rules_template.md` | TL review and design rules |
| `rules/QA_Rules_template.md` | QA acceptance criteria rules |
| `rules/Product_Owner_Rules_template.md` | PO story closure and AC rules |
| `rules/Business_Analyst_Rules_template.md` | BA scope and requirements rules |

### Tier B — Walkthrough review on change (medium risk)

Changes to these files affect project setup or agent context:

| File | Why medium risk |
|---|---|
| `instructions/*_instructions_template.md` (5 files) | Agent identity and pre-work checklist |
| `context/Project_Priming_template.md` | Project architecture and working directories |
| `context/Document_Index_template.md` | Document navigation reference |
| `rules/Strict_Mode_Story_Guide_template.md` | Strict-mode operation substitutions |
| `rules/CICD_Validation_Guide_template.md` | CI workflow validation procedure |
| `rules/Blocked_Request_template.md` | Blocked story escalation procedure |
| `rules/Retro_Rules_template.md` | Retrospective format |
| `rules/Clean_Code_Rules_template.md` | Code quality standards |

### Tier C — Static validation only (lowest risk)

These files do not directly drive agent decisions in the sprint pipeline:

| Files |
|---|
| `wiki/*.md` templates (4 files) |
| `workflows/Workflow_Guide_template.md` |
| `workflows/Build_Software_Project_Workflow_template.md` |
| `workflows/Sync_Devkit_Workflow_template.md` |

---

## 6. Coverage Model

Layer-1 invariants apply corpus-wide (all 55+ template files and 5 workflow
files). Coverage is tracked at two levels:

**Invariant × file:** every file is subject to invariants #1, #2, #4, #6.
Invariant #3 applies only to shared files and thin variant pairs. Invariant #5
is a global check (not per-file).

**Behavioral walkthroughs:** defined by tier. Tier-A files receive a walkthrough
review on every change PR before TL approval. The reviewer verifies:
- AC alignment (does the edited rule match the story's AC?).
- Downstream consistency (does a change in one role's rules require a matching
  update in the shared pipeline stages?).

Coverage status is tracked implicitly via PR history. No separate coverage
report is generated until the Layer-3 harness is implemented.

---

## 7. AC-as-Oracle

For change-scoped doc stories (stories that modify only template or workflow
files), the story's Acceptance Criteria are the test oracle:

1. Each AC describes an expected behavior or structural property of the changed
   file.
2. After implementation, self-check each AC against the actual file content.
3. For Tier-A changes, re-run the `refactor templates` scan (see §9) as the
   regression check.

**Do not tick AC checkboxes** — that is the PO's role after QA confirms.

---

## 8. Running the Checks

### Local pre-PR (mandatory for any PR touching templates or workflows)

```bash
python scripts/validate_templates.py
```

Exit 0 = clean. Exit non-zero = violations printed; fix before opening a PR.

### Fixture self-test (proves each invariant actually fires)

```bash
bash scripts/test/run.sh
```

Five fixture files (one per invariant class tested) are in
`scripts/test/fixtures/bad/`. The runner asserts each fixture produces at
least one `[ERROR]` line. Invariant #5 (manifest integrity) is a global check
and is covered by the main `validate_templates.py` run on the full corpus.

### CI gate

`.github/workflows/validate-templates.yml` runs `python scripts/validate_templates.py`
on every PR that touches `.claude/agents/templates/**` or
`.claude/agents/workflows/**`. The PR may not be merged until the CI job passes.

---

## 9. Relationship to Existing Gates

### Project_Priming §8 — Tech Stack pre-PR gates

`Project_Priming.md §8` (devkit-internal, `.claude/agents/working/context/`) lists
the pre-PR syntax gates:

| Check | Command | Applies when |
|---|---|---|
| Shell script syntax | `bash -n <file>` | Any `.sh` file changed |
| PowerShell syntax | PowerShell parser check | Any `.ps1` file changed |
| **Template validator** | `python scripts/validate_templates.py` | **Any template or workflow `.md` changed** |

The template validator is the new addition from this story. It runs in addition
to (not instead of) the `bash -n` and PowerShell checks.

### The `refactor templates` workflow — heuristic/exploratory complement

`refactor templates` is the exploratory scan for style and drift issues that are
too heuristic for Layer-1:

- `@`-mention style checking (the corpus legitimately contains constructed
  `@<login>` mentions in `Blocked_Request_template.md` — no blanket ban).
- Bare `#NN` style checking (illustrative PR examples exist in templates).
- Cross-mode content-drift heuristics.

`refactor templates` and `validate_templates.py` are complements: the validator
is the deterministic regression gate; `refactor templates` is the periodic
heuristic clean-up sweep.

---

## 10. Layer-2 / Layer-3 Roadmap

### Layer-2: Deployment smoke-test harness (deferred)

Implement as a follow-up story. Automates the test matrix described in §3:
- `init project` in both modes → assert file set + placeholder substitution.
- `update project` → assert idempotency.
- Coverage: catches RF-016/017 class (init writes wrong path or content).

### Layer-3: Agent-in-the-loop behavioral harness (deferred)

Implement as a follow-up story (Tier-A files first). Requires:
- A test-story scaffold with known AC.
- A test-agent harness that can observe agent output.
- An oracle that asserts the agent followed the correct procedure.

---

## 11. Maintenance

### Adding a new invariant

1. Implement the check function in `scripts/validate_templates.py`.
2. Add a fixture file in `scripts/test/fixtures/bad/` that reliably triggers it.
3. Add a `run_fixture` call for it in `scripts/test/run.sh`.
4. Document the new invariant in §4 of this guide.

### Updating the placeholder registry

When adding a new `{{TOKEN}}` to a template:
1. Add the token name to `KNOWN_DOUBLE_BRACE_TOKENS` in `validate_templates.py`.
2. Run `python scripts/validate_templates.py` to confirm clean pass.
3. Document the new placeholder in the relevant template file or init workflow.

### Updating the alias table (section refs)

When adding a new rules file or renaming a section:
1. Add or update the entry in `SECTION_REF_ALIAS` in `validate_templates.py`.
2. Verify the template file has the referenced `## N.` heading.
3. Run `python scripts/validate_templates.py` to confirm.

### Updating RETIRED_TRIGGERS

When a trigger command is confirmed retired:
1. Add the exact string to `RETIRED_TRIGGERS` in `validate_templates.py`.
2. Run `python scripts/validate_templates.py` to check for stragglers.
3. Fix any flagged occurrences or add them to a documented exemption.

### Keeping fixtures in sync

When a new invariant is added or an existing one is changed:
- Update or add the corresponding fixture in `scripts/test/fixtures/bad/`.
- Verify `bash scripts/test/run.sh` still passes (all fixtures flagged).

---

**Document version:** 1.0  
**Created:** 2026-06-30  
**Story:** ST-000016
