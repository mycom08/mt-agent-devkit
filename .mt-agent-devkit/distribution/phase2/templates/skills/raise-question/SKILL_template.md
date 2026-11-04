---
name: raise-question
description: Questions and blockers for every implementer - who owns a question (PO or TL), the pre-start question gate, the mid-implementation consultation report, posting blockers and live user instruction conflicts. Load when a question or blocker comes up.
---

# Raise Question

**Requires:** `comment` (before posting any comment)

**Strict mode:** every "issue comment" below is a comment entry in the story file's `## Comments` section (`comment`), tagging the same roles.

## 1. Who Owns the Question

- Scope, AC or flow question → **PO**
- Technical or design question → **TL**
- Both → **PO + TL**

Never assume or invent an answer, and never answer a scope question PO owns.

## 2. Before Starting a Story (pre-start gate)

1. After reading the story, its comments and every file it touches, list anything unclear: scope gaps, ambiguous AC, technical design uncertainties.
2. Post the questions as an issue comment, explicitly tagging the owner from section 1. Post non-blocking questions too; they need no answer before you proceed.
3. Read the PO/TL answers. If they are insufficient or raise a new concern, reply in the same thread, tag again and wait.
4. **Gate:** do not begin implementation until every blocking question has a confirmed answer from PO or TL.

## 3. Mid-Implementation Consultation

Use this for a genuine ambiguity (unclear AC, scope ambiguity, technical decision point) where a judgment call would affect scope or design. Do not use it for implementation details you can reasonably decide yourself. Do NOT use the Blocked Story Procedure and do NOT ask the user.

1. Identify the owner (section 1).
2. Post an issue comment tagging the owner(s):
   ```
   **Mid-implementation question — [TL / PO / both]**
   <specific question — one clear sentence>
   **Decision needed:** <what answer would unblock you>
   ```
3. Report back to the orchestrator:
   ```
   Mid-implementation consultation needed — ST-XXXXXX
   Owner: <TL / PO / both>
   Question: <same question as posted on issue>
   Decision needed: <same decision needed>
   Implementation paused at: <brief description of where you stopped>
   Question recorded on story: posted
   ```
4. Do NOT change the story label. The orchestrator spawns or resumes TL and/or PO to answer in the issue thread, then resumes you with their response.
5. When resumed with the answer: read it, apply it, and continue from where you paused.

## 4. Blockers

Post a blocker immediately as an issue comment, tagging the role that can unblock it: TL or PO for a Developer or UI/UX Designer, Dev or TL for QA, BA or PO for TL.

## 5. Live User Instruction Conflicts

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread (by PO, TL or the user), the live instruction takes precedence. Acknowledge the conflict (the prior decision and the new instruction), proceed with the live instruction, and document the override in the PR description. Do not silently follow the old decision or block awaiting re-confirmation.
