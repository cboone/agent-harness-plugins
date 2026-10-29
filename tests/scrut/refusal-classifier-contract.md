# Shared refusal classifier

Notify and attention-log ship the same classifier. The fixture uses isolated copies and stubbed notification delivery. It replaces both fixture helpers with a constant predicate to prove both entry points consume the shared function.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

## Shipped copies match

```scrut
$ cmp -s "${REPO_ROOT}/plugins/notify/scripts/claude-transcript.jq" \
>   "${REPO_ROOT}/plugins/attention-log/scripts/claude-transcript.jq" && echo shared
shared
```

## Both consumers apply the shared prompt and refusal rules

```scrut
$ "${CHECK_NOTIFICATIONS_BIN}" tier-refusal-contract
metadata-log: refusal_stop
human-log: api_error_stop
result-log: refusal_stop
reply-log: api_error_stop
helper-log: refusal_stop
metadata: Refusal: shared | atlas: w 42-fix-parser | Funk
human: Error: shared | atlas: w 42-fix-parser | Funk
result: Refusal: shared | atlas: w 42-fix-parser | Funk
reply: Error: shared | atlas: w 42-fix-parser | Funk
helper: Refusal: shared | atlas: w 42-fix-parser | Funk
```
