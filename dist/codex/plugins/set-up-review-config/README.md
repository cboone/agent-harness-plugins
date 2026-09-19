# Set-Up Review Config

Install style-guide review checklists as a Copilot code-review skill, with matching AGENTS.md review rules and a REVIEW.md, so Copilot, Codex, and Claude Code Review apply the same guidance.

**Type:** Skill
**Trigger:** `/set-up-review-config`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## Requirements

- **git**: Required. Detection reads `git ls-files`, and pinning reads the marketplace's current commit with `git ls-remote`.
- **Network access**: Optional. Without it, the installed checklists link to the style guides on `main` instead of a pinned commit, and a later run with network access pins them. `curl` is used to check that the bundled checklists match the marketplace.

## What It Does

The style guides in this marketplace shape code while an agent writes it. This skill carries them into automated pull request review, where each reviewer reads guidance from a different place:

- **Copilot code review** reads skills under `.github/skills/`, and always uses a skill directory named `code-review`. The skill installs `.github/skills/code-review/SKILL.md`, which routes each changed file to a condensed checklist in the same directory, one per detected style guide.
- **Codex cloud review** reads `## Code Review Rules` sections in `AGENTS.md`. The skill adds a short block there that maps checklist severities to Codex priorities.
- **Claude Code Review** reads the root `REVIEW.md`. The skill writes a block that defines what Important means, copies every installed checklist's Important rules, caps Nits at five per review, and suppresses new Nits after the first review.

Each checklist is written by hand beside its style guide, ranks the guide's rules as Important, Nits and Do not flag, and gives every rule a bold name, so review comments cite rules such as `write-go-code: Checked errors`. The installed copies link back to the full guide at a pinned commit.

Supported guides: Go, Lean, Lean tests, Bash, Zsh, Markdown and scrut tests. The skill also detects the checks CI already runs and the generated, lockfile and vendored paths to skip, and tells every reviewer not to repeat them.

Everything the skill writes sits in a managed block or a file marked as managed, so reruns replace only their own content. Rules and checks you add outside the blocks take precedence.

## Usage

```text
/set-up-review-config
/set-up-review-config --dry-run
```

`--dry-run` detects file types, CI checks and skip paths, and presents the plan without writing anything.

After the skill runs, commit on a branch and open a pull request: Copilot reads skills from a pull request's head branch, so that pull request is already reviewed with the new config.

## Examples

- "set up review config": detects file types and installs the review config
- "configure Copilot code review for this repo": same behavior
- "add a REVIEW.md": same behavior, including the Copilot skill and the `AGENTS.md` rules
- "is the review config current?": use `--dry-run` to compare the installed checklists with the bundled ones

## See Also

- [Set-Up Linters](../set-up-linters/README.md): configure the linters and formatters whose findings reviewers are told to skip
- [Refresh Project Scaffolding](../refresh-project-scaffolding/README.md): audit installed review config for drift
- [Resolve Copilot PR Feedback](../resolve-copilot-pr-feedback/README.md): process the review comments that follow
- [All plugins](../../../../README.md)
