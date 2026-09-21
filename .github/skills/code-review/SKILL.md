---
name: code-review
description: Style checklists for reviewing this repository's pull requests. Use for every pull request review to match each changed file to its checklist and report findings with the severities defined here.
---

# Code Review

<!-- BEGIN set-up-review-config -->

Apply the checklist that matches each changed file, and apply it only to the lines the pull request changes.

## Checklists

- Bash scripts (`bin/*`, `plugins/*/scripts/*`, `plugins/*/skills/*/references/scripts/*`, `tests/fixtures/*`, except `bin/AGENTS.md`, `bin/CLAUDE.md`, `**/*.yml`): `write-bash-scripts.md`. Full guide: [write-bash-scripts style guide](https://github.com/cboone/agent-harness-plugins/blob/7b2f18f490d22c59a4210f4c68c0b6528a5ea49f/plugins/write-bash-scripts/skills/write-bash-scripts/SKILL.md).
- Scrut test files (`tests/scrut/**/*.md`): `write-scrut-tests.md`. Full guide: [write-scrut-tests style guide](https://github.com/cboone/agent-harness-plugins/blob/7b2f18f490d22c59a4210f4c68c0b6528a5ea49f/plugins/write-scrut-tests/skills/write-scrut-tests/SKILL.md).
- Markdown files (`**/*.md`, except `tests/scrut/**/*.md`): `write-markdown.md`. Full guide: [write-markdown style guide](https://github.com/cboone/agent-harness-plugins/blob/7b2f18f490d22c59a4210f4c68c0b6528a5ea49f/plugins/write-markdown/skills/write-markdown/SKILL.md).

## Reporting

- Start each finding with the checklist name and the rule name, for example `write-bash-scripts: Strict mode`.
- Rules under a checklist's Important heading block merging. Report each one you find.
- Rules under a checklist's Nits heading are minor. Report at most five per review, and give the number of any others in the summary.
- Follow each checklist's Do not flag section.
- Do not report what these CI checks already report: `markdownlint-cli2`, `prettier`, `shellcheck`, `shfmt`, `actionlint`, `bin/validate-json`, `bin/validate-plugins`, the `make build` generated-mirror drift check, `scrut`.
- Do not review these paths: `yarn.lock`, `dist/`, `.agents/`, `plugins/set-up-review-config/skills/set-up-review-config/references/checklists/`, `docs/plans/done/`, `.github/skills/code-review/*.md` except `SKILL.md`.
- A script without a file extension follows its shebang: Bash scripts use `write-bash-scripts.md`.
- Rules outside this block, in this file, `.github/copilot-instructions.md`, `AGENTS.md` or `REVIEW.md`, take precedence over it.

<!-- END set-up-review-config -->
