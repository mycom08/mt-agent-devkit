# Feature: multi-provider-harness

## Decisions

| Decision | Reason | Rejected Alternative |
|---|---|---|
| Route role standards and selected adapter in Pre-Work tables; route full Retro Rules at stage end | Make existing compliance requirements reachable without duplicating rule content | Loading every rule at spawn |
| Keep native Claude AC4 pending on a draft PR | Codex/static checks cannot establish native Claude Read behavior | Simulating, waiving or claiming the native gate |

## Constraints

Historical Claude templates remain frozen; current deployment changes use active Phase 2 templates and regenerated bundle/manifest. The current changes.json deployment pointer already includes these assets.

## Open Questions

The native Claude operator uses the isolated internal role-stage audit (not the GitHub pipeline or strict mode) and must provide audited Developer/TL/QA Read transcripts for the exact candidate SHA; independent QA decides AC4. The frozen case and handoff are in ../test-scenarios/ST000227_Compliance_Read_Routing.md.

## State

Independent QA failed native AC4 at 44ec4af: shell exposure did not satisfy direct Read coverage and adapters followed first shell. The fix moves a generic reading-tool contract to the ordinary worker packet boundary; updated role/Common routing preserves native direct full reads and adapter-first order. A new candidate needs independent approval and a fresh native audit.

ST-000227 is in review with draft PR240. Mechanical implementation is complete; static validators, wrappers/bundle, 23 internal tests, 94 aggregate tests and all 10 fixture groups pass. Independent Developer review and QA remain required; no AC is ticked and no merge/release is authorized by this handoff.
