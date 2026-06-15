# Workflow Guide

Triggered by: `"workflow help"`

Read this file and present its contents to the user as a formatted summary. Do not spawn any agents.

---

## What Are These Workflows?

This project uses Claude Code as an AI Scrum team. Workflows are commands you type in the chat that trigger a multi-agent pipeline — Claude orchestrates specialized agents (Product Owner, Technical Lead, Developer, QA) to plan, implement, review, and close stories automatically.

---

## Sprint Lifecycle — Run in This Order

```
1. create stories       ← Create new stories in the backlog
2. plan next sprint     ← Assign backlog stories to a sprint, create sprint plan (PO + TL)
3. refine sprint        ← Raise and resolve questions before work starts
4. continue sprint      ← Execute all ready stories (implement → review → QA → close)
```

Steps 1–3 are **pre-sprint setup**. Step 4 is the **execution loop** — run it each time you want to advance the sprint.

---

## All Workflows at a Glance

| Command | When to use |
|---|---|
| `create stories` | You have requirements and want Claude to draft stories — saved as GitHub Issues (github mode) or local MD files (strict mode) |
| `plan next sprint [feature]` | Backlog stories exist and you are ready to plan the next sprint |
| `refine sprint` | Stories are planned and need questions answered before development |
| `continue sprint` | Stories are `ready` and you want to run the full pipeline |
| `start story ST-XXXXXX` | You want to run the pipeline for one specific story only |
| `resume story ST-XXXXXX` | A story is `blocked` and you have provided the missing information |
| `token probe` | Measure each role's onboarding read-cost (subagent tokens) before/after a docs change |
| `workflow help` | Show this guide |

---

## Scenario: Starting a Brand-New Sprint

```
Step 1 — create stories
         Describe the stories you need. Claude drafts them, you confirm, then
         they are saved to the backlog (GitHub Issues in github mode;
         local MD files in strict mode).

Step 2 — plan next sprint [feature-name]
         PO verifies current sprint is done, then PO + TL assign backlog stories
         to the next sprint and create the sprint plan.

Step 3 — refine sprint
         Developer, TL, and QA review each planned story and post any questions
         as comments. PO and TL answer. Stories are marked ready when clear.

Step 4 — continue sprint
         Claude picks up all status:ready stories and runs each through the full
         pipeline: implement → code review → QA → PO closes.
         Re-run "continue sprint" any time to pick up the next ready story.
```

---

## Scenario: Mid-Sprint

| Situation | Command |
|---|---|
| Stories are ready and you want to continue | `continue sprint` |
| You want to run just one story | `start story ST-XXXXXX` |
| A story got blocked and you have answered the questions | `resume story ST-XXXXXX` |
| A new story was added and needs refining | `refine sprint` |

---

## When NOT to Run a Workflow

- Do **not** run `plan next sprint` before `create stories` — the plan workflow expects stories to already exist in the backlog.
- Do **not** run `plan next sprint` if any story in the current sprint is still open — the workflow will stop and warn you, but save yourself the wait.
- Do **not** run `continue sprint` if no stories have `ready` status — there is nothing to pick up.
- Do **not** run `resume story` unless the blocked story's missing information has actually been provided — the workflow validates this and will stop if items are still missing.

---

## Story Status Flow

```
backlog → ready → in-progress → review → testing → done
                                          ↑
                               blocked (waiting on input)
                               resolved via "resume story ST-XXXXXX"
```

---

## Key Files for New Users

| What | Where |
|---|---|
| Project overview and architecture | `.claude/agents/context/Project_Priming.md` |
| All workflow trigger mappings | `CLAUDE.md` §Workflows |
| Agent roles and instruction files | `CLAUDE.md` §Agent Roster |
| Strict-mode story format and operations | `.claude/agents/rules/Strict_Mode_Story_Guide.md` |
| CI/CD story validation (github mode only) | `.claude/agents/rules/CICD_Validation_Guide.md` |
