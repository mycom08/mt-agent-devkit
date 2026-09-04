#!/usr/bin/env bash

VERSION_FILE="{{AGENT_DIR_PREFIX}}/agents/devkit_version.txt"
[ -f "$VERSION_FILE" ] || exit 0
CURRENT=$(tr -d '[:space:]' < "$VERSION_FILE")

[ -f "{{ROOT_FILE}}" ] || exit 0
SOURCE_URL=$(grep -oP '(?<=\*\*Devkit source:\*\* )https?://\S+' {{ROOT_FILE}} 2>/dev/null | head -1)
[ -n "${SOURCE_URL:-}" ] || exit 0
SOURCE_URL="${SOURCE_URL%/}"
SOURCE_URL="${SOURCE_URL%.git}"

# Tolerate an older install whose field still holds a raw base URL
# (https://raw.githubusercontent.com/{owner}/{repo}/<ref>) — reduce it to the
# canonical repository URL so the tag lookup below still resolves. The next
# `sync devkit` rewrites the field itself.
case "$SOURCE_URL" in
    https://raw.githubusercontent.com/*)
        owner_repo=$(printf '%s' "${SOURCE_URL#https://raw.githubusercontent.com/}" | cut -d/ -f1,2)
        SOURCE_URL="https://github.com/${owner_repo}"
        ;;
esac

# Latest release = highest tag matching vX.Y.Z. git ls-remote needs no credentials
# on a public repo and has no rate limit, unlike the GitHub REST API (60/hour per
# IP unauthenticated) — a rate-limited call would suppress update notices silently.
# The ^v[0-9]+\.[0-9]+\.[0-9]+$ filter is required: -v:refname sorts a bare v7-style
# tag above v7.0.0, so an unfiltered head -1 can return a non-release tag.
LATEST_TAG=$(GIT_TERMINAL_PROMPT=0 git ls-remote --tags --refs --sort=-v:refname "${SOURCE_URL}.git" 2>/dev/null \
    | sed 's#.*refs/tags/##' \
    | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' \
    | head -1)
[ -n "${LATEST_TAG:-}" ] || exit 0
LATEST="${LATEST_TAG#v}"

if [ "$CURRENT" != "$LATEST" ]; then
    printf '{"systemMessage": "Devkit update available: v%s -> v%s. Run '\''sync devkit'\'' to update."}\n' "$CURRENT" "$LATEST"
fi
