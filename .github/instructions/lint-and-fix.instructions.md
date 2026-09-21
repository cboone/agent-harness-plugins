---
applyTo: "plugins/lint-and-fix/**,dist/codex/plugins/lint-and-fix/**"
---

# Lint and fix review instructions

For repository-wide conventions, see [the general Copilot instructions](../copilot-instructions.md).

- **A documented command runs verbatim, and is never expanded into its constituent commands.** A project narrows a lint invocation on purpose, so rewriting an aggregate entry point such as `make lint` or `npm run lint` into the steps it wraps substitutes the skill's reconstruction for the project's own, which is the failure the documented-command precedence exists to prevent. Do not propose expanding, decomposing, or partially replacing a documented command.
- **A downgrade does not mean running the same command in a different mode.** Under the No-Write Rule a downgraded tool runs only a command whose check-only behavior is established, and where none exists it is recorded as `check-only (no safe check command)` and nothing runs. An aggregate command that wraps a forbidden fixer therefore does not execute, so it is not evidence that the prohibition can be bypassed. Do not report a wrapper as an escape from a prohibition on that premise.
