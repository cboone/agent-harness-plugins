---
name: set-up-review-config
description: >-
  Install style-guide review checklists as a Copilot code-review skill, with
  matching AGENTS.md review rules and a REVIEW.md, so Copilot, Codex, and Claude
  Code Review apply the same guidance.
---

# Set-Up Review Config

Install review guidance that three automated pull request reviewers read, built from the style guides in this marketplace:

| Reviewer            | Reads                                                                                | Installed                                                                              |
| ------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Copilot code review | Skills under `.github/skills/`; a skill directory named `code-review` is always used | `.github/skills/code-review/SKILL.md`, which routes each changed file to its checklist |
| Codex cloud review  | `## Code Review Rules` sections in `AGENTS.md`                                       | A managed block in that section of the root `AGENTS.md`                                |
| Claude Code Review  | The root `REVIEW.md`, plus `CLAUDE.md` as nit-level context                          | A managed block in `REVIEW.md`, including every checklist's Important rules            |

The checklists are bundled in `./references/checklists/`, one per style guide, and are installed verbatim beside the entry `SKILL.md`. Every rule has a bold name, and findings cite it as `<guide>: <rule name>`, for example `write-go-code: Checked errors`.

## Options

- **--dry-run**: Detect, then present the plan in step 5 and stop without writing anything.

## Managed Content

- **Blocks**: A managed block starts with a line holding exactly `<!-- BEGIN set-up-review-config -->` and ends with a line holding exactly `<!-- END set-up-review-config -->`, with one blank line after the first and one before the second. A rerun replaces everything from the BEGIN line through the END line, and nothing else.
- **Whole files**: An installed checklist file is managed as a whole. Its first line is a comment that begins `<!-- Managed by set-up-review-config`. A file without that first line is never overwritten or removed.
- **Precedence**: Everything outside the managed blocks belongs to the repository. The blocks say that rules outside them take precedence, so exceptions and repository-specific checks go there.
- **Format**: The templates avoid tables, `*` bullets and other constructs that Markdown formatters rewrite, so a formatted file still matches what a rerun writes.

## Workflow

### 1. Check the Repository

1. Work from the repository root (`git rev-parse --show-toplevel`). Stop if the directory is not in a git repository.
1. In `.github/skills/code-review/SKILL.md`, `AGENTS.md` and `REVIEW.md`, count the BEGIN and END marker lines. If a file has more than one of either, or an END before its BEGIN, stop and ask the user how to repair it.
1. If `.github/skills/code-review/SKILL.md` exists, read its frontmatter. Copilot requires `name: code-review` and a non-empty `description`; if either is missing or different, report it and ask before continuing.
1. Report any `.claude/skills/code-review/` or `.agents/skills/code-review/` directory: a second skill with the same name may compete with the installed one. Do not change it.
1. Resolve `AGENTS.md`. When it is a symlink, edit its target and never replace the link. When it is absent and `CLAUDE.md` is a regular file, ask before creating `AGENTS.md`, and mention `/clean-up-agent-config` for consolidating agent instruction files.
1. Report an existing `## Review guidelines` section in any `AGENTS.md` (an older Codex heading) and any nested `AGENTS.md` files. Codex layers nested files over the root one; leave them unchanged.

### 2. Detect File Types

List tracked files with `git ls-files`, so `.gitignore` applies. Exclude `vendor/`, `node_modules/`, `.lake/`, `dist/`, `build/`, `testdata/`, `docs/plans/done/`, lockfiles, and Go files whose first lines carry a `Code generated ... DO NOT EDIT.` comment.

Apply the detection rules in `./references/guides.md` to choose the guides and their routing globs. Record, for the report, files that match no supported guide because their checklist does not exist yet, such as Pandoc-academic Markdown and POSIX `sh` scripts.

### 3. Detect What CI Enforces and What to Skip

1. **CI checks**: Read `.github/workflows/*.yml` and the Makefile targets or package scripts they call. List only checks that CI actually runs, such as `gofmt`, `goimports`, `go vet`, `golangci-lint`, `shellcheck`, `shfmt`, `zsh -n`, `markdownlint-cli2`, `prettier`, `cspell`, `lake build` and `lake lint`. Note which of them read Markdown, since step 7 runs those on the written files. When a workflow calls a reusable workflow, read the called workflow if it is reachable and list the checks its inputs enable; otherwise name the reusable workflow and its inputs.
1. **Skip paths**: List the paths reviewers should ignore that exist in the repository: lockfiles (`go.sum`, `yarn.lock`, `package-lock.json`, `pnpm-lock.yaml`, `Cargo.lock`, `lake-manifest.json`, `*.lock`), vendored directories, and generated files or mirrors that the repository documents as generated.

### 4. Resolve Pinned Links

Each installed checklist records the commit of this marketplace that its full-guide link points at, or `unpinned`.

1. For each selected guide whose checklist is already installed, compare the installed body (everything after the managed first line and the blank line that follows it) with the bundled `./references/checklists/<guide>.md`. When they match and the recorded pin is a commit, keep that pin; the guide needs no network access.
1. For new guides, changed checklists and `unpinned` installs, resolve the marketplace tip once:

   ```bash
   git ls-remote https://github.com/cboone/agent-harness-plugins refs/heads/main
   ```

   Use the first field as the pin. If the command fails, for example because the harness has no network access, record those guides as `unpinned`; their links point at `main`, and a later run with network access pins them.

1. With a pin, check that the bundled checklists are current. For each guide, fetch `https://raw.githubusercontent.com/cboone/agent-harness-plugins/<sha>/plugins/<guide>/skills/<guide>/references/review-checklist.md` with `curl -fsSL` and compare it with the bundled copy. If one differs, the installed marketplace is behind: say so, suggest updating the marketplace and rerunning, and ask whether to continue with the bundled checklists. If the fetch fails, continue and note that the check was skipped.

### 5. Present the Plan

Show a table with one row per guide: guide, routing globs, checklist file, action (create, update, unchanged or remove) and pin. Then list the CI checks, the skip paths, the change to each of `.github/skills/code-review/SKILL.md`, `AGENTS.md` and `REVIEW.md`, the files waiting on a future checklist, and every conflict reported in step 1.

If nothing would change, report that the review config is current and stop. With `--dry-run`, stop here. Otherwise ask whether to proceed; the user may deselect guides.

### 6. Write the Files

Fill the templates in `./references/code-review-skill.md`, `./references/agents-md-section.md` and `./references/review-md.md`.

1. **Checklists**: For each selected guide, write `.github/skills/code-review/<guide>.md`: the managed first line, one blank line, then the bundled checklist byte for byte. Remove managed checklist files for guides that are no longer selected. If an unmanaged file already has a selected guide's file name, skip that guide and report the conflict.
1. **Entry skill**: When `.github/skills/code-review/SKILL.md` does not exist, create it from the template. Otherwise replace its managed block, or append the block at the end of the file, leaving the frontmatter and all other content unchanged.
1. **AGENTS.md**: When the file has a `## Code Review Rules` heading, replace the managed block inside that section, or append the block at the end of the section. Otherwise append the heading and the block at the end of the file. Create the file with an H1 naming the repository when it does not exist. Never add a second `## Code Review Rules` heading.
1. **REVIEW.md**: When the file does not exist, create it with the template's H1. Otherwise replace its managed block, or append the block at the end of the file. If the file already defines severities, a nit cap or skip rules outside the block, report the overlap; the repository's own text takes precedence.

### 7. Validate

1. `.github/skills/code-review/SKILL.md` has `name: code-review` and a non-empty `description` in its frontmatter.
1. Every checklist named in the routing list exists and starts with the managed first line, and no managed checklist file is left unrouted.
1. `.github/skills/code-review/SKILL.md`, `AGENTS.md` and `REVIEW.md` each have exactly one BEGIN line followed by one END line.
1. The root `AGENTS.md` plus the largest nested `AGENTS.md` chain stays under 32 KiB, the default budget Codex reads. Warn when it does not.
1. Run the repository's own Markdown linter, formatter and spell checker on the written files, the way its CI does. The checklists are installed verbatim, so never edit them to satisfy a tool:
   - A spell checker rejects technical terms the checklists use, such as `shfmt` or `compadd`. List the unknown words for the user, then add them to the project's word list, in the order the list already follows: the file its configuration names as a custom dictionary, or its inline `words` list.
   - A linter or formatter finding in managed content is a defect in this plugin's templates or checklists. Keep the formatted result and report the construct that changed.
1. Repeat steps 2 to 4 against the written files and confirm that a rerun would change nothing.

### 8. Report

Summarize each file and its action, the pins, the CI checks, the skip paths, any words added to the spell checker's word list, the files waiting on a future checklist, and any conflicts. Then give the next steps:

- Commit on a branch and open a pull request. Copilot reads skills and instructions from a pull request's head branch, so that pull request is already reviewed with the new config.
- Add repository-specific checks to `REVIEW.md` under an `## Always check` heading outside the managed block.
- Codex posts only P0 and P1 findings on GitHub, so from Codex expect the Important rules only.
- Rerun `/set-up-review-config` after updating the marketplace or when the repository gains a new file type; `/refresh-project-scaffolding` audits installed review config.

Ask whether to commit. Suggest `chore: set up review config` as the commit message.

## Error Handling

- **Not a git repository**: Stop; detection needs `git ls-files`.
- **No supported file types**: Report the file types found and that no checklist covers them yet, and stop without writing.
- **Unbalanced or duplicated markers**: Stop and ask how to repair the file before writing anything.
- **Unmanaged file in the way**: Skip the affected guide and report the file; never overwrite a checklist file that lacks the managed first line.
- **Invalid hand-written entry skill**: Ask before appending to a `.github/skills/code-review/SKILL.md` whose frontmatter Copilot would reject.
- **No network access**: Install with `unpinned` links and say so; a later run with network access pins them.
- **Marketplace behind**: When a bundled checklist differs from the marketplace tip, warn and ask whether to continue.
- **Formatter rewrites managed content**: Keep the formatted result, report which construct changed, and treat the template as needing a fix in this plugin.
- **Spell checker rejects checklist words**: Add the words to the project's word list after listing them for the user; editing a verbatim checklist would make the next run rewrite it.
