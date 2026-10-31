# Claude schema validation

The fixture runs the repository Make target with convention checks stubbed and
an isolated PATH. Its committed Claude stub records each schema validation call.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Marketplace and every plugin run

```scrut
$ "${CLAUDE_VALIDATION_FIXTURE_BIN}" success
make status=0
.
plugins/alpha
plugins/beta
```

```scrut
$ "${CLAUDE_VALIDATION_FIXTURE_BIN}" newer
make status=0
.
plugins/alpha
plugins/beta
```

Version components use decimal arithmetic even when they have leading zeros.

```scrut
$ "${CLAUDE_VALIDATION_FIXTURE_BIN}" leading-zeros
make status=0
.
plugins/alpha
plugins/beta
```

## Missing and older CLI fail clearly

```scrut
$ "${CLAUDE_VALIDATION_FIXTURE_BIN}" missing 2>&1
Claude Code >= 2.1.314 is required on PATH for make validate; install or update it manually.
make*: *** *Error 1 (glob)
make status=2
[2]
```

```scrut
$ "${CLAUDE_VALIDATION_FIXTURE_BIN}" old 2>&1
Claude Code >= 2.1.314 is required; found 2.1.313 (Claude Code). Update it manually.
make*: *** *Error 1 (glob)
make status=2
[2]
```

## Schema failures reach Make and stop further validation

```scrut
$ "${CLAUDE_VALIDATION_FIXTURE_BIN}" marketplace-failure 2>&1
Schema rejected: .
make*: *** *Error 7 (glob)
make status=2
.
[2]
```

```scrut
$ "${CLAUDE_VALIDATION_FIXTURE_BIN}" plugin-failure 2>&1
Schema rejected: plugins/alpha
make*: *** *Error 7 (glob)
make status=2
.
plugins/alpha
[2]
```
