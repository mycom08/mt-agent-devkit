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
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

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
