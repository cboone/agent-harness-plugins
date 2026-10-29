# Git and review chain adapters

## The opt-in runner captures a reply and rejects missing replies

These driver cases require zsh, matching the measured host's login shell. Linux CI runs the portable helper and checker cases below; the driver is an opt-in macOS procedure.

```scrut {fail_fast: true}
$ source "${REPO_ROOT}/bin/lib/git-environment.bash"
```

```scrut
$ if ! command -v zsh >/dev/null; then echo 'zsh driver check skipped'; else root="$(mktemp -d "${TMPDIR:-/tmp}/chain-driver.XXXXXX")" && mkdir "${root}/bin" && cp "${CHAIN_CODEX_STUB_BIN}" "${root}/bin/codex" && chmod +x "${root}/bin/codex" && export PATH="${root}/bin:${PATH}" && test "$(command -v codex)" = "${root}/bin/codex" && printf '[]\n' > "${root}/overrides.json" && node "${REPO_ROOT}/tests/data/git-review-chain-evals/run.mjs" after "${root}" "${root}/overrides.json" activation-negative | jq -e '.exit == 0 and .nonempty == true'; fi
true|zsh driver check skipped (regex)
```

```scrut
$ if ! command -v zsh >/dev/null; then echo 'zsh driver check skipped'; else root="$(mktemp -d "${TMPDIR:-/tmp}/chain-driver.XXXXXX")" && mkdir "${root}/bin" && cp "${CHAIN_CODEX_STUB_BIN}" "${root}/bin/codex" && chmod +x "${root}/bin/codex" && export PATH="${root}/bin:${PATH}" && test "$(command -v codex)" = "${root}/bin/codex" && printf '[]\n' > "${root}/overrides.json" && CHAIN_CODEX_STUB_MODE=missing node "${REPO_ROOT}/tests/data/git-review-chain-evals/run.mjs" after "${root}" "${root}/overrides.json" activation-negative > "${root}/result.json"; status=$?; test "${status}" = 1 && jq -e '.exit == 0 and .nonempty == false' "${root}/result.json"; fi
true|zsh driver check skipped (regex)
```

## Helper resolution follows the loaded symlink to its current package

```scrut
$ "${CHAIN_HELPER_FIXTURE_BIN}" "${REPO_ROOT}/plugins/monitor-pr/skills/monitor/SKILL.md"
current
```

```scrut
$ "${CHAIN_HELPER_FIXTURE_BIN}" "${REPO_ROOT}/plugins/monitor-pr/skills/resolve-copilot-feedback/SKILL.md"
current
```

## A continuation requires the child's contract

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Capabilities and authority' '' '## Skill dependencies' '' '- **Required:** None' '- **Optional:** `other:other`' '' '## Workflow' '' 'Invoke the `other:other` skill.' '' 'Parent continuation:' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
::error::plugins/demo/skills/demo/SKILL.md passes a parent continuation to other:other, but plugins/other/skills/other/SKILL.md has no Parent Continuation Contract
[1]
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Parent Continuation Contract' > plugins/other/skills/other/SKILL.md && printf '%s\n' '## Capabilities and authority' '' '## Skill dependencies' '' '- **Required:** None' '- **Optional:** `other`' '' '## Workflow' '' 'Invoke the `other` skill.' '' 'Parent continuation:' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

## Missing preflights warn only on adopted workflows

The contract check extracts the matched skill, including when preceding code spans name options or a trailer.

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Capabilities and authority' '' '## Skill dependencies' '' '- **Required:** None' '- **Optional:** `other:other`' '' '## Workflow' '' 'For `--no-push`, invoke the `other:other` skill.' '' 'Parent continuation:' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
::error::plugins/demo/skills/demo/SKILL.md passes a parent continuation to other:other, but plugins/other/skills/other/SKILL.md has no Parent Continuation Contract
[1]
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Capabilities and authority' '' '## Skill dependencies' '' '- **Required:** None' '- **Optional:** `other`' '' '## Workflow' '' 'After `Trailer:`, Invoke the `/other` skill.' '' 'Parent continuation:' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
::error::plugins/demo/skills/demo/SKILL.md passes a parent continuation to other, but plugins/other/skills/other/SKILL.md has no Parent Continuation Contract
[1]
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Capabilities and authority' '' '## Skill dependencies' '' '- **Required:** `other`' '- **Optional:** None' '' '## Workflow' '' 'Invoke the `other` skill.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
::warning::plugins/demo/skills/demo/SKILL.md lacks a canonical availability preflight for other
All skill cross-references resolve.
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Capabilities and authority' '' '## Skill dependencies' '' '- **Required:** `other`' '- **Optional:** None' '' '## Workflow' '' 'Confirm that the `other` skill is available.' '' 'Invoke the `other` skill.' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```

```scrut
$ cd "$("${CROSS_REFERENCE_FIXTURE_BIN}")" && printf '%s\n' '## Skill dependencies' '' '- **Required:** `other`' '- **Optional:** None' '' '## Workflow' '' 'Invoke the `other` skill.' '' 'Parent continuation:' > plugins/demo/skills/demo/SKILL.md && "${CHECK_CROSS_REFERENCES_BIN}" plugins/demo/skills/demo/SKILL.md
All skill cross-references resolve.
```
