# Claude Code Plugins

A collection of plugins (skills and hooks) for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [OpenAI's Codex CLI](https://developers.openai.com/codex/cli), from [Christopher Boone](https://cboone.github.io).

## Contents

- [Install](#install): [Claude Code](#claude-code), [Codex CLI](#codex-cli), [OpenCode](#opencode)
- [Moved and removed plugins](#moved-and-removed-plugins)
- [Skills](#skills): [Git](#git), [Issues and Worktrees](#issues-and-worktrees), [Code Review](#code-review), [Code Quality](#code-quality), [Writing](#writing), [Scaffolding](#scaffolding), [CI and Release](#ci-and-release), [Agents](#agents)
- [Hooks](#hooks)
- [Using with Codex CLI](#using-with-codex-cli)
- [License](#license)

## Install

### Claude Code

From within `claude`, open the plugins manager via `/plugin`, tab to `Marketplace`, and hit `enter` on `Add Marketplace`. Type `cboone/agent-harness-plugins`, then choose which plugins to install.

Or, from within `claude`:

```bash
/plugin marketplace add cboone/agent-harness-plugins
```

### Codex CLI

Register the marketplace, then install the plugins you want:

```bash
codex plugin marketplace add cboone/agent-harness-plugins
codex plugin add commit@agent-harness-plugins
```

See [Using with Codex CLI](#using-with-codex-cli) below for selective installation, hook review and trust, refreshing and removing plugins, troubleshooting, and Codex-specific limitations.

### OpenCode

OpenCode is no longer supported. The last `dist/opencode/` mirror is available at commit [`41605e95`](https://github.com/cboone/agent-harness-plugins/tree/41605e95bd814e354799722eae2fc9c8d50e2796/dist/opencode).

## Moved and removed plugins

The catalog consolidates related workflows into plugins with several skills and folds focused workflows into their existing hosts. Reinstall the destination plugin and update saved invocations using this mapping. The old plugin registrations are removed. Use qualified invocations to identify both the plugin and skill; Claude Code still resolves the retained bare names `create-worktree` and `create-issue` to their new plugins.

| Former plugin or skill        | Install plugin      | Invocation or workflow                 |
| ----------------------------- | ------------------- | -------------------------------------- |
| `create-worktree`             | `workmux`           | `/workmux:create-worktree`             |
| `address-issue-in-worktree`   | `workmux`           | `/workmux:start-issue`                 |
| `monitor-pr`                  | `monitor-pr`        | `/monitor-pr:monitor`                  |
| `resolve-copilot-pr-feedback` | `monitor-pr`        | `/monitor-pr:resolve-copilot-feedback` |
| `merge-main`                  | `sync-with-main`    | `/sync-with-main:merge`                |
| `rebase-onto-main`            | `sync-with-main`    | `/sync-with-main:rebase`               |
| `review-dependabot-config`    | `dependabot`        | `/dependabot:review-config`            |
| `triage-dependabot-prs`       | `dependabot`        | `/dependabot:triage-prs`               |
| `create-issue`                | `use-git`           | `/use-git:create-issue`                |
| `add-goreleaser-homebrew`     | `set-up-installers` | GoReleaser mode                        |
| `write-homebrew-formula`      | `set-up-installers` | Homebrew formula mode                  |
| `add-cobra-version`           | `scaffold-go-cli`   | Existing CLI version mode              |
| `check-zsh-scripts`           | `write-zsh-scripts` | Lint workflow                          |
| `write-lean-tests`            | `write-lean-code`   | Mirrored test-library reference        |
| `optimize-runner-usage`       | `set-up-ci`         | Runner-usage mode                      |
| `add-community-files`         | `scaffold-new-repo` | Community-files mode                   |

Install the destination using `/plugin install PLUGIN@agent-harness-plugins` in Claude Code or `codex plugin add PLUGIN@agent-harness-plugins` in Codex CLI, replacing `PLUGIN` with the table's Install plugin value. For example:

```text
/plugin install workmux@agent-harness-plugins
codex plugin add workmux@agent-harness-plugins
```

Folded workflows retain requests such as "add a version command", "add community files", "reduce CI costs" and "write a Homebrew formula". They run only the selected mode when updating an existing project. See each destination's README for usage and requirements.

## Skills

Each skill links to its own README. The `Trigger` column shows the slash command. Some style-guide skills also activate automatically when you touch their target file types; see the per-plugin README for activation rules.

### Git

| Plugin                                               | Trigger                                           | What it does                                                                                                                      |
| ---------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [Commit](./plugins/commit/README.md)                 | `/commit`                                         | Smart, context-aware git commits with conventional commit messages and plan awareness.                                            |
| [Sync With Main](./plugins/sync-with-main/README.md) | `/sync-with-main:merge`, `/sync-with-main:rebase` | Merge or rebase the base branch into the current branch, resolve conflicts, and push using the selected workflow.                 |
| [PR](./plugins/pr/README.md)                         | `/pr`                                             | Lint, commit, push, and create a pull request in one step with no prompts.                                                        |
| [Release](./plugins/release/README.md)               | `/release`                                        | Prepare a versioned release: update release files, create a release commit, tag locally, and optionally publish a GitHub Release. |
| [Review Branch](./plugins/review-branch/README.md)   | `/review-branch`                                  | Review and evaluate all work done on the current branch: summarize changes, assess plan compliance, and evaluate code quality.    |
| [Use Git](./plugins/use-git/README.md)               | `/use-git:use-git`, `/use-git:create-issue`       | Apply git and GitHub CLI conventions for tmpfile bodies, signed commits and safe pushes, and create GitHub issues.                |

**External tools:**

- _PR, Use Git:_ [`gh`](https://cli.github.com/)
- _Sync With Main, Review Branch:_ [`gh`](https://cli.github.com/) for default-branch detection; each falls back to a local git query if unavailable
- _Release:_ [`jq`](https://jqlang.org/) for marketplace catalog releases; [`gh`](https://cli.github.com/) optional for GitHub Release creation

### Issues and Worktrees

| Plugin                                                               | Trigger                                                                           | What it does                                                                                                                                               |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Address Issue](./plugins/address-issue/README.md)                   | `/address-issue <issue>`                                                          | Fetch a GitHub issue, plan the work, stop for approval, then execute changes and commit with issue references.                                             |
| [Workmux](./plugins/workmux/README.md)                               | `/workmux:create-worktree <issue-or-description>`, `/workmux:start-issue <issue>` | Create worktrees, branches and tmux windows with workmux, or launch issue planning in a new session.                                                       |
| [Create Deferred Issues](./plugins/create-deferred-issues/README.md) | `/create-deferred-issues`                                                         | Scan the session, branch, and pull request for concerns set aside as out of scope, propose them as one batch, and file the approved ones as GitHub issues. |
| [Suggest Next Issue](./plugins/suggest-next-issue/README.md)         | `/suggest-next-issue`                                                             | Recommend the next open GitHub issue in a focused terminal answer, with reasoning, progress signals and resource constraints.                              |
| [WTAF](./plugins/wtaf/README.md)                                     | `/wtaf`                                                                           | Summarize where the conversation, branch, and tasks stand and what comes next, with a thorough mode that also reads the history.                           |

**External tools:**

- _Address Issue, Create Deferred Issues, Suggest Next Issue:_ [`gh`](https://cli.github.com/)
- _Workmux:_ [`workmux`](https://github.com/raine/workmux), plus [`gh`](https://cli.github.com/) when given an issue number and [`jq`](https://jqlang.org/) for an issue number or a resource claim
- _WTAF:_ optional [`gh`](https://cli.github.com/) for pull request, issue, and CI state; without it, the summary uses the conversation and local git alone

### Code Review

| Plugin                                                           | Trigger                                                       | What it does                                                                                                                                                                                                                                                          |
| ---------------------------------------------------------------- | ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Address Review](./plugins/address-review/README.md)             | `/address-review <path>`                                      | Parse a review document for actionable feedback, work through items systematically, and track resolution progress.                                                                                                                                                    |
| [Review Anti-Patterns](./plugins/review-anti-patterns/README.md) | `/review-anti-patterns`                                       | Review a branch or a fix diff, read-only, against a checklist of the defect patterns that most often survive local review and surface in later Copilot rounds, such as bypassable sanitizers, parallel paths left behind, and docs that disagree with the code.       |
| [Review Colleague PR](./plugins/review-colleague-pr/README.md)   | `/review-colleague-pr`                                        | Review a colleague's pull request carefully and considerately from a checkout of its branch, and report a brief, read-only assessment in chat: requirements, direction, blockers, follow-ups, and questions for the author.                                           |
| [Review Plan](./plugins/review-plan/README.md)                   | `/review-plan [path]`                                         | Review an implementation plan against the current repository and its explicit dependencies, reporting evidence-backed blockers, required revisions, and optional improvements before work begins. Use when asked to review a plan or assess implementation readiness. |
| [Review PR with Codex](./plugins/review-pr-with-codex/README.md) | `/review-pr-with-codex`                                       | Have Codex review the current branch in focused aspects (code, error handling, tests, comments, types), each in its own read-only run, then merge the findings into one report with an action plan.                                                                   |
| [Review Until Clean](./plugins/review-until-clean/README.md)     | `/review-until-clean`                                         | Run a read-only reviewer from another model family over every local change, fix the findings at or above a severity threshold, and repeat until the exact snapshot on disk comes back clean or a round limit stops the loop.                                          |
| [Monitor Pr](./plugins/monitor-pr/README.md)                     | `/monitor-pr:monitor`, `/monitor-pr:resolve-copilot-feedback` | Monitor a pull request until its checks pass, Copilot signs off on the current head, and it is mergeable, fixing failures along the way, then offer the merge and sync the main worktree once it lands; resolve Copilot feedback on demand.                           |
| [Set-Up Review Config](./plugins/set-up-review-config/README.md) | `/set-up-review-config`                                       | Install style-guide review checklists as a Copilot code-review skill, with matching AGENTS.md review rules and a REVIEW.md, so Copilot, Codex, and Claude Code Review apply the same guidance.                                                                        |

**External tools:**

- _Review Anti-Patterns:_ [`gh`](https://cli.github.com/) (optional; finds the default branch when `origin/HEAD` is unset, and reads the open pull request's body)
- _Review Colleague PR:_ [`gh`](https://cli.github.com/) (required; the skill reads the PR, its linked issues, its reviews, and its CI status over the GitHub API, and writes nothing)
- _Review Plan:_ [`gh`](https://cli.github.com/) (optional; only for explicitly linked GitHub context)
- _Review PR with Codex:_ [`codex`](https://github.com/openai/codex) (required; every aspect runs through Codex, read-only except `simplify`); `jq` (required; the bundled helpers emit and validate JSON)
- _Review Until Clean:_ [`codex`](https://github.com/openai/codex) or [`claude`](https://code.claude.com/docs/en/overview) (one required, as the reviewer backend; both run read-only and neither is given a fix flag); `jq` (required; the bundled scope helper emits JSON)
- _Resolve Copilot PR Feedback:_ [`gh`](https://cli.github.com/) (required; the skill reads review threads over the GitHub API and posts its summary comment)
- _Set-Up Review Config:_ `git` (required; the skill detects file types with `git ls-files` and pins links with `git ls-remote`); `curl` (optional; checks that the bundled checklists match the marketplace)

### Code Quality

| Plugin                                                                      | Trigger                      | What it does                                                                                                                                                                     |
| --------------------------------------------------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Add Scrut CLI Tests](./plugins/add-scrut-cli-tests/README.md)              | `/add-scrut-cli-tests`       | Set up scrut snapshot-based CLI integration testing for a CLI project.                                                                                                           |
| [Handle Secrets](./plugins/handle-secrets/README.md)                        | `/handle-secrets`            | Best practices for handling user-provided secrets in CLI tools: secure input methods, credential storage, secret masking, and language-specific libraries.                       |
| [Lint and Fix](./plugins/lint-and-fix/README.md)                            | `/lint-and-fix`              | Detect project linters and formatters, run them with auto-fix, resolve remaining issues, then commit and push the fixes.                                                         |
| [Plant Defects](./plugins/plant-defects/README.md)                          | `/plant-defects`             | Deliberately break code to prove a test can see it: plant the defect an instrument claims to catch, confirm it goes red, and record it so it regresses.                          |
| [Set-Up Linters](./plugins/set-up-linters/README.md)                        | `/set-up-linters`            | Detect project languages, recommend linters and formatters, install them, and generate config files, including Pandoc-academic Markdown presets.                                 |
| [Trim Comments](./plugins/trim-comments/README.md)                          | `/trim-comments`             | Trim and rewrite code comments so each leads with what the code does and the minimum why, cutting trivia, jargon, restatement, and details that go stale.                        |
| [Write Bash Scripts](./plugins/write-bash-scripts/README.md)                | `/write-bash-scripts`        | Applies Bash style conventions when creating or editing Bash scripts.                                                                                                            |
| [Write Go Code](./plugins/write-go-code/README.md)                          | `/write-go-code`             | Go code style guide based on Google Go Style Guide, Effective Go, Code Review Comments, and Cobra CLI behavior.                                                                  |
| [Write LaTeX](./plugins/write-latex/README.md)                              | `/write-latex`               | LaTeX mathematical typesetting style guide based on AMS, IEEE, ISO 80000-2, and Knuth conventions.                                                                               |
| [Write Lean Code](./plugins/write-lean-code/README.md)                      | `/write-lean-code`           | Lean 4 and Mathlib conventions for code, proofs, naming, documentation and compile-time tests that mirror the public library API.                                                |
| [Write Real-Time Audio Code](./plugins/write-realtime-audio-code/README.md) | `/write-realtime-audio-code` | Write and review real-time audio code: callback safety, bounded cross-thread communication, memory ordering, sample-accurate events, and compatible plugin parameters and state. |
| [Write Scrut Tests](./plugins/write-scrut-tests/README.md)                  | `/write-scrut-tests`         | Applies scrut test style conventions when creating or editing scrut test files for CLI binaries and zsh plugins.                                                                 |
| [Write Zsh Scripts](./plugins/write-zsh-scripts/README.md)                  | `/write-zsh-scripts`         | Zsh scripting conventions for syntax, types, expansion, scope and completions, with a workflow for syntax checks, compilation, linting and formatting.                           |

**External tools:**

- _Add Scrut CLI Tests, Write Scrut Tests:_ [`scrut`](https://github.com/facebookincubator/scrut) (Makefile checks for availability and provides install instructions)
- _Check Zsh Scripts:_ [`shellcheck`](https://www.shellcheck.net/), [`shfmt`](https://github.com/mvdan/sh), [`shellharden`](https://github.com/anordal/shellharden), [`checkbashisms`](https://packages.debian.org/devscripts)
- _Trim Comments:_ `realpath` (GNU coreutils, or macOS 13 and later)

### Writing

| Plugin                                                                               | Trigger                           | What it does                                                                                                                                                           |
| ------------------------------------------------------------------------------------ | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Publish Report Board](./plugins/publish-report-board/README.md)                     | `/publish-report-board`           | Publish a recurring analysis, such as backlog triage or bug triage, as a live report board with a stable URL, and re-sync it in place as the source data changes.      |
| [Trim Text](./plugins/trim-text/README.md)                                           | `/trim-text`                      | Trim and rewrite prose, such as PR and issue bodies and agent instructions, so it leads with what the reader needs and the minimum why, without changing what it says. |
| [Write Formalization Roadmap](./plugins/write-formalization-roadmap/README.md)       | `/write-formalization-roadmap`    | Document-structure guide for multi-milestone formalization roadmaps in Lean, Rocq, Isabelle, HOL, and other proof assistants.                                          |
| [Write Manual Verification Plan](./plugins/write-manual-verification-plan/README.md) | `/write-manual-verification-plan` | Write a numbered, resumable checklist for checks run by hand, where every step says what to do, what you should see, and how to tell nothing from broken.              |
| [Write Markdown](./plugins/write-markdown/README.md)                                 | `/write-markdown`                 | Applies Markdown style conventions when creating or editing Markdown files.                                                                                            |
| [Write Math](./plugins/write-math/README.md)                                         | `/write-math`                     | Mathematical writing and exposition guide based on Tao, Knuth, Halmos, and other leading references.                                                                   |
| [Write Pandoc Markdown](./plugins/write-pandoc-markdown/README.md)                   | `/write-pandoc-markdown`          | Pandoc-flavored Markdown conventions for academic papers with LaTeX output.                                                                                            |

**External tools:**

- _Publish Report Board:_ [`jq`](https://jqlang.org/) (required; the bundled `report-board` script validates and renders board data with it), [`gh`](https://cli.github.com/) (required for the backlog board, which reads issues, milestones, and pull requests)
- _Trim Text:_ an authenticated [`gh`](https://cli.github.com/) session, only for PR and issue bodies; `realpath` (GNU coreutils, or macOS 13 and later) for symlinked instruction files
- _Write Manual Verification Plan:_ an authenticated [`gh`](https://cli.github.com/) session, only when the checklist is kept on an issue rather than in a plan

### Scaffolding

| Plugin                                                                         | Trigger                        | What it does                                                                                                                                                |
| ------------------------------------------------------------------------------ | ------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Bootstrap Project](./plugins/bootstrap-project/README.md)                     | `/bootstrap-project`           | Assess a repository, determine what scaffolding and setup tools are needed, present a plan, and execute them in the correct order.                          |
| [Manage Repo Licensing](./plugins/manage-repo-licensing/README.md)             | `/manage-repo-licensing`       | Bootstrap, audit, and maintain REUSE-style mixed-license coverage in a repository: LICENSES/, NOTICE, REUSE.toml, SPDX headers, and reuse lint cleanliness. |
| [Refresh Project Scaffolding](./plugins/refresh-project-scaffolding/README.md) | `/refresh-project-scaffolding` | Refresh existing project scaffolding against the latest plugin templates.                                                                                   |
| [Scaffold Go Library](./plugins/scaffold-go-library/README.md)                 | `/scaffold-go-library`         | Scaffold a Go library project with GoReleaser changelog-only releases, golangci-lint, GitHub Actions CI/CD, and Makefile.                                   |
| [Scaffold Lean Library](./plugins/scaffold-lean-library/README.md)             | `/scaffold-lean-library`       | Scaffold a Lean 4 library project with Mathlib or PFR dependencies, Lake test/lint wiring, GitHub Actions CI, text linting, and agent instructions.         |
| [Scaffold New Repo](./plugins/scaffold-new-repo/README.md)                     | `/scaffold-new-repo`           | Scaffold language-agnostic repository files: LICENSE, README, CHANGELOG, .gitignore, agent config and plans, with optional community files.                 |
| [Scaffold Rust CLI](./plugins/scaffold-rust-cli/README.md)                     | `/scaffold-rust-cli`           | Scaffold a complete Rust CLI project with Cargo, cargo-deny, cargo-nextest, git-cliff, GitHub Actions CI/CD, and Makefile.                                  |
| [Scaffold Zig CLI](./plugins/scaffold-zig-cli/README.md)                       | `/scaffold-zig-cli`            | Scaffold a complete Zig CLI project with build.zig, build.zig.zon, cross-compiled releases, GitHub Actions CI/CD, and Makefile.                             |

**External tools:**

- _Manage Repo Licensing:_ [`reuse`](https://reuse.software/). Install via [Homebrew](https://brew.sh): `brew install reuse`
- _Scaffold Go CLI, Scaffold Go Library, Scaffold Lean Library, Scaffold New Repo, Scaffold Rust CLI:_ [`gh`](https://cli.github.com/) to resolve the GitHub owner and create the repository. Each also needs its own toolchain: Go, [`elan`](https://github.com/leanprover/elan)/`lake` for Lean, and Cargo for Rust
- _Scaffold Zig CLI:_ [`gh`](https://cli.github.com/) to resolve the GitHub owner, and [Zig](https://ziglang.org/download/) 0.16 or later. It runs `git init` locally but does not create a repository on GitHub

### CI and Release

| Plugin                                                               | Trigger                                               | What it does                                                                                                                                                                                   |
| -------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Scaffold Go Cli](./plugins/scaffold-go-cli/README.md)               | `/scaffold-go-cli`                                    | Scaffold a complete Go CLI project with Cobra, GoReleaser, GitHub Actions and Homebrew tap support, or add version metadata to an existing Cobra CLI.                                          |
| [Pin Everything](./plugins/pin-everything/README.md)                 | `/pin-everything`                                     | Pin every version surface in a repository (action SHAs, packageManager integrity digests, dependency exact-pins, runtime version files, install commands) for one-shot supply-chain hardening. |
| [Dependabot](./plugins/dependabot/README.md)                         | `/dependabot:review-config`, `/dependabot:triage-prs` | Review Dependabot configuration and triage open Dependabot pull requests, applying configuration fixes or PR actions as approved.                                                              |
| [Set-Up CI](./plugins/set-up-ci/README.md)                           | `/set-up-ci`                                          | Create GitHub Actions CI and matching Makefile targets, or optimize existing workflows with path filters, concurrency groups and job timeouts.                                                 |
| [Set-Up Secret Scanning](./plugins/set-up-secret-scanning/README.md) | `/set-up-secret-scanning`                             | Set up secret scanning with gitleaks and TruffleHog GitHub Actions workflows and optional gitleaks configuration.                                                                              |
| [Upgrade Everything](./plugins/upgrade-everything/README.md)         | `/upgrade-everything`                                 | Assess every version reference in a repository, evaluate available upgrades with repo-specific risk and reward, and present selectable upgrade options.                                        |
| [Set-Up Installers](./plugins/set-up-installers/README.md)           | `/set-up-installers`                                  | Set up installer and distribution methods for Go, Swift, Rust and Zig projects, configure GoReleaser publishing, and write or update Homebrew formulae.                                        |

**External tools:**

- _Monitor PR:_ [`gh`](https://cli.github.com/) and [`jq`](https://jqlang.org/) (both required; the skill reads check, review, and merge state over the GitHub API and pipes paginated review JSON through `jq`)
- _Pin Everything:_ [`gh`](https://cli.github.com/), [`jq`](https://jqlang.org/); optional [`corepack`](https://github.com/nodejs/corepack) (only when pinning Yarn or pnpm) and [`reuse`](https://reuse.software/) (only in REUSE-licensed repos)
- _Dependabot configuration:_ [`gh`](https://cli.github.com/) and [`jq`](https://jqlang.org/) (reads repository settings, labels, alerts, and Dependabot secrets); optional [`uv`](https://docs.astral.sh/uv/) for schema validation with `check-jsonschema`
- _Set-Up Installers:_ [`gh`](https://cli.github.com/) to detect the repository owner and probe for a `homebrew-tap` repo
- _Dependabot PR triage:_ [`gh`](https://cli.github.com/) and [`jq`](https://jqlang.org/) (both required; the bundled script reads PRs, comparisons, and alerts over the GitHub API and summarizes them with `jq`)
- _Set-Up Installers:_ authenticated [`gh`](https://cli.github.com/) for GoReleaser publishing; optional [`goreleaser`](https://goreleaser.com/) for configuration checks; [Homebrew](https://brew.sh/) for formula validation

### Agents

| Plugin                                                             | Trigger                  | What it does                                                                                                                                             |
| ------------------------------------------------------------------ | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Clean Up Agent Config](./plugins/clean-up-agent-config/README.md) | `/clean-up-agent-config` | Review and reorganize AI coding agent configuration and instruction files across Claude Code, Codex, and Copilot.                                        |
| [Create Plugin](./plugins/create-plugin/README.md)                 | `/create-plugin`         | Guide for creating new plugins in this repository with consistent structure and conventions.                                                             |
| [Push Notification](./plugins/push-notification/README.md)         | `/push-notification`     | Send push notifications through ntfy when work finishes or needs a decision, on request or from another skill, including from remote and cloud sessions. |

**External tools:**

- _Push Notification:_ [`curl`](https://curl.se/) 7.76.0 or newer, [`jq`](https://jqlang.org/), and an [ntfy](https://ntfy.sh) topic on ntfy.sh or a self-hosted server

## Hooks

Hooks are event-driven; they have no slash-command trigger.

| Plugin                                       | What it does                                                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| [Notify (macOS)](./plugins/notify/README.md) | Sends macOS notifications when Claude Code or Codex CLI finishes a task or needs your attention. |

**External tools:**

- _Notify:_ [`alerter`](https://github.com/vjeantet/alerter). Install via [Homebrew](https://brew.sh): `brew install vjeantet/tap/alerter`

## Using with Codex CLI

This repository works as a native [Codex CLI](https://developers.openai.com/codex/cli) plugin marketplace. Codex reads the generated `.agents/plugins/marketplace.json`, which points at committed plugin roots under `dist/codex/plugins/`. Those generated roots mirror the canonical `plugins/*` directories and copy every `SKILL.md` unchanged, so Codex routes on the same skill descriptions as Claude Code.

For per-plugin metadata Codex prefers `.codex-plugin/plugin.json` when present and falls back to `.claude-plugin/plugin.json` otherwise. Hook registration requires a `.codex-plugin/plugin.json` with a non-empty `hooks` path (for example `"hooks": "./hooks/hooks.json"`); this lets hook plugins point Codex at a Codex-compatible hook file. Codex exposes `PLUGIN_ROOT` to plugin-bundled hook commands, plus `CLAUDE_PLUGIN_ROOT` for compatibility with existing Claude Code plugins.

### Installing and managing plugins

Registering the marketplace makes its plugins available without installing any of them. Install each plugin you want by name, qualified with the marketplace name `agent-harness-plugins`:

```bash
codex plugin marketplace add cboone/agent-harness-plugins
codex plugin list --marketplace agent-harness-plugins
codex plugin add commit@agent-harness-plugins
codex plugin add pr --marketplace agent-harness-plugins
```

`codex plugin marketplace add` also accepts a Git ref (`cboone/agent-harness-plugins@main`, or `--ref`) and a local path, such as a clone of this repository.

Start a new Codex session after installing so it loads the new skills. Mention a skill with `$commit`, or choose it from `/skills`. Codex also selects a skill on its own when a request matches the skill's description. The `Trigger` column in the tables above shows the Claude Code slash-command form.

Some workflow skills invoke other skills; for example, `pr` invokes `lint-and-fix`. Each such skill lists them in the `## Skill dependencies` section of its `SKILL.md`: install its required skills for the workflow to complete, and its optional skills for the steps that use them.

List installed plugins, refresh them, and remove them:

```bash
codex plugin list
codex plugin marketplace upgrade agent-harness-plugins
codex plugin remove commit@agent-harness-plugins
codex plugin marketplace remove agent-harness-plugins
```

`codex plugin marketplace upgrade` refreshes a Git-backed marketplace and the installed plugins it provides, including files that changed without a version change. Omit the name to refresh every Git-backed marketplace. `upgrade` and `marketplace remove` take the marketplace name, not the `owner/repo` source used by `add`.

`upgrade` does not refresh a local-path marketplace. After pulling changes into a local clone, run `codex plugin add` again for each installed plugin to replace its cached copy, then start a new session.

When changing plugin metadata, skills, hooks, scripts, or references in this repository, regenerate the Codex marketplace with `bin/build-codex-marketplace` and commit `.agents/plugins/marketplace.json` plus `dist/codex/`.

### Reviewing and trusting hooks

Plugin hooks need no feature flag, but Codex runs them only after you review and trust them, and installing a plugin does not trust its hooks. After installing `notify`, open `/hooks` in a Codex session, review the plugin's hooks, and trust them. Codex records trust against each hook definition's hash, so when an upgrade changes a hook, Codex skips that hook until you review and trust it again.

### Troubleshooting

- **`codex plugin add` cannot find a plugin:** confirm the marketplace name with `codex plugin marketplace list` and the plugin name with `codex plugin list --marketplace agent-harness-plugins`.
- **An installed skill does not appear:** confirm that `codex plugin list` shows the plugin as installed, start a new session, and check `/skills`.
- **Installed files are out of date:** run `codex plugin marketplace upgrade agent-harness-plugins` for a Git-backed marketplace, or `codex plugin add` again for a local-path one.
- **A hook does not run:** open `/hooks`, then review and trust it, including after an upgrade that changed it.

### Codex CLI known limitations

- **Skill invocations are written in Claude Code syntax.** The catalog's triggers, skill prose, and generated worktree prompts write invocations as `/name`. In Codex, use `$name` or `/skills` instead. Correcting them is [milestone 3][codex-milestone-3] of the Codex roadmap.
- **Workflow chains are written for Claude Code tools.** Skills such as `pr`, `monitor-pr:monitor`, and `bootstrap-project` invoke other skills and ask structured questions through Claude Code tool names, so Codex has to translate those steps. Applying the shared adapter conventions is [milestone 2][codex-milestone-2] for the Git and review chain and [milestone 3][codex-milestone-3] for the rest of the catalog.
- **`${CLAUDE_PLUGIN_ROOT}` is substituted only in hook commands.** Codex exposes the variable to plugin-bundled hook commands, but does not substitute it in skill bodies the way Claude Code does. The bundled script paths in `/workmux:start-issue`, `/workmux:create-worktree`, `/monitor-pr:monitor`, `/publish-report-board`, and `/monitor-pr:resolve-copilot-feedback` therefore arrive unsubstituted. Each of those skills carries a documented fallback that locates the script by glob, so they stay usable at the cost of an extra search step. Package-relative helper resolution is [milestone 3][codex-milestone-3].
- **Installed plugin READMEs have broken links.** An installed plugin's links to this README and to sibling plugins resolve to paths that do not exist in the Codex plugin cache. Read plugin documentation on GitHub until [milestone 3][codex-milestone-3] corrects them.
- **`notify` covers three Codex events.** On Codex, `notify` wires `Stop` for completion, `UserPromptSubmit` to reset completion deduplication, and `PreToolUse` for the `request_user_input` question tool. `PermissionRequest` is deliberately left unwired: it runs before Codex's automatic approval review decides whether to prompt you, so a notification there would announce decisions that need no response. For approval and plan prompts, enable Codex's built-in terminal notifications as the [`notify` plugin README](./plugins/notify/README.md) describes. Reassessing the other lifecycle events is [milestone 3][codex-milestone-3].
- **End-to-end verification is partial.** Linux, multiple cached plugin versions, paths containing spaces, restricted destinations, and complete hook payload coverage are not yet verified; that is [milestone 4][codex-milestone-4].
- **No custom prompts shipped.** Codex's `~/.codex/prompts/` mechanism is officially deprecated in favor of skills. This repository ships skills (and hooks), not prompts.

[codex-milestone-2]: ./docs/plans/todo/2026-09-15-codex-consumption-improvements.md#milestone-2-prove-the-design-on-the-git-and-review-chain
[codex-milestone-3]: ./docs/plans/todo/2026-09-15-codex-consumption-improvements.md#milestone-3-apply-the-design-across-the-catalog
[codex-milestone-4]: ./docs/plans/todo/2026-09-15-codex-consumption-improvements.md#milestone-4-verify-the-complete-distribution

## License

[MIT License](./LICENSE). TL;DR: Do whatever you want with this software, just keep the copyright notice included. The authors aren't liable if something goes wrong.
