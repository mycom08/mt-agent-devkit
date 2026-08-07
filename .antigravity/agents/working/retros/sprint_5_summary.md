# Sprint 5 — Retro Summary
**Sprint:** sprint-5
**Last Updated:** 2026-07-28

---

## ST-000026 — Roadmap stories must be drained into tracked backlog issues at authoring time
**Date:** 2026-07-28
**Loop counts:** Impl→Reviewer: 1 | Impl→QA: 0

### Findings
- `[failure]` A design answer that leans on an existing resume/ordering rule must quote the rule's actual skip condition, not paraphrase it from memory — TL's own Q2 answer asserted Stage 5's resume rule "re-runs safely," which was false as stated *(Technical Lead)*
- `[workflow]` The review checklist had no step for "the documented mechanism is coherent, but does the actual CLI command answer the question the AC asks" — both CR-1 (status filter couldn't answer "is this tracked at all") and CR-2 (GitHub phrase search is a contiguous-token-subsequence match, not exact-line) passed every existing check and still shipped wrong behavior *(Technical Lead)*
- `[context]` Mode-parity (comparing strict vs. github branches of the same step) is a cheap, effective bug-detector — CR-1 was localized immediately because the two branches answered different questions *(Technical Lead)*
- `[instruction]` Citing a rule section (`§N`) without opening the file was wrong twice in one story — TL's round-1 decision comment ("§11") and TL's own round-2 fix ("§15", a grep line number mistaken for a section number) *(Technical Lead / Developer)*
- `[workflow]` A documented resume rule is only closed if the *instruction* changes, not if a warning is added next to it — prose noting "this check does not confirm step N ran" while the rule still says "skip the repo" leaves the gap fully intact *(Technical Lead)*
- `[context]` Enumerating specific call sites in a change request invites treating the list as exhaustive — CR-2 named 3, the implementer found and fixed a 4th (and a 5th) sharing the same mechanism *(Technical Lead)*
- `[context]` Verifying an "invariant untouched" claim by diffing the specific bullet's text (not scanning the PR diff for absence of a hunk) is a cheap, high-value check *(QA)*
- Orchestrator process note: `gh issue close 82 --comment "..."` errored "already closed" (PR's `Closes #82` had already auto-closed it on merge) and the comment silently did not post — had to post it as a separate follow-up `gh issue comment` call. Same friction as community retro issue #76, now observed live.

### What Worked Well
- The refine-sprint thread (TL Q1/Q2, PO Q4) left almost no ambiguity by the time implementation started — all three touch points and the idempotency marker format were pinned down before coding began *(Developer)*
- Placement, scoping, and dual-update (template + working mirror) were all correct on the first pass; the review reduced entirely to mechanism correctness, not design *(Technical Lead)*
- Because round-2 fixed all 4 CRs as genuine instruction changes (not warnings-next-to-rules), independent QA re-derivation converged on the same pass verdict without new findings *(QA)*

### Actions Applied
- `Technical_Lead_Rules_template.md` + working mirror — resume-rule branch-completeness check, §N citation-accuracy check, fix/call-site-menu-not-exhaustive phrasing convention (commit `a906a95`)
- `Shared_Pipeline_Stages_Shared_template.md` + working mirror — GitHub-mode closure-comment-ordering note (commit `a906a95`)

---

## ST-000027 — Bug Story pre-flight reproduction before spawning agent team
**Date:** 2026-07-28
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[workflow]` A design-first story's resolved Q&A (TL's Q1/Q2 answers, treated as "final") covered GitHub-mode behavior completely but left a strict-mode symmetry gap (no label mechanism to detect a bug story) that only surfaced once template edits were already in progress — worth a PO/TL scan for the equivalent gap in the *other* mode before calling design closed *(Developer)*
- `[skipped-step]` Orchestrator jumped Stage 1→3 in one edit during the non-behavioral fast path (Stage 2 approval + Stage 3 QA sign-off both executed directly, no agent spawn) without an intermediate Stage/Updated write at the Stage 2 boundary *(Orchestrator)*

### What Worked Well
- The prior design-first Q&A thread gave a complete, unambiguous spec for the GitHub-mode behavior and the exact 4 branches to cover — implementation was a direct, low-friction translation of already-agreed decisions with only one small mode-symmetry gap to fill in *(Developer)*
- `validate_templates.py` and the stub/TODO grep both passed clean on the first run, confirming new cross-references were named correctly against existing corpus conventions *(Developer)*

### Actions Applied
- *(none — this story's findings were folded into the broader sprint-5 batch items above rather than applied individually)*

---

## ST-000028 — New workflow: UI/UX Refine — direct orchestrator/user prototype iteration loop
**Date:** 2026-07-28
**Loop counts:** Impl→Reviewer: 1 | Impl→QA: 0

### Findings
- `[failure]` An injected template (deployed to target projects) carried executable references to devkit-only artifacts — a script path under a maintainer-only directory, plus "follow file X exactly" pointing at a file the receiving project never gets. Both read as correct while editing, because the author's own working tree contains them *(Technical Lead)*
- `[failure]` Automated corpus validation gave false assurance: the reference-integrity check resolves candidate paths against the toolkit repo root and its regex covers `.md` only, so a toolkit-only script path inside an injected template resolves clean *(Technical Lead)*
- `[failure]` The injected-template-references-devkit-only-path defect is corpus-wide, not a one-off — a **pre-existing** instance was found in `Sync_Devkit_Workflow_template.md`'s "Settings hook" section during re-review, in a file this story did not author *(Technical Lead)*
- `[workflow]` A new pipeline-state file specified a terminal status value and a "delete only after the final step" write rule, but the resume rule enumerated branches for only the non-terminal values — the 3rd/4th story this sprint where a resume rule's branch set lagged the states its own write rules create *(Technical Lead)*
- `[workflow]` When a story's technical scope says design-first, a pre-flight Q&A that resolves the *architectural* questions is not a substitute for a design draft — the questions answered up front were about placement and ownership; the defects landed in mechanics ("in the receiving project, what actually executes this step?") *(Technical Lead)*
- `[workflow]` Enumerating specific fix options in a change request has the same flaw as enumerating call sites — TL offered 3 fixes, the implementer found a 4th that was strictly better because they were closer to the mechanism inventory *(Technical Lead)*
- A stale intra-file cross-reference (`Step 3g` where sub-steps are plain-numbered 1–6) survived both TL review rounds and QA's independent check — non-blocking, but it's the exact defect type the review checklist claims to catch *(Technical Lead / QA)*

### What Worked Well
- Reproducing the scaffold from both the PR branch and the base branch into scratch targets, then diffing the outputs, converted three separate claims into evidence in one step: no regression, correct file count in both modes, and proof that mode-specific thin-variant comments are stripped before deployment *(Technical Lead)*
- The fix chosen for CR-1/CR-2 was better than the options offered — routing through the already-injected `{DEVKIT_SOURCE_URL}` fetch mechanism instead of resolving a devkit checkout at runtime, which removes the dependency rather than resolving it *(Technical Lead / Developer)*
- Independently re-deriving CR-1/CR-2/CR-3 from live file content (grep + read, not trusting TL's round-2 prose) found no daylight between the review claim and actual file state *(QA)*
- The scaffold dry-run (both modes, PR branch vs. `origin/main`, via `git worktree`) converted several separate claims into one piece of evidence, reusing the same technique TL used in their own review *(QA)*

### Actions Applied
- `Technical_Lead_Rules_template.md` + working mirror — resume-rule branch-completeness check, fix/call-site-menu-not-exhaustive phrasing convention (commit `a906a95`)
- `Sync_Devkit_Workflow_template.md` + working mirror — fixed the confirmed pre-existing Settings-hook bug (commit `a906a95`)
- *(deferred — validator enhancement to widen `_FILEREF_RE` and scope injected-template checks against the deployed inventory needs its own story; not applied in this batch)*

---

## Sprint Consolidated Summary

**Common themes across all 3 stories:**
- **Design-first Q&A resolves architecture, not mechanics.** All three stories had a pre-flight design round that TL/PO called "resolved" before implementation started. In every case, the architectural questions (placement, ownership, scope) were genuinely settled — but real defects still surfaced once implementation began, in the mechanics the Q&A never asked about: mode symmetry (ST-000027, strict mode's missing bug-detection marker) and deployment-context executability (ST-000028, devkit-only paths that only fail once run outside the author's own tree). A closed Q&A thread is not evidence the design is complete for this class of gap.
- **Resume-rule branch sets keep lagging their own state-file's write rules.** ST-000028's `Loop Status: ended` gap is the same shape as ST-000026's Stage 5 gap, which TL's own memory already traces back to ST-000025. Three occurrences across three consecutive sprints of work, always caught in review, never caught by the implementer's own self-check or by `validate_templates.py`.
- **Enumerated lists (call sites, fix options) get treated as exhaustive.** Recurred twice in this sprint alone (ST-000026 CR-2, ST-000028's fix-menu) — TL named specific items, the implementer found more sharing the same mechanism.
- **A devkit-only-path defect class in injected templates is corpus-wide, not story-specific.** ST-000028 found not only its own instance (CR-1/CR-2) but also a second, pre-existing instance in `Sync_Devkit_Workflow_template.md` that no story was actively touching — meaning there are likely more such instances still undiscovered.

**Recurring blockers:** None that stopped a story — every finding above was caught during review/QA before merge, not after. The cost was round-trip cycles (1 CR round on ST-000026, 1 CR round on ST-000028), not lost work.

**What went well:**
- Independent, non-trusting re-verification (diffing the specific claimed-untouched text, re-deriving evidence rather than citing another role's claim, scaffold dry-runs comparing PR branch vs. `origin/main`) caught real gaps on every story it was applied to, with zero false alarms.
- Design-first pre-flight Q&A, even though it didn't cover mechanics, genuinely eliminated architectural rework — no story in this sprint needed a scope-level redo, only mechanism-level fixes.
- The non-behavioral/behavioral fast-path split worked as intended: ST-000027 (genuinely docs-only) cleared Stage 2–4 with zero agent spawns and zero rework; ST-000028 was correctly reclassified to behavioral mid-pipeline when a script file appeared in its diff, and that reclassification caught real defects a fast-path review would have missed.

**Top process improvements (this batch):**
1. **Applied — `Technical_Lead_Rules_template.md`:** resume-rule branch-completeness check, §N citation-accuracy check, and a fix/call-site-menu-not-exhaustive phrasing convention, targeting the two most-repeated findings above.
2. **Applied — `Shared_Pipeline_Stages_Shared_template.md`:** GitHub-mode closure-comment-ordering note, closing out a friction point first reported in community retro issue #76 and now confirmed live in this repo.
3. **Deferred to a new story (not a retro-batch edit):** widen `validate_templates.py`'s reference check past `.md` and scope it to the deployed-file inventory for anything under `templates/`, so the devkit-only-path defect class stops depending on a human reviewer catching it by hand. Flagged by TL as real engineering work with false-positive risk, not a same-shape rule tweak.
