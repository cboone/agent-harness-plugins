# Review Until Clean

Run a reviewer of your choice (a skill, slash command or CLI) over every local change, fix its findings at or above a severity threshold, and repeat until the exact snapshot on disk comes back clean or a round limit stops the loop.

**Type:** Skill
**Trigger:** `/review-until-clean`

## Installation

See the [marketplace install instructions](../../../../README.md#install).

## What It Does

Most automated review happens after a pull request opens, so every finding costs a push, a CI run, and a round trip. This skill moves that loop to your machine, before the push. It reviews, fixes, and re-reviews until the reviewer has nothing left to say about the code that is actually on disk.

The fixer half of that loop already existed in [Address Review](../address-review/README.md). What was missing was a reviewer, and a rule for when to stop that cannot be fooled.

### Four invariants

The loop is only worth running if a clean result means something. Four rules make it mean something.

1. **Every round reviews the whole scope.** Committed branch changes, staged changes, unstaged changes, and untracked files, every round. The common failure in an agent review loop is that the agent fixes a finding and the next round quietly reviews only its own patch, so the code the first round never reached is never reviewed at all.
1. **The loop knows each round's mode.** A reviewer either reports findings, which the loop fixes, or edits the code itself. The loop tells which by checking the snapshot as the reviewer returns. A round in which the reviewer changed the code is never clean; the next round reviews what it left.
1. **A run that does not finish is never clean.** A CLI must exit 0 with stdout that holds a non-whitespace character, and a skill or command must report that it completed. A reviewer that crashes, times out, returns nothing, or stops partway ends the run as `failed`. Silence is the same shape as success, and that is exactly the failure this rule exists to catch.
1. **A clean result is bound to a content snapshot.** The snapshot covers disk and index content, bucket membership, HEAD and the resolved base. Any edit after the review invalidates the clean result, so a run cannot report clean for code that no longer exists.

### Choosing a reviewer

The loop works with any reviewer and knows nothing about how any of them works. `--reviewer` takes what you would type yourself: a skill or slash command such as `/pr-review-toolkit:review-pr`, `/review-pr-with-codex` or `/simplify`, or a shell command such as `coderabbit review --agent --fresh`. The reviewer's own options go inside the value, as in `--reviewer "/review-pr-with-codex --effort high"`. One run uses one reviewer; to combine reviewers, run the loop once for each.

The loop reads what the reviewer returns and transcribes its findings into one ledger format, mapping its severities into Critical, Important and Nit. A finding with no severity counts as Important, so a reviewer that does not grade its findings still blocks a clean result at the default threshold, but not at `critical`.

Without `--reviewer`, the skill uses the reviewer your repository's `AGENTS.md` or `CLAUDE.md` names for `review-until-clean`, for example:

```text
review-until-clean reviewer: /pr-review-toolkit:review-pr
```

It shows the named reviewer and the file it came from, and asks you to confirm it once before the first round, because those files can be part of the change under review. If none is named, it asks once which to use. A run where no one can answer, such as a pre-push hook, needs `--reviewer`.

A reviewer chooses its own diff, so the loop cannot make it read all four buckets. It offers once per run to make untracked files visible with `git add -N`, then compares what the reviewer reports it read against the scope. A round's coverage is `full`, `partial`, or `unverified` when the reviewer does not say.

### Findings you disagree with

A finding you decline is recorded in the ledger with its reason and carried forward. Later rounds match the reviewer's findings against those declines and mark them declined instead of asking again, which is what lets a run with a disputed finding still converge. A declined finding is excluded from the clean check and is never silently dropped. A clean run that relies on declines at or above the threshold reports `clean-with-declines at <threshold>`; declines below the threshold do not change the status.

### What it reports

Each run keeps a ledger while it works and, when it finishes, saves it to `docs/reviews/<date>-<branch>-until-clean.md`. The run ends with a status line:

```text
Review-until-clean status: clean | clean-with-declines | decisions-needed | stopped | failed | no-op
```

Every status carries its coverage, and every clean result names the threshold. A clean result that left part of the scope out is reported as `clean at <threshold>, partial scope`, and one whose reviewer did not say what it read as `clean at <threshold>, coverage unverified`, never as plain `clean`. One reviewer pass is a sample, not proof that the branch is defect-free, and the report says what was covered rather than claiming more.

A reviewer's output varies between runs over identical code, so a round that finds nothing is not proof that there was nothing to find. `--confirm-clean` requires two consecutive clean rounds instead of one: the first clean round does not end the run, a second review runs over the same snapshot with no fix pass in between, and only two in a row satisfy the clean rule. Any change to the snapshot resets the pair, and if the confirming round turns up an undeclined finding at or above `--severity`, the count starts over after it is fixed. Findings below the threshold and carried declines do not block the confirmation, exactly as they do not block a clean round. The confirming round uses a round from `--max-rounds` when one is left. When the first clean round used the last one, the confirming round runs anyway as one round past the cap, purely as a review: if it finds something blocking then, nothing is fixed and the run ends `stopped`.

The skill never pushes.

## Requirements

A reviewer: any skill, slash command or CLI that reviews code, installed and authenticated.

Also required:

- `git`. The loop itself never pushes and never rewrites history, but it does commit: [Address Review](../address-review/README.md) does the fixing, and its default is to commit each round's changes locally. Your index is left alone apart from the optional `git add -N` described under [Usage](#usage). The loop relies on your reviewer not to push or rewrite history either; it checks remote refs and `HEAD` ancestry around each review, which catches the common cases but not every one. Computing the snapshot also writes unreferenced blob and tree objects into `.git/objects`, which `git gc` collects.
- [`jq`](https://jqlang.org/). The bundled scope helper emits JSON and will not run without it.

## Usage

```text
/review-until-clean [--reviewer <command>] [--base <ref>] [--severity <critical|important|nit>]
                    [--max-rounds <n>] [--confirm-clean] [--report-only] [--no-save]
```

| Option                                  | Description                                                                                                                                                                                                    |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--reviewer <command>`                  | The reviewer, as you would type it: a skill or slash command, or a shell command. Quote a value with spaces; its own options go inside it                                                                      |
| `--base <ref>`                          | Take the merge base with this ref instead of with the default branch                                                                                                                                           |
| `--severity <critical\|important\|nit>` | Lowest severity the loop fixes; default `important`                                                                                                                                                            |
| `--max-rounds <n>`                      | Cap the rounds; default 3                                                                                                                                                                                      |
| `--confirm-clean`                       | Require two consecutive clean rounds over the same snapshot rather than one                                                                                                                                    |
| `--report-only`                         | Run one round and write the ledger without a fix pass; with `--confirm-clean`, also run the confirming round when the first is clean. A reviewer that edits still edits, and its changes are kept and reported |
| `--no-save`                             | Leave the ledger at its temporary path instead of saving it to `docs/reviews/`                                                                                                                                 |

Before each fix pass, [Address Review](../address-review/README.md), which does the fixing, asks you to confirm the item list. A reviewer that edits, such as `/simplify`, changes the tree itself while it runs, before any such confirmation and under its own approval behavior; that round's changes are recorded in the ledger and reviewed by the next round when the round budget allows. This is a gate you watch, not an unattended job.

When untracked files are in scope, the skill asks once whether to make them visible to the reviewer with `git add -N`, which records an intent to add without staging content. It does this before capturing the round's snapshot and keeps those entries through the validity checks and any confirming round. Afterward it restores only the entries this run added, leaving pre-existing and concurrently staged entries alone. Declining is fine; the untracked bucket is then recorded as not covered, unless the reviewer's report shows it read those files anyway. Staging and intent-to-add move the snapshot, because the index is review input.

The skill does not sandbox the reviewer. A reviewer skill runs with your agent's own tools and a shell reviewer runs as you, so either can read any file you can, including the target of an untracked symlink. The skill keeps a symlink's target out of what it hands the reviewer and out of the ledger, but cannot stop a reviewer that opens it on its own.

### Severity thresholds

The order is Critical > Important > Nit. The default `important` fixes Critical and Important findings; `nit` fixes all three. `--severity critical` fixes only Critical findings and reports `clean at critical` when none remain undeclined. Important and Nit findings stay printed, recorded and open, and are skipped by the fixer. An unlabelled finding maps to Important and therefore does not block at `critical`.

Critical, blocker and P0 map to Critical. High, major, important, error, P1 and "must fix" remain Important; existing Nit mappings are unchanged. The ledger records the selected threshold, and every clean result names it alongside its coverage and any confirmation or decline qualifiers. The same threshold applies to `--report-only` and both rounds of `--confirm-clean`; failures, edit rounds and invalid snapshots still cannot be clean.

### As a pre-push hook

The skill is deliberately agent-invoked rather than a shipped git hook, because a hook adds latency to every push and one that fails open is worse than no hook at all. To wire one up yourself, have your `pre-push` hook ask before running, and run the skill through your agent's non-interactive mode with an explicit `--reviewer`: a reviewer named only in agent instructions needs a confirmation that a non-interactive run cannot give, so without `--reviewer` the run ends `failed`.

## Recommended Permissions

This skill runs git commands, and your reviewer's own commands, that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/review-scope\")", "Bash(bash \"*/review-scope\" *)", "Bash(test -x *)", "Bash(command -v *)", "Bash(mktemp *)", "Bash(readlink *)", "Bash(git rev-parse *)", "Bash(git merge-base *)", "Bash(git diff *)", "Bash(git status*)", "Bash(git ls-files *)", "Bash(git log *)", "Bash(git branch *)", "Bash(git diff-tree *)", "Bash(git for-each-ref *)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.

The first two rules cover the bundled helper, which runs at least twice every round. `Bash(command -v *)` covers the availability check run on a shell reviewer's first word before round 1. `Bash(mktemp *)` covers the capture directory made for a shell reviewer, and `Bash(readlink *)` covers the untracked-symlink check. The remaining commands the skill and its references run are each either in the list or left out on purpose, as the next sentences say. A shell reviewer runs inside a wrapper script, `bash -e -o pipefail <temporary file>`, so a rule for the reviewer's own command, such as `Bash(coderabbit review *)`, never matches it, and each round asks you to approve the wrapper; that approval is where you see what is about to run. `git add -N` and `git reset` are left out on purpose: the skill asks before touching the index, so approving those two each time is the point. So are `mkdir`, `mv` and `rm`, which write the ledger and remove the capture directory.

## Examples

- "review until clean": the default loop, with the reviewer your agent config names, or asked once
- "/review-until-clean --reviewer /pr-review-toolkit:review-pr": the toolkit's review each round
- "/review-until-clean --reviewer '/review-pr-with-codex --effort high'": a Codex review at high effort
- "/review-until-clean --reviewer 'coderabbit review --agent --fresh'": the CodeRabbit CLI
- "/review-until-clean --reviewer /simplify": a reviewer that edits, run until it leaves the tree unchanged
- "/review-until-clean --report-only": one round, a written ledger, nothing changed by the loop
- "/review-until-clean --severity critical": fix only Critical findings and leave lower-severity findings open
- "/review-until-clean --severity nit": fix the nits too, not just the Important findings
- "/review-until-clean --max-rounds 1": one review and one fix pass, then stop whatever the result
- "/review-until-clean --confirm-clean": keep going after the first clean round until a second one confirms it

## See Also

- [Address Review](../address-review/README.md): the fixer this skill hands each round's findings to
- [Review Branch](../review-branch/README.md): a report on committed branch changes, with no fix pass and no loop
- [Plant Defects](../plant-defects/README.md): proving an instrument can fail, which is what this skill's empty-output rule is for
- [Review PR with Codex](../review-pr-with-codex/README.md): a Codex review in focused aspects, usable as this loop's reviewer
- [Set-Up Review Config](../set-up-review-config/README.md): the checklists the reviewers apply once they are installed
- [PR](../pr/README.md): what to run once the loop reports clean
- [All plugins](../../../../README.md)
