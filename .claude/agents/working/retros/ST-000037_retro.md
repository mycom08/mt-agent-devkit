# Retrospective — ST-000037
**Date:** 2026-07-31
**Story:** [ST-000037][DEVKIT] Inject Auditor into target projects + wire sync devkit / update project audit stage

## Implementer — Developer
### Impediments & Unclear Points
- `[context]` AC13 named only 4 files for the rules-file count bump (`Init_Project_Workflow.md`, `Update_Project_Workflow.md`, both `Sync_Devkit_Workflow*` templates), but adding a 20th rules file is the same "Nth enumerated corpus item" ripple as ST-000022/ST-000023 — `scaffold_mechanical.sh`'s `VERBATIM_RULES` array and `Build_Software_Workflow.md`'s two count mentions also needed the bump, confirmed by re-reading those two stories' own CHANGELOG entries (both bumped exactly these same extra files every time). Reinforces: `Developer_Memory.md` Fact 1.
- `[context]` Refinement's own thread had already resolved the two real open points (orchestrator-folder scope, written-vs-resolved scope precision) before implementation started — the TL/PO exchange on #102 was thorough enough that zero new mid-implementation questions came up.

### Process Suggestions
- `[workflow]` Consider having `Project_Priming.md §15a`'s "Nth role" ripple-site table gain a parallel "Nth rules file" row (or point at Developer Memory Fact 1 explicitly) — the AC-writing step (PO/TL refinement) keeps under-naming the same 2 extra files (`scaffold_mechanical.sh`, `Build_Software_Workflow.md`) across three stories now (ST-000022, ST-000023, ST-000037), even though the Dev catches it every time from memory. Codifying it in the priming doc would remove the reliance on Dev's own memory file being read.

### What Worked Well
- Running `validate_templates.py` twice (real baseline via `git stash`, since untracked new files survive a plain stash and would otherwise pollute a "baseline") caught that my `changes.json` entry actually fixed a would-be error rather than introducing one — confirmed zero new violations before opening the PR.
- The devkit-internal `Audit_Rules.md`/`Audit_Agent_Files_Workflow.md` pair (ST-000035) was detailed enough to lift the subagent-spawn shape and report/fallback mechanics directly, with no re-derivation needed — scoping the target-side spec down to a single `MA-n` class (report-only, no template access) was the only real design decision.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- `[failure]` Round 1 CHANGES REQUESTED on a single finding: adding the Nth item to an enumerated corpus set rippled into one site the AC did not name and the implementer's own ripple-site list did not cover — a **deployed template** carrying a scaffold instruction that enumerates the set by name and by count. The implementer caught the two devkit-internal ripple sites from memory but stopped at the boundary of the list their memory fact records; the missed site was of a different kind (template, not devkit-internal), so it also needed a manifest entry, not just a count edit. Same defect class as three prior stories, now recurring across a fourth.
- `[context]` The refinement I authored on this story named ripple sites and did not include the missed one either — so the AC under-specification and the review-side catch both trace to the same absent inventory. A reviewer re-deriving the ripple set independently of the implementer's list is what closed it; had I only checked the sites the AC named, this would have shipped.

### Process Suggestions
- `[context]` Priming docs carry an "Nth agent role" ripple-site checklist but no equivalent for the more frequent case — adding an Nth item to any other enumerated set (rules file, workflow file). Both implementer and reviewer are currently reconstructing that inventory from a personal memory file, which is why the same 1–2 sites get missed each time. Promote it to the shared priming doc as a set-agnostic checklist, and include the **deployed-template** sites alongside the internal ones, since only the former also require a change-manifest entry.
- `[workflow]` When a story adds an item to an enumerated set, the reviewer's cheapest complete check is a corpus-wide grep for the *old count and the set's signature members* rather than a re-read of the AC-named files. That inverts the default review order — verify the enumeration inventory first, since it is the failure mode with precedent, then the story's actual design content. Worth stating explicitly in the reviewer checklist for enumeration-ripple stories.

### What Worked Well
- Treating "is this scope an actual mechanism or just prose?" as the primary review question paid off in the opposite direction from expected: the new stage's scoped-file-list, which looked like the most likely place for unbacked hand-waving, turned out to rest on three pre-existing mechanisms already in the file (a per-write log instruction, a "log every file written" rule, and a "skipped files never appear in the written-files report" rule). Confirming a claim by locating the mechanism it names is faster than arguing about the prose around it.
- Verifying a cited precedent against the actual changelog entries rather than the citation. The implementer's precedent claim was accurate, and checking it took one grep — but the same check is what exposed that the precedent covered only the internal ripple sites, which is precisely the gap the missed file fell through. Verifying a citation and reading what it *doesn't* cover are the same operation.
- The differential validator run stayed decisive despite a corpus that fails on the base branch too: parallel clean worktrees, sorted output, diffed. The entire delta was one line-number shift of a pre-existing violation, which took a non-zero, exit-1 tool and turned it into a usable signal.

**Round-2 addendum (APPROVED).** Round-1 content above is unchanged; nothing in it was revised by the second pass.
- `[workflow]` Round-2 scoping needed one adjustment the standard `git diff <round1-head> <round2-head> --stat` recipe does not anticipate: the reviewer's own memory/retro commit had landed between the two refs, so that range overstated the implementer's work by two files. Diffing from *the reviewer's own commit* to the new head isolated the actual round-2 change (3 files, 6 insertions). Worth folding into the recipe — after a stage-transition commit, the round-1 head is no longer the right base.
- `[context]` Confirmed the round-1 finding was the whole of it: re-running the residual-stale-site grep on the fixed tree returned only the corrected line, so the enumeration ripple closed completely rather than revealing further sites. This is the payoff for having run the exhaustive grep at round 1 instead of reporting the first hit and stopping — the change request could be stated as a complete fix, and round 2 was a confirmation pass rather than another discovery pass.
- The manifest check that mattered was structural, not visual: parsing `changes.json` to assert version keys still strictly descending, `descriptions` keys exactly equal to `new` + `modified`, and every referenced path present on disk. Version-key ordering in particular is explicitly outside what the validator checks, so it is only ever caught by hand — cheap to assert programmatically, invisible to eyeballing a diff hunk.

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
