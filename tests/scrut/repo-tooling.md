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

```scrut
$ cd "${REPO_ROOT}" && "${LIST_SHELL_SCRIPTS_BIN}" | grep -c '^dist/' || true
0
```

## The shell script list reaches scripts under skill references

The previous `plugins/*/scripts/*` lint glob never reached this 33 KB script,
and widening it by hand would have swept in a sibling `.yml`.

```scrut
$ cd "${REPO_ROOT}" && "${LIST_SHELL_SCRIPTS_BIN}" | grep -q 'pin-everything/skills/pin-everything/references/scripts/version-audit-template' && echo found
found
```

## The shell script list contains only Bash scripts

```scrut
$ cd "${REPO_ROOT}" && "${LIST_SHELL_SCRIPTS_BIN}" | while IFS= read -r f; do head -n 1 "${f}" | grep -q bash || echo "not bash: ${f}"; done
```

## No angle-bracket placeholder is padded into a shell redirect

Prettier once rewrote `git diff <base-branch>...HEAD` into
`git diff < base-branch > ...HEAD` inside fenced blocks, which reads a file
named `base-branch` and truncates the commit range. `embeddedLanguageFormatting`
is off now; this guards the seven sites that were repaired.

```scrut
$ cd "${REPO_ROOT}" && grep -rlE '< (base-branch|base-ref|merge-base|default-branch|source-branch) >' plugins/ | wc -l | tr -d ' '
0
```
