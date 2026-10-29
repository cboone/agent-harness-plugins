# Owner-file reservation identity

## An empty reservation can be released before PID recording

```scrut
$ "${OWNER_LOCK_PROBE_BIN}" empty
empty reservation released
```

## Release preserves a different file at the same owner path

```scrut
$ "${OWNER_LOCK_PROBE_BIN}" successor
successor identity preserved
```

## A stale token cannot release the next reservation in the same process

```scrut
$ "${OWNER_LOCK_PROBE_BIN}" stale
stale token refused; current reservation released
```

## Session and rotation can retain separate identities

```scrut
$ "${OWNER_LOCK_PROBE_BIN}" nested
independent session and rotation identities released
```

## Descriptor 8 rejects a contender that passed the existence precheck

```scrut
$ "${OWNER_LOCK_PROBE_BIN}" contend8
slot 8: exclusive open refused the second actor without diagnostics
```

## Descriptor 9 rejects a contender that passed the existence precheck

```scrut
$ "${OWNER_LOCK_PROBE_BIN}" contend9
slot 9: exclusive open refused the second actor without diagnostics
```

## Non-contention open failures retain their reason after diagnostic creation

```scrut
$ "${OWNER_LOCK_PROBE_BIN}" open-error
exclusive-open error: status 2; owner path and reason retained; no token
```
