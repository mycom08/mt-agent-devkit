# ST-000227 Compliance Read Routing

## Current verdict

AC1–AC3 have mechanical implementation evidence. **AC4: NOT VERIFIED.** The implementation runtime exposes Codex collaboration tools only; no native Claude workers or Claude `Read` transcripts were produced. Static checks, Codex runs and this audit plan cannot satisfy AC4. Keep the PR draft and the story open until independent QA accepts measured native Claude evidence on the candidate SHA.

## Routing and deployment contract

Developer, Technical Lead and QA instruction Pre-Work tables explicitly require their role-scoped Story Standard and the selected adapter supplied in the worker packet. Internal and installed adapters resolve to `{PROVIDER_ROOT}/harness/Provider_Adapter.md`; the deployment manifest declares `.claude/harness/Provider_Adapter.md`, `.antigravity/harness/Provider_Adapter.md` and `.codex/harness/Provider_Adapter.md`. The adapter is selected once by verified live capabilities; no worker discovers other providers. The Shared Pipeline explicitly routes a full `.mt-agent-devkit/rules/Retro_Rules.md` read at each stage end.

The active Phase 2 templates intentionally retain installer prefixes and target-project wording; bundle compilation resolves shared paths. Historical `.claude/agents/templates/` are frozen. The current `changes.json` deployment declaration already points to the rebuilt bundle manifest, which contains the new asset hashes; legacy bridge lists and checksums stay unchanged.

## Frozen native audit case

Use only a runtime with actual enabled native Claude spawn, resume, messaging and completion capabilities, validated through the Provider Contract. Installation or a CLI binary alone is insufficient. Do not invoke a paid external runtime without separate authorization. Record the candidate full Git SHA, native model/version, enabled tool identities, adapter path, resolved bindings, mode and run identity before the audit. Use an isolated copy at that SHA with fresh Claude role state, without importing operational records. Do not modify GitHub issues or production branches.

Freeze the following local story verbatim before any worker starts:

```markdown
# ST-900227 — Update a documentation heading
**Assigned:** Developer
**Base Branch:** main
## User Story
As a maintainer, I want the fixture heading corrected so readers see its current name.
## Acceptance Criteria
- The first heading of docs/Fixture.md changes from Old Heading to Current Heading.
- The sentence and trailing newline remain unchanged.
- No unrelated product file changes.
## Deliverables
A reviewed local change and a QA verdict.
```

Seed `docs/Fixture.md` with exactly `# Old Heading\n\nKeep this sentence.\n` (interpret the displayed escapes as newlines). Create a fresh strict-mode state snapshot at implementation start; use candidate shared harness sources and selected Claude bindings. Capture seed hashes before the run. Run the normal shared pipeline with Developer implementation, independent TL review, and independent QA validation. Allow required role reads, bounded story context and owning-role local state; prohibit unrelated role standards, another provider adapter, recursive startup discovery, story rewrites and GitHub mutations. Do not add a checklist telling workers to open the three files: the candidate routing must cause those reads. Pass only the ordinary role/stage packets, selected adapter and bindings; retain stage-end retro instructions from the shared pipeline.

## Native execution and transcript audit

1. Start fresh native Developer, TL and QA workers at their respective stages. Capture each worker's actual native `Read` tool requests and returned content, not just orchestrator messages or statements in final reports.
2. Verify successful full reads of `.mt-agent-devkit/rules/Story_Standard_Dev.md`, `Story_Standard_TL.md` or `Story_Standard_QA.md` for the owning role; `.claude/harness/Provider_Adapter.md` before its first shell command; and `.mt-agent-devkit/rules/Retro_Rules.md` before its stage report. Bounded reads must collectively cover the whole required file without truncation; an attempted path or partial response is insufficient.
3. Record per worker the native session identity, stage, exact path, `Read` event identifiers, covered line/byte ranges, file character count, actual available token usage and observed duration. Missing usage remains null. Count read events and covered characters separately from token billing; never infer tokens from characters. Report required and forbidden read results, task result and deviations.
4. Verify the exact heading change and independent review/QA outcomes, no unauthorized mutations, and all three complete read sets. Keep raw transcripts in a gitignored evidence directory; publish only sanitized summaries and stable event pointers. Do not include home paths, credentials or raw sensitive prompts.
5. Independent QA must audit the raw worker transcripts and attach the sanitized evidence to the PR/issue for the exact candidate SHA. Any missing native worker, omitted/partial mandatory file, wrong provider, or absent transcript keeps AC4 pending. Product changes after the audited SHA require a scoped evidence refresh.

## Required evidence handoff

| Worker | Role Standard | Adapter | Full Retro Rules | Current evidence |
|---|---|---|---|---|
| Developer | Story_Standard_Dev.md | .claude/harness/Provider_Adapter.md | .mt-agent-devkit/rules/Retro_Rules.md | NOT RUN |
| Technical Lead | Story_Standard_TL.md | .claude/harness/Provider_Adapter.md | .mt-agent-devkit/rules/Retro_Rules.md | NOT RUN |
| QA | Story_Standard_QA.md | .claude/harness/Provider_Adapter.md | .mt-agent-devkit/rules/Retro_Rules.md | NOT RUN |

The native operator supplies the pinned setup, fixture hashes, successful `Read` coverage/events, timing/usage availability, final product diff, verdicts and deviations. Independent QA records PASS or explicit failures per row and decides AC4. No acceptance checkbox is changed by the implementer.
