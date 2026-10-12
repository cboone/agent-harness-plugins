# Verification

Local verification turns a Needs testing PR into Safe to merge or Needs work on evidence. It runs the repository's own checks against what the default branch would look like after the merge, next to a control run on the default branch as it is.

Run it in a detached worktree under a temporary directory. Never in the user's working tree, and never on a branch that would be pushed.

Each command runs in a fresh shell, so no variable survives from one to the next, and neither does a working directory. Run `mktemp -d "${TMPDIR:-/tmp}/dependabot-verify-XXXXXX"` twice, note the two paths it prints, and write them literally where the commands below say `PR_DIR` and `CONTROL_DIR`. `DEFAULT` is the PR's base branch. Every install, check, and build command after step 1 names its worktree in the same command, `cd PR_DIR/pr && COMMAND` or `cd CONTROL_DIR/control && COMMAND`: a bare `npm ci` or `make test` runs in the user's checkout.

Running tests executes the new version's code, and skipping install scripts does not sandbox that. Verify on a machine whose environment holds no production or publishing credentials.

## 1. Build the would-be merge result

The PR head is already in `refs/dependabot-triage/N` from step 3 of the skill.

```bash
git worktree add --detach PR_DIR/pr refs/dependabot-triage/N
git -C PR_DIR/pr merge --no-commit --no-ff origin/DEFAULT
```

`--no-commit` leaves the merged tree in place without creating a commit, so nothing needs signing and nothing can be pushed by accident. A conflict at the merge step is itself the answer: the PR is Needs refresh. Abort with `git -C PR_DIR/pr merge --abort` and stop verifying it.

For the control run, a second worktree on `origin/DEFAULT`:

```bash
git worktree add --detach CONTROL_DIR/control origin/DEFAULT
```

## 2. Install without changing the lockfile

A verification that rewrites the lockfile is testing a different change from the one in the PR. Use the frozen install for the repository's package manager, skipping install scripts where the package manager allows it, in each worktree:

```bash
cd PR_DIR/pr && npm ci --ignore-scripts
cd CONTROL_DIR/control && npm ci --ignore-scripts
```

The table gives the install for each package manager:

| Package manager | Install                                           |
| --------------- | ------------------------------------------------- |
| npm             | `npm ci --ignore-scripts`                         |
| Yarn Berry      | `yarn install --immutable --mode=skip-build`      |
| Yarn classic    | `yarn install --frozen-lockfile --ignore-scripts` |
| pnpm            | `pnpm install --frozen-lockfile --ignore-scripts` |
| uv              | `uv sync --locked`                                |
| Go              | `go mod download` (then `go build ./...`)         |
| Cargo           | `cargo fetch --locked`                            |
| Bundler         | `BUNDLE_FROZEN=true bundle install`               |

An install that fails with the frozen lockfile is Needs work: the lockfile and manifest the PR produced do not agree.

When a project genuinely needs its install scripts to build, run with scripts enabled only after reading what they do in the new version.

## 3. Run the repository's own checks

Read the repository's `AGENTS.md`, `CLAUDE.md`, `Makefile`, and `package.json` scripts to find the commands CI runs, and run those in both worktrees, each prefixed with `cd PR_DIR/pr &&` or `cd CONTROL_DIR/control &&`:

- `make test`, `make lint`, `make build`, or the repository's equivalents
- the test runner the workflow calls (`go test ./...`, `cargo test --locked`, `uv run pytest`, `yarn test`)
- the build for anything that ships (a site, a binary, a container image)

Compare the two runs. A failure in both is pre-existing and says nothing about the PR. A failure only in the PR worktree is caused by the update.

## 4. Guard against a vacuous pass

A clean run proves something only if the check could have failed:

- **Linters and formatters**: plant a violation in a scratch copy of a file the tool covers and confirm the PR worktree's tool reports it. A tool version that ignores a file type, or a config the new version no longer reads, passes everything.
- **Counts**: compare how many files the tool checked in the control and PR runs. A drop means the new version or its config is skipping files.
- **Tool versions**: confirm the command ran the version the PR installs (`npx NAME --version`, `yarn NAME --version`), not a globally installed one.

## 5. Ecosystem-specific checks

- **GitHub Actions**: local runs cannot execute a workflow faithfully. Verify by reading instead: the release notes, `runs.using`, changed inputs and outputs, and trigger restrictions (see `./evidence.md`). For a repository that publishes actions or reusable workflows, grep the consumers the user names for the changed inputs.
- **Runtime dependencies CI does not exercise**: start the application in the PR worktree and exercise the affected path, or name the staging check the user should run. A server, proxy, or middleware upgrade is a behavior change even when every unit test passes.
- **Containers**: build the image in the PR worktree and run its smoke command.

## 6. Clean up

```bash
rm -rf PR_DIR CONTROL_DIR
git worktree prune
```

The triage refs themselves are removed in the skill's wrap-up step.

Deleting the temporary directories and pruning avoids forcing `git worktree remove` past the untracked files the install created. Both directories came from `mktemp -d` in this verification, so nothing else lives in them.

## 7. Record the result

In the report, each verified PR states what ran, in which worktree, and the outcome, for example: "`yarn install --immutable` and `yarn lint` pass in the PR worktree and the control; planted MD001 violation reported." That line is the deciding evidence for its new category.
