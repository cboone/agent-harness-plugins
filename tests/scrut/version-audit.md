# Pip version drift

## Offline setup

```scrut {fail_fast: true}
$ export AUDIT_FIXTURE="$(mktemp -d "${TMPDIR:-/tmp}/scrut.XXXXXX")" && mkdir -p "${AUDIT_FIXTURE}/bin" "${AUDIT_FIXTURE}/plugins" "${AUDIT_FIXTURE}/.github" && ln -s "${VERSION_AUDIT_STUB_BIN}" "${AUDIT_FIXTURE}/bin/curl" && ln -s "${VERSION_AUDIT_STUB_BIN}" "${AUDIT_FIXTURE}/bin/gh" && export PATH="${AUDIT_FIXTURE}/bin:${PATH}" && cd "${AUDIT_FIXTURE}" && test "$(command -v curl)" = "${AUDIT_FIXTURE}/bin/curl" && test "$(command -v gh)" = "${AUDIT_FIXTURE}/bin/gh"
```

## Real upgrades in fenced templates remain visible

````scrut
$ printf '```bash\npip install sample==1.9.0\nuv pip install sample==1.10.0\nuv add --dev "sample==1.99.0"\n```\n' > plugins/pins.md && "${VERSION_AUDIT_BIN}" | sed -n '/^| pip/p'
| pip / uv install | `sample` | `1.9.0` | `2.0.0` | skill templates |
| pip / uv install | `sample` | `1.10.0` | `2.0.0` | skill templates |
| pip / uv install | `sample` | `1.99.0` | `2.0.0` | skill templates |
````

## The documentation placeholder produces no drift

```scrut
$ printf '| Install commands | `pip install tool==1.2.3` in scripts |\n' > plugins/pins.md && "${VERSION_AUDIT_BIN}"
```

## Minor and patch upgrades compare every numeric component

```scrut
$ printf 'pip install components==2.9.0\nuv add components==2.10.0\nuv pip install components==2.10.2\n' > plugins/pins.md && "${VERSION_AUDIT_BIN}" | sed -n '/^| pip/p'
| pip / uv install | `components` | `2.9.0` | `2.10.1` | skill templates |
| pip / uv install | `components` | `2.10.0` | `2.10.1` | skill templates |
```

## Numeric downgrades and equivalent releases produce no drift

```scrut
$ printf 'pip install sample==10.0.0\nuv add sample==2.0\nuv pip install sample==2.0.0\n' > plugins/pins.md && "${VERSION_AUDIT_BIN}"
```

## Nonnumeric PyPI releases keep the existing drift behavior

```scrut
$ printf 'pip install postrelease==2.0.0\n' > plugins/pins.md && "${VERSION_AUDIT_BIN}" | sed -n '/^| pip/p'
| pip / uv install | `postrelease` | `2.0.0` | `2.0.0.post1` | skill templates |
```

## An empty lookup produces no drift

```scrut
$ printf 'pip install unavailable==1.0.0\n' > plugins/pins.md && "${VERSION_AUDIT_BIN}"
```

## Comparison failures stop the audit

```scrut
$ ln -s "$(command -v jq)" "${AUDIT_FIXTURE}/bin/jq-real" && ln -s "${VERSION_AUDIT_STUB_BIN}" "${AUDIT_FIXTURE}/bin/jq" && test "$(command -v jq)" = "${AUDIT_FIXTURE}/bin/jq" && printf 'pip install sample==1.9.0\n' > plugins/pins.md && "${VERSION_AUDIT_BIN}" 2>&1
jq: injected comparison failure
[5]
```
