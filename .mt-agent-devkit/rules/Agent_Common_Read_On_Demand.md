# Agent Common — Read On Demand

**Compatibility authority:** This complete safe path remains mandatory for providers not enabled by canonical Common capability routing. Registry-selected verified consumers use Agent_Common_Core.md and triggered modules instead. The policies are mutually exclusive authorities; Developer stage procedures remain at existing owners.
**Applies to:** All agents (Developer, Technical Lead, QA, Product Owner, Business Analyst, UI/UX Designer)
**Purpose:** Companion to `Agent_Common_Bootstrap.md`. Nothing here is read automatically — `Agent_Common_Bootstrap.md §5`'s routing table names the one section to fetch when its trigger fires. §8 is devkit-internal only (not mirrored to `templates/`). Where this file and a role-specific rule disagree, the role-specific rule wins.

> **Two things to know before extracting a section from this file.**
> 1. **There are two intentional gaps.** Numbering runs §1, §2, §3, §5, §6, §8. **§4** is where the pre-split *Working Record* section sat before it was folded into `Agent_Common_Bootstrap.md §1`. **§7** is where the *Token-Trace Log* sat before it left the agent rules altogether for `orchestrator_instructions.md`. Numbers are never reused: leave the gap rather than renumbering, so a stale citation resolves to nothing rather than to a different rule (same convention as `Technical_Lead_Memory.md`'s fact numbering).
> 2. **§1 contains unnumbered sub-headings** (`## Stored Facts`, `## Troubleshooting Facts`). Bound a section extraction on **numbered** headings only (`grep -nE "^## [0-9]+\."`) — a bare `^## ` treats those sub-headings as the end of §1 and silently returns a truncated section, dropping the format block and §1's closing two-tier note.

---

## 1. Project Memory

<!-- BEGIN GENERATED agent-memory part facts: edit .mt-agent-devkit/skills/agent-memory/SKILL.md, then regenerate -->
**Purpose.** Memory stops an agent making the same mistake twice: a fix it worked out, a convention the user asked for, a project-specific trick. Not a session diary, the story tracker, the PR diff or the Working Record.

Record **durable facts only** for future sessions (not task state or conversation context); update an existing fact rather than add a duplicate; keep entries short.

**Inclusion test** (before adding or keeping a line): *would losing it make someone repeat a mistake or re-derive something expensive?* If no, cut it.

**Never record:** anything recoverable from the story, PR diff or Working Record; history driving no future action; a fact whose premise expired; narrative of how one story was verified.

**Fact-writing rules:**

1. **Rule-first format.** Line 1 = the reusable rule/decision; evidence and context follow in 1–3 sentences. Soft cap **~100–120 words per fact**; never bury the rule in a multi-paragraph narrative.
2. **Corrections rewrite in place.** Edit a superseded fact to the current truth, keeping one `Corrected: <date> — <what changed>` line; never stack addenda under stale text.
3. **Prune on write, verified on schedule.** On adding a fact, merge or delete any fact it obsoletes; broader staleness (expired premises, history-only entries, missed duplicates) is caught by the once-per-sprint Sprint-End Memory Pruning in `Retro_Rules.md` — do not rely on noticing it mid-task.
4. **Point, don't mirror.** If the substance lives in a committed doc or another role's session artifacts, store a one-line pointer plus your role-specific delta. Issue comments too (every downstream role re-reads them): cite a fact already in memory (`Developer_Memory.md` Fact N), never re-explain it (the Commenter gate in the `comment` skill).

**Enforced file-level cap:** **≤ 40,000 characters** per memory file (`wc -c`); `≤ 200 lines` is non-enforced guidance only.

**Format:** `## Stored Facts` uses this four-field shape for all six roles:

```md
## Stored Facts

### Fact N
- **Rule:** the reusable decision/convention (line 1, rule 1)
- **Applies when:** the trigger condition that makes an agent need this
- **Evidence:** one-line pointer — story ID, `file:section` (rule 4)
- **Expires when:** the premise whose failure makes this fact wrong
```

> **Dev, QA and TL use the two-tier variant below**; PO, BA and UI/UX Designer keep the single file.
<!-- END GENERATED agent-memory part facts -->

<!-- BEGIN GENERATED troubleshooting part format: edit .mt-agent-devkit/skills/troubleshooting/SKILL.md, then regenerate -->
`## Troubleshooting Facts` keeps its own shape, distinct from `## Stored Facts`:

```md
## Troubleshooting Facts

### Fix N — <short label>
- **Problem:** Short label (e.g., "gh CLI authentication fails")
- **Symptoms:** Exact error message or observable behavior
- **Root Cause:** Why it happened
- **Fix:** Exact commands/steps to resolve
- **Prevention:** What to check upfront to avoid this next time
```

> PO and BA record `## Stored Facts` only — the `## Troubleshooting Facts` section applies to roles that run tooling (Developer, Technical Lead, QA). The Stored Facts shape applies uniformly across all six roles; Troubleshooting Facts stays scoped to Dev/TL/QA.
<!-- END GENERATED troubleshooting part format -->

---

## 2. Troubleshooting Protocol

<!-- BEGIN GENERATED troubleshooting part protocol: edit .mt-agent-devkit/skills/troubleshooting/SKILL.md, then regenerate -->
Applies on any tooling/environment blocker: `gh` CLI auth failures · script syntax errors · shell script fails to run · CI YAML errors.

**Step 1 — Check memory first.** Scan your memory file's `## Troubleshooting Facts` for a matching entry. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix.** If no match, find the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory).** After resolving, record the fix under `## Troubleshooting Facts` in the Troubleshooting Facts shape before resuming.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.
<!-- END GENERATED troubleshooting part protocol -->

---

## 3. Triggered Retrospective Contribution

<!-- BEGIN GENERATED retro-contribution part writing: edit .mt-agent-devkit/skills/retro-contribution/SKILL.md, then regenerate -->
Load this guidance only after retro detection recorded a required contribution. Clean stages skip it entirely.

1. Read Retro_Rules in full using the selected provider's supported mechanism before writing; preserve lesson-first, privacy, shared deduplication and role ownership.
2. Create the bound story retro only if missing, with its story/date header and your triggered role section. Do not create other roles or pending placeholders. If it exists, preserve all prior history and other sections.
3. Write only your actual role contribution and new observations. A late/resumed trigger updates existing lessons or records the new delta; do not duplicate earlier findings. Populate required observations, not a no-op “None” section.
4. Update the same completion identity with its confined exact role contribution and evidence pointers; run the helper check for the expected stage identity before handoff. Unknown or missing required contributions block completion.
5. For an explicitly grandfathered already-started legacy run, retain its existing skeleton and write your owned section under that prior contract; do not erase other placeholders/history.
<!-- END GENERATED retro-contribution part writing -->

---

## 5. Runtime-State Handoff (implementer & reviewer roles)

<!-- BEGIN GENERATED handoff part state: edit .mt-agent-devkit/skills/handoff/SKILL.md, then regenerate -->
Memory, Working Records, retrospectives, telemetry, and pipeline state are local runtime state. Never `git add`, commit, or push them on a product branch; report stage completion after the local handoff.
<!-- END GENERATED handoff part state -->

---

## 6. Credential-Gated Verification

<!-- BEGIN GENERATED credential-gate part gate: edit .mt-agent-devkit/skills/credential-gate/SKILL.md, then regenerate -->
Applies whenever a story's verification requires a runtime secret (API token, PAT, signing key, DB password, etc.) that is not available in your working environment.

- **Never self-approve a skip.** A dummy-value substitute, or an analogy to a different code path/CI job that happens to use the same secret, is not equivalent to exercising the real credential — do not treat it as sufficient verification.
- **Stop and report** the specific constraint: what credential is missing, why, what you verified without it, and what the credential would additionally prove.
- **Wait** for either the real credential or explicit user authorization to proceed with permitted work. Quote that authorization in your report or retro. An authorization to proceed is not PASS evidence: unexercised AC remain NOT VERIFIED, and acceptance/merge/closure require verification or an approved tracked split with renewed QA under `Story_Standard.md §14`.
<!-- END GENERATED credential-gate part gate -->

---

## 7. Token-Trace Log — RETIRED

> **The Token-Trace Log is no longer an agent-tier rule at all.** It sat here as §7, moved to `Agent_Common_Bootstrap.md §6` on 2026-08-21, and on 2026-08-21 left the agent rules entirely: the format now lives only in `orchestrator_instructions.md`, and the orchestrator injects it verbatim into the spawn prompt of any agent it wants a trace from. An agent never reads a rule to learn the format — it reads the prompt. That removes the circularity the bootstrap move was chasing (a trace must account for the pre-work reads, which happen before any rule could be fetched) without charging any spawn for a convention most spawns never use. §7 stays retired and is never reused; a stale `§7` or `Agent_Common_Bootstrap.md §6` citation must resolve to nothing.

---

## 8. Two-Tier Memory (devkit-internal pilot — Developer, QA, Technical Lead only)

<!-- BEGIN GENERATED agent-memory part two-tier: edit .mt-agent-devkit/skills/agent-memory/SKILL.md, then regenerate -->
Dev, QA and TL split `## Stored Facts` across two files (internal pilot, #118):

- **`<Role>_Memory.md`** (live; bounded Standing Checks/Keyword Index reads at fresh or expired entry): **Standing Checks** — unconditional always-do actions, no recall needed (leave `*(none yet)*` if none qualify) — plus a **Keyword Index**: one line per fact, `### Fact N — <short title>` + a `Keywords:` line, no fact body. `## Troubleshooting Facts` stays here, unchanged shape.
- **`<Role>_Memory_Archive.md`** (open only on a keyword match): full four-field bodies.

**Retrieval:** bounded read only, never the full archive — use the `read-section` skill (`.mt-agent-devkit/contracts/Read_Section.md`, heading marker `^### Fact `).

**Writing a fact:** append the body to the archive under the next number, then its index line — both files change together; an entry in only one is a defect. Never reuse or renumber; retire gaps.

**Caps:** the live file is under the ≤ 40,000-char cap by construction (no fact bodies); until the pilot's retention policy is settled, that cap is also the archive's ceiling.
<!-- END GENERATED agent-memory part two-tier -->
