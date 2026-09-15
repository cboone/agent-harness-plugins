# Repository tooling instructions

Read [plugin development](../docs/plugin-development.md) for the schemas and path rules these tools enforce.

- `validate-json` and `validate-plugins` are merge gates. Keep cross-reference rule 19 delegated to `check-cross-references` and executable helper checks in rule 18.
- `compute-catalog-state` is the canonical catalog-tag calculation used by validation and release CI. Keep callers consistent with it.
- Generators own `../dist/` and `../.agents/`; changes must keep their output deterministic and freshness checks effective.
- `list-shell-scripts` defines local and CI shell-lint selection. Ensure new executable helpers are included.
- Add meaningful tooling coverage in `../tests/scrut/`; stubs and JSON data belong in the corresponding fixture directories.
- `version-audit` requires authenticated `gh`, `jq` and `curl`. Empty output means no upstream drift; it is a weekly audit, not a merge gate.
