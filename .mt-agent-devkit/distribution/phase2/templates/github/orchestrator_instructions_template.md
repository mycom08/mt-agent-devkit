<!-- Shared logic: templates/shared/orchestrator_instructions_shared_template.md -->

<!-- GitHub-mode Orchestrator Instructions: the shared file plus the section below. -->

## Project Repository (GitHub mode)

Installed `gh` commands name no repository, so `gh` must resolve to this project's own: the one on the remote the base branch tracks (`git config branch.<base>.remote`, else `origin`; `<base>` is the branch stories start from, usually `main`).

At every workflow start, before the first `gh` command:

1. If only one remote in `git remote -v` points to GitHub, there is nothing to do.
2. Otherwise run `gh repo set-default --view`. It exits 0 even when no default is set, so judge by its standard output: a repository name there is the project's explicit choice and stays.
3. If the output is empty, run `gh repo set-default <URL>` with the URL from `git remote get-url <remote>` for the remote above (pass `OWNER/REPO` from that URL if `gh` rejects it). Then confirm that `--view` prints that repository.
4. If that remote is missing or is not on GitHub, stop and ask the user which repository is the project's.

This writes only `.git/config`; no installed file changes.
