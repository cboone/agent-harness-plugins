# Repository sound selection

Each scenario captures Claude and Codex completion, permission, Claude and Codex questions, elicitation and plan approval, in that order. The fixture runs the notifier under `/bin/bash` with an isolated sound directory.

## POSIX checksum vectors without a trailing newline

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ for name in sample-repo another-repo outside-repo; do printf '%s' "${name}" | cksum; done
419135404 11
1836255427 12
1377423397 12
```

## Full set selects the pinned sample repository index

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-full
Chord-stop-4
Chord-stop-4
Chord-permission-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
```

## Another repository selects its pinned index

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-other
Chord-stop-2
Chord-stop-2
Chord-permission-2
Chord-attention-2
Chord-attention-2
Chord-attention-2
Chord-attention-2
```

## Worktrees share the repository index

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-worktree
Chord-stop-4
Chord-stop-4
Chord-permission-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
```

## Supported and duplicate extensions count indices once

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-extensions
Chord-stop-4
Chord-stop-4
Chord-permission-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
```

## Unset setting preserves every default

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-unset
Glass
Glass
Funk
Tink
Tink
Tink
Tink
```

## Empty setting preserves every default

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-empty
Glass
Glass
Funk
Tink
Tink
Tink
Tink
```

## Invalid prefix preserves every default

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-invalid
Glass
Glass
Funk
Tink
Tink
Tink
Tink
```

## A gap stops the count before later files

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-gap
Chord-stop-0
Chord-stop-0
Chord-permission-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
```

## Missing index zero ignores later files

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-zero
Glass
Glass
Chord-permission-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
```

## Missing role preserves its built-in sound

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-missing
Chord-stop-4
Chord-stop-4
Funk
Chord-attention-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
```

## Different counts use the same hash per role

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-counts
Chord-stop-4
Chord-stop-4
Chord-permission-1
Chord-attention-4
Chord-attention-4
Chord-attention-4
Chord-attention-4
```

## Outside Git uses the folder name

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" sound-outside
Chord-stop-2
Chord-stop-2
Chord-permission-2
Chord-attention-2
Chord-attention-2
Chord-attention-2
Chord-attention-2
```
