# Repository tooling

Tests for the `bin/` scripts that gate releases and generated output. These had
no coverage at all, even though `compute-catalog-state` alone decides the tag
name and GitHub Release that `release.yml` publishes.

## Catalog state sums each SemVer field independently

No normalization and no carry between components, so patch 3 + patch 10 is 13,
not 1.3.

```scrut
$ dir="$(mktemp -d)" && jq -n '{plugins: [{version: "1.2.3"}, {version: "2.0.10"}]}' > "${dir}/marketplace.json" && MARKETPLACE="${dir}/marketplace.json" "${COMPUTE_CATALOG_STATE_BIN}"
catalog-M3-m2-p13-n2
```

## Catalog state counts plugins

```scrut
$ dir="$(mktemp -d)" && jq -n '{plugins: [{version: "0.0.1"}, {version: "0.0.1"}, {version: "0.0.1"}]}' > "${dir}/marketplace.json" && MARKETPLACE="${dir}/marketplace.json" "${COMPUTE_CATALOG_STATE_BIN}"
catalog-M0-m0-p3-n3
```

## Catalog state reports a missing marketplace

```scrut
$ MARKETPLACE="/nonexistent/marketplace.json" "${COMPUTE_CATALOG_STATE_BIN}" 2>&1
compute-catalog-state: /nonexistent/marketplace.json not found
[2]
```

## Catalog state rejects a non-SemVer version

A short version must fail loudly rather than contribute a partial sum to a
release tag.

```scrut
$ dir="$(mktemp -d)" && jq -n '{plugins: [{version: "1.2"}]}' > "${dir}/marketplace.json" && MARKETPLACE="${dir}/marketplace.json" "${COMPUTE_CATALOG_STATE_BIN}" > /dev/null 2>&1 || echo "rejected"
rejected
```

## The shell script list excludes generated mirrors

`dist/` holds byte-identical copies of scripts already listed from `plugins/`,
so linting them would report every finding twice.

Reported alongside the total so a run that lists nothing at all cannot pass this
as a vacuous zero.

```scrut
$ "${LIST_SHELL_SCRIPTS_BIN}" | awk 'BEGIN {d=0} /^dist\// {d++} END {print "dist=" d, "total>10=" (NR>10 ? "yes" : "no")}'
dist=0 total>10=yes
```

## The shell script list reaches scripts under skill references

The previous `plugins/*/scripts/*` lint glob never reached this 33 KB script,
and widening it by hand would have swept in a sibling `.yml`.

```scrut
$ "${LIST_SHELL_SCRIPTS_BIN}" | grep -q 'pin-everything/skills/pin-everything/references/scripts/version-audit-template' && echo found
found
```

## The shell script list contains only Bash scripts

```scrut
$ cd "${REPO_ROOT}" && "${LIST_SHELL_SCRIPTS_BIN}" | while IFS= read -r f; do head -n 1 "${f}" | grep -q bash || echo "not bash: ${f}"; done; echo done
done
```

## No angle-bracket placeholder is padded into a shell redirect

Prettier once rewrote `git diff <base-branch>...HEAD` into
`git diff < base-branch > ...HEAD` inside fenced blocks, which reads a file
named `base-branch` and truncates the commit range. `embeddedLanguageFormatting`
is off now; this guards the seven sites that were repaired.

Checks every prose surface, not just `plugins/`: the repo-local `check-versions`
skill carried two of these too, and a guard scoped to `plugins/` missed them.
`docs/plans/done/` is excluded as a historical archive.

The scanned count is reported as a yes/no so an empty scan, which would make the
zero meaningless, fails the test instead of passing it.

```scrut
$ cd "${REPO_ROOT}" && corrupted="$(grep -rlE '< [a-z][a-z0-9-]+ >' plugins/ .claude/ .github/ README.md AGENTS.md 2>/dev/null | wc -l)" && scanned="$(grep -rl 'git ' plugins/ .claude/ 2>/dev/null | wc -l)" && printf 'corrupted=%d scanned_enough=%s\n' "${corrupted}" "$([ "${scanned}" -gt 20 ] && echo yes || echo no)"
corrupted=0 scanned_enough=yes
```

## The duplicated worktree scripts stay byte-identical

`create-worktree` and `address-issue-in-worktree` ship the same
`compose-issue-prompt` and `launch-workmux`. Rule 18 of `bin/validate-plugins`
requires every `${CLAUDE_PLUGIN_ROOT}/scripts/NAME` reference to resolve inside
its own plugin, so the two plugins cannot share one copy.

The copies drifted once before: one grew `--base` support while the other grew
Codex-pane prompt resending, and neither gained the other's feature. These
guards fail the build instead of letting that happen again.

```scrut
$ cd "${REPO_ROOT}" && cmp plugins/create-worktree/scripts/compose-issue-prompt plugins/address-issue-in-worktree/scripts/compose-issue-prompt && echo identical
identical
```

```scrut
$ cd "${REPO_ROOT}" && cmp plugins/create-worktree/scripts/launch-workmux plugins/address-issue-in-worktree/scripts/launch-workmux && echo identical
identical
```
