# Copilot Instructions Template

This file gives GitHub Copilot repo-wide context. It should NOT duplicate
AGENTS.md. Instead, it cross-references AGENTS.md for full conventions.
A default PR review rule is included; more can be added as needed (see Notes).

Replace `PROJECT-NAME` with the exact binary or repository name (kebab-case).

```markdown
# GitHub Copilot Instructions for PROJECT-NAME

For full project conventions, see AGENTS.md in the repository root.

## PR Review

- **Done plans are historical records**: Files in `docs/plans/done/` are completed plan documents preserved for reference. They may not match the final implementation. Do not flag discrepancies between done plan content and the actual codebase.
```

## Notes

- **Pointer pattern:** This template uses the "pointer" strategy, a brief
  cross-reference to AGENTS.md. This avoids duplicating conventions that
  already live in AGENTS.md.
- **PR Review section included by default:** The template ships with a
  `## PR Review` section containing the done-plans rule. Add more rules
  using the bold-key pattern (`**Convention name**: explanation`) as needed.
- **Keep concise:** GitHub recommends keeping instruction files short and
  putting the most important rules first. Start with a focused set of review
  rules and add more iteratively.
- **Title format:** Use `# GitHub Copilot Instructions for PROJECT-NAME` for
  new repos. Some repos use the shorter `# Copilot Instructions`, both work.
- The heading uses the exact binary or repository name (e.g., `my-cool-tool`),
  not a titleized version.
- **Per-skill false positive entries:** Other scaffold and setup tools
  (`scaffold-go-cli`, `scaffold-go-library`, `setup-linters`) append PR review
  entries to this file for patterns they generate that Copilot commonly flags.
  This file serves as the append target for those entries.
