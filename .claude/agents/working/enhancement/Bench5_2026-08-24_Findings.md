# Bench 5 Findings — 2026-08-24

**Shape:** Full pipeline — Developer → Technical Lead (review) → QA (validate). First round to benchmark this shape; rounds 1 (#144/#145) and 4 (#154/#155) were narrow single-Developer spawns.

**Story:** "Add a script for agents to read multiple sections from a harness file in one call" (`read_sections.sh`, new file only — touches nothing on the two branches' diverging-file list). Issues #158 (BENCH5-B, baseline) / #159 (BENCH5-A, treatment), `test:benchmark` label.

**Baseline:** `main` @ `87d49b9`. **Treatment:** `agent-enhancement` @ `a6c0a2e` (full TL/QA/PO bootstrap rollout, current head). Both arms run in this session, sequentially, baseline first — **not** a separate-session baseline (§4a's leak risk accepted by explicit user choice, same shortcut as round 4).

---

## 1. Read set (byte-measured, `git show <ref>:<path> | wc -c` on the files each arm's own trace reported reading)

| Role | Baseline (main) | Treatment (agent-enhancement) | Δ (as-reported) |
|---|---|---|---|
| Developer | 58,019 B | 35,238 B | −39.3% |
| Technical Lead | 55,928 B | 42,189 B | −24.6% |
| QA | 43,836 B | 36,662 B | −16.4% |
| **Sum** | **157,783 B** | **114,089 B** | **−27.7%** |

**Two compliance gaps make the raw numbers untrustworthy at face value — §1's rule (never quote nominal, but an unreported compliant read is also not "actual"):**

- **Developer/treatment never reported reading `Story_Standard_Dev.md`**, despite `Developer_Rules_Bootstrap.md`'s identical mandatory gate ("Do not begin implementation until `Story_Standard_Dev.md` has been read"). Baseline's Developer read it (6,529 B). This is the same class of gap `be3988b` was written to fix — a **possible regression**, not confirmed fixed. Adding the file back for a compliance-adjusted figure: 35,238 → 40,708 B, dropping the Dev delta to **−29.8%**.
- **QA/baseline never reported reading its own `qa_instructions.md` (2,236 B) or `Story_Standard_QA.md` (4,207 B)**, both mandated identically on `main`. Treatment's QA read both. This is a **main-branch** gap, unrelated to the split under test. Adding both back to baseline: 43,836 → 50,279 B, moving the QA delta to **−27.1%**.

**Compliance-adjusted sum:** 58,019 + 55,928 + 50,279 = 164,226 → 40,708 + 42,189 + 36,662 = 119,559 = **−27.2%**. Close to the as-reported sum because the two gaps partially offset (one inflates the saving, one deflates it) — do not read that as the gaps cancelling out or not mattering; both are independent findings that need their own follow-up, not a wash.

## 2. `subagent_tokens` (self-reported, noisy — §6; full session including implementation/verification/commenting, not just pre-work)

| Role | Baseline | Treatment | Δ |
|---|---|---|---|
| Developer | 121,248 | 81,897 | −32.5% |
| Technical Lead | 78,035 | 87,106 | +11.6% |
| QA | 84,517 | 98,434 | +16.5% |
| **Sum** | **283,800** | **267,437** | **−5.8%** |

**This is the headline result of the round.** Sum-level `subagent_tokens` moved only **−5.8%**, far below both prior narrow-task rounds (−12.7%, −10.2%) and far below the byte-measured read-set effect (−27 to −39% per role). TL and QA even ran *higher* on tokens in the treatment arm. This is the first direct measurement of the shape-effect `Bootstrap_OnDemand_Split_Notes.md` flagged as a risk from indirect evidence alone (`Developer_Rules` measured +15% on a full spawn vs −63% on a narrow task): **on a full pipeline, pre-work reads are a shrinking fraction of total cost**, and implementation/verification/comment-writing work — identical in both arms — dominates the total. The read-set saving is real and reproducible; its share of the total spawn cost is not what the narrow-task rounds implied.

Do not read TL/QA's higher totals as the split making review/QA *more expensive* — both roles did more investigative work in the treatment arm for reasons unrelated to bootstrap/on-demand tiering (see §4).

## 3. Output quality (§9b question: do the arms differ, and is either worse?)

**Unlike round 4 (byte-identical PRs), this round's two implementations genuinely diverge** — a stronger test of quality parity, since neither arm could free-ride on the other's design:

- **File location differs**: baseline placed the script at `.claude/skills/read-section/scripts/read_sections.sh`; treatment at `.claude/agents/working/scripts/read_sections.sh`. The story deliberately left this unspecified (Story Standard §3: no file-by-file specs), so this is expected variance, not a defect.
- **Extraction strategy differs**: baseline does one `grep -nE` boundary scan into a bash array, then `sed -n` slices per marker; treatment runs a separate `awk` state-machine pass per marker. Both correctly handle the `11a`/`11b` non-swallowing case, the `## Version` footer terminator, EOF-as-last-section, and per-marker unmatched reporting without aborting the batch.
- **Exit-code convention differs** (baseline: 1 for both usage and marker errors; treatment: 2 for usage/file errors, 1 for marker mismatch) — the AC didn't constrain this, so both are compliant; a follow-up story should pick one convention if the script is ever wired into the `read-section` skill.

**Both were independently validated as fully correct** by their own arm's TL (opus) and QA (sonnet), including edge cases neither Developer's own verification list covered by name. No quality gap found. This is a better n=1 signal than round 4's for "no quality cost," precisely because the two arms didn't converge on identical code — genuine independent implementation, genuine independent verification, same result.

## 4. Benchmark-methodology artifact (not a harness effect — a lesson for the runbook)

Cutting `bench-a/multi-section-script` from `agent-enhancement`'s head while the PR targets `main` made `gh pr diff 161` return the **entire branch delta** (288 KB / 52 files / 18 commits) instead of the story's own 2-file change. Both TL and QA independently caught this and correctly re-scoped to the story's actual commit (`git show <sha> --stat`) rather than trusting the raw PR diff — which would otherwise have produced a **false AC4 failure** (`SKILL.md`/`version.txt`/`changes.json` all appear "touched" in the full-branch diff). This cost both reviewer/QA spawns extra investigative steps in the treatment arm specifically (see §2's TL/QA token increase) — an artifact of how this benchmark's branches were cut, not of the split under test. **Runbook note for next time:** either tell the reviewer/QA spawn prompt to scope by commit up front, or accept this as a fixed, symmetric-ish tax that a real (non-benchmark) `agent-enhancement`-based story would also pay before merge — it is not unique to benchmarking, just surfaced by it here.

## 5. §4a confabulation leak — fourth recurrence

Baseline Developer's step-1 trace entry: *"bootstrap-named paths from the prompt didn't exist on this branch; fell back to actual files."* The spawn prompt named **zero** file paths — same pattern as the three prior occurrences (§4a, 2026-08-21 ×2, 2026-08-24 round 4). Confirms this is a durable property of this user's carried-over auto-memory (which names the split by filename in its own index), not a one-off. The read set itself was not spoiled (it still read whatever the actual harness mandated) — only the Developer's own narration of *why* was fabricated. Treat every self-reported "the prompt said X" claim as unverified, per §4a's existing guidance.

---

## Bottom line

The split's read-set effect replicates a third time and holds up under a genuinely divergent-implementation quality check. But the full-pipeline shape this repo actually runs most often shows the effect diluting hard at the aggregate-token level (−5.8%, not −27%), and this round surfaced two real, unrelated compliance gaps (Dev/treatment skipping a mandatory Story-Standard read; QA/baseline skipping two mandatory reads) that need their own follow-up stories — they are not artifacts of this benchmark and should not be waved off as such.
