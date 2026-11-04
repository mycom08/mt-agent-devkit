# Developer Skills — Read Measurement

**Feature:** `role-skills`
**Story:** ST-000309 (B)
**Design:** `Dev_Skills_Proposal.md` §2, §10 (B)
**Date:** 2026-11-04

Bytes read and read calls for an internal Developer spawn, **before** (base `4f40388`, rules files) and **after** (ST-000309, skills). This is byte arithmetic over real manifests, not a token measurement. A native token comparison is out of scope (design §2).

## Method

- Story and peer-review rows come from `read_manifest.py build` against the actual registry and files of each tree (provider `claude`, layout `internal`, mode `github`, fresh session). Refinement and question spawns have no Developer manifest task, so they use the spawn set that the implementation manifest gives, minus its task reads, plus the task guidance each load map names.
- **Bytes** is the covered content of each read: the whole file, or the extracted section for a section read. **Read calls** counts one native read per manifest entry. A section read is one call.
- **Excluded** in both columns: the story context inputs and the runtime Working Record and memory, which are local state and the same size before and after.
- "Through PR and handoff" adds the triggers a full story fires: `shell_safety`, `story_comment`, `pre_pr`, `runtime_handoff`, `completion`. After the change it also adds `git-workflow` and `dev-deliver`, which the load map names but no manifest trigger routes.

## Results

| Spawn type | Before: bytes | Before: calls | After: bytes | After: calls | Bytes change |
|---|---:|---:|---:|---:|---:|
| Story, at spawn | 57,698 | 6 | 39,061 | 11 | −32% |
| Story, through PR and handoff | 102,996 | 12 | 55,070 | 17 | −47% |
| Peer review | 60,072 | 8 | 40,111 | 11 | −33% |
| Sprint refinement | 58,848 | 6 | 37,950 | 10 | −36% |
| Question (answer on the issue) | 62,041 | 7 | 40,636 | 10 | −35% |

## What Each Spawn Reads

Shared by every row: provider adapter (5,710), `developer_instructions.md` (4,253 before, 4,566 after) and `Project_Priming_Bootstrap.md` (8,692).

| Spawn type | Before | After |
|---|---|---|
| Common and role rules | `Agent_Common_Bootstrap.md` (19,352) + `Developer_Rules_Bootstrap.md` (18,670) | `pre-work`, `agent-security`, `token-efficiency`, `shell-rules`, `retro` (15,389) + `dev-core` (1,464) |
| Story | + Priming On-Demand §3 | + `dev-implement`, Priming On-Demand §3 |
| Story, through PR | + Shell Safety, `comment`, On-Demand §5 and §20, and full re-reads of the Common and Developer Bootstraps (`completion`, `pre_pr`) | + `comment`, `change-metadata`, `pre-pr-gate`, `handoff`, `git-workflow`, `dev-deliver`; `shell_safety` and the `completion` retro read are deduplicated |
| Peer review | + Developer On-Demand §14, §16 | + `pr-review` |
| Sprint refinement | + Developer On-Demand §15 | + `dev-refine` |
| Question | + `comment`, Developer On-Demand §20 | + `comment` |

## Reading the Numbers

- **Bytes fall for every spawn type**, by a third at spawn. The two Bootstraps (38 KB) become 17 KB of spawn-time skills, and the role guidance a spawn does not use (pre-PR, git, delivery) moves to point-of-use skills.
- **A full story falls most (−47%)**, because the old `pre_pr` and `completion` triggers re-read the full Developer and Common Bootstraps, while the new triggers add small skills and drop what the spawn set already holds.
- **Read calls rise by 3 to 5 per spawn**, as design §2 expected: one call per skill instead of two large files. Calls drive cost through transcript resends (token-efficiency conventions), so the saving per spawn is smaller than the byte change suggests.
- The design's "about 15 KB" estimate for a narrow spawn counted role and Common text only. Here the adapter, instructions and priming (19 KB, unchanged) are included, so narrow spawns land near 38–41 KB.
