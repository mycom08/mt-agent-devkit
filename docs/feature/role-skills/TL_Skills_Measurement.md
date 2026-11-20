# Technical Lead Skills — Read Measurement

**Feature:** `role-skills`
**Story:** ST-000328
**Design:** `Dev_Skills_Proposal.md` §2, §10 (modeled on `Dev_Skills_Measurement.md`)
**Date:** 2026-11-20

Bytes read and read calls for an internal Technical Lead spawn, **before** (base `78b3e46`, rules files) and **after** (ST-000328, skills). This is byte arithmetic over real manifests, not a token measurement.

## Method

- Implementation, review and question rows come from `read_manifest.py build` against the actual registry and files of each tree (provider `claude`, layout `internal`, mode `github`, fresh session, no triggers). The refinement spawn has no TL manifest task, so it uses the implementation spawn set minus its task reads (`tl_implementation_*`), plus the design guidance: nothing extra before (design standards sat in the Bootstrap), and `tl-design` after (the new `design_standards` trigger).
- **Bytes** is the covered content of each read: the whole file, or the extracted section for a section read. **Read calls** counts one native read per manifest entry. A section read is one call.
- **Excluded** in both columns: the story context inputs and the runtime Working Record and memory, which are local state and the same size before and after.

## Results

| Spawn type | Before: bytes | Before: calls | After: bytes | After: calls | Bytes change |
|---|---:|---:|---:|---:|---:|
| Implementation (TL as implementer) | 58,663 | 10 | 43,746 | 13 | −25% |
| PR review | 59,157 | 9 | 42,455 | 12 | −28% |
| Sprint refinement | 51,191 | 7 | 37,758 | 11 | −26% |
| Question (answer on the issue) | 36,502 | 6 | 31,762 | 9 | −13% |

## What Each Spawn Reads

Shared by every row: provider adapter (5,636) and `technical_lead_instructions.md` (5,178 before, 4,531 after). Every row except the question also reads `Project_Priming_Bootstrap.md` (7,629) and Priming On-Demand §3 (1,021).

| Spawn type | Before | After |
|---|---|---|
| Common and role rules | `Agent_Common_Bootstrap.md` (19,352) + `Story_Standard_TL.md` (2,952) + `Technical_Lead_Rules_Bootstrap.md` (9,423) | `pre-work`, `agent-security`, `token-efficiency`, `shell-rules`, `retro` (15,389) + `tl-core` (1,548) |
| Implementation | + `git-workflow`, `pre-pr-gate`, On-Demand §4 (916) | + `git-workflow`, `pre-pr-gate`, `tl-implement` (1,436) |
| PR review | + `pr-review`, On-Demand §5 (4,697) | + `pr-review`, `tl-review` (3,405) |
| Sprint refinement | no task reads | + `tl-design` (2,004) |
| Question | `Agent_Common_Bootstrap.md` + On-Demand §6 (1,076), Story Standard TL §9 (445), `comment` | five spawn-time skills + `tl-answer` (1,391), `comment` (the §9 read and the `comment` read are the same skill and are read once) |

## Reading the Numbers

- **Bytes fall for every spawn type**, by a quarter for the three spawns that read priming. The Common Bootstrap, `Story_Standard_TL.md` and the Rules Bootstrap (31.7 KB) become 17 KB of spawn-time skills, and the design standards, unused by an implementation or a review, load only when a design is made.
- **The question spawn falls least (−13%)**: it never read the Rules Bootstrap or priming, so the Common split is its only saving, and its two comment reads collapse into one.
- **Read calls rise by 3 to 4 per spawn**, as the design expected: one call per skill instead of three large files. Calls drive cost through transcript resends (token-efficiency conventions), so the saving per spawn is smaller than the byte change suggests.
- **Review no longer loads design standards.** A review that must judge compliance with an approved design reads the design from the story, and loads `tl-design` only through the `design_standards` trigger or the load map when it evaluates an approach.
