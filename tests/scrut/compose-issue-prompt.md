# Compose issue prompt

Tests for converting GitHub issue JSON into the workmux task prompt.

## Labels and body

```scrut
$ jq -n '{number: 265, title: "Consolidate prompt creation", labels: [{name: "enhancement"}, {name: "worktree"}], body: "Implement stdin prompt transport.", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}"
Work on issue #265: Consolidate prompt creation

Labels: enhancement, worktree

Implement stdin prompt transport.
```

## Omitted labels and empty body

```scrut
$ jq -n '{number: 12, title: "No details", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}"
Work on issue #12: No details
```

## Long body truncation notice

```scrut
$ body="$(printf 'First sentence. '; printf 'x%.0s' {1..2100})" && jq -n --arg body "${body}" '{number: 265, title: "Long body", labels: [], body: $body, state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}" | tail -1
(Issue body truncated. Run `gh issue view 265` for full details.)
```

## Invalid JSON

```scrut
$ printf '{' | "${COMPOSE_ISSUE_PROMPT_BIN}" 2>&1
compose-issue-prompt: invalid issue JSON
[1]
```

## Missing required field

```scrut
$ jq -n '{title: "Missing number", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}" 2>&1
compose-issue-prompt: invalid issue JSON: missing required numeric field 'number'
[1]
```
