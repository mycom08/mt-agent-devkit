---
name: sprint-status
description: Sprint-state checks - in-flight stories, current sprint number, whether that sprint is done, whether the next one is already planned, the refinement target sprint and the sprint-label rules. Load before checking sprint state or picking a sprint to refine.
---

# Sprint Status

**Requires:** none

The only owner of these checks. Pass `--repo mycom08/mt-agent-devkit` on every query. Every check is repo-wide, with or without a feature: sprint numbers are one sequence. This skill only finds the state; the caller decides what to do with it.

## 1. In-Flight Stories

Run three separate queries, `gh issue list --label "<status>" --state open --limit 1000 --json number,title,labels` for `status:in-progress`, `status:review` and `status:testing`, and union the results (repeated `--label` flags in one query require all labels on one issue). Any result is unfinished work.

## 2. Current Sprint Number

N is the highest `sprint-N` label, compared numerically, over the section 1 results and every done story (`gh issue list --label "status:done" --state all --limit 1000 --json labels`); no such label means N = 0. To get a result set's highest number, add `--jq '[.[].labels[].name | select(test("^sprint-[0-9]+$")) | ltrimstr("sprint-") | tonumber] | max // 0'` to its query.

## 3. Current Sprint Done

Done means no in-flight story (section 1), and every issue from `gh issue list --label "sprint-N" --state open --limit 1000 --json number,title,labels` carries `status:done`.

## 4. Next Sprint Already Planned

Any result from `gh issue list --label "sprint-{N+1}" --state open --limit 1` means the next sprint is already planned.

## 5. Refinement Target Sprint

The target is the highest sprint over open `status:open` issues: `gh issue list --state open --label "status:open" --limit 1000 --json labels --jq '[.[].labels[].name | select(test("^sprint-[0-9]+$"))] | sort_by(ltrimstr("sprint-") | tonumber) | last'`. Do not use `gh label list`: it returns labels alphabetically, so `sprint-3` sorts higher than `sprint-13`.

## 6. Sprint-Label Violations

A `backlog` story carries no sprint; `open`, `ready`, `in-progress`, `review`, `testing`, `hotfix` and `blocked` stories carry exactly one. Skip `done`, `on-hold` and open-topic stories (`analysis-open-topic`).

Apply the rule to each line of `gh issue list --state open --limit 1000 --json number,title,labels --jq '.[] | "#\(.number) \(.title): \([.labels[].name] | join(", "))"'`.

Report each violation (ID, labels); change no label.
