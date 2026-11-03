---
name: retro
description: Retro trigger detection for every role - trigger definitions, recording each trigger when detected, stage-state reporting and the completion check. Load at spawn.
---

# Retro

**Requires:** `retro-contribution` (only after a recorded trigger)

Canonical owner; part `detection` is generated into Common Bootstrap and Core §7. Orchestrator bookkeeping (expected identities, sprint retros, legacy runs) is `retro-contribution` part `orchestration`.

<!-- part: detection -->
Single authoritative detection policy: evaluate it during work and before each stage handoff, before loading retrospective-only guidance. Completion reports, verification evidence, telemetry, memory pruning and runtime handoffs stay required independently.

| Observable event | Trigger kind |
|---|---|
| Tooling/environment failure or external blocker (runner cannot connect, unavailable credential, external owner blocks verification) | `tooling_failure` / `external_blocker` |
| Requirement ambiguity needing a decision (conflicting AC needs PO/TL resolution) | `decision_ambiguity` |
| Second or later fix round, across review/QA combined | `repeated_fix` |
| New reusable lesson (a newly discovered verification gap with future action) | `reusable_lesson` |
| Explicit user request for a story or sprint retro (record the requested scope; never invent failures) | `explicit_request` |

Not triggers: ordinary successful verification, a first routine correction alone, a passing routine check with no lesson, an intentionally failing seeded negative test proving a guard works. Independent exceptions override the first-fix exemption (a runner failure during the first fix still triggers); repeated fix rounds trigger even when each correction is routine.

1. **When detected,** record each kind (`record ... --state required --trigger <kind>`) before loading writing guidance.
2. **For every completed stage,** report the evaluated state `clean`, `required` or `unknown` under the concrete selected provider/run/story/stage/role identity; missing or uncertain evaluation is `unknown`, never clean. Required stays sticky across clean/unknown resumes; late triggers update the same identity and preserve/deduplicate earlier lessons.
3. **A triggered role** loads the contribution guidance its route names and writes only its own contribution; a clean role loads no writing guidance or Retro_Rules and creates no retro skeleton, section or no-op entry.
4. **At handoff,** `record --provider <selected-provider> --runtime-root <concrete-runtime-root> --run <run-id> --story ST-XXXXXX --stage <stage-id> --role <role> --state clean` for an evaluated clean stage (`unknown` when uncertain). A required stage, after writing its populated contribution, adds `--contribution 'retros/ST-XXXXXX_retro.md#<exact role heading>' --evidence 'tmp/<relative-evidence-file>'`; a missing contribution blocks completion until submitted. Evidence is a confined existing provider-local file, never a secret or sensitive prompt.
5. **Before accepting stage/story/sprint completion,** run `check --provider <selected-provider> --runtime-root <concrete-runtime-root> --expected 'tmp/<expected-identities.json>'`. Missing/unknown records, identity conflicts, foreign/escaping pointers and missing/unpopulated required contributions block it; story files alone prove nothing. Clean-only results have no retro files; mixed results return only required source paths.

Helper: `python .mt-agent-devkit/scripts/retro_completion.py` (bounded provider-local metadata; never writes retros). Identity: `provider`, `run`, `story`, `stage`, `role` (underscored, e.g. `Technical_Lead`); distinct stages and actual actors get separate identities, resumed/fix work updates its own. Retros and evidence stay runtime-local and uncommitted. This bookkeeping never bypasses independent TL/QA or the acceptance contract.
<!-- /part: detection -->
