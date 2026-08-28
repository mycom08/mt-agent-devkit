# Audit Rules — Tier A Detection Spec

**Applies to:** the `audit agent files` workflow's scan subagent (`.antigravity/agents/workflows/Audit_Agent_Files_Workflow.md`).
**Scope:** devkit-internal corpus audit only — `.antigravity/agents/templates/**`, `.antigravity/agents/workflows/**`, `.antigravity/agents/working/**` (excluding this file's own findings-output directory, `.antigravity/agents/internal/`).

This file defines **what counts as a finding**. It does not define report mechanics, approval flow, apply/revert, or crash handling — those live in `Audit_Agent_Files_Workflow.md`.

---

## 1. Tier A Only

Tier A is the entire scope of this audit. Four finding classes, and nothing else:

| Class | Name | Edit proposed? |
|---|---|---|
| `D-n` | Cross-file duplication — byte-identical | Yes |
| `RP-n` | Cross-file duplication — role-parallel | Yes (opt-in default) |
| `C-n` | Contradictions | **No — report-only** |
| `X-n` | Dead or orphaned references | Yes |

### Explicitly out of scope

- **Sentence-level wordiness rewriting.** Concision editing within a single passage is a style judgment call, not a detectable defect — never flagged, never proposed.
- **Intra-file repetition.** A file repeating itself is usually deliberate emphasis, not a defect. `QA_Rules_template.md §3` intentionally states "PO ticks AC, not QA" twice — the redundancy exists because the single-statement version shipped and broke live (see `#77`). An audit pass that treats intra-file repetition as a defect would delete exactly this kind of safeguard. Only **cross-file** duplication is in scope.

### Absolute exclusion

- **`<!-- audit:keep -->`.** Any content marked with this comment is never proposed for change, under any finding class — `D-n`, `RP-n`, `C-n` (not applicable, report-only), or `X-n`. This is checked before any other rule and overrides every matching condition below.

---

## 2. Duplication — Matching Mechanics

**No similarity percentage, ever.** Matching is byte-identical after normalization — a reviewer must be able to verify "identical except the role name," not "87% similar." Two normalization profiles apply, one per class:

- **`D-n` normalization:** whitespace collapse only — runs of spaces collapsed to one, trailing whitespace stripped. No other substitution.
- **`RP-n` normalization:** whitespace collapse **plus** substitution over a **closed role-alias table**, and nothing else. No dates, numbers, paths, or section numbers are ever normalized in either class.

**Closed role-alias table** (`RP-n` only):

```
Developer | Dev
Technical Lead | TL
QA
Product Owner | PO
Business Analyst | BA
UI/UX Designer
```

Plus each role's derived file-name forms, e.g. for Developer: `developer_instructions`, `Developer_Rules`, `Developer_Memory` (and the equivalent derived forms for every other role). No token outside this table — and its derived file-name forms — is ever substituted.

### Common gate (both `D-n` and `RP-n`)

A finding is only raised when **both** hold:
1. The shared block is **>= 15 contiguous lines** (post-normalization).
2. The proposed target file is **already on the consuming agent's mandatory read list** — i.e. a file that role's instruction/rules chain requires reading unconditionally every session (`Agent_Common_Bootstrap.md §1`'s Project Priming/Rules/Memory sequence, plus that role's own Rules file's own "Mandatory Reading" section). A file only reachable via a conditional trigger pointer ("read X before doing Y") does not satisfy this — the duplicate would only be *replaced* with a pointer the consuming agent won't reliably follow.

### `D-n` — byte-identical duplication

- Threshold: **N >= 2** instances (two files sharing an identical >=15-line block already justifies a canonical copy + pointer).
- Proposed edit: keep the canonical block in the target file (mandatory-read file); replace the duplicate block in every other file with a one-line pointer (`See <target file> §<section>.`).

### `RP-n` — role-parallel duplication

Beyond the common gate, three additional conditions:

- **Uniform substitution.** Every role token inside one instance must map to the *same* alias throughout that instance. A block where file A uses `Developer` at one point and `QA` at another, while file B swaps which role appears where, is **not** a match — the roles are participants the rule is *about*, not the subject of a parallel restatement, and normalizing would erase that distinction rather than reveal a duplicate.
- **N >= 3 instances.** Higher floor than `D-n` because merging replaces N copies with 1 canonical copy + N pointers — at N=2 the pointer-follow risk on two agents isn't repaid; N=3 is the cheapest defensible floor where it is.
- **Never candidates, regardless of length:** YAML frontmatter, and the `## Your Role` section of any instruction file. These are the file's identity — merging them defeats their purpose.

Proposed edit (when a finding is raised): rewrite the canonical block in the target file in role-neutral language (no role name embedded), replace each instance's original role-specific block with a one-line pointer to the target file.

**Report and approval:** `RP-n` findings go in their **own report section**, never mixed into `D-n`. They **default to not selected** at the approval gate — the user opts in **per finding**, individually. There is no "approve all duplication" batch action for this class; it is the highest-value and highest-risk class in Tier A and must be reviewed one at a time.

---

## 3. Contradictions (`C-n`) — Report-Only

A contradiction finding requires **all three** of:

1. **Same subject** — same actor + same artifact + same action (e.g. "who ticks AC," "when status moves to testing"). Different subjects are never contradictions.
2. **Both statements unconditional in their own file** — neither is guarded by a stated mode, role, or phase condition.
3. **Co-reachable** — both files land in one agent's context in one run: both on some role's mandatory read list, or one file references the other.

### Carve-outs — never a contradiction

- **Mode bifurcation.** Anything guarded by `**GitHub mode:**` / `**Strict mode:**` prose. Stronger: `.antigravity/agents/templates/github/**` and `.antigravity/agents/templates/strict/**` are **excluded from scanning entirely** (both duplication and contradiction). Their thin variants are comment-only — `scaffold_mechanical.sh` strips every all-comment mode body before append, so both modes deploy byte-identical files. A thin variant contributes no deployed content; it can neither contradict nor duplicate the shared file, because overlapping with it is the design.
- **Template vs. `working/` mirror.** Never compare `templates/X_template.md` against `working/X.md`. `Project_Priming_Read_On_Demand.md §15` explicitly sanctions intentionally-diverged mirrors (the devkit runs GitHub-mode-only while templates stay target-generic). Divergence there is drift, tracked by the §15 dual-update rule — out of Tier A scope entirely; scanning it would false-positive across most of the corpus.
- **Role-scoped views.** E.g. `Story_Standard.md` (full) vs. `Story_Standard_QA.md` (role view). A view that omits or narrows does not contradict the file it's scoped from.
- **Different lifecycle phases.** Statements about different gates ("before merge" vs. "after merge") are not opposites.
- **`<!-- audit:keep -->`** content, per §1 above.

### Reporting and approval

- `C-n` findings are **report-only** — the audit proposes **no edit** and **never selects a winning side**. Choosing which statement is correct is a design decision, not a detection outcome (the `#77` case is the proof that getting this wrong ships live).
- "Approval" for a `C-n` finding means the user **records the resolution in their response** to the report — not a file-edit accept/reject. No file changes as a result of a `C-n` finding by itself.

---

## 4. Dead or Orphaned References (`X-n`)

A finding in this class is a reference inside the scanned corpus that does not resolve:

- **Dead file-path reference** — a `.antigravity/agents/...` path cited in prose (backtick-quoted or plain) that does not exist under any of the three resolution roots `validate_templates.py`'s `_resolve_file_ref` already uses (repo-verbatim, `working/` mirror, `<stem>_template.md` fallback). If it resolves through any of the three roots, it is **not** a finding — the audit's `X-n` class is for references that fail all three, not a stricter check than the validator's.
- **Dead section-anchor reference** — a `<File> §N` / `<File> §Name` citation where the target file exists but no heading matching that section number/name exists in it.
- **Orphaned reference** — a file present in a scanned directory that is not referenced from any other in-scope file's mandatory-read list, trigger-pointer, or workflow routing table, and is not itself an entry point (`AGENTS.md`, a workflow file reachable from a `AGENTS.md` trigger row, `Project_Priming_Bootstrap.md`). An orphaned file is reported, not deleted automatically — the proposed edit is stated per finding (remove the file, or re-link it from wherever it should be referenced), and remains subject to the same per-finding approval as `D-n`/`RP-n`.

Proposed edit: correct the reference (fix the path/anchor) if the intended target is unambiguous from context; otherwise propose removal of the dead reference and state the ambiguity in the rationale so the user decides at approval time.

**Known coverage gap (accepted, not fixed by this class):** `_resolve_file_ref`'s three-root resolution means a reference the audit edits can still resolve through a sibling root undetected, and an edit made only inside a `working/` file's prose is never read by the validator at all. `X-n` detection is a best-effort corpus read, not a substitute for `validate_templates.py`'s mechanical reference-integrity invariant — the workflow's own apply-time validator run (see `Audit_Agent_Files_Workflow.md`) and the dedicated-branch/git-diff-scoped revert are the real safety net for any edit this class proposes, exactly as they are for `D-n`/`RP-n`.

---

## 5. Report Grouping (spec only — full format lives in the workflow file)

Findings are grouped by class in this fixed order, one report section per class: `## Duplication - byte-identical` (`D-n`), `## Duplication - role-parallel` (`RP-n`), `## Contradictions (report-only)` (`C-n`), `## Dead references` (`X-n`). One line per finding: ID, `file:line-range` for every instance, proposed target file (dedup classes only, or `report-only` for `C-n`), one-clause rationale.

**Reviewability over exhaustiveness.** The tier boundaries above (>=15 lines, N>=2/N>=3, three-condition contradiction test, carve-outs) exist specifically so the report stays short enough to actually read. A report of hundreds of marginal items gets rubber-stamped, which defeats the purpose of a per-finding approval gate — when in doubt about whether something clears a threshold, it is not a finding.

---

## Version

**Created:** 2026-07-30 (ST-000035)
