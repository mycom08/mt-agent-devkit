---
name: qa-regression
description: QA regression check before sign-off - blast radius, init project and sync devkit impact, the template and harness regression suites, the local-verify contract and the CI-equivalent exception. Load once every AC is verified, before sign-off.
---

# QA Regression

**Requires:** `qa-core`, `pre-pr-gate` (the check table), `raise-question` (blockers)

Mandatory before merge sign-off. For long local verification use `.mt-agent-devkit/contracts/Local_Verify.md` (local-verify) with the full required command, the selected provider bindings and a new run ID. Launch once; resume only supported waits on that identity. Missing completion is not success. Keep provider-local logs and independent verification gates.

After all story AC are verified, confirm no regression was introduced:

1. Review the changed files and consider the blast radius.
2. Check whether the change affects `init project` behavior, `sync devkit`, and both GitHub and strict mode.
3. **Template or workflow changes** (`.claude/agents/templates/**`, `.claude/agents/workflows/**`): follow `docs/Template_Test_Strategy.md`; the regression suite is the Layer-1 gate, `python scripts/validate_templates.py` and `bash scripts/test/run.sh`, both exit 0.
4. Changes to `.mt-agent-devkit/**`, any provider's `harness/**`, internal working wrappers or skills, or root entrypoints: run the harness and template/deployment checks in the `pre-pr-gate` skill section 1 table, all exit 0.
5. Regression risk found: comment on the story issue tagging **Dev**; treat it as a QA failure and loop back for a fix.

**Gate:** no merge sign-off until the regression check is complete.

**CI-equivalent exception:** when the Technical Scope is `.github/workflows/**` only and the PR's own CI run already executes an equivalent check (for example `validate-templates.yml` running the same `validate_templates.py`), cite that passing CI run instead of re-running the Layer-1 gate locally. It never applies to a story that touches template or workflow content itself.
