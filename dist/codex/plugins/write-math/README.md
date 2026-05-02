# Write Math

Mathematical writing and exposition guide based on Tao, Knuth, Halmos, and other leading references.

**Type:** Skill
**Trigger:** `/write-math` (also activates automatically)

## Installation

Add the [`cboone/cboone-cc-plugins`](https://github.com/cboone/cboone-cc-plugins) marketplace in Claude Code:

```text
/plugin marketplace add cboone/cboone-cc-plugins
```

Then select **Write Math** from the available plugins.

## What It Does

Provides mathematical writing conventions for clarity, notation discipline, theorem and proof structure, paper organization, and revision workflow. Activates automatically when producing or discussing mathematical content in any venue, including LaTeX or Pandoc Markdown files, Lean docstrings with mathematical content, and chat-response proof sketches.

Includes a condensed essential checklist plus comprehensive references on notation, theorem-and-proof structure, paper structure, English usage, reader-centered writing, citations, and revision process.

## Usage

```text
/write-math
```

The skill also activates automatically when Claude Code detects mathematical exposition work (LaTeX, Pandoc Markdown, Lean docstrings, theorem statements, proof sketches).

## Examples

- Drafting a theorem statement or proof: activates automatically
- Writing a paper introduction or notation table: activates automatically
- "explain why this proof goes through": activates automatically when responding
- "/write-math": loads the full style guide explicitly

## See Also

- [Write LaTeX](../write-latex/README.md): typesetting conventions for `.tex` files
- [Write Pandoc Markdown](../write-pandoc-markdown/README.md): Pandoc Markdown for academic papers
- [Write Formalization Roadmap](../write-formalization-roadmap/README.md): structuring multi-milestone proof projects
- [All plugins](../../../../README.md)
