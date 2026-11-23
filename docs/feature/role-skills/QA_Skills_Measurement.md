# QA Skills — Read Measurement

**Feature:** `role-skills`
**Story:** ST-000331
**Design:** `Dev_Skills_Proposal.md` §2, §10 (modeled on `TL_Skills_Measurement.md`)
**Date:** 2026-11-23

Bytes read and read calls for an internal QA spawn, **before** (base `188e40f`, rules files) and **after** (ST-000331, skills). This is byte arithmetic over real manifests, not a token measurement.

## Method

- The story validation and regression check rows come from `read_manifest.py build` against the actual registry and files of each tree (provider `claude`, layout `internal`, mode `github`, fresh session, task `qa`). The regression check adds the `regression_check` trigger after the change; before the change the Rules Bootstrap already carried the regression rule, so the two rows are equal.
- The refinement spawn has no QA manifest task, so it uses the validation spawn set minus its task reads (`acceptance_contract`, and after the change `qa_validate` and `qa_testing`): QA has no refinement-only guidance before or after. The question spawn is that set plus `comment`, which the load map and the old Story Standard QA section 9 both name before a comment.
- **Bytes** is the covered content of each read: the whole file, or the extracted section for a section read. **Read calls** counts one native read per manifest entry. A section read is one call.
- **Excluded** in both columns: the story context inputs and the runtime Working Record and memory, which are local state and the same size before and after.

## Results

| Spawn type | Before: bytes | Before: calls | After: bytes | After: calls | Bytes change |
|---|---:|---:|---:|---:|---:|
| Story validation | 58,478 | 8 | 45,804 | 13 | −22% |
| Regression check | 58,478 | 8 | 47,855 | 14 | −18% |
| Refinement | 53,420 | 7 | 35,310 | 10 | −34% |
| Question (answer on the issue) | 58,235 | 8 | 40,125 | 11 | −31% |

## What Each Spawn Reads

Shared by every row: provider adapter (5,636), `Project_Priming_Bootstrap.md` (7,629) and Priming On-Demand §3 (1,021). The instructions file is 4,533 before and 4,323 after.

| Spawn type | Before | After |
|---|---|---|
| Common and role rules | `Agent_Common_Bootstrap.md` (19,352) + `Story_Standard_QA.md` (3,087) + `QA_Rules_Bootstrap.md` (12,162) | `pre-work`, `agent-security`, `token-efficiency`, `shell-rules`, `retro` (15,389) + `qa-core` (1,312) |
| Story validation | + `Story_Standard.md` §14 (5,058), Priming On-Demand §3 | + `Story_Standard.md` §14, `qa-validate` (2,705), `qa-testing` (2,731), Priming On-Demand §3 |
| Regression check | same set as validation (the Rules Bootstrap holds the regression rule) | the validation set + `qa-regression` (2,051) |
| Refinement | validation set minus §14 | validation set minus §14, `qa-validate` and `qa-testing` |
| Question | refinement set + `comment` (4,815) | refinement set + `comment` |

## Reading the Numbers

- **Bytes fall for every spawn type.** The Common Bootstrap, `Story_Standard_QA.md` and the Rules Bootstrap (34.6 KB) become 16.7 KB of spawn-time skills, and the hotfix and regression rules, unused by most spawns, load only at their point of use.
- **Validation falls least (−22%)** because it is the one spawn that needs the testing and sign-off rules: `qa-validate` and `qa-testing` (5.4 KB) replace the same rules inside the Rules Bootstrap. The regression check pays 2.1 KB for `qa-regression`, and still reads 18% less than before.
- **Refinement and question fall by a third.** They never needed the task rules, so the Common split is their whole change.
- **Read calls rise by 3 to 6 per spawn**, as the design expected: one call per skill instead of three large files. Calls drive cost through transcript resends (token-efficiency conventions), so the saving per spawn is smaller than the byte change suggests.
- **The hotfix spawn** reads `qa-hotfix` (654 bytes) through the `post_done_bug` trigger instead of an On-Demand section; it needs no validation skills.
