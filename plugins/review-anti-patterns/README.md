# Review Anti-Patterns

Review a branch or a fix diff, read-only, against a checklist of the defect patterns that most often survive local review and surface in later Copilot rounds, such as bypassable sanitizers, parallel paths left behind, and docs that disagree with the code.

**Type:** Skill
**Trigger:** `/review-anti-patterns`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

A general review asks whether a change is right. This skill asks narrower questions that a general review tends to skip: what the sibling of each handled case is and whether it behaves the same way, which other places do the same job and whether they changed too, and which documents describe what just changed. Those questions come from a review of 132 pull requests in which most Copilot findings after the first round were a sibling input form, a parallel path, or a document that the previous fix had left behind.

The checklist has thirteen patterns, and each names the kinds of files it applies to: code, agent prose or docs, so a change touching only docs skips what cannot apply there. Agent prose, such as skills, prompts and agent instruction files, is reviewed as a program: rule order, branches that end nowhere, rules that conflict, and commands that the permission block does not cover. Where an item depends on how a platform behaves, the skill runs a read-only check such as `actionlint` or a validate-only flag, runs project tests and scripts only when you pass `--run-checks`, and reports anything it could not check as unverified rather than passed.

It never edits. Nothing but its instructions enforces that unless you run it somewhere that cannot write, and `--run-checks` lets project code run, which can write; the report says which applied and lists anything a check left behind. It returns JSON whose findings have the same fields as [Review Until Clean](../review-until-clean/README.md)'s, each with the case that goes wrong and the evidence, plus whether the review covered the whole scope and what it left unverified. A plain-text report follows, naming the siblings examined for each finding, so a fix can cover the whole class at once.

It is built for your own changes in your own checkout: it trusts your git and SSH configuration and the repository's own tooling, and does not defend against a deliberately malicious diff. Review a contributor's pull request crafted to attack the reviewer with a sandboxed tool instead.

## Requirements

- A Git repository with an `origin` remote. The skill finds the default branch from `origin/HEAD`, falling back to the [GitHub CLI](https://cli.github.com/). The GitHub CLI also reads the open pull request's body; without it, the report says the body was not reviewed.

## Usage

```text
/review-anti-patterns
/review-anti-patterns --range 4f2a9c1..HEAD --run-checks
/review-anti-patterns --files src/redact.ts --severity important
```

| Option                        | Effect                                                                                                                                                                                          |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--range <rev-range>`         | Review this revision range, written with `..` or `...`. The default is the merge base with the default branch through the working tree, including staged, unstaged and untracked changes.       |
| `--files <paths>`             | Limit the scope to these paths or globs. The report lists the changed files this leaves out.                                                                                                    |
| `--severity <important\|nit>` | Lowest severity reported. The default, `nit`, reports everything.                                                                                                                               |
| `--run-checks`                | Also run checks that execute repository code: tests, Makefile targets and package scripts. Pass it only for code you trust, such as your own branch; the skill cannot tell from the repository. |

Two places it fits:

- **Before opening a pull request**, as a targeted re-review after the general review and its fixes.
- **On a fix for review feedback**, with `--range` set to the commits the fix added, before the fix is pushed. Fix code is new code, and it is where most later-round findings come from. Each file the fix touches is reviewed whole, because Copilot re-reviews the whole pull request every round.

## Recommended Permissions

This skill runs read-only Git and GitHub CLI commands to find its scope, every Git command in one hardened form that starts the same way, so one rule covers them. To allow them without prompts, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(git --no-pager -c core.fsmonitor=false *)", "Bash(ssh -G *)", "Bash(gh repo view *)", "Bash(gh pr list *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. The mechanical checks run the project's own linters, validators and tests, which depend on the project.

## Examples

- "review anti-patterns on this branch": the whole branch, every applicable item
- "check the fix before pushing it": the fix commits, with `--range`, and the files they touch
- "did this sanitizer change miss a sibling form?": the sanitizer's file, with `--files`

## See Also

- [Review Until Clean](../review-until-clean/README.md): a looping review with fixes, from another model family
- [Resolve Copilot PR Feedback](../monitor-pr/README.md#monitor-prresolve-copilot-feedback): fixes Copilot findings
- [Plant Defects](../plant-defects/README.md): proves a test can fail
- [All plugins](../../README.md)
