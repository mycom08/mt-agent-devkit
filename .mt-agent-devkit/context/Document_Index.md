# Document Index — mt-agent-devkit

Quick lookup for all project documents and external references. Update this file whenever a document is added, moved, or removed.

---

## Internal Project Documents

### Business & Product

| Document | Path |
|---|---|
| Business Requirements | `docs/requirements/Business_Requirements.md` |
| Implementation Roadmap | `docs/plan/Implementation_Roadmap.md` |
| Product Backlog | `docs/plan/Product_Backlog.md` |

### Technical

| Document | Path |
|---|---|
| Technical Analysis | `docs/technical/Technical_Analysis.md` |
| Architecture Overview | `docs/technical/Architecture.md` |

### Reviews and Improvement Guides

| Document | Path |
|---|---|
| Top Four Agent Harness Fixes — Implementation Guide | `docs/reviews/fix_guidline/Top_Four_Agent_Harness_Fix_Guide.md` |
| Four Agent Harness Fixes — Execution and Test Plan | `docs/reviews/fix_guidline/Four_Fix_Execution_and_Test_Plan.md` |

### Sprint Docs

| Document | Path Pattern |
|---|---|
| Sprint Overview | `docs/sprints/Sprint_N_Overview.md` |

---

## External References

| Resource | URL / Location |
|---|---|
| GitHub repo | https://github.com/mycom08/mt-agent-devkit |
| Raw content base | Derived at use time, pinned to a release tag: `https://raw.githubusercontent.com/mycom08/mt-agent-devkit/v<version>` — never `/main`, which carries unreleased work |

---

## Agent Working Files

<!-- GitHub mode: stories are GitHub Issues — no local story MD files. -->

| What | Path |
|---|---|
| Sprint Retro Summaries | `{RUNTIME_ROOT}/retros/ST-XXXXXX_retro.md` |
| Agent Instructions | `.mt-agent-devkit/instructions/` |
| Agent Rules | `.mt-agent-devkit/rules/` |
| Agent Memory | `{RUNTIME_ROOT}/memory/` |
| Agent Working Records | `{RUNTIME_ROOT}/working-record/` |
| Devkit Templates | `.claude/agents/templates/` |
| Internal Command Workflows | `.mt-agent-devkit/workflows/commands/` |
| Target Lifecycle Workflows (init/update/build/sync) | `{LIFECYCLE_ROOT}/agents/workflows/` (`.claude` or `.antigravity`) |
| Sprint Workflows | `.mt-agent-devkit/workflows/` |

---

**Last Updated:** 2026-09-21

## Multi-Provider Harness

- Design: `docs/feature/multi-provider-harness/Shared_Harness_Provider_Architecture.md`
- Migration: `docs/feature/multi-provider-harness/Phase_1_Migration_and_Verification.md`
- QA acceptance scenarios: `docs/feature/multi-provider-harness/test-scenarios/Phase_1_Harness_Acceptance_Scenarios.md` — native evidence limits and accepted deviations are recorded in the document; full harness compliance is not certified.
