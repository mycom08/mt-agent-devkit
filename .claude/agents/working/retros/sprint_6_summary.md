# Sprint 6 — Retro Summary
**Sprint:** sprint-6
**Last Updated:** 2026-07-30

---

## ST-000032 — Working Record: story-entry retention, file cap, rewrite-in-place, detection
**Date:** 2026-07-30
**Loop counts:** Impl→Reviewer: 0 | Impl→QA: 0

### Findings
- `[instruction]` Developer's spawn prompt cited `.claude/agents/working/scripts/validate_templates.py`; the real path is `scripts/validate_templates.py` — cost one failed invocation. *(Developer)*
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
- `.claude/agents/templates/shared/workflows/Shared_Pipeline_Stages_Shared_template.md` + working mirror `Shared_Pipeline_Stages.md` — GitHub mode closure-comment-ordering note rewritten from a prose warning into a mandatory `gh issue view --json state` pre-check with an explicit branch, since the prose-only version had already recurred once despite being documented. Applied directly, no version bump (devkit-internal reliability fix).
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
- `[failure]` Both original PR commits carried `[skip ci]`, including the feat commit touching `.claude/agents/templates/**` — the exact path this repo's CI validates. `Developer_Rules.md §6`'s docs-only-push rule (`.claude/agents/**` = non-code) is correct for target projects but mis-scoped when mirrored verbatim into the devkit's own working copy. CI never ran until the orchestrator's unrelated changes.json-merge commit (no tag) triggered it for real — recovered, but only incidentally. *(Orchestrator)*
- `[context]` No version bump this run, per explicit user instruction — files merged into the existing `"0.1.40"` `changes.json` entry instead of a new version key. *(Orchestrator)*

### What Worked Well
- Land-order coordination worked exactly as designed — the ST-000032 Stage 5 block was a clean append, no rebase conflict, same bullet-and-glob pattern reused verbatim (`s/working-record/memory/`, `s/4,000/10,000/`). *(Developer)*
- `validate_templates.py` ran clean on the first pass (3 pre-existing known issues, none touching the diff). *(Developer)*
- Non-behavioral fast path (Stage 2/3/4, no agent spawn) verified all 10 AC directly against the diff with no domain-knowledge gaps. *(Orchestrator)*

### Actions Applied
- None — user reviewed all 5 findings and judged none critical enough to act on now (the CI skip-ci item is the closest, but it's a repeat-risk for next time, not something broken this run). All left as observations only.
