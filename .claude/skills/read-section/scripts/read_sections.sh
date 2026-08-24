#!/usr/bin/env bash
# Fetches several named sections from one Markdown file in a single call, so a spawned
# agent doesn't pay one skill invocation (and one file open) per section when a task
# needs more than one from the same file.
#
# Section markers follow the flat numbering convention used across
# `.claude/agents/working/{rules,instructions,context}/`: every citable section is a
# `##`-level heading, numbered either bare ("## 5. Working Record") or lettered
# ("## 11a. Roadmap Story Drain") — `###` is reserved for unnumbered prose and is never
# a citation target. Boundary detection below always scans the whole numbered family
# (`^## ([0-9]+[a-z]*\.|Version)`), never just the requested marker's own shape —
# narrowing to one marker's shape (e.g. only "### " for a lettered marker) reproduces
# the over-/under-read bug the flat convention exists to avoid: a file with exactly one
# lettered sub-heading would return a single boundary hit and read straight to EOF.
#
# Usage: read_sections.sh <file> <marker> [<marker> ...]
#   <marker>: a section number, optionally lettered — "5", "11a", "15b" (no "##"/"§").
#
# Prints each matched section, delimited by a "===== ## <marker> =====" header line.
# An unmatched marker is reported to stderr and does not abort the run — every other
# requested marker that does match is still printed. Exit status is 1 if any marker
# was invalid or went unmatched, 0 if every marker matched.
#
# No dependency beyond bash/grep/sed — same tool class the repo's other shell scripts
# already use.
set -euo pipefail

FILE="${1:?usage: read_sections.sh <file> <marker> [<marker> ...]}"
shift

if [[ $# -lt 1 ]]; then
  echo "error: at least one section marker is required" >&2
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "error: file not found: $FILE" >&2
  exit 1
fi

# Every heading boundary in the numbered family, line-numbered, in file order. One scan,
# reused for every requested marker below — this is what makes the multi-section case
# cheaper than N separate single-section reads.
mapfile -t BOUNDARIES < <(grep -nE '^## ([0-9]+[a-z]*\.|Version)' "$FILE")

if [[ ${#BOUNDARIES[@]} -eq 0 ]]; then
  echo "error: no numbered '## N.' / '## Na.' sections found in ${FILE}" >&2
  exit 1
fi

exit_status=0

for marker in "$@"; do
  if [[ ! "$marker" =~ ^[0-9]+[a-z]*$ ]]; then
    echo "error: marker '${marker}' is not a valid section number (expected e.g. '5' or '11a')" >&2
    exit_status=1
    continue
  fi

  start=""
  end=""
  for i in "${!BOUNDARIES[@]}"; do
    entry="${BOUNDARIES[$i]}"
    lineno="${entry%%:*}"
    text="${entry#*:}"
    if [[ "$text" =~ ^##\ ${marker}\.[[:space:]] ]]; then
      start="$lineno"
      if [[ $((i + 1)) -lt ${#BOUNDARIES[@]} ]]; then
        next_entry="${BOUNDARIES[$((i + 1))]}"
        end="${next_entry%%:*}"
      fi
      break
    fi
  done

  if [[ -z "$start" ]]; then
    echo "error: section marker '${marker}' not found in ${FILE}" >&2
    exit_status=1
    continue
  fi

  echo "===== ## ${marker} ====="
  if [[ -n "$end" ]]; then
    sed -n "${start},$((end - 1))p" "$FILE"
  else
    sed -n "${start},\$p" "$FILE"
  fi
  echo
done

exit "$exit_status"
