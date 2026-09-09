# Paper-Backed Stubs

When paper-backed mode is enabled, create these additional directories and files.

## Directories

```text
references/papers/
references/extractions/
references/transcriptions/
docs/plans/todo/
docs/plans/done/
```

Create `.gitkeep` files in empty directories that should remain tracked.

## references/papers/README.md

```markdown
# Papers

Place source PDFs, bibliographic notes, and citation metadata for papers that guide the formalization here.
```

## references/extractions/README.md

```markdown
# Extractions

Place extracted theorem statements, definitions, and proof outlines here. Treat extraction files as reference material, not generated Lean source.
```

## references/transcriptions/README.md

```markdown
# Transcriptions

Place verbatim or near-verbatim transcriptions here. Keep generated or mechanically extracted text out of proof modules until it has been reviewed.
```

## references/papers.bib

```bibtex
@comment{Add paper bibliography entries here as the formalization starts citing them.}
```

## docs/plans/todo/.gitkeep

```text

```

## docs/plans/done/.gitkeep

```text

```

## Notes

- The generated markdownlint and cspell configs already ignore extraction and transcription trees.
- Add author surnames and domain vocabulary from `references/papers.bib` to `cspell-words.txt` when citations are added.
