#!/usr/bin/env python3
"""
validate_templates.py -- Layer-1 corpus invariant checker for mt-agent-devkit.

Scans .claude/agents/templates/**/*.md and .claude/agents/workflows/**/*.md
and enforces 6 deterministic invariants. Exits non-zero on any hard violation.

Output contract: one line per finding
  [ERROR]        file:line -- <issue>   (counts toward non-zero exit)
  [KNOWN_ISSUE]  file:line -- <issue>   (informational; does not affect exit code)

Usage:
  python scripts/validate_templates.py            # scan full corpus
  python scripts/validate_templates.py <dir>...   # scan specific dirs or files
"""

import sys
import re
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

SCAN_DIRS = [
    REPO_ROOT / ".claude/agents/templates",
    REPO_ROOT / ".claude/agents/workflows",
]

CHANGES_JSON = REPO_ROOT / "changes.json"

# ---------------------------------------------------------------------------
# Invariant #2: placeholder registry
# ---------------------------------------------------------------------------

# All legal {{TOKEN}} double-brace names in the corpus.
# Add new names here when introducing a new {{PLACEHOLDER}} in a template.
KNOWN_DOUBLE_BRACE_TOKENS = {
    "ANTIPATTERNS",
    "AUTOMATION_SUITE",
    "BACKWARD_COMPATIBILITY_RULES",
    "BRANCH_NAMING_FORMAT",
    "CODE_ORGANIZATION",
    "CODE_QUALITY_CHECKLIST",
    "COMMENT_STYLE",
    "COMMIT_FORMAT",
    "CONCURRENCY_PATTERNS",
    "CONVENTIONS_CHECKLIST",
    "CORE_PRINCIPLES",
    "COVERAGE_COMMAND",
    "COVERAGE_MINIMUM",
    "COVERAGE_TARGET",
    "DATE",
    "DEVKIT_SOURCE_URL",
    "DEVKIT_VERSION",
    "DONTS",
    "DOS",
    "ERROR_HANDLING",
    "ERROR_HANDLING_STANDARDS",
    "ERROR_RESPONSE_FORMAT",
    "FILE_NAMING_STANDARDS",
    "INTEGRATION_TEST_COMMANDS",
    "INTEGRATION_TEST_PLACEMENT",
    "LANGUAGE",
    "LINT_FORMAT_COMMANDS",
    "LOGGING_STANDARDS",
    "MODE",
    "NAMING_CONVENTION_1",
    "NAMING_CONVENTION_2",
    "NAMING_CONVENTION_3",
    "NAMING_SUBJECT_1",
    "NAMING_SUBJECT_2",
    "NAMING_SUBJECT_3",
    "PLACEHOLDER",
    "PROJECT_DESCRIPTION",
    "PROJECT_FILE_STRUCTURE",
    "PROJECT_NAME",
    "RECOMMENDED_PATTERNS",
    "REPOS",
    "SECURITY_CHECKLIST",
    "START_COMMAND",
    "TEST_FILE_NAMING_CONVENTION",
    "TEST_FILE_ORGANIZATION",
    "TEST_FILE_PLACEMENT",
    "TEST_NAMING_CONVENTION",
    "TEST_RUN_COMMAND",
    "TEST_RUN_COMMANDS",
    "TL_MAY_SUGGEST",
    "TL_MUST_PASS",
    "TL_SHOULD_FIX",
    "UNIT_TEST_NAMING",
    "UNIT_TEST_PLACEMENT",
    "UNIT_TEST_STRUCTURE",
}

# Legal single-brace ALL-CAPS {TOKEN} names (second legitimate placeholder class).
# The single-brace check ONLY applies to all-caps tokens -- mixed-case and
# lowercase single-brace tokens (e.g. {github-org}, {Language}) appear as prose
# notation in workflow instructions and are not checked here.
KNOWN_SINGLE_BRACE_TOKENS = {
    # Variables in Sync_Devkit_Workflow_template.md
    "CURRENT_VERSION",
    "DEVKIT_SOURCE_URL",
    "DEVKIT_VERSION",
    "LANGUAGE",
    "LATEST_VERSION",
    "METHOD",
    "MODE",
    # Variables in Init_Project_Workflow.md and Update_Project_Workflow.md
    "DATE",
    "NFR",
    "PLACEHOLDER",
    "PROJECT_DESCRIPTION",
    "PROJECT_NAME",
    "PROJECT_VERSION",
    "REPOS",
    "TARGET_PROJECT",
}

# ---------------------------------------------------------------------------
# Invariant #4: retired trigger strings
# ---------------------------------------------------------------------------

# EMPTY by design. Populate only when a trigger is confirmed retired.
# "update agents" is a LIVE target-project operation -- must NEVER be seeded.
RETIRED_TRIGGERS: list = []

# ---------------------------------------------------------------------------
# Invariant #5: changes.json allowlists
# ---------------------------------------------------------------------------

# Paths listed in changes.json that were legitimately removed/moved in ST-000006
# (templates split into github/strict/shared layout). These entries remain in
# historical version records but the files no longer exist on disk.
ALLOWLIST_REMOVED_PATHS = {
    ".claude/agents/templates/CLAUDE_TEMPLATE.md",
    ".claude/agents/templates/workflows/Create_Stories_Workflow_template.md",
    ".claude/agents/templates/workflows/Plan_Sprint_Workflow_template.md",
    ".claude/agents/templates/workflows/Refine_Sprint_Workflow_template.md",
    ".claude/agents/templates/workflows/Resume_Story_Workflow_template.md",
    ".claude/agents/templates/workflows/Shared_Pipeline_Stages_template.md",
    ".claude/agents/templates/workflows/Sprint_Workflow_template.md",
    ".claude/agents/templates/workflows/Start_Story_Workflow_template.md",
}

# Templates that predate changes.json tracking (added before v0.0.1).
# Their absence from changes.json is a historical gap, not an error.
# Backlog item: add a v0.0.0 baseline entry to changes.json covering these files.
ALLOWLIST_UNTRACKED_TEMPLATES = {
    ".claude/agents/templates/context/Document_Index_template.md",
    ".claude/agents/templates/context/Project_Priming_template.md",
    ".claude/agents/templates/instructions/business_analyst_instructions_template.md",
    ".claude/agents/templates/instructions/developer_instructions_template.md",
    ".claude/agents/templates/instructions/qa_instructions_template.md",
    ".claude/agents/templates/instructions/technical_lead_instructions_template.md",
    ".claude/agents/templates/rules/Agent_Common_template.md",
    ".claude/agents/templates/rules/Blocked_Request_template.md",
    ".claude/agents/templates/rules/Business_Analyst_Rules_template.md",
    ".claude/agents/templates/rules/CICD_Validation_Guide_template.md",
    ".claude/agents/templates/rules/Clean_Code_Rules_template.md",
    ".claude/agents/templates/rules/Story_Standard_Dev_template.md",
    ".claude/agents/templates/rules/Story_Standard_PO_template.md",
    ".claude/agents/templates/rules/Story_Standard_QA_template.md",
    ".claude/agents/templates/rules/Story_Standard_template.md",
    ".claude/agents/templates/rules/Strict_Mode_Story_Guide_template.md",
    ".claude/agents/templates/workflows/Workflow_Guide_template.md",
}

# ---------------------------------------------------------------------------
# Invariant #1A: file-path reference resolution config
# ---------------------------------------------------------------------------

# Runtime-generated paths: created by agents at runtime, not present in the
# devkit repo. Skip file-existence checks for paths under these prefixes.
RUNTIME_PATH_PREFIXES = (
    ".claude/agents/tmp/",
    ".claude/agents/docs/",
    ".claude/agents/retros/",
)

# Known-wrong references in the current corpus, tracked for fix in the
# refactor-templates sprint. Printed as [KNOWN_ISSUE] and do NOT exit non-zero.
KNOWN_ISSUE_REFS = {
    ".claude/agents/rules/Blocked_Request_Template.md",
    # Should be .claude/agents/rules/Blocked_Request.md (capital-T typo).
    # Appears in Resume_Story_Workflow_Shared_template.md and
    # Shared_Pipeline_Stages_Shared_template.md. Tracked for refactor-templates.
}

# ---------------------------------------------------------------------------
# Invariant #1B: section-ref alias table
# ---------------------------------------------------------------------------

# Maps the short name (stem of a .md filename) that appears in "Name.md §N"
# references to the template file path (relative to REPO_ROOT) where heading N
# is checked. Names NOT in this table are skipped -- prevents false positives.
SECTION_REF_ALIAS = {
    "Agent_Common": ".claude/agents/templates/rules/Agent_Common_template.md",
    "Business_Analyst_Rules": ".claude/agents/templates/rules/Business_Analyst_Rules_template.md",
    "Developer_Rules": ".claude/agents/templates/rules/Developer_Rules_template.md",
    "Product_Owner_Rules": ".claude/agents/templates/rules/Product_Owner_Rules_template.md",
    "Project_Priming": ".claude/agents/templates/context/Project_Priming_template.md",
    "QA_Rules": ".claude/agents/templates/rules/QA_Rules_template.md",
    "Retro_Rules": ".claude/agents/templates/rules/Retro_Rules_template.md",
    "Story_Standard": ".claude/agents/templates/rules/Story_Standard_template.md",
    "Story_Standard_Dev": ".claude/agents/templates/rules/Story_Standard_Dev_template.md",
    "Story_Standard_PO": ".claude/agents/templates/rules/Story_Standard_PO_template.md",
    "Story_Standard_QA": ".claude/agents/templates/rules/Story_Standard_QA_template.md",
    "Story_Standard_TL": ".claude/agents/templates/rules/Story_Standard_TL_template.md",
    "Technical_Lead_Rules": ".claude/agents/templates/rules/Technical_Lead_Rules_template.md",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Regex for a fenced-code block opening line (``` or ~~~, optional lang tag).
_FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})")


def parse_fenced_regions(lines: list) -> list:
    """
    Return a boolean list: True at index i means line i is inside a fenced block.
    Opening and closing fence lines themselves are marked True.
    """
    in_fence = False
    fence_marker = ""
    inside = []
    for line in lines:
        m = _FENCE_OPEN.match(line)
        if not in_fence and m:
            in_fence = True
            fence_marker = m.group(1)[0] * len(m.group(1))
            inside.append(True)
        elif in_fence and line.startswith(fence_marker):
            inside.append(True)
            in_fence = False
            fence_marker = ""
        else:
            inside.append(in_fence)
    return inside


def rel(path) -> str:
    """Return path relative to REPO_ROOT for display, using forward slashes."""
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def emit(findings: list, kind: str, path, lineno: int, msg: str) -> None:
    findings.append((kind, path, lineno, msg))


# ---------------------------------------------------------------------------
# Invariant #1A: file-path reference integrity
# ---------------------------------------------------------------------------

# Match .claude/agents/... .md path candidates in text.
_FILEREF_RE = re.compile(r"\.claude/agents/[\w./ -]+\.md")

# Tokens that mark a candidate as an example/placeholder (discard these).
_DISCARD_CHARS = frozenset("<>*{}XXXXX")
_DISCARD_SUBS = ("ST-XXXXXX",)


def _should_discard_ref(cand: str) -> bool:
    if any(c in cand for c in _DISCARD_CHARS):
        return True
    for sub in _DISCARD_SUBS:
        if sub in cand:
            return True
    return False


def _resolve_file_ref(cand: str) -> bool:
    """True if the candidate path resolves under any of the 3 resolution roots."""
    # Root 1: verbatim from repo root.
    if (REPO_ROOT / cand).exists():
        return True
    # Root 2: devkit working mirror (.claude/agents/<rest> -> working/<rest>).
    if cand.startswith(".claude/agents/"):
        rest = cand[len(".claude/agents/"):]
        if (REPO_ROOT / ".claude/agents/working" / rest).exists():
            return True
    # Root 3: template source -- map any .md basename to <stem>_template.md.
    if cand.endswith(".md"):
        stem = Path(cand).stem  # e.g. "Agent_Common" from "Agent_Common.md"
        template_name = f"{stem}_template.md"
        template_root = REPO_ROOT / ".claude/agents/templates"
        for candidate_tpl in template_root.rglob(template_name):
            if candidate_tpl.exists():
                return True
    return False


def check_reference_integrity(path, lines: list, fenced: list,
                               findings: list) -> None:
    """Invariant #1A: every .claude/agents/...md path reference resolves."""
    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        for cand in _FILEREF_RE.findall(line):
            if _should_discard_ref(cand):
                continue
            # Skip runtime-generated paths (created at agent runtime, not in repo).
            if any(cand.startswith(p) for p in RUNTIME_PATH_PREFIXES):
                continue
            if cand in KNOWN_ISSUE_REFS:
                emit(findings, "KNOWN_ISSUE", path, i + 1,
                     f"unresolved reference (known typo, tracked for refactor-templates): '{cand}'")
                continue
            if not _resolve_file_ref(cand):
                emit(findings, "ERROR", path, i + 1,
                     f"unresolved reference '{cand}'")


# ---------------------------------------------------------------------------
# Invariant #1B: section reference integrity
# ---------------------------------------------------------------------------

# Match optional "Name.md <sep>" or "Name <sep>" before §N.
# Separator after .md may include non-alphanumeric chars (e.g. backtick+space).
# Group 1 = path/name prefix before .md, Group 2 = bare word prefix, Group 3 = §N.
_SECREF_RE = re.compile(
    r"(?:([\w./][\w./_-]*?)\.md[^\w\d§\n]+|(\b\w[\w_]*)\s+)?§(\d+)"
)

# Heading pattern: "## N." or "## N " (not "## 5.1" sub-section notation).
_HEADING_NUM_RE = re.compile(r"^#{1,6}\s+(\d+)\.?\s+")


def _get_file_headings(rel_path: str) -> set:
    """
    Return the set of numeric section numbers (N from '## N. Title') in the file.
    Only counts headings like '## 1.' or '## 2 ' -- NOT sub-section '### 5.1'.
    Returns empty set if file cannot be read.
    """
    fp = REPO_ROOT / rel_path
    if not fp.exists():
        return set()
    nums = set()
    for line in fp.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _HEADING_NUM_RE.match(line)
        if m:
            # Reject sub-section numbering like "5.1" by checking the char
            # immediately after the matched number is NOT another digit.
            raw = line[m.end(1):]  # text after the digit group
            if raw and raw[0].isdigit():
                continue  # e.g. "5.1" -- skip
            nums.add(int(m.group(1)))
    return nums


def _extract_alias_stem(raw: str) -> str:
    """
    From a raw name token that appeared before §N (may be a path like
    '.claude/agents/rules/Agent_Common'), return the stem (e.g. 'Agent_Common').
    """
    return Path(raw).name  # last component of the path, no extension


def check_section_refs(path, lines: list, fenced: list,
                        findings: list) -> None:
    """Invariant #1B: §N references resolve to real headings."""
    # Build the set of numbered headings in the current file (for bare §N).
    current_headings = _get_file_headings(rel(path))
    # Only validate bare §N references if this file uses numbered-section style.
    has_numbered_sections = bool(current_headings)

    # Cache for aliased files.
    alias_headings_cache: dict = {}

    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        for m in _SECREF_RE.finditer(line):
            path_prefix = m.group(1)   # e.g. ".claude/agents/rules/Agent_Common"
            name_prefix = m.group(2)   # e.g. "Agent_Common"
            section_num = int(m.group(3))

            raw_name = path_prefix or name_prefix

            if raw_name is None:
                # Bare §N -- only check if this file uses numbered-section style.
                if not has_numbered_sections:
                    continue
                if section_num not in current_headings:
                    emit(findings, "ERROR", path, i + 1,
                         f"bare §{section_num} has no matching numbered heading in this file")
                continue

            # Qualified §N -- look up alias by stem.
            stem = _extract_alias_stem(raw_name)
            if stem not in SECTION_REF_ALIAS:
                continue  # Not in alias table -- skip (prevents false positives).

            alias_path = SECTION_REF_ALIAS[stem]
            if alias_path not in alias_headings_cache:
                alias_headings_cache[alias_path] = _get_file_headings(alias_path)
            headings = alias_headings_cache[alias_path]

            if not headings:
                emit(findings, "ERROR", path, i + 1,
                     f"section-ref alias '{stem}' file not found or unreadable: '{alias_path}'")
            elif section_num not in headings:
                emit(findings, "ERROR", path, i + 1,
                     f"'{stem}' has no §{section_num} (file has sections: {sorted(headings)})")


# ---------------------------------------------------------------------------
# Invariant #2: placeholder well-formedness
# ---------------------------------------------------------------------------

def check_placeholders(path, lines: list, fenced: list,
                        findings: list) -> None:
    """Invariant #2: {{PLACEHOLDER}} and uppercase single-brace {TOKEN} checks."""
    for i, line in enumerate(lines):
        if fenced[i]:
            continue

        # 2a. Unbalanced double-braces on the line.
        opens = line.count("{{")
        closes = line.count("}}")
        if opens != closes:
            emit(findings, "ERROR", path, i + 1,
                 f"unbalanced placeholder braces: {opens} '{{{{' vs {closes} '}}}}'")
            continue  # Cannot reliably parse further tokens on this line.

        # 2c. Triple-brace run.
        if "{{{" in line or "}}}" in line:
            emit(findings, "ERROR", path, i + 1,
                 "triple-brace run '{{{' or '}}}' found")
            continue

        # Extract and validate {{...}} tokens.
        for token_match in re.finditer(r"\{\{([^}]*)\}\}", line):
            inner = token_match.group(1)

            # 2b. Malformed inner token (must be [A-Z][A-Z0-9_]*).
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", inner):
                emit(findings, "ERROR", path, i + 1,
                     f"malformed placeholder inner token: '{{{{ {inner} }}}}'")
                continue

            # 2d. Well-formed but not in the registry.
            if inner not in KNOWN_DOUBLE_BRACE_TOKENS:
                emit(findings, "ERROR", path, i + 1,
                     f"unknown placeholder '{{{{{inner}}}}}' (add to KNOWN_DOUBLE_BRACE_TOKENS if legitimate)")

        # 2e. Single-brace all-caps {TOKEN} not in allowlist.
        # Strip double-brace tokens first to avoid re-matching their inner braces.
        stripped = re.sub(r"\{\{[^}]*\}\}", "", line)
        for sb_match in re.finditer(r"\{([A-Z][A-Z0-9_]+)\}", stripped):
            token = sb_match.group(1)
            if token not in KNOWN_SINGLE_BRACE_TOKENS:
                emit(findings, "ERROR", path, i + 1,
                     f"possibly-malformed all-caps single-brace placeholder '{{{token}}}' "
                     f"(add to KNOWN_SINGLE_BRACE_TOKENS if legitimate)")


# ---------------------------------------------------------------------------
# Invariant #3: shared-block include integrity
# ---------------------------------------------------------------------------

_SHARED_START = re.compile(r"<!--\s*SHARED-START\s*-->")
_SHARED_END = re.compile(r"<!--\s*SHARED-END\s*-->")
_SHARED_LOGIC = re.compile(r"<!--\s*Shared logic:\s*(.+?)\s*-->")
_INCLUDED_BY = re.compile(r"<!--\s*Included by:\s*(.+?)\s*-->")

TEMPLATES_DIR = REPO_ROOT / ".claude/agents/templates"


def _is_shared(path) -> bool:
    """True if the file lives under a directory named 'shared' (templates or test fixtures)."""
    return "shared" in path.parts


def _is_thin_variant(path) -> bool:
    """True if the file lives under a directory named 'github' or 'strict'."""
    return any(p in ("github", "strict") for p in path.parts)


def check_shared_integrity(path, lines: list, fenced: list,
                            findings: list) -> None:
    """Invariant #3: shared-block include integrity."""

    # 3a. Balanced SHARED-START / SHARED-END markers (shared files only).
    if _is_shared(path):
        stack = 0
        for i, line in enumerate(lines):
            if _SHARED_START.search(line):
                if stack > 0:
                    emit(findings, "ERROR", path, i + 1,
                         "nested SHARED-START (previous block not closed)")
                stack += 1
            elif _SHARED_END.search(line):
                if stack == 0:
                    emit(findings, "ERROR", path, i + 1,
                         "unbalanced/mis-ordered SHARED marker: SHARED-END without open SHARED-START")
                else:
                    stack -= 1
        if stack != 0:
            emit(findings, "ERROR", path, len(lines),
                 f"unbalanced SHARED marker: {stack} SHARED-START(s) without SHARED-END")

    # 3b. Shared-logic pointer resolves (thin variant files).
    if _is_thin_variant(path):
        for i, line in enumerate(lines):
            m = _SHARED_LOGIC.search(line)
            if m:
                pointer = m.group(1).strip()
                target = REPO_ROOT / ".claude/agents" / pointer
                if not target.exists():
                    emit(findings, "ERROR", path, i + 1,
                         f"Shared logic pointer '{pointer}' does not exist")

    # 3c. Bidirectional consistency (shared files: Included-by header check).
    if _is_shared(path):
        included_by: list = []
        for line in lines:
            m = _INCLUDED_BY.search(line)
            if m:
                for entry in m.group(1).split(","):
                    entry = entry.strip()
                    if entry:
                        included_by.append(entry)

        for ref_path in included_by:
            target = REPO_ROOT / ".claude/agents" / ref_path
            if not target.exists():
                emit(findings, "ERROR", path, 1,
                     f"Included-by/Shared-logic mismatch: listed file '{ref_path}' does not exist")
                continue
            target_text = target.read_text(encoding="utf-8", errors="replace")
            # The pointer in the thin file references the shared file relative to
            # .claude/agents/ -- compute that relative path.
            shared_rel = rel(path)
            if shared_rel.startswith(".claude/agents/"):
                shared_rel = shared_rel[len(".claude/agents/"):]
            if shared_rel not in target_text:
                emit(findings, "ERROR", path, 1,
                     f"Included-by/Shared-logic mismatch: '{ref_path}' has no "
                     f"Shared logic pointer back to '{shared_rel}'")

    # 3c (converse). Thin variant must appear in referenced shared file's Included-by.
    if _is_thin_variant(path):
        for i, line in enumerate(lines):
            m = _SHARED_LOGIC.search(line)
            if m:
                pointer = m.group(1).strip()
                shared_path = REPO_ROOT / ".claude/agents" / pointer
                if not shared_path.exists():
                    continue  # Already flagged in 3b.
                shared_text = shared_path.read_text(encoding="utf-8", errors="replace")
                thin_rel = rel(path)
                if thin_rel.startswith(".claude/agents/"):
                    thin_rel = thin_rel[len(".claude/agents/"):]
                if thin_rel not in shared_text:
                    emit(findings, "ERROR", path, i + 1,
                         f"Included-by/Shared-logic mismatch: this file ('{thin_rel}') "
                         f"not listed in Included-by of '{pointer}'")

    # 3d. Thin variant must not contain SHARED-START / SHARED-END.
    if _is_thin_variant(path):
        for i, line in enumerate(lines):
            if _SHARED_START.search(line) or _SHARED_END.search(line):
                emit(findings, "ERROR", path, i + 1,
                     "SHARED block inlined in thin variant (github/**|strict/**)")


# ---------------------------------------------------------------------------
# Invariant #4: retired-trigger check
# ---------------------------------------------------------------------------

def check_retired_triggers(path, lines: list, fenced: list,
                            findings: list) -> None:
    """Invariant #4: no occurrences of strings on the retired-triggers list."""
    if not RETIRED_TRIGGERS:
        return
    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        for trigger in RETIRED_TRIGGERS:
            if trigger in line:
                emit(findings, "ERROR", path, i + 1,
                     f"retired trigger '{trigger}'")


# ---------------------------------------------------------------------------
# Invariant #5: changes.json manifest integrity
# ---------------------------------------------------------------------------

def check_manifest_integrity(findings: list) -> None:
    """Invariant #5: changes.json path existence and template coverage."""
    if not CHANGES_JSON.exists():
        emit(findings, "ERROR", CHANGES_JSON, 0, "changes.json not found")
        return

    try:
        with CHANGES_JSON.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        emit(findings, "ERROR", CHANGES_JSON, 0, f"changes.json parse error: {exc}")
        return

    # Verify every version key is a valid semver string (no ordering check --
    # the file uses newest-first (descending) convention which is intentional).
    for version_key in data:
        try:
            parts = [int(x) for x in version_key.split(".")]
            if len(parts) != 3:
                raise ValueError("not 3 components")
        except ValueError:
            emit(findings, "ERROR", CHANGES_JSON, 0,
                 f"version key '{version_key}' is not valid semver (expected N.N.N)")

    # Collect all paths listed and check existence.
    all_listed: set = set()
    for entry in data.values():
        if not isinstance(entry, dict):
            continue  # Skip legacy list-format entries (pre-v0.0.7).
        for key in ("new", "modified"):
            for listed_path in entry.get(key, []):
                all_listed.add(listed_path)
                if listed_path in ALLOWLIST_REMOVED_PATHS:
                    continue
                if not (REPO_ROOT / listed_path).exists():
                    emit(findings, "ERROR", CHANGES_JSON, 0,
                         f"listed path '{listed_path}' missing from disk")

    # Check every template file appears in at least one changes.json entry.
    templates_dir = REPO_ROOT / ".claude/agents/templates"
    for tpl in sorted(templates_dir.rglob("*.md")):
        tpl_rel = rel(tpl)
        if tpl_rel not in all_listed and tpl_rel not in ALLOWLIST_UNTRACKED_TEMPLATES:
            emit(findings, "ERROR", CHANGES_JSON, 0,
                 f"template '{tpl_rel}' not referenced by any changes.json entry "
                 f"(add to ALLOWLIST_UNTRACKED_TEMPLATES or to changes.json if newly added)")


# ---------------------------------------------------------------------------
# Invariant #6: Markdown well-formedness
# ---------------------------------------------------------------------------

def check_markdown_wellformedness(path, lines: list, fenced: list,
                                   findings: list) -> None:
    """Invariant #6: heading continuity, balanced fences, table pipe-counts."""

    # 6b. Balanced code fences -- track unclosed open fences.
    unclosed_fences: list = []
    in_fence = False
    fence_marker = ""
    for i, line in enumerate(lines):
        m = _FENCE_OPEN.match(line)
        if not in_fence and m:
            in_fence = True
            fence_marker = m.group(1)[0] * len(m.group(1))
            unclosed_fences.append(i + 1)
        elif in_fence and line.startswith(fence_marker):
            in_fence = False
            fence_marker = ""
            if unclosed_fences:
                unclosed_fences.pop()

    if unclosed_fences:
        emit(findings, "ERROR", path, unclosed_fences[-1],
             "unbalanced code fence (opened here, not closed)")

    # 6a. Heading-level continuity (skip headings inside fenced regions).
    prev_level = None
    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            level = len(m.group(1))
            if prev_level is not None and level > prev_level + 1:
                emit(findings, "ERROR", path, i + 1,
                     f"heading level jumps from {prev_level} to {level}")
            prev_level = level

    # 6c. Table pipe-count consistency.
    _check_table_pipes(path, lines, fenced, findings)


_PIPE_RE = re.compile(r"(?<!\\)\|")  # unescaped pipe


def _count_pipes(line: str) -> int:
    """Count unescaped pipes, stripping inline code spans to avoid pipe-in-code."""
    cleaned = re.sub(r"`[^`]*`", lambda m: " " * len(m.group()), line)
    return len(_PIPE_RE.findall(cleaned))


def _check_table_pipes(path, lines: list, fenced: list,
                        findings: list) -> None:
    """Check that table rows have the same pipe count as the header row."""
    i = 0
    while i < len(lines):
        if fenced[i]:
            i += 1
            continue
        line = lines[i].rstrip()
        # Detect header row: contains at least 2 unescaped pipes.
        if _count_pipes(line) >= 2:
            header_pipes = _count_pipes(line)
            j = i + 1
            # Skip separator row (|---|---|  style).
            if j < len(lines) and re.match(r"^\s*\|[\s|:=-]+\|?\s*$", lines[j]):
                j += 1
            # Validate data rows until a non-table line.
            while j < len(lines):
                row = lines[j].rstrip()
                if not row or "|" not in row or fenced[j]:
                    break
                row_pipes = _count_pipes(row)
                if row_pipes != header_pipes:
                    emit(findings, "ERROR", path, j + 1,
                         f"table row has {row_pipes} pipe(s), header has {header_pipes}")
                j += 1
            i = j
            continue
        i += 1


# ---------------------------------------------------------------------------
# Main scan loop
# ---------------------------------------------------------------------------

def scan_file(path, findings: list) -> None:
    """Run all per-file invariants on a single .md file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        emit(findings, "ERROR", path, 0, f"cannot read file: {exc}")
        return

    lines = text.splitlines()
    fenced = parse_fenced_regions(lines)

    check_reference_integrity(path, lines, fenced, findings)
    check_section_refs(path, lines, fenced, findings)
    check_placeholders(path, lines, fenced, findings)
    check_shared_integrity(path, lines, fenced, findings)
    check_retired_triggers(path, lines, fenced, findings)
    check_markdown_wellformedness(path, lines, fenced, findings)


def main() -> int:
    # Parse arguments.
    # --test-retired-trigger <token>  adds a one-off retired trigger for fixture testing.
    args = sys.argv[1:]
    scan_targets_raw = []
    i = 0
    while i < len(args):
        if args[i] == "--test-retired-trigger" and i + 1 < len(args):
            RETIRED_TRIGGERS.append(args[i + 1])
            i += 2
        else:
            scan_targets_raw.append(args[i])
            i += 1

    if scan_targets_raw:
        scan_targets = [Path(a) for a in scan_targets_raw]
    else:
        scan_targets = SCAN_DIRS

    findings: list = []

    # Per-file invariants.
    for scan_dir in scan_targets:
        if not scan_dir.exists():
            print(f"[WARN] scan target not found: {scan_dir}", file=sys.stderr)
            continue
        if scan_dir.is_file():
            scan_file(scan_dir, findings)
        else:
            for md_path in sorted(scan_dir.rglob("*.md")):
                scan_file(md_path, findings)

    # Global invariant (changes.json).
    check_manifest_integrity(findings)

    # Report findings.
    errors = 0
    for kind, path, lineno, msg in findings:
        loc = f"{rel(path)}:{lineno}" if lineno else rel(path)
        print(f"[{kind}] {loc} -- {msg}")
        if kind == "ERROR":
            errors += 1

    if errors == 0 and not findings:
        print("OK -- all Layer-1 invariants passed")
    elif errors == 0:
        known = sum(1 for k, *_ in findings if k == "KNOWN_ISSUE")
        print(f"OK -- all hard invariants passed ({known} known-issue note(s))")
    else:
        print(f"\n{errors} violation(s) found", file=sys.stderr)

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
