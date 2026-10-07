# Start Story Workflow

Triggered by: `"start story ST-XXXXXX"` or `"/story ST-XXXXXX"` in the selected provider entrypoint

The orchestrator runs the [Shared Pipeline Stages](Shared_Pipeline_Stages.md) for the specified story only. **Pipeline stops after Stage 4 — PO does NOT promote the next story.**

---

## Stage Entry Check (run before anything else)

**Read the story's current GitHub label and route:**

| Story label | Entry point |
|---|---|
| `status:ready` | Story Base Preflight, Bug Reproduction Pre-Flight, then Stage 0 — Implementer Routing |
| `status:in-progress` | Resume the recorded story and stage from the pipeline state file; use the existing story branch and session. Do not rerun new-story `inspect` or `create`. If the state file is missing or names another story, stop for state recovery before any write. |
| `status:review` | Stage 2 — Review |
| `status:testing` | Stage 3 — QA Validation |
| `status:blocked` | Stop — story is blocked on external input; notify user to run `resume story ST-XXXXXX` once the required information has been provided |
| `status:done` | Stop — story is already closed; notify user |

> If the status is missing or unrecognised, stop and notify the user before proceeding.
> Bug Reproduction Pre-Flight runs only for a new `status:ready` entry (see `Shared_Pipeline_Stages.md`). A resumed `status:in-progress` story continues from its recorded stage without repeating preflight or branch creation. If pre-flight determines **not reproduced**, report the result to the user and stop — do not proceed to Stage 0.

---

## Pipeline Rules

- Targets only the story specified in the trigger command
- Loop limit: max 3 Impl→Reviewer or Impl→QA cycles before escalating to the user
- **Session reuse** — always resume an existing session before spawning
- **Bug Reproduction Pre-Flight not-reproduced outcome** — report to the user and stop; do not proceed to Stage 0 (see `Shared_Pipeline_Stages.md`)
- **Pipeline stops after Stage 4 completes for the targeted story**
- **Stage 5 (Retrospective)** — after Stage 4's observation check completes, check the Stage 5 heading in `Shared_Pipeline_Stages.md`: if `[BETA: enabled]`, run Stage 5; if `[BETA: disabled]`, skip and go directly to Retro Review.
- **Retro Review** — after Stage 5 (or immediately after Stage 4 if Stage 5 is disabled):
  1. Read `{RUNTIME_ROOT}/retros/ST-XXXXXX_retro.md`
  2. Collect all signal-tagged items (`[context]`, `[instruction]`, `[workflow]`, `[failure]`) from every section
  3. Present collected items to the user as proposed improvements; for each approved item, apply the change targeting the right artifact (same routing as the Batch Retro Review in Sprint_Workflow.md)
  4. Read `Sprint` from this story's state; append its story section to
     `{RUN_ROOT}/retros/sprint_N_summary.md` (see Sprint_Workflow.md for format).
  5. Delete `{RUNTIME_ROOT}/retros/ST-XXXXXX_retro.md`
  6. Delete the state file

> The pipeline state file format and write rules are defined in [Sprint_Workflow.md](Sprint_Workflow.md) — the same file is shared between Sprint and Start Story workflows.
