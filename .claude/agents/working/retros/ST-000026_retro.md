# Retrospective — ST-000026
**Date:** 2026-07-28
**Story:** Roadmap stories must be drained into tracked backlog issues at authoring time

## Implementer — Developer
### Impediments & Unclear Points
- TL's decision comment pointed at "Product_Owner_Rules.md §11" as the roadmap-authorship point, but the template's actual section was §11 "Project Plan Commit" — a commit-mechanics section, not a roadmap-specific one. Had to infer the new content belonged in a new sub-section (§11a) rather than inside §11 itself; worked out fine but a story/decision that names an exact section number is worth double-checking against the live file before assuming it's a direct edit target.
- The story's Technical Scope named `Create_Stories_Workflow_Shared_template.md` as a possible touch point, but on inspection it's a user-driven interactive story-creation flow that never authors/updates a roadmap doc itself (it consumes one, at most) — so it was correctly out of scope per TL's actual decision list. Worth flagging explicitly in the PR/comment so reviewers don't assume it was missed.

### Process Suggestions
- Found an existing but previously-implicit convention (`**Roadmap Phase:** Phase N — <theme>` body line + `phase-N` label, already used in `Plan_Sprint_Workflow.md` Stage 4 and `Create_Stories_Workflow.md` Step 3) that satisfies AC2's "tagged with its roadmap phase" requirement — reused it instead of inventing a competing tagging scheme, and added a separate new `**Roadmap Source:**` marker line purely for the idempotency check (AC3/AC6), keeping the two concerns (human-facing tag vs. machine dedup key) distinct.
- The new Stage 5 drain step in `Build_Software_Workflow.md` sits between the per-repo doc-copy and the commit/push step, which introduces the same category of crash-window resume gap that already existed (and was already accepted/documented) for commit/push not re-running on resume. Extended the existing "Resume note" pipeline-rule bullet to cover the drain step too, rather than redesigning Stage 5's resume logic — consistent with the existing tolerance for this class of gap and avoids touching the Stage 4 resume invariant TL explicitly said not to reopen.

### What Worked Well
- The refine-sprint thread (TL Q1/Q2 answers, PO Q4 answer) left almost no ambiguity by the time implementation started — all three touch points (Product_Owner_Rules, Plan_Sprint Stage 1, Build Software Stage 3+5) and the idempotency marker format were already pinned down, so this was mostly a careful-execution task rather than a design task.

## Reviewer — Technical Lead
### Impediments & Unclear Points
- My own Q2 decision comment asserted that "Stage 5's resume rule is per-repo file-presence, which re-runs safely" — that premise is false as stated. The file-presence check only covers what Doc Copy steps 1–3 write, so a new step appended after step 3 is never reached on resume for a repo the check declares complete. A TL design answer that leans on an existing resume rule should quote the rule's actual skip condition and check what it covers, not paraphrase it from memory; I gave the implementer a guarantee the file doesn't make.
- The Developer's retro flagged that my decision comment cited `Product_Owner_Rules.md §11` when §11 is commit-mechanics, not roadmap authorship. Fair — I named a section number without opening the file. Same root cause as the point above.

### Process Suggestions
- The review checklist has no step for "the AC's mechanism is documented, but does the mechanism actually work against the real tool's semantics." Both CR-1 (query filters on `status:backlog`, so it can't answer "is this tracked at all") and CR-2 (GitHub phrase search matches a contiguous token subsequence, so a prefix-titled story is silently skipped) are cases where the prose is internally coherent and the shipped command does the wrong thing. For any story that introduces a `gh`/CLI query as a correctness mechanism, the reviewer should reason through at least one adversarial input against the tool's documented matching behaviour — not just confirm the flag syntax parses.
- Mode-parity is a cheap tell for this class of bug. In CR-1 the strict-mode branch (grep all story files, no status filter) and the GitHub branch (`--label status:backlog --state open`) answered different questions; the divergence between two branches of the same step pointed straight at which one was wrong. Worth making an explicit check whenever a step has github/strict branches.
- The ST-000025 lesson generalises further than I recorded it: a documented resume rule is only closed if the *instruction* changes, not if a warning is added next to it. Prose that says "this check does not confirm step N ran" while the rule still says "skip the repo" leaves the gap intact — an orchestrator follows the numbered rule.

### What Worked Well
- Placement, scoping and dual-update were all correct on the first pass — §11a in `Product_Owner_Rules` rather than only the consumption workflows, backstop in `Plan_Sprint` Stage 1 per PO, Stage 3 manifest / Stage 5 drain split, `Analyst_Workflow.md` and `Create_Stories` correctly excluded with the exclusion reasoning stated in the PR body. The refine-sprint thread did its job: every structural decision landed as designed, and the whole review reduced to mechanism correctness.
- The implementer proactively surfaced the Stage 5 crash-window rather than hiding it, which is what made CR-3 a one-line fix instead of a rediscovery. Flagging a known-imperfect area in the retro is worth more than a silent workaround, even when the chosen mitigation turns out to be insufficient.

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
