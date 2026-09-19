---
name: write-markdown
description: >-
  Applies Markdown style conventions when creating or editing Markdown files.
  Use when: (1) creating new Markdown files, (2) editing existing .md files,
  or (3) reviewing Markdown for style and formatting issues.
---

# Markdown Style Guide

Apply the Markdown conventions from `./references/MARKDOWN.md` when creating or editing Markdown files. This guide targets GitHub Flavored Markdown (GFM) and aligns with markdownlint-cli2 rules.

## Common Mistakes

These two issues cause the most formatting churn and lint failures. Check every Markdown file for them.

### Tables: aligned pipes, from Prettier where it runs

A committed table has every pipe aligned, every cell padded to its column width, and delimiter hyphens filled to match. Who does the padding depends on the project.

```markdown
<!-- Committed form: pipes aligned, cells padded -->

| Name    | Type   | Default |
| ------- | ------ | ------- |
| timeout | number | 30      |
| retries | number | 3       |
```

```markdown
<!-- Ragged: fine as a draft only where Prettier will format it -->

| Name | Type | Default |
| --- | --- | --- |
| timeout | number | 30 |
| retries | number | 3 |
```

Determine ownership for each edited file. Verify that Prettier is available as a project dependency or a global tool. Its settings may live in `.prettierrc*`, `prettier.config.*`, or a `prettier` key in `package.json`; config presence alone does not prove that formatting runs. If project format commands exist, inspect their paths, globs, working directory, and options: a command restricted to JavaScript or other non-Markdown files does not own Markdown alignment. If no format command exists, configured and available Prettier can format the file through the direct CLI fallback in Validation. In either case, honor the chosen command's effective ignore files: `.gitignore` and `.prettierignore` by default, or the files specified by `--ignore-path`.

Before formatting a Markdown file with fenced code blocks, check the effective `embeddedLanguageFormatting` setting. Prettier's default `auto` may reformat recognized code blocks along with the tables. Use `embeddedLanguageFormatting: "off"` for the formatting pass, or inspect and accept those code-block changes explicitly.

**Prettier formats this file:** Prettier owns alignment. Write rows without padding, including rows added to an existing table, and follow the command order in Validation. Do not hand-pad cells, and do not cite MD060 as the reason for alignment: projects that run Prettier typically disable it.

**Prettier does not format this file:** align tables by hand, including in files excluded from a project's Prettier command, and do it before running `markdownlint-cli2 --fix`. MD060 has no fix toward the aligned style, and at its default settings it can compact a table that picked up a few unpadded rows, stripping the padding from the rows that were aligned. Procedure: write all rows, find the longest content per column, pad every cell to that width, fill delimiter hyphens to match, then verify all pipes line up.

### Code blocks: always include a language identifier

````markdown
<!-- Correct -->

```bash
echo "hello"
```
````

````markdown
<!-- Wrong: bare fence -->

```
echo "hello"
```
````

Use `text` when no syntax highlighting applies. Never leave the opening fence bare.

## Key Conventions

Read `./references/MARKDOWN.md` for the complete guide. Summary:

### Document Structure

- One top-level heading (`# Title`) per document (MD025)
- Blank line before and after headings, lists, code blocks, and block quotes
- End files with a single trailing newline (MD047)

### Headings

- ATX-style headings (`#`) only, never Setext underlines (MD003)
- Do not skip heading levels (MD001)
- No trailing punctuation on headings (MD026)
- Sibling headings must be unique; same text is fine under different parents (MD024)

### Links and Images

- Inline links for one-off references: `[text](url)`
- Reference links for repeated URLs or long URLs: `[text][id]`
- Always include alt text on images (MD045)

### Lists

- Consistent markers: `-` for unordered (MD004); for ordered lists, use either `1.` for every item or sequential numbering (`1.`, `2.`, `3.`), but be consistent within each list (MD029)
- Indent nested lists consistently
- Blank line before and after a list block (MD032)

### Tables

- Align every pipe vertically and pad delimiter hyphens to match; where Prettier formats Markdown, its format command does this, and elsewhere it is done by hand because markdownlint cannot
- Leading and trailing pipes on every row (MD055)
- Consistent column count across all rows (MD056)

### Code

- Fenced code blocks must have a language identifier, use `text` if none applies (MD040)
- Backtick fences, not tilde fences (MD048)
- Inline code for identifiers, commands, and short expressions

### HTML

- Prefer Markdown syntax when an equivalent exists
- HTML is acceptable for features Markdown lacks (`<details>`, `<kbd>`, `<br>`, `<sub>`, `<sup>`, etc.)

## Pull Request Review

When reviewing a pull request, apply `./references/review-checklist.md`: the rules of this guide that a reviewer can check in a diff, ranked as Important, Nits and Do not flag. The same checklist is installed into repositories for automated reviewers, so update it whenever a rule here changes.

## Validation

After creating or editing Markdown files, run the project's lint-fix and format commands to correct list numbering, spacing, and other formatting issues. This is a required final step, not optional.

Check `package.json` for project-specific scripts (e.g., `yarn lint:fix`, `yarn lint:md:fix`, `yarn format`, `npm run lint:fix`). Also check `Makefile` targets and scripts in `bin/`.

For direct CLI calls, resolve locally installed tools through the project's package manager: `npm exec --`, `yarn`, `pnpm exec`, or `bunx`, following the project's established runner mapping when available. For example, use `yarn markdownlint-cli2 --fix README.md` and `yarn prettier --write README.md` in a Yarn project. Do not use `npx` for Yarn Plug'n'Play projects because it may not resolve the project's locked binary. Use a bare command only when a global installation is verified. Preserve the project's working directory, configuration arguments, and ignore options, and pass the edited file paths.

Choose the order for each file using the Prettier detection above:

- **Prettier formats the file:** Check the effective MD060 setting. If it is enabled or unknown, run a standalone Prettier pass before any lint-fix script; an unpadded table can otherwise produce an unfixable MD060 error and prevent a chained formatter step from running. When MD060 is disabled, this initial pass is unnecessary. Then run lint fixes and finish with Prettier so it has the final say on layout. Use project scripts when available; if a script is missing, use the package-manager runner above with `markdownlint-cli2 --fix` or `prettier --write`. An initial standalone pass must invoke Prettier without a preceding linter, even if the project's usual format target chains both tools.
- **Prettier does not format the file:** Align tables by hand before running any command that invokes markdownlint's fix mode, including project-specific lint-fix scripts. Then run the project's lint-fix command, or use the package-manager runner above with `markdownlint-cli2 --fix` if no such command exists.
