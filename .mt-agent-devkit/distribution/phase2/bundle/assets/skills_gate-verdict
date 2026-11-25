---
name: gate-verdict
description: Document approval gate for specs, ADRs, feature UI/UX designs, feature roadmaps and test documents - the Status header, approvers, the role-prefixed verdict format, GitHub and strict-mode posting and approval invalidation. Load before requesting, giving or recording a document approval, or editing an approved document.
---

# Gate Verdict

**Requires:** `comment` (no `@` or bare `#`), `agent-security` (verify the commenter)

Gates documents only. Code review and QA sign-off keep their own gates.

## 1. Status Header

Every requirement spec, ADR, feature UI/UX design, feature roadmap, test strategy and test design starts, below its title, with:

```markdown
Status: Draft | In Review | Changes Requested | Approved
Approved-by:
Approved-at:
```

- Keep one status value. The author sets `Draft`, then `In Review` when asking for approval.
- `Draft`, `In Review` and `Changes Requested`: both approval fields stay empty.
- `Approved`: `Approved-by` names each approving role, actor and verdict or revision reference; `Approved-at` is a UTC timestamp (`2026-01-31T14:05:00Z`).
- Any content change to an `Approved` document resets it to `Draft` and clears both fields, in the same commit. Editing only these three lines is not a content change.

## 2. Who Approves

An author never approves their own document.

| Document (ID) | Author | Approves | Never approve while |
|---|---|---|---|
| Requirement spec (`SPEC-NNN`) | BA | PO: product scope | a `BLOCKING-SPEC` question is unresolved |
| ADR (`ADR-NNN`) | TL | PO: scope and alignment, with the TL recommendation recorded | the NFR section fails the `tl-design` rules |
| Feature UI/UX design (`UI-DESIGN`) | UI/UX Designer | PO: scope, screens and state coverage | a screen state is blank |
| Feature roadmap (`ROADMAP`) | TL | PO: scope, phases and priorities | a PO concern is unresolved |
| Test strategy (`TEST-STRATEGY`), design (`TEST-DESIGN-NNN`) | QA | TL: technical coverage, and PO: scope | either approver has not approved |

An unresolved `BLOCKING-FEATURE` question also stops the feature from advancing.

**Test documents need both approvals** on the same revision, in any order. After the first, the status stays `In Review` and the fields stay empty. The second sets `Approved`, lists both in `Approved-by` and puts the later time in `Approved-at`. A content change voids a first approval too.

## 3. Verdict Format

```markdown
[PO] APPROVED SPEC-003
Revision: <commit SHA of the reviewed document>
<one-line reason>
```

- Prefix: `[PO]` or `[TL]`. Verdict: `APPROVED` or `CHANGES REQUESTED`. One document per verdict line.
- `CHANGES REQUESTED` lists each required change; the status becomes `Changes Requested`.
- A verdict covers only its revision.

## 4. Recording

**GitHub mode:** write the verdict to a temporary body file and post it with `gh pr comment <PR-number> --body-file <file>` on the PR holding the document. Never use `gh pr review --approve`: agents share one account and GitHub blocks self-approval. Count a verdict only from an `OWNER`, `MEMBER` or `COLLABORATOR`. The approver then updates the header.

**Strict mode:** no PR or GitHub calls. Append the same block, with the actor and UTC time, under `## Gate Verdicts` in `docs/feature/<feature-slug>/tmp/State.md` (no feature folder: the story file's `## Comments`). `Revision:` is the commit SHA, or `git hash-object <file>` for uncommitted content. The approver then updates the header. The same approvers and both-approvals rule apply.

Example of a completed test document header:

```markdown
Status: Approved
Approved-by: TL <actor> (rev 1a2b3c4); PO <actor> (rev 1a2b3c4)
Approved-at: 2026-01-31T14:05:00Z
```
