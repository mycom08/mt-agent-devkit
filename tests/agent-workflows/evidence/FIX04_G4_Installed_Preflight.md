# FIX-04 G4 installed-workflow verification

**Date:** 2026-09-29  
**Integration head:** `6446c0ccd605eac9c3d9684882e5c48c6011d380`  
**Verdict:** G4 passed for the installed branch-preflight and runtime-state isolation path.

## Fixture and checks

- `python -m unittest scripts.test.test_branch_preflight -v` passed 22/22 tests. The suite covers B01–B10, blocked cases without recovery, SHA-pinned branch creation, strict mode without remote mutation, workflow ordering, and helper parity.
- `python scripts/validate_templates.py` passed.
- Fresh GitHub and strict-mode scaffold fixtures copied the installed `branch_preflight.py` byte-for-byte from the template. Git ignored memory, working-record, retro, and telemetry runtime paths in both modes. After a scaffold commit and runtime writes, `git status --porcelain` and `git diff HEAD --name-only` were empty.
- A separate fresh GitHub fixture used a local bare remote and a `main` branch containing the installed scaffold. The installed helper's `inspect --mode github --base main --story-branch story/ST-000211` passed. `create` passed with the full inspected base and remote SHAs. The new branch's `HEAD` equaled the inspected base SHA (`ed24ed9005e770dc21d25f39ab45b0d88332baca`). After committing a fixture `product.txt` change and writing runtime state, `git diff --name-only main..HEAD` contained only `product.txt`, and `git status --porcelain` was empty.
- The shell scaffold's tracked blob uses LF. This Windows checkout converted it to CRLF, so `bash -n` on the checkout failed. An LF-normalized scratch copy passed `bash -n` and scaffold checks in both modes. No tracked shell source change was needed.

All fixture repositories and scratch copies were removed. An initial complete-stage harness attempt had a PowerShell scalar-array assertion error; the corrected harness was rerun successfully. Six devkit working role-rule footers still mention a “stage-transition commit” as stale routing prose. The operative common rule forbids committing runtime state; wording cleanup remains separate from the G4 behavior verdict.
