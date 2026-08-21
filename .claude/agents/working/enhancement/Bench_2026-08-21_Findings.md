# Benchmark 2026-08-21 — `agent-enhancement` vs `main`

**Method:** `Harness_Benchmark_Guide.md`. Two Developer spawns, one story, paired issues.
**Arms:** A = `agent-enhancement` (`df53016`, treatment) · B = `main` (`d3d32aa`, baseline). Baseline run first.
**Story:** ignore `.antigravity/` runtime files — issues #144 (A) / #145 (B). PRs #147 (A) / #146 (B).

---

## 1. Headline

**Pre-work read set fell 43.5%, from 58,019 to 32,780 characters.** This is the finding that holds.

The token figures moved the same direction but are not significant (§3): 58,323 vs 66,778 reported `subagent_tokens` (−12.7%), 16,850 vs 23,100 self-reported (−27.1%).

## 2. This is the first actual-vs-actual comparison in the series

Both arms read their full mandated set. Every prior round had at least one arm skipping mandatory reads, which made the "before" figure a measure of non-compliance rather than of the harness (`Agent_Common_Split_Findings.md §2`). That defect is absent here, so the delta is attributable.

| Arm B — `main` | Bytes | Arm A — `agent-enhancement` | Bytes |
|---|---|---|---|
| `developer_instructions.md` | 3,698 | `developer_instructions.md` | 2,867 |
| `Agent_Common.md` | 20,282 | `Agent_Common_Bootstrap.md` | 10,390 |
| `Project_Priming.md` | 11,530 | `Project_Priming_Bootstrap.md` | 6,110 |
| `Developer_Rules.md` | 11,688 | `Developer_Rules_Bootstrap.md` | 3,628 |
| `Developer_Memory.md` | 4,292 | `Developer_Memory.md` | 4,305 |
| **Mandated subtotal** | **51,490** | **Mandated subtotal** | **27,300** (−47.0%) |
| `Story_Standard_Dev.md` (§1 gate) | 6,529 | `Story_Standard_Dev.md` (§1 gate) | 5,480 |
| **Total** | **58,019** | **Total** | **32,780** (−43.5%) |

Arm A additionally section-read `Developer_Rules_Read_On_Demand.md` §1/§5/§6 once triggers fired (~1,100 tok self-estimated) — the tier working as designed. Arm B bounded-read one archive fact (6 lines) rather than the 11k file, so the archive is not a differentiator.

Both arms produced **14 files changed** with the same 12 un-tracked files. Arm B added 8 `.gitignore` lines (3 prefixes plus comment annotation), arm A added 3. Materially equivalent; arm B did marginally more, which works against arm A and does not threaten the result.

## 3. What this does not establish

- **n=1 per arm.** The 2026-08-20 pair varied ~23% between two runs of one story. The −12.7% actual-token delta sits **inside** that band and should not be quoted as a saving. Only the read-set delta is a direct byte measurement rather than an estimate.
- **`subagent_tokens` recorded `(unlabelled)`** — the completion reports did not say per-call or cumulative, and the figure remains unreliable in general.
- **Task shape favours the treatment arm.** This was a narrow, fully-specified story. `Bootstrap_OnDemand_Split_Notes.md` measured the tiered harness at −63% on narrow tasks and **+15% on full story spawns**. A full TL→Dev→QA story spawn is still unmeasured, and is the path we run most.
- **Orchestrator side held constant.** The trace block was pasted on both arms, so arm B had the format in `Agent_Common.md §11` *and* in the prompt. That is the variable `1a1fa90` changed and it is not isolated here.

## 4. A contamination leak the guide's controls did not stop

Arm B reported that its spawn prompt "points at bootstrap/read-on-demand filenames that do not exist on this branch," and spent an `ls` call resolving it. **The prompt named no such files** — only the unsplit `Agent_Common.md`, `Project_Priming.md`, `Developer_Rules.md`.

Those names existed in exactly two places the agent could reach: the Orchestrator Working Record, and `token-trace_sprint/readme_check_dev_steps_done.md` — a prior trace sitting in the directory it had to write into. Arm 1 of ST-000131 is on record reading a prior trace as a format example; the same path is the likeliest source here.

**Two consequences.** Snapshot-and-restore makes the arms *equal* but does not make them *clean* — the retained artifacts are post-split and actively mislead a baseline-arm agent. And the failure mode is the one `Bootstrap_OnDemand_Split_Notes.md` named: the agent reconstructed from absorbed shape and misattributed the source, rather than re-reading what it was actually given.

**Control to add to `Harness_Benchmark_Guide.md §4`:** empty `token-trace_sprint/` for the duration of a benchmark, restoring it afterwards, rather than merely equalising it.

## 5. Incidental findings

- `$TMPDIR` is unset under the Bash tool on this machine, so `Story_Standard_Dev.md §15`'s instruction to write `gh` body files to `/tmp/body.md` fails with a permission error. Cost arm A one retry. **Worth a story** — it hits every `gh pr create` on Windows.
- `.claude/agents/internal/` has no `.antigravity/` mirror either. Latent (nothing tracked there today), independently noted by both arms.

---

## Version

**Version:** 1.0 — Created 2026-08-21. First benchmark run under `Harness_Benchmark_Guide.md`.
