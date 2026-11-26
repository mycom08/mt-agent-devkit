<!-- Shared logic: templates/shared/orchestrator_instructions_shared_template.md -->

<!-- GitHub-mode Orchestrator Instructions: the shared file plus the section below. -->

## Project Repository (GitHub mode)

Installed `gh` commands name no repository, so `gh` must resolve to this project's own: the one on the remote the base branch tracks (`git config branch.<base>.remote`, else `origin`; `<base>` is the branch stories start from, usually `main`).

At every workflow start, before the first `gh` command:

1. Take the URL from `git remote get-url <remote>` for the remote above and read `OWNER/REPO` from it (drop a trailing `.git`). If that remote is missing or is not on GitHub, stop and ask the user which repository is the project's.
2. Run `gh repo set-default --view`. It exits 0 even when no default is set, so judge by its standard output.
3. If it prints a repository, compare it with that `OWNER/REPO`, ignoring letter case. When they match, continue. When they differ, `gh` would act on another repository: stop, show the user both names and ask which is the project's. Never overwrite the default without that answer.
4. If it prints nothing and only one remote in `git remote -v` points to GitHub, continue.
5. If it prints nothing and there are several, run `gh repo set-default <URL>` (pass `OWNER/REPO` if `gh` rejects the URL), then confirm that `--view` prints that repository.

The guard writes only `.git/config`; no installed file changes.
