#!/usr/bin/env bash
# Extract one heading-delimited section from a Markdown file by line number,
# without reading the whole file. See ../SKILL.md for how to build the two
# regexes from a citation.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: read_section.sh <file> <marker-regex> <target-regex>

  marker-regex  Matches every heading in the citation family, e.g.
                '^## ([0-9]+[a-z]?\.|Version)' for a numbered §N/§Na
                citation, or '^### Fact ' for a memory archive's "Fact N"
                family. Must match the whole family, never just the
                target's own shape (see SKILL.md).
  target-regex  Matches the single heading line to extract, e.g.
                '^## 11b\.' or '^### Fact 2\b'.

Prints the target heading through to the line before the next heading in
marker-regex's family, or to end of file if the target is the last one.
EOF
  exit 1
}

[ $# -eq 3 ] || usage

file=$1
marker=$2
target=$3

[ -f "$file" ] || { echo "read_section: file not found: $file" >&2; exit 1; }

match_count=0
start=""
end=""
want_end=0

while IFS=: read -r lineno content; do
  if [ "$want_end" -eq 1 ]; then
    end="$lineno"
    want_end=0
  fi
  if printf '%s\n' "$content" | grep -qE "$target"; then
    match_count=$((match_count + 1))
    if [ "$match_count" -eq 1 ]; then
      start="$lineno"
      want_end=1
    fi
  fi
done < <(grep -nE "$marker" "$file")

if [ "$match_count" -eq 0 ]; then
  echo "read_section: no heading in '$file' matched target-regex: $target" >&2
  exit 1
fi

if [ "$match_count" -gt 1 ]; then
  echo "read_section: target-regex matched $match_count headings in '$file', expected exactly 1: $target" >&2
  exit 1
fi

if [ -n "$end" ]; then
  sed -n "${start},$((end - 1))p" "$file"
else
  sed -n "${start},\$p" "$file"
fi
