# Invocation

How each entry point runs an aspect, and how a finished aspect is told apart from one that failed silently. The `codex exec` rules follow the Codex backend of `review-until-clean`, whose `references/backends.md` records the measurements behind them.

## Every aspect meets the same contract

1. Review aspects must not write. Standalone runs use a read-only sandbox; native subagents rely on instructions and the documented end-state checks.
1. It covers the whole scope that `review-scope` reported.
1. Its result is one JSON object matching `codex-aspects schema`, naming its aspect and the snapshot it reviewed.
1. **A completed aspect is distinguishable from one that did not finish**, by every signal the entry point offers. A missing, empty, unparseable or non-matching result is a failed aspect, never an empty findings list.

## The `codex exec` path

`codex-aspects run` builds this invocation for each aspect and runs them in parallel:

```bash
codex exec \
  --cd <external temporary working directory> \
  --skip-git-repo-check \
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
- **External `--cd` and `--skip-git-repo-check`.** The helper rejects repository-local `TMPDIR` to keep its working directory and prompt artifacts external. This excludes current checkout instructions from initial project-instruction discovery. Global instructions and user configuration remain active. The prompt supplies historical guidance and absolute reads with `git -C`; keep the session directory outside the checkout. `simplify` receives `--add-dir <repository root>` for authorized edits.
- **`--sandbox read-only`** makes the read-only rule structural. `simplify` alone gets `workspace-write`, and the helper refuses to run it beside any other aspect, without passing the review gate, or when the scope changed after `--scope` was captured. The recheck runs immediately before launch but takes no lock, so a concurrent edit in that window is not prevented.
- **`--ephemeral`** keeps each run from persisting a session.
- **`--model` and `--config model_reasoning_effort`** apply to that run only, so the user's Codex defaults are untouched.
- **`--output-schema` and `--output-last-message` point outside the working tree.** A file written inside it would join the scope under review and move the snapshot. The helper refuses an `--out-dir` inside the repository.

Stopping `codex-aspects run` records observed descendants, sends TERM to them and each run, then polls for stopped or terminated state before collecting the runs. Polling is bounded; unobserved descendants and processes created during shutdown remain a limitation. If inspection is unavailable or a process remains active, cleanup exits with status `4` and retains its temporary directory. Do not measure final state or simplify until launched workers are known to have stopped. Failed or cancelled runs are incomplete even with valid output.

`codex-aspects` refuses to run from inside the repository under review, because the change could then rewrite the aspect instructions its own review runs with. Run the installed copy of the plugin. Untracked file names and symlink targets go into the prompt as JSON strings, so a crafted name cannot start a line of its own.

The prompt goes in as one argument, because stdin must stay `/dev/null`. The helper refuses a prompt above 120,000 bytes, under Linux's per-argument limit. Only untracked files are listed one by one; committed, staged and unstaged changes take one diff command each. To shrink a prompt that is too large, commit the untracked files, which moves them into a diff, or add the ones that are not part of the change to `.gitignore`.

### Signals

`codex-aspects run` checks each aspect in this order, and the first failure is its reason:

1. `codex` exited zero.
1. The output file exists. A failed run can still leave a complete, valid file, so the file never stands in for the exit status.
1. The file is not empty. `jq .` exits 0 on an empty file, so emptiness is checked by size.
1. The file parses as JSON and holds exactly one value. jq reads a file as a stream and `jq -e` reports on the last value, so without this an invalid object followed by a valid one would pass every check after it.
1. It matches the schema.
1. Its `aspect` is the one requested, and its `reviewed` is the snapshot in the scope file.

An unauthenticated `codex` fails at step 1. Report it as an authentication problem in the aspect's notes, still as a failed aspect, and do not try to authenticate.

## The subagent path

Use subagents only in a Codex session, such as Codex CLI with `spawn_agent`; other harnesses' subagents use their own models. Schedule within available slots and preserve completed results. When slots cannot be released, run queued aspects sequentially or standalone. Supply each task's full rendered prompt and use fresh context when supported, particularly for model and reasoning-effort overrides. Fresh context does not guarantee isolation from project instructions or permissions; disclose those limits and prefer standalone runs when changed instructions require isolation. Native read-only access relies on instructions, not a sandbox. Step 5 checks for lasting edits, with the limits in [Checking the tree](#checking-the-tree).

There is no process here, so there is no exit status and no output file of the subagent's own. The signals that remain are the reply itself and the schema:

1. Save the subagent's final reply verbatim. A subagent that ended without a reply has failed.
1. `codex-aspects validate` then applies checks 3 to 6 above to the saved reply.

Never transcribe a reply into the schema by hand. A subagent that did not return the JSON object it was asked for did not do what it was told, and its content is unknown.

On cancellation, stop and observe launched workers before measuring scope. If completion cannot be confirmed, report incomplete cancellation and skip simplification. Tasks are self-contained and need no `[agents.<role>]` entries in the user's `~/.codex/config.toml`.

## Checking the tree

`review-scope` records a full review-input `snapshot` and a separate `tree`, a content digest of every path git tracks or would track. `codex-aspects changes` diffs two of those trees. It lists every path whose content, as Git would store it, changed between the two scope reads, in any bucket, and marks the ones outside the first read's scope. Untracked files excluded by ignore rules are outside the digest, which matches the scope rule. A tracked file stays covered even when its path matches an ignore rule.

The comparison detects lasting changes to that stored content between two scans, and nothing more. It cannot see:

- a write to an ignored, untracked file, because those are outside the digest;
- an edit reverted before the second scan, because only the two end states are compared;
- an edit that Git normalizes away, such as a line-ending change under text normalization or one a clean filter undoes, because the digest is built from the content Git would store, not the bytes on disk.

Index content, HEAD, base-tip and bucket changes are detected separately by `scope_changed`, even when `changed` is empty. A changed snapshot invalidates findings and blocks edits. So an empty disk-change result means no lasting content changes were found, not that nothing was written. On the `codex exec` path the read-only sandbox is what prevents writes, and the comparison is a second check. On the subagent path the comparison is the only check, with those blind spots.

## Historical instruction discovery

The helper supplies one non-empty guide per relevant directory from the merge base, or HEAD when no base exists. Precedence is `AGENTS.override.md`, `AGENTS.md`, explicit `--guide-name` fallbacks, then `CLAUDE.md` for compatibility. Pass configured fallback basenames in their configured order; the helper does not inspect user configuration or credentials. It resolves historical relative symlinks, rejects cycles and links outside that tree, and never follows checkout symlinks. Treat changed instructions as review material.

External startup isolates initial checkout instruction discovery, not global policy, user configuration, plugins or tools that discover guidance independently. Native subagents inherit the host environment and cannot claim standalone isolation. Report these limits and verify stronger claims against the installed CLI and its rendered prompt.
