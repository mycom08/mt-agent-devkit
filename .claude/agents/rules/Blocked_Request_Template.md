# Blocked Request Template

Use this template whenever implementation is blocked on input from a 3rd party (colleague, external team, or service owner).

## Agent Instructions

When you hit an external blocker during Stage 1 or Stage 2:

### Step 1 — Identify who to tag

Run these checks in order and stop at the first match:

1. **GitHub assignees** — `gh issue view <number> --repo {github-org}/{repo-name} --json assignees --jq '[.assignees[].login] | join(", @")'`
   - If one or more assignees are returned → use them as `@<login>`
2. **Story body** — scan the issue body for any GitHub @mentions or named individuals
   - If found → use that name/handle
3. **No match found** → set `Waiting on:` to `<unknown>` and report back to the orchestrator: `"Blocked — could not determine who to tag. Please provide the GitHub username or team name before I post the comment."` The orchestrator asks the user, then passes the name back before the comment is posted.

### Step 2 — Post the blocked comment

1. Fill in the template below — story ID, resolved `Waiting on` value, what's confirmed, what's missing
2. Write the filled-in comment to `.claude/agents/tmp/blocked_<story-id>.md`
3. Post it: `gh issue comment <number> --repo {github-org}/{repo-name} --body-file .claude/agents/tmp/blocked_<story-id>.md`
4. Change the story label: `gh issue edit <number> --repo {github-org}/{repo-name} --remove-label "status:ready" --add-label "status:blocked"`
5. Return to the orchestrator: `"Blocked — awaiting external input. Comment posted on issue #<number>."`

The orchestrator stops the pipeline and notifies the user.

---

## Comment Template

```markdown
## External Input Required — [ST-XXXXXX]

**Waiting on:** @<person or team name>
**Requested by:** <Agent role, e.g. Developer>
**Needed to unblock:** <what this enables, e.g. ST-000045 CD pipeline>

---

### ✅ Already Confirmed

| Item | Status |
|---|---|
| <confirmed item 1> | ✅ |
| <confirmed item 2> | ✅ |

---

### ❓ Still Need From You

Please fill in the table below and reply to this comment:

| # | What We Need | Your Answer |
|---|---|---|
| 1 | <specific question or value needed> | |
| 2 | <specific question or value needed> | |
| 3 | <specific question or value needed> | |

---

### 🔧 Helpful Commands

<Paste any commands the 3rd party can run to gather the required info>

---

Once you reply, notify the team and we will resume implementation.
```
