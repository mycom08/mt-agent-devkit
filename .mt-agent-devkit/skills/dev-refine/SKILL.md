---
name: dev-refine
description: Developer sprint refinement task - fetch the sprint's backlog stories, find open points per story, post one question comment or an explicit cleared note per story, then review answers and confirm readiness. Load at spawn when the orchestrator asks for a Sprint Refinement.
---

# Dev Refine

**Requires:** `dev-core`, `comment` (before every comment), `raise-question` (who owns each question), `working-record` (step 4.4)

Task skill, only when the orchestrator asks for a Sprint Refinement.

## 1. Fetch Target Stories

1. Run `gh issue list --repo mycom08/mt-agent-devkit --label "sprint-N" --label "status:backlog" --state open`.
2. For each returned issue, read the full body: User Story, AC, Technical Scope.

## 2. Identify Open Points per Story

- Is every AC specific, testable and unambiguous? (scope or AC question → PO)
- Are implementation dependencies, design decisions or workflow questions left unanswered? (technical question → TL)
- Does an AC conflict with, or is it missing from, its context? (scope question → PO)
- **Step-positioning check:** an AC that places a step in a multi-step sequence only by its outer boundaries ("after X and before Z") while unnamed intermediate steps exist is ambiguous: raise it to PO.

## 3. Post Comments

1. **Open points:** post **one** issue comment per story in the `comment` format, `**Thread Status:** Open`, tagging the owners.
2. **No open points:** post an explicit **cleared note**: one comment stating the story was reviewed and no open points were found, `**Thread Status:** Resolved`, no agent tagged. Never leave a clear story silent: Stage 4 promotes on the presence of a comment, so a silent story stays `status:backlog`.

## 4. Review Answers and Confirm

After the orchestrator reports that TL and PO have answered:

1. Re-read each thread where you posted questions.
2. All answers clear: post "All open points resolved — story is ready for development. PO please move to ready." with `**Thread Status:** Resolved`.
3. An answer is insufficient: post a follow-up in the same thread.
4. Update your Working Record.
