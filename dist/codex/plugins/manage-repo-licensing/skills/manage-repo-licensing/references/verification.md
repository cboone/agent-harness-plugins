<!--
SPDX-FileCopyrightText: 2026 Christopher Boone
SPDX-License-Identifier: CC-BY-4.0
-->

# Verification

Run every bootstrap, maintain, or new-file-drop commit through the invariants below before declaring the work done.

## 1. `reuse lint`

From the repo root:

```bash
reuse lint
```

(or `uvx reuse-tool lint` if not installed persistently.)

Zero errors. Not "only low-severity" -- zero. Common errors and what they mean:

| Error                                                                 | Likely cause                                                                                              |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `<path> has no copyright and licensing information`                   | File lacks inline SPDX, sidecar, and REUSE.toml coverage.                                                 |
| `<path> has copyright information, but no licensing information`      | Only one of the two SPDX tags present; both are required.                                                 |
| `License <SPDX-ID> in <path> is not included in the LICENSES/ folder` | License-text file missing or mis-cased in `LICENSES/`.                                                    |
| `Unused license <path>`                                               | License-text file present but no file claims it. Either add a file using that license or remove the text. |
| `Could not parse <path>`                                              | Malformed SPDX in a header or sidecar. Re-check syntax.                                                   |

Fix the error, do not suppress it. `reuse lint --quiet` is for CI plumbing, not for rolling past real failures.

## 2. Repo-local lint

Run whatever the project's `make lint` / `npm run lint` / `ruff` / `cargo fmt --check` equivalent is. Licensing edits can introduce line-length, whitespace, or comment-style violations that project linters catch and `reuse lint` does not.

Typical invocation:

```bash
make lint
```

## 3. Build or proof check

If edits touched source-bearing files (Lean, Python, shell, `.tex`), run the build / proof check. An SPDX block inserted at the wrong position can break imports, shebangs, or LaTeX preambles.

For a Lean project, this is typically `make check-proofs` (or whatever the project's wrapper target is), which runs `lake build`, `lake test`, and any project-specific proof-boundary check. For a Go project: `make build && make test`. For a Python project: `make test` or the equivalent. The principle is the same: the licensing edit should not have changed any compiled artifact's behavior.

## 4. Read-through

Re-read `README.md`, `NOTICE`, and a representative sample of per-file headers together. They must agree on the split. Things to catch during read-through:

- A license listed in `NOTICE` but not in `README.md`'s `## License` section, or vice versa.
- A license text file in `LICENSES/` that no file in the repo claims.
- A `NOTICE` carve-out paragraph that names a path no longer in the repo.
- A prose-group path list in `REUSE.toml` that includes a deleted directory.
- A per-file inline header that contradicts the REUSE.toml prose group (an actual override is fine; an accidental override is drift).

## 5. CI (optional but recommended)

For repos that run CI, add a `reuse lint` step to the lint workflow. Example (GitHub Actions):

```yaml
- name: REUSE compliance
  uses: cboone/gh-actions/actions/run-reuse@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0
```

or inline:

```yaml
- name: REUSE compliance
  run: uvx reuse-tool lint
```

This prevents future drift from landing silently.

`run-reuse` installs reuse 6.2.0 from a hash-pinned requirements file, so there is no input that holds it at 5.x. A repository that passed under 5.0.2 can fail under 6.2.0 for three reasons, none of which is a change in what REUSE requires:

- `lint` reads whole files, where 5.x stopped after the first 4 KiB. Copyright or license text deeper in a file is now found and attributed. Wrap the passage in `REUSE-IgnoreStart` and `REUSE-IgnoreEnd`. Vendored headers, license blocks quoted inside documentation, and test fixtures are the usual sources, and this is the one most likely to bite.
- A new Invalid SPDX License Expressions criterion flags an expression that is not valid SPDX grammar, which was previously ignored. Correct the expression, or the license identifier it names.
- Bad licenses now considers only `LICENSES/`. This narrows what is reported rather than widening it, so a repository relying on it to flag files elsewhere loses that signal.

## Common verification gotchas

1. **License text that doesn't match the canonical SPDX version.** `reuse download <SPDX-ID>` places canonical text; hand-downloaded text from a search engine may have extra whitespace, removed section numbers, or Unicode quirks that upset some tooling. Prefer `reuse download`.
2. **Trailing-whitespace diffs when `reuse annotate` inserts headers.** Project formatters may strip or reformat. Run the formatter after annotating and before committing.
3. **Sidecars with no target file.** Orphan `.license` sidecars are a `reuse lint` error. If you delete a file, delete its sidecar in the same commit.
4. **`.lean` comment block vs. `lake build`.** Lean's `/- ... -/` at the very top of a file is fine. If the header comes before the module docstring (`/-! ... -/`), that is also fine. If it falls between imports and the first declaration, Lean may parse it but style will drift -- keep SPDX strictly at the top.
5. **YAML front-matter clashes.** For Pandoc Markdown files that have YAML front matter (`--- ... ---` at the top), the REUSE.toml prose group is still the right coverage, not an inline HTML comment above the front matter. A leading `<!-- SPDX-* -->` block before the YAML breaks Pandoc's front-matter detection.
