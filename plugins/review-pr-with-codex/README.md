# Review PR with Codex

Have Codex review the current branch in focused read-only aspects (code, error handling, tests, comments, types), then merge the findings into one report with an action plan.

**Type:** Skill
**Trigger:** `/review-pr-with-codex`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

This skill splits a review into focused aspects, each with its own instructions, runs them side by side with Codex as the reviewer, and merges what they find into one report. It is a Codex counterpart to the `review-pr` command of Anthropic's `pr-review-toolkit`, whose six agents its aspects are adapted from.

| Aspect     | Looks at                                                           | Runs when                            |
| ---------- | ------------------------------------------------------------------ | ------------------------------------ |
| `code`     | Project guidelines from `AGENTS.md` and `CLAUDE.md`, bugs, quality | Always                               |
| `errors`   | Silent failures, broad catches, unjustified fallbacks              | Error handling changed               |
| `tests`    | Behavioral coverage gaps and brittle tests                         | Tests or tested behavior changed     |
| `comments` | Comment and documentation accuracy, and comment rot                | Comments or docs added or changed    |
| `types`    | Invariants, encapsulation and enforcement in type design           | Types added or changed               |
| `simplify` | Clarity edits that keep behavior unchanged                         | Last, only when the review allows it |

The review covers committed changes since the merge base with the default branch, plus staged, unstaged and untracked files.

### Two entry points

- **In Codex CLI**, aspects run in batches within available subagent slots. Tasks carry their full instructions and need no additions to `~/.codex/config.toml`. If slots cannot be released or spawning fails, remaining aspects run sequentially or standalone. The report records actual settings and inherited-instruction limits.
- **In Claude Code**, each aspect is its own `codex exec` run, all in parallel, and the host agent merges the results.

### Read-only, and honest about failure

Review aspects use `--sandbox read-only` in standalone Codex runs or read-only instructions in subagents. The skill compares disk content before and after review and reports changed paths. A separate snapshot comparison invalidates results after index-content, HEAD, base or bucket changes. Disk comparison misses writes to ignored untracked files, reverted edits and changes Git normalizes to identical content.

An aspect whose run failed, timed out, or returned nothing or something unparseable is reported as **failed**, never as clean. A reviewer that crashed and one that found nothing produce the same empty list unless something checks. The standalone helper checks every signal: the exit status, the output file, its size, its schema, and that it names the right aspect and snapshot.

### Simplify

`simplify` edits files last and alone. It requires explicit selection alongside review aspects, successful selected reviews, no Critical findings and an unchanged review scope. Omitted arguments and `all` never authorize edits. After edits, run relevant project checks and a final read-only review; actionable findings refer to the final snapshot. The report lists measured working-tree changes rather than Codex's account. Nothing is committed or pushed.

### The report

```text
# PR review summary

## Critical issues (N found)
- [aspect]: Issue. [file:line]

## Important issues (N found)
## Suggestions (N found)
## Strengths
## Aspect runs
## Simplify changes
## Recommended action
```

## Requirements

- [`codex`](https://github.com/openai/codex), authenticated. Install via Homebrew: `brew install codex`. Codex CLI subagents require the `multi_agent` feature.
- `git`, `ps`, `pgrep` and [`jq`](https://jqlang.org/). Process inspection verifies cancelled descendants stopped; a sandbox denial means incomplete cancellation. Helpers emit and validate JSON with `jq`.

## Usage

```text
/review-pr-with-codex [aspects...|all] [--base <ref>] [--model <model>] [--effort <level>] [--window <tokens>]
```

| Option              | Description                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------- |
| `aspects...`        | Any of `code`, `errors`, `tests`, `comments`, `types`, `simplify`; named aspects always run |
| `all`               | Every aspect that applies to the change; the default                                        |
| `--base <ref>`      | Take the merge base with this ref instead of with the default branch                        |
| `--model <model>`   | Codex model for every aspect; default `gpt-6.1-sol`                                         |
| `--effort <level>`  | Codex reasoning effort for every aspect; default `xhigh`                                    |
| `--window <tokens>` | Codex context window (`model_context_window`) for every aspect; default `872000`            |

The model, effort and window are passed on each run, so your own Codex defaults stay as they are and never fill in for an omitted option.

## Recommended Permissions

This skill runs git, its bundled helpers, and Codex. To allow them automatically in Claude Code, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/review-scope\")", "Bash(bash \"*/review-scope\" *)", "Bash(bash \"*/codex-aspects\" *)", "Bash(test -x *)", "Bash(mktemp -d*)", "Bash(mkdir *)", "Bash(git diff *)", "Bash(git rev-parse *)", "Bash(command -v codex)", "Bash(codex --version)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences. `codex-aspects run` starts the `codex exec` processes itself, so allowing the helper covers them. Removing the temporary directory with `rm -rf` is left out on purpose: a rule broad enough to match it would also allow deleting anything, so approve that one command when it runs.

## Examples

- "review pr with codex": every applicable read-only review aspect
- "/review-pr-with-codex all simplify": review, then explicitly authorized simplification, validation and final review
- "/review-pr-with-codex code errors": only the code and error-handling aspects
- "/review-pr-with-codex tests --effort medium": the tests aspect at lower effort, for a faster run
- "/review-pr-with-codex --base release/2.0": review against a release branch

## Attribution

The aspect instructions, workflow and report format are adapted from Anthropic's [`pr-review-toolkit`](https://github.com/anthropics/claude-plugins-official), licensed under the Apache License 2.0. See [NOTICE](NOTICE) and [LICENSE-APACHE](LICENSE-APACHE). The rest of the plugin is MIT-licensed, like the repository.

## See Also

- [Review Until Clean](../review-until-clean/README.md): a fix loop around any one reviewer, this skill included, run until the snapshot comes back clean
- [Review Branch](../review-branch/README.md): a summary and quality review of committed branch changes
- [Address Review](../address-review/README.md): work through the findings once they are saved to a review document
- [All plugins](../../README.md)
