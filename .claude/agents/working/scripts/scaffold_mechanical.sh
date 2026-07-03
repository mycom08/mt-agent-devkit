#!/usr/bin/env bash
# Writes every scaffold file that needs zero project-specific judgment — pure copy or
# fixed-token substitution. Run this BEFORE generating the adaptive-tier files (CLAUDE.md,
# README.md, Project_Priming.md, Document_Index.md, 5 instruction files, 8 rules files that
# need real adaptation, 4 wiki docs) so an LLM agent never has to touch content it would
# only reproduce byte-for-byte.
#
# Usage: scaffold_mechanical.sh <devkit_root> <target_project> <mode:strict|github> [github-org/repo-name]
#
# <github-org/repo-name> is optional. When omitted, {github-org}/{repo-name} tokens in rules
# files are left as literal placeholders (same convention already used for workflow files —
# fill them in manually or via a follow-up run once the GitHub repo exists).
set -euo pipefail

DEVKIT_ROOT="$1"
TARGET="$2"
MODE="$3"
GH_SLUG="${4:-}"

TPL="$DEVKIT_ROOT/.claude/agents/templates"
AGENTS="$TARGET/.claude/agents"

if [[ "$MODE" != "strict" && "$MODE" != "github" ]]; then
  echo "error: mode must be 'strict' or 'github', got '$MODE'" >&2
  exit 1
fi

# 1. Directories
mkdir -p "$AGENTS/context" "$AGENTS/memory" "$AGENTS/rules" "$AGENTS/working-record" \
         "$AGENTS/workflows" "$AGENTS/scripts" "$AGENTS/retros" "$AGENTS/tmp" "$AGENTS/docs" \
         "$TARGET/docs/wiki"
# No .gitkeep for retros/ — it's gitignored below (github mode) or covered by the blanket
# .claude/agents/ ignore (strict mode), so an empty-dir placeholder would never be committed.

if [[ "$MODE" == "strict" ]]; then
  mkdir -p "$AGENTS/docs/stories" "$AGENTS/docs/sprints" "$AGENTS/docs/reviews"
  echo "0" > "$AGENTS/docs/story_counter.txt"
fi

# 2. Verbatim rules files — content-diffed against real scaffold output to confirm they
#    carry no project-specific judgment beyond {github-org}/{repo-name} substitution. NOT
#    the same set Init_Project_Workflow.md's prose implies: Story_Standard_Dev/PO/QA all
#    reference a hardcoded generic API-spec location (`docs/api/`) in plain prose (no
#    {placeholder} token) that real scaffolds rewrite per-project, so those three — plus
#    the base Story_Standard.md and the three explicitly-adaptive role files — belong in
#    the adaptive tier, not here. Story_Standard_TL has no such reference and is safe.
#    Do not add a file here without re-verifying: diff a scripted copy against a known-good
#    real scaffold output for that file (byte tokens alone are not sufficient — some
#    per-project rewrites use plain prose with no {} marker at all).
VERBATIM_RULES=(
  Agent_Common Blocked_Request CICD_Validation_Guide Clean_Code_Rules
  Product_Owner_Rules Retro_Rules Story_Standard_TL Strict_Mode_Story_Guide
)
GH_ORG="${GH_SLUG%%/*}"
GH_REPO="${GH_SLUG##*/}"
for f in "${VERBATIM_RULES[@]}"; do
  src="$TPL/rules/${f}_template.md"
  dst="$AGENTS/rules/${f}.md"
  if [[ -n "$GH_SLUG" ]]; then
    sed -e "s/{github-org}/${GH_ORG//\//\\/}/g" -e "s/{repo-name}/${GH_REPO//\//\\/}/g" "$src" > "$dst"
  else
    cp "$src" "$dst"
  fi
  # Strip a leading UTF-8 BOM if the template carries one — devkit convention is BOM-free.
  sed -i '1s/^\xEF\xBB\xBF//' "$dst"
done

# 3. Workflow files — never adapted; {github-org}/{repo-name} and every {{PLACEHOLDER}} in
#    these files are intentionally left literal for runtime resolution (devkit convention).
NONSPLIT_WORKFLOWS=(Sync_Devkit_Workflow Workflow_Guide)
for f in "${NONSPLIT_WORKFLOWS[@]}"; do
  cp "$TPL/workflows/${f}_template.md" "$AGENTS/workflows/${f}.md"
done

SPLIT_WORKFLOWS=(
  Create_Stories_Workflow Plan_Sprint_Workflow Refine_Sprint_Workflow
  Resume_Story_Workflow Shared_Pipeline_Stages Sprint_Workflow Start_Story_Workflow
)
for f in "${SPLIT_WORKFLOWS[@]}"; do
  shared="$TPL/shared/workflows/${f}_Shared_template.md"
  modefile="$TPL/$MODE/workflows/${f}_template.md"
  dst="$AGENTS/workflows/${f}.md"
  awk '/<!-- SHARED-START -->/{flag=1;next}/<!-- SHARED-END -->/{flag=0}flag' "$shared" > "$dst"

  # Mode-specific appendix: line 1 of the mode file is always a "Shared logic:" pointer
  # comment (never real content). Most mode files are ENTIRELY comments beyond that —
  # internal notes for whoever maintains the template, not content to copy — so only
  # append a separator + content when something real (non-comment, non-blank) remains.
  mode_body="$(tail -n +2 "$modefile" | grep -vE '^<!--.*-->[[:space:]]*$' || true)"
  if [[ -n "$(printf '%s' "$mode_body" | tr -d '[:space:]')" ]]; then
    trimmed="$(printf '%s\n' "$mode_body" | awk '
      NF{p=1} p{buf[++n]=$0}
      END{last=1; for(i=n;i>=1;i--){if(buf[i]!~/^[ \t]*$/){last=i;break}}
          for(i=1;i<=last;i++) print buf[i]}')"
    printf '\n---\n\n' >> "$dst"
    printf '%s\n' "$trimmed" >> "$dst"
  fi
done

# 4. Version-check scripts (verbatim)
cp "$TPL/scripts/check_devkit_version.ps1" "$AGENTS/scripts/check_devkit_version.ps1"
cp "$TPL/scripts/check_devkit_version.sh" "$AGENTS/scripts/check_devkit_version.sh"

# 5. devkit_version.txt
cp "$DEVKIT_ROOT/version.txt" "$AGENTS/devkit_version.txt"

# 6. Blank memory files
for role in Business_Analyst Developer Product_Owner QA Technical_Lead; do
  role_label="${role//_/ }"
  printf '# %s Memory\n\nNo facts recorded yet.\n' "$role_label" > "$AGENTS/memory/${role}_Memory.md"
done

# 7. Blank working-record files
TODAY="$(date +%Y-%m-%d)"
for role in Business_Analyst Developer Product_Owner QA Technical_Lead; do
  role_label="${role//_/ }"
  printf '# %s Working Record\n\n## %s\n**Completed:** —\n**In Progress:** —\n**Impediments:** —\n' \
    "$role_label" "$TODAY" > "$AGENTS/working-record/${role}_Working_Record.md"
done

# 8. .gitignore additions
if [[ "$MODE" == "github" ]]; then
  cat >> "$TARGET/.gitignore" <<'EOF'

# Claude Code agent temp files
.claude/agents/tmp/

# Workflow output documents
/result/

# Agent working records — ephemeral session state, no long-term git value
.claude/agents/working-record/*_Working_Record.md

# Agent retrospective files — for human review only, not part of the committed codebase
.claude/agents/retros/
EOF
else
  cat >> "$TARGET/.gitignore" <<'EOF'

# Claude Code agent files — all agent infrastructure and docs are local-only
.claude/agents/

# Workflow output documents
/result/
EOF
fi

# 9. .claude/settings.json SessionStart hook — only handles the "file doesn't exist yet" case,
#    since merging into arbitrary existing JSON safely needs a real parser, not sed. If the
#    file already exists, this step is skipped and must be merged separately (this is the
#    uncommon case for brand-new repos, which is the primary caller of this script).
mkdir -p "$TARGET/.claude"
if [[ ! -f "$TARGET/.claude/settings.json" ]]; then
  UNAME_S="$(uname -s 2>/dev/null || echo unknown)"
  if [[ "$UNAME_S" == MINGW* || "$UNAME_S" == MSYS* || "${OS:-}" == "Windows_NT" ]]; then
    cat > "$TARGET/.claude/settings.json" <<'EOF'
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{ "type": "command", "command": "powershell -File .claude/agents/scripts/check_devkit_version.ps1", "timeout": 10 }]
      }
    ]
  }
}
EOF
  else
    cat > "$TARGET/.claude/settings.json" <<'EOF'
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{ "type": "command", "command": "bash .claude/agents/scripts/check_devkit_version.sh", "timeout": 10 }]
      }
    ]
  }
}
EOF
  fi
  echo "settings.json: created"
else
  echo "settings.json: already exists — SessionStart hook NOT merged, do this separately"
fi

echo "Mechanical scaffold complete: $TARGET"
