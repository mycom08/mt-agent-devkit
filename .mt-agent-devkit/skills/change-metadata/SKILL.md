---
name: change-metadata
description: Devkit change metadata, internal only - the changes.json entry and descriptions format, the CHANGELOG.md entry rule and _template file naming. Load before opening a PR in the devkit repo.
---

# Change Metadata

**Requires:** none. Internal only: never distributed to target projects.

## 1. CHANGELOG.md (every PR)

1. Before opening any PR, add a bullet to `CHANGELOG.md` under the current `## [x.y.z] - Unreleased` heading, the one the release workflow already opened.
2. Never add, edit or rename a version heading by hand. `VERSION` is owned by the release workflow and never hand-edited.
3. If `CHANGELOG.md` does not exist, create it in the standard format (use any existing entry as the template). The first story touching the repo owns creating it; never skip this step.

## 2. `changes.json` (template changes only)

`changes.json` tracks only template files deployed to target projects (under `.claude/agents/templates/`); devkit-internal files are excluded. A new version entry uses the `new`/`modified` key format:

```json
"X.Y.Z": {
  "new": ["<relative-path-to-new-file>"],
  "modified": ["<relative-path-to-modified-file>"],
  "descriptions": {
    "<relative-path>": "[ST-NNNNNN] <8-15 word plain-language delta>"
  }
}
```

Older entries use different formats; ignore them and always use `new`/`modified` for any entry you write.

**`descriptions`:** one line per file, shown verbatim in `sync devkit`'s update plan: `[ST-NNNNNN] <short delta>`, one clause per story, joined with `; `. State only what changed, not why (the rationale lives in `CHANGELOG.md` and the commit). No `"New/Fix (ST-XXXXXX, no separate version bump):"` wrapper prose, no issue backstory, no `"same X mirrored under Y"` notes.

If another still-unreleased story already described the file, **append your own `[ST-NNNNNN] ...` clause; never restate or wrap the earlier clauses.** Example: `[ST-000132] Split out of Agent_Common as the bootstrap tier. [ST-000140] §1 Working Record cap now configurable via CLAUDE.md.`

## 3. Template File Naming

Files under `.claude/agents/templates/` take a descriptive name with the `_template` suffix (`Developer_Rules_template.md`, `Sprint_Workflow_template.md`). The suffix is stripped when the file is written to a target project.
