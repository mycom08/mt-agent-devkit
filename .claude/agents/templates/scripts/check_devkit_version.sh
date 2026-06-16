#!/usr/bin/env bash

VERSION_FILE=".claude/agents/devkit_version.txt"
[ -f "$VERSION_FILE" ] || exit 0
CURRENT=$(tr -d '[:space:]' < "$VERSION_FILE")

[ -f "CLAUDE.md" ] || exit 0
SOURCE_URL=$(grep -oP '(?<=\*\*Devkit source:\*\* )https?://\S+' CLAUDE.md 2>/dev/null | head -1)
[ -n "${SOURCE_URL:-}" ] || exit 0
SOURCE_URL="${SOURCE_URL%/}"

LATEST=$(curl -sf --max-time 5 "$SOURCE_URL/version.txt" 2>/dev/null | tr -d '[:space:]') || exit 0
[ -n "$LATEST" ] || exit 0

if [ "$CURRENT" != "$LATEST" ]; then
    printf '{"systemMessage": "Devkit update available: v%s -> v%s. Run '\''sync devkit'\'' to update."}\n' "$CURRENT" "$LATEST"
fi
