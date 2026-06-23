<!-- Included by: templates/github/workflows/Start_Story_Workflow_template.md, templates/strict/workflows/Start_Story_Workflow_template.md -->

<!-- SHARED-START -->
# Start Story Workflow

Triggered by: `"start story ST-XXXXXX"` or `"/story ST-XXXXXX"` in CLAUDE.md

The orchestrator runs the [Shared Pipeline Stages](Shared_Pipeline_Stages.md) for the specified story only. **Pipeline stops after Stage 4 — PO does NOT promote the next story.**

---

## Stage Entry Check (run before anything else)

**If `Mode: github`** — read the story's current GitHub label and route:

| Story label | Entry point |
|---|---|
| `status:ready` or `status:in-progress` | Stage 0 — Implementer Routing |
| `status:review` | Stage 2 — Review |
| `status:testing` | Stage 3 — QA Validation |
| `status:blocked` | Stop — story is blocked on external input; notify user to run `resume story ST-XXXXXX` once the required information has been provided |
| `status:done` | Stop — story is already closed; notify user |

**If `Mode: strict`** — read `**Status:**` field from `.claude/agents/docs/stories/ST-XXXXXX.md` and route using the same table above (status values are identical — see `Strict_Mode_Story_Guide.md` §Status Values).

> If the status is missing or unrecognised, stop and notify the user before proceeding.

---

## Pipeline Rules

- Targets only the story specified in the trigger command
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- **Pipeline stops after Stage 4 completes for the targeted story**
- **Stage 5 (Retrospective)** — after Stage 4's observation check completes, check the Stage 5 heading in `Shared_Pipeline_Stages.md`: if `[BETA: enabled]`, run Stage 5; if `[BETA: disabled]`, skip and go directly to Retro Review.
- **Retro Review** — after Stage 5 (or immediately after Stage 4 if Stage 5 is disabled):
  1. Read `.claude/agents/retros/ST-XXXXXX_retro.md`
  2. Collect all signal-tagged items (`[context]`, `[instruction]`, `[workflow]`, `[failure]`) from every section
  3. Present collected items to the user as proposed improvements; for each approved item, apply the change targeting the right artifact (same routing as the Batch Retro Review in Sprint_Workflow.md)
  4. Read `Sprint` from the state file; append a story section to `.claude/agents/retros/sprint_N_summary.md` (see Sprint_Workflow.md for format; create the file if it does not exist)
  5. Delete `.claude/agents/retros/ST-XXXXXX_retro.md`
  6. Delete the state file

> The pipeline state file format and write rules are defined in [Sprint_Workflow.md](Sprint_Workflow.md) — the same file is shared between Sprint and Start Story workflows.
<!-- SHARED-END -->
