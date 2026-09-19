# Supported Guides

Each entry names a style guide, how to detect the files it covers, the routing globs written into the entry `SKILL.md`, and the bundled checklist installed as `.github/skills/code-review/<guide>.md`. Detection runs over `git ls-files` after the exclusions in step 2 of the workflow.

A file can match more than one guide: Lean test modules get both Lean checklists. A routing bullet lists the concrete globs, followed by the exclusions that apply to it.

## Shebang Rule

An extensionless file is a script of the language its first line names. Read the interpreter from `#!/usr/bin/env NAME`, `#!/usr/bin/env -S NAME ...` or `#!/path/to/NAME`, ignoring trailing flags. The shebang overrides the file extension.

- `bash` selects `write-bash-scripts`.
- `zsh` selects `write-zsh-scripts`.
- `sh`, `dash` and `ksh` match no guide. Report those files as unsupported rather than applying the Bash checklist, which would push Bash-only syntax into POSIX scripts.

When either shell guide is installed, the entry skill's reporting rules include the line telling reviewers that an extensionless script follows its shebang, so scripts added later are routed too.

## write-go-code

- **Detect**: A tracked `go.mod`.
- **Route**: `**/*.go`.
- **Checklist**: `./references/checklists/write-go-code.md`

## write-lean-code

- **Detect**: A tracked `lakefile.toml`, `lakefile.lean` or `lean-toolchain`, or any tracked `*.lean` file.
- **Route**: `**/*.lean`.
- **Checklist**: `./references/checklists/write-lean-code.md`

## write-lean-tests

- **Detect**: A Lean project whose lakefile names a test library, either through `testDriver = "NAMETest"` or a `lean_lib` whose name ends in `Test`, and a tracked directory with that name at any depth.
- **Route**: The test directory's `**/*.lean` files and the test library's root module, for example `ShannonTest/**/*.lean` and `ShannonTest.lean`. Library changes that add, rename or remove exported declarations are also in scope, which the checklist states itself.
- **Checklist**: `./references/checklists/write-lean-tests.md`

## write-bash-scripts

- **Detect**: Tracked `*.sh` or `*.bash` files, or extensionless files with a Bash shebang.
- **Route**: `**/*.sh` and `**/*.bash`, plus each extensionless Bash script by path, or a directory glob such as `bin/*` when every file in the directory is a Bash script.
- **Exclude**: Files whose shebang names another shell.
- **Checklist**: `./references/checklists/write-bash-scripts.md`

## write-zsh-scripts

- **Detect**: Tracked `*.zsh`, `*.plugin.zsh` or `*.zsh-theme` files; zsh startup files (`.zshrc`, `.zshenv`, `.zprofile`, `.zlogin`, `.zlogout`, with or without the leading dot); files whose first line is `#compdef` or `#autoload`; or extensionless files with a zsh shebang.
- **Route**: `**/*.zsh` and `**/*.zsh-theme`, plus each startup file, completion function and extensionless zsh script by path, or a directory glob when every file in the directory is zsh.
- **Checklist**: `./references/checklists/write-zsh-scripts.md`

## write-scrut-tests

- **Detect**: A tracked `tests/scrut/` directory, or tracked Markdown files containing a code fence whose info string starts with `scrut`.
- **Route**: `tests/scrut/**/*.md`, plus each other Markdown file with a scrut fence by path.
- **Checklist**: `./references/checklists/write-scrut-tests.md`

## write-markdown

- **Detect**: Any tracked `*.md` file that is neither a scrut test file nor Pandoc-academic Markdown.
- **Route**: `**/*.md`, followed by its exclusions.
- **Exclude**: Scrut test files, which the scrut checklist covers, and Pandoc-academic Markdown, which the Markdown checklist would misjudge. Treat a project as Pandoc-academic when it has `references/papers/`, `references/extractions/` or `references/transcriptions/`, or `papers/**/main.md` beside `papers/shared/templates/*.latex`; exclude those trees. Also exclude individual files with `bibliography:` or `csl:` in their frontmatter, `[@key]` citations, or raw `{=latex}` blocks. Report the excluded Pandoc files as waiting on a Pandoc checklist.
- **Checklist**: `./references/checklists/write-markdown.md`
