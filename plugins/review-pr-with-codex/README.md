# Review PR with Codex

Have Codex review the current branch in focused aspects (code, error handling, tests, comments, types), each in its own read-only run, then merge the findings into one report with an action plan.

**Type:** Skill
**Trigger:** `/review-pr-with-codex`

## Installation

See the [marketplace install instructions](../../README.md#install).

## What It Does

A single general review spreads its attention across everything at once. This skill splits the review into focused aspects, each with its own instructions, runs them side by side with Codex as the reviewer, and merges what they find into one report. It is a counterpart to the `review-pr` command of Anthropic's `pr-review-toolkit`, whose six agents its aspects are adapted from, with Codex doing the reviewing.

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

- **In Codex CLI**, each aspect goes to its own Codex subagent. Every subagent's task carries its full instructions, so nothing needs adding to `~/.codex/config.toml`. If the session cannot spawn subagents, the aspects run one after another, and the report says so.
- **In Claude Code** (and OpenCode), each aspect is its own `codex exec` run, all in parallel, and the host agent merges the results.

### Read-only, and honest about failure

Every review aspect is read-only: in a `--sandbox read-only` Codex run, or under read-only instructions in a subagent. Either way, the skill measures the working tree before and after the review and reports any path that changed.

An aspect whose run failed, timed out, or returned nothing or something unparseable is reported as **failed**, never as clean. A reviewer that crashed and a reviewer that found nothing produce the same empty list unless something checks, and the bundled helper checks every signal: the exit status, the output file, its size, its schema, and that it names the right aspect and snapshot.

### Simplify

`simplify` is the one aspect that edits files. It runs last, alone, and only when every review aspect succeeded and none reported a Critical finding. Its changes are measured from the working tree, not taken from Codex's account, and listed in the report. Nothing is committed or pushed.

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

- [`codex`](https://github.com/openai/codex), authenticated. Install via Homebrew: `brew install codex`. Subagents in Codex CLI need its `multi_agent` feature, which is on by default as of `codex-cli` 0.162.1.
- `git` and [`jq`](https://jqlang.org/). The bundled helpers emit and validate JSON with `jq`.

## Usage

```text
/review-pr-with-codex [aspects...|all] [--base <ref>] [--model <model>] [--effort <level>]
```

| Option             | Description                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------- |
| `aspects...`       | Any of `code`, `errors`, `tests`, `comments`, `types`, `simplify`; named aspects always run |
| `all`              | Every aspect that applies to the change; the default                                        |
| `--base <ref>`     | Take the merge base with this ref instead of with the default branch                        |
| `--model <model>`  | Codex model for every aspect; default `gpt-6.1-sol`                                         |
| `--effort <level>` | Codex reasoning effort for every aspect; default `medium`                                   |

The model and effort are passed on each run, so your own Codex defaults stay as they are.

## Recommended Permissions

This skill runs git, its bundled helpers, and Codex. To allow them automatically in Claude Code, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

```json
{
  "permissions": {
    "allow": ["Bash(bash \"*/review-scope\")", "Bash(bash \"*/review-scope\" *)", "Bash(bash \"*/codex-aspects\" *)", "Bash(test -x *)", "Bash(mktemp -d*)", "Bash(git diff *)", "Bash(git rev-parse *)", "Bash(command -v codex)", "Bash(codex --version)"]
  }
}
```

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences. `codex-aspects run` starts the `codex exec` processes itself, so allowing the helper covers them.

## Examples

- "review pr with codex": every applicable aspect, then `simplify` if the review allows it
- "/review-pr-with-codex code errors": only the code and error-handling aspects
- "/review-pr-with-codex tests --effort high": the tests aspect at higher effort
- "/review-pr-with-codex --base release/2.0": review against a release branch

## Attribution

The aspect instructions, workflow and report format are adapted from Anthropic's [`pr-review-toolkit`](https://github.com/anthropics/claude-plugins-official), licensed under the Apache License 2.0. See [NOTICE](NOTICE) and [LICENSE-APACHE](LICENSE-APACHE). The rest of the plugin is MIT-licensed, like the repository.

## See Also

- [Review Until Clean](../review-until-clean/README.md): a fix loop with one general reviewer per round, run until the snapshot comes back clean
- [Review Branch](../review-branch/README.md): a summary and quality review of committed branch changes
- [Address Review](../address-review/README.md): work through the findings once they are saved to a review document
- [All plugins](../../README.md)
