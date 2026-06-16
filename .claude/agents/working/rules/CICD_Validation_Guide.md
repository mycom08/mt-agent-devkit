# CI/CD Workflow Validation Guide

**Applies to:** Any implementer (Developer, Technical Lead, QA, Business Analyst)  
**Trigger:** Story Technical Scope includes any file under `.github/workflows/`

---

## Why This Matters

GitHub Actions workflow files cannot be unit-tested locally — the only way to confirm they behave correctly is to let the GitHub runner execute them. The `ci-validation` branch is a permanent staging branch for this purpose: workflow changes run against the real runner without touching `main`.

---

## One-Time Setup (verify before first use on a new workflow)

The `ci-validation` branch must satisfy two conditions:

1. It exists on origin:
   ```bash
   git ls-remote --heads origin ci-validation
   ```
2. The target workflow's `on.push.branches` filter includes `ci-validation` **or** uses no branch filter.

If either condition is missing, fix it and push the branch filter change to both `ci-validation` and `main` before validating the story's actual workflow change.

---

## Validation Steps

**Step 1 — Push your workflow changes to `ci-validation`**

```bash
git push origin HEAD:ci-validation --force
```

**Step 2 — Wait for the run to appear (~30 seconds) and read the result**

```bash
gh run list --branch ci-validation --limit 3
gh run view <run-id> --log
```

If the run **fails**: fix the workflow and repeat from Step 1.  
If the run **passes**: proceed to Step 3.

**Step 3 — Capture the passing run URL**

Include the run URL in the PR description under a **CI Validation** heading:

```
## CI Validation
Passing run on `ci-validation`: <run-url>
```

---

## Gate

> **Gate:** Do not open a PR for a story touching `.github/workflows/` until a passing run on `ci-validation` is confirmed and its URL is included in the PR description.

---

## Exception — Cosmetic Changes

If the only change is cosmetic with no logic impact (e.g., renaming a job display name, reordering steps with identical effect), state the reason explicitly in the PR description under **CI Validation** — a live run is not required in that case.

---

## Exception — `workflow_dispatch`-Only Workflows

GitHub only discovers `workflow_dispatch` workflows from the default branch, so they cannot be triggered on `ci-validation` before merging. Use this procedure instead:

**Step 1 — Merge to main first**

Open the PR with a thorough description and get TL review as normal, but skip the CI Validation run URL requirement. State in the PR description:

```
## CI Validation
workflow_dispatch-only — pre-merge ci-validation run not possible.
Post-merge validation will be run on ci-validation; hotfix will follow if needed.
```

**Step 2 — Post-merge validation on `ci-validation`**

After merging to main, sync `ci-validation`:

```bash
git push origin main:ci-validation --force
```

Then trigger the workflow:

```bash
gh workflow run <workflow-file.yml> --ref ci-validation
```

Wait for the run to complete and verify it passes:

```bash
gh run list --workflow=<workflow-file.yml> --branch ci-validation --limit 3
gh run view <run-id> --log
```

**Step 3 — Hotfix if the run fails**

If the post-merge run fails, create a hotfix branch off main, fix the workflow, and merge back through a standard PR.

---

## Version

**Version:** 1.1 — Exception added for workflow_dispatch-only workflows  
**Created:** 2026-06-16
