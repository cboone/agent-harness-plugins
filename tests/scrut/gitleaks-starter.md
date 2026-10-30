# Gitleaks starter configuration

The first TOML fence is the emitted starter. This guard pins its active configuration; it does not emulate scanner rules. Gitleaks behavior is checked separately with synthetic credentials.

## Starter keeps default rules without added exclusions

```scrut
$ template="${REPO_ROOT}/plugins/set-up-secret-scanning/skills/set-up-secret-scanning/references/gitleaks-config.md"; "${CHECK_GITLEAKS_STARTER_BIN}" "${template}"
Starter extends default rules without added exclusions.
```

## Blanket path exclusion is rejected

````scrut
$ sample="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '```toml' '[extend]' 'useDefault = true' '[allowlist]' "paths = ['vendor/']" '```' > "${sample}" && "${CHECK_GITLEAKS_STARTER_BIN}" "${sample}" 2>&1
Starter must only extend default rules without added exclusions.
[1]
````

## Disabled defaults are rejected

````scrut
$ sample="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '```toml' '[extend]' 'useDefault = false' '```' > "${sample}" && "${CHECK_GITLEAKS_STARTER_BIN}" "${sample}" 2>&1
Starter must only extend default rules without added exclusions.
[1]
````

## Missing starter is rejected

```scrut
$ sample="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' 'No starter' > "${sample}" && "${CHECK_GITLEAKS_STARTER_BIN}" "${sample}" 2>&1
Starter must only extend default rules without added exclusions.
[1]
```

## Unclosed starter is rejected

````scrut
$ sample="$(mktemp "${TMPDIR:-/tmp}/scrut.XXXXXX")" && printf '%s\n' '```toml' '[extend]' 'useDefault = true' > "${sample}" && "${CHECK_GITLEAKS_STARTER_BIN}" "${sample}" 2>&1
Starter must only extend default rules without added exclusions.
[1]
````
