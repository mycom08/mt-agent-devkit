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

## Exception — New Check Whose First Red Run Is the Expected, Correct Outcome

If the story adds a **new** validation check (e.g. a new rule in `validate_templates.py`) whose purpose is to catch a real template/workflow defect, an initial red run on `ci-validation` that fails because it genuinely caught that defect is an acceptable, expected gate outcome. Document this in the PR description under **CI Validation**, naming the specific defect the check caught, rather than treating the red run as something to work around.

This exception does **not** apply to a red run caused by the check's own setup/script failing before it ever evaluated a real file — that is a broken check, not a working new one, and must be fixed before opening the PR.

---

## Note — PR-Triggered Gates Still Need a `push: [ci-validation]` Trigger

If your CI gate is **PR-triggered** (`on: pull_request`, often with a `paths:` filter), it will not run when you push to `ci-validation`, so the pre-merge validation flow above produces no referenceable run. Add `ci-validation` as a push trigger alongside the PR trigger so Steps 1–3 work:

```yaml
on:
  pull_request:
    paths: [ ... ]
  push:
    branches: [ ci-validation ]
```

Keep the push trigger permanently — it makes every future change to this gate validatable on `ci-validation`.

---

## Note — Gitignored Reference Paths Won't Exist on the Runner

A check that resolves file paths (references, includes) can pass locally but fail on the runner if a referenced path is **gitignored** — the runner only checks out committed files. Before pushing, surface paths your check depends on that the runner won't have:

```bash
git ls-files --others --exclude-standard   # untracked but not ignored
git status --ignored --short               # ignored paths
```

Either commit the path, add it to the check's known-runtime-path allowlist, or skip it explicitly. Discovering this only after the first CI run is the common failure mode.

---

## Version

**Version:** 1.3 — New exception added: a new check's first red run genuinely catching a defect is an expected, acceptable gate outcome  
**Previous:** 1.2 — Notes added: PR-triggered gates need a push:[ci-validation] trigger; gitignored reference paths won't exist on the runner (ST-000016 retro)  
**Created:** 2026-06-16
