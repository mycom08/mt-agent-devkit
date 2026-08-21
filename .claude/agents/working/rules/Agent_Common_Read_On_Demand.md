# Agent Common — Read On Demand

**Applies to:** All agents (Developer, Technical Lead, QA, Product Owner, Business Analyst, UI/UX Designer)
**Purpose:** Companion to `Agent_Common_Bootstrap.md` (the bootstrap-mandatory sections read at every spawn — including the Working Record's write format, folded into `Agent_Common_Bootstrap.md §1` since it fires on every session, not just conditionally). Nothing in this file is read automatically — `Agent_Common_Bootstrap.md §5`'s routing table names the one section to fetch when its trigger fires. §8 is devkit-internal only (not mirrored to `templates/`). Where this file and a role-specific rule disagree, the role-specific rule wins.

> **Two things to know before extracting a section from this file.**
> 1. **There are two intentional gaps.** Numbering runs §1, §2, §3, §5, §6, §8. **§4** is where the pre-split *Working Record* section sat before it was folded into `Agent_Common_Bootstrap.md §1`. **§7** is where the *Token-Trace Log* sat before it left the agent rules altogether for `Orchestrator_Guide.md`. Numbers are never reused: leave the gap rather than renumbering, so a stale citation resolves to nothing rather than to a different rule (same convention as `Technical_Lead_Memory.md`'s fact numbering).
> 2. **§1 contains unnumbered sub-headings** (`## Stored Facts`, `## Troubleshooting Facts`). Bound a section extraction on **numbered** headings only (`grep -nE "^## [0-9]+\."`) — a bare `^## ` treats those sub-headings as the end of §1 and silently returns a truncated section, dropping the format block and §1's closing two-tier note.

---

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
2. **Corrections rewrite in place.** When a fact is superseded or a number corrected, edit the fact body to the current truth and keep only a one-line `Corrected: <date> — <what changed>` note. Never stack correction addenda under stale text.
3. **Prune on write, verified on schedule.** When adding a fact, still check whether it obsoletes an existing one — merge or delete the loser. This on-write check is not the only pruning mechanism: broader corpus staleness (expired-premise facts, history-only entries, duplicates missed at write time) is caught by the scheduled once-per-sprint pass in `Retro_Rules.md` (Sprint-End Memory Pruning) — do not rely on noticing it yourself mid-task.
4. **Point, don't mirror.** If the substance lives in a committed project doc or another role's session artifacts, store a one-line pointer plus only your role-specific delta — never a full re-derivation.
   > **Scope: memory writes *and* issue comments.** The same failure is more expensive in a comment, because a comment is re-read by every downstream role on the story. A fact already recorded in your own memory file is cited (`Developer_Memory.md` Fact N), never re-explained in a thread. Enforced by the Commenter gate in `Story_Standard.md §12`.

**Enforced file-level cap:** **≤ 40,000 characters** per memory file, measured with `wc -c` — not a line count. `≤ 200 lines` is retained only as non-enforced structural guidance; it does not track token cost (a fully rule-compliant 60-line file can already run ~7,250 tokens) and is never itself checked.

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
- **Problem:** Short label (e.g., "gh CLI authentication fails")
- **Symptoms:** Exact error message or observable behavior
- **Root Cause:** Why it happened
- **Fix:** Exact commands/steps to resolve
- **Prevention:** What to check upfront to avoid this next time
```

> PO and BA record `## Stored Facts` only — the `## Troubleshooting Facts` section applies to roles that run tooling (Developer, Technical Lead, QA). The four-field Stored Facts shape applies uniformly across all six roles; Troubleshooting Facts is unchanged and stays scoped to Dev/TL/QA.

> **Developer, QA, and Technical Lead use a two-tier variant of this format, not the single file above** — see §8. PO, BA, and UI/UX Designer are unaffected.

---

## 2. Troubleshooting Protocol

Applies on any tooling/environment blocker: `gh` CLI auth failures · script syntax errors · shell script fails to run · CI YAML errors.

**Step 1 — Check memory first.** Scan your memory file's `## Troubleshooting Facts` for a matching entry. If a fix is recorded, apply it directly — do not re-diagnose.

**Step 2 — Diagnose and fix.** If no match, find the root cause and fix it properly. Do not work around it or skip the failing step.

**Step 3 — Save to memory (mandatory).** After resolving, record the fix under `## Troubleshooting Facts` using the §1 format before resuming.

> **Gate:** Do not resume the blocked task until the fix is recorded in memory.

---

## 3. End-of-Work Retrospective

Before reporting back to the orchestrator, write your retrospective section to the story retro file:

1. Read `.claude/agents/working/rules/Retro_Rules.md` for the three questions and format
2. Open `.claude/agents/working/retros/ST-XXXXXX_retro.md` (story ID is in your spawn prompt)
3. Overwrite the `*(pending)*` placeholders in **your own section only** — see the section name in your role instructions
4. Then report back

---

## 5. Stage-Transition Commit (implementer & reviewer roles)

Before signaling completion to the orchestrator, commit any **agent memory file** changes made during the session.

**Mode: github:**
- Commit memory files only — the Working Record is gitignored and must not be committed
- Never commit any file under `.claude/agents/working/` other than memory files
- Commit message: `Agent: <short description>` — under 50 characters (e.g., `Agent: Update QA memory`)
- Add `[skip ci]` on its own line in the commit message **body** — memory-only pushes must never trigger CI. GitHub Actions skips push-triggered workflows when the **head commit** of the push contains `[skip ci]`, so if unpushed code commits exist on the branch, push those first and push the memory commit separately
- If no memory files changed, skip the commit — do not create an empty commit
- Push before reporting stage completion

> **Gate (github mode only):** Do not signal stage completion until the commit is pushed (if applicable).

---

## 6. Credential-Gated Verification

Applies whenever a story's verification requires a runtime secret (API token, PAT, signing key, DB password, etc.) that is not available in your working environment.

- **Never self-approve a skip.** A dummy-value substitute, or an analogy to a different code path/CI job that happens to use the same secret, is not equivalent to exercising the real credential — do not treat it as sufficient verification.
- **Stop and report** the specific constraint: what credential is missing, why, what you verified without it, and what the credential would additionally prove.
- **Wait** for either the real credential or explicit user authorization to proceed. Quote that authorization in your eventual sign-off or retro.

---

## 7. Token-Trace Log — RETIRED

> **The Token-Trace Log is no longer an agent-tier rule at all.** It sat here as §7, moved to `Agent_Common_Bootstrap.md §6` on 2026-08-21, and on 2026-08-21 left the agent rules entirely: the format now lives only in `Orchestrator_Guide.md`, and the orchestrator injects it verbatim into the spawn prompt of any agent it wants a trace from. An agent never reads a rule to learn the format — it reads the prompt. That removes the circularity the bootstrap move was chasing (a trace must account for the pre-work reads, which happen before any rule could be fetched) without charging any spawn for a convention most spawns never use. §7 stays retired and is never reused; a stale `§7` or `Agent_Common_Bootstrap.md §6` citation must resolve to nothing.

---

## 8. Two-Tier Memory (devkit-internal pilot — Developer, QA, Technical Lead only)

Issue #118 follow-up, not mirrored to `templates/`. Each role's `## Stored Facts` splits across two files:

- **`<Role>_Memory.md`** (live, read every spawn): **Standing Checks** — unconditional always-do actions, no recall needed (leave `*(none yet)*` if none qualify) — plus a **Keyword Index**: one line per fact, `### Fact N — <short title>` + a `Keywords:` line, no fact body. `## Troubleshooting Facts` stays here too, unchanged §1 shape.
- **`<Role>_Memory_Archive.md`** (conditional — open only on a keyword match): full four-field bodies, unchanged §1 shape.

**Retrieval:** bounded read only, never a full-file read of the archive — use the `read-section` skill (`.claude/skills/read-section/`, heading marker `^### Fact `).

**Writing a fact:** append the body to the archive under the next number, then the matching index line — both files change together; an entry in one without the other is a defect. Numbers are never reused — retire gaps rather than renumbering (see `Technical_Lead_Memory.md`'s "Numbering gaps ... do not renumber").

**Caps:** the live file falls under §1's ≤ 40,000-char cap and should stay far under it by construction (no fact bodies). The archive has no separate cap yet — treat §1's cap as its working ceiling until this pilot's retention policy is settled.
