# Developer Rules — Bootstrap

**Applies to:** Developer agent — devkit's own team only (`.claude/agents/working/`).
**Reference from:** `.claude/agents/working/instructions/developer_instructions.md`
**Purpose:** The whole of the Developer's bootstrap-tier rules — everything that is true on *every* Dev spawn regardless of what the task is, including a spawn that never touches a story. Read this file in full at step 3 of `Agent_Common_Bootstrap.md §1`. Read nothing else from the Developer rules set until a trigger below actually fires.

---

## 1. On-Demand Rules — Routing Table

Nothing below this table is loaded at spawn. When a trigger fires, fetch **only** the named section with the `read-section` skill (`.claude/skills/read-section/`, bound on `^## [0-9]+\.`) — not the whole file.

| Trigger | Fetch |
|---|---|
| You have been assigned a story — **before writing any file** | `Developer_Rules_Read_On_Demand.md §1` (mandatory-reading gate → `Story_Standard_Dev.md`), then `§2` (pre-start steps) and `§3` (status management) |
| About to branch, commit, or open a PR | `Developer_Rules_Read_On_Demand.md §5` (Pre-PR Gate) and `§6` (Git Workflow) |
| Creating a file under `templates/`/`workflows/`, or writing a `changes.json` entry | `Developer_Rules_Read_On_Demand.md §4` (File Naming) |
| Creating or updating a project document | `Developer_Rules_Read_On_Demand.md §8` (Document Placement) |
| Blocked on a story and reporting it | `Developer_Rules_Read_On_Demand.md §7` (Reporting & Blockers) |
| A question surfaces mid-implementation, or a live user instruction contradicts the issue thread | `Developer_Rules_Read_On_Demand.md §12–§13` |
| Orchestrator assigns you as peer reviewer for a TL-implemented story | `Developer_Rules_Read_On_Demand.md §14` (checklist) and `§16` (full reviewer procedure) |
| Orchestrator asks you to run a Sprint Refinement | `Developer_Rules_Read_On_Demand.md §15` |
| A post-Done bug (hotfix) | `Developer_Rules_Read_On_Demand.md §17` |
| Signaling stage completion to the orchestrator, or you changed a memory file this session | `Agent_Common_Read_On_Demand.md §5` (Stage-Transition Commit) — **mandatory before handoff** |
| A tooling/environment blocker | **First** scan your own `## Troubleshooting Facts` in `Developer_Memory.md` for a recorded fix and apply it without re-diagnosing; fetch `Agent_Common_Read_On_Demand.md §2` only for the diagnose-and-record-back procedure |

> Triggers shared by all six roles that are not restated here — writing a memory fact, the end-of-work retro, credential-gated verification — are routed by `Agent_Common_Bootstrap.md §5`. That table and this one are both live; neither supersedes the other.

---

## 2. Always-On

- Keep working record updates short and fact-based (file paths, PR #s, story IDs, commits).
- **Working record retention:** delete entries older than the 3 most recent story entries before writing a new one (see `Agent_Common_Bootstrap.md §1` for the char cap and snapshot format).

---

## Version

**Version:** 1.1 — Routing table repointed to `Developer_Rules_Read_On_Demand.md` §12–§17 after `Developer_Rules_Extended.md` was merged into it (one on-demand file per role, not two).
**Previous:** 1.0 — Created 2026-08-21. Bootstrap tier split out of `Developer_Rules.md` v1.5; §1–§6/§8 and §7's blocker bullet moved to `Developer_Rules_Read_On_Demand.md` at their original numbers, §9–§11 folded into §1's routing table above. Devkit's own team only — the distributable `.claude/agents/templates/rules/Developer_Rules_template.md` is unchanged.
