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

Zero errors. Not "only low-severity" — zero. Common errors and what they mean:

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
  uses: fsfe/reuse-action@v5
```

or inline:

```yaml
- name: REUSE compliance
  run: uvx reuse-tool lint
```

This prevents future drift from landing silently.

## Common verification gotchas

1. **License text that doesn't match the canonical SPDX version.** `reuse download <SPDX-ID>` places canonical text; hand-downloaded text from a search engine may have extra whitespace, removed section numbers, or Unicode quirks that upset some tooling. Prefer `reuse download`.
2. **Trailing-whitespace diffs when `reuse annotate` inserts headers.** Project formatters may strip or reformat. Run the formatter after annotating and before committing.
3. **Sidecars with no target file.** Orphan `.license` sidecars are a `reuse lint` error. If you delete a file, delete its sidecar in the same commit.
4. **`.lean` comment block vs. `lake build`.** Lean's `/- ... -/` at the very top of a file is fine. If the header comes before the module docstring (`/-! ... -/`), that is also fine. If it falls between imports and the first declaration, Lean may parse it but style will drift — keep SPDX strictly at the top.
5. **YAML front-matter clashes.** For Pandoc Markdown files that have YAML front matter (`--- ... ---` at the top), the REUSE.toml prose group is still the right coverage, not an inline HTML comment above the front matter. A leading `<!-- SPDX-* -->` block before the YAML breaks Pandoc's front-matter detection.
