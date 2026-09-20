---
applyTo: "plugins/**/*.md,tests/**/*.md,dist/**/*.md"
---

# Tmpfile pattern review instructions

Temporary paths in this repository target `${TMPDIR:-/tmp}` rather than a literal `/tmp`, because the macOS Bash sandbox denies `/private/tmp` and the per-user directory `mktemp` picks by default. `plugins/use-git/skills/use-git/references/tmpfile-pattern.md` is the canonical description. These specific shapes are correct and have been checked, so they are not defects:

- **`mktemp -u "${TMPDIR:-/tmp}/<prefix>-XXXXXX"` is the intended form**, for files, as is `mktemp -d "${TMPDIR:-/tmp}/<prefix>-XXXXXX"` for directories. A file already written this way needs no further change; do not report it as an unresolved gap. Within this pattern, a bare `mktemp`, a bare `mktemp -d`, a `mktemp -ut <prefix>`, or a literal `/tmp/...` template is a finding, because each of those selects a directory the sandbox denies.
- **Plain `mktemp` stays correct for security-sensitive temporary files**, and is not a finding. The canonical reference deliberately keeps it for content written through a shell redirect rather than the Write tool, because `-u` does not atomically reserve the name and both man pages call it unsafe. The general shell style references in `write-bash-scripts` and `write-zsh-scripts` recommend plain `mktemp` for exactly that reason, and a table contrasting `tmp=$(mktemp)` with a predictable `/tmp/...` path is showing the safe form beside the unsafe one. Leave all of those alone. The rule above governs the non-secret pattern only: a body passed to a command's file flag, or a scrut test's working directory.
- **The `:-/tmp` fallback is deliberate.** A bare `${TMPDIR}` resolves to an empty string on a shell that leaves it unset and writes at the filesystem root. macOS usually sets `$TMPDIR` with a trailing slash, so the expansion can produce a doubled slash mid-path, which every POSIX filesystem treats as one separator.
- **`-u` is required for the file form**, even though both man pages call it unsafe in general. Plain `mktemp` creates the file, and the Write tool refuses to overwrite a file it has not read first. The trade-off is scoped to non-secret bodies such as pull request, issue and release text.
- **An example path such as `/tmp/claude-501/gh-pr-body-x4y5z6` is illustrative output**, showing what `mktemp` prints under the sandbox. It is not a hardcoded path and is not a finding.

## Permission rule asymmetry

The two allow-rule forms in each plugin README differ on purpose, and neither should be reported as inconsistent with the other:

- **`mktemp` rules quote the expression**, as in `"Bash(mktemp -u \"${TMPDIR:-/tmp}/gh-pr-body-*\")"`. That command really is run with `${TMPDIR:-/tmp}` intact in its text, so the rule matches it literally.
- **`rm -f` rules key on the filename prefix**, as in `"Bash(rm -f *gh-pr-body-*)"`. By cleanup time the skills have substituted the placeholder with the literal path `mktemp` printed, so the command carries an expanded path and a rule written against the expression can never match it. Pinning the cleanup rule to a directory does not work either, because `$TMPDIR` is `/tmp/claude-501/` under the sandbox and something like `/var/folders/xx/.../T/` outside it. The filename prefix is the part that holds constant.

Inner quotes inside these JSON strings must stay escaped (`\"`), since the blocks are meant to be copied into `settings.json`.
