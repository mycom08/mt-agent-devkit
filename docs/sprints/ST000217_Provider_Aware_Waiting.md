# ST-000217 Provider Aware Waiting Test Scenarios

QA scope: issue 217 current ten acceptance criteria; implementation revision
`5cc1771d48e8c68404e82b33197bc7cf084d6be8`, PR260. Independent QA runs precede
merge. Evidence stays in the selected Codex runtime; this document defines the
oracle before execution.

| Scenario | Expected result | AC |
|---|---|---|
| Discover deployed CI/local skills in three providers, two modes and both profiles | Shared contracts/helpers installed; receipt bindings used; custom content/history retained | 1,5,9 |
| PR and commit CI success with multiple workflow identities | Compact PASS contains inspected SHA and run identities; commit evidence cannot approve a PR | 1,3 |
| Required check pending, missing, failed, cancelled or timed out | PENDING or FAIL blocks advancement; a passing single run does not hide other evidence | 2,3,8 |
| No runs and earlier passing candidate | NO RUN includes changed-file scope and requires explicit canonical exception | 3,8 |
| Delayed discovery, bounded expiry and repeated wait | Original identity retained, no rerun launched; later completion observed | 4,8 |
| PR head changes, scope mismatch, authentication or network error | STALE/ERROR; no stale approval, private response or false PASS | 2,8,10 |
| Real local success/failure/exit124 and repeated waits | Launch once; true process exit retained; exit124 is FAIL, absent completion is PENDING | 4,6,8 |
| Empty command, missing identity, escaped/foreign provider path and launch error | Explicit sanitized error; no duplicate or foreign execution | 6,8 |
| Strict installed helper | CI rejected before invoking GitHub; full local verification remains usable | 7 |
| Log redaction and long output | Known secrets/URL credentials removed; private full log, bounded compact details | 6,10 |
| Native Codex foreground aggregate and live CI | Retain exec session and wait ID; completion collected through supported API; exact-head gates rechecked | 4,5,6 |
| Documentation and distributed gates | Runtime capability limits disclosed, real sequential fallback, independent TL/QA and canonical routing retained | 5,7,10 |
| Full required regression and syntax/LF gates | Internal validator/wrappers/unittest, template validator and both aggregate entrypoints pass; metadata unreleased only | 9,10 |

Unavailable native Claude/Antigravity execution is disclosed separately from
deterministic installation/helper execution. Revised AC5 does not require paid
or unavailable runtimes. No asynchronous wakeup certification follows from fixtures.
