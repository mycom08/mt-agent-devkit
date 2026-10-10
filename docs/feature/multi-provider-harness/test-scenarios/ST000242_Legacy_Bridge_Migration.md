# ST-000242 Legacy Bridge Migration

Implementation under validation: `131ab52ffc9ac677d66ed7cc03a51e577580d59f`.
Independent QA runs the documented Windows aggregate and focused migration tests.
This scenario specifies deterministic deployment evidence; native provider interpretation remains separately gated.

| AC | Scenario and expected result |
|---|---|
| 1 | Execute frozen first-pass bridge finalization, writing the current release stamp; authenticated installed bridge reaches reviewed migration. Edited/missing/counterfeit bridges and unknown stamps fail without writes, returning inventory. |
| 2 | Bind Claude and Antigravity with provider substitutions; equivalent candidates retain both exact original texts/hashes, expose normalized comparison, and require explicit shared adaptation. Genuine differences retain every variant without selecting a copy. |
| 3 | Use supported mixed legacy versions; inventory reports both versions and review remains mandatory. Mixed modes and incomplete provider bindings still block. |
| 4 | Compare relative `.` and absolute inventory, inspection and serialized plans; they identify identical paths and fingerprints. Apply/verify with `.` succeeds; traversal/redirect protections remain enforced. |
| 5 | Run focused sync tests, frozen bridge contracts, complete deployment regressions and invariant fixtures. All applicable checks must pass. |
| 6 | Snapshot target bytes before planning and confirm no changes; explicitly review divergent custom rules and retirements, apply, verify custom union and unchanged provider runtime bytes, and retain migration backup journal. Existing rollback, source identity and containment regressions pass. |
| 7 | Check generated bundle drift and wrappers, inspect active instructions and manifest provenance, confirm frozen bridge and version files unchanged, and confirm unreleased changelog entry. No release. |

## Commands

```powershell
python -m unittest scripts.test.test_phase2_sync -v
powershell -File scripts/test/run.ps1
python scripts/validate_templates.py
python scripts/validate_internal_harness.py
python .mt-agent-devkit/scripts/generate_wrappers.py --check
python -m unittest scripts.test.test_internal_harness
python .mt-agent-devkit/distribution/phase2/build_bundle.py --root . --output .mt-agent-devkit/distribution/phase2/bundle --check
git diff --check
```

## Results

Independent QA completed on 2026-10-10: focused migration 12 tests passed;
internal harness 23 tests passed; complete Windows aggregate 99 tests and
10 validator fixture groups passed. Layer-1/internal validators, wrapper drift,
generated bundle drift (152 assets, 472 entries), and whitespace checks passed.
The aggregate includes 24 frozen legacy upgrade combinations across three
versions, two providers, two modes and missing/present initial stamps.

All seven AC pass within the deterministic mechanical scope above. Planning
snapshots remain unchanged; reviewed apply preserves custom rules and provider
runtime, with backup journals and receipt verification. Unknown stamp, edited
bridge and tampered provenance rejection remain fail-closed. Frozen bridge bytes,
`VERSION` and `version.txt` are unchanged; no release occurred.

Logs remain provider-local: `QA_ST242_Aggregate.log`, `QA_ST242_Focused.log` and
`QA_ST242_Internal.log` under `.codex/agents/working/tmp/`. Remote publication,
exact-head CI and refreshed review of this scenario are separate merge gates.
Native Markdown interpretation and real external release acquisition were not
certified by these offline fixtures.
