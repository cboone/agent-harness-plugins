# Agent Harness Plugins

## Project overview

This is the canonical source for Claude Code plugins (skills and hooks), with committed generated mirrors for Codex CLI and OpenCode. See [README.md](README.md) for installation and the catalog.

## Critical constraints

- Edit canonical sources in `plugins/<name>/`. Never hand-edit `dist/`, `.agents/` or `set-up-review-config`'s `references/checklists/` copies of each style guide's `references/review-checklist.md`; regenerate with `make build` and commit the results when source changes affect them.
- `.claude-plugin/marketplace.json` is the catalog of record. Each plugin's `.claude-plugin/plugin.json` is its sole version source; a `.codex-plugin/plugin.json` mirrors that version when present. New plugins start at `1.0.0`; wording/fixes are patch changes, new capabilities are minor changes, and breaking changes are major changes.
- After merging, rebasing or before creating a PR, use the repository's [check-versions skill](.claude/skills/check-versions/SKILL.md).
- Root and plugin README descriptions match the catalog description verbatim. Preserve root README anchors `install`, `using-with-opencode` and `codex-cli-known-limitations`; plugin READMEs always link to `install` and link to the other anchors when relevant.

## Navigation and scoped instructions

Read the applicable scoped file before editing its directory, including when working from the repository root. Every scoped `CLAUDE.md` is a symlink to its sibling `AGENTS.md`.

- [plugins/AGENTS.md](plugins/AGENTS.md): skill and hook source, bundled helpers, registration and versioning.
- [bin/AGENTS.md](bin/AGENTS.md): repository validators, generators and tooling.
- [tests/AGENTS.md](tests/AGENTS.md): scrut suites, fixture stubs and CI environment wiring.
- [docs/AGENTS.md](docs/AGENTS.md): plans, reviews and reference documentation.
- [Plugin development](docs/plugin-development.md): full layouts, adding plugins, cross-reference syntax, README catalog format and version rules. Read this before editing plugin or catalog surfaces, including the root README and marketplace files.
- `.github/copilot-instructions.md`: Copilot review rules; `.github/instructions/`: scoped review guidance.

## Running tests and linters

Node and Yarn are pinned in `.tool-versions` and `package.json`; use Yarn through Corepack. Install the pinned dependencies with `yarn install --immutable`. Shell tools must be available on `PATH`.

```bash
make help
make lint          # markdownlint, prettier, shellcheck, shfmt, actionlint
make validate      # JSON, manifests, catalog, mirrors and cross-references
make build         # regenerate bundled review checklists and the Codex and OpenCode mirrors
make test-scrut
make test-all      # lint, validate and scrut
```

`make format` fixes Markdown and shell formatting. `yarn lint:fix` and `yarn format` cover Markdown/Prettier. Run relevant checks after edits; plugin additions require `make test-all` before a PR. Observe the final test result before reporting a pass.

`bin/check-cross-references` runs independently or through validation rule 19. `bin/list-shell-scripts` defines shell lint coverage for local checks and CI. `bin/version-audit` checks upstream drift on the weekly workflow; it is not a merge gate.

## Writing conventions

These rules cover all repository text, including skill prompts, references, READMEs, plans, reviews, commits, PRs and issues.

- No em dashes. Use other punctuation, or a spaced double hyphen where appropriate.
- No human or agent work estimates, including durations, “quick”, sprints, sizes or story points. Describe scope, dependencies and uncertainty. Code runtime measurements and complexity are allowed.
- Use neutral technical terms: running/stopped, in use/unused, terminate, validity check, sample data, unexpected, primary/replica and allowlist/blocklist. Fixed upstream identifiers and proper nouns remain unchanged.
- Keep this operating summary concise. Place component rules in paired scoped instruction files and specialized detail in references. Check global plus root plus nested instruction sizes against 32 KiB.

## License

MIT; see `LICENSE`.

## Code Review Rules

<!-- BEGIN set-up-review-config -->

- Review each changed file against its checklist in `.github/skills/code-review/`; the `SKILL.md` there maps file patterns to checklists.
- Rules under a checklist's Important heading are P1. All other checklist rules are P2 or lower.
- Start each finding with the checklist name and the rule name, for example `write-go-code: Checked errors`.
- Do not report what these CI checks already report: `markdownlint-cli2`, `prettier`, `shellcheck`, `shfmt`, `actionlint`, `bin/validate-json`, `bin/validate-plugins`, the `make build` generated-mirror drift check, `scrut`.
- Do not review these paths: `yarn.lock`, `dist/`, `.agents/`, `plugins/set-up-review-config/skills/set-up-review-config/references/checklists/`, `docs/plans/done/`, `.github/skills/code-review/*.md` except `SKILL.md`.
- Claude Code Review takes its severities from `REVIEW.md`.
- Rules outside this block take precedence over it.

<!-- END set-up-review-config -->
