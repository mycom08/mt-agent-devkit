# Sprint 6 — Retro Summary
**Sprint:** sprint-6
**Last Updated:** 2026-07-31

---

## ST-000032 — Working Record: story-entry retention, file cap, rewrite-in-place, detection
**Date:** 2026-07-30
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[instruction]` Developer's spawn prompt cited `.antigravity/agents/working/scripts/validate_templates.py`; the real path is `scripts/validate_templates.py` — cost one failed invocation. *(Developer)*
- `[failure]` Developer began editing files before creating the story branch and flipping the status label, contrary to the mandatory branch-before-first-file order in their own rules. No harm resulted (self-corrected before the first commit). *(Developer)*
- `[context]` Stale `sprint_pipeline_state.md` from ST-000028 (sprint-5) was still present at the start of this run — Retro Review step 6 ("delete the state file") had been skipped on that story. Verified #84 closed and folded into `sprint_5_summary.md`, then removed. *(Orchestrator)*
- `[context]` Refine run this sprint was scoped to ST-000032/ST-000033 only; ST-000030 (#93) and ST-000031 (#94) remain `status:backlog`. *(Orchestrator)*
- `[workflow]` 3 improvement candidates carried over unactioned from the ST-000032/033 refine's Stage 4 review: AC boilerplate "applied to both github and strict variants" is structurally impossible for split workflow files (3rd occurrence); size caps on agent artifacts should be stated in characters not lines (now resolved by this story); the six roles' §1 pre-start sections are structurally divergent, making corpus-wide AC expensive to verify. *(Orchestrator)*
- `[failure]` Orchestrator combined `gh issue close --comment` on issue #95, which GitHub had already auto-closed via the merged PR's `Closes #95` — the combined call errored and silently dropped the comment, the exact failure mode `Shared_Pipeline_Stages.md` already warned about in prose. Recovered via a separate `gh issue comment` call. *(Orchestrator)*

### What Worked Well
- Refinement thread resolved every open design question (stage positioning, char-vs-line cap, file-set scope) before Stage 1 started — implementation was a direct translation of TL/PO decisions with zero mid-implementation consultations. *(Developer)*
- The intentionally-diverged-mirror pattern (`Project_Priming` §15) applied cleanly to the devkit's own `Shared_Pipeline_Stages.md` Observation Check bullet — the devkit's working-record path differs from the target-project scaffold path, and the existing carve-out rule made that divergence expected rather than drift. *(Developer)*
- Non-behavioral fast path (Stage 2/3/4, no agent spawn) verified cleanly against the diff and Technical Scope with no domain-knowledge gaps — all 10 AC confirmed directly. *(Orchestrator)*

### Actions Applied
- `.antigravity/agents/templates/shared/workflows/Shared_Pipeline_Stages_Shared_template.md` + working mirror `Shared_Pipeline_Stages.md` — GitHub mode closure-comment-ordering note rewritten from a prose warning into a mandatory `gh issue view --json state` pre-check with an explicit branch, since the prose-only version had already recurred once despite being documented. Applied directly, no version bump (devkit-internal reliability fix).
- Wrong `validate_templates.py` path in Developer's spawn-prompt reference — not applied; user did not select it this round.
- Developer branch-before-first-file sequencing — not applied; treated as a one-off execution slip, not a missing rule.
- 3 carried-over workflow items (AC boilerplate impossibility, structurally divergent §1 sections) — not applied; deferred again.
- Stale pipeline-state-file pattern — not applied; no rule change proposed, noted as a recurring risk.

---

## ST-000033 — Agent memory: purpose test, file cap, scheduled prune, detection
**Date:** 2026-07-30
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[context]` The pruning-schedule AC referenced "existing sprint-end cleanup" without naming a file — Developer had to grep for `Sprint_Workflow.md`'s "Sprint end" sequence rather than follow a pointer. *(Developer)*
- `[context]` No refinement-thread decision existed for exactly where the once-per-sprint pruning step should live (unlike the other 5 AC points, all resolved with worked examples) — Developer made a judgment call: new "Sprint-End Memory Pruning" section in `Retro_Rules.md` + a new step in `Sprint_Workflow.md`'s Sprint-end sequence. *(Developer)*
- `[workflow]` When a design-first refinement thread resolves most but not all AC points explicitly, flag the remaining point(s) so the implementer knows a judgment call is expected there rather than assuming full thread coverage. *(Developer)*
- `[failure]` Both original PR commits carried `[skip ci]`, including the feat commit touching `.antigravity/agents/templates/**` — the exact path this repo's CI validates. `Developer_Rules.md §6`'s docs-only-push rule (`.antigravity/agents/**` = non-code) is correct for target projects but mis-scoped when mirrored verbatim into the devkit's own working copy. CI never ran until the orchestrator's unrelated changes.json-merge commit (no tag) triggered it for real — recovered, but only incidentally. *(Orchestrator)*
- `[context]` No version bump this run, per explicit user instruction — files merged into the existing `"0.1.40"` `changes.json` entry instead of a new version key. *(Orchestrator)*

### What Worked Well
- Land-order coordination worked exactly as designed — the ST-000032 Stage 5 block was a clean append, no rebase conflict, same bullet-and-glob pattern reused verbatim (`s/working-record/memory/`, `s/4,000/10,000/`). *(Developer)*
- `validate_templates.py` ran clean on the first pass (3 pre-existing known issues, none touching the diff). *(Developer)*
- Non-behavioral fast path (Stage 2/3/4, no agent spawn) verified all 10 AC directly against the diff with no domain-knowledge gaps. *(Orchestrator)*

### Actions Applied
- None — user reviewed all 5 findings and judged none critical enough to act on now (the CI skip-ci item is the closest, but it's a repeat-risk for next time, not something broken this run). All left as observations only.

---

## refine sprint — ST-000035 (#100) / ST-000036 (#101)
**Date:** 2026-07-30
**Loop counts:** #100: 1 | #101: 0 (clear at Stage 1, no loop)

### Findings
- `[failure]` Stage 4's promotion rule had no branch for a story clear at Stage 1. Stage 1 step 7 said a story with no open points gets NO comment, so it matched Stage 4's "no final comment -> leave as status:backlog" branch and could never be promoted. Only the All-Clear Shortcut (every story clear) covered it; a mixed run like this one -- #100 with questions, #101 clear -- fell through. #101 reached `status:ready` anyway, but not by rule. *(Orchestrator)*
- `[workflow]` `Technical_Lead_Rules.md §2` says to update the story body AC when an answer narrows its meaning, but the Stage 2 spawn prompt forbids editing the issue body. The two conflict; §2 should state the refinement-stage exception (PO owns body edits at Stage 2 step 5). *(Technical Lead)*
- `[workflow]` TL branched off `main` and committed to satisfy the no-work-on-main rule, orphaning a commit unrelated to any story implementation. Refine Stage 2 produces comments only -- the workflow should say no branch or commit is expected at this stage. *(Technical Lead)*
- `[workflow]` Agents committing files they own mid-refinement splits unrelated in-flight work across branches. Resolved by fast-forwarding `main`. Worth a Pipeline Rule that Stage 2 agents do not commit. *(Orchestrator)*
- `[context]` User scoped this run to #100/#101 only, not the full sprint-6 backlog (#93/#94/#98/#102 excluded) -- same narrowing precedent as the #95/#96 run. *(Orchestrator)*

### What Worked Well
- Per-story independence held: #101 was clear at Stage 1 and did not wait on #100's question loop.
- One Impl->TL/PO cycle on #100 was enough; no escalation to the 3-loop limit.

### Actions Applied
- Stage 4 promotion gap -- **applied** (commit `67d3204`, before this retro was written). Stage 1 step 7 now requires an explicit cleared note through the same channel as step 6; the All-Clear Shortcut is retested on question-presence rather than comment-presence; Stage 4 names both promote paths. Shared template + devkit working copy, folded into the existing `0.1.40` changes.json entry, no version bump.
- Remaining 4 findings -- **not applied**; user reviewed and judged none critical. The TL-rule contradiction resolves safely in practice (spawn prompt is the narrower instruction, worst case is a TL that pauses to ask); the branch/commit pair cost real cleanup but was fully recoverable via fast-forward; the scoping item is an observation with no rule change proposed. Left as observations only.

---

## ST-000035 — Audit agent files workflow (devkit-only, Tier A detection)
**Date:** 2026-07-30
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[failure]` CI's green badge covered `Layer-1 invariant check` but its default `SCAN_DIRS` never reaches `working/`, giving zero evidence for the story's largest new file (`Audit_Rules.md`) — TL had to run the AC-mandated explicit-path validator manually to get real coverage. *(Technical Lead)*
- `[failure]` A non-worktree differential validator run undercounted violations by 14 (53 vs. the true 67) because gitignored `working-record/*.md` files on disk skew the count versus a clean worktree. *(QA)*
- `[workflow]` The differential-gate-needs-both-sides-diffed lesson was independently rediscovered by both TL (corrected round 1's "~70" to 67) and QA (found the actual undercount bug behind it) — a structural gap in method, hit twice in one story, not a fluke. *(Technical Lead, QA)*
- `[instruction]` AC phrase "added to the trigger table" was ambiguous about which of `CLAUDE.md`'s three candidate tables — resolved by precedent-matching sibling commands, no story-blocking question needed. *(Developer)*
- `[workflow]` A story introducing a new gitignored runtime-output directory should prompt the implementer to check `validate_templates.py`'s `RUNTIME_PATH_PREFIXES` — caught this run only because Developer Memory Fix 1 already documented the pattern. *(Developer)*
- `[workflow]` A size-gated digest-subagent rule (`Agent_Common.md §9.6`) added mid-sprint needed a carve-out (never digest the AC/body contract, only discussion) before a live A/B test (two independent TL review passes of the same PR, gate on vs. off) proved the whole mechanism a net token cost, not a savings — prompt caching makes same-session raw reads cheaper than subagent isolation. Rule removed outright rather than kept disabled. *(Orchestrator, Technical Lead)*

### What Worked Well
- Design-first was fully satisfied by the issue thread itself before Dev ever spawned — zero mid-implementation consultations across Developer, both TL rounds, and QA. *(Developer, Technical Lead, QA)*
- Re-deriving AC from live branch/file content rather than diff hunks or a prior role's verdict caught absence-type criteria a hunk-only read can't establish, independently at every stage. *(Technical Lead, QA)*
- Non-blocking nits were phrased as an open "at minimum these" list rather than a closed inventory, keeping the follow-up bucket honest for ST-000036. *(Technical Lead)*

### Actions Applied
- `.antigravity/agents/working/workflows/Shared_Pipeline_Stages.md` — Stage 1 spawn-prompt reminder: name only the role-scoped Story Standard variant, never offer the full cross-role file as an alternative. Committed `37e6241`.
- `.antigravity/agents/working/rules/Agent_Common.md` §9 — corrected preamble (prompt caching makes same-session repeats cheap; session fragmentation, not read size, is the real cost driver); the `§9.6` digest-gate rule this same session had added was removed outright after the live A/B test showed it cost more, not less. Committed `37e6241`.
- `.antigravity/agents/working/memory/QA_Memory.md` Fact 2 — corrected to require worktree-vs-worktree checkouts for every differential validator run. Applied by QA directly, pushed as part of PR #103.
- Remaining findings (CI scan-gap as a standing rule, worktree-required as a *shared* rule beyond QA's own memory, story-authoring table-heading clarity, runtime-dir PO-side checklist reminder) — **not applied**; user reviewed all four and judged none critical enough to act on now, including the two flagged as closest to critical (CI scan-gap, worktree-required gate). Left as observations only.

---

## ST-000037 — Inject Auditor into target projects + wire sync devkit / update project audit stage
**Date:** 2026-07-31
**Loop counts:** Impl→Reviewer: 1 | Impl→QA: 0

### Findings
- `[failure]` Round 1 review CHANGES REQUESTED on one finding: adding a 20th rules file rippled into a deployed-template scaffold enumeration (`Refine_Prototype_Workflow_Shared_template.md`) that neither the AC, the implementer's own ripple memory, nor the reviewer's own refinement-thread scope answer had named — same defect class as ST-000022/ST-000023, now a 3rd occurrence. *(Technical Lead)*
- `[workflow]` Three roles (Developer, Technical Lead, Product Owner) independently flagged the same gap: `Project_Priming.md §15a` has a ripple checklist for "Nth agent role" but nothing for "Nth enumerated set" (rules files, workflow files) — both implementer and reviewer currently reconstruct that inventory from personal memory files, which is why the same 1-2 sites get missed each time. *(Developer, Technical Lead, Product Owner)*
- `[workflow]` Reviewer suggestion: for enumeration-ripple stories, grep the corpus for the old count/signature terms first, before verifying the story's actual design content — inverts the default review order for this story class. *(Technical Lead)*
- `[workflow]` The standard round-2 scoping recipe (`git diff <round1-head> <round2-head> --stat`) overstates the implementer's work when the reviewer's own stage-transition commit lands between rounds — should diff from the reviewer's own last commit instead. *(Technical Lead)*
- `[workflow]` AC4/AC5's scoped-file-list description read like unbacked prose until traced to three pre-existing mechanisms already in the target file — a general habit worth applying to any AC whose correctness rests on a described-but-not-visibly-implemented runtime log. *(QA)*
- `[skipped-step]` Orchestrator did not refresh the pipeline state file's `Updated` timestamp at every stage transition (only `Stage` was kept current) — harmless here, real process gap. *(Orchestrator)*

### What Worked Well
- Refinement (Dev/TL/PO thread on #102) was thorough enough that zero new mid-implementation or QA-time AC questions arose across the whole pipeline. *(Developer, Product Owner)*
- "Is this scope an actual mechanism or just prose?" as the primary review question paid off — the new audit stage's scoped-file-list, which looked like the likeliest spot for unbacked hand-waving, held up because it rested on three pre-existing mechanisms in the file. *(Technical Lead, QA)*
- Verifying a cited precedent (ST-000022/ST-000023) against the actual CHANGELOG entries, not the citation, is what exposed that the precedent covered only devkit-internal ripple sites — the same operation that found the gap also confirmed what it didn't cover. *(Technical Lead)*
- QA's independent re-derivation of all 14 AC plus a two-mode scaffold-output regression diff gave high closing confidence with zero regressions. *(QA, Product Owner)*

### Actions Applied
*(none — user reviewed all 3 proposed items (§15a enumeration-ripple checklist, reviewer grep-first checklist, TL Memory Fact 9 round-2 diff-recipe fix) and deferred applying any of them this round; left as recorded observations for a future pass.)*
