# Check Zsh Scripts

Check and evaluate zsh scripts using multiple static analysis, syntax checking, and formatting tools.

**Type:** Skill
**Trigger:** `/check-zsh-scripts` (also activates automatically)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Check Zsh Scripts** from the available plugins.

## What It Does

Runs seven complementary tools against zsh scripts in a recommended order: syntax checking (`zsh -n`), compilation (`zcompile`), static analysis (`shellcheck`), bashism detection (`checkbashisms`), safety suggestions (`shellharden`), variable scope warnings (`setopt warn_create_global warn_nested_var`), and formatting (`shfmt`). Reports findings with false-positive filtering for tools that have limited zsh support. Offers auto-formatting via shfmt where applicable.

## Requirements

- [`shellcheck`](https://www.shellcheck.net/). Install via Homebrew: `brew install shellcheck`
- [`shfmt`](https://github.com/mvdan/sh). Install via Homebrew: `brew install shfmt`
- [`shellharden`](https://github.com/anordal/shellharden). Install via Homebrew: `brew install shellharden` (or `cargo install --locked --version 4.3.1 shellharden`)
- [`checkbashisms`](https://packages.debian.org/devscripts). Install via Homebrew: `brew install devscripts`
- `zsh` and `zcompile` are typically pre-installed on macOS and most Linux distributions.

## Usage

Invoke manually with `/check-zsh-scripts`, or the skill activates automatically when working with zsh files (`.zsh`, `.zshrc`, `.zshenv`, `.zprofile`, `.zlogin`, `.zlogout`).

## Recommended Permissions

This skill runs shell commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(zsh -n *)", "Bash(zsh -c *)", "Bash(shellcheck *)", "Bash(checkbashisms *)", "Bash(shfmt *)", "Bash(shellharden *)", "Bash(rm -f *.zwc)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

## Examples

- "Check my zsh scripts"
- "Lint the zshrc file"
- "Validate this zsh code"
- "Run zsh checks on these files"
- Editing a `.zsh` file (auto-activates)

## See Also

- [Write Bash Scripts](../write-bash-scripts/README.md): Bash style conventions
- [Lint and Fix](../lint-and-fix/README.md): General linter and formatter runner
- [All plugins](../../../../README.md)
