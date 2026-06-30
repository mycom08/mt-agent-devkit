# QA Rules

**Applies to:** QA agent  
**Reference from:** `.claude/agents/working/instructions/qa_instructions.md`

---

## 1. Before Starting a Task (Mandatory Pre-Start Steps)

Do these **in order** before any testing or validation work:

1. **Read Project Priming** — `.claude/agents/working/context/Project_Priming.md`
2. **Read Story Standard (QA)** — `.claude/agents/working/rules/Story_Standard_QA.md`
3. **Read your Working Record** — `.claude/agents/working/working-record/QA_Working_Record.md`
4. **Read the relevant GitHub Issues** — filter by `status:testing` label for the current task

---

## 2. Locating Work Before Testing

Before testing any story:

1. Open the GitHub Issue for the story
2. Find the linked PR in the issue body (Deliverables section) or in the issue's linked pull requests
3. **Test on the dev branch** — do not wait for the PR to be merged; testing happens before merge
4. If no PR is linked or the story is not in `status:testing`, comment in issue for Dev

---

## 3. Story Status & Acceptance Criteria

Story status: `Backlog → Ready → In Progress → Review → Testing → Done`

- **Only QA ticks Acceptance Criteria** — do not mark AC complete if you are another role
- **Verify AC on the dev branch before the PR is merged** — QA sign-off is a merge gate
- Once all AC are checked and sign-off is complete, notify Dev to proceed with the merge
- Move story label to `status:done` after the PR is merged
- If AC cannot be validated (missing impl, unclear behavior), post a blocker Comment and keep in `status:testing`

See `Story_Standard.md` §4 for the full workflow and gate conditions.

---

## 4. Testing Rules

**This devkit has no runtime service, no database, and no API.** QA validates by reading and checking that template and workflow files are correct and complete.

**Before testing:**
- Always create a test scenario document first — do not begin testing without it
- Place it under `docs/feature/<feature_name>/test-scenarios/` or `docs/sprints/` using `Title_Case_With_Underscores`
- The scenario must cover: happy path, error cases, edge cases (missing placeholders, incorrect path references, mode-specific behavior)

**Template and workflow validation:**
- Read every template file changed by the story
- Verify all placeholders (`{{PROJECT_NAME}}`, `{github-org}`, etc.) are correct and present where expected
- Verify that the file name follows the `_template` suffix convention if it lives under `.claude/agents/templates/`
- Verify path references inside the file match the actual file structure of the devkit
- Check that GitHub mode content is complete and accurate; check strict mode content separately if the story affects strict mode

**Shell script validation:**
- For any changed `.sh` file: run `bash -n <script>` and confirm zero errors
- For any changed `.ps1` file: confirm PowerShell syntax check passes
- Review the script logic manually to confirm it achieves the intended behavior described in the story AC

**`changes.json` validation:**
- If the story modifies template files, verify that `changes.json` includes an entry for the current devkit version listing those files
- Verify the format is correct (array for older versions, object with `files`/`descriptions`/`checksums` for v0.0.8+)

**Test failure policy — any failure blocks sign-off:**
When any validation fails, QA must:
1. Post a blocker comment on the GitHub Issue describing the failure, tagging **Dev**
2. Keep the story in `status:testing`
3. Not sign off or tick any AC until every validation passes

---

## 5. Document Placement

- Place all new documents in the correct subfolder — see `.claude/agents/working/context/Document_Index.md` for paths
- Use `Title_Case_With_Underscores` for all document file names

---

## 6. Story Comment

- Post QA findings, acceptance gaps, and sign-off notes as **comments on the GitHub Issue**
- Reply in the same comment when retesting or validating the same issue

---

## 7. Post-Pass Commit (mandatory after validation passes)

Once all Acceptance Criteria are validated and QA sign-off is complete, QA **must** commit the test scenario document to the repository before notifying Dev to merge:

1. **Commit the Test Scenario document** — file under `docs/feature/<feature_name>/test-scenarios/`
2. Use commit message format: `test(<scope>): Add test scenario for ST-XXXXXX`
3. Push the commit

> **Gate:** Do not give merge sign-off until the test scenario document is committed and pushed.

---

## 8. Regression Check (mandatory before sign-off)

After all story AC are verified, confirm no regression was introduced:

1. Review the changed files and consider the blast radius
2. Specifically check: does the change affect `init project` behavior? Does it affect `sync devkit`? Does it affect both GitHub and strict mode?
3. **For template or workflow changes** (`.claude/agents/templates/**` or `.claude/agents/workflows/**`) → follow `docs/Template_Test_Strategy.md` as the test approach; run the Layer-1 gate (`python scripts/validate_templates.py` + `bash scripts/test/run.sh`, both must exit 0) as the regression suite
4. **If regression risk is identified** → post a comment on the story issue tagging **Dev**; treat as a QA failure and loop back for a fix

> **Gate:** Do not give merge sign-off until the regression check is complete.

---

## 9. Pre-PR Gate (when acting as Implementer)

When QA is the story Implementer, run the applicable local checks before opening a PR:

| Change type | Required local check |
|---|---|
| `.sh` files changed | `bash -n <each changed .sh file>` — zero errors |
| `.ps1` files changed | PowerShell syntax check — zero parse errors |
| `.github/workflows/` changed | Validate YAML syntax; verify job structure and step ordering |
| `.claude/agents/templates/**` or `.claude/agents/workflows/**` changed | `python scripts/validate_templates.py` + `bash scripts/test/run.sh` — both exit 0 (see `docs/Template_Test_Strategy.md`) |
| Docs only (no templates, workflows, or scripts) | Exempt |

> **Gate:** Do not open a PR until all applicable checks pass.

---

## 10. Live User Instruction Conflicts (when acting as Implementer)

If a live instruction from the user during implementation contradicts a prior decision recorded in the issue thread, the live instruction takes precedence. Acknowledge the conflict, proceed with the live instruction, and document the override in the PR description.

---

## 11. Reporting & Blockers

- Keep working record updates short and fact-based (story IDs, validation results, AC status)
- Post blockers immediately as a Comment on the GitHub Issue; tag Dev or TL as appropriate
- **Working record retention:** Delete entries older than 3 most-recent stories before writing a new one

---

## 12. Stage-Transition Commit (mandatory before handoff)

Commit agent memory file changes before signaling stage completion — see `.claude/agents/working/rules/Agent_Common.md §6`.

---

## 13. Troubleshooting Protocol (mandatory on any tooling/environment blocker)

On any tooling/environment blocker, follow the check-memory → fix → record-to-memory protocol in `.claude/agents/working/rules/Agent_Common.md §3`.

---

## Version

**Version:** 1.0 — Initial devkit-specific version  
**Created:** 2026-06-16
