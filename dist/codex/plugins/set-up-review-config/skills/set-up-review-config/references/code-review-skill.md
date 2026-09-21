# Code Review Skill Templates

Templates for the files written under `.github/skills/code-review/` in the target repository. Uppercase words are placeholders.

## Entry Skill

Write this file when `.github/skills/code-review/SKILL.md` does not exist. When it exists, write only the part from the BEGIN line through the END line.

```markdown
---
name: code-review
description: Style checklists for reviewing this repository's pull requests. Use for every pull request review to match each changed file to its checklist and report findings with the severities defined here.
---

# Code Review

<!-- BEGIN set-up-review-config -->

Apply the checklist that matches each changed file, and apply it only to the lines the pull request changes.

## Checklists

ROUTING

## Reporting

- Start each finding with the checklist name and the rule name, for example CITATION-EXAMPLE.
- Rules under a checklist's Important heading block merging. Report each one you find.
- Rules under a checklist's Nits heading are minor. Report at most five per review, and give the number of any others in the summary.
- Follow each checklist's Do not flag section.
- Do not report what these CI checks already report: CI-CHECKS.
- Do not review these paths: SKIP-PATHS.
SHEBANG-LINE
- Rules outside this block, in this file, `.github/copilot-instructions.md`, `AGENTS.md` or `REVIEW.md`, take precedence over it.

<!-- END set-up-review-config -->
```

The description stays the same for every repository, so a rerun never rewrites the frontmatter.

## Placeholders

- **ROUTING**: One bullet per installed checklist, in the order of `./references/guides.md`:

  ```markdown
  - FILE-TYPE files (GLOBS): `GUIDE.md`. Full guide: [GUIDE style guide](https://github.com/cboone/agent-harness-plugins/blob/PIN/plugins/GUIDE/skills/GUIDE/SKILL.md).
  ```

  GLOBS is a comma-separated list of backticked globs and paths, followed by "except" and the backticked exclusions when the guide has any. PIN is the pinned commit, or `main` for an `unpinned` install. For example:

  ```markdown
  - Go files (`**/*.go`): `write-go-code.md`. Full guide: [write-go-code style guide](https://github.com/cboone/agent-harness-plugins/blob/136cf5554b3a35e4908ffa131ddf09b2b400601e/plugins/write-go-code/skills/write-go-code/SKILL.md).
  - Markdown files (`**/*.md`, except `tests/scrut/**/*.md`): `write-markdown.md`. Full guide: [write-markdown style guide](https://github.com/cboone/agent-harness-plugins/blob/136cf5554b3a35e4908ffa131ddf09b2b400601e/plugins/write-markdown/skills/write-markdown/SKILL.md).
  ```

- **CITATION-EXAMPLE**: A backticked citation that names a checklist this installation routes, so the example never sends a reviewer to a checklist the repository does not have. Build it from the first installed checklist in the order of `./references/guides.md` and the first rule name under that checklist's `## Important` heading. An installation routing only the Bash, scrut and Markdown checklists gets `write-bash-scripts: Strict mode`. The same value fills this placeholder in `./references/agents-md-section.md` and `./references/review-md.md`, so all three files cite the same rule.
- **CI-CHECKS**: The checks from step 3, backticked and comma-separated, such as `gofmt`, `golangci-lint`. When CI runs none, replace the whole line with `- Report formatting and lint findings as Nits.`
- **SKIP-PATHS**: The skip paths from step 3, backticked and comma-separated, ending with `.github/skills/code-review/*.md` except `SKILL.md`. The installed checklists are always skipped, so the line is always present.
- **SHEBANG-LINE**: When the Bash or zsh checklist is installed, this line, naming only the installed checklists. Otherwise remove the line.

  ```markdown
  - A script without a file extension follows its shebang: Bash scripts use `write-bash-scripts.md` and zsh scripts use `write-zsh-scripts.md`.
  ```

## Checklist Files

Each `.github/skills/code-review/<guide>.md` is this first line, one blank line, then the bundled `./references/checklists/<guide>.md` byte for byte, with GUIDE replaced by the guide name:

```markdown
<!-- Managed by set-up-review-config from GUIDE at PIN. Rerun /set-up-review-config to update this file; local edits are replaced. -->
```

PIN is the 40-character commit or the word `unpinned`. Step 4 reads it back on a rerun.
