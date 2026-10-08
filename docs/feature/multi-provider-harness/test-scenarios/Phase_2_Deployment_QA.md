# Phase 2 Deployment QA

Story: ST-000221. Candidate: `06f4de12d6d90b46ca06055613033e18fa40dd3e`.

## Scenarios

| Case | Oracle |
|---|---|
| Fresh/install/update/build | All three providers and both modes install shared ownership and selected adapter; repo/root profiles remain distinct. |
| Legacy direct/missing stamp | Frozen v0.1.48ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â‚¬Å¡Ã‚Â¬ÃƒÂ¢Ã¢â€šÂ¬Ã…â€œ50 Claude/Antigravity, both modes, preserve custom content and runtime bytes; two-pass bridge reaches verified receipt. Native interpretation is separately assessed. |
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
- Suite includes all six provider/mode layouts and both profiles; real lifecycle launchers; immutable release/sync interruption; frozen v0.1.48ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“50 helpers and 24 two-pass legacy migration cases; customization/runtime preservation, conflicts, provider isolation, idempotency and recovery/rollback including receipt edits.
- Only changed historical templates are compatible ordinary/root sync headers, reviewed in full against retained legacy bodies. Additive metadata and bridge-only files alias match approved legacy parser decisions. VERSION and version.txt are unchanged.

## Native evidence and support boundary

Source-bound disposable installed fixtures use receipt source candidate `06f4de12d6d90b46ca06055613033e18fa40dd3e`, manifest SHA256 `9bbdddf320a1c3ece4456e2ec9225c601989079f78880ad31a482d5ca6e730a2` and fixture-local `.codex/agents` bindings. Explicit installed-instruction dispatch uses actual Codex collaboration tools. Automatic CLI discovery is not observed.

Distinct Developer participant completed GitHub and strict normalization implementation; five meaningful cases failed before and passed afterward in both modes. Independent TL reviewed source and independently passed the same five checks in both modes. Independent QA independently passed five existing tests plus ten canonical/control/Unicode/internal-spacing edge cases and idempotence/repeated-call isolation in each mode, with scenario written before execution. All three participant sessions remained distinct. Both read actual installed role/common/bootstrap/Story_Standard and selected adapter and validated concrete bindings; no self-approval, external lifecycle edits, commits or merges. TL observed an undiscovered read-section skill citation and used bounded local extraction, so automatic skill discovery remains unverified.

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
