# review-anti-patterns result check

Tests for `result-check.jq`, the filter that decides whether a Codex run of
`review-anti-patterns` returned a usable result. A reply the filter passes is
the review; one it fails sends the skill to its fallback. Each case edits one
field of a valid reply and pipes it through the shipped filter.

```scrut
$ function check() {
>   jq "${1}" <<< '{"complete":true,"excluded":[],"findings":[{"detail":"d","evidence":"e","file":"src/a.ts","line":3,"severity":"important","title":"t"}],"not_reviewed":[],"report":"r","reviewed":"abc..HEAD","status":"success","unverified":[]}' \
>     | jq -e -f "${RESULT_CHECK_JQ}"
> }
```

## A complete reply with a finding passes

```scrut
$ check '.'
true
```

## A finding about a whole file passes with a null line

```scrut
$ check '.findings[0].line = null'
true
```

## An incomplete review with no findings passes

```scrut
$ check '.complete = false | .findings = [] | .not_reviewed = ["PR body"]'
true
```

## A fractional line fails

```scrut
$ check '.findings[0].line = 1.5'
false
[1]
```

## A line of zero fails

```scrut
$ check '.findings[0].line = 0'
false
[1]
```

## An unknown severity fails

```scrut
$ check '.findings[0].severity = "critical"'
false
[1]
```

## A finding with a missing field fails

```scrut
$ check 'del(.findings[0].evidence)'
false
[1]
```

## A reply with an extra field fails

```scrut
$ check '.summary = "s"'
false
[1]
```

## A list holding a non-string fails

```scrut
$ check '.not_reviewed = [1]'
false
[1]
```

## An unknown status fails

```scrut
$ check '.status = "clean"'
false
[1]
```

## Complete with a failure status fails

```scrut
$ check '.status = "failure"'
false
[1]
```

## Complete with something not reviewed fails

```scrut
$ check '.not_reviewed = ["PR body"]'
false
[1]
```

## A reply that is not an object fails

```scrut
$ check '[.]'
false
[1]
```

## A successful review without a report fails

```scrut
$ check '.report = " "'
false
[1]
```

## A successful review that names no scope fails

```scrut
$ check '.reviewed = ""'
false
[1]
```

## A failed run may leave the scope and report empty

```scrut
$ check '.status = "failure" | .complete = false | .findings = [] | .reviewed = "" | .report = ""'
true
```
