# Supported Guides

Each entry names a style guide, how to detect the files it covers, the routing globs written into the entry `SKILL.md`, and the bundled checklist installed as `.github/skills/code-review/<guide>.md`. Detection runs over `git ls-files` after the exclusions in step 2 of the workflow.

A file can match more than one guide. The Lean checklist includes mirrored test-library conventions where the project uses them. A routing bullet lists the concrete globs, followed by the exclusions that apply to it.

## Shebang Rule

An extensionless file is a script of the language its first line names. Read the interpreter from `#!/usr/bin/env NAME`, `#!/usr/bin/env -S NAME ...` or `#!/path/to/NAME`, ignoring trailing flags. The shebang overrides the file extension.

- `bash` selects `write-bash-scripts`.
- `zsh` selects `write-zsh-scripts`.
- `sh`, `dash` and `ksh` match no guide. Report those files as unsupported rather than applying the Bash checklist, which would push Bash-only syntax into POSIX scripts.

When either shell guide is installed, the entry skill's reporting rules include the line telling reviewers that a script without a file extension follows its shebang, so scripts added later are routed too.

## write-go-code

- **Detect**: A tracked `go.mod`.
- **Route**: `**/*.go`.
- **Checklist**: `./references/checklists/write-go-code.md`

## write-lean-code

- **Detect**: A tracked `lakefile.toml`, `lakefile.lean` or `lean-toolchain`, or any tracked `*.lean` file.
- **Route**: `**/*.lean`.
- **Checklist**: `./references/checklists/write-lean-code.md`

## write-bash-scripts

- **Detect**: Tracked `*.sh` or `*.bash` files, and any other tracked file whose shebang names Bash, whether or not it has an extension.
- **Route**: `**/*.sh` and `**/*.bash`, plus every other Bash script by path, or a directory glob such as `bin/*` when every file in the directory is a Bash script. A `*.sh` or `*.bash` file that the exclusion below removes is named in the exclusions of this guide's routing bullet, so the glob does not carry it.
- **Exclude**: Files whose shebang names another shell, including a `*.sh` or `*.bash` file that does.
- **Checklist**: `./references/checklists/write-bash-scripts.md`

### Embedded Bash

Select `write-bash-scripts` even when the repository's only Bash is embedded. Inspect tracked `.github/workflows/*.yml` and `.github/workflows/*.yaml` for `run:` steps. Resolve the effective shell from step `shell`, job and workflow `defaults.run.shell`, then runner and container defaults. Explicit Bash and implicit Bash on non-Windows runners qualify; default container `sh`, Windows PowerShell, explicit non-Bash shells and unresolved dynamic shells do not. Report unsupported or unresolved shells rather than guessing.

Inspect tracked Makefiles and included makefiles for recipes whose effective `SHELL` selects Bash, including target-specific settings or an explicit Bash invocation. Default POSIX `sh` recipes do not qualify. Tracked git hooks follow the shebang rule regardless of their directory; do not read untracked `.git/hooks` or live hooks selected by local configuration.

For embedded Bash, add the concrete containing paths or workflow globs to the Bash routing bullet with the qualifier "Bash content only, not the surrounding YAML or Make syntax". Keep these separate from standalone-script globs and their exclusions, so an exclusion such as `**/*.yml` for standalone scripts cannot exclude the embedded content. An installation with only embedded Bash still installs and routes the Bash checklist.

Fill EMBEDDED-SHELL in all three templates whenever Bash is selected, including when only standalone Bash exists today. In `REVIEW.md`, put it before the copied Important rules so those rules have the same content boundary as the entry skill.

## write-zsh-scripts

- **Detect**: Tracked `*.zsh`, `*.plugin.zsh` or `*.zsh-theme` files; zsh startup files (`.zshrc`, `.zshenv`, `.zprofile`, `.zlogin`, `.zlogout`, with or without the leading dot); files whose first line is `#compdef` or `#autoload`; and any other tracked file whose shebang names zsh, whether or not it has an extension.
- **Route**: `**/*.zsh` and `**/*.zsh-theme`, plus each startup file, completion function and other zsh script by path, or a directory glob when every file in the directory is zsh. A `*.zsh` file that the exclusion below removes is named in the exclusions of this guide's routing bullet.
- **Exclude**: Files whose shebang names another shell, including a `*.zsh` file that does.
- **Checklist**: `./references/checklists/write-zsh-scripts.md`

## write-scrut-tests

- **Detect**: A tracked `tests/scrut/` directory, or tracked Markdown files containing a code fence whose info string starts with `scrut`.
- **Route**: `tests/scrut/**/*.md`, plus each other Markdown file with a scrut fence by path.
- **Checklist**: `./references/checklists/write-scrut-tests.md`

## write-markdown

- **Detect**: Any tracked `*.md` file that is neither a scrut test file nor Pandoc-academic Markdown.
- **Route**: `**/*.md`, followed by its exclusions.
- **Exclude**: Scrut test files, which the scrut checklist covers, and Pandoc-academic Markdown, which the Markdown checklist would misjudge. Treat a project as Pandoc-academic when it has `references/papers/`, `references/extractions/` or `references/transcriptions/`, or `papers/**/main.md` beside `papers/shared/templates/*.latex`; exclude those trees. Also exclude individual files with `bibliography:` or `csl:` in their frontmatter, `[@key]` citations in prose, or raw `{=latex}` blocks. A citation shown inside inline code or a code block, such as documentation of the citation syntax, is not a signal. Report the excluded Pandoc files as waiting on a Pandoc checklist.
- **Checklist**: `./references/checklists/write-markdown.md`
