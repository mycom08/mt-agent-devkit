# Project Roadmap

**Readers:** Product Owner, Business Analyst, orchestrator. Implementers do not read this file; it is not part of Project Priming.
**Owner:** Product Owner
**Last updated:** 2026-11-26

One line per topic, linking to the topic's own roadmap or umbrella issue. Never list stories here; a topic's story list lives in its own roadmap. No dates. A topic moves bucket when its state changes, and a new topic is added when work on it starts.

## Now

- Analyze Requirements workflow for target projects: intake to approved specs, ADRs, roadmap, design and backlog stories — [#244](https://github.com/mycom08/mt-agent-devkit/issues/244)
- UX foundation: project UX standard, feature design docs and pipeline enforcement for UI stories — [#233](https://github.com/mycom08/mt-agent-devkit/issues/233)

## Next

- None.

## Later

- Stage-specific Developer and Common read profiles (on hold): profiles, manifest routing and efficiency comparison — [#263](https://github.com/mycom08/mt-agent-devkit/issues/263)
- Harness efficiency and process backlog: Developer token waste, refinement and review gates, retro-sourced fixes — [open enhancement issues](https://github.com/mycom08/mt-agent-devkit/issues?q=is%3Aopen+label%3Aenhancement)
- Parallel execution and efficiency benchmark (FIX-02) — [#218](https://github.com/mycom08/mt-agent-devkit/issues/218)
- Cross-tool dispatch and native-run telemetry accuracy — [#225](https://github.com/mycom08/mt-agent-devkit/issues/225), [#228](https://github.com/mycom08/mt-agent-devkit/issues/228)

## Done

- Workflow test-run fixes (sprint 15): branch preflight judges the base by paths, the retro completion helper follows the installed runtime binding, and installed commands need no repository placeholder — [#372](https://github.com/mycom08/mt-agent-devkit/issues/372), [#371](https://github.com/mycom08/mt-agent-devkit/issues/371), [#370](https://github.com/mycom08/mt-agent-devkit/issues/370)
- Project-owned model and effort override (sprint 13): `agent_models` in `project_settings.json` overrides model and effort per role or policy, pinned per run and preserved by sync — [#322](https://github.com/mycom08/mt-agent-devkit/issues/322)
- Release metadata trim (sprint 13): `changes.json` keeps only the snapshot and the newest three released versions; legacy stamps from 0.1.51 still migrate and the coverage validator checks are retired — [#345](https://github.com/mycom08/mt-agent-devkit/issues/345), [#346](https://github.com/mycom08/mt-agent-devkit/issues/346), [#347](https://github.com/mycom08/mt-agent-devkit/issues/347)
- Role skills, remaining roles (sprint 12): Technical Lead and QA rules became `tl-*` and `qa-*` skills, shipped to targets, with the legacy rules files retired — [docs/feature/role-skills/](feature/role-skills/)
- Project roadmap and sprint-end docs sync (sprint 11): a planner-only status doc replaces the Priming status text, and a sprint-end check keeps roadmaps and entrypoints current — [#238](https://github.com/mycom08/mt-agent-devkit/issues/238), [#283](https://github.com/mycom08/mt-agent-devkit/issues/283)
- Role skills (sprint 10): Developer rules became `dev-*` and shared common skills, internally and in targets — [docs/feature/role-skills/](feature/role-skills/)
- Multi-provider harness: shared `.mt-agent-devkit/` harness with Claude, Antigravity and Codex adapters and the Phase 2 bundle — [docs/feature/multi-provider-harness/](feature/multi-provider-harness/)
