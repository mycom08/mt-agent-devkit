# ST-000288 PO Skills (Internal) Test Scenarios

## Scope and acceptance

Validate the ten internal `po-*` skills, the slimmed PO instruction, deletion of the three PO rules files and their working wrappers, internal per-layout routing (including `po_validation`), the unchanged target layout, the ripple and the new checks. Source under test: PR 294, branch `ST-000288/po-skills-internal`, head `de06d2b3cbc951d7d90ec5478116f87027a040b9` (the TL Approved-SHA). Result: AC1-AC6 PASS. Python gates ran with a PATH shim (`python` -> `python3`) outside the repo.

## Scenarios

| AC | Scenario | Input / action | Required result | Result / evidence |
|---|---|---|---|---|
| AC1 | Happy path | `wc -c` on each `.mt-agent-devkit/skills/po-*/SKILL.md`; check the three provider wrapper sets; grep `**Requires:**` | 10 canonical files, 10 wrappers per provider; `po-core` <= 1500 B, others <= 4000 B; requires resolve; story ID rule in `po-write-story` | PASS; po-core 1345, max 3211 (po-write-story); 30 wrappers; every requires target exists; ID rule at line 14 |
| AC2 | Happy path | `git diff --name-status` against base; read `product_owner_instructions.md` | 3 rules files and 6 working wrappers deleted; instruction holds role summary, Common routing, records, "load `po-core`" | PASS; 9 deletions; instruction 2331 B with a PO Skills section; only Bootstrap sections 12 and 13 absent from the skills |
| AC3 | Happy path | Build and validate manifests for all 5 internal PO tasks (implementation, fix, closure, scope_question, po_validation) in a throwaway copy with the context each task needs | Bootstrap is `po-core`; no retired file read; `po_validation` adds `po-validate-ac` and `po-comment` | PASS; 5 of 5 build and validate; no retired source |
| AC3 | Error case | `QA` + `po_validation` | Rejected as unsupported role/task | PASS; covered by `test_internal_po_tasks_route_to_po_skills_without_retired_rules` |
| AC4 | Happy path | Build a bundle and inspect `deployment.json`; run `scripts.test.test_read_manifest` | Old PO files still shipped as assets; no `po-` skill shipped; target PO manifests build against old files | PASS; deployment lists the 3 rules files and templates intact; 23 tests OK, including target-layout PO assertions |
| AC5 | Happy path | grep corpus for retired filenames outside templates, bundle, docs, changelog | Only target-layout registry alternates, migration ledger, tests and the validator remain | PASS; remaining hits are target alternates in `read-routing.json`, `migration-inventory.json`, tests and `validate_retired_citations.py` |
| AC6 | Error case | Throwaway copy: plant `Story_Standard_PO.md` in `Agent_Common_Core.md`; separately plant `Product_Owner_Rules_Read_On_Demand §5` in a workflow | `validate_retired_citations.py` exits 1 naming file and line; clean copy exits 0 | PASS; clean rc 0; both plants rc 1 (Core line 81, Plan_Sprint_Workflow line 2); repo tree untouched |
| AC6 | Happy path | Run every gate at head | Every gate exits 0 | PASS; `validate_internal_harness.py`, `generate_wrappers.py --check`, `unittest scripts.test.test_internal_harness` (43 OK), `validate_templates.py`, `bash scripts/test/run.sh` (10 passed), `build_bundle.py --check` (180 assets, 568 files), all exit 0 |

## Notes and limitations

- The `build_bundle.py` path in the brief (`.mt-agent-devkit/scripts/`) is wrong; the script lives under `.mt-agent-devkit/distribution/phase2/`.
- Fresh manifest builds need runtime-state files that are gitignored; they were created as placeholders in a scratch copy only.
- Native provider skill discovery is not exercised, only file and frontmatter validity.
- Accepted by TL, not re-litigated: `po_validation` exists in both layouts with internal-only routing to `po-validate-ac`; orchestrator-mode escalation is deferred to ST-000292; the `po-` bundle exemption is owned by ST-000289.
