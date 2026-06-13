# Token Probe Workflow

Triggered by: `"token probe"`

Measures the **onboarding read-cost** of each agent role in isolation — the tokens an agent spends reading its pre-work files (Project Priming, Working Record, Rules, Memory, Agent_Common) before doing any task. Run this **before and after** a docs change to quantify the effect. Results go in `.claude/agents/retros/token_baseline.md`.

> This is a controlled measurement, not a real pipeline run. It deliberately excludes story work and GitHub I/O so the only variable is the onboarding read path.

---

## Step 1 — Capture the doc version

Run `git rev-parse --short HEAD` and note it as `docs_sha`. If `.claude/agents/` has uncommitted changes, commit them first (or append `-dirty` to the sha) so the baseline row maps to a known doc state.

## Step 2 — Probe each role

For each role in `Developer`, `Technical Lead`, `QA`, `Product Owner`, `Business Analyst`:

1. **Spawn** the role agent with this exact task prompt:

   > Complete your standard pre-work reading per your instruction file (Project Priming, your Working Record, your Rules, your Memory, and Agent_Common). **Do not** read any GitHub issue, **do not** sync story statuses with GitHub, and **do not** perform any task. When your reading is done, reply with exactly `READY` and nothing else.

2. On completion, read the `<usage>` block and record `subagent_tokens` for that role. If no `<usage>` block is returned, record `n/a`.

Spawn fresh each time (do not resume) — onboarding cost only applies to a cold start.

## Step 3 — Record the baseline

Append one row to the table in `.claude/agents/retros/token_baseline.md`:

```
| <docs_sha> | <YYYY-MM-DD> | <Dev tokens> | <TL tokens> | <QA tokens> | <PO tokens> | <BA tokens> | <optional note> |
```

## Step 4 — Report the delta

If a previous row exists under a different `docs_sha`, present a per-role comparison to the user: tokens before → after, absolute and percent change. State the total across all five roles. If no prior row exists, report this run as the new baseline.

> Keep `token_baseline.md` — it is the historical record. Do not delete it during sprint cleanup.
