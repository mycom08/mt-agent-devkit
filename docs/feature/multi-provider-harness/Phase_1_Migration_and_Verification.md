# Multi-Provider Harness — Phase 1 Migration and Verification

**Story:** ST-000220  
**Feature:** `multi-provider-harness`  
**Verified source:** `62349287bc9835093a02586d8658993ba8ac685b` (main)  
**Status:** Implementation candidate; independent review and native evidence pending

## Migration map and authority

The machine-readable inventory is
`.mt-agent-devkit/contracts/migration-inventory.json`. It accounts for all 189
tracked baseline internal harness/discovery paths, recording revision, hash,
ownership, destination, consumers and exclusion reason. Claude provides shared
content, ordering, numbering, tier placement and routing. This implements the
agreed architecture, not the proposed stage-profile redesign or FIX-02.

| Baseline source | Canonical owner / treatment |
|---|---|
| Both providers' working instructions, rules, context and skeletons | `.mt-agent-devkit/` with source-linked generated compatibility wrappers |
| Working story/sprint workflows | `.mt-agent-devkit/workflows/` |
| Analyst, audit and apply-retros command workflows | `.mt-agent-devkit/workflows/commands/` |
| Role model frontmatter and native provider tools | Provider discovery wrappers and `.<provider>/harness/` |
| Internal branch preflight | `.mt-agent-devkit/scripts/branch_preflight.py`, with legacy executable wrappers |
| Internal telemetry | Shared wrapper delegates to the unchanged distributed collector/schema |
| Section extraction | Shared cross-platform Python helper; native read-section discovery and legacy shell shims |
| Init/update/build/sync target lifecycle and scaffold helpers | Existing provider-local operations retained; Phase 2 owns target-layout migration |
| 45 tracked memory/retro history files | Original locations and bytes preserved |
| Historical plan, enhancement and legacy usage references | Original files retained and explicitly inventoried |

Generated wrappers are not editable rules. Regenerate with
`python .mt-agent-devkit/scripts/generate_wrappers.py`; verify with `--check`.
Bootstrap wrappers explicitly require the full canonical bootstrap. On-demand
wrappers require only the triggered numbered section. Legacy section extraction
resolves the wrapper's inventory mapping before reading the section. Active
internal rule routing points directly to canonical paths.

Ignored/untracked local configuration, sessions, Working Records and scratch
worktrees are outside the tracked-source inventory and are preserved. Do not
copy secrets or local settings into the shared tree. Native settings remain
provider-local; this migration grants no new permissions.

## Provider selection and rollout

`AGENTS.md` and `CLAUDE.md` explicitly load neutral project priming for ordinary
repository work. Only authorized workflow work loads the shared provider
contract, checks actual enabled operation identities, selects one adapter, and
loads shared orchestrator instructions. `.codex/` is routed explicitly, without
assuming provider auto-discovery. Multiple capabilities require an explicit
available provider declaration; missing mappings block before writes or spawning.

The coherent initial migration path is role/bootstrap → Start Story → shared
implementation/review/QA/PO pipeline → resume/expired-session handling. The
remaining role/rule/context and command sources follow that same ownership
contract. Model policies, tool permissions, lifecycle/session IDs, CI waits and
usage extraction belong to adapters. The pinned inventory prevents deleting an
old editable copy without a replacement route.

Antigravity candidate operation aliases are documented by the baseline skill,
and must be verified in the active runtime. Its default operational mapping is unset;
the live runtime must supply a verified manifest and actual tool identities.
This is an explicit blocked capability, not a simulated portability claim.

## Runtime preservation and rollback

Normal working state remains under each provider's existing `agents/working/`
paths, with existing command tmp/reports under `agents/`. Each provider owns a
`harness/state-paths.json`; selection returns validated concrete bindings for
every spawn/resume. Missing/foreign bindings block; no cross-provider fallback
search is allowed. Records, memory, retrospectives, reports, temporary files,
telemetry and progress are not shared, copied into runs or migrated. Existing
histories and lifecycles are preserved. Disposable validation evidence may stay
in isolated provider-local `agents/runtime/runs/` directories.

Sprint execution retains its provider-local singleton state and story-named
retrospectives. Verify provider/story/branch before resuming interrupted work;
concurrent or ambiguous ownership blocks. Keep existing state in place during
rollout and rollback; no state copying, mass move or deletion is performed.

Rollback uses `git revert <migration-commit>` on an isolated clean product branch
and the normal independent review process. This restores tracked entrypoints
and legacy instruction bodies; ignored runtime directories remain on disk.
Keep those directories when reverting. Before resuming an older harness, verify
provider/story/branch identity. Operational state remains in its original
provider paths; no restoration from a run directory is needed. Never reset the
user's current checkout or delete runtime directories as part of rollback.

The fixed source inventory documents migration provenance. Normal validation
checks live ownership, wrapper generation, reference routing and adapter bindings;
it permits future release/template/history updates. The explicit
`--migration-preservation` audit alone compares protected bytes to the frozen
migration baseline. Retain that audit for migration review, not ongoing CI.

Command state deliberately remains provider-local singleton storage, including
across run IDs. Inspect interrupted state and verify topic/project and ownership
before resume or replacement; active or ambiguous ownership blocks concurrent
commands. Tests assert provider separation and same-provider reuse, not run isolation.

## Verification and limits

Run the internal static validator, wrapper check, provider/section routing tests,
existing template validator and existing helper/deployment regression suite:

```text
python scripts/validate_internal_harness.py
# One-shot audit for this migration only, not an ongoing CI/pre-PR gate:
python scripts/validate_internal_harness.py --migration-preservation
python .mt-agent-devkit/scripts/generate_wrappers.py --check
python -m unittest scripts.test.test_internal_harness
python scripts/validate_templates.py
python -m unittest scripts.test.test_branch_preflight scripts.test.test_telemetry scripts.test.test_upgrade_deployment
```

CI runs these fast gates when shared sources, adapters, native wrappers/skills,
entrypoints, validator code or templates change. Checkout retains history to
read the inventory source revision. Normal validation checks active references,
generated wrappers and inventory coverage. Only the explicit one-shot
`--migration-preservation` audit freezes baseline history/helper hashes, templates,
VERSION, version.txt and changes.json; CI does not invoke that option. Existing deployment tests exercise legacy emitted
trees, including provider/mode helper identity and runtime-ignore contracts.

Independent review found that mechanical scaffolds did not cover generated
skeleton CI filters. Shared skeletons now render `LIFECYCLE_ROOT` for the chosen
legacy target before generation; both-provider fenced artifacts and inline CI
triggers are compared against the pinned baseline. Provider binding tests cover all three providers, missing/foreign configuration
and preservation of working paths across stories and runs. Active reference
checks cover explicit legacy reads and registered runtime/lifecycle bindings;
the missing Analyst instruction is a negative fixture. Internal binding tokens
are rejected in distributable templates.

| Evidence class | Candidate status |
|---|---|
| Static source/reference/wrapper/preservation checks | Collected during implementation; exact-head results belong in the PR |
| Provider selection and section isolation fixtures | Deterministic tests; do not claim native execution |
| Claude complete story path | **NOT VERIFIED** — native runtime unavailable |
| Antigravity complete story path | **NOT VERIFIED** — native runtime unavailable; mapping unset |
| Codex complete story with independent reviewer/QA | **NOT VERIFIED** until this story's actual review/QA and closure evidence exists |

Before declaring native success, retain sanitized evidence of fresh role spawn,
same-session and expired-session fix, independent review and QA handoff,
permission denial/escalation handling, pending/failed CI outcomes, and worker
completion without an open-ended wait. Tool-identity tests and prose walkthroughs
do not satisfy the complete native story criterion. Missing usage remains
unavailable/null; no efficiency benchmark or token-saving claim is made.

Phase 2 story ST-000221 owns template generation, installer/sync changes,
customized legacy target migration, release metadata and multi-provider installed
layout. No Codex target installer is invented in Phase 1.
