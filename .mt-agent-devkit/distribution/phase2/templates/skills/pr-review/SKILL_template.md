---
name: pr-review
description: Peer review procedure - locate the PR, read the diff, confirm CI actually ran on the current head SHA, review criteria, inline change requests, the issue notify comment and the verdict through gh pr comment with the gh pr checks paste. Load when assigned as a reviewer.
---

# PR Review

**Requires:** `comment` (before any comment), `pre-pr-gate` (the checks you verify), `credential-gate` (credential evidence)

TL keeps its approval authority (the merge gate, design compliance) in its own rules; this skill is the shared reviewer procedure. **Strict mode** has no PR: review the story file's change record and post the verdict as a story comment entry.

## Steps

1. **Locate the work.** Open the story issue and find the PR in its Deliverables or linked pull requests. If none is linked, ask the implementer to link it first.
2. **Read the diff:** `gh pr diff <number> --repo {github-org}/{repo-name}`.
3. **CI gate (before any verdict).**
   - Pending CI routes to `.mt-agent-devkit/contracts/Wait_Work.md` (ci-watch); keep its wait ID and native command/session identity. PENDING never advances review or merge; FAIL/cancel/timeout routes to fixes. NO RUN uses the explicit zero-check evidence gate, never automatic PASS. After waiting, revalidate the exact head and approval scope.
   - Every check has **finished** and none **failed**.
   - Open the job log and confirm the check **actually executed**, not just its conclusion; a run that died at dependency resolution is a different failure, not proof either way.
   - The cited run's head SHA equals the PR's current head SHA; a result from an older commit, or no run for the latest one, is "no confirmed CI result".
   - Diagnose a red required check from its actual failing step and log, never from the PR's explanation.
4. **Review criteria.**
   - Naming conventions (`clean-code`), commit message format, test coverage and the `pre-pr-gate` checks. Commit subject-line **length** is a non-blocking nit: comment on it, never request changes over it alone.
   - Obvious logic errors, missing error handling at system boundaries and security issues; each AC-specified behavior is implemented.
   - No stale references: paths, section numbers and placeholder names.
   - Deleted or renamed files are absent from the branch tree (`git ls-tree` on the PR branch), and the old path string is grepped for in the files the story updates.
   - Stub/TODO re-check: stub markers and trivial-return patterns in AC-functional methods were scanned; a hit with no owning backlog story blocks approval.
   - No dummy-value or analogy substitute for a credential-gated check (`credential-gate`).
5. **Change requests.** Post each as an inline PR comment with enough detail to act on. Phrase named files or call sites as "at minimum these, plus any site sharing the same pattern".
6. **Notify on the issue** (approving or not):
   ```
   ## PR #NNN peer review — <Approved | Changes Requested>
   **Thread Status:** Open | Resolved
   **Area:** Implementation

   **<Role> - YYYY-MM-DD**
   <Summary of findings or approval rationale>

   **Next:** <implementer> to address CR items | None
   ```
7. **Verdict** with `gh pr comment`, never `gh pr review --approve` (GitHub blocks self-approval). An approval carries the literal `gh pr checks <PR-number>` output (the `comment` skill's single transcript carve-out).
