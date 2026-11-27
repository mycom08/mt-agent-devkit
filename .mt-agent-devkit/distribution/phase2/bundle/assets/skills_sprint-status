---
name: sprint-status
description: Sprint-state checks - in-flight stories, current sprint number, whether that sprint is done, whether the next one is already planned, and the refinement target sprint. Load before checking sprint state or picking a sprint to refine.
---

# Sprint Status

**Requires:** none

The only owner of these checks. Use the project's mode. `feature_name` is the sprint's feature or `none`; `<plan>` is `docs/feature/<feature_name>/plan/`; strict-mode story files are `{RUNTIME_ROOT}/docs/stories/*.md`. This skill only finds the state; the caller decides what to do with it.

## 1. In-Flight Stories

- **GitHub mode** (repo-wide, feature or not): run three separate queries, `gh issue list --label "<status>" --state open --limit 1000 --json number,title,labels` for `status:in-progress`, `status:review` and `status:testing`, and union the results (repeated `--label` flags in one query require all labels on one issue). Any result is unfinished work.
- **Strict mode:** story files with `**Status:**` `in-progress`, `review` or `testing`.

## 2. Current Sprint Number

- **GitHub mode** (repo-wide, feature or not): N is the highest `sprint-N` label, compared numerically, over the section 1 results and every done story (`gh issue list --label "status:done" --state all --limit 1000 --json labels`); no such label means N = 0. To get a result set's highest number, add `--jq '[.[].labels[].name | select(test("^sprint-[0-9]+$")) | ltrimstr("sprint-") | tonumber] | max // 0'` to its query.
- **Strict mode, feature sprint:** N is the sprint marked `🔄 In Progress` in `<plan>Product_Backlog.md`. Also read its `Sprint_N_Overview.md`.
- **Strict mode, non-feature sprint:** the section 1 files name the active sprint. If there are none, take the `**Status:** done` files, ignoring files with an `**Analysis Open Topic:**` line: N is the `**Sprint:**` field of the most recently created story (highest ID).

## 3. Current Sprint Done

- **GitHub mode:** no in-flight story (section 1), and every issue from `gh issue list --label "sprint-N" --state open --limit 1000 --json number,title,labels` carries `status:done`.
- **Strict mode:** read every story file of sprint N; all have `**Status:** done`.

## 4. Next Sprint Already Planned

- **GitHub mode** (every sprint): any result from `gh issue list --label "sprint-{N+1}" --state open --limit 1` means already planned.
- **Strict mode, feature sprint:** already planned if `<plan>Sprint_{N+1}_Overview.md` exists.
- **Strict mode, non-feature sprint:** no check.

## 5. Refinement Target Sprint

- **GitHub mode** (feature or not): the highest sprint over open backlog issues: `gh issue list --state open --label "status:backlog" --limit 1000 --json labels --jq '[.[].labels[].name | select(startswith("sprint-"))] | sort_by(ltrimstr("sprint-") | tonumber) | last'`. Sprint numbers are one repo-wide sequence. Do not use `gh label list`: it returns labels alphabetically, so `sprint-3` sorts higher than `sprint-13`.
- **Strict mode, feature sprint:** the sprint marked `🔲 Planned` in `<plan>Product_Backlog.md`.
- **Strict mode, non-feature sprint:** over the `**Sprint:**` values of all story files, the highest sprint number with at least one `**Status:** backlog` story.
