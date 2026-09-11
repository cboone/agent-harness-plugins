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

## Non-object JSON

```scrut
$ printf 'null' | "${COMPOSE_ISSUE_PROMPT_BIN}" 2>&1
compose-issue-prompt: invalid issue JSON: expected object
[1]
```

## Missing required field

```scrut
$ jq -n '{title: "Missing number", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}" 2>&1
compose-issue-prompt: invalid issue JSON: missing required numeric field 'number'
[1]
```

## Chained command footer

`address-issue-in-worktree` passes `--chain-command` so the injected prompt
tells the new session which command to run first. The footer deliberately says
nothing about stopping for approval: that is `address-issue`'s own default.

```scrut
$ jq -n '{number: 42, title: "Fix login crash", labels: [{name: "bug"}], body: "Login fails on empty password.", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}" --chain-command "/address-issue 42"
Work on issue #42: Fix login crash

Labels: bug

Login fails on empty password.

---

Start by running this command:

/address-issue 42
```

## Chained command carries its own flags

```scrut
$ jq -n '{number: 7, title: "Update README", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}" --chain-command "/address-issue 7 --no-approval"
Work on issue #7: Update README

---

Start by running this command:

/address-issue 7 --no-approval
```

## Chained command requires a value

```scrut
$ jq -n '{number: 7, title: "Update README", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}" --chain-command 2>&1
compose-issue-prompt: --chain-command requires a command
[1]
```

## Unknown argument is rejected

```scrut
$ jq -n '{number: 7, title: "Update README", state: "OPEN"}' | "${COMPOSE_ISSUE_PROMPT_BIN}" --nope 2>&1 | tail -n 1
compose-issue-prompt: unexpected argument: --nope
```

## The create-worktree copy omits the footer by default

`create-worktree` ships the same script but never passes `--chain-command`,
because it creates the worktree and stops.

```scrut
$ jq -n '{number: 42, title: "Fix login crash", state: "OPEN"}' | "${CREATE_WORKTREE_COMPOSE_ISSUE_PROMPT_BIN}"
Work on issue #42: Fix login crash
```
