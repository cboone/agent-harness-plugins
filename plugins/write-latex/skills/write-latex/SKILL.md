---
name: write-latex
description: >-
  LaTeX mathematical typesetting style guide based on AMS, IEEE, ISO 80000-2,
  and Knuth conventions. Use when: (1) writing or editing .tex files, (2)
  writing raw LaTeX blocks in Pandoc Markdown, (3) setting up LaTeX preambles
  or macros, (4) working with BibTeX files, or (5) reviewing LaTeX code for
  typesetting quality.
---

# Write LaTeX

Apply the LaTeX conventions from the reference files below when creating or
editing LaTeX source.

## Core Principles

1. **Semantic markup over visual hacks** -- use the right command for its
   meaning, not for its appearance
1. **Standard compliance** -- follow AMS, ISO 80000-2, and IEEE conventions
1. **No deprecated constructs** -- never use `$$`, `eqnarray`, `\def`,
   `\centerline`, `\over`, or two-letter font commands
1. **Macro discipline** -- define `\newcommand` macros for recurring notation
   so a single edit propagates everywhere

## Workflow

1. Review against the essential checklist:
   `./references/essential/checklist.md`
1. For specific questions, consult the comprehensive references below

## Reference Navigation

**Quick reviews (default):**

- `references/essential/checklist.md` -- condensed, actionable rules

**Deep dives by topic:**

- `references/comprehensive/math-typesetting.md` -- display math, environments,
  operators, delimiters, fractions, ellipsis, mathtools
- `references/comprehensive/iso-conventions.md` -- ISO 80000-2: variables,
  constants, vectors, differential notation, custom macros
- `references/comprehensive/tables.md` -- booktabs, caption placement, column
  alignment, complete examples
- `references/comprehensive/bibliography.md` -- BibTeX: capital protection,
  DOI, journal abbreviations, backref
- `references/comprehensive/packages.md` -- recommended packages with load
  order: mathtools, cleveref, hyperref, siunitx, microtype, and more
- `references/comprehensive/spacing-and-alignment.md` -- math spaces, phantom
  alignment, intertext, Knuth's @ technique
- `references/comprehensive/common-mistakes.md` -- deprecated commands and
  their modern replacements
- `references/comprehensive/figures-and-floats.md` -- graphics formats,
  subcaption, float placement, caption conventions
- `references/comprehensive/macros-and-cross-refs.md` -- macro design,
  cleveref cross-references, label prefixes
- `references/comprehensive/document-conventions.md` -- equation punctuation,
  enumitem lists, unbreakable spaces, hyperref metadata

## Sources

- Downes, M. and Beeton, B. _Short Math Guide for LaTeX_. AMS, 2017.
- IEEE. _Math Typesetting Guide for LaTeX Users_.
- Higham, N. J. Blog posts on tables, BibTeX, packages, spacing, ISO
  typesetting, ellipses, lists, and book writing. 2013--2021.
- Beeton, B. "How to Typeset Equations in LaTeX." _TUGboat_ 18(1), 1997.
- Chen, E. _LaTeX Style Guide_. web.evanchen.cc.
- Ensenbach, M. et al. _l2tabu: A List of Don'ts in LaTeX_.
- Voss, H. _Mathmode_. CTAN.
- Mittelbach, F. and Fischer, U. _The LaTeX Companion_. 3rd ed., 2024.
- MathSciNet. _Serials Abbreviations_.
