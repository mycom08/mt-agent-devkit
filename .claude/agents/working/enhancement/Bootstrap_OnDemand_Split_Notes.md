# Bootstrap / Read-On-Demand Split — Session Notes

**Date:** 2026-08-21 · **Branch:** `agent-enhancement` · **Scope:** devkit's own team only (`.claude/agents/working/`); `templates/` and `.antigravity/` untouched.
**Follows:** `Agent_Common_Split_Findings.md` (issue #134 test round).

---

## The rule applied

One test, asked of every section: **is this needed at spawn, regardless of what the task is?**
Yes → bootstrap file, read in full. No → on-demand file, fetched only when a trigger fires.

This is a different axis from #123's, which asked *"does this apply to a rare scenario?"* — that axis silently assumed every spawn is a story spawn, so it could never reach story pre-start, PR gates, or git workflow. Under the new axis those are all conditional.

## What changed

| Was | Now |
|---|---|
| `Developer_Rules.md` (9,724) + `Developer_Rules_Extended.md` | `Developer_Rules_Bootstrap.md` (3,566) + `Developer_Rules_Read_On_Demand.md` |
| `Agent_Common.md` | `Agent_Common_Bootstrap.md` |
| `Agent_Common_Records.md` | `Agent_Common_Read_On_Demand.md` |
| `Project_Priming.md` (11,540) | `Project_Priming_Bootstrap.md` (6,110) + `Project_Priming_Read_On_Demand.md` |

`Extended` and `Read_On_Demand` were the same tier under one test — both answer *no* to "needed at spawn?" — so Dev has one on-demand file, not two.

**Numbering is never reused.** Retired numbers (`Developer_Rules` §9–§11, `Agent_Common_Read_On_Demand` §4 and §7) are left as gaps so a stale citation resolves to *nothing* rather than silently to a different rule. `Developer_Rules_Extended` §1–§6 became §12–§17 for the same reason.

## The load-bearing fix was a citation, not a split

`Agent_Common.md` was already ~90% bootstrap content. What made a live Dev spawn read only 3,236 of 9,966 chars was that all six instruction files said *"Follow the read sequence in `Agent_Common.md §1`"* — a **section** citation, which §3 rule 4 then correctly told the agent to satisfy with `read-section`. The agent obeyed two rules and still skipped Secret Handling and External Content Handling.

Fixed by: instruction files now cite the **file** and say "read in full"; the file header names the exact failure; §3 rule 4's carve-out is closed for `*_Bootstrap.md` files.

**Generalisable:** a section citation is an instruction to section-read. Never cite `§N` of a file you need loaded whole.

## Token result: flat. This did not save tokens.

| Measured against | Bootstrap chars |
|---|---|
| Nominal baseline (what the rules *said* to read) | 40,640 |
| **Actual** baseline (what run 1 *really* read) | **33,910** |
| After the split (run 2, all mandated files read in full) | **33,638** |

Self-reported pre-work: ~7,360 tok (run 1) vs ~7,300 tok (run 2).

Quoting the 40,640 figure as the "before" would repeat the error `Agent_Common_Split_Findings.md` §2 warns about — run 1's apparent cheapness *was* the skipped safety sections. **What this bought is compliance at unchanged price, not a saving.**

It is also task-shape dependent, and loses on the path we run most:

| Task shape | `Developer_Rules` cost | vs. old 9,724 |
|---|---|---|
| Full story spawn (triggers §1–§6) | 11,206 | **+1,482 (+15%)** |
| Narrow non-story task | 3,566 | −6,158 (−63%) |

Every measurement this session was a non-story task — the shape the split favours. **The clean experiment (same story, pre- and post-split, as #123 ran) has not been done.**

## The finding that outlives the token question

**Being in context is not being consulted.**

Token-trace `§6` was moved into the bootstrap tier so agents carry the format from step 2. Run 2 confirmed the mechanical win: **zero** search calls to locate it, where run 1 burned three. But the trace it produced declared a total of 18,200 against step values summing to 18,700 — and asked directly, Dev said it never added them, and never re-read §6 at all:

> "I wrote the trace from the shape I had absorbed... §6 sat in context, unused, for nineteen steps."

The error signature confirms it: recalled format reproduces **structure** faithfully (every header field, every `approx` label, orchestrator's field left blank) and degrades on the **literal** bits — one word, `sum`. Those you only get right by looking. The same mechanism corrupted a file that turn: Dev edited from a remembered copy without re-reading.

**Bootstrap placement guarantees loading, not application.** Moving more text into bootstrap will not close that gap. Co-locate an obligation with the act that needs it, or verify mechanically.

## Open items

- **Not measured properly.** Three spawns, self-reported; JSONL transcript wrote **0 bytes all three times** (reproducible harness limitation — run 2 in `Agent_Common_Split_Findings.md` hit it too). Read sets are corroborated only by behavioural tells.
- **`subagent_tokens` semantics unresolved.** Rounds reported 70,652 / 77,975 / 77,274 — round 3 made 0 tool calls and came in *lower*, so it is neither per-call nor strictly cumulative. Do not derive from it. See `token-trace_sprint/gitignore_audit_dev_steps_done.md`.
- **Five roles unsplit.** TL/QA/PO/BA/UI-UX still read their full `*_Rules.md`; TL/QA/PO still have inconsistently-named `*_Rules_Extended.md`.
- **Bootstrap gate still unenforced** — carried over from `Agent_Common_Split_Findings.md`; nothing detects a skipped read.
- **`.antigravity/` gitignore gap** (found by the run-2 audit, independently verified): 12 runtime files are committed — 6 working records, 6 token traces. Root `.gitignore` anchors every runtime rule to `.claude/…`, but `README.md:3` makes `.antigravity/` a supported agent root. Fix: add the three `.antigravity/…` prefixes and `git rm --cached` the 12. **Needs a story.**
- **`Agent_Common_Read_On_Demand.md` §5 is overbroad** — "never commit any file under `working/` other than memory files" is literally false (69 tracked there, incl. 10 retros); true only within stage-transition scope. Needs a scope word.
- **Dangling `Repo Roster` reference** in `Agent_Common_Bootstrap.md §4` — still unresolved from the prior round.
