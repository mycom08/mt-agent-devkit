# Technical Lead Memory

## Stored Facts

### Fact 1
- **Rule:** Any file under `.claude/agents/templates/` must have every executable path and "read file X" pointer resolve against the **deployed** target-project inventory, never the devkit tree. Target projects have no `working/`, no `templates/`, and never receive devkit-internal workflows. When an injected template needs devkit-only automation, use `Sync_Devkit_Workflow_template.md`'s fetch path (`{DEVKIT_SOURCE_URL}` from the target's own `CLAUDE.md`, WebFetch + curl fallback) — that removes the dependency instead of resolving it at runtime. The two trees can never share a source file: **restate the convention + pointer**, never extract into a shared one.
- **Applies when:** reviewing or writing any `templates/**` file that names a path, script, or another workflow file.
- **Evidence:** ST-000028 PR #87 CR-1/CR-2; unfixed instance in `Sync_Devkit_Workflow_template.md`'s "Settings hook".
- **Expires when:** a validator invariant scopes injected templates to the deployed "Expected files" inventory.

### Fact 2
- **Rule:** `validate_templates.py` cannot catch the Fact 1 class. Its `_FILEREF_RE` matches `.md` only (scripts never checked) and `_resolve_file_ref` tries **three** roots — repo-verbatim, the `working/` mirror, and a `<stem>_template.md` fallback — so a devkit-only or since-deleted path still resolves via a sibling root. `SCAN_DIRS` is `templates/` + `workflows/` only: nothing under `working/` is scanned at all (pass dirs explicitly — `main()` takes `<dir>...`). It also does not check roster ↔ write-location consistency. A green run is not evidence. For any batch-edit workflow, the real revert net is a dedicated branch + `git diff --stat`, not a validator verdict.
- **Applies when:** tempted to treat a passing validator run as review coverage.
- **Evidence:** ST-000028; same class as the ST-000015 path-move finding.
- **Expires when:** `_FILEREF_RE` widens past `.md` and deployment-scoped resolution lands.

### Fact 3
- **Rule:** Split-workflow thin variants in `github/` and `strict/` are comment-only; `scaffold_mechanical.sh:88-93` strips them, so **both modes deploy byte-identical files**. Any mode-dependent AC must be satisfied by inline "**GitHub mode:** / **Strict mode:**" prose in the *shared* file. Say so at refinement — otherwise Dev hunts for a mode difference that cannot exist.
- **Applies when:** an AC says "applied to both github and strict variants" for a split workflow.
- **Evidence:** ST-000028, restated in ST-000032/033 refinement.
- **Expires when:** thin variants gain non-comment content or the merge stops stripping.

### Fact 4
- **Rule:** A resume-governing state field needs an explicit branch for **every value it can hold**, not just the "still working" one. A resume gap is only closed when the *instruction* changes: a warning beside a rule that still says "skip" leaves the gap intact. When a new step is appended after the steps a file-presence check covers, make it unconditional on resume (safe whenever idempotent).
- **Applies when:** reviewing any pipeline/loop state file or a newly inserted workflow step.
- **Evidence:** ST-000025 Stage 4, ST-000026 Stage 5, ST-000028 CR-3 — three consecutive stories, same defect.
- **Expires when:** state-file design gains a checklist that enforces branch completeness.

### Fact 5
- **Rule:** Phrase change requests and fix menus as "at minimum these, plus any site sharing the same mechanism" — an enumerated list gets treated as exhaustive.
- **Applies when:** writing any CR that names call sites, or proposing fix options.
- **Evidence:** ST-000026 — listed 3 call sites, missed the strict-mode 4th; ST-000028 r2 — offered 3 fixes, implementer found a better 4th.
- **Expires when:** never — this is a phrasing discipline.

### Fact 6
- **Rule:** Cite `§N` section numbers, never line numbers. Resolve a `grep -n` hit to its `## N.` header before writing `§N` — a wrong-but-existing section number ships silently.
- **Applies when:** citing a rules file in a review comment or design answer.
- **Evidence:** ST-000026 — wrote "§15" meaning line 15, which sits in §1; propagated into 2 files.
- **Expires when:** never.

### Fact 7
- **Rule:** `gh issue list --json` reads the immediately-consistent issues API; `--search` hits the eventually-consistent search index **and** does contiguous-token phrase matching (GitHub strips `**`/`::` at index time), so a prefix-title story silently matches another. For small result sets prefer plain list + local exact-line match. In strict mode the equivalent is `grep -Fxq`.
  Always hand-construct one adversarial input against the tool's *documented* semantics — prose can be coherent while the command answers a different question.
- **Applies when:** an AC's correctness mechanism is a `gh`/CLI idempotency or dedup query.
- **Evidence:** ST-000026 PR #85 CR-2, fixed at 5 call sites.
- **Expires when:** GitHub changes search semantics.

### Fact 8
- **Rule:** Narrowing or clarifying an existing AC's technical meaning is TL scope; **adding a standalone AC is PO scope**. When a design decision creates a new deliverable, fold it into the existing AC's wording plus the TL-owned **Technical Scope** section, and flag to PO that they may want it promoted.
- **Applies when:** answering refinement questions that surface a new obligation.
- **Evidence:** `Technical_Lead_Rules.md §2`; `Story_Standard_TL.md §7` red flag "TL commenting on scope".
- **Expires when:** the TL/PO boundary in those rules changes.

### Fact 9
- **Rule:** Round-2 scope confirmation is `git diff <round1-head> <round2-head> --stat` — it proves which round-1 clean findings could even have regressed, far cheaper and stronger than re-reading them. Verify an implementer's "this reuses the existing mechanism" claim by grepping the cited file's own headings rather than accepting it.
- **Applies when:** re-reviewing after CHANGES REQUESTED.
- **Evidence:** ST-000028 — showed only one template file changed, so 4 count-ripple files needed no re-verification.
- **Expires when:** never.

### Fact 10
- **Rule:** Write the retro section at the end of stage work regardless of verdict — `Retro_Rules.md` "When to Write" is unconditional. A spawn prompt saying "if approved: … write your retro" is the happy path, not a narrowing of the rule. Add addenda per round.
- **Applies when:** a review round ends in CHANGES REQUESTED.
- **Evidence:** ST-000015/25/26/28 precedent.
- **Expires when:** `Retro_Rules.md` adds a verdict condition.

### Fact 11
- **Rule:** Templates and their `working/` mirrors drift silently between stories — verify **both** when checking consistency, and diff before editing (`git diff --no-index <template> <mirror>`). Carve-outs in `Project_Priming.md §15` cover intentionally-diverged and no-mirror cases.
- **Applies when:** changing any template that has a devkit working mirror.
- **Evidence:** `Technical_Lead_Rules.md §3` once said "after merge" vs the template's "before merge".
- **Expires when:** mirrors are generated rather than hand-maintained.

### Fact 12
- **Rule:** A change to where a file is *written*, or any step renumbering, must update every referrer — grep the whole template+workflow corpus for the old path/pattern before approving, against the **final** file on the PR branch (`git show <branch>:<file> | grep`), not the diff hunks. A hunk-only check cannot distinguish a reference correctly left alone from one that should have changed. If an Update-side migration self-heals via a directory-existence check, moving Init to pre-create that dir silently disables the self-heal.
- **Applies when:** reviewing a path-move, scaffold-location, or step-renumbering change.
- **Evidence:** ST-000015 / PR #41; ST-000025 PR #71 (8 `Path A/B step` hits verified individually).
- **Expires when:** never.

### Fact 13
- **Rule:** Orchestrator state files live in the orchestrating workspace's `.claude/agents/tmp/`, not the managed repo — that dir is gitignored in both modes, has a cleanup lifecycle, and must exist before the managed repo does. Bridge the two working directories by recording the managed repo's absolute path plus per-step commit SHAs in the state file.
- **Applies when:** designing any new pipeline/loop state file.
- **Evidence:** ST-000028; `build_software_state.md` is the pattern.
- **Expires when:** never.

### Fact 14
- **Rule:** Size caps on memory files and Working Records must be stated in **characters** (`wc -c`), never lines — entries are one soft-wrapped bullet each, so `wc -l` is uncorrelated with token cost. Agreed caps: Working Record ≤ 4,000, memory ≤ 10,000.
- **Applies when:** reviewing or proposing any cap on these artifacts.
- **Evidence:** ST-000032/033; a 60-line memory file measured 29,016 chars.
- **Expires when:** the caps in `Agent_Common.md §2` change.

### Fact 15
- **Rule:** A **pre-spawn** eligibility filter (nothing spawned, no state) is a skip-and-continue, structurally the same as `Sprint_Workflow`'s `status:blocked` rule — not the Blocked Story Procedure, which halts the pipeline because an agent is mid-story with a live branch. If the status label must stay unchanged, skip-and-continue needs an in-run skip list in the state file or the selection loop re-selects forever.
- **Applies when:** designing any story-eligibility gate.
- **Evidence:** ST-000027.
- **Expires when:** never.

### Fact 16
- **Rule:** Always pass `--repo <slug>` explicitly on `gh` calls — never rely on the working directory's git remote.
- **Applies when:** any `gh` invocation, especially cross-project.
- **Evidence:** standing devkit convention.
- **Expires when:** never.

## Troubleshooting Facts

No troubleshooting facts recorded yet.
