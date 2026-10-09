# Phase 2 Deployment QA

Story: ST-000221. Candidate: `06f4de12d6d90b46ca06055613033e18fa40dd3e`.

Historical evidence below is retained for traceability. Current correction-round evidence and the user-authorized acceptance boundary are recorded in the final section.

## Scenarios

| Case | Oracle |
|---|---|
| Fresh/install/update/build | All three providers and both modes install shared ownership and selected adapter; repo/root profiles remain distinct. |
| Legacy direct/missing stamp | Frozen v0.1.48–50 Claude/Antigravity, both modes, preserve custom content and runtime bytes; two-pass bridge reaches verified receipt. Native interpretation is separately assessed. |
| Conflicts and invalid sources | Custom edits, tampering, unsafe paths, unsupported schema/layout and active/mixed sessions fail closed. |
| Idempotency and isolation | Repeat deployment leaves bytes stable; another provider cannot replace existing provider histories. Release acquisition uses one immutable commit. |
| Recovery | Initialization interruption leaves complete recoverable state or no published lock; resume/rollback reject human receipt edits and restore exact before bytes. |
| References and packaging | All managed references resolve, bridges are old-parser-compatible, assets stay outside legacy arrays; VERSION/version.txt remain unchanged. |
| Native github/strict | Distinct installed Developer, TL and QA participants execute canonical whitespace-normalization case using real installed instructions and fixture-local bindings; no external lifecycle mutations. |
| Native unavailable | Claude/Antigravity runtimes and automatic entrypoint discovery remain unverified; reason, follow-up, support boundary and PO decision required. |

## Results

Independent mechanical validation PASS at candidate `06f4de12d6d90b46ca06055613033e18fa40dd3e`:

- Template/internal validators, wrapper drift check, 23 internal tests, deterministic artifact check (149 assets/294 entries), changed Bash and PowerShell syntax pass.
- Documented Windows aggregate `powershell -NoProfile -File scripts/test/run.ps1`: 86 unittest cases PASS; eight negative validator fixture groups and one clean exclusion group PASS, exit 0. Initial restricted-sandbox temporary writes/Bash service failed; authorized elevated native execution resolved this. WSL Bash lacked `python`, so the documented Windows equivalent supplied aggregate evidence.
- Suite includes all six provider/mode layouts and both profiles; real lifecycle launchers; immutable release/sync interruption; frozen v0.1.48–50 helpers and 24 two-pass legacy migration cases; customization/runtime preservation, conflicts, provider isolation, idempotency and recovery/rollback including receipt edits.
- Only changed historical templates are compatible ordinary/root sync headers, reviewed in full against retained legacy bodies. Additive metadata and bridge-only files alias match approved legacy parser decisions. VERSION and version.txt are unchanged.

## Native evidence and support boundary

Source-bound disposable installed fixtures use receipt source candidate `06f4de12d6d90b46ca06055613033e18fa40dd3e`, manifest SHA256 `9bbdddf320a1c3ece4456e2ec9225c601989079f78880ad31a482d5ca6e730a2` and fixture-local `.codex/agents` bindings. Explicit installed-instruction dispatch uses actual Codex collaboration tools. Automatic CLI discovery is not observed.

Distinct Developer participant completed GitHub and strict normalization implementation; five meaningful cases failed before and passed afterward in both modes. Independent TL reviewed source and independently passed the same five checks in both modes. Independent QA independently passed five existing tests plus ten canonical/control/Unicode/internal-spacing edge cases and idempotence/repeated-call isolation in each mode, with scenario written before execution. All three participant sessions remained distinct. All three read actual installed role/common/bootstrap/Story_Standard and selected adapter and validated concrete bindings; no self-approval, external lifecycle edits, commits or merges. TL observed an undiscovered read-section skill citation and used bounded local extraction, so automatic skill discovery remains unverified.

Claude/Antigravity native runtimes are not exposed by enabled tools. Their GitHub/strict behavior, automatic provider entrypoint/skill discovery, and native interpretation of historical two-invocation bridge remain explicitly unverified. Mechanical layout/parser success does not certify these behaviors. Tracked follow-up: [ST-000232](https://github.com/mycom08/mt-agent-devkit/issues/232). ST-000226/ST-000227 remain separate compliance release gates. No native blanket support or timing claims; explicit PO gap acceptance is required before Phase2 sign-off. No release is authorized by this QA result.


## Acceptance matrix

| AC | QA result |
|---|---|
| 1 Ownership/adapters | PASS: shared compiled corpus, isolated selected adapters, deterministic bundle and installed reference checks. |
| 2 Lifecycle/layout | PASS mechanical: six provider/mode combinations, both profiles and executable init/update/build/sync contracts. |
| 3 Legacy/preservation/recovery | PASS mechanical: frozen releases/helper execution, 24 bridge cases, protected ownership/runtime, explicit conflicts and real interruption/receipt-edit recovery regressions. Native legacy interpretation remains unverified in ST-000232. |
| 4 Repeat/pinning/isolation | PASS: repeat/no-op and provider-addition tests, immutable acquisition, partial-fetch refusal and tamper guards. |
| 5 Discovery/references | PASS managed references and explicit Codex adapter dispatch; automatic entrypoint/skill discovery UNVERIFIED in ST-000232. |
| 6 Static/deployment/native | Mechanical suite PASS; available Codex representative runs recorded separately. Unavailable native provider/mode gaps require explicit PO acceptance. |
| 7 Documentation/metadata | PASS: migration/rollback/support guidance, complete manifest and bridge-only legacy metadata; release-owned version files unchanged. |

No AC checkboxes are changed by QA. Full native certification is withheld for the listed gaps; Phase2 landing requires PO's explicit evidence-boundary decision and refreshed TL approval after this scenario commit.

## Correction round 3 — current evidence

Validated implementation: `63d340668a31c201eea4e1e7b9ee3ab0c2f97b4a`, independently approved by [TL](https://github.com/mycom08/mt-agent-devkit/pull/231#issuecomment-6073681208). This section supersedes the historical pending-acceptance statements above.

Independent QA Windows aggregate passed 94 tests in 257.174 seconds, all ten validator fixture groups and exit 0. The 24-case frozen release/provider/mode/stamp migration matrix preserves Antigravity settings and both legacy version-helper bytes through migration and repeated update; Claude still transfers its known hooks before retirement. Independent manifest inspection confirms both Antigravity helpers are excluded from retirement. Authoritative-corpus negative tests reject missing shared pointers and section aliases even where frozen counterparts exist. Template/internal validators, wrapper drift, 23 internal tests, deterministic bundle (151 assets/472 entries), and syntax checks for all eleven changed Bash/PowerShell files passed. Exact-head Linux CI [37879129657](https://github.com/mycom08/mt-agent-devkit/actions/runs/37879129657) independently executed the aggregate/internal/static gates. VERSION and version.txt remain unchanged.

Fresh GitHub and strict Codex fixtures were installed from the validated implementation, with receipt manifest SHA256 `c29f3aaaec0e18c6b2e02f04d0160bc9ee035acee3a02db86e7a79234f8c9bbe`. Installed resolver checks selected Codex from actual collaboration tool identities and validated fixture-local `.codex` / `.codex/agents` / `.codex/agents` bindings. Distinct installed Developer, TL and QA participants read the installed entrypoint, selected contract/adapter, role/common/bootstrap/standard and priming instructions. Developer observed three failures in five fixed normalization tests before implementation and five passes afterward in each mode. TL independently reviewed and passed all five tests per mode. QA created scenarios before execution, then passed five supplied cases plus ten independent cases per mode, including thirty assertions for Unicode/control whitespace, internal spacing, case, empty input, idempotence and repeated-call isolation. Participants preserved separate state ownership and made no external lifecycle mutations. One initial approval rejection misunderstood the synthetic case as unrelated work; a supported retry verified the actual ST-000221 AC5/AC6 scope and succeeded.

The user's accepted documented gap is recorded in [PO scope alignment](https://github.com/mycom08/mt-agent-devkit/issues/221#issuecomment-6073740724). Current AC5 permits verified explicit installed Codex dispatch in both modes with automatic native discovery, missing native Antigravity/Codex surfaces and Antigravity's unset default mapping explicitly uncertified. Claude/Antigravity native runs and native historical bridge interpretation remain unavailable; native macOS remains unobserved. These limitations are accepted for bounded Phase 2 landing and tracked in [ST-000232](https://github.com/mycom08/mt-agent-devkit/issues/232); they do not certify unsupported functionality or weaken core migration checks. ST-000226/ST-000227 remain separate gates before the combined release. No release is authorized.

| Current AC | QA result |
|---|---|
| 1 Ownership/adapters | PASS: shared corpus and isolated adapters, deterministic artifact and installed reference checks. |
| 2 Lifecycle/layout | PASS: six provider/mode layouts, both profiles and executable lifecycle fixtures. |
| 3 Legacy/preservation/recovery | PASS mechanical: 24 frozen migration cases, retained Antigravity hook targets, customization/runtime preservation and fault/rollback/conflict checks; native bridge interpretation remains explicitly unverified under accepted limitations. |
| 4 Repeat/pinning/isolation | PASS: repeats retain bytes, pinned acquisition/tamper/conflict/provider-isolation checks pass. |
| 5 Explicit dispatch/references | PASS under user-aligned scope: fresh distinct installed Codex participants in both modes and managed references; automatic discovery/native surfaces/mapping remain uncertified in ST-000232. |
| 6 Checks/native behavior | PASS within accepted boundary: 94 aggregate/23 internal tests, ten fixture groups, static/shell gates and fresh Codex behavior; unavailable native combinations/macOS remain unverified. |
| 7 Documentation/metadata | PASS: migration, rollback, hook preservation and future adaptation-review guidance; unreleased metadata covers changes, release-owned version files unchanged. |

QA validates all seven criteria under the explicit accepted boundary. This scenario update must be committed and pushed, and its documentation delta independently reviewed before merge. QA does not tick AC or close the story.
