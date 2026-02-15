# GitHub Copilot Instructions

For full project conventions, see AGENTS.md in the repository root.

## PR Review

- **Version bumps are selective**: Only plugins with actual code changes get version bumps. Do not flag missing version bumps on unchanged plugins.
- **PR descriptions may contain stale commit references**: PR descriptions are often auto-generated from commit messages and may reference superseded commits. Do not flag discrepancies between PR description bullet points and the actual diff.
- **Skill files use short command placeholders intentionally**: In SKILL.md files, bare command names like `resolve-copilot-threads` in code examples are documented placeholders for the script's quoted absolute path. A preamble in the "Script Setup" section explains this convention. Do not flag these as missing paths or broken commands.
- **HEREDOC with `-m` is intentional**: The pattern `git commit -m "$(cat <<'EOF' ... EOF)"` is a project convention for commit messages. The `$(cat ...)` command substitution correctly preserves internal newlines. Do not suggest replacing it with `git commit -F -` or other alternatives.
