# Agent Harness Token Efficiency Analysis

**Scope:** mt-agent-devkit agent harness and story pipeline

**Evidence sources:** portfolio-site stories ST-000159, ST-000161, ST-000164, and ST-000166; their per-role step traces and sprint-16 aggregate; raw ST-000161 transcript reconstruction in `Harness_Token_Usage_2026-09-18.json`

**Related issue:** [mt-agent-devkit #207](https://github.com/mycom08/mt-agent-devkit/issues/207)

**Date:** 2026-09-19

---

## 1. Problem

The devkit completes stories correctly, but moderate work can drive much larger
session-final token counters than the implementation itself appears to require.
Agents repeatedly load large policy files, replay resolved story history,
retain verbose tool output, and write overlapping state to several artifacts.

The problem is not independent review by Technical Lead and QA. Those gates
should remain. The problem is the avoidable context and workflow overhead
around them.

Main questions:

- Is the always-loaded harness proportional to the current task?
- Do Bootstrap and Read-on-Demand load the right information at the right time?
- Do Working Record, Memory, retros, and story comments have clear ownership?
- Does each workflow stage perform only the verification that adds new evidence?
- Can token usage and cost be measured and distinguished reliably?

---

### Measurement terms

- **Recorded session-final tokens** are the orchestrator-reported
  `subagent_tokens` value captured when a role session completes. Raw ST-000161
  transcript reconstruction produces 674,523 tokens versus 673,851 recorded
  by the orchestrator (a 672-token, <0.1% difference), which validates the
  magnitude.
- This value behaves like a **final session-context counter**, not total API
  tokens processed across every request and not invoice cost. Do not describe
  it simply as "tokens consumed."
- **Unique tool invocations** are counted from distinct raw transcript
  `tool_use` events. Do not add intermediate cumulative completion snapshots;
  doing so double-counts calls across resumes.
- **Estimated tokens** in step traces are agent-authored approximations based on
  visible files, output, and tool activity. They are not measurements.

---

## 2. Observed and Derived Evidence

### Story measurements

| Story | Shape | Evidence-backed cost signal | Main observation |
|---|---|---:|---|
| ST-000159 | 5-point behavioral UI/data story | 388,007 recorded session-final tokens excluding Developer | QA used 205,188 tokens; no review loop was required |
| ST-000161 | 5-point behavioral UI/form story | 673,851 recorded session-final tokens; 374 unique tool invocations | Developer and QA stalled after substantive work; TL had a fix/re-review loop |
| ST-000164 | 1-point documentation rename | ~51,900 estimated tokens; actual totals missing | Fast path helped, but fixed startup dominated a two-file text edit |
| ST-000166 | 5-point UI/data parity story | 184,208 recorded refinement session-final tokens before implementation; most later totals missing | Broad scope, branch contamination, CI flake, and closure ceremony added overhead |

The earlier 611-call ST-000161 figure was incorrect. It added three
intermediate cumulative snapshots a second time: Developer 89, TL 23, and QA
125. Raw unique counts are Developer 128, TL 78, QA 157, and PO 11, totaling
374. The raw transcript also contains 347 assistant requests; requests and tool
invocations are different measures.

### Repeated evidence across stories

- QA recorded 205,188 session-final tokens on ST-000159 and 227,652 on ST-000161.
- PO closure recorded about 55,000 session-final tokens on both ST-000159 and ST-000161.
- ST-000161 background-wait resumes were associated with a 60,057-token
  increase (38,960 Developer + 21,097 QA). The stalls are verified, but the
  whole delta is not proven waste: the resumed turns also completed PR,
  handoff, sign-off, and record-writing work.
- ST-000159, ST-000161, and ST-000166 contained functional-AC versus prototype-fidelity ambiguity.
- Unrelated Playwright failures or dependency cascades affected multiple reviews and QA runs.
- Issue bodies were updated after refinement, but downstream agents still reread resolved comment history.
- ST-000166 inherited an agent-memory commit from local `main`, requiring branch cleanup and a full verification rerun.
- ST-000164 and ST-000166 traces frequently left `Actual total` blank, so the
  observability mechanism did not preserve its key measurement. ST-000161's QA
  trace also left the field blank even though the sprint aggregate later
  captured 227,652.

### Harness observations

- Common and role Bootstrap files are still large and contain material for
  several different tasks.
- The installed Developer instruction points fresh pre-work at
  `Developer_Rules_Bootstrap.md §1`, but the common read sequence is actually
  owned by `Agent_Common_Bootstrap.md §1`. This is a correctness defect as well
  as an efficiency problem because it can skip common safety and routing rules.
- Role instructions, role rules, story standards, and pipeline workflows repeat
  lifecycle and handoff rules.
- Developer rules require all existing issue comments even though the updated
  story body is intended to be canonical.
- Working Records, Memory, retros, issue comments, PR comments, test-scenario
  documents, and pipeline state often repeat the same information.
- The two-tier Memory design is sound, but an oversized live-memory cap defeats
  the purpose of a lean index.
- The `read-section` skill safely bounds local file reads. The portfolio target
  also has local `run` and `verify` skills, including compact Playwright output,
  so "no test-output skill exists" would be inaccurate for that repository.
  The devkit templates still lack universal bounded helpers for story context,
  branch preflight, CI evidence, and prototype comparison, and do not deploy the
  portfolio-specific `run`/`verify` helpers.

---

## 3. Root Causes

1. **Large fixed context.** The installed Developer fresh-start chain is about
   57,749 characters (~14,437 chars/4 proxy tokens) before issue discussion,
   source inspection, or technical references.
2. **Incorrect startup ownership.** The Developer instruction names the wrong
   owner for the pre-work sequence, creating installed-project drift and making
   the intended common bootstrap unreliable.
3. **Role-shaped instead of task-shaped loading.** A TL or Developer receives
   rules for several lifecycle stages even when performing one narrow action.
4. **Context replay across many requests.** Large files, screenshots, HTML,
   test logs, and CI output remain in the transcript. ST-000161's raw role
   transcripts recorded about 50 million cache-read token units across 347
   requests, demonstrating how retained context is repeatedly carried forward.
5. **Duplicated sources of truth.** Current state and evidence are copied across
   the issue, PR, pipeline state, Working Record, Memory, retro, and test docs.
6. **Overlapping verification.** TL confirms CI, then QA often reruns the same
   complete suite locally even when head-SHA CI already provides equivalent
   regression evidence. Some overlap is intentional independent verification;
   only equivalent automation at the same SHA is a reuse candidate.
7. **Unresolved story contradictions.** Prototype behavior and functional AC can
   disagree without an explicit precedence decision before implementation.
8. **Unsafe operational state.** Agent-memory commits share product Git history,
   and branch creation lacks a mandatory clean/synchronized-base gate.
9. **Weak devkit-wide process automation.** Repeated mechanics are expressed as
   prose rather than compact helpers that return bounded evidence. Local target
   helpers exist, but they are not a consistent devkit capability.
10. **Mandatory ceremony.** Every clean stage may still update a Working Record,
   retro, memory, trace, and issue comment.
11. **Incomplete observability and ambiguous units.** Agents estimate invisible
    costs, actual completion metrics are not always written to the trace, and
    session-final counters have been described as total consumption without a
    stable billing/usage definition.

---

## 4. Fix Suggestions

### Detailed design proposal

The proposed Developer stage profiles, Agent Common capability split, explicit
read manifests, state-ownership model, migration sequence, and validation
criteria are specified in the
[Stage-Specific Read Profiles Proposal](./Stage_Specific_Read_Profiles_Proposal.md).
This analysis remains the evidence and diagnosis; the companion document is the
implementation design.

### Priority 0 — correctness and measurement

1. Have the orchestrator record the reported session-final token counter, unique
   raw tool invocations when available, assistant-request count, duration,
   spawn/resume state, and stage immediately after every agent completion. Keep
   these fields separate and label their semantics.
2. Prohibit open-ended background waits. Agents must poll explicitly, collect
   current output, and complete their handoff before returning.
3. Add a branch preflight: clean worktree, correct base, local base equals remote,
   no unpushed commits, and no unrelated agent-memory commit.
4. Remove agent-memory commits from product branches. Use local gitignored state,
   a dedicated branch, or a dedicated memory workflow.

### Priority 1 — reduce loaded and retained context

5. Replace role-wide read sets with `role + stage + risk` profiles for Developer,
   TL, QA, and PO.
6. Reduce the universal Bootstrap to safety, mode, role boundary, state ownership,
   tool-output discipline, and completion contract.
7. Treat the refined story body as canonical for requirements and decisions.
   Load unresolved threads and the latest authoritative stage verdict, not the
   full resolved history; retain links to the audit trail.
8. Add compact devkit helpers for story context, branch preflight, CI evidence,
   prototype parity, and visual checks. Promote or generalize the target-local
   `run`/`verify` pattern instead of claiming no test-output helper exists.
9. Save full logs to artifacts and return only counts, relevant excerpts, and
   failure details. Perform minimal screenshots near the end of visual QA.

### Priority 2 — right-size the workflow

10. Use risk classes: mechanical, low-risk logic, UI/content, data/schema,
    security/tenancy, and CI/infrastructure.
11. Reuse equivalent green head-SHA CI regression evidence only when the SHA,
    command, environment, and test scope match. QA still performs independent
    targeted tests and behavior checks; it runs local full regression when that
    adds distinct evidence.
12. Add a refinement gate for functional-AC versus prototype conflicts and record
    explicit precedence before `status:ready`.
13. Make routine PO closure mechanical and orchestrator-owned. Spawn PO only when
    product judgment or follow-up prioritization is required.
14. Strengthen the non-behavioral fast path so mechanical changes do not require
    a full specialized-agent bootstrap.

### Priority 3 — simplify persistent state

15. Use pipeline state for current workflow state, the story body for requirements
    and decisions, the PR for implementation evidence, and Memory only for durable
    cross-story knowledge.
16. Read or update a Working Record only for interrupted, blocked, or multi-session
    work.
17. Give the live Memory index and archive separate caps; keep the live index small.
18. Make retros exception-driven and avoid rewriting verification already stored
    in tests, CI, the PR, or the issue verdict.

### Priority 4 — validate the improvement

19. Fix recurring target-project test flakes that repeatedly trigger unrelated
    diagnosis and reruns.
20. Benchmark each change independently on the same representative story shape.
    Verify token reduction without reducing safety, required tests, or independent
    TL/QA judgment.

---

## 5. Evidence Limits

- The sample contains four heterogeneous stories. Only ST-000161 has a complete
  recorded pipeline total; ST-000159 has a complete captured non-Developer
  subtotal, while the other two have larger measurement gaps.
- ST-000159 lacks the Developer actual; ST-000164 is estimate-only; ST-000166
  lacks most post-refinement actuals.
- Story points are scope estimates, not reliable predictors of agent cost.
- No controlled same-story-shape A/B harness benchmark has yet isolated the
  effect of any proposed change.
- The target ranges below are calibration hypotheses, not verified outcomes or
  hard completion budgets.

---

## 6. Expected Result (Benchmark Hypotheses)

After Issue #207's Developer-focused changes:

- Clean Developer stages should move toward roughly **100k–170k recorded
  session-final tokens**.
- If ST-000161's non-Developer stages remained unchanged, that Developer range
  would still yield roughly **544k–614k** for the full pipeline.
- A genuinely clean run without ST-000161's QA stall and TL fix/CI-diagnosis
  loop could plausibly move toward roughly **475k–550k**, but this requires a
  controlled benchmark before it can be treated as a target.

After the complete harness and workflow changes above:

- Clean moderate pipelines should move toward **300k–450k recorded
  session-final tokens**.
- Runs above **450k** should initially trigger investigation.
- Runs above **550k** should initially be treated as severe efficiency incidents
  unless explained by genuine failures, security investigation, or multiple
  fix loops.
- Mechanical documentation stories should complete through a minimal fast path.
- Agent output should remain independently verifiable, with no reduction in
  safety, required regression coverage, or TL/QA judgment.
- Token reports should be complete and comparable across stories.

The proposed **250k–350k** target may become realistic only after pipeline-wide
changes and a controlled benchmark. It is not a credible outcome from
Developer-only optimization: ST-000161's recorded non-Developer stages alone
total 443,723 session-final tokens.

---

**Verification note:** Evidence re-audited 2026-09-19 against portfolio-site
step traces, sprint-16 aggregation, Git history, GitHub story records, installed
harness files, and raw ST-000161 transcript reconstruction. Forecasts remain
explicitly unverified until an A/B harness benchmark is run.
