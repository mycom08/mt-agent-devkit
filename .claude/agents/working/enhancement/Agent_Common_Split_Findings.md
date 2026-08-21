# Agent_Common Split — Test Findings

**Scope:** commit `6d4dc48` (issue #134), branch `agent-enhancement`, devkit team only.
**Method:** two live Developer spawns on non-story tasks. Run 1 verified against the subagent transcript; run 2 self-reported (transcript came back empty).
**Date:** 2026-08-21

---

## 1. The bootstrap gate is not enforced

Both runs skipped mandatory `Agent_Common.md §1` reads, despite every path being named in the spawn prompt.

| Run | Read | Skipped |
|---|---|---|
| 1 | instructions, `Agent_Common.md`, `Agent_Common_Records.md` | Priming, Working Record, Rules, Memory |
| 2 | instructions, Rules, Memory, `Agent_Common_Records.md` (§1+§8) | Priming, Working Record, **`Agent_Common.md`** |

Neither run wrote a session-start Working Record entry. Nothing detected either defection — run 1 surfaced only because it was asked directly.

**Consequence:** "the bootstrap tier is always loaded" is an assumption, not a fact. #134's safety argument for keeping Secret Handling always-loaded rests on it.

**Cause:** `Agent_Common.md §1`'s only escape hatch names PO and forwards to role instructions that define no reduced set. With no sanctioned lane for read-only/no-story tasks, agents improvise one.

## 2. Reported savings are mostly non-compliance

Run 2, measured from actual byte ranges (~4 chars/token):

| Source | ~Tokens |
|---|---|
| Saved by bounded reading (the split) | 1,987 |
| "Saved" by skipping mandatory reads | 6,001 |

Bounded reads work where used: `Agent_Common_Records.md` cost 1,517 tok across three bounded calls vs 3,504 full (−57%). But enforce the gate and the run costs ~6,000 tok more — 3× what the split saved. **Do not cite spawn-cost reductions from these runs as evidence for the split.**

Largest compliant waste: `Developer_Rules.md`, 2,431 tok, self-assessed as changing nothing on a drafting task.

## 3. The routing table is not the active mechanism

Run 2 never opened `Agent_Common.md`, so `§5`'s routing table played no part. It reached §1 and §8 via `developer_instructions.md:35`'s direct pointers.

**Consequence:** per-role instruction pointers carry the split; the central table is currently bypassed on this path. Routing changes must land in the instruction files to take effect.

## 4. The `read-section` skill is not being used

Run 2 rolled its own `grep -n "^#\{1,3\} "` + offset/limit reads instead of invoking the skill — on the one file that is the skill's own worked cautionary case. It avoided §1's truncation by eyeballing the heading list, not by tooling.

**Consequence:** the `SKILL.md` boundary fix is **untested**. §1 came through whole by luck of the agent's own grep pattern.

---

## Open items

- **Bootstrap enforcement (parked).** Options: (a) require completion reports to list files read; (b) sanction a reduced-read lane for read-only/no-story tasks; (c) orchestrator inlines bootstrap content into spawn prompts — newly viable at ~2,300 tok post-split.
- **Validator blind spot.** `validate_templates.py` `SCAN_DIRS` excludes `.claude/agents/working/` and `.claude/skills/`; `SECTION_REF_ALIAS` maps `Agent_Common` to the unsplit template path and lacks `Agent_Common_Records`. A clean run is no evidence for changes in those trees. Declined for now.
- **Dangling reference.** `Agent_Common.md §4` cites "the Repo Roster"; no such section exists in the devkit's `Project_Priming.md`. Needs a content decision.
