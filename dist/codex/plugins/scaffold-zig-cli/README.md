# Scaffold Zig CLI

Scaffold a complete Zig CLI project with build.zig, build.zig.zon, cross-compiled releases, GitHub Actions CI/CD, and Makefile.

**Type:** Command
**Trigger:** `/scaffold-zig-cli`
**Requires:** Zig 0.16 or later, and `gh` to resolve the GitHub owner

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Generates the full boilerplate for a new Zig CLI project: `build.zig`, `build.zig.zon`, `src/root.zig`, `src/main.zig`, `typos.toml`, `Makefile`, `.gitignore`, `.editorconfig`, CI and release workflows, `LICENSE`, `README`, `CHANGELOG`, seeded Claude Code permissions, and directory stubs.

The project is split into a library module (`src/root.zig`) and a CLI module (`src/main.zig`), so the logic stays testable without a process around it and downstream packages can depend on it directly.

Four details exist because each one has a recorded failure behind it, repeated across four Zig repositories:

- **The compiler emits the fingerprint.** `build.zig.zon` is written without a `.fingerprint` field, the first `zig build` prints the value to use, and the skill writes it back. Guessing the value, or copying one from another project, is the single most common way to stall a new Zig repository.
- **`minimum_zig_version` is always written.** CI resolves the toolchain by reading `build.zig.zon`, so a manifest without it leaves CI with nothing to install. The version is detected from the local toolchain and normalized, so a development build does not become the pin.
- **`.claude/settings.json` is seeded.** `Bash(zig build*)`, `Bash(zig fmt*)` and `Bash(zig version)` go into the tracked allowlist, because every contributor runs them and an empty allowlist means every build prompts.
- **`make check` is a real target.** One command runs the format check, the build and the tests, instead of a hand-spelled `zig fmt --check ... && zig build && zig build test` that comes out differently every time.

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
    "allow": ["Bash(git init*)", "Bash(git add *)", "Bash(git commit *)", "Bash(git config *)", "Bash(gh api user*)", "Bash(zig build*)", "Bash(zig fmt*)", "Bash(zig version)"]
  }
}
```

The skill also writes the three `zig` rules into the scaffolded project's own `.claude/settings.json`, so a project created this way does not need them added by hand.

## See Also

- [Scaffold New Repo](../scaffold-new-repo/README.md): language-agnostic repo boilerplate (included automatically)
- [Set-Up CI](../set-up-ci/README.md): the same Zig CI workflow for a project that already exists
- [Set-Up Installers](../set-up-installers/README.md): set up Homebrew formula and shell install script after scaffolding
- [Add Scrut CLI Tests](../add-scrut-cli-tests/README.md): snapshot tests for the generated binary
- [All plugins](../../../../README.md)
