# Stage Profile Proposal — Feedback

**Reviews:** [Stage-Specific Read Profiles Proposal](./Stage_Specific_Read_Profiles_Proposal.md)

**Applies:** the cost model and measured baseline in [Token Cost Model and Fix Priorities](./Token_Cost_Model_and_Priorities.md)

**Verdict:** Adopt in reduced form, sequenced after parallel tool calls (RC-A). The pattern is sound, but its token benefit is roughly a fifth of what its framing implies, and it introduces a correctness risk it does not acknowledge.

**Date:** 2026-09-21

---

## 1. Quantified Benefit

Current distributable Developer chain (`developer_instructions` + `Agent_Common_Bootstrap` + `Developer_Rules_Bootstrap`) is 29,323 chars ≈ **7,330 proxy tokens**. §10 targets 3,000–5,000, so the split removes ~2,300–4,300 tokens of resident context.

Against measured cache-read, with `cost ≈ requests × mean depth`:

| Resident saving | ST-000161 | ST-000199 |
|---|---:|---:|
| 2,300 tok (the proposal's own target) | **1.6%** | 2.9% |
| 4,300 tok | 3.0% | 5.5% |
| 8,000 tok (optimistic; includes priming/memory) | 5.6% | 10.2% |

For comparison, parallel tool calls (1.1 → 1.8 calls/request) yield **−39%** on both stories. The file-split programme is worth one-twentieth to one-tenth of that, at far greater effort. This ordering is the central finding.

---

## 2. The Validation Criterion Measures the Wrong Thing

§10's "fresh Developer fixed context targets 3,000–5,000 proxy tokens" measures **file bytes at spawn**. Cost is requests × depth. The criterion can pass while cache-read moves ~2%.

**Change it to:** cache-read per stage, and calls-per-request, measured before and after on the same story shape.

---

## 3. Structural Flaw — Profiles Re-Accumulate

§7 adds the Pre-PR profile to the *active* session, and §3 routes Hotfix → Pre-PR. A normal Developer stage running implement → pre-PR → fix-round therefore holds Core plus three profiles: approximately the old bootstrap, loaded later, when context is deeper and cost per token is higher.

The saving materializes only where a session performs **one** action and stops — peer review, refinement, hotfix, non-behavioral fast path. Those are the minority of spawns and not where the tokens are.

---

## 4. Risks Not Addressed

**4a. Conditional safety rules.** `Agent_Common_Shell_Safety` loads "before the first shell write or Git/GitHub mutation." A missed trigger means a destructive Git operation with the safety rules absent. This is the live P0 defect — §6 (Shell Command Rules) silently dropped from the mandatory set in every install by the `§2–§5` template drift — promoted from accident to design. **Safety rules stay unconditional.**

**4b. Drift surface.** The proposal replaces 3 Developer files with 8 and 2 Common files with 8. Generalized across six roles that is ~40–50 rule files in two parallel trees. The current P0 was caused by one file being updated and its sibling not, at today's file count.

**4c. Missing migration net.** §9 step 6 assumes validation that detects dead references and duplicated rules. `validate_templates.py` has no such check today, scans `templates/` only, and has no heading check. The migration's safety net does not exist yet.

---

## 5. What to Take, Independent of the Split

These carry most of the proposal's real value and do not require the file reorganisation:

- **§8 State Ownership** — one canonical owner per information class. Fixes the duplication root cause outright; costs one table.
- **Exception-driven retros** and **Working Record only for interrupted work** — removes whole read+write cycles per stage. This is call count, not bytes, so it outranks the split itself.
- **§7 resume deltas and the fix-round context packet** — correct, and orthogonal to file layout.
- **Orchestrator-emitted read manifest** — the strongest idea, for an unstated reason: knowing every path upfront is what makes startup reads *parallelizable*. Its value comes from pairing with RC-A, not from shrinking files.

---

## 6. Recommendation

1. Adopt §8, exception-driven retros, conditional Working Record, and resume deltas now.
2. Adopt the manifest, and use it to issue startup reads in one parallel turn.
3. Apply stage profiles **only** to single-action spawns (peer review, refinement, hotfix, fast path), where §3 shows they pay.
4. Hold the full 16-file split until `validate_templates.py` has `working/` ↔ `templates/` parity and heading-range checks — otherwise the migration multiplies the exact defect class that produced the current P0.
5. Keep all safety rules unconditional. Non-negotiable.
6. Replace §10's byte-based criterion per §2 before any before/after claim is made.

---

## 7. Open Decisions in §11 — Positions

- **Separate files vs extracted sections:** separate files only for the single-action profiles in item 3. Sections elsewhere, until 4c is resolved.
- **Peer review core:** a smaller reviewer core, not the full Developer core — peer review is a single-action spawn and is where profiles pay best.
- **Memory persistence:** gitignored local state or a dedicated branch; this is already P0 item 3 in the priorities document.
