# Copilot fix ancestry

The fixture builds real Git histories and supplies a local PR repository URL
through a checked gh stub. All comparisons use the recorded PR head, regardless
of upstream configuration.

## A checkout without an upstream verifies its PR fix

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" no-upstream
result=true; exit=0
```

## An unrelated upstream cannot establish PR ancestry

The candidate fix is on the unrelated upstream, but not the PR head.

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" unrelated-upstream
result=false; exit=0
```

## Missing objects are fetched from the PR head ref

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" missing
result=true; exit=0
missing fix fetched from PR ref; history complete
```

## A missing fix after fetch is a workflow failure

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" unknown
result=none; exit=1
Error: Fix commit object is unavailable after fetching PR head
```

## A failed ref fetch cannot become negative ancestry

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" fetch-error
result=none; exit=1
Error: Cannot fetch PR head ref
```

## A moved PR head invalidates the recorded context

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" moved
result=none; exit=1
Error: PR head moved; refetch PR context before recovery
```

## A failed ancestry read is not a negative answer

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" ancestry-error
result=none; exit=1
Error: Cannot read fix ancestry
```

## Existing endpoints do not make shallow history complete

```scrut
$ bash "${COPILOT_ANCESTRY_CASE_BIN}" "${RESOLVE_COPILOT_THREADS_BIN}" shallow-endpoints
result=true; exit=0
missing fix fetched from PR ref; history complete
```
