# Checked gate runner

Use `checked-gate` for an ordered group of checks followed by one dependent
action. It extends the checked plant runner's execution core. It does not
activate a hook or enforce use outside its own invocation. Commands are trusted
local code, not sandboxed. Secrets belong in environment variables; captured
output is included in the receipt.

## Manifest

```json
{
  "checks": [
    {
      "argv": ["git", "diff", "--check"],
      "expected_exit": 0,
      "timeout": 60,
      "inputs": ["HEAD", "tree", "index", "package.json"]
    },
    {
      "pipeline": [["make", "lint"], ["tee", "/tmp/owned-lint.log"]],
      "inputs": ["tree"]
    }
  ],
  "action": ["git", "commit", "-S", "-m", "fix: validate the checked tree"],
  "action_timeout": 60
}
```

`checks` is a nonempty ordered array. Arguments may include empty strings; the
executable name must be nonempty. Each check declares either `argv` or `pipeline`, plus `inputs`;
`expected_exit` defaults to zero and accepts an integer process return code.
Negative codes denote signal termination; timeout or capture/cleanup failure
never passes merely because a return code matches. Check and action
timeouts default to 60 seconds and must be positive and at most 3600 seconds.
`pipeline` is an array of at least two argv arrays. Pipeline checks require
expected exit zero. Every stage must exit zero, and every stage exit, duration
and capture digest is retained. All checks are attempted in order, including after a failed check. Missing,
unrun, timed out, truncated or incompletely cleaned commands cannot pass.
The action always requires exit zero and runs at most once.

Each check records its declared inputs at its start and end as journal facts.
Every boundary must match the initial inputs. A different or unknown boundary
refuses the action even if a later check restores the original inputs; all
checks are still attempted. Verification applies the same boundary rule.
These are boundary samples, not continuous observation inside an opaque argv.

HEAD and the entire working tree are always fingerprinted. `HEAD` and `tree`
are input labels; `index` additionally declares the index's tree and stage
entries. Other inputs name regular files relative to the checkout root, with
SHA-256 content and permission fingerprints. Symlinked declared inputs, missing
files and directories are refused by the shared regular-file reader.
Declare supporting scripts, configuration and fixtures that affect the check.
External tools and environment values are caller responsibilities.

The working tree ID comes from a private alternate Git index initialized from
HEAD, updated with tracked and unignored untracked files, then written as a Git
tree. The real index is not used to build that tree. Normal Git clean filters,
ignore rules and submodule representation apply. Declared `index` state includes
its tree, staged entries and status flags, not volatile index cache bytes. Ignored inputs
must be declared as files when they affect checks.

Each argv is an opaque program. The runner records its arguments verbatim and
uses its own exit status. This includes interpreters with `-c`: a program that
runs a failing command and then exits zero has reported zero. The runner neither
classifies interpreters nor injects strict-mode options into them. Each command
receives a temporary `PYTHONPYCACHEPREFIX` and `PYTHONDONTWRITEBYTECODE=1`;
pipeline stages inherit these settings.
Put each logical step in a separate check. Use staged `pipeline` argv for a
pipeline whose individual stage exits must gate the action. Reviewers can see
interpreter strings in the receipt and assess the steps they hide.

The runner connects pipeline stages concurrently, retaining bounded stdout and
stderr spools for every stage. All stages share the worker's owned process group;
the existing command supervisor holds that leader with `waitid(WNOWAIT)` until
cleanup is checked. An unrun, failed, timed out, truncated or incompletely
captured stage fails the pipeline. The first stage receives an empty stdin.

## Run

Resolve the helper from the loaded plugin, just as for `checked-plant`. Claude
can use `${CLAUDE_PLUGIN_ROOT}/scripts/checked-gate`; Codex uses the script
beside the loaded skill's plugin `scripts/` directory. Invoke it through uv:

```bash
uv run --script /absolute/plugin/scripts/checked-gate run \
  /absolute/manifest.json /absolute/owned-run --root /absolute/checkout
```

The output directory must not exist and must be outside the checkout. Its
`receipt.json` is published atomically through the same writer as
`checked-plant`. An initial incomplete receipt is replaced by the complete
result. A stopped process may leave the incomplete receipt, which cannot pass
verification. Capture is bounded to 1 MiB per stream, with owned spools,
process groups and bounded cleanup using `waitid(WNOWAIT)`.

The receipt records schema version and kind, manifest and its digest, every
check and action argv, exit, duration, SHA-256 digests of captured UTF-8 text and full bounded execution
result. Command rows share one constructor and schema, with explicit `not-run`,
`setup-error`, `exited` and `exit-unknown` states. An `exited` state records a
known process exit; timeout, capture and cleanup flags can still make it fail.
Unknown exits remain null and retain their cause; they are never passing evidence.
The runner appends every start, exit, bounded byte chunk, EOF, capture load,
cleanup, reap and failure to `facts.jsonl` as observed. The receipt embeds that
journal and is produced only by folding its facts; publication and loading
reject a projection that differs from its journal. Later failures only add
facts, retaining every observed start, exit, duration and byte. Worker response
validation failures cannot replace stage observations. Spool reads are checked
independently after observed bytes and exits have been recorded. Missing facts
stay explicitly unknown. The same strict JSON codec reads manifests, worker
responses, journals and receipts, rejecting exponent overflow and non-finite
numbers on input and output. It records HEAD, working tree, declared index and file fingerprints
before checks, after checks and after the action. The action is refused unless
all checks passed and pre-action fingerprints and manifest bytes still match.
A failing run exits nonzero, retaining whether the action was refused and why.
Action changes to HEAD and the tree are recorded separately; they do not
retroactively change the tree the checks verified.

Fingerprint comparison observes state at the boundaries. It is not a lock
against another process changing files after comparison, and does not detect a
change that is reverted before the next fingerprint. Run against an exclusively
owned checkout when a dependent action needs that guarantee.

## Verify and render

```bash
uv run --script /absolute/plugin/scripts/checked-gate verify \
  /absolute/owned-run/receipt.json --tree FULL_TREE_ID
uv run --script /absolute/plugin/scripts/checked-gate verify \
  /absolute/owned-run/receipt.json --head FULL_HEAD_ID
uv run --script /absolute/plugin/scripts/checked-gate render \
  /absolute/owned-run/receipt.json
```

`verify` returns zero only for a complete passing receipt whose checked tree
matches the supplied full tree ID, or whose checked HEAD matches the supplied
full commit ID, recorded before or after the action, whose commit tree equals
the checked tree. Use `--tree` when a commit action advances HEAD while preserving
the checked content. Missing, malformed, unknown-schema, failed, partial and
mismatched receipts return nonzero. Verification reads the receipt alone,
without rerunning commands or requiring the source checkout. Receipts are local
evidence, not signatures or protection against deliberate forgery.

`render` reads only the receipt and prints every check's recorded exit and
status, every pipeline stage's recorded exit, then the action's exit, status and refusal cause. Rendering identifies failed and unrun commands; it does not claim successful
verification.
No command is run by `verify` or `render`. Both accept only the known schema;
rendering accepts every well-formed execution state, while verification requires
passing, completed execution. The publisher refuses rows that bypass the shared
constructor. A contract suite exercises setup, spawn, timeout, truncation, capture,
cleanup and reap failures through publication, loading and rendering, and confirms
verification refuses each one.

The committed Scrut cases replay the failed apply/commit gate as separate checks,
staged pipeline failure, opaque interpreter exits,
tree and declared index changes, missing execution and the one-action success
case. Source plants exercise the verdict, pipeline verdict, absence of interpreter classification, tree, completeness
and verification boundaries through `checked-plant`.
