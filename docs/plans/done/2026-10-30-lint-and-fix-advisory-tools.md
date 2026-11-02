# Advisory tools in lint-and-fix

Resolve [issue 532](https://github.com/cboone/agent-harness-plugins/issues/532) by extending the existing skill. File-presence inference must not impose new repository requirements.

## Prior art

- [pre-commit](https://pre-commit.com/#adding-pre-commit-plugins) selects hooks through repository configuration. Reuse explicit selection as evidence of enforcement; replacing the skill would lose its parent continuation and agent-policy handling.
- [MegaLinter](https://megalinter.io/latest/configuration/) separates enabled linters from non-blocking errors through `DISABLE_ERRORS_LINTERS`. Reuse separate reporting and failure classification; its default broad activation does not satisfy this issue's repository-first policy.

## Changes

1. Classify each tool as enforced or inferred only, citing configuration, hooks, CI, Makefile/package scripts, agent instructions or executing tests. Preserve repository command selection, scopes and policy precedence.
2. Restrict inferred-only tools to verified check commands; keep findings, unavailable checks and execution errors advisory throughout remediation, verification, push and parent continuation.
3. Add a separate advisory result line, update examples and bump the plugin version. Regenerate mirrors with `make build`.

## Verification and completion

Walk through shell-only inference, each enforcement signal, mixed outcomes, unavailable advisory tools, unsafe check commands, `--tool`, `--check` and existing policy restrictions. This is a prompt-only change; text-matching tests would not establish agent behavior. No executable helper or new test is planned.

Use the small-change review path if the canonical change remains about 100 lines of tooling/docs outside security: one Codex round, expanding to full review order for Important/Critical findings or a larger diff. Finish with lint-and-fix without push, version checks, the locked `SCRUT_JOBS=2 make test-all` run, signed exact-tree tidy, push and a ready PR. Record known baseline failures separately and report to TOOLING; TOOLING merges. No live configuration changes.
