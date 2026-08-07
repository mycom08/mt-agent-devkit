# CI/CD Workflow Validation Guide

**Applies to:** Any implementer (Developer, Technical Lead, QA, Business Analyst)  
**Trigger:** Story Technical Scope includes any file under `.github/workflows/`

---

## Why This Matters

GitHub Actions workflow files cannot be unit-tested locally — the only way to confirm they behave correctly is to let the GitHub runner execute them. The `ci-validation` branch is a permanent staging branch for this purpose: workflow changes run against the real runner without touching `master`.

---

## One-Time Setup (verify before first use on a new workflow)

The `ci-validation` branch must satisfy two conditions:

1. It exists on origin:
   ```bash
   git ls-remote --heads origin ci-validation
   ```
2. The target workflow's `on.push.branches` filter includes `ci-validation` **or** uses no branch filter.

If either condition is missing, fix it and push the branch filter change to both `ci-validation` and `master` before validating the story's actual workflow change.

---

## Validation Steps

**Step 0 — Pre-check: does a `pull_request` trigger already cover this change?**

Before pushing to `ci-validation`, inspect the target workflow's `on:` block:

- **If `on.pull_request` exists with no branch/path restriction narrower than the story's changed paths** (the common case — e.g. `pull_request:` with no `branches:` filter, and no `paths`/`paths-ignore` filter that would exclude this story's changes): **skip the `ci-validation` push entirely.** Open the PR as normal — the `pull_request`-triggered run that fires when the PR opens **is** the pre-merge validation run. Cite that run's URL in the PR's **CI Validation** section instead of a separate `ci-validation` run URL. Pushing to `ci-validation` first would produce a second, identical run against the same commit with no added signal.
- **If not** (the workflow is `push`-only, or the `pull_request` trigger has a `branches`/`paths` filter that would exclude this story's changes): proceed with Steps 1–3 below — the `ci-validation` push is the only way to get a real pre-PR run.

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

> **Gate:** Do not open a PR for a story touching `.github/workflows/` until a passing run on `ci-validation` is confirmed and its URL is included in the PR description — **unless** Step 0 applies (the `pull_request` trigger already covers the change), in which case the PR's own `pull_request`-triggered run is the validation run: confirm it passes and cite its URL in the **CI Validation** section before requesting review.

---

## Exception — Cosmetic Changes

If the only change is cosmetic with no logic impact (e.g., renaming a job display name, reordering steps with identical effect), state the reason explicitly in the PR description under **CI Validation** — a live run is not required in that case.

---

## Exception — `workflow_dispatch`-Only Workflows

GitHub only discovers `workflow_dispatch` workflows from the default branch, so they cannot be triggered on `ci-validation` before merging. The standard pre-merge gate does not apply. Use this procedure instead:

**Step 1 — Merge to master first**

Open the PR with a thorough description and get TL review as normal, but skip the CI Validation run URL requirement. State in the PR description:

```
## CI Validation
workflow_dispatch-only — pre-merge ci-validation run not possible.
Post-merge validation will be run on ci-validation; hotfix will follow if needed.
```

**Step 2 — Post-merge validation on `ci-validation`**

After merging to master, sync `ci-validation` with master so it picks up the new workflow file:

```bash
git push origin master:ci-validation --force
```

Then trigger the workflow against the `ci-validation` branch:

```bash
gh workflow run <workflow-file.yml> --ref ci-validation
```

Wait for the run to complete and verify it passes:

```bash
gh run list --workflow=<workflow-file.yml> --branch ci-validation --limit 3
gh run view <run-id> --log
```

**Step 3 — Hotfix if the run fails**

If the post-merge run fails, create a hotfix branch off master, fix the workflow, and merge back through a standard PR. Apply the same `workflow_dispatch` exception — no pre-merge ci-validation run required.

---

## Exception — New Check Whose First Red Run Is the Expected, Correct Outcome

If the story adds a **new** CI check whose purpose is to exercise real application behavior end-to-end, an initial red run on `ci-validation` that fails on genuine application assertions (not on the check's own setup/infra) is an acceptable, expected gate outcome — it means the new check is doing its job. Document this in the PR description under **CI Validation**, naming the specific failing assertions the check caught, rather than treating the red run as something to work around or suppress.

This exception does **not** apply to a red run caused by the check's own setup/infra failing before the application code under test ever ran — that is a broken workflow, not a working new check, and must be fixed before opening the PR.

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

**Version:** 1.4 — Step 0 pre-check added: skip the `ci-validation` push when the workflow's `pull_request` trigger already covers the change — the PR's own run is the validation run  
**Previous:** 1.3 — New exception added: a new check's first red run on genuine application assertions is an expected, acceptable gate outcome  
**Created:** 2026-06-05
