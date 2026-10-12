# Invocation

How each entry point runs an aspect, and how a finished aspect is told apart from one that failed silently. The `codex exec` rules follow the Codex backend of `review-until-clean`, whose `references/backends.md` records the measurements behind them.

## Every aspect meets the same contract

1. A review aspect runs without write access to the working tree.
1. It covers the whole scope that `review-scope` reported.
1. Its result is one JSON object matching `codex-aspects schema`, naming its aspect and the snapshot it reviewed.
1. **A completed aspect is distinguishable from one that did not finish**, by every signal the entry point offers. A missing, empty, unparseable or non-matching result is a failed aspect, never an empty findings list.

## The `codex exec` path

`codex-aspects run` builds this invocation for each aspect and runs them in parallel:

```bash
codex exec \
  --cd <repository root> \
  --sandbox read-only \
  --ephemeral \
  --model <model> \
  --config 'model_reasoning_effort="<effort>"' \
  --output-schema <out-dir>/schema.json \
  --output-last-message <out-dir>/<aspect>.json \
  "<rendered prompt>" < /dev/null
```

Each part is there for a reason:

- **Plain `codex exec`, never `codex exec review` or `codex review`.** The review subcommands cannot combine a custom prompt with `--base`, and they accept `--output-schema` and ignore it. Their output could not be validated, so a crash and a clean review would look alike. Do not switch to them as a simplification.
- **`< /dev/null`.** `codex exec` appends a non-terminal stdin to the prompt. An agent harness's stdin is a pipe that never closes, so without the redirect the run waits forever and never writes its output file.
- **`--sandbox read-only`** makes the read-only rule structural. `simplify` alone gets `workspace-write`, and the helper refuses to run it beside any other aspect.
- **`--ephemeral`** keeps each run from persisting a session.
- **`--model` and `--config model_reasoning_effort`** apply to that run only, so the user's Codex defaults are untouched.
- **`--output-schema` and `--output-last-message` point outside the working tree.** A file written inside it would join the scope under review and move the snapshot. The helper refuses an `--out-dir` inside the repository.

Stopping `codex-aspects run`, with TERM or by a failure partway through, stops every Codex run it started, so a `simplify` run cannot go on editing after the caller has measured its changes.

The prompt goes in as one argument because stdin must stay `/dev/null`. The helper refuses a prompt above 120,000 bytes, under Linux's per-argument limit; only the untracked files are listed one by one, since committed, staged and unstaged changes each take a single diff command, so a prompt that large means too many untracked files. Commit them, which moves them into a diff, or add the ones that are not part of the change to `.gitignore`.

### Signals

`codex-aspects run` checks each aspect in this order, and the first failure is its reason:

1. `codex` exited zero.
1. The output file exists. A run stopped early usually leaves none, but a failed run can leave a complete, valid file, which is why the exit status is checked first and the file never stands in for it.
1. The file is not empty. `jq .` exits 0 on an empty file, so emptiness is checked by size.
1. The file parses as JSON and holds exactly one value. jq reads a file as a stream and `jq -e` reports on the last value, so without this an invalid object followed by a valid one would pass every check after it.
1. It matches the schema.
1. Its `aspect` is the one requested, and its `reviewed` is the snapshot in the scope file.

An unauthenticated `codex` fails at step 1. Report it as an authentication problem in the aspect's notes, still as a failed aspect, and do not try to authenticate.

## The subagent path

This path is only for a session that is itself running on Codex, such as Codex CLI with `spawn_agent`. Another harness's subagents run its own models, so they would not be a Codex review. The parent session spawns one subagent per aspect, each given the rendered prompt as its task. The read-only rule is an instruction in that prompt rather than a sandbox, which is why step 5 of the workflow checks the tree afterwards for lasting changes. That check catches the writes that matter most, edits to the files under review, but not every write; see [Checking the tree](#checking-the-tree).

There is no process here, so there is no exit status and no output file of the subagent's own. The signals that remain are the reply itself and the schema:

1. Save the subagent's final reply verbatim. A subagent that ended without a reply has failed.
1. `codex-aspects validate` then applies checks 3 to 6 above to the saved reply.

Never transcribe a reply into the schema by hand. The subagent was asked for the JSON object and did not return it, which means it did not do what it was told, and its content is unknown.

Each subagent's task is complete on its own, so the skill needs no `[agents.<role>]` entries in the user's `~/.codex/config.toml`.

## Checking the tree

`review-scope` records `tree`, a content digest of every path git tracks or would track. `codex-aspects changes` diffs two of those trees, so it lists every path whose content, as Git would store it, changed between two scope reads, whichever bucket the path sits in, and marks those outside the first read's scope. Untracked files excluded by ignore rules are outside the digest, which matches the scope rule. A tracked file stays covered even when its path matches an ignore rule.

The comparison detects lasting changes to that stored content between two scans, and nothing more. It cannot see:

- a change only to the index, such as staging a file without editing it, because the tree is built from the content on disk;
- a write to an ignored, untracked file, because those are outside the digest;
- an edit reverted before the second scan, because only the two end states are compared.
- an edit that Git normalizes away, such as a line-ending change under text normalization or one a clean filter undoes, because the digest is built from the content Git would store, not the bytes on disk.

So an empty result means no lasting changes were found, not that nothing was written. On the `codex exec` path the read-only sandbox is what prevents writes, and the comparison is a second check. On the subagent path the comparison is the only check, with those blind spots.
