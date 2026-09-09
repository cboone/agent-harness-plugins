<!--
SPDX-FileCopyrightText: 2026 Christopher Boone
SPDX-License-Identifier: CC-BY-4.0
-->

# Example Flows

Two worked transcripts. The first is Bootstrap mode against a fresh Lean repo; the second is Maintain mode catching a single drift item on an already-covered repo.

## Example A: Bootstrap mode on a fresh Lean-plus-prose repo

Scenario: a brand-new repository with Lean code under `src/`, Python scripts under `bin/`, a `papers/1-demo/` Pandoc-paper subtree, and no licensing at all. The user says "bootstrap licensing for this repo."

### Run

1. **Precondition check.**
   - `reuse --version` -> present.
   - Content detection: Lean (`lakefile.toml`, `src/*.lean`), Python (`bin/*.py`), Pandoc paper (`papers/1-demo/main.md`). No fork lineage. No bundled third-party material today.
2. **Policy freeze.** Propose:
   - Lean code: `Apache-2.0` (inline)
   - Python / shell substantive code: `MIT` (inline)
   - Prose (project-authored Markdown, `.bib`, `NOTICE`): `CC-BY-4.0` (REUSE.toml prose group)
   - Infrastructure config (Makefile, `lakefile.toml`, `pyproject.toml`, dotfiles, YAML, JSONC): `MIT` (REUSE.toml config group)
   - Generated artifacts (lock files, `lean-toolchain`, Pandoc `.tex`, `.ics`): `CC0-1.0` (REUSE.toml generated group)
   - No CoC today -> skip `CC-BY-SA-4.0`.
   - No reference material today -> skip `LicenseRef-Reference-Material`.
     User confirms.
3. **License-text normalization.**
   - Run `reuse download Apache-2.0 MIT CC-BY-4.0 CC0-1.0`. `LICENSES/` now has four canonical files, all with correct SPDX-identifier casing.
   - `reuse lint` reports "Missing X files have no licensing information" but no "bad license filename" errors.
4. **`NOTICE`.**
   - Author using the template. Names the project, records copyright, lists the four licenses and their `LICENSES/*.txt` files (CC0 gets the conditional paragraph because generated artifacts exist), notes no fork or bundled third-party material, names the standard carve-outs, ends with the anti-override paragraph.
   - Mirror in `README.md`'s `## License` section.
5. **Root `REUSE.toml`.**
   - Prose-group annotation covering `NOTICE`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `.github/**/*.md`, `docs/**/*.md`, `papers/**/*.md`, `papers/**/*.bib`. Precedence `aggregate`.
   - Config-group annotation covering `Makefile`, `**/*.toml`, `**/*.yaml`/`**/*.yml`, `**/*.jsonc`, `.editorconfig`, `.gitignore`, `.gitattributes`, `cspell-words.txt`, `REUSE.toml` itself. Precedence `aggregate`. License `MIT`.
   - Generated-group annotation covering `**/lake-manifest.json`, `**/lean-toolchain`, `papers/*/main.tex`, and any script-output JSON/ICS paths. Precedence `override`. License `CC0-1.0`. `SPDX-FileCopyrightText = "NONE"`.
   - Structural-group annotation covering `**/.gitkeep`. Precedence `override`. License `MIT`.
   - No CoC block (no CoC).
   - No reference-material block (no bundle).
   - The `REUSE.toml` file is covered by the config group — no inline header at its top.
6. **SPDX placement (inline coverage only).**
   - `reuse annotate --copyright "2026 <user>" --license Apache-2.0 src/**/*.lean` -> inline `/- ... -/`.
   - `reuse annotate --copyright "2026 <user>" --license MIT bin/**/*.py` -> inline `#` after shebangs.
   - No inline headers on `lakefile.toml`, `Makefile`, `pyproject.toml`, `.gitignore`, `.editorconfig`, `cspell-words.txt`, CI workflows — the REUSE.toml config group covers them.
   - No sidecars on `lean-toolchain`, `lake-manifest.json`, generated `papers/*/main.tex` — the REUSE.toml generated group covers them.
   - Prose Markdown (`papers/1-demo/main.md`, `README.md`, etc.) is covered by the REUSE.toml prose group — no inline headers, no sidecars.
7. **Verification.**
   - `reuse lint` -> zero errors.
   - Repo lint -> clean.
   - Build check -> clean.
8. **Plan document?** Repo is small (one paper, thin Lean tree). Skip.
9. **Commit ladder.** Four commits land: `docs: update README and licenses` (adds `LICENSES/*.txt` × 4); `docs: add NOTICE and REUSE.toml with prose/config/generated/structural groups`; `chore(research): add SPDX to Lean sources`; `chore(tooling): add SPDX to non-Lean substantive code`.

### Deliverables

- `LICENSES/Apache-2.0.txt`, `LICENSES/MIT.txt`, `LICENSES/CC-BY-4.0.txt`, `LICENSES/CC0-1.0.txt`.
- `NOTICE`.
- `REUSE.toml` with prose, config, generated, and structural groups.
- Inline SPDX on Lean and Python sources only.
- Zero sidecars.
- Clean `reuse lint`.

## Example B: Maintain mode catching a single drift

Scenario: `zhang-yeung-inequality` is already covered (per-file sidecars on two reference PDFs, inline headers on Lean and configs). A recent commit added a new Python tool under `bin/analyze.py` without an SPDX header. User says "audit license coverage."

### Run

1. `reuse lint` reports: `bin/analyze.py has no copyright and licensing information.`
2. Read `bin/analyze.py` — classify via the matrix: Python, commentable, hand-authored, not prose -> **inline `#`** comment block.
3. Apply: `reuse annotate --copyright "2026 <user>" --license MIT bin/analyze.py`.
4. Re-run `reuse lint` — clean.
5. Repo lint — clean (cspell and markdownlint untouched by the change).
6. Commit: `chore(tooling): add SPDX header to bin/analyze.py`.

### What the skill did **not** do

- Did not open the prose group in `REUSE.toml` (nothing in the prose path list changed).
- Did not touch `NOTICE` or `README.md` (split unchanged).
- Did not emit a plan document (Maintain mode, single-item scope).
- Did not ask the user to confirm the license bucket — the matrix answered it.

## Example C: Maintain mode catching structural drift

Scenario: `non-shannon-inequalities` has per-file sidecars scattered across config files (`Makefile.license`, `lakefile.toml.license`, `cspell.jsonc.license`, `.editorconfig.license`, `.gitignore.license`, `.markdownlint-cli2.jsonc.license`, `pyproject.toml.license`), generated artifacts (`uv.lock.license`, `lake-manifest.json.license`, `lean-toolchain.license`), placeholders (six `.gitkeep.license`), and project-authored Markdown (`NOTICE.license`, `CODE_OF_CONDUCT.md.license`, many `*.md.license`). Plus inline `<!-- SPDX-* -->` blocks in every project-authored `.md`. The user says "audit REUSE against the matrix."

### Run

1. `reuse lint` reports zero errors — but this is structural drift against the matrix, not a lint failure.
2. Punch list:
   - **Config sidecars.** Delete all seven. The REUSE.toml config group covers them; no inline headers needed.
   - **Generated-artifact sidecars.** Delete `uv.lock.license`, `lake-manifest.json.license`, `lean-toolchain.license`. Add `LICENSES/CC0-1.0.txt`. The REUSE.toml generated group covers them under CC0.
   - **Placeholder sidecars.** Delete six `.gitkeep.license` files. The REUSE.toml structural group covers them under the repo's code-bucket license.
   - **Prose sidecars and inline.** Delete `NOTICE.license` and every `*.md.license`; strip `<!-- SPDX-* -->` from project-authored Markdown. The REUSE.toml prose group covers them.
3. Commit sequence, each commit leaves `reuse lint` clean:
   - `docs: normalize LICENSES/` — add `LICENSES/CC0-1.0.txt`.
   - `docs: extend REUSE.toml with config/generated/structural groups` — update `REUSE.toml` to cover all three bucket classes.
   - `chore(tooling): fold config sidecars into config group` — delete the seven `.license` files.
   - `chore: fold generated-artifact sidecars into CC0 group` — delete lock/toolchain `.license` files.
   - `chore: fold .gitkeep sidecars into structural group` — delete the six placeholder `.license` files.
   - `docs: fold Markdown sidecars and inline SPDX into prose group` — delete every `*.md.license`, strip every `<!-- SPDX-* -->` HTML-comment block in project-authored `.md`.

### Why split into many commits

Each migration affects a different file class and has a different review audience. Landing them separately means a reviewer can veto (say) the CC0 change without blocking the `.gitkeep` fix. Each commit is small and mechanical; collectively they represent a non-trivial policy shift and deserve separate review slots.
