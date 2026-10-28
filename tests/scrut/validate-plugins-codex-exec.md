# Plugin validator: scripted codex exec runs

Tests for rule 23 of `bin/validate-plugins`, which requires every scripted
`codex exec` run in the catalog to pass `approval_policy="never"` and
`web_search="disabled"`, each as a `--config` or `-c` argument. Without the
first, the user's Codex configuration supplies the approval policy, and a run
can ask to leave its read-only sandbox; without the second, Codex's built-in web
search stays as that configuration sets it. The rule reads every run in a
shipped script and every run in a fenced Markdown block, through its last
backslash-continued line.

Every case runs the validator through `tests/fixtures/validate-plugin-fixture`,
which validates a disposable copy of the repository after one targeted
mutation. These cases have their own document, apart from
`validate-plugins-skills.md`, so neither outgrows its share of a CI job.

## Validator rejects runs without both settings

The fixture drops the approval setting from `codex-aspects` and the web search
setting from the fenced invocation documented by `review-pr-with-codex`. It also adds four runs. The first two are
each followed by another command holding the setting they lack: a run ends at
its first line without a trailing backslash, so that command does not count for
it. The third sets another approval policy, and the fourth, which starts with
`if !`, holds both settings only in its prompt.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" unpinned-codex-exec 2>&1
Codex skill inventory: * (glob)
::error::plugins/release/skills/release/SKILL.md:* runs codex exec without approval_policy="never"; pass --config 'approval_policy="never"' and --config 'web_search="disabled"' so it stays sandboxed with web search off (glob)
::error::plugins/release/skills/release/SKILL.md:* runs codex exec without web_search="disabled"; pass --config 'approval_policy="never"' and --config 'web_search="disabled"' so it stays sandboxed with web search off (glob)
::error::plugins/release/skills/release/SKILL.md:* runs codex exec without approval_policy="never"; pass --config 'approval_policy="never"' and --config 'web_search="disabled"' so it stays sandboxed with web search off (glob)
::error::plugins/release/skills/release/SKILL.md:* runs codex exec without approval_policy="never" and web_search="disabled"; pass --config 'approval_policy="never"' and --config 'web_search="disabled"' so it stays sandboxed with web search off (glob)
::error::plugins/review-pr-with-codex/scripts/codex-aspects:* runs codex exec without approval_policy="never"; pass --config 'approval_policy="never"' and --config 'web_search="disabled"' so it stays sandboxed with web search off (glob)
::error::plugins/review-pr-with-codex/skills/review-pr-with-codex/references/invocation.md:* runs codex exec without web_search="disabled"; pass --config 'approval_policy="never"' and --config 'web_search="disabled"' so it stays sandboxed with web search off (glob)
6 plugin validation error(s) found.
[1]
```

## Validator accepts prose, comments and both argument forms

Prose outside a fence and a comment inside one only name the command. A run
after `if !` passes both settings with escaped quotes, and another passes them
as `--config=value`.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" pinned-codex-exec-forms 2>&1
Codex skill inventory: * (glob)
All plugin validations passed.
```

## Validator fails when rule 23 cannot search or scan

A wrapper first on `PATH` makes the rule's own `grep` or `awk` call exit 2 and
runs the real tool for every other call. A failed search or scan must fail
validation, never count as finding no unpinned runs.

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" failed-codex-exec-search 2>&1
Codex skill inventory: * (glob)
::error::Rule 23 could not search plugins/ for codex exec runs
1 plugin validation error(s) found.
[1]
```

```scrut
$ "${VALIDATE_PLUGIN_FIXTURE_BIN}" failed-codex-exec-scan 2>&1
Codex skill inventory: * (glob)
::error::Rule 23 could not scan the codex exec runs it found
1 plugin validation error(s) found.
[1]
```
