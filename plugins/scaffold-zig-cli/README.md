# Scaffold Zig CLI

Scaffold a complete Zig CLI project with build.zig, build.zig.zon, cross-compiled releases, GitHub Actions CI/CD, and Makefile.

**Type:** Command
**Trigger:** `/scaffold-zig-cli`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Generates the full boilerplate for a new Zig CLI project: `build.zig`, `build.zig.zon`, `src/root.zig`, `src/main.zig`, `typos.toml`, `Makefile`, `.gitignore`, `.editorconfig`, CI and release workflows, `LICENSE`, `README`, `CHANGELOG`, seeded Claude Code permissions, and directory stubs.

The project is split into a library module (`src/root.zig`) and a CLI module (`src/main.zig`), so the logic stays testable without a process around it and downstream packages can depend on it directly.

Four details exist because each one has a recorded failure behind it, repeated across four Zig repositories:

- **The compiler emits the fingerprint.** `build.zig.zon` is written without a `.fingerprint` field, the first `zig build` prints the value to use, and the skill writes it back. Guessing the value, or copying one from another project, is the single most common way to stall a new Zig repository.
- **`minimum_zig_version` is always written.** CI resolves the toolchain by reading `build.zig.zon`, so a manifest without it leaves CI with nothing to install. The version is taken from the local toolchain exactly as printed, development snapshots included, because `mlugg/setup-zig` installs precisely that value and a truncated one names a release that does not exist.
- **`.claude/settings.json` is seeded.** `Bash(zig build*)`, `Bash(zig fmt*)` and `Bash(zig version)` go into the tracked allowlist, because every contributor runs them and an empty allowlist means every build prompts.
- **`make check` is a real target.** One command runs the format check, the build and the tests, instead of a hand-spelled `zig fmt --check ... && zig build && zig build test` that comes out differently every time.

## Requirements

- **Zig 0.16 or later.** The templates use `std.Io` and the `std.process.Init` form of `main`, neither of which exists in 0.15. Install from [ziglang.org/download](https://ziglang.org/download/) rather than Homebrew, whose `zig` formula floats to the next minor release on upgrade.
- **`gh`**, authenticated, to resolve the GitHub owner for repository URLs and the Homebrew tap. The skill does not create a repository on GitHub.
- **Git commit signing**, configured and working. The initial commit is `git commit -S`, and the skill reports the failure rather than retrying without `-S`, because dropping the signature is the user's decision and not a fallback it should take. Either an OpenPGP key or `gpg.format=ssh` with a `user.signingkey` satisfies it, and `user.name` and `user.email` must be set in the target repository.

Without signing configured, every file is still generated and the run stops short of the initial commit, leaving the project uncommitted rather than committed unsigned.

## Usage

```text
/scaffold-zig-cli
```

The command prompts for project name and description during setup.

## Examples

- "scaffold zig cli": starts the interactive scaffolding process
- "new zig cli": same behavior
- "start a zig cli project": same behavior

## Recommended Permissions

This skill runs git, GitHub CLI, and Zig commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git init*)", "Bash(git rev-parse *)", "Bash(git check-ignore *)", "Bash(git add *)", "Bash(git commit *)", "Bash(git config *)", "Bash(git status*)", "Bash(gh api user*)", "Bash(gh api \"repos/*)", "Bash(gh release view*)", "Bash(zig build*)", "Bash(zig fmt*)", "Bash(zig version)", "Bash(cd *)", "Bash(test -L *)", "Bash(readlink *)", "Bash(find *)", "Bash(pwd*)", "Bash(date +%Y)", "Bash(echo *)", "Bash(ls -d *)", "Bash(mkdir -p*)", "Bash(touch *)"]
  }
}
```

This covers every command the workflow runs, not only the Zig ones: `cd`, `test -L`, `readlink`, `find`, `pwd` and `ls -d` for the step 3 target selection, symlink checks and overwrite preflight, `git rev-parse` for the step 4 repository-root test, `git check-ignore` for the step 23 ignore probe, `echo` for the SHA-refresh output, `date +%Y` for the LICENSE year, `gh release view` and `gh api` for the `cboone/gh-actions` SHA refresh, and `mkdir -p` plus `touch` for the directory stubs.

The escaped quote in `Bash(gh api \"repos/*)` is deliberate. Permission rules match the command text before the shell expands it, and the SHA-refresh step runs `gh api "repos/cboone/gh-actions/commits/${TAG}"` with the endpoint quoted, because it interpolates a variable. A rule written as `Bash(gh api repos/*)` expects `r` where the command has `"`, so it does not match and the step prompts anyway.

The skill also writes the three `zig` rules into the scaffolded project's own `.claude/settings.json`, so a project created this way does not need them added by hand.

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): language-agnostic repo boilerplate, including `AGENTS.md`, `CLAUDE.md` and `.github/copilot-instructions.md`, none of which this skill generates. Run it separately and **run it first**: it writes its own `LICENSE`, `README.md` and `CHANGELOG.md`, and a `.claude/settings.json` with an empty allowlist, so running it afterwards overwrites the Zig-specific versions and drops the seeded `zig build` and `zig fmt` permissions
- [Set-Up CI](../set-up-ci/README.md): the same Zig CI workflow for a project that already exists
- [Set-Up Installers](../set-up-installers/README.md): set up Homebrew formula and shell install script after scaffolding
- [Add Scrut CLI Tests](../add-scrut-cli-tests/README.md): snapshot tests for the generated binary
- [All plugins](../../README.md)
