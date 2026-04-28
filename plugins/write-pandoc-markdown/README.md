# Write Pandoc Markdown

Pandoc-flavored Markdown conventions for academic papers with LaTeX output.

**Type:** Skill
**Trigger:** `/write-pandoc-markdown` (also activates automatically)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Write Pandoc Markdown** from the available plugins.

## What It Does

Provides Pandoc Markdown conventions for academic papers, covering YAML frontmatter, math and citations, cross-references, raw LaTeX blocks, and the Pandoc-to-LaTeX build pipeline. Activates automatically on `.md` files that use Pandoc extensions (math delimiters, citation syntax, raw LaTeX blocks). Distinct from `write-markdown`, which covers GitHub Flavored Markdown and markdownlint rules.

## Usage

```text
/write-pandoc-markdown
```

The skill also activates automatically when Claude Code detects Pandoc Markdown work (math delimiters, citation syntax, raw LaTeX, academic YAML frontmatter).

## Examples

- Editing `main.md` for an academic paper that compiles to LaTeX
- Adding citations using Pandoc `[@key]` syntax
- Embedding raw LaTeX blocks for figures or theorems
- "/write-pandoc-markdown": loads the full style guide explicitly

## See Also

- [Write Markdown](../write-markdown/README.md): GitHub Flavored Markdown for non-academic documents
- [Write Math](../write-math/README.md): mathematical exposition for the prose body
- [Write LaTeX](../write-latex/README.md): the LaTeX target the Pandoc build emits
- [All plugins](../../README.md)
