# Product Owner Memory

## Stored Facts

### Fact 1
- **Rule:** Distributable templates live under `.claude/agents/templates/` (rules in `rules/`, shared workflows in `shared/workflows/`, each named `*_template.md`). There is no top-level `templates/` directory. A story whose target is only `.claude/agents/working/` changes the devkit's own team and never reaches consumer projects — name the `*_template.md` file explicitly in the story, and add the mirror-the-working-copy criterion separately when both are wanted.
- **Applies when:** Writing any devkit story that changes agent rules, workflows, or priming.
- **Evidence:** #182–#188 (all seven filed with corrected paths); `ls .claude/agents/templates/rules/`.
- **Expires when:** The devkit relocates its template tree.

### Fact 2
- **Rule:** Unscheduled backlog issues use title `[DEVKIT] <what is wrong>` with **no** `ST-` ID (IDs are assigned at sprint pull-in) and labels `status:backlog` + `enhancement-2` only — no sprint label, no feature label. This overrides `Product_Owner_Rules_Read_On_Demand.md §5`'s `[ST-XXXXXX][DEVKIT]` + `sprint-N` shape, which applies to stories filed straight into a sprint.
- **Applies when:** Filing backlog issues that are not being scheduled in the same act.
- **Evidence:** House style in #174, #175, #176, #180; batch #182–#188.
- **Expires when:** `§5` is amended to cover the unscheduled case directly.
