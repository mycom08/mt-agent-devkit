#!/usr/bin/env bash
# read_sections.sh
#
# Fetch two or more sections from a single Markdown harness file (a rules,
# instructions, or context file that uses the repo's flat "## N." / "## Na."
# heading convention, plus the "## Version" footer) in one call — so a
# spawned agent doesn't pay one read-section invocation (and one file open)
# per section when a task needs more than one from the same file.
#
# Usage:
#   read_sections.sh <file> <marker> <marker> [<marker> ...]
#
# Each <marker> is a section number exactly as it appears in a "§N" / "§Na"
# citation (e.g. "5", "11a", "Version" for the "## Version" footer). Requires
# a file and at least two markers — for a single section, use the
# `read-section` skill directly.
#
# A marker that does not match any heading in <file> is reported on stderr;
# the script still prints every section that DID match rather than aborting
# the whole call.
#
# Exit status: 0 if every marker matched, 1 if at least one marker did not
# (matched sections are still printed to stdout either way), 2 for usage /
# file errors.

set -uo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $(basename "$0") <file> <marker> <marker> [<marker> ...]" >&2
  echo "Requires a file path and at least two section markers (e.g. 5, 11a, Version)." >&2
  exit 2
fi

file="$1"
shift

if [ ! -f "$file" ]; then
  echo "ERROR: file not found: $file" >&2
  exit 2
fi

exit_code=0

for marker in "$@"; do
  if [ "$marker" = "Version" ]; then
    heading_re='^## Version'
  else
    # Doubled backslash: awk's -v assignment applies one round of C-style
    # escape processing to the value, same as a string literal in the awk
    # program text — a single "\." here would warn and collapse to a plain
    # ".", turning the heading's period into an any-char wildcard.
    heading_re="^## ${marker}\\\\."
  fi

  section=$(awk -v heading_re="$heading_re" '
    /^## ([0-9]+[a-zA-Z]?\.|Version)/ {
      if (in_target) { exit }
      in_target = ($0 ~ heading_re) ? 1 : 0
    }
    in_target { print }
  ' "$file")

  if [ -z "$section" ]; then
    echo "=== §${marker}: NOT FOUND in ${file} ===" >&2
    exit_code=1
    continue
  fi

  echo "===== §${marker} ====="
  printf '%s\n' "$section"
  echo "===== end §${marker} ====="
  echo
done

exit "$exit_code"
