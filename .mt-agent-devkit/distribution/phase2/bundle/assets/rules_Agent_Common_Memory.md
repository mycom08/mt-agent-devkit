# Agent Common Memory

Load on observed keyword match or durable fact write. Standing Checks and Keyword Index are bounded entry reads; failure activates Troubleshooting Facts. Legacy single-file memories retain full safe reads until explicit migration.

## 1. Project Memory

**Purpose.** Memory exists so an agent does not make the same mistake twice — a fix it worked out, a command or convention the user asked it to follow, or a trick specific to this project. It is not a session diary and not a substitute for the story tracker, the PR diff, or the Working Record.

Update your memory file when you encounter a fact worth remembering for future sessions.

- Record **durable facts only** — not current task state or conversation context.
- Prefer updating an existing fact over adding a duplicate.
- Keep entries short and practical.

**Inclusion test** (apply before adding or keeping any line): *would losing this line cause someone to repeat a mistake, or re-derive something expensive?* If no, cut it.

**Never record:**
- Anything recoverable from the story, the PR diff, or the Working Record
- History that drives no future action
- A fact whose premise has expired
- Narrative of how one story was verified

**Fact-writing rules:**

1. **Rule-first format.** Line 1 of the fact = the reusable rule/decision. Evidence and context follow in 1–3 sentences. Soft cap **~100–120 words per fact** — never a multi-paragraph narrative with the rule buried at the end.
2. **Corrections rewrite in place.** When a fact is superseded or a number corrected, edit the fact body to the current truth and keep only a one-line `Corrected: <date> — <what changed>` note. Never stack correction addenda under stale text — a skimming agent reads the opening as current.
3. **Prune on write, verified on schedule.** When adding a fact, still check whether it obsoletes an existing one — merge or delete the loser. This on-write check is not the only pruning mechanism: broader corpus staleness (expired-premise facts, history-only entries, duplicates missed at write time) is caught by the scheduled once-per-sprint pass in `Retro_Rules.md` (Sprint-End Memory Pruning) — do not rely on noticing it yourself mid-task.
4. **Point, don't mirror.** If the substance lives in a committed project doc or another role's session artifacts, store a one-line pointer plus only your role-specific delta — never a full re-derivation.
   > **Scope: memory writes *and* issue comments.** The same failure is more expensive in a comment, because a comment is re-read by every downstream role on the story. A fact already recorded in your own memory file is cited (`Developer_Memory.md` Fact N), never re-explained in a thread. Enforced by the Commenter gate in `Story_Standard.md §12`.

**Enforced file-level cap:** the value of **`**Memory file cap:**`** in this project's `{ENTRYPOINT}` (default **10,000** if the field is absent), measured with `wc -c` — not a line count. `≤ 200 lines` is retained only as non-enforced structural guidance; it does not track token cost (a fully rule-compliant 60-line file can already run ~7,250 tokens) and is never itself checked.

**Format:**

`## Stored Facts` uses its own four-field shape — distinct from `## Troubleshooting Facts` below, which keeps its existing shape unchanged:

```md
## Stored Facts

### Fact N
- **Rule:** the reusable decision/convention (this is line 1 — already required by rule 1 above)
- **Applies when:** the trigger condition that makes an agent need this
- **Evidence:** one-line pointer — story ID, `file:section` (point, don't mirror — rule 4)
- **Expires when:** the premise whose failure makes this fact wrong

## Troubleshooting Facts

### Fix N — <short label>
- **Problem:** Short label (e.g., "Docker sandbox fails to start")
- **Symptoms:** Exact error message or observable behavior
- **Root Cause:** Why it happened
- **Fix:** Exact commands/steps to resolve
- **Prevention:** What to check upfront to avoid this next time
```

> PO and BA record `## Stored Facts` only — the `## Troubleshooting Facts` section applies to roles that run tooling (Developer, Technical Lead, QA). The four-field Stored Facts shape applies uniformly across all six roles; Troubleshooting Facts is unchanged and stays scoped to Dev/TL/QA.

> **Developer, QA, and Technical Lead use a two-tier variant of this format, not the single file above** — see §8. PO, BA, and UI/UX Designer are unaffected.

---

## 8. Two-Tier Memory (Developer, QA, Technical Lead only)

Each role's `## Stored Facts` splits across two files:

- **`<Role>_Memory.md`** (live, bounded Standing Checks/Keyword Index on fresh/expired entry): **Standing Checks** — unconditional always-do actions, no recall needed (leave `*(none yet)*` if none qualify) — plus a **Keyword Index**: one line per fact, `### Fact N — <short title>` + a `Keywords:` line, no fact body. `## Troubleshooting Facts` stays here too, unchanged §1 shape.
- **`<Role>_Memory_Archive.md`** (conditional — open only on a keyword match): full four-field bodies, unchanged §1 shape.

**Retrieval:** bounded read only, never a full-file read of the archive — use the `read-section` skill (`.mt-agent-devkit/contracts/Read_Section.md`, heading marker `^### Fact `).

**Writing a fact:** append the body to the archive under the next number, then the matching index line — both files change together; an entry in one without the other is a defect. Numbers are never reused — retire gaps rather than renumbering.

**Caps:** the live file falls under §1's cap (the configured `**Memory file cap:**` value, default 10,000) and should stay far under it by construction (no fact bodies). The archive has no separate cap yet — treat §1's cap as its working ceiling until a retention policy is settled.

---

