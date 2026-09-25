# Review Until Clean

Run a read-only reviewer from another model family over every local change, fix the findings at or above a severity threshold, and repeat until the exact snapshot on disk comes back clean or a round limit stops the loop.

**Type:** Skill
**Trigger:** `/review-until-clean`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

Most automated review happens after a pull request opens, so every finding costs a push, a CI run, and a round trip. This skill moves that loop to your machine, before the push. It reviews, fixes, and re-reviews until the reviewer has nothing left to say about the code that is actually on disk.

The fixer half of that loop already existed in [Address Review](../address-review/README.md). What was missing was a reviewer, and a rule for when to stop that cannot be fooled.

### Four invariants

The loop is only worth running if a clean result means something. Four rules make it mean something.

1. **Every round reviews the whole scope.** Committed branch changes, staged changes, unstaged changes, and untracked files, every round. The common failure in an agent review loop is that the agent fixes a finding and the next round quietly reviews only its own patch, so the code the first round never reached is never reviewed at all.
1. **The reviewer is read-only.** Codex runs in a read-only sandbox, and Claude is never given `--fix`. The host agent owns every change, so nothing is modified by a process whose output you have not seen.
1. **Empty or unparseable output is not clean.** A reviewer that crashes, times out, returns nothing, or returns something that does not parse ends the run as `failed`. Silence is the same shape as success, and that is exactly the failure this rule exists to catch.
1. **A clean result is bound to a content snapshot.** The snapshot covers every file in scope by content. Any edit after the review invalidates the clean result, so a run cannot report clean for code that no longer exists.

### Model diversity

A reviewer from the same model family as the agent that wrote the code misses the same things it does. By default the skill picks the family the host is not: Codex when it runs under Claude Code, Claude when it runs under Codex CLI. Override with `--reviewer`.

### Findings you disagree with

A finding you decline is recorded in the ledger with its reason and carried forward. Later rounds match the reviewer's findings against those declines and mark them declined instead of asking again, which is what lets a run with a disputed finding still converge. A declined finding is excluded from the clean check and is never silently dropped, and a run that ends with declines reports `clean-with-declines`, not `clean`.

### What it reports

Each run keeps a ledger while it works and, when it finishes, saves it to `docs/reviews/<date>-<branch>-until-clean.md`. The run ends with a status line:

```text
Review-until-clean status: clean | clean-with-declines | decisions-needed | stopped | failed
```

Every status carries its coverage. A clean result that could not reach the untracked files in scope is reported as `clean, partial scope`, never as plain `clean`. One reviewer pass is a sample, not proof that the branch is defect-free, and the report says what was covered rather than claiming more.

The skill never pushes.

## Requirements

At least one reviewer backend:

- [`codex`](https://github.com/openai/codex), authenticated. Install via Homebrew: `brew install codex`
- [`claude`](https://code.claude.com/docs/en/overview), when the host is not Claude Code itself

Also required:

- `git`. The loop itself never pushes and never rewrites history, but it does commit: [Address Review](../address-review/README.md) does the fixing, and its default is to commit each round's changes locally. Your index is left alone apart from the optional `git add -N` described under [Usage](#usage). Computing the snapshot also writes unreferenced blob and tree objects into `.git/objects`, which `git gc` collects.
- [`jq`](https://jqlang.org/). The bundled scope helper emits JSON and will not run without it.

## Usage

```text
/review-until-clean [--reviewer <codex|claude>] [--base <ref>] [--effort <level>]
                    [--severity <important|nit>] [--max-rounds <n>] [--report-only] [--no-save]
```

| Option                              | Description                                                                                     |
| ----------------------------------- | ----------------------------------------------------------------------------------------------- |
| `--reviewer <codex\|claude>`        | Choose the backend instead of taking the model-diverse default                                  |
| `--base <ref>`                      | Take the merge base with this ref instead of with the default branch                            |
| `--effort <low\|medium\|high\|max>` | Effort for the Claude backend; the Codex backend takes its effort from your Codex configuration |
| `--severity <important\|nit>`       | Lowest severity the loop fixes; default `important`                                             |
| `--max-rounds <n>`                  | Cap the rounds; default 3                                                                       |
| `--report-only`                     | Run one round, write the ledger, change nothing                                                 |
| `--no-save`                         | Leave the ledger at its temporary path instead of saving it to `docs/reviews/`                  |

Each round asks you to confirm the item list before anything is edited, because [Address Review](../address-review/README.md) does the fixing and always confirms first. This is a gate you watch, not an unattended job.

When the Claude backend is selected and untracked files are in scope, the skill asks once whether to make them visible to the reviewer with `git add -N`, which records an intent to add without staging content. It restores the index with `git reset -- <paths>` afterward, touching only those paths. Declining is fine; the run then reports `partial scope`. The snapshot is computed from file content rather than from index state, so staging a file this way does not move it.

### As a pre-push hook

The skill is deliberately agent-invoked rather than a shipped git hook, because a hook adds latency to every push and one that fails open is worse than no hook at all. To wire one up yourself, have your `pre-push` hook ask before running, and run the skill through your agent's non-interactive mode.

## Recommended Permissions

This skill runs git and reviewer commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/review-scope\")", "Bash(bash \"*/review-scope\" *)", "Bash(test -x *)", "Bash(git rev-parse *)", "Bash(git merge-base *)", "Bash(git diff *)", "Bash(git status*)", "Bash(git ls-files *)", "Bash(git log *)", "Bash(git branch *)", "Bash(codex exec *)", "Bash(claude -p *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

The first two rules cover the bundled helper, which runs every round. `git add -N` and `git reset` are left out on purpose: the skill asks before touching the index, so approving those two each time is the point.

## Examples

- "review until clean": the default loop, using Codex under Claude Code
- "/review-until-clean --report-only": one round, a written ledger, nothing changed
- "/review-until-clean --reviewer claude --effort max": a Claude review at maximum effort instead
- "/review-until-clean --severity nit": fix the nits too, not just the Important findings
- "/review-until-clean --max-rounds 1": one review and one fix pass, then stop whatever the result

## See Also

- [Address Review](../address-review/README.md): the fixer this skill hands each round's findings to
- [Review Branch](../review-branch/README.md): a report on committed branch changes, with no fix pass and no loop
- [Plant Defects](../plant-defects/README.md): proving an instrument can fail, which is what this skill's empty-output rule is for
- [Set-Up Review Config](../set-up-review-config/README.md): the checklists the reviewers apply once they are installed
- [PR](../pr/README.md): what to run once the loop reports clean
- [All plugins](../../README.md)
