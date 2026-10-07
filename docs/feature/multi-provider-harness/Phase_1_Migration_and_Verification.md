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
but unavailable in this Codex runtime. Its default operational mapping is unset;
the live runtime must supply a verified manifest and actual tool identities.
This is an explicit blocked capability, not a simulated portability claim.

## Runtime preservation and rollback

New state is gitignored at `.<provider>/agents/runtime/`, with individual runs
under `runs/<run-id>/<story-id>/`. Provider/run/story identifiers prevent shared
singleton state and history collisions. Bind and pass the exact runtime path on
each spawn/resume. Legacy provider memory seeds runtime-local copies; histories
are not merged, deleted or committed. A missing/ambiguous resumed state blocks
before mutation.

Before rollout, retain current interrupted state and record its exact worktree,
story, branch and provider. Do not resume an old singleton state blindly under a
new run binding: verify its identity and explicitly carry it into the selected
run directory, preserving the original. Unknown state remains blocked for
recovery. No automatic mass state move is performed.

Rollback uses `git revert <migration-commit>` on an isolated clean product branch
and the normal independent review process. This restores tracked entrypoints
and legacy instruction bodies; ignored runtime directories remain on disk.
Keep those directories when reverting. Before resuming an older harness, verify
provider/story/branch identity and explicitly restore only that run's required
state to the legacy location without overwriting another run. Never reset the
user's current checkout or delete runtime directories as part of rollback.

## Verification and limits

Run the internal static validator, wrapper check, provider/section routing tests,
existing template validator and existing helper/deployment regression suite:

```text
python scripts/validate_internal_harness.py
python .mt-agent-devkit/scripts/generate_wrappers.py --check
python -m unittest scripts.test.test_internal_harness
python scripts/validate_templates.py
python -m unittest scripts.test.test_branch_preflight scripts.test.test_telemetry scripts.test.test_upgrade_deployment
```

CI runs these fast gates when shared sources, adapters, native wrappers/skills,
entrypoints, validator code or templates change. Checkout retains history to
compare the recorded source revision. The preservation validator checks baseline
history hashes and unchanged templates, scaffold functional code, VERSION,
version.txt and changes.json. Existing deployment tests exercise legacy emitted
trees, including provider/mode helper identity and runtime-ignore contracts.

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
