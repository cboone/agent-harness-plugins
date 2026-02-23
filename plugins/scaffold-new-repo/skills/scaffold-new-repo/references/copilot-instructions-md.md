# .github/copilot-instructions.md Template

This file gives GitHub Copilot repo-wide context. It should NOT duplicate
AGENTS.md. Instead, it cross-references AGENTS.md for full conventions.
PR review rules can be added later as needed (see Notes).

Replace `PROJECT-NAME` with the project name in title case.

```markdown
# GitHub Copilot Instructions for PROJECT-NAME

For full project conventions, see AGENTS.md in the repository root.
```

## Notes

- **Pointer pattern:** This template uses the "pointer" strategy, a brief
  cross-reference to AGENTS.md. This avoids duplicating conventions that
  already live in AGENTS.md.
- **Adding PR Review rules:** When Copilot incorrectly flags a project
  convention during PR review, add a `## PR Review` section with the
  bold-key pattern (`**Convention name**: explanation`). Example:

  ```markdown
  ## PR Review

  When reviewing pull requests, do not flag the following patterns as issues.
  Each is an intentional project convention:

  - **Bare TODO in template files**: These are intentional placeholders for
    the repo owner to fill in later, not incomplete work.
  ```

- **Keep concise:** GitHub recommends keeping instruction files short and
  putting the most important rules first. Start with a focused set of review
  rules and add more iteratively.
- **Title format:** Use `# GitHub Copilot Instructions for PROJECT-NAME` for
  new repos. Some repos use the shorter `# Copilot Instructions`, both work.
- The heading uses the project name in title case (e.g., `my-cool-tool`
  becomes `My Cool Tool`).
