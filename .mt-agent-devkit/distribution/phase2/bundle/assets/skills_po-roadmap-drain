---
name: po-roadmap-drain
description: Drain every story a roadmap or planning doc defines into a tracked status:backlog issue, idempotently, whenever that roadmap is authored or updated.
---

# PO Roadmap Drain

**Requires:** `po-write-story`, `po-plan-docs`

**Mandatory whenever you author or update a roadmap/planning doc that defines stories ahead of pickup**: the Implementation Roadmap or any `*Roadmap*.md` under `docs/feature/<feature_name>/plan/`, where a story tracker exists (`init project` has run). It does not apply to the Analyst workflow's pre-repo `implementation_roadmap.md`, which has no tracker or real story IDs yet.

Every story the roadmap defines becomes a tracked `status:backlog` story **at this same moment**. Do not defer it to sprint planning; `Plan_Sprint_Workflow.md` Stage 1 step 7 is only a drift backstop.

1. For each story (each Phase/theme entry) build the marker `**Roadmap Source:** <roadmap-file> :: Phase N :: <story title>`.
2. Before creating anything, check every story on every write:
   - **GitHub mode:** `gh issue list --search "\"<marker>\" in:body" --state all --json number,body`. The result is a candidate set, not a verdict: phrase search matches a token subsequence, so a title that prefixes another drained title can falsely match. Treat the story as drained only when the marker is an **exact, full line** in a candidate's body. Search is eventually consistent: track the issues you just created directly.
   - **Strict mode:** whole-line match per story file, e.g. `grep -Fxq "<marker>"` over `{RUNTIME_ROOT}/docs/stories/*.md`; a plain substring grep has the same prefix-title risk.
3. If no match, create the story per `po-write-story`, with the `**Roadmap Phase:** Phase N — <theme>` body line and the `phase-N` label (see `Plan_Sprint_Workflow.md` Stage 4), plus the step 1 marker line verbatim alongside `**Phase:**`/`**Story Points:**`/`**Priority:**`/`**Assigned:**`. The marker exists only for step 2.
4. **Idempotent re-run:** repeating steps 1–3 on an unchanged roadmap finds a match for every story and creates zero stories.

Commit the roadmap update per `po-plan-docs`.
