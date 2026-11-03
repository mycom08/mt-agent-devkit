# Agent Common Memory

Load on observed keyword match or durable fact write. Standing Checks and Keyword Index are bounded entry reads; failure activates Troubleshooting Facts. Legacy single-file memories retain full safe reads until explicit migration.

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
## Stored Facts

### Fact N
- **Rule:** the reusable decision/convention (this is line 1 — already required by rule 1 above)
- **Applies when:** the trigger condition that makes an agent need this
- **Evidence:** one-line pointer — story ID, `file:section` (point, don't mirror — rule 4)
- **Expires when:** the premise whose failure makes this fact wrong

## Troubleshooting Facts

### Fix N — <short label>
- **Problem:** Short label (e.g., "gh CLI authentication fails")
- **Symptoms:** Exact error message or observable behavior
- **Root Cause:** Why it happened
- **Fix:** Exact commands/steps to resolve
- **Prevention:** What to check upfront to avoid this next time
```

> PO and BA record `## Stored Facts` only — the `## Troubleshooting Facts` section applies to roles that run tooling (Developer, Technical Lead, QA). The four-field Stored Facts shape applies uniformly across all six roles; Troubleshooting Facts is unchanged and stays scoped to Dev/TL/QA.

> **Developer, QA, and Technical Lead use a two-tier variant of this format, not the single file above** — see §8. PO, BA, and UI/UX Designer are unaffected.

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
