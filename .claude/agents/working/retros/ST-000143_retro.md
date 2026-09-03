# Retrospective — ST-000143
**Date:** 2026-09-03
**Story:** TL loads 6,362 chars of code-review criteria on every spawn — split §2 by spawn shape

## Implementer — Technical Lead
### Impediments & Unclear Points
- `[instruction]` The story's own AC used "relocated ... as §5" and "bootstrap keeps a §2 gap" without saying whether the old heading should survive as a pointer stub. This file already had two working precedents for the opposite choice (`§11`/`§13` keep a stub heading with a one-line pointer) — I resolved the ambiguity toward a true gap (no stub) to match the literal AC wording and the Memory-file gap convention, but a design comment had to spell out the reasoning since the AC alone under-specified it.
- `[context]` Self-approval is structurally impossible when TL is both designer and Stage-1 implementer on the same story — this is the second devkit story I'm aware of hitting that pattern (first-hand: this one). Worth a standing note in `Story_Standard_TL.md` rather than re-deriving the reroute each time.
- `[failure]` My own design comment's Mitigation 1 claim ("the Stage 2 spawn prompt already names the target section — existing orchestrator pattern") was asserted from memory of the general pattern rather than verified against the actual file, and the reviewer caught it. Grep the cited file before asserting an "existing pattern" exists, every time — not just when a reviewer asks.

### Process Suggestions
- `[workflow]` The AC's own reference-values line (`43,269 = bootstrap 14,072 + ...`) was measurable directly from current file sizes (`wc -c`) before writing anything — worth normalizing "measure the actual file first" as a step in any spawn-load-reduction story rather than trusting the issue's stated figures at face value.
- `[failure]` `wc -c` on a working-tree file and `git show <ref>:<path> | wc -c` on the same content disagree when `core.autocrlf=true` (blob is LF-only, checkout is CRLF) — a real before/after byte-count comparison across a git ref must normalize both sides the same way (`git show ... | sed 's/$/\r/' | wc -c` reproduced the true checked-out byte count exactly here). Mixing the two silently understates or overstates a measured delta without erroring.

### What Worked Well
- The `Product_Owner_Rules_Read_On_Demand.md §1` task-shape template (`Triggered from …` / `read only:` / `Then execute:`) transferred cleanly to a different role with a different reduced-file list — confirms the mechanism generalizes rather than being PO-specific, which is exactly what this story bets on.
- Corrected prediction from round 2 (`1,867 + 11,418 + 3,959 = 17,244`) landed within 10 characters of the actual measured post-implementation answer-shape total (17,254) — the character-arithmetic approach this story leans on is reliable once the read set itself is correct.

## Reviewer — Developer
### Impediments & Unclear Points
- `[instruction]` The design's own gate-safety mitigation ("the Stage 2 spawn prompt already names the target file+section explicitly — existing orchestrator pattern") did not hold up on inspection: `Shared_Pipeline_Stages.md`'s Stage 2 Review/Behavioral step 2 says only "Reviewer reads its own instruction files, memory, and rules" — no section is named there today. Had to grep the actual pipeline file to catch this rather than trusting the design comment's characterization at face value.

### Process Suggestions
- `[workflow]` A design comment's cited "existing orchestrator pattern" for a safety mitigation should be treated as a claim to verify, not a fact to accept — grepping the named file directly (here `Shared_Pipeline_Stages.md`) took one tool call and caught a real gap between claimed and actual mitigation strength.
- `[workflow]` `Agent_Common_Bootstrap.md`'s own header ("read in full, do not section-read — §2/§4 exist precisely to be active before the situation is recognised") is an absolute, unconditional even for narrow task-shaped read sets. `Product_Owner_Rules_Read_On_Demand.md §1` already violates it (cites `§6` alone) — that existing violation should be treated as a bug to eventually fix, not precedent to extend into new role rule files.

### What Worked Well
- The character-count arithmetic in the design's §5/§6 predictions checked out almost exactly against actual file sizes (`Story_Standard_TL §9` = 1,867 chars, `Agent_Common_Bootstrap §4` = 995 chars, both matching the design's cited figures to the character) — the "measure the actual file first" habit TL's own retro entry recommends paid off immediately on the review side too.

## QA
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Product Owner
### Impediments & Unclear Points
*(pending)*

### Process Suggestions
*(pending)*

### What Worked Well
*(pending)*

## Orchestrator
### Observations
*(pending)*
