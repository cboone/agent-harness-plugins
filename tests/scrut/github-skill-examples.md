# GitHub skill examples

Canonical skill examples run as disposable Bash scripts.
Their PATH contains only the committed gh capture stub. A guard refuses to run
unless `gh` resolves to that stub; no GitHub writes occur.
Issue classification runs the documented jq filters against synthetic URLs.

## Issue creation and PR creation and correction preserve literal titles

```scrut
$ "${GITHUB_SKILL_EXAMPLES_BIN}" titles
literal title examples: 5
```

## The documented apostrophe escape preserves the title

```scrut
$ "${GITHUB_SKILL_EXAMPLES_BIN}" apostrophe
Fix parser's handling
```

## Both connected-issue strategies keep issues and reject pull requests

```scrut
$ "${GITHUB_SKILL_EXAMPLES_BIN}" issues
issue-only detection strategies: 2
```

## Refuse an inherited gh function that would bypass the stub

```scrut
$ function gh() { "${EXPECTED_GH_STUB}" "$@"; }; export -f gh; "${GITHUB_SKILL_EXAMPLES_BIN}" titles
[1]
```
