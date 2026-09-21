<!-- Managed by set-up-review-config from write-markdown at 7b2f18f490d22c59a4210f4c68c0b6528a5ea49f. Rerun /set-up-review-config to update this file; local edits are replaced. -->

# Markdown Review Checklist

Applies to GitHub Flavored Markdown files (`*.md`). Cite findings as `write-markdown: Rule name`.

## Important

- **Working links**: Relative links point to files that exist, and heading anchors match a heading that exists, after renames and moves in the same pull request.
- **Defined references**: Every reference-style link has a matching definition.
- **Rendered structure**: Blank lines surround headings, lists, code blocks, block quotes and tables, so each renders as intended instead of merging into the paragraph above it.
- **Consistent tables**: Every table row has the same number of columns as the header row, so no cell is dropped or shifted.

## Nits

- **One top-level heading**: A document has a single `#` heading.
- **Heading levels**: Headings do not skip levels, have no trailing punctuation, and are not entirely inline code.
- **Unique sibling headings**: Headings under the same parent do not repeat the same text.
- **Semantic headings**: Headings organize the outline; bold text is not used as a substitute heading, and headings are not used only for visual size.
- **Meaningful link text**: Link text makes sense on its own; no "click here", "here" or a bare URL as the link text.
- **Alt text**: Images have alt text that conveys their purpose.
- **Code fence languages**: Every fenced code block names a language, with `text` when none applies, and uses backtick fences.
- **Commands and output**: Terminal examples keep the command (`bash` or `console`) apart from its output (`text`).
- **Emphasis markers**: `**bold**` and `_italic_`, not `__bold__` or `*italic*`.
- **List markers**: `-` for unordered lists; ordered lists use `1.` for every item or sequential numbers, consistently within a list.
- **Aligned tables**: Table pipes line up and cells are padded, where no formatter does this automatically.
- **Markdown before HTML**: HTML only for features Markdown lacks, such as `<details>`, `<kbd>` and `<sup>`.
- **File names**: Lowercase words separated by hyphens with a `.md` extension, except conventional names such as `README.md` and `CHANGELOG.md`.
- **Unused definitions**: Reference-link definitions that nothing uses are removed.

## Do not flag

- **Formatter output**: Table padding, list numbering, blank lines and whitespace that Prettier produces when it runs in CI.
- **Linter findings**: Anything markdownlint reports when it runs in CI.
- **Line length**: This guide sets no line-length limit, so long lines and unwrapped paragraphs are fine.
- **Uppercase conventional files**: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE.md` and similar names.
