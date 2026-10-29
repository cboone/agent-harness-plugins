# Bash empty lists

Every subject runs through `/bin/bash`, including on macOS where it is Bash
3.2. `make test-bash32` requires that version before running this document;
the ordinary suite also runs it on the host's native Bash.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Empty branch names and path segments produce no issue identities

```scrut
$ /bin/bash "${PR_BRANCH_ISSUES_BIN}" '' && /bin/bash "${PR_BRANCH_ISSUES_BIN}" / && echo checked
checked
```

## Populated branch segments retain their issue identities

```scrut
$ /bin/bash "${PR_BRANCH_ISSUES_BIN}" fix/433-434-empty-lists
433
434
```

## Cross-reference checking accepts no file arguments and no candidate files

```scrut
$ root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && mkdir "${root}/plugins" && cd "${root}" && /bin/bash "${CHECK_CROSS_REFERENCES_BIN}"
All skill cross-references resolve.
```

## The generator accepts no arguments and an empty catalog

Both outputs go into the testcase directory, away from the committed mirror.

```scrut
$ root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '{"name":"empty","plugins":[]}' > "${root}/catalog.json" && CLAUDE_MARKETPLACE="${root}/catalog.json" CODEX_MARKETPLACE="${root}/marketplace.json" CODEX_DIST_DIR="${root}/dist" /bin/bash "${BUILD_CODEX_MARKETPLACE_BIN}"
Built Codex marketplace at */marketplace.json (glob)
Built Codex plugin roots at */dist/plugins (glob)
```

## Report-board reaches usage with no arguments

Capture the status before selecting the first diagnostic line, so a pipeline
cannot hide an expansion failure.

```scrut
$ output="$(/bin/bash "${REPORT_BOARD_BIN}" 2>&1)"; result=$?; test "${result}" -eq 2 && printf '%s\n' "${output}" | head -1
report-board: a command is required
```

## Each report-board subcommand forwards an empty remaining argument list

```scrut
$ output="$(/bin/bash "${REPORT_BOARD_BIN}" validate 2>&1)"; result=$?; test "${result}" -eq 2 && printf '%s\n' "${output}" | head -1
report-board: validate takes one data file
```

```scrut
$ output="$(/bin/bash "${REPORT_BOARD_BIN}" render 2>&1)"; result=$?; test "${result}" -eq 2 && printf '%s\n' "${output}" | head -1
report-board: render takes a data file and an output path
```

```scrut
$ output="$(/bin/bash "${REPORT_BOARD_BIN}" extract 2>&1)"; result=$?; test "${result}" -eq 2 && printf '%s\n' "${output}" | head -1
report-board: extract takes one rendered page
```

```scrut
$ output="$(/bin/bash "${REPORT_BOARD_BIN}" compare 2>&1)"; result=$?; test "${result}" -eq 2 && printf '%s\n' "${output}" | head -1
report-board: compare takes the previous board and the current data
```

```scrut
$ output="$(/bin/bash "${REPORT_BOARD_BIN}" starter 2>&1)"; result=$?; test "${result}" -eq 2 && printf '%s\n' "${output}" | head -1
report-board: starter takes an output path
```

## The launcher accepts an empty fan-out list

```scrut
$ /bin/bash "${LAUNCH_WORKMUX_BIN}" --check-fan-out-branches && echo checked
checked
```

## The cross-reference fixture accepts no arguments

```scrut
$ root="$(/bin/bash "${CROSS_REFERENCE_FIXTURE_BIN}")" && test -d "${root}/plugins/demo" && echo created
created
```

## The GitHub fixture reports its own diagnostic with no arguments

```scrut
$ set -o pipefail && /bin/bash "${GH_STUB_BIN}" 2>&1 | sed -n l
gh-stub: unexpected invocation: gh $
[1]
```

## The tmux fixture forwards no remaining options to its handler

```scrut
$ /bin/bash "${TMUX_STUB_BIN}" load-buffer 2>&1
tmux-stub: missing load-buffer -b
[1]
```

## The curl fixture can log an empty argument array

```scrut
$ root="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && STUB_CURL_LOG="${root}/log" /bin/bash "${NTFY_CURL_STUB_BIN}" </dev/null >/dev/null && sed -n '1,2l' "${root}/log"
arg: $
body: $
```
