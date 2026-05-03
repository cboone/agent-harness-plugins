
# BibTeX and Bibliography Management

Comprehensive reference for managing bibliographies in LaTeX, covering BibTeX best practices, entry formatting, capital protection, author names, DOIs, journal abbreviations, and the comparison between BibTeX and BibLaTeX. Based on Nicholas Higham's BibTeX posts (2015 and 2021) and standard LaTeX bibliography conventions.

## Capital Protection

BibTeX lowercases titles according to the bibliography style. To prevent proper nouns, acronyms, and other terms from being lowercased, wrap them in braces inside the title field.

```bibtex
% Correct: protected capitals
title = {A {B}ayesian Approach to {GPU}-Accelerated {Monte Carlo} Simulation},

% Wrong: will be lowercased to "a bayesian approach to gpu-accelerated monte carlo simulation"
title = {A Bayesian Approach to GPU-Accelerated Monte Carlo Simulation},
```

### What to protect

- **Proper nouns**: `{B}ayesian`, `{G}aussian`, `{M}arkov`, `{E}uclidean`, `{N}ewton`
- **Acronyms**: `{GPU}`, `{CPU}`, `{HTML}`, `{DNS}`, `{NIST}`, `{IEEE}`
- **Multi-word proper names**: `{Monte Carlo}`, `{Latin America}`, `{United States}`
- **Chemical formulas**: `{CO}$_2$`, `{NaCl}`
- **Software names**: `{TensorFlow}`, `{Python}`, `{MATLAB}`

### Brace placement

Wrap individual letters or words, not the entire title. Wrapping the entire title in an extra set of braces prevents the bibliography style from applying any case changes at all, which may produce inconsistent formatting across entries:

```bibtex
% Good: selective protection
title = {Stochastic Gradient Descent for {B}ayesian Optimization},

% Bad: disables all case formatting
title = {{Stochastic Gradient Descent for Bayesian Optimization}},
```

## Author Names

### Basic format

BibTeX understands two name formats:

```bibtex
% "First Last" format
author = {Donald E. Knuth and Leslie Lamport},

% "Last, First" format (preferred for unambiguous parsing)
author = {Knuth, Donald E. and Lamport, Leslie},
```

Use the "Last, First" format when surnames could be ambiguous.

### Multi-word surnames

Wrap multi-word surnames in braces so BibTeX does not split them incorrectly:

```bibtex
author = {{De Boor}, Carl},
author = {{Van der Waerden}, Bartel Leendert},
author = {{da Silva}, Maria},
```

Without braces, BibTeX would treat "De" or "Van" as a first/middle name.

### Corporate and institutional authors

Wrap the entire name in braces to prevent BibTeX from parsing it as "Last, First":

```bibtex
author = {{National Institute of Standards and Technology}},
author = {{World Health Organization}},
author = {{Google Brain Team}},
```

### Many authors

For papers with many authors, list them all. Do not use "and others" in the author field. The bibliography style controls truncation (e.g., "et al." after three names). Let the style handle it.

```bibtex
% Correct: list all authors
author = {Smith, Alice and Jones, Bob and Williams, Carol and Brown, David},

% Wrong: manual truncation
author = {Smith, Alice and others},
```

### Junior suffixes

Use the four-part name format:

```bibtex
author = {Ford, Jr., Henry},
```

## DOI: Always Include

Every entry that has a DOI should include it. DOIs are permanent identifiers that resolve even when URLs change.

### Format

Use the bare DOI, not the full URL:

```bibtex
% Correct
doi = {10.1109/SP.2019.00021},

% Wrong: full URL in doi field
doi = {https://doi.org/10.1109/SP.2019.00021},
```

The bibliography style or `hyperref` package handles converting the DOI to a clickable link.

### Hyperref linking

With `hyperref` loaded, DOIs become clickable links automatically when using styles that support them. For custom formatting:

```latex
\usepackage{hyperref}
\usepackage{doi}  % formats DOI fields as clickable links
```

### DOI to BibTeX

The service at `https://doi2bib.org` generates BibTeX entries from DOIs. Paste a DOI and get a ready-to-use entry. Always review the generated entry for:

- Missing capital protection in titles
- Inconsistent author name formatting
- Missing or incorrect entry type

## Journal Abbreviations

Use MathSciNet standard abbreviation strings for journal names. This ensures consistency across your bibliography. The full list is available at: `https://mathscinet.ams.org/msnhtml/serials.pdf`

### Using @String definitions

Define abbreviation strings at the top of your `.bib` file (or in a separate strings file) and reference them without braces:

```bibtex
@String{j-ieee-sp   = "IEEE Symp. Secur. Privacy"}
@String{j-usenix    = "USENIX Secur. Symp."}
@String{j-cacm      = "Commun. ACM"}
@String{j-tocs      = "ACM Trans. Comput. Syst."}

@inproceedings{smith2024passwords,
  author    = {Smith, Alice},
  title     = {A New Approach to Password Security},
  booktitle = j-ieee-sp,
  year      = {2024},
}
```

Note that string references are not wrapped in braces or quotes. BibTeX expands them during processing.

### Benefits of string abbreviations

- **Consistency**: every reference to the same venue uses the same abbreviation
- **Easy updates**: change the string definition once to update all entries
- **Compact entries**: shorter `.bib` file lines

## Back-references

The `backref` package adds page numbers to bibliography entries showing where each reference is cited:

```latex
\usepackage[pagebackref]{hyperref}
% or
\usepackage{backref}
```

This produces entries like:

> [1] A. Smith, "Password Security," IEEE S&P, 2024. (Cited on pages 3, 7, 12.)

This is invaluable for long documents, helping readers trace how each reference is used.

## Entry Types

### When to use each type

| Entry type       | Use for                                                           |
| ---------------- | ----------------------------------------------------------------- |
| `@article`       | Journal papers (with volume, number, pages)                       |
| `@inproceedings` | Conference papers (with booktitle for the conference name)        |
| `@book`          | Complete books (with publisher, address)                          |
| `@incollection`  | Chapters in edited books (with booktitle for the book title)      |
| `@techreport`    | Technical reports from institutions                               |
| `@phdthesis`     | Doctoral dissertations                                            |
| `@mastersthesis` | Master's theses                                                   |
| `@misc`          | Anything that does not fit above (preprints, software, web pages) |
| `@unpublished`   | Manuscripts not yet published (with a note field)                 |

### Common mistakes

- Using `@misc` for conference papers (use `@inproceedings`)
- Using `@article` for conference papers (conferences use `booktitle`, not `journal`)
- Using `@inproceedings` for journal papers (journals use `journal`, not `booktitle`)
- Omitting required fields (each entry type has required and optional fields; check the BibTeX documentation)

### Example entries

```bibtex
@article{shannon1948mathematical,
  author  = {Shannon, Claude E.},
  title   = {A Mathematical Theory of Communication},
  journal = {Bell Syst. Tech. J.},
  volume  = {27},
  number  = {3},
  pages   = {379--423},
  year    = {1948},
  doi     = {10.1002/j.1538-7305.1948.tb01338.x},
}

@inproceedings{bonneau2012science,
  author    = {Bonneau, Joseph},
  title     = {The Science of Guessing: Analyzing an Anonymized
               Corpus of 70 Million Passwords},
  booktitle = {IEEE Symp. Secur. Privacy},
  pages     = {538--552},
  year      = {2012},
  doi       = {10.1109/SP.2012.49},
}

@book{knuth1997art,
  author    = {Knuth, Donald E.},
  title     = {The Art of Computer Programming},
  volume    = {2},
  edition   = {3rd},
  publisher = {Addison-Wesley},
  address   = {Reading, MA},
  year      = {1997},
}

@techreport{nist800-63b,
  author      = {{National Institute of Standards and Technology}},
  title       = {Digital Identity Guidelines: Authentication and
                 Lifecycle Management},
  institution = {NIST},
  number      = {SP 800-63B},
  year        = {2017},
  doi         = {10.6028/NIST.SP.800-63b},
}
```

## URL and Access Dates

### Typesetting URLs

Use the `url` package (or `xurl` for better line-breaking) to typeset URLs:

```latex
\usepackage{url}
% or for better line-breaking at hyphens and other characters
\usepackage{xurl}
```

In `.bib` entries:

```bibtex
@misc{owasp2023top10,
  author  = {{OWASP Foundation}},
  title   = {OWASP Top 10},
  year    = {2023},
  url     = {https://owasp.org/www-project-top-ten/},
  urldate = {2024-01-15},
}
```

### Access dates

For online sources, include `urldate` (or `note` with traditional BibTeX) to record when the URL was last accessed:

```bibtex
% With BibLaTeX
urldate = {2024-01-15},

% With traditional BibTeX (no native urldate field)
note = {Accessed: 2024-01-15},
```

## BibLaTeX vs BibTeX

### Traditional BibTeX

- Uses `.bst` style files (written in a stack-based postfix language)
- Limited to ASCII; struggles with Unicode
- Limited entry types (no native `@online`)
- Style customization requires editing or creating `.bst` files
- Widely supported; works everywhere

### BibLaTeX

- Uses LaTeX macros for style definition (much easier to customize)
- Full Unicode support via `biber` backend
- Additional entry types: `@online`, `@software`, `@dataset`, `@review`
- Fine-grained formatting control in the preamble
- `urldate` field for access dates
- Multiple bibliographies, per-chapter bibliographies, and filtered bibliographies
- Growing adoption but not yet universal

### Recommendation

For new projects where you control the toolchain, BibLaTeX with biber is the better choice. It is more powerful, more flexible, and easier to customize.

For journal submissions, use whatever the venue requires. IEEE and ACM templates use traditional BibTeX. Check the submission guidelines.

### Basic BibLaTeX setup

```latex
\usepackage[
  backend=biber,
  style=numeric,
  sorting=nyt,
  maxbibnames=99,
]{biblatex}

\addbibresource{references.bib}

% In the document body, at the end:
\printbibliography
```

### Basic BibTeX setup

```latex
\bibliographystyle{IEEEtran}  % or plain, abbrv, alpha, etc.
\bibliography{references}      % references.bib
```

## Best Practices Summary

1. **Always protect capitals** in titles for proper nouns and acronyms.
2. **Always include DOIs** when available.
3. **Use "Last, First" format** for author names, with braces around multi-word surnames.
4. **Use the correct entry type** for each reference.
5. **Use @String definitions** for journal and conference names.
6. **Review auto-generated entries** from doi2bib or Google Scholar for formatting issues.
7. **Keep one canonical `.bib` file** per project, sorted consistently.
8. **Test your bibliography** by compiling and visually inspecting the output for formatting errors, missing fields, and broken links.
