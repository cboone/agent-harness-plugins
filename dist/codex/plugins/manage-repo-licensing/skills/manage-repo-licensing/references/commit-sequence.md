<!--
SPDX-FileCopyrightText: 2026 Christopher Boone
SPDX-License-Identifier: CC-BY-4.0
-->

# Commit Sequence

The four prior rollouts (`strength-model`, `shannon-entropy`, `zhang-yeung-inequality`, `non-shannon-inequalities`) converged on the following commit ladder. Bootstrap mode executes the full ladder; Maintain mode uses a subset; New-file drop lands a single commit.

## Bootstrap ladder (full)

Each step is a single commit. Do not batch unrelated steps together — review value collapses when the diff mixes licenses, headers, and configs.

1. **`docs: add licensing rollout plan`** — commit `docs/plans/todo/YYYY-MM-DD-license-notice-spdx-rollout.md` first, before any edits. Only emitted when the plan document is warranted (see SKILL.md Section 9). Skip this step when scope does not justify a plan document.
2. **`docs: update README and licenses`** — populate `LICENSES/` with the full canonical text of every license in the confirmed split, with SPDX-correct filenames. Update `README.md`'s `## License` section to match the split. No per-file headers yet.
3. **`docs: add notice and license split`** — author `NOTICE`. Add the root `REUSE.toml` with the required prose-group annotation plus any conditional blocks (CoC, reference material, fork lineage). This commit unlocks prose coverage for every `.md` file covered by the group.
4. **`chore(research): add SPDX to Lean sources`** — inline Apache-2.0 headers (`/- ... -/`) on every `.lean` file, and on any other substantive source files whose SPDX tag should travel with the file (hand-authored `.tex` macros, `.lua` filters, Python figure scripts). Batched via `reuse annotate`.
5. **`chore(tooling): add SPDX to non-Lean substantive code`** — inline MIT headers on Python scripts under `bin/`, shell scripts, any non-Lean source files with substantive logic. Skip entries already covered in commit 4.
6. **`chore: add CC0 coverage for generated artifacts`** — no inline edits; the REUSE.toml generated-group annotation from commit 3 already covers lock files, `lean-toolchain`, Pandoc-generated `.tex`, and script-generated JSON/ICS/JSONL. This commit exists only if the generated-group paths were not finalized in commit 3 (for example, a new generated tree was discovered during rollout).
7. **`docs(refs): add LicenseRef-Reference-Material coverage`** — add `LICENSES/LicenseRef-Reference-Material.txt`, extend REUSE.toml with the reference-material annotation block, and update NOTICE to call out the carve-out. Skip if `references/` has no bundled third-party material.

## Maintain ladder (subset)

For drift audits:

1. **`docs: normalize LICENSES/`** — rename mis-cased license filenames (for example, `APACHE-2.0.txt` -> `Apache-2.0.txt`). Use `git mv` so history follows. Add any new license texts the ladder will need (`CC0-1.0.txt`, `LicenseRef-Reference-Material.txt`).
2. **`docs: add REUSE.toml with prose and config groups`** — when the repo is missing `REUSE.toml` entirely or is missing the prose / config groups. Extend existing path lists rather than authoring duplicates.
3. **`docs: fold Markdown sidecars and inline SPDX into prose group`** — delete `NOTICE.license`, `*.md.license` sidecars for project-authored Markdown. In the same commit, strip inline `<!-- SPDX-* -->` blocks from those Markdown files.
4. **`chore(tooling): fold config sidecars and inline SPDX into config group`** — delete every `.license` sidecar on hand-authored config files (`Makefile.license`, `lakefile.toml.license`, `cspell.jsonc.license`, `cspell-words.txt.license`, `.editorconfig.license`, `.gitignore.license`, `pyproject.toml.license`, etc.); strip any inline SPDX blocks from those files. The REUSE.toml config group covers them.
5. **`chore: fold .gitkeep sidecars into REUSE.toml structural group`** — delete every `.gitkeep.license` in favor of the `**/.gitkeep` annotation. One commit regardless of count.
6. **`chore: fold generated-artifact sidecars into CC0 group`** — delete `uv.lock.license`, `lake-manifest.json.license`, `lean-toolchain.license`, generated `.tex.license`, figure `*.json.license`, benchmark `*.jsonl.license`, etc. The REUSE.toml generated group (with `CC0-1.0`) covers them.
7. **`docs: add LicenseRef-Reference-Material coverage`** — when the repo bundles third-party material but lacks the LicenseRef text or path coverage.
8. **`chore: guard SPDX quotes in prose with REUSE-IgnoreStart/End`** — wrap passages that literally quote SPDX-License-Identifier syntax in Markdown and docstrings with `<!-- REUSE-IgnoreStart -->` / `<!-- REUSE-IgnoreEnd -->`. Required for planning documents, the skill's own docs, and any README that includes SPDX examples.
9. **`chore: fix orphaned sidecars`** — delete `.license` sidecars whose covered file no longer exists.

Each fix lands in its own commit. Running multiple items together blurs review.

## New-file drop

One commit, descriptive subject. Examples:

- **`chore(tooling): add SPDX header to bin/new-script.py`**
- **`docs: extend REUSE.toml prose group to cover papers/11/`**
- **`docs: extend REUSE.toml generated group to cover new figure JSON`**

## Commit subject style

- Use Conventional Commits types (`docs`, `chore`, `build`).
- Keep the subject line under 70 characters.
- Do not squash licensing commits into a giant "chore: add licensing" blob. The whole point of the ladder is that each layer is independently reviewable.

## Branch strategy

Licensing rollouts run on their own branch and land as a single PR. Individual commits map to the ladder steps. Do not merge-commit; rebase to keep the ladder linear.
