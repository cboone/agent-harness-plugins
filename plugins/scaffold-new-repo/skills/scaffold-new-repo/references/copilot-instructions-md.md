# .github/copilot-instructions.md Template

This file gives GitHub Copilot repo-wide context and PR review rules. It
should NOT duplicate AGENTS.md. Instead, it cross-references AGENTS.md for
full conventions and adds Copilot-specific review guidance.

Replace `PROJECT-NAME` with the project name in title case.

```markdown
# GitHub Copilot Instructions for PROJECT-NAME

For full project conventions, see AGENTS.md in the repository root.

## PR Review

When reviewing pull requests, do not flag the following patterns as issues.
Each is an intentional project convention:

- **Convention name**: Brief explanation of why this pattern is intentional and should not be flagged.
```

## Notes

- **Pointer pattern:** This template uses the "pointer" strategy — a brief
  cross-reference to AGENTS.md plus Copilot-specific PR review rules. This
  avoids duplicating conventions that already live in AGENTS.md.
- **"Do not flag" items:** The PR Review section uses a bold-key pattern
  (`**Convention name**: explanation`) to document project patterns that
  Copilot commonly misidentifies as issues. At scaffold time, there are no
  project-specific items yet, so the template includes a single placeholder
  entry. Real items accumulate over time as Copilot incorrectly flags patterns
  during PR reviews.
- **Keep concise:** GitHub recommends keeping instruction files short and
  putting the most important rules first. Start with a focused set of review
  rules and add more iteratively.
- **Title format:** Use `# GitHub Copilot Instructions for PROJECT-NAME` for
  new repos. Some repos use the shorter `# Copilot Instructions` — both work.
- The heading uses the project name in title case (e.g., `my-cool-tool`
  becomes `My Cool Tool`).
