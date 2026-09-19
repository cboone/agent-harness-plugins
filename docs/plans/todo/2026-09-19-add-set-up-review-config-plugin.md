# Add the set-up-review-config plugin

Tracks #462.

## Context

The style guides in this repository shape code only while an agent writes it. When a bot reviews the resulting pull request, it applies generic conventions, even in repositories where a precise guide exists. Three reviewers can now take repository guidance, each from a different place (verified against the official docs, September 2026):

| Reviewer            | Reads                                                                                                                | Notes                                                                                                                                                                                         |
| ------------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Copilot code review | `.github/skills/<name>/SKILL.md`, root `AGENTS.md`, `copilot-instructions.md`, `.github/instructions/`               | Skills are chosen by relevance. A directory named `code-review` is the documented way to guarantee use. Supporting files in the skill directory are made available. Reads the PR head branch. |
| Codex cloud review  | `## Code Review Rules` sections in root and nested `AGENTS.md`                                                       | Flags only P0 and P1 on GitHub. 32 KiB default `AGENTS.md` budget.                                                                                                                            |
| Claude Code Review  | Root `REVIEW.md` (sent to every finding and verification agent), `CLAUDE.md` at every level (violations become Nits) | `REVIEW.md` can redefine Important, cap Nits, list skip paths, and suppress new Nits after the first review.                                                                                  |

Two claims in the issue text are out of date: Copilot does not apply every skill on every review, and Codex's section is `## Code Review Rules`, not "Review guidelines". The design below follows the docs.

**Intended outcome:** `/set-up-review-config` detects a repository's file types, installs condensed review checklists for the matching style guides as one Copilot `code-review` skill, and writes matching rules into `AGENTS.md` and `REVIEW.md`, so all three reviewers apply the same guidance.

## Design decisions

| Decision         | Choice                                                                                                                                                                                                                                                                       |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Plugin name      | `set-up-review-config`, category `code-review`, `1.0.0`                                                                                                                                                                                                                      |
| Checklist source | Hand-written `references/review-checklist.md` beside each style guide (user decision)                                                                                                                                                                                        |
| Distribution     | New `bin/build-review-checklists` copies each checklist byte for byte into `plugins/set-up-review-config/skills/set-up-review-config/references/checklists/<guide>.md` during `make build`; new validator rule 20 fails on stale, missing or orphaned copies (user decision) |
| Scope of this PR | Core set: `write-go-code`, `write-lean-code`, `write-lean-tests`, `write-bash-scripts`, `write-zsh-scripts`, `write-markdown`, `write-scrut-tests`. A follow-up issue covers the rest (user decision)                                                                        |
| Copilot layout   | One `.github/skills/code-review/` skill: `SKILL.md` routes changed files to sibling `<guide>.md` checklists. Fallback, only if the step 0 check fails: path-scoped `.github/instructions/<guide>.instructions.md` files with `applyTo` and `excludeAgent: "cloud-agent"`     |
| Managed content  | `<!-- BEGIN set-up-review-config -->` and `<!-- END set-up-review-config -->` blocks in files the user also edits; whole-file ownership, marked by a leading comment, for installed checklists                                                                               |
| Pinned links     | Resolved at install time with `git ls-remote https://github.com/cboone/agent-harness-plugins refs/heads/main`. Kept on rerun when the installed body is unchanged; unpinned `blob/main` fallback when offline, reported as such                                              |
| Rule citation    | Every checklist item has a bold rule name; findings start with `<guide>: <rule name>` so a comment citing the rule can be checked objectively                                                                                                                                |

## Step 0: confirm the Copilot layout before building

Copilot is documented to use a `code-review` skill, but only to make sibling files "available", not to inject them. Settle this first:

1. Write the Go review checklist (part of commit 2 below).
1. In a branch of `cboone/gh-problemas` (a Go CLI you own), hand-assemble `.github/skills/code-review/SKILL.md` plus `write-go-code.md`, and add a Go change that breaks one Important rule and one Nit rule.
1. Open a draft PR, request a Copilot review, and record whether the comments cite the rules.
1. If Copilot cites them, continue with the skill layout. If not, stop and report before switching to the instruction-file fallback.

The same PR is reused for final acceptance, then closed and its branch deleted. Each Copilot review consumes premium requests.

**Result:** on cboone/gh-problemas#18, Copilot cited `write-go-code: Checked errors` (Medium) and `write-go-code: Initialisms` (Low). Those rule names exist only in the sibling checklist, so Copilot reads it through the routing in `SKILL.md`. The skill layout stands; the fallback is not needed.

## Review checklist format

Each `plugins/<guide>/skills/<guide>/references/review-checklist.md`:

- `# <Language> Review Checklist`, then one line naming the files it covers.
- `## Important`: defects that change behavior, lose data, or break tooling. Maps to Claude Important and Codex P1.
- `## Nits`: style rules no formatter enforces.
- `## Do not flag`: accepted exceptions and "when X runs in CI" items. Tool-enforced rules are excluded generically through the installed blocks, not per item.
- Every item is `- **Rule name**: explanation`. Items that apply only to executable scripts (for example, strict mode) say so, so sourced files and rc files are exempt.
- Self-contained: no relative links, no `./references/` paths, no plugin-root placeholder, no `validate-plugins` comments, no backticked `/word` (the cross-reference checker reads it as a skill). No tables or code fences, so a target repository's formatter never rewrites installed files.
- Byte cap of 5,000, enforced by the generator as an error. The largest of the seven checklists is about 4,400 bytes.

These differ from the existing `references/essential/checklist.md` files: they drop formatter-enforced items, assign severity, and target what a reviewer can see in a diff.

## Target repository output

- **`.github/skills/code-review/SKILL.md`**: frontmatter `name: code-review` and a language-neutral `description`, an H1, then a managed block. The block holds a bullet routing list (no tables): each changed-file glob, its checklist file, and a pinned link to the full guide; plus reporting rules: apply to changed lines only; start findings with `<guide>: <rule name>`; Important items are blocking; at most five Nits; do not report what the listed CI tools report; skip the listed paths; rules outside this block take precedence. An existing hand-written `SKILL.md` keeps its frontmatter and gains the block. One whose `name` does not match the directory, or which lacks a description, is reported and the user is asked.
- **`.github/skills/code-review/<guide>.md`**: one leading comment (managed marker, source guide, pinned SHA or "unpinned"), one blank line, then the bundled checklist verbatim. A file with the same name but without the marker is never overwritten.
- **Root `AGENTS.md`**: a managed block at the end of `## Code Review Rules` (heading created if absent, never duplicated). Short bullets: where the checklists are, Important is P1 and everything else P2 or lower, CI tools and skip paths not to report, severity for Claude Code Review is defined in `REVIEW.md`. If `AGENTS.md` is a symlink, edit its target. If only a regular `CLAUDE.md` exists, ask before creating `AGENTS.md` and suggest `/clean-up-agent-config`. Report a legacy `## Review guidelines` section and any nested `AGENTS.md` files; do not edit them.
- **Root `REVIEW.md`**: H1 when created, then a managed block: what Important means here, including the `## Important` items of each installed checklist copied inline (Claude's verification agents may not follow pointers); cap of five Nits with "plus N similar items"; after the first review, Important findings only; do not report CI-enforced tools, generated, lockfile and vendored paths; Nits come from the checklists in `.github/skills/code-review/`. Repository-specific "Always check" items belong outside the block.
- Blank line after each BEGIN marker and before each END marker. Duplicated or unbalanced markers stop the run with a question.

## Plugin: `plugins/set-up-review-config/`

- `.claude-plugin/plugin.json` at `1.0.0`; marketplace entry between `set-up-linters` and `set-up-secret-scanning`; description of 320 characters or fewer (rule 17 warns above that and would break the scrut snapshots). Draft: "Install style-guide review checklists as a Copilot code-review skill, with matching AGENTS.md review rules and a REVIEW.md, so Copilot, Codex, and Claude Code Review apply the same repository guidance."
- `README.md`: verbatim first paragraph, `## Requirements` (git; network optional for pinning), usage, examples, Recommended Permissions JSON, See Also. Root README row in the Code Review table and an External tools bullet.
- `skills/set-up-review-config/SKILL.md` workflow, with a `--dry-run` option that stops after step 5:
  1. **Check the repository**: git root; existing managed blocks, marker balance, `.claude/skills/code-review` or `.agents/skills/code-review` (reported as possible name collisions).
  1. **Detect file types** from `git ls-files`, excluding `vendor/`, `node_modules/`, `.lake/`, `dist/`, `build/`, `testdata/`, lockfiles, `docs/plans/done/`, and Go files marked `Code generated ... DO NOT EDIT.`. Map to guides with `./references/guides.md`.
  1. **Detect what CI enforces and what to skip**: tools actually run by `.github/workflows/` and the Makefile targets they call (gofmt, golangci-lint, shellcheck, shfmt, markdownlint, Prettier, `lake build`, `lake lint`), plus generated, lockfile and vendored paths.
  1. **Resolve pins**: compare installed bodies with bundled copies offline first; keep the existing SHA when unchanged. For changed or new checklists, resolve the tip of `main`, then check the bundled copy against the source at that SHA and warn if the installed plugin is out of date.
  1. **Present the plan**: guides and globs, files to create or update, CI tools, skip paths, pin status, files waiting on the follow-up issue (Pandoc Markdown, POSIX `sh`). Confirm before writing.
  1. **Write** the checklists, the entry skill, the `AGENTS.md` block and the `REVIEW.md` block from the templates. Remove managed checklist files (marker present) for guides no longer detected.
  1. **Validate**: frontmatter `name` matches the directory, markers balanced, root plus nested `AGENTS.md` under 32 KiB, and run the target's own Markdown linters when it has them. Recompute the plan and confirm a rerun would change nothing.
  1. **Report** a summary table and next steps: commit on a branch and open a PR (Copilot reads the head branch, so the PR exercises the new config), add "Always check" items to `REVIEW.md` outside the block.
- `references/guides.md`: per guide, detection signals, routing globs, and the concrete `./references/checklists/<guide>.md` path (so rule 19 checks every named copy exists). Detection rules:
  - **Go**: `go.mod`; `**/*.go`.
  - **Lean**: `lakefile.toml`, `lakefile.lean`, `lean-toolchain` or `*.lean` outside `.lake/`; `**/*.lean`.
  - **Lean tests**: `testDriver` or a `<Name>Test` `lean_lib` in the lakefile, then `<Name>Test/` at any depth plus `<Name>Test.lean`; both Lean checklists apply to those files.
  - **Bash and Zsh**: the shebang interpreter (including `env` and `env -S` forms) overrides the extension. Bash: `.sh`, `.bash`. Zsh: `.zsh`, `*.plugin.zsh`, `.zsh-theme`, zsh dotfiles, `#compdef` or `#autoload` first lines. Extensionless scripts get explicit paths or directory globs. POSIX `sh` is reported as unsupported.
  - **Scrut**: `tests/scrut/**` and Markdown files containing a scrut fence; excluded from the Markdown checklist.
  - **Markdown**: all other tracked `*.md`, except Pandoc-academic files: `set-up-linters`' project signals (`references/papers/`, `references/extractions/`, `references/transcriptions/`, `papers/**/main.md` with templates) plus per-file signals (`bibliography:` or `csl:` frontmatter, `[@key]` citations, `{=latex}` blocks). Those are reported as waiting on the follow-up issue.
- `references/code-review-skill.md`, `references/agents-md-section.md`, `references/review-md.md`: templates in fenced blocks. No template is named `SKILL.md`.
- `references/checklists/`: generated, never hand-edited.
- Avoid a backticked slash form of `code-review` and phrasings like "the `code-review` skill" in plugin files; the cross-reference checker would look for `plugins/code-review`.

## Generator and validation

- **`bin/build-review-checklists`** (Bash, following `write-bash-scripts`):
  - Sources: `plugins/*/skills/*/references/review-checklist.md`, skipping `set-up-review-config`; plugin and skill directory names must match. `LC_ALL=C` ordering. No git dependency. Exit 2 when `plugins/` is missing.
  - Validates every source before writing anything: H1 ending in "Review Checklist"; `## Important`, `## Nits`, `## Do not flag` once each, in order; none of the forbidden constructs above; byte cap. A failing source leaves committed copies untouched.
  - Writes byte-identical copies, removes orphaned `*.md` copies, and refuses an empty or unsafe output path. `REVIEW_CHECKLISTS_DIR` overrides the output directory.
- **`Makefile`**: `build` runs the generator before `bin/build-codex-marketplace` (the Codex mirror copies `plugins/`). Update `help`.
- **`bin/validate-plugins` rule 20**, following rule 16: regenerate into `mktemp -d`, then report one error per missing, stale or orphaned copy (only `*.md` compared), relay generator errors, and check that `references/guides.md` names every copy. Messages say "run make build".
- **`.github/workflows/ci.yml`**: run the generator in the "Validate generated mirrors" step and add the checklists directory to the `git status --porcelain` paths. `release.yml` needs no change; its `bin/validate-plugins` step runs rule 20.
- Editing a source checklist changes two plugin directories, so both need forward version bumps. Documented below.

## Repository integration

- **Style guides** (minor bumps): add `review-checklist.md` and a `./references/review-checklist.md` pointer in each SKILL.md. `write-go-code` 1.3.0, `write-lean-code` 1.1.0, `write-lean-tests` 1.1.0 (its first `references/`), `write-bash-scripts` 2.1.0, `write-zsh-scripts` 1.1.0, `write-markdown` 1.3.0, `write-scrut-tests` 1.2.0.
- **`bootstrap-project`** 1.5.0: existing-infrastructure row (managed marker in `.github/skills/code-review/SKILL.md` or `REVIEW.md`), overlap bullet, execution order after `add-scrut-cli-tests` and before `pin-everything`, example plan row (renumber), invocation list, next steps, `references/overlap-rules.md` section and applicability row, README bullet and See Also.
- **`refresh-project-scaffolding`** 2.2.0: signature row keyed on the managed marker, update-strategy row (rerun `set-up-review-config`), update order, skill list, and a "Reference: Review Config Checks (set-up-review-config)" section (balanced markers, `name: code-review`, routed files present with markers, block under `## Code Review Rules`, `REVIEW.md` block present, unpinned links). Content currency comes from `set-up-review-config --dry-run`, so detection rules live in one plugin. README bullet and See Also.
- **`clean-up-agent-config`** 1.3.1: recognize `REVIEW.md` and `.github/skills/code-review/` in the target structure, "what goes where" and audit list; never move, deduplicate or rewrite managed blocks or marked files; exempt them from the linter-rule and duplication rules.
- **`create-plugin`** 1.2.14: point the mirror step at `make build` and mention review checklists for style-guide plugins.
- **Repository docs**: root `AGENTS.md` critical constraint (never hand-edit the checklists directory; `make build` regenerates it); `plugins/AGENTS.md` and `bin/AGENTS.md` bullets; `docs/plugin-development.md` "Review checklists" section (format, double bumps), and "Adding a plugin" step 8 uses `make build`; `.github/instructions/review-checklists.instructions.md` for this repository's own Copilot reviews, listed in `.github/copilot-instructions.md`'s scoped section.

## Tests

- **New `tests/scrut/build-review-checklists.md`** with fixture `tests/fixtures/review-checklist-fixture` (prints a temp root with two sources and one orphaned copy): copies and removes the orphan; copies match with `cmp`; a second run changes nothing; the directory override leaves committed files alone; each validation error with its exit code (forbidden link, missing heading, size cap, mismatched names, no `plugins/`); a failing run keeps existing copies; the real repository's copies match their sources, reporting whether at least seven sources were found so an empty scan cannot pass.
- **`tests/scrut/repo-tooling.md` plus `validate-plugin-fixture`**: `stale-review-checklist`, `orphan-review-checklist`, `unlisted-review-checklist` scenarios, each producing exactly the rule 20 error and exit 1. The fixture never runs the generator globally.
- Register `BUILD_REVIEW_CHECKLISTS_BIN` and `REVIEW_CHECKLIST_FIXTURE_BIN` in the `Makefile` `SCRUT_ENV` and in `ci.yml` `scrut-env`; add `-u REVIEW_CHECKLISTS_DIR` to `SCRUT_UNSET`.

## Commits

GPG-signed, unscoped Conventional Commits ending in `(#462)`, each leaving `make test-all` green:

1. `docs: add set-up-review-config plan (#462)`
1. `feat: add review checklists to the core style guides (#462)` (Go first, for step 0)
1. `feat: add set-up-review-config plugin (#462)` (plugin, templates, copies, catalog, READMEs, mirrors)
1. `build: generate and validate bundled review checklists (#462)` (generator, Makefile, rule 20, CI, repository docs)
1. `test: cover review checklist generation and validation (#462)`
1. `feat: run set-up-review-config from bootstrap-project (#462)`
1. `feat: audit review config in refresh-project-scaffolding (#462)`
1. `fix: preserve managed review config in clean-up-agent-config (#462)`
1. `docs: add Copilot review guidance for review checklists (#462)`
1. `docs: point create-plugin at make build and review checklists (#462)`

## Verification

- **Mechanical**: `make build`, `make lint`, `make validate`, `make test-scrut`, then `make test-all`, observing the final result. Run the `check-versions` skill before the PR.
- **Go CLI acceptance**: in a scratchpad clone of `gh-problemas`, follow the new `SKILL.md`. Expect `write-go-code`, `write-markdown`, `write-scrut-tests`, and Bash only if shell scripts exist; CI tools from its workflows; `go.sum` skipped. Rerun and confirm zero changes.
- **Lean library acceptance**: in a scratchpad clone of `zhang-yeung-inequality` (`shannon-entropy` is a fork, so it was set aside), expect `write-lean-code` on `**/*.lean`, `write-lean-tests` on `ZhangYeungTest/` and `ZhangYeungTest.lean`, `write-zsh-scripts` on `bin/bootstrap-worktree` by its shebang, `write-markdown` on the rest, and the Pandoc-academic trees under `references/` plus the citing `README.md` reported as waiting on the follow-up. Run the repository's own `markdownlint-cli2` and `cspell` on the output. Rerun and confirm zero changes. This run found that verbatim checklists fail a target's spell checker, so step 7 now adds technical words to the project's word list rather than editing checklists.
- **Copilot citation**: push the generated Go output to the step 0 PR in `cboone/gh-problemas`, request a Copilot review, and confirm a comment cites the violated rule by name. Record the result in the PR description of this repository's PR, then close the test PR and delete its branch.
- **Follow-up issue**: file with the `create-issue` skill for `write-latex`, `write-pandoc-markdown`, `write-math`, `write-realtime-audio-code`, `write-homebrew-formula`, `write-formalization-roadmap` and `handle-secrets`, noting that `write-math` and `handle-secrets` have no file-glob signal.

## Risks

- Copilot might not read sibling checklist files; step 0 settles this before the plugin is built.
- Claude Code Review and Codex following pointers into `.github/skills/code-review/` is undocumented. `REVIEW.md` inlines Important items for Claude; Codex posts only P0 and P1 anyway. Neither is part of the acceptance criteria; both can be spot-checked on the test PR if they are enabled there.
- Editing a source checklist requires two version bumps; rule 20, `check-versions`, and the release workflow all surface a missed one.

## Out of scope

- Review checklists for the seven guides in the follow-up issue.
- Running `set-up-review-config` on this repository.
- Consolidating the detection tables that `set-up-ci`, `set-up-linters`, `bootstrap-project`, `refresh-project-scaffolding` and `add-scrut-cli-tests` each maintain (they have drifted apart); noted for a separate issue.
- Nested `AGENTS.md` review sections and `REVIEW.md` "Always check" content, which stay with the user.
