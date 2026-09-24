# Repository tooling instructions

Read [plugin development](../docs/plugin-development.md) for the schemas and path rules these tools enforce.

- `validate-json` and `validate-plugins` are merge gates. Keep cross-reference rule 19 delegated to `check-cross-references`, executable helper checks in rule 18, and review checklist freshness in rule 20, which regenerates through `build-review-checklists`.
- Generators own `../dist/`, `../.agents/` and the review checklist copies in `set-up-review-config`'s `references/checklists/`; changes must keep their output deterministic and freshness checks effective. `make build` runs `build-review-checklists` before the mirror builders, which copy `../plugins/`.
- `build-codex-marketplace` makes one sanctioned change to a `SKILL.md`: `disable-model-invocation` becomes an `agents/openai.yaml` invocation policy, because Codex ignores the frontmatter field. Rule 16b reproduces that edit independently and rejects every other difference, and rule 21 holds frontmatter to the allowlist in `../docs/plugin-development.md`. Any further transformation changes both rules on purpose.
- `list-shell-scripts` defines local and CI shell-lint selection. Ensure new executable helpers are included.
- Add meaningful tooling coverage in `../tests/scrut/`; stubs and JSON data belong in the corresponding fixture directories.
- `materialize-case` and `validate-corpus` read the review case corpus, whose conventions are in [review case corpus](../docs/review-case-corpus.md). Both tools are gated, by `../tests/scrut/review-corpus.md`; validation against the real corpus is not, because that corpus lives in a separate repository and is absent from most checkouts, which is why `make validate-corpus` stands apart from `validate`. `validate-corpus` needs `jq` and mikefarah `yq` v4.
- `version-audit` requires authenticated `gh`, `jq` and `curl`. Empty output means no upstream drift; it is a weekly audit, not a merge gate.
