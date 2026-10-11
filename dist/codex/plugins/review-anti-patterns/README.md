# Review Anti-Patterns

Review a branch or a fix diff, read-only, against a checklist of the defect patterns that most often survive local review and surface in later Copilot rounds, such as bypassable sanitizers, parallel paths left behind, and docs that disagree with the code.

**Type:** Skill
**Trigger:** `/review-anti-patterns`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

A general review asks whether a change is right. This skill asks narrower questions that a general review tends to skip: what the sibling of each handled case is and whether it behaves the same way, which other places do the same job and whether they changed too, and which documents describe what just changed. Those questions come from a review of 132 pull requests in which most Copilot findings after the first round were a sibling input form, a parallel path, or a document that the previous fix had left behind.

The checklist has thirteen patterns, grouped into code, agent prose and docs, so a change with no code skips the code items. Agent prose, such as skills, prompts and agent instruction files, is reviewed as a program: rule order, branches that end nowhere, rules that conflict, and commands that the permission block does not cover. Where an item depends on how a platform behaves, the skill runs the project's own read-only check, such as `actionlint` or a validate-only flag, and reports anything it could not check as unverified rather than passed.

It never edits. It returns findings in the same JSON shape as [Review Until Clean](../review-until-clean/README.md), each with the case that goes wrong and the evidence, followed by the siblings it examined, so a fix can cover the whole class at once.

## Usage

```text
/review-anti-patterns
/review-anti-patterns --range 4f2a9c1..HEAD
/review-anti-patterns --files src/redact.ts --severity important
```

| Option                        | Effect                                                                                                                                                        |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--range <rev-range>`         | Review this revision range. The default is the merge base with the default branch through the working tree, including staged, unstaged and untracked changes. |
| `--files <paths>`             | Limit the scope to these paths or globs.                                                                                                                      |
| `--severity <important\|nit>` | Lowest severity reported. The default, `nit`, reports everything.                                                                                             |

Two places it fits:

- **Before opening a pull request**, as a targeted re-review after the general review and its fixes.
- **On a fix for review feedback**, with `--range` set to the commits the fix added, before the fix is pushed. Fix code is new code, and it is where most later-round findings come from.

## Requirements

- A Git repository. The [GitHub CLI](https://cli.github.com/) finds the default branch and reads the pull request body when it is available; otherwise the skill falls back to the remote's `HEAD` ref.

## Recommended Permissions

This skill runs read-only Git and GitHub CLI commands to find its scope. To allow them without prompts, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(gh repo view *)", "Bash(gh pr view *)", "Bash(git symbolic-ref *)", "Bash(git merge-base *)", "Bash(git diff *)", "Bash(git log *)", "Bash(git ls-files *)", "Bash(git rev-parse *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. The mechanical checks run the project's own linters, validators and tests, which depend on the project.

## Examples

- "review anti-patterns on this branch": the whole branch, every applicable item
- "check the fix before pushing it": the fix commits only, with `--range`
- "did this sanitizer change miss a sibling form?": the sanitizer's file, with `--files`

## See Also

- [Review Until Clean](../review-until-clean/README.md): a looping review with fixes, from another model family
- [Resolve Copilot PR Feedback](../resolve-copilot-pr-feedback/README.md): fixes Copilot findings
- [Plant Defects](../plant-defects/README.md): proves a test can fail
- [All plugins](../../../../README.md)
