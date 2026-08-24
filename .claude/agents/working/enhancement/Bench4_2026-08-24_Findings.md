# Benchmark 2026-08-24 (round 4) — `agent-enhancement` (539f3a0) vs `main` (87d49b9)

**Method:** `Harness_Benchmark_Guide.md`. Two Developer spawns, one story, paired issues. Both arms run from the orchestrator's own session (§4a baseline-session control was not used — see §3).
**Arms:** A = `agent-enhancement` (treatment) · B = `main` (baseline). Baseline run first.
**Story:** fix the `status:testing`-owner contradiction in `Story_Standard_Dev_template.md` (real backlog issue #113) — issues #154 (A) / #155 (B). PRs #157 (A, base `agent-enhancement`) / #156 (B, base `main`).

---

## 1. Headline

**Pre-work read set fell 25.7%, from 67,468 to 50,157 bytes** — real but roughly half the −43.5% measured in the 2026-08-21 round on a different story. `subagent_tokens` moved less: 81,206 vs 72,922 (−10.2%), and per `Harness_Benchmark_Guide.md §6` this figure is noisy and not independently trustworthy.

**The gap versus round 1 has an identifiable cause, not just story-shape noise:** `Developer_Rules_Bootstrap.md` is now 11,581 bytes — almost exactly the size of the unsplit `Developer_Rules.md` (11,688 bytes) it replaces. Commit `be3988b` ("Move Developer_Rules §1-§6 back to the bootstrap tier"), made *after* round 1, moved most of that file's content back into the always-loaded tier to close a compliance gap. That was very likely the right correctness call, but it means Developer_Rules currently contributes close to **zero** of this round's savings — the entire reduction comes from `Agent_Common_Bootstrap.md` (10,353 vs 20,282, −49.0%) and `Project_Priming_Bootstrap.md` (6,132 vs 11,530, −46.8%).

## 2. Read-set table (byte counts read directly from each branch, not self-reported)

| File | Arm B — `main` | Arm A — `agent-enhancement` |
|---|---|---|
| `developer_instructions.md` | 3,698 | 2,867 |
| `Agent_Common.md` / `Agent_Common_Bootstrap.md` | 20,282 | 10,353 (−49.0%) |
| `Developer_Rules.md` / `Developer_Rules_Bootstrap.md` | 11,688 | 11,581 (−0.9%) |
| `Project_Priming.md` / `Project_Priming_Bootstrap.md` | 11,530 | 6,132 (−46.8%) |
| `Developer_Memory.md` | 4,292 | 4,305 |
| **Mandated subtotal** | **51,490** | **35,238** (−31.6%) |
| `Story_Standard_Dev.md` (§1 gate, working mirror) | 6,529 | 5,470 |
| `Story_Standard_Dev_template.md` (story target, identical on both branches) | 9,449 | 9,449 |
| **Total** | **67,468** | **50,157** (−25.7%) |

**Caveat on `developer_instructions.md`:** unlike round 1, neither arm's step trace itemized this file as its own step this round (it may be folded into an unlogged pre-trace action, or genuinely skipped). Included in the table on the CLAUDE.md-mandate assumption, not confirmed compliance — flagged, not asserted.

Neither arm touched a Read-On-Demand / Extended file — this story's triggers (a two-line template edit, no version bump, no working-record dual-update) didn't fire any on-demand section on either branch. That is consistent with the tier design, but means this round doesn't exercise the on-demand path at all — see §3.

## 3. What this does not establish

- **n=1 per arm**, same limitation as every round so far.
- **Both arms ran in this orchestrator session**, not a genuinely naive separate session (`§4a`'s stronger control). The user explicitly accepted this tradeoff for this round. See §4 — it produced exactly the leak the guide predicted, again.
- **`subagent_tokens` is `(unlabelled)`** for both arms — 81,206 (B) and 72,922 (A), each covering the whole spawn including PR/issue mechanics, not comparable to a per-step figure.
- **Task shape triggered no Read-On-Demand read on either arm.** This round says nothing about the on-demand tier's cost when it *does* fire, and nothing about a full TL→Dev→QA story spawn (`Bootstrap_OnDemand_Split_Notes.md`'s +15%-on-full-spawns finding is still the only data point there).
- **The Developer_Rules regression (§1) is a one-round observation.** It reflects one specific post-round-1 commit, not a general trend — worth re-checking after any further changes to that file's tiering.

## 4. The session-level contamination leak recurred — third occurrence

Arm B (baseline, checked out to `main`) reported, as its very first step: *"Attempted to read `Agent_Common_Bootstrap.md` per spawn-prompt paths; file did not exist."*

**The spawn prompt named no such file.** It said only "Follow your role's normal startup and rules" — no filenames at all, unlike round 1 where at least the real (unsplit) filenames were named. This is a stronger case than either prior occurrence: the agent didn't just misattribute a real name, it invented a `_Bootstrap.md` filename that exists **only on the branch it was never pointed at**, from an orchestrator session whose `<env>` block and `MEMORY.md` both name the split. This is the exact mechanism `Harness_Benchmark_Guide.md §4a` describes, reproduced a third time, and this time with an even weaker prompt than the ones that triggered it before.

**Practical impact was small** (~200 tokens per arm B's own estimate, one wasted tool call) but the pattern is now reproduced on 2026-08-21 (twice) and 2026-08-24 (once) under three different spawn-prompt phrasings, including one with zero filenames at all. `§4a`'s conclusion stands and is further confirmed: **do not run a baseline arm from a session whose `<env>`/memory names the treatment change, if the round needs to say anything about the agent's awareness.** The read-set comparison itself (§1–§2) is unaffected — it's a direct byte count, not a self-report.

## 5. Incidental findings

- Both PRs are genuine fixes to real backlog issue #113 — either could be reopened as the real delivery per the runbook's cleanup step. Recommend closing out with the user/TL rather than a unilateral pick, since #157 (targets `agent-enhancement`) and #156 (targets `main`) aren't interchangeable — merging both would produce the same content via two different paths.
- Arm A's step 1 shows a live inefficiency, not confabulation: it first tried the `read-section` skill against `Agent_Common.md §1` (a path that no longer exists in that form on this branch), then discovered the split and grepped `Agent_Common_Bootstrap.md` headings instead. Worth checking whether `developer_instructions.md` or the `read-section` skill's own guidance still cites the pre-split path anywhere on `agent-enhancement` — that would be a real stale-reference defect, not a benchmark artifact.

---

## Version

**Version:** 1.0 — Created 2026-08-24. Fourth benchmark round; first to run after the #148/#149 round was found abandoned and cleaned up (`Harness_Benchmark_Guide.md §8`).
