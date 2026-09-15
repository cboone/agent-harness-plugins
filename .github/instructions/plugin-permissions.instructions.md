---
applyTo: "plugins/**/README.md"
---

# Plugin Permission Examples

For repo-wide conventions, see [copilot-instructions.md](../copilot-instructions.md) and `AGENTS.md` at the repository root.

Claude Code accepts a terminal `:*` suffix and a whitespace-delimited terminal `*` as equivalent command-prefix matches. Do not flag rules such as `Bash(git show:*)` or `Bash(gh pr view:*)` as non-matching because of the colon. See the [permission wildcard documentation](https://code.claude.com/docs/en/permissions#wildcard-patterns).
