# Running a Skill Through `codex exec`

How to run a skill's read-only work through `codex exec` and check that it finished. Each consuming skill names its model, effort, context window, prompt and fallback.

## When to use it

Use the Codex path only when all of these hold:

- This session is not itself Codex. A Codex session takes the skill's fallback.
- The skill was not given `--no-codex`.
- `command -v codex` succeeds.
- With an output schema, `command -v jq` succeeds.
- When `TMPDIR` is set, `realpath "${TMPDIR}"` must be outside the working tree: neither the path `git rev-parse --show-toplevel` prints nor under it.

Otherwise, or when the run fails a completion check below, take the skill's fallback. Never try the Codex run a second time: a silent retry hides the failure and repeats the cost.

## The invocation

Make a capture directory outside the working tree, and note the path it prints:

```bash
mktemp -d "${TMPDIR:-/tmp}/codex-exec.XXXXXX"
```

Write the prompt to `<codex_tmp>/prompt.md` with the harness's file-writing tool, then run these lines from the repository root, with the printed path in place of `<codex_tmp>` and the skill's settings in place of `<model>`, `<effort>` and `<window>`:

```bash
tmp='<codex_tmp>'
if codex exec \
  --cd "$(git rev-parse --show-toplevel)" \
  --sandbox read-only \
  --ephemeral \
  --model '<model>' \
  --config 'model_reasoning_effort="<effort>"' \
  --config 'model_context_window=<window>' \
  --output-last-message "${tmp}/reply" \
  "$(cat "${tmp}/prompt.md")" \
  < /dev/null > "${tmp}/log" 2>&1; then
  codex_status=0
else
  codex_status=$?
fi
printf 'codex_status=%s\n' "${codex_status}"
```

A skill that ships an output schema adds `--output-schema <absolute path to the schema>` before `--output-last-message`.

Each part is there for a reason:

- **`--sandbox read-only`** makes the run unable to write, so the skill's read-only rule no longer rests on instructions alone. It also blocks network access; see [What the run cannot reach](#what-the-run-cannot-reach).
- **`--model` and both `--config` settings** apply to this run only. The skill's settings always win, an omitted one never falls back to the user's interactive Codex configuration, and that configuration stays unchanged.
- **`--ephemeral`** keeps the run from persisting a session.
- **`< /dev/null`.** `codex exec` appends a non-terminal stdin to the prompt. An agent harness's stdin is a pipe that never closes, so without the redirect the run waits forever and writes nothing.
- **The prompt from a file.** The prompt holds paths and arguments with quotes of their own; a file-writing tool takes it as data, so no quoting rule applies.
- **`codex_status`, not `status`.** zsh reserves `status` as a read-only variable, so assigning it fails and loses the exit status.
- **A long timeout.** Give the call the longest timeout the tool allows, or run it in the background and wait for it. A timeout is a failed run.

## The prompt

Point the prompt at the skill's own file so the run does not require the plugin to be installed in Codex:

```text
Follow the skill at <absolute path to this skill's SKILL.md>, reading its
references from the same directory, with these arguments: <arguments> --no-codex
Run it in this session. Do not hand it to `codex exec` or to a subagent.

<the skill's additions>
```

- **Always pass `--no-codex` and tell the run to do the work itself.** It reads the same `SKILL.md`; these instructions prevent it from starting another Codex run or its own fallback.
- **The Codex run starts at the repository root**, not in the caller's working directory, so pass every path root-relative. A path the calling session has already resolved is passed as a literal file name, and the skill names how the run must treat it, so the run does not expand it as a pattern again. Each skill says which arguments it passes; anything it does not name passes through unchanged.
- **Include the user's context as one plain sentence in the prompt**, such as that the scope is a fix for review feedback.

## What the run cannot reach

The read-only sandbox blocks network access, so a step that calls `gh` or another network service fails inside the run, and the run cannot ask the user anything. Before starting it, the calling session performs any such read or question the skill names, such as finding the base branch, writes the result into the capture directory or the prompt, and names it as data for the step that needs it.

## Completion checks

A run is finished only when every check passes, in this order. The first failure is the reason the report gives:

1. `codex_status` is 0.
1. `<codex_tmp>/reply` exists and holds at least one non-whitespace character. A run that exits 0 having written nothing is a failure, never a clean result.
1. With an output schema: the reply parses as exactly one JSON value (`jq -s 'length == 1' <reply>` prints `true`), and it matches the schema, by the check the skill names.
1. The reply has the shape the skill names for a finished run. A reply that is only an error, ends partway, asks a question, or says the skill could not run fails here.

Do not repair a reply that fails, and do not read it as prose instead: its content is unknown. Record the status and the last lines of `<codex_tmp>/log` in the report, then take the skill's fallback. An unauthenticated `codex` fails at check 1; report it as an authentication problem and do not try to authenticate.

Remove the capture directory once the reply and the log are reported.

## Reporting

Say in the skill's report which path ran: Codex, with the model, effort and window actually passed; or the fallback, with the failed check or the condition that ruled Codex out.
