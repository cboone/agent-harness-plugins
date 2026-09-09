<!--
SPDX-FileCopyrightText: 2026 Christopher Boone
SPDX-License-Identifier: CC-BY-4.0
-->

# `LicenseRef-Reference-Material.txt` Canonical Text

This is the shared canonical text for `LICENSES/LicenseRef-Reference-Material.txt`. Use it identically across repos that bundle third-party reference material, adjusting only the path names in the first paragraph to match the repo's actual layout.

## Canonical text

```text
This repository bundles certain PDFs and verbatim transcriptions under `references/papers/` and `references/transcriptions/` as reference material for study, verification, and scholarly context.

No copyright license to modify, redistribute, or republish those materials is granted by this repository. Copyright remains with the original authors and/or publishers, as identified in the materials themselves.

Where use beyond local reference, quotation, or other applicable legal exceptions is desired, consult the original publication or publisher for the governing terms.
```

## Path adjustments

- Most repos: keep `references/papers/` and `references/transcriptions/` as in the canonical text.
- If the repo uses different directory names, update only the first paragraph. Preserve the second and third paragraphs verbatim — they are the substantive statement.

## Scope (what goes under `LicenseRef-Reference-Material`)

Covered:

1. `references/papers/**/*.pdf` — third-party source PDFs.
2. `references/papers/**/*.html` — saved publisher HTML snapshots.
3. `references/extractions/**` — Mathpix Markdown, per-line OCR JSON, legacy pdftotext caches. These faithfully reproduce third-party content.
4. `references/transcriptions/**/*.md` — verbatim transcriptions of theorem statements, definitions, and excerpts.

Not covered (stays under project licenses, usually `CC-BY-4.0`):

1. `references/summaries/**/*.md` — one-page editorial writeups.
2. `references/reviews/**/*.md` — literature reviews.
3. `references/datasets/**/*.md` — dataset cards.
4. `references/papers.bib` — project-curated bibliography. Bibliographic facts are thin data and not independently copyrightable; curation and keying are project-authored.
5. `references/README.md` and other navigation prose.

Ambiguous:

- `references/bibliographies/**/*.md` — parsed references from third-party papers. Thin factual data plus project-authored cleanup. Default to `CC-BY-4.0`. Demote individual files to `LicenseRef-Reference-Material` only if they contain substantial verbatim prose from a third-party paper.

## Placement mechanism: scale-tiered

<!-- REUSE-IgnoreStart -->

1. **Small curated collections (~20 files or fewer).** Per-file `.license` sidecars. Each sidecar carries actual `SPDX-FileCopyrightText` lines for author(s) and publisher where known, plus `SPDX-License-Identifier: LicenseRef-Reference-Material`.
2. **Larger collections (more than ~20 files).** A single `REUSE.toml` `[[annotations]]` block covering the path glob with `SPDX-FileCopyrightText = "Original authors and publishers"` and `SPDX-License-Identifier = "LicenseRef-Reference-Material"`. Per-paper authorial attribution already lives in `references/papers.bib`.

<!-- REUSE-IgnoreEnd -->

Threshold is soft. Prefer the `REUSE.toml` approach whenever per-file sidecar maintenance would drift from the bibliography.

## Per-work `LicenseRef-*` exceptions

Allowed only when both conditions hold:

1. The work has unusual prominence in the repository (for example, it is the single primary source that the repository formalizes or reconstructs).
2. The `LicenseRef-*.txt` wording needs to be specific to that work beyond what the shared `LicenseRef-Reference-Material` expresses.

Every such exception must be justified in `NOTICE`. Otherwise, fold the work into the shared umbrella.

Known good example: `LicenseRef-Claude-Shannon-1948-Reference` in `shannon-entropy`, because the repo is a forked formalization of Shannon's 1948 paper and the Shannon text needs its own carve-out wording.
