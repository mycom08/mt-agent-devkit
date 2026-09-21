# Token Cost Model and Fix Priorities

**Scope:** mt-agent-devkit agent harness — cost model, verification of the companion analysis, merged priority list.

**Companion:** [Agent Harness Token Efficiency Analysis](./Agent_Harness_Token_Efficiency_Analysis.md) (evidence and diagnosis) and [Stage-Specific Read Profiles Proposal](./Stage_Specific_Read_Profiles_Proposal.md) (design). This document supplies the cost model both assume, corrects three of their claims, and ranks what to fix.

**Evidence:** `Harness_Token_Usage_2026-09-18.json` (ST-000161 and ST-000199, four role sessions each) plus direct inspection of the devkit source trees.

**Date:** 2026-09-21

---

## 1. Cost Model

Output tokens are **0.30%** (ST-000161) and **0.49%** (ST-000199) of cache-read. Effectively all cost is retained input, replayed once per request.

> **cost ≈ (number of requests) × (mean context depth)**

Two consequences that govern every item below:

- A tool call's cost is not the size of its output. It is the size of the whole transcript at the moment it is made.
- Context is never evicted, so cost is **convex in session length** — the same command costs roughly 5× more at turn 100 than at turn 10.

Most existing token rules optimize the brevity of written output. That is the 0.3%.

---

## 2. Measured Baseline

ST-000161 (expensive, 674,523 reconstructed) vs ST-000199 (clean, 390,357). Both complete four-role pipelines.

| Role | calls/request (161 / 199) | cache-read share (161) | cache-read share (199) |
|---|---|---:|---:|
| QA | 1.08 / 1.18 | **47.3%** | 33.9% |
| Developer | 1.07 / 1.12 | 36.0% | 32.6% |
| TL | 1.10 / 1.10 | 15.9% | 23.2% |
| PO | 1.10 / 1.07 | 0.85% | 10.3% |

**Spawn prefix** (`first_request_input`) is near-constant across both stories: Dev ~42.0k, QA ~42.2k, TL ~36.5k, PO ~31.1k (variance < 1%). Replayed per request, it is **28.2%** of all cache-read on ST-000161 and **49.6%** on ST-000199.

**Metric warning.** Session-final tokens and cache-read rank the roles differently. PO is 8.2% of session-final and 0.85% of compute; QA is 33.8% of session-final and 47.3% of compute. Prioritizing on session-final misdirects effort. Session-final also blends Opus (TL), Sonnet (Dev/QA) and Haiku (PO) into one number.

---

## 3. Verification of the Existing Analysis

Confirmed exact against the JSON: reconstruction 674,523; unique tool calls 374 (Dev 128 / TL 78 / QA 157 / PO 11); 347 requests; 49,997,075 cache-read. Harness claims confirmed: `Developer_Rules_Bootstrap.md:30` requires all issue comments; the live memory index has no cap of its own (`Agent_Common_Read_On_Demand.md:137`); `read-section` is the only bounded helper shipped to targets.

Three claims do not hold:

1. **Root cause #1 is mis-attributed.** It derives fixed context from a ~57.7k-character file chain (~14.4k proxy tokens). Measured spawn prefix is ~42k tokens. Most of it is harness system prompt and tool schemas, which the devkit cannot trim. Prefix-shrinking therefore has roughly a quarter to a third of the headroom implied.
2. **Root cause #2 is not reproducible.** The Developer instruction points at `Agent_Common_Bootstrap.md §1` in all three trees (`templates/`, `working/`, `.antigravity/`), and has since ST-000132 (`b3fdf91`). Version-stamp it against the installed copy or drop it. The real defect in that area is §5 item 1 below.
3. **§5 "Only ST-000161 has a complete recorded pipeline total" is contradicted by the cited JSON.** ST-000199 has all four roles and totals 390,357 — inside the 300k–450k target band, and usable as a baseline today.

Minor: QA on ST-000161 is 227,652 in the analysis, 227,766 in the JSON; unreconciled.

---

## 4. Root Causes Added or Reframed

- **RC-A — No parallel tool use.** 1.07–1.18 calls/request across 8/8 sessions, both stories, all roles, all models. Each call replays the full transcript. `Agent_Common_Bootstrap §3` states the correct cost model but teaches only shell-level chaining, which does not remove a replay. Absent from the companion analysis. Cross-cutting: it multiplies into every other item.
- **RC-B — Prefix replay, not prefix size.** See §2. Reduce the number of replays before reducing the prefix.
- **RC-C — Monotonic context.** `last − first`: Dev +188k, QA +186k on ST-000161. This is a persistence and ordering problem, not an output-size problem.
- **RC-D — Failures compound.** 161 vs 199: requests 2.1×, cache-read 3.8×. Stalls and fix loops raise call count *and* depth; the two multiply. Post-hoc budget thresholds (450k/550k) fire after the compounding, so control on calls-per-request and turns-since-spawn instead.

---

## 5. Priority List

**P0 — correctness, independent of the token programme**

1. **`§2–§5` vs `§6` drift in all six distributable instruction templates.** Installed projects are told §2–§5 of `Agent_Common_Bootstrap` are mandatory; the file has §6 (Shell Command Rules — Permissions and Tool Choice). Introduced by ST-000137 (`3cadbe3`), which updated `working/` only. `validate_templates.py` has no heading-range check, so it stays green. Fix six lines plus a validator rule.
2. **Observability with labelled units and model attribution.** Record session-final counter, cache-read, requests, unique tool calls, model, stage and spawn/resume as separate fields. Precondition for judging everything below.
3. **Branch preflight; agent-memory commits off product branches.** Operational risk first (ST-000166 forced a full rerun), token cost second.

**P1 — token leverage, ranked by measured share**

4. **Adopt parallel tool calls** (RC-A). Target ≥ 1.8 calls/request. Moving from ~1.1 removes ~39% of requests and at least that much cache-read. Lowest effort, highest leverage.
5. **QA — the largest single sink** (47.3% of compute). Three compounding causes: re-deriving regression evidence CI already produced at the same SHA; high-persistence Chrome MCP screenshots; call count from item 4. Reuse green head-SHA CI evidence only when SHA, command, environment and scope match; independent targeted testing stays.
6. **Tool-output persistence** (RC-C). Save full logs to artifacts, return counts and excerpts, defer screenshots to the end of visual QA.
7. **Stage-specific read profiles.** Worth doing, but capped by §3 item 1 — the devkit owns roughly a third of the prefix. Strongest on clean stories, where prefix is 49.6% of cache-read.
8. **Replace budget thresholds with leading indicators** (RC-D).
9. **Refinement gate for functional-AC vs prototype-fidelity conflicts.** Correctness item; the loops it prevents are the ones that compound.

**P2 — real, defer until 4–6 are measured**

10. Duplicated sources of truth; separate live/archive memory caps. Latent — live indexes run 67 B–7.5 kB against a 40 kB cap.
11. Bounded devkit helpers for story context, CI evidence, prototype parity.
12. PO closure ceremony — 73.2% of PO's cost is prefix replay, but PO is 0.85% of compute. Trivial to fix; not a priority.

---

## 6. Evidence Limits

- Two stories, eight role sessions, one target project (portfolio-site). No controlled A/B run yet; ST-000199 is a usable baseline, not a control.
- Projected savings in §5 item 4 are arithmetic from measured call ratios, not observed outcomes.
- `first_request_input` is read as the first request's input context. Per-role variation (31k–42k) tracks read-set size, so some spawn-prompt content is included; the §3 item 1 conclusion holds under either reading.
- Cache-read units are usage units, not invoice cost.
