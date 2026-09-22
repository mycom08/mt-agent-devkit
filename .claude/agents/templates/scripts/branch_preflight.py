#!/usr/bin/env python3
"""Verify a story base branch before creating a story branch.

The helper deliberately performs no repair.  ``inspect`` reports a bounded
PASS/BLOCKED result; ``create`` repeats the checks immediately before creating
the branch from the recorded full SHA.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


MAX_PATHS = 20
MAX_COMMITS = 3
MAX_EVIDENCE_CHARS = 160
RUNTIME_PREFIXES = (
    ".antigravity/agents/memory/",
    ".antigravity/agents/working-record/",
    ".antigravity/agents/retros/",
    ".antigravity/agents/tmp/",
    ".antigravity/agents/internal/",
    ".claude/agents/memory/",
    ".claude/agents/working-record/",
    ".claude/agents/retros/",
    ".claude/agents/tmp/",
    ".claude/agents/internal/",
)


class PreflightError(RuntimeError):
    pass


def git(*args: str, check: bool = True) -> bytes:
    completed = subprocess.run(("git", *args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and completed.returncode:
        detail = display(completed.stderr).strip() or "git command failed"
        raise PreflightError(detail)
    return completed.stdout


def nul_items(value: bytes) -> list[bytes]:
    return [item for item in value.split(b"\0") if item]


def display(value: bytes | str) -> str:
    """Render untrusted Git text on one bounded, control-character-safe line."""
    if isinstance(value, bytes):
        value = value.decode("utf-8", "surrogateescape")
    return "".join(
        char if ord(char) >= 32 and char != "\x7f" else f"\\x{ord(char):02x}"
        for char in value
    ).replace("\n", "\\x0a").replace("\r", "\\x0d")


def decoded(value: bytes) -> str:
    """Decode trusted Git control output before parsing it."""
    return value.decode("utf-8", "surrogateescape").strip()


def is_runtime_path(path: bytes) -> bool:
    return any(path.startswith(prefix.encode()) for prefix in RUNTIME_PREFIXES)


def current_branch() -> str | None:
    value = git("symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    return decoded(value) if value else None


def status_paths() -> list[bytes]:
    # The v1 -z format gives a fixed two-byte status, then a path.  Renames
    # include a second NUL-delimited path; both are evidence worth reporting.
    entries = nul_items(git("status", "--porcelain=v1", "-z", "--untracked-files=all"))
    paths: list[bytes] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        paths.append(entry[3:] if len(entry) >= 3 else entry)
        # Porcelain v1 -z reverses rename/copy path order: new path first,
        # followed by old path without a status prefix. Keep both intact.
        if len(entry) >= 2 and (entry[:1] in (b"R", b"C") or entry[1:2] in (b"R", b"C")) and index + 1 < len(entries):
            index += 1
            paths.append(entries[index])
        index += 1
    return paths


def upstream_for(base: str) -> tuple[str, str] | None:
    remote = decoded(git("config", "--get", f"branch.{base}.remote", check=False))
    merge = decoded(git("config", "--get", f"branch.{base}.merge", check=False))
    if not remote or not merge.startswith("refs/heads/"):
        return None
    return remote, merge.removeprefix("refs/heads/")


def ref_sha(ref: str) -> str | None:
    value = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", check=False)
    return decoded(value) or None


def bounded_commits(revision: str) -> list[str]:
    raw = git("log", "-z", "--format=%h%x1f%s", f"-n{MAX_COMMITS}", revision, check=False)
    return [display(item).replace("\x1f", " ") for item in nul_items(raw)]


@dataclass
class Result:
    mode: str
    base: str
    base_sha: str | None = None
    remote_sha: str | None = None
    worktree: str = "clean"
    ahead_behind: str = "unavailable"
    unpushed: str = "unavailable"
    agent_state: str = "no"
    story_branch: str = "not-created"
    reason: str = ""
    evidence: list[str] | None = None

    def block(self, reason: str, evidence: list[str] | None = None) -> "Result":
        self.reason = reason
        self.evidence = evidence or []
        return self

    @property
    def passed(self) -> bool:
        return not self.reason

    def render(self) -> str:
        lines = [
            f"Preflight: {'PASS' if self.passed else 'BLOCKED'}",
            f"Mode: {self.mode}",
            f"Base branch: {self.base or 'unavailable'}",
            f"Base SHA: {self.base_sha or 'unavailable'}",
            f"Remote base SHA: {self.remote_sha or 'unavailable'}",
            f"Worktree: {self.worktree}",
            f"Ahead/behind: {self.ahead_behind}",
            f"Unpushed commits: {self.unpushed}",
            f"Agent-state commits detected: {self.agent_state}",
            f"Story branch: {self.story_branch}",
            f"Reason: {self.reason}",
        ]
        lines.extend(
            f"Evidence: {display(item)[:MAX_EVIDENCE_CHARS]}"
            for item in (self.evidence or [])[:MAX_PATHS]
        )
        return "\n".join(lines)


def inspect(mode: str, base: str, story_branch: str) -> Result:
    result = Result(mode=mode, base=base)
    if not base or any(char.isspace() or ord(char) < 32 for char in base):
        return result.block("explicit base selection required")
    dirty = status_paths()
    if dirty:
        result.worktree = "dirty"
        return result.block("worktree contains user changes", [display(path) for path in dirty[:MAX_PATHS]])
    branch = current_branch()
    if branch != base:
        return result.block("declared base is not the checked-out branch")
    result.base_sha = ref_sha("HEAD")
    if not result.base_sha:
        return result.block("checked-out base has no commit")
    remote_ref: str | None = None
    if mode == "github":
        upstream = upstream_for(base)
        if not upstream:
            return result.block("declared base has no configured upstream")
        remote, remote_branch = upstream
        fetched = subprocess.run(
            ("git", "fetch", "--no-tags", remote, f"refs/heads/{remote_branch}:refs/remotes/{remote}/{remote_branch}"),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if fetched.returncode:
            return result.block("fetch of declared upstream failed", [display(fetched.stderr).strip()])
        remote_ref = f"refs/remotes/{remote}/{remote_branch}"
        result.remote_sha = ref_sha(remote_ref)
        if not result.remote_sha:
            return result.block("declared upstream ref is unavailable")
        counts = decoded(git("rev-list", "--left-right", "--count", f"HEAD...{remote_ref}")).split()
        if len(counts) != 2:
            return result.block("cannot determine ahead/behind state")
        ahead, behind = counts
        result.ahead_behind = f"{ahead}/{behind}"
        result.unpushed = ahead
        ahead_agent = False
        if ahead != "0":
            ahead_messages = git("log", "--format=%B%x00", f"{remote_ref}..HEAD", check=False)
            ahead_agent = any(display(message).startswith("Agent:") for message in nul_items(ahead_messages))
            ahead_paths = nul_items(git("diff", "--name-only", "-z", f"{remote_ref}..HEAD", check=False))
            ahead_agent = ahead_agent or any(is_runtime_path(path) for path in ahead_paths)
            if ahead_agent:
                result.agent_state = "yes"
        if behind != "0" and ahead != "0":
            return result.block("base diverges from upstream")
        if behind != "0":
            return result.block("base is behind upstream")
        if ahead != "0":
            return result.block("base is ahead of upstream", bounded_commits(f"{remote_ref}..HEAD"))
    tree_paths = nul_items(git("ls-tree", "-rz", "--name-only", "-r", result.base_sha))
    contaminated = [display(path) for path in tree_paths if is_runtime_path(path)]
    message = display(git("log", "-1", "--format=%B", result.base_sha))
    if contaminated or message.startswith("Agent:"):
        result.agent_state = "yes"
        evidence = contaminated[:MAX_PATHS]
        if message.startswith("Agent:"):
            evidence.append(message[:160])
        return result.block("verified base contains agent runtime state", evidence)
    if ref_sha(f"refs/heads/{story_branch}") or (mode == "github" and remote_ref and ref_sha(f"refs/remotes/{upstream_for(base)[0]}/{story_branch}")):
        return result.block("story branch already exists")
    return result


def create(mode: str, base: str, story_branch: str, expected_sha: str, expected_remote_sha: str | None) -> Result:
    # Re-run the whole inspection so a worktree/ref change between calls cannot
    # turn a previously-valid result into a branch creation race.
    result = inspect(mode, base, story_branch)
    if not result.passed:
        return result
    if result.base_sha != expected_sha or (mode == "github" and result.remote_sha != expected_remote_sha):
        return result.block("verified base changed since inspection")
    created = subprocess.run(("git", "switch", "-c", story_branch, expected_sha), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if created.returncode:
        return result.block("story branch creation failed", [display(created.stderr).strip()])
    if current_branch() != story_branch or ref_sha("HEAD") != expected_sha:
        return result.block("story branch verification failed")
    result.story_branch = story_branch
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("inspect", "create"))
    parser.add_argument("--mode", required=True, choices=("github", "strict"))
    parser.add_argument("--base", required=True)
    parser.add_argument("--story-branch", required=True)
    parser.add_argument("--expected-base-sha")
    parser.add_argument("--expected-remote-sha")
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            result = inspect(args.mode, args.base, args.story_branch)
        else:
            if not args.expected_base_sha:
                raise PreflightError("create requires --expected-base-sha")
            result = create(args.mode, args.base, args.story_branch, args.expected_base_sha, args.expected_remote_sha)
    except PreflightError as exc:
        result = Result(args.mode, args.base).block(display(str(exc)))
    print(result.render())
    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
