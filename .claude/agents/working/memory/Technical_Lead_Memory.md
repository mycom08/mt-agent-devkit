# Technical Lead Memory

## Stored Facts

### Fact 1
- **Rule:** Any file under `.claude/agents/templates/` must have every executable path and "read file X" pointer resolve against the **deployed** target-project inventory, never the devkit tree — targets have no `working/`, no `templates/`, no devkit-internal workflows. When an injected template needs devkit-only automation, use `Sync_Devkit_Workflow_template.md`'s fetch path (`{DEVKIT_SOURCE_URL}` from the target's own `CLAUDE.md`) — that removes the dependency rather than resolving it at runtime. The two trees can never share a source file: **restate the convention + pointer**, never extract. **Corollary:** a target-side detect pass has no template to diff against, so it finds only defects self-evident inside one file — never divergence-from-source. Scope it to model-generated writes (adapt-to-mode, merge); verbatim-overwrite files self-heal via the next sync's checksum pre-filter.
- **Applies when:** reviewing any `templates/**` file naming a path, script, or workflow file; scoping a target-side audit stage.
- **Evidence:** ST-000028 PR #87 CR-1/CR-2; ST-000037 refinement.
- **Expires when:** a validator invariant scopes templates to the deployed inventory.

### Fact 2
- **Rule:** `validate_templates.py` cannot catch the Fact 1 class: `_FILEREF_RE` matches `.md` only (scripts never checked); `_resolve_file_ref` tries **three** roots (repo-verbatim, `working/` mirror, `<stem>_template.md`), so a devkit-only or deleted path still resolves via a sibling. `SCAN_DIRS` is `templates/`+`workflows/` only — CI green is **no evidence for a `working/` file** (pass dirs explicitly; `main()` takes `<dir>...`). It never checks `changes.json` ordering or roster↔write-location consistency. Under explicit paths the baseline is **~70 violations and exit 1 on `main` too**, so any validator verdict must be *differential*: same command on base and head in parallel `git worktree`s, diff sorted output.
- **Applies when:** tempted to treat a passing validator run as review coverage.
- **Evidence:** ST-000028; ST-000035 PR #103; same class as the ST-000015 path-move finding.
- **Expires when:** `_FILEREF_RE` widens past `.md` and deployment-scoped resolution lands.

### Fact 3
- **Rule:** Split-workflow thin variants in `github/` and `strict/` are comment-only; `scaffold_mechanical.sh:88-93` strips them, so **both modes deploy byte-identical files**. Any mode-dependent AC must be satisfied by inline "**GitHub mode:** / **Strict mode:**" prose in the *shared* file. Say so at refinement.
- **Applies when:** an AC says "applied to both github and strict variants".
- **Evidence:** ST-000028, restated in ST-000032/033.
- **Expires when:** thin variants gain non-comment content.

### Fact 4
- **Rule:** Resume-branch completeness is now a `Technical_Lead_Rules.md §2` bullet — read it there. Devkit-specific residue: a resume gap closes only when the *instruction* changes (a warning beside a rule that still says "skip" leaves it intact), and a step appended after the ones a file-presence check covers must be unconditional on resume.
- **Applies when:** reviewing any pipeline/loop state file or a newly inserted workflow step.
- **Evidence:** ST-000025/026/028 — three consecutive stories, same defect.
- **Expires when:** state-file design gains a branch-completeness checklist.

### Fact 5
- **Rule:** Phrase change requests and fix menus as "at minimum these, plus any site sharing the same mechanism" — an enumerated list gets treated as exhaustive.
- **Applies when:** writing any CR that names call sites, or proposing fix options.
- **Evidence:** ST-000026 (listed 3 sites, missed a 4th); ST-000028 r2 (offered 3 fixes, Dev found a better 4th).
- **Expires when:** never — this is a phrasing discipline.

> Fact 6 removed (ST-000037): now a `Technical_Lead_Rules.md §2` bullet. Gap kept on purpose.

### Fact 7
- **Rule:** `gh issue list --json` reads the immediately-consistent issues API; `--search` hits the eventually-consistent index **and** does contiguous-token phrase matching (GitHub strips `**`/`::` at index time), so a prefix-title story silently matches another. Prefer plain list + local exact-line match (`grep -Fxq` in strict mode). Always hand-construct one adversarial input against the tool's *documented* semantics — prose can be coherent while the command answers a different question.
  Always pass `--repo <slug>` explicitly — never rely on the working directory's git remote.
- **Applies when:** any `gh` invocation, especially an AC whose correctness mechanism is a CLI idempotency or dedup query.
- **Evidence:** ST-000026 PR #85 CR-2, fixed at 5 call sites; standing devkit convention.
- **Expires when:** GitHub changes search semantics.

### Fact 8
- **Rule:** Narrowing an existing AC's technical meaning is TL scope; **adding a standalone AC is PO scope**. When a design decision creates a new deliverable, fold it into the existing AC's wording plus the TL-owned **Technical Scope** section, and flag PO to consider promoting it.
- **Applies when:** answering refinement questions that surface a new obligation.
- **Evidence:** `Technical_Lead_Rules.md §2`; `Story_Standard_TL.md §7` red flag "TL commenting on scope".
- **Expires when:** the TL/PO boundary in those rules changes.

### Fact 9
- **Rule:** Round-2 scope confirmation is `git diff <round1-head> <round2-head> --stat` — proves which round-1 clean findings could even have regressed, cheaper and stronger than re-reading them. Exclude your own memory commits from the range. Verify an implementer's "reuses the existing mechanism" claim by grepping the cited file's headings.
- **Applies when:** re-reviewing after CHANGES REQUESTED.
- **Evidence:** ST-000028; ST-000037 (own commit inflated the range).
- **Expires when:** never.

### Fact 10
- **Rule:** Write the retro at the end of stage work regardless of verdict — `Retro_Rules.md` "When to Write" is unconditional; a spawn prompt's "if approved, write your retro" is the happy path, not a narrowing. Addenda per round.
- **Applies when:** a review round ends in CHANGES REQUESTED.
- **Evidence:** ST-000015/25/26/28 precedent.
- **Expires when:** `Retro_Rules.md` adds a verdict condition.

### Fact 11
- **Rule:** Templates and their `working/` mirrors drift silently — verify **both**, and diff before editing (`git diff --no-index <template> <mirror>`). `Project_Priming.md §15` carve-outs cover intentionally-diverged and no-mirror cases (`Strict_Mode_Story_Guide_template.md` is the named no-mirror file).
- **Applies when:** changing any template with a devkit working mirror.
- **Evidence:** `Technical_Lead_Rules.md §3` once said "after merge" vs the template's "before merge"; ST-000038.
- **Expires when:** mirrors are generated, not hand-maintained.

### Fact 12
- **Rule:** A change to where a file is *written*, or any step/rule renumbering, must update every referrer — grep the whole template+workflow corpus for the old path/pattern against the **final** file on the PR branch (`git show <branch>:<file> | grep`), not the diff hunks, which cannot distinguish a reference correctly left alone from one that should have changed. If an Update-side migration self-heals via a directory-existence check, moving Init to pre-create that dir silently disables it. Same for an Nth-enumerated-set item: grep the **old count** + a signature member corpus-wide; the AC never names every site, and deployed `templates/` sites also need a `changes.json` entry.
- **Applies when:** a path-move, scaffold-location, renumbering, or Nth-enumerated-item change.
- **Evidence:** ST-000015/PR #41; ST-000025 PR #71; ST-000037 (4th consecutive ripple miss).
- **Expires when:** never.

### Fact 13
- **Rule:** Orchestrator state files live in the orchestrating workspace's `.claude/agents/tmp/`, not the managed repo — gitignored in both modes, has a cleanup lifecycle, and must exist before the managed repo does. Bridge the two working dirs by recording the managed repo's absolute path plus per-step commit SHAs in the state file.
- **Applies when:** designing any pipeline/loop state file.
- **Evidence:** ST-000028; `build_software_state.md` is the pattern.
- **Expires when:** never.

> Fact 14 removed (ST-000035): superseded by `Agent_Common.md §2`/`§5`. Gap kept on purpose.

### Fact 15
- **Rule:** A **pre-spawn** eligibility filter (nothing spawned, no state) is skip-and-continue, like `Sprint_Workflow`'s `status:blocked` rule — not the Blocked Story Procedure, which halts because an agent is mid-story with a live branch. If the status label stays unchanged, skip-and-continue needs an in-run skip list in the state file or the loop re-selects forever.
- **Applies when:** designing any story-eligibility gate.
- **Evidence:** ST-000027.
- **Expires when:** never.

> Fact 16 removed (ST-000038): merged into Fact 7. Gap kept on purpose.

### Fact 17
- **Rule:** When a story hardens a soft principle into an absolute ("evidence by pointer" → "**never** paste command output"), check what elsewhere in the same rules family **mandates** the now-prohibited act. The cross-role source usually survives on a scoping preamble (`Story_Standard.md` §9 = "GitHub Issue comments"), but the per-role views restate the rule **without** that preamble — so the absolute lands unqualified next to bullets that govern PR comments. Grep the new absolute's own verb corpus-wide for a matching imperative before approving.
- **Applies when:** reviewing any story that converts advisory wording into a prohibition, or adds a gate item.
- **Evidence:** ST-000038 PR #108 CR-1 — §9 rule 4's "never paste" vs §12 Reviewer gate's mandatory `gh pr checks` paste.
- **Expires when:** never — restatement strips scope by construction.

## Troubleshooting Facts

No troubleshooting facts recorded yet.
