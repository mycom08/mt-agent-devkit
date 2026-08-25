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
- **TL/PO/QA's split predates this axis and hasn't been redone — all three now renamed (2026-08-24).** They each had a `*_Rules_Extended.md`, but it was built under issue #123's older, narrower test — *"does this apply to a rare scenario?"* (e.g. TL/QA acting as story implementer) — which silently assumes every spawn is a story spawn and so never questions story pre-start / PR-gate / git-workflow content. **TL** ("TL rename pass" below), **QA** ("QA rename pass" below), and **PO** ("PO rename pass" below) were each verified against the new axis and found to already satisfy it — every existing split isolates only genuinely rare scenarios (TL: acting as implementer, context anchoring; QA: acting as implementer, post-Done hotfix; PO: story closure, sprint refinement, plan-next-sprint, roadmap drain, story creation). All three were renamed to `_Bootstrap.md`/`_Read_On_Demand.md` and given a routing table. TL and QA additionally needed new "otherwise skip" instructions-file blocks (they had none); **PO's instructions file already had this flagging before the rename** — it was the one role that predates #123 doing this part right, so PO's pass was rename + citation-fix only. None of the three have been benchmarked (only Developer spawns were measured — `Bench_2026-08-21_Findings.md`, `Bench4_2026-08-24_Findings.md`); none of the three passes made a token-savings claim for exactly this reason. This item is now closed for naming/flagging parity; content-boundary re-examination (e.g. whether any bootstrap-tier section is actually rare enough to move) remains unmeasured and open, same caveat as Dev's own split.
- **`.antigravity/` TL/QA/PO rules mirrors now drift on filename, not just content — created by this pass.** `.antigravity/agents/working/rules/Technical_Lead_Rules.md`, `QA_Rules.md`, `Product_Owner_Rules.md` still exist under their pre-rename names with no `_Bootstrap`/`_Read_On_Demand` split at all; the `.claude/` originals were renamed out from under them. This is the same class of drift the TL rename pass's own scope note already accepted for Dev (`.antigravity/` untouched, "templates/ and .antigravity/ untouched" — see this file's header), but it's now visibly a *structural* mismatch (missing files, not just stale content), not merely stale prose. **Needs a decision** — sync the mirrors now, or batch it with whatever eventually handles BA/UI-UX — not a silent mechanical copy.
- ~~**BA/UI-UX unsplit.**~~ Closed 2026-08-25 — see "BA/UI-UX split pass" below.
- **`Story_Standard_PO.md` is on-demand while its Dev/TL/QA counterparts are bootstrap — looks unintentional.** `Story_Standard_Dev.md`/`Story_Standard_TL.md`/`Story_Standard_QA.md` are each mandatory pre-start reads (gated in `Developer_Rules_Bootstrap.md §1`, `Technical_Lead_Rules_Bootstrap.md §1`, `QA_Rules_Bootstrap.md §1`). `Story_Standard_PO.md` is not in PO's Pre-Work Checklist at all — `product_owner_instructions.md` only says "When writing or managing stories, also read Story Standard (PO)," making it conditional. Nothing explains why PO's is less "needed at spawn" than TL's/QA's. Separately, the shared `Story_Standard.md` (no role suffix) is on-demand for every role, always accessed by section citation (§4/§8/§9/§12) and never read whole — that part looks deliberate, just worth stating explicitly since it's not written down anywhere. **Fix later:** decide whether `Story_Standard_PO.md` should move to PO's Pre-Work Checklist (bootstrap, matching Dev/TL/QA) or whether Dev/TL/QA's should move to on-demand instead — don't leave the asymmetry unexamined.
- **Bootstrap gate still unenforced** — carried over from `Agent_Common_Split_Findings.md`; nothing detects a skipped read.
- **`.antigravity/` gitignore gap** (found by the run-2 audit, independently verified): 12 runtime files are committed — 6 working records, 6 token traces. Root `.gitignore` anchors every runtime rule to `.claude/…`, but `README.md:3` makes `.antigravity/` a supported agent root. Fix: add the three `.antigravity/…` prefixes and `git rm --cached` the 12. **Needs a story.**
- **`Agent_Common_Read_On_Demand.md` §5 is overbroad** — "never commit any file under `working/` other than memory files" is literally false (69 tracked there, incl. 10 retros); true only within stage-transition scope. Needs a scope word.
- **Dangling `Repo Roster` reference** in `Agent_Common_Bootstrap.md §4` — still unresolved from the prior round.

## 2026-08-24 — TL rename pass

Applied the Dev naming/flagging pattern to Technical Lead only (QA/PO deferred to separate passes, at the user's request). Scope was deliberately narrow — **mechanical parity, not a content re-split**:

- Verified `Technical_Lead_Rules_Extended.md`'s own header against the new axis before touching anything: it explicitly states §2 Code Review/PR-gate content was *not* moved because it's "the reason TL exists on most spawns." That already matches Dev's own converged conclusion (`Developer_Rules_Bootstrap.md` v2.0: common-path content — a full story spawn's §1–§6 — belongs in bootstrap; only genuinely rare/task-specific content earns on-demand). So no section was moved or renumbered.
- Renamed `Technical_Lead_Rules.md` → `Technical_Lead_Rules_Bootstrap.md` and `Technical_Lead_Rules_Extended.md` → `Technical_Lead_Rules_Read_On_Demand.md` via `git mv`. All `§N` numbers preserved — only filenames changed, so every existing citation needed a name swap, not a renumber.
- Added `Technical_Lead_Rules_Bootstrap.md §15`, a routing table mirroring `Developer_Rules_Bootstrap.md §18`.
- Closed the specific gap the open item named: `technical_lead_instructions.md` previously had no mention of the on-demand file anywhere in its Pre-Work Checklist — the only pointers lived inline inside the base rules file. Added two explicit "otherwise skip" task blocks ("When Acting as Story Implementer", "Context Anchoring") matching PO's/Dev's instructions-file pattern.
- Fixed every citation of the old filenames on a **living** path: `Shared_Pipeline_Stages.md`, `Story_Standard_TL.md` (×3), `Story_Standard.md`, `Developer_Rules_Read_On_Demand.md`, and `Technical_Lead_Memory.md` (the live index only).
- **Left untouched, deliberately:** `Technical_Lead_Memory_Archive.md` and the sprint retro files that cite the old filename — these are point-in-time records; rewriting them would falsify history. Also untouched: `Sync_Devkit_Workflow.md`'s two references — those name the *distributable* `.claude/agents/templates/rules/Technical_Lead_Rules.md`, a different, unsplit file on a different surface (target-project sync), out of scope per this notes file's own header.
- **No token-savings claim.** Content didn't move, so there's nothing to measure here — this pass buys citation/discoverability parity with Dev, not a cheaper spawn. A real content re-split (e.g. whether TL's §6 Document Placement or §10 Reporting deserve on-demand treatment) is separate work, flagged but not attempted.

## 2026-08-24 — QA rename pass

Same treatment as the TL pass above, applied to QA. Mechanical parity, not a content re-split:

- Verified `QA_Rules_Extended.md`'s own header before touching anything: the three relocated sections (Pre-PR Gate as Implementer, Live User Instruction Conflicts, post-Done Hotfix) are each explicitly scoped to a rare scenario (QA acting as Implementer, or a post-Done bug) — QA's common path (validating AC, regression checks, sign-off) already stayed in the base file. Matches the axis on inspection; no section moved or renumbered.
- Renamed `QA_Rules.md` → `QA_Rules_Bootstrap.md` and `QA_Rules_Extended.md` → `QA_Rules_Read_On_Demand.md` via `git mv`. All `§N` numbers preserved.
- Added `QA_Rules_Bootstrap.md §14`, a routing table mirroring `Developer_Rules_Bootstrap.md §18` and `Technical_Lead_Rules_Bootstrap.md §15`.
- Closed the same instructions-file gap as TL's pass: `qa_instructions.md` previously had zero mention of the on-demand file. Added two "otherwise skip" blocks ("When Acting as Story Implementer", "Post-Done Bug (Hotfix)").
- Fixed every citation of the old filenames on a living path: `Shared_Pipeline_Stages.md` (×2 — including the Stage 3 QA spawn-read-list, a load-bearing citation the orchestrator actually executes), `Story_Standard_QA.md`, and this notes file's own PO/asymmetry bullet.
- **Left untouched, deliberately:** no QA memory-file citations existed to fix (`QA_Memory.md`/`QA_Memory_Archive.md` don't cite the rules file by name). `Sync_Devkit_Workflow.md`'s reference to the distributable `QA_Rules.md` template is out of scope, same reasoning as TL's pass.
- **No token-savings claim**, same reasoning as TL's pass.

## 2026-08-24 — PO rename pass

Same treatment as the TL/QA passes above, applied to PO — the last of the three. Mechanical parity, not a content re-split:

- Verified `Product_Owner_Rules_Extended.md`'s own header before touching anything: PO's instructions file already carried three full "otherwise skip" task blocks (Story Closure, Refine Sprint, Plan Next Sprint) plus `Story_Standard_PO.md`'s pointer to §5 (Story Creation Template) — every on-demand trigger was already scenario-scoped, none tied to "most PO spawns." Matches the axis on inspection; no section moved or renumbered.
- Renamed `Product_Owner_Rules.md` → `Product_Owner_Rules_Bootstrap.md` and `Product_Owner_Rules_Extended.md` → `Product_Owner_Rules_Read_On_Demand.md` via `git mv`. All `§N` numbers preserved.
- Added `Product_Owner_Rules_Bootstrap.md §13`, a routing table mirroring the TL/QA/Dev pattern — restating PO's five existing triggers in one place, since (unlike TL/QA) all five were already individually flagged elsewhere.
- **Unlike TL/QA, no new instructions-file blocks were needed** — `product_owner_instructions.md` already had the "otherwise skip" flagging pattern before this pass (it's the reason the original open item explicitly excluded PO from that specific criticism). Only the filenames inside the three existing blocks and the Pre-Work Checklist table row were updated.
- Fixed every citation of the old filenames on a living path: `Shared_Pipeline_Stages.md` (Stage 4 PO closure spawn-read-list), `Plan_Sprint_Workflow.md` (×2, the roadmap-reconciliation-backstop citations of §11a), and `Story_Standard_PO.md`.
- **Left untouched, deliberately:** `retros/sprint_1_summary.md` and `retros/sprint_2_summary.md` (historical, cite the old filename at the time those retros were written); `Sync_Devkit_Workflow.md`'s reference to the distributable `Product_Owner_Rules.md` template — out of scope, same reasoning as TL/QA's passes.
- **No token-savings claim**, same reasoning as TL/QA's passes.

This closes out the "TL/PO/QA split predates this axis" open item for naming/flagging parity across all three roles. Content-boundary re-examination (e.g. whether PO's Stage-4 closure spawn genuinely needs all of §1–§12, not just closure-relevant sections) was surfaced during the TL verification pass but deliberately not attempted here — it needs real measurement, not inspection, per this file's repeated warning against overclaiming.

## 2026-08-25 — BA/UI-UX split pass

Unlike the TL/QA/PO passes above, BA and UI/UX Designer had **no** `_Extended` file to rename — they were single, never-split rules files. This pass did a real content split (Dev's original model), not a rename:

- **Business Analyst:** `Business_Analyst_Rules.md` (5 sections) → `_Bootstrap.md` (§1, §3–§5) + `_Read_On_Demand.md` (§1, renumbered from the old §2). Moved: "Pre-PR Gate (when acting as Implementer)" — rare, BA is not usually the story implementer. Kept in bootstrap: pre-start steps, Story Comment Rules (BA's routine per-story activity), and the two shared-trigger pointer sections (Stage-Transition Commit, Troubleshooting Protocol), matching the TL/QA/PO/Dev precedent of keeping those as thin bootstrap pointers rather than moving them. Old §2's number is retired, not reused. Added `_Bootstrap.md §6` routing table.
- **UI/UX Designer:** `UI_UX_Designer_Rules.md` (9 sections) → `_Bootstrap.md` (§1, §3–§9, all numbers unchanged) + `_Read_On_Demand.md` (§1–§2, new numbers). Moved only the two inline sub-blocks embedded in old §2 — "Mid-implementation consultation" and "Live user instruction conflicts" — both genuinely rare/task-specific, matching `Developer_Rules_Read_On_Demand.md §12`/`§13`'s identical pattern for Dev. The rest of §2 (read the story, raise questions, start implementation — the mandatory per-story path) and every other section stayed in bootstrap unchanged, so the existing external citation of this file's §4 (`UI_Prototype_Rules.md`) still resolves. Added `_Bootstrap.md §10` routing table.
- Both instructions files (`business_analyst_instructions.md`, `ui_ux_designer_instructions.md`) updated: Pre-Work Checklist "Rules" row now points at the `_Bootstrap.md` file and says "read in full"; a new "otherwise skip" block was added for each on-demand trigger (BA had none before; UI/UX Designer had none before either — same gap Dev/TL/QA's passes closed).
- Fixed the one other living citation found: `UI_Prototype_Rules.md`'s reference to `UI_UX_Designer_Rules.md §4` → `UI_UX_Designer_Rules_Bootstrap.md §4`.
- **Left untouched, deliberately:** the distributable `.claude/agents/templates/rules/` copies and every `Sync_Devkit_Workflow.md`/`Init_Project_Workflow.md`/`Build_Software_Workflow.md`/`Refine_Prototype_Workflow_Shared_template.md` reference to the unsplit template names — those name the *distributable* surface (target-project sync), which is issue #143 AC6, explicitly out of scope for this pass (skipped at the user's direction, along with the other open §2d/§7 items, pending merge to `main`).
- **No token-savings claim.** Neither role has been benchmarked; both are lean files with only one or two truly rare sections, so no meaningful saving is expected on the common path either way — consistent with this file's repeated warning against overclaiming without measurement.
