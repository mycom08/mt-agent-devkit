# Product Owner Rules — Read On Demand (Scenario-Conditional)

**Applies to:** Product Owner agent. `Product_Owner_Rules_Bootstrap.md` is read in full on every PO spawn regardless of task; the section below applies only when authoring or updating a roadmap/planning doc — not most spawns. Read this file **only when the matching scenario actually occurs**. `Product_Owner_Rules_Bootstrap.md` §11a still carries a one-line pointer to the relocated section here.

---

## 1. Roadmap Story Drain (mandatory whenever a roadmap doc is authored or updated)

Triggered from `Product_Owner_Rules_Bootstrap.md §11a` — cited by that section number from `Plan_Sprint_Workflow_Shared_template.md` Stage 1, so keep this section's content in sync with that citation even if renumbered here.

**Applies whenever you author or update a roadmap/planning doc that defines stories ahead of pickup — the Implementation Roadmap or any `*Roadmap*.md` under `docs/feature/<feature_name>/plan/` — in a context where a story tracker already exists** (i.e. `init project` has already run; this rule doesn't apply to the Analyst workflow's pre-repo `implementation_roadmap.md`, which has no tracker yet and no real story IDs).

Every story the roadmap defines must become a tracked `status:backlog` issue/story record **at this same moment** — do not defer this to sprint planning, and do not wait for `plan next sprint`/`create stories` to notice it.

1. For each story the roadmap defines (each Phase/theme entry), build the idempotency marker: `**Roadmap Source:** <roadmap-file> :: Phase N :: <story title>`.
2. Check whether a tracked issue/story already carries this exact marker **before creating anything** — this check is what makes re-authoring or updating the same roadmap safe against duplicates; run it for every story on every write, not just the ones you think are new:
   - **Mode: github** — `gh issue list --repo {github-org}/{repo-name} --search "\"<marker from step 1>\" in:body" --state all --json number,body`. Treat the result as a **candidate set, not a verdict**: GitHub's phrase search matches a contiguous token subsequence of the body, not an exact line, so a story whose title is a prefix of another already-drained story's title can return a false match. For each candidate, confirm the marker appears as an **exact, full line** in that issue's body before treating this story as already drained — skip creating it only then. Note: GitHub's search index is eventually consistent, so an issue you created moments earlier in this same pass may not be returned yet — track what you just created directly rather than relying on search to re-find it.
   - **Mode: strict** — grep `.antigravity/agents/docs/stories/*.md` for the exact marker line using a whole-line match (e.g. `grep -Fxq "<marker>"` per file, not a plain substring grep, which carries the same prefix-title false-positive risk). A match means this story is already drained — skip it.
3. If no match, create the tracked issue/story:
   - **Mode: github** — follow `Story_Standard_PO.md` §13's title/label/`--body-file` conventions, with the usual `**Roadmap Phase:** Phase N — <theme>` body line and `phase-N` label already used for roadmap-sourced stories (see `Plan_Sprint_Workflow.md` Stage 4, `Create_Stories_Workflow.md` Step 3) — those are your phase-reference tag (AC2). Add the new marker line from step 1 verbatim in the body too (alongside `**Phase:**`/`**Story Points:**`/`**Priority:**`/`**Assigned:**`) — that one exists purely for the idempotency check in step 2, not as a human-facing phase tag.
   - **Mode: strict** — follow `Create_Stories_Workflow.md` Step 4's strict-mode story-creation steps; set `**Feature:**`/`**Phase:**` from the roadmap entry as usual, and include the marker line from step 1 in the body for the same idempotency purpose.
4. **Verification (idempotent re-run):** re-running steps 1–3 against an unchanged roadmap must return an existing match at step 2 for every story and create zero new issues/records — this is the mechanism that satisfies "re-authoring the same roadmap does not create duplicates."

> This is separate from, and happens earlier than, `Plan_Sprint_Workflow.md` Stage 1's reconciliation backstop. That backstop exists only to catch drift if a roadmap somehow got out of sync with tracked issues despite this rule (e.g. a manual edit made outside your own workflow) — it is not a substitute for draining at authoring time.

---

## Version

**Version:** 1.0 — Split out of `Product_Owner_Rules_template.md` v1.9 (former section 11a's full procedure relocated here as §1; the section 11a heading stays in `Product_Owner_Rules_Bootstrap_template.md` as a pointer since it is cited by number externally), mirroring the boundary already validated on the devkit's own team.
**Created:** 2026-08-25
