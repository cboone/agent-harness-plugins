---
name: manage-repo-licensing
description: >-
  Bootstrap, audit, and maintain REUSE-style mixed-license coverage in a
  repository: populate `LICENSES/`, write a root `NOTICE`, wire a root
  `REUSE.toml`, apply SPDX headers or sidecars to files, and keep
  `reuse lint` clean. Use when the user says "license this repo",
  "bootstrap licensing", "add SPDX headers", "normalize LICENSES",
  "audit license coverage", "REUSE lint", "fix REUSE", "add a NOTICE",
  "set up multi-license", "this new file needs a license header", or any
  variant involving SPDX, REUSE, `.license` sidecars, CC-BY, or dual
  licensing in a repo-maintenance context. Do not fire for legal
  interpretation of license text or for third-party dependency licensing
  questions.
---
<!--
SPDX-FileCopyrightText: 2026 Christopher Boone
SPDX-License-Identifier: CC-BY-4.0
-->

# Manage Repo Licensing

Encode the REUSE-style mixed-license workflow that has converged across four sibling repos (`strength-model`, `shannon-entropy`, `zhang-yeung-inequality`, `non-shannon-inequalities`). The skill is a structured companion for these rollouts: it frames policy, standardizes placement, and drives verification. It is not an automated sweeper.

## Core Invariants

Every run, regardless of mode, honors these rules. They are the lessons from the four prior rollouts.

1. **Policy is frozen before edits.** Surface the license split, the fork-lineage question, and the reference-material scope, and wait for user confirmation before touching any file.
2. **License-text filenames are normalized first.** `LICENSES/<SPDX-ID>.txt` must match the SPDX identifier byte-for-byte (case-sensitive). Fix mis-cased filenames (`APACHE-2.0.txt` -> `Apache-2.0.txt`) before any annotation pass — otherwise `reuse lint` will flag every tag.
3. **Placement is decided by file type, not by repo convention.** Use the standardized matrix in `references/file-type-matrix.md`. Existing divergence is drift to migrate.
4. **`REUSE.toml` is the default coverage surface.** Every repo ships one with at least prose, config, generated, and structural groups (plus conditional CoC and reference-material blocks). Inline SPDX is reserved for substantive source code; per-file `.license` sidecars are a narrow residual. Config files (`Makefile`, `lakefile.toml`, `pyproject.toml`, `cspell-words.txt`, dotfiles, YAML, JSONC) and generated artifacts (lock files, `lean-toolchain`, Pandoc output, regenerated JSON/ICS) both fall in `REUSE.toml`, not inline or sidecar.
5. **Rollouts advance in small, reviewable commits.** Use the ladder in `references/commit-sequence.md`. Do not squash.
6. **`reuse lint` must be clean when done.** Plus any repo-local checks (e.g. `make lint`, `make check-proofs`).
7. **Third-party bundled reference material is covered, not excluded.** It uses `LicenseRef-Reference-Material` (shared canonical text) with scale-tiered placement — per-file sidecars for small curated collections (~20 or fewer), a `REUSE.toml` glob for larger ones. Per-work `LicenseRef-*` exceptions require explicit justification in `NOTICE`.
8. **Comments live where required, nowhere else.** No `NOTICE.license` sidecar. No `*.md.license` sidecars or HTML-comment SPDX inside project-authored Markdown — both are absorbed by the `REUSE.toml` prose group.
9. **`NOTICE` is a summary, not an override.** Never write wording that implies every file is under one license.
10. **Prose that documents SPDX syntax is a hazard.** Any project-authored Markdown that contains the literal string `SPDX-License-Identifier` followed by a colon (or a similar tag) outside a REUSE-ignore region is parsed by `reuse` as a real declaration and usually corrupts the lint report. Wrap such passages in `<!-- REUSE-IgnoreStart -->` / `<!-- REUSE-IgnoreEnd -->` HTML comments. This applies to this skill's own documentation, to any plan document that describes the workflow, and to README sections that show SPDX examples. The code-block fence does not protect the content; REUSE scans code blocks.
11. **Intentional deviations are data, not drift.** When running against a repo that is already REUSE-compliant, compare coverage to the matrix but do not flatten deliberate policy choices. Common legitimate deviations: (a) a fork preserving upstream attribution via per-file sidecars on unmodified files, dual-copyright MIT on lockfiles, or a compound license on the README; (b) a non-default code-bucket license (for example, Apache-2.0 rather than MIT for project-authored tooling); (c) per-work `LicenseRef-*` exceptions with justification in `NOTICE`; (d) explicit prose path lists instead of globs when auditability matters more than elasticity. Surface these as candidate cleanups and wait for user direction before normalizing. The defaults in Sections 2-6 are a starting point; once a repo has a working policy, changes should be additive and policy-preserving, not flattening.

## Modes

Pick the mode that matches the user's ask. Announce the mode before executing so the user can redirect.

### Mode B — Bootstrap

For a repo with no or minimal SPDX coverage.

Flow:

1. Run preconditions and content-class detection (Section 1 below).
2. Freeze policy with the user (Section 2).
3. Normalize `LICENSES/` filenames and add any missing license text (Section 3).
4. Author the root `NOTICE` (Section 4) and mirror the `## License` section in `README.md`.
5. Write the root `REUSE.toml` with the required prose-group annotation plus any conditional blocks (Section 5).
6. Apply SPDX coverage per the file-type matrix (Section 6).
7. Verify (Section 7).
8. Only emit a tracked plan document when the scope warrants one (Section 8).

Execute in commits that follow `references/commit-sequence.md`.

### Mode M — Maintain

For a repo that already has SPDX coverage and needs a drift audit or catch-up.

Flow:

1. Run `reuse lint` and capture the report.
2. Read `LICENSES/`, `NOTICE`, and `REUSE.toml` and compare against the file-type matrix.
3. Emit a punch list: bad license filenames, missing or unnecessary sidecars, inline Markdown SPDX that should fold into the REUSE.toml prose group, missing `LICENSES/LicenseRef-Reference-Material.txt`, orphaned sidecars for deleted files, policy mismatches (for example, a `.py` file carrying `Apache-2.0` in an MIT-for-Python repo).
4. **Classify each item as drift or intentional deviation.** Drift is structural mismatch with the matrix that should be migrated (stray `*.md.license` sidecars, inline SPDX on infrastructure config, `.gitkeep.license` files). Intentional deviations are fork-preserving sidecars on unmodified upstream files, dual-copyright on lockfiles, a compound license on `README.md`, a non-default code-bucket license, or a justified per-work `LicenseRef-*`. Per invariant 11, surface deviations as candidate cleanups, not drift, and wait for explicit user direction.
5. Present the punch list and proposed targeted patches before applying.
6. Apply approved fixes in small commits.
7. Re-verify.

### Mode N — New file drop

For one or more newly added files.

Flow:

1. Classify each file per the matrix: license bucket + inline/sidecar/REUSE.toml group.
2. Note any LicenseRef or carve-out membership.
3. Apply the headers or sidecars (or extend the `REUSE.toml` prose-group path list).
4. `reuse lint` the affected paths.

No plan document. No commit ladder. One small commit.

## 1. Preconditions and Detection

Confirm tooling and detect content classes before editing:

1. `reuse --version` (or `uvx reuse-tool --version`). If absent, offer the install command (`uv tool install reuse` or `pipx install reuse`) but continue read-only.
2. Detect content classes:
   - Lean: `**/*.lean`, `lakefile.toml`, or `lakefile.lean`
   - Python: `**/*.py`, `pyproject.toml`, or `bin/*.py`
   - Pandoc paper pipeline: `papers/**/main.md` plus `papers/shared/templates/*.latex`
   - Fork lineage: upstream copyright lines in tracked files, or a non-empty `git log --diff-filter=A --follow` on legacy paths
   - Bundled third-party material: `references/papers/`, `references/extractions/`, `references/transcriptions/`, or equivalents
   - Shared external corpora: `corpora/` as a symlink outside the worktree
3. Read current `LICENSES/`, `NOTICE`, `REUSE.toml`, and representative inline headers.

Do **not** auto-detect the repo's sidecar-vs-inline convention. The file-type matrix governs placement; any repo-specific deviation is drift.

## 2. Policy Freeze

Before editing, propose and confirm:

1. **License split.** Defaults (see `references/license-split.yaml`):
   - Lean code: `Apache-2.0`
   - Non-Lean substantive code (Python scripts, shell tools, vendored LaTeX macros): `MIT`
   - Hand-authored infrastructure config (Makefile, TOML, YAML, JSONC, dotfiles, word lists): same code-bucket license (`MIT` when present), covered via the REUSE.toml config group — not inline.
   - Prose, mathematical exposition, planning notes: `CC-BY-4.0`
   - Generated artifacts (lock files, Pandoc output, tool-regenerated JSON/ICS): `CC0-1.0`, covered via the REUSE.toml generated group.
   - Contributor Covenant derivative `CODE_OF_CONDUCT.md`: `CC-BY-SA-4.0`
   - Third-party bundled materials: explicit carve-out or `LicenseRef-*`
2. **Repo content-driven adjustments.** Only add a bucket the repo actually needs. Omit MIT when there is no non-Lean substantive code (in a Lean-only repo the config and placeholder groups fall back to `Apache-2.0`). Omit CC-BY-SA-4.0 when there is no Contributor Covenant derivative. Omit CC0-1.0 when there are no tracked generated artifacts.
3. **Fork lineage.** Ask the user whether the repo is a fork, who the upstream is, and whether retained upstream files should use a `REUSE.toml` bulk annotation or per-file sidecars. Do not attempt to auto-detect fork lineage beyond surfacing upstream copyright lines for confirmation.
4. **Reference-material scope.** Identify which paths fall under `LicenseRef-Reference-Material` and which stay under project licenses. See `references/reference-material-text.md` for the canonical boundary.

Record confirmed overrides in the emitted plan document when one is warranted.

## 3. License-Text Surface Normalization

This precedes any annotation pass.

1. For every license in the confirmed split, confirm `LICENSES/<SPDX-ID>.txt` exists with the exact SPDX identifier casing.
2. Rename wrong-cased files (`APACHE-2.0.txt` -> `Apache-2.0.txt`). Use `git mv`.
3. Download or copy canonical license text for any missing entry (SPDX canonical texts live at <https://spdx.org/licenses/>). Prefer `reuse download <SPDX-ID>` which places canonical text under `LICENSES/`.
4. Author `LicenseRef-*.txt` files for carve-outs. For third-party bundled reference material, use the canonical text in `references/reference-material-text.md` (adjust path names to match the repo's actual layout, keep the rest unchanged).
5. Run `reuse lint` and confirm the "bad license filename" class of errors is gone.

## 4. Root `NOTICE`

Author a short `NOTICE` that:

1. Names the project.
2. Records the project copyright.
3. States that the repository contains material under multiple licenses.
4. Lists each license used, pointing at its `LICENSES/*.txt` file.
5. Calls out fork lineage if present.
6. Calls out third-party carve-outs via `LicenseRef-Reference-Material` (or the per-work `LicenseRef-*` if one is justified).
7. States that per-file SPDX metadata together with the `REUSE.toml` prose-group annotation is authoritative and that `NOTICE` is a summary.

Do **not** ship `NOTICE.license`. `NOTICE` is covered by the `REUSE.toml` prose-group annotation.

Mirror the split exactly in `README.md`'s `## License` section. `README.md` is itself covered by the prose group and carries no inline SPDX header.

Template: `references/NOTICE.template.md`.

## 5. Root `REUSE.toml`

Every repo ships one. `REUSE.toml` is the default coverage surface; inline SPDX and per-file sidecars are exceptions, not defaults. The required annotation groups are:

1. **Project prose (`CC-BY-4.0`, `precedence = "aggregate"`).** Covers `NOTICE` and every project-authored `.md` path from the matrix. This group replaces per-file `.md` inline headers and `.license` sidecars for prose.
2. **Project config (code-bucket license, `precedence = "aggregate"`).** Covers hand-authored infrastructure config: `Makefile`, `lakefile.toml`, `pyproject.toml`, `**/*.yaml`, `**/*.yml`, `**/*.jsonc`, `.editorconfig`, `.gitignore`, `.gitattributes`, `.ignore`, `cspell-words.txt`, and similar. License is the repo's code bucket — `MIT` if present, otherwise `Apache-2.0`. Replaces per-file sidecars and inline headers on config files.
3. **Generated artifacts (`CC0-1.0`, `precedence = "override"`).** Covers auto-regenerated files whose content is mechanical: lock files, `lean-toolchain`, Pandoc-generated `.tex`, generated JSON/JSONL, `.ics` output, script-generated figure data. `CC0-1.0` is the honest framing (public-domain dedication on content the project does not originate) and adds `LICENSES/CC0-1.0.txt`.
4. **Structural placeholders (code-bucket license, `precedence = "override"`).** Covers `**/.gitkeep`. One glob, no per-file sidecars.
5. **Contributor Covenant derivative (`CC-BY-SA-4.0`, `precedence = "override"`).** Include only when `CODE_OF_CONDUCT.md` exists and is Contributor-Covenant-derived.
6. **Third-party reference material (`LicenseRef-Reference-Material`, `precedence = "override"`).** Include when the collection exceeds the small-collection threshold (~20 files). `SPDX-FileCopyrightText = "Original authors and publishers"`.

Optional additional groups:

- **Upstream fork trees** retained unchanged (upstream copyright, original license).
- **Mixed-copyright paths** (for example, a fork's `README.md` under `MIT AND CC-BY-4.0`) — give them their own annotation block with multi-entry `SPDX-FileCopyrightText`.

The `REUSE.toml` file itself is covered by group 2 (config), not inline. Do not add an inline SPDX block at its top.

Canonical skeleton (MIT-code-bucket, repo has `CODE_OF_CONDUCT.md` and bundled reference material; trim blocks to what the repo actually needs):

<!-- REUSE-IgnoreStart -->

```toml
version = 1

# Prose: NOTICE, README, CHANGELOG, agent configs, docs, project-authored
# Markdown subtrees, bibliographic metadata.
[[annotations]]
path = [
  "NOTICE",
  "README.md",
  "CHANGELOG.md",
  "CONTRIBUTING.md",
  "AGENTS.md",
  "CLAUDE.md",
  ".github/**/*.md",
  "docs/**/*.md",
  # repo-specific prose subtrees go here
  "references/summaries/**/*.md",
  "references/reviews/**/*.md",
  "references/datasets/**/*.md",
  "references/bibliographies/**/*.md",
  "references/README.md",
  "references/papers.bib",
  "skills/**/*.md",
  "skills/**/*.yaml",
]
precedence = "aggregate"
SPDX-FileCopyrightText = "<year> <author>"
SPDX-License-Identifier = "CC-BY-4.0"

# Config: Makefiles, TOML, YAML, JSONC, dotfiles, and word lists. One
# glob covers all hand-authored infrastructure config.
[[annotations]]
path = [
  "Makefile",
  "**/*.mk",
  "**/*.toml",
  "**/*.yaml",
  "**/*.yml",
  "**/*.jsonc",
  ".editorconfig",
  ".gitignore",
  ".gitattributes",
  ".ignore",
  "cspell-words.txt",
  "REUSE.toml",
]
precedence = "aggregate"
SPDX-FileCopyrightText = "<year> <author>"
SPDX-License-Identifier = "MIT"

# Generated artifacts: lock files, pinned versions, tool output. CC0 is
# the honest framing for content the project does not originate.
[[annotations]]
path = [
  "**/lake-manifest.json",
  "uv.lock",
  "poetry.lock",
  "package-lock.json",
  "yarn.lock",
  "**/lean-toolchain",
  "papers/*/main.tex",
  "papers/submission-schedule.ics",
  "references/cross-reference-*.json",
  "references/cross-reference-frequency.md",
  # repo-specific generated trees go here
]
precedence = "override"
SPDX-FileCopyrightText = "NONE"
SPDX-License-Identifier = "CC0-1.0"

# Structural placeholders.
[[annotations]]
path = ["**/.gitkeep"]
precedence = "override"
SPDX-FileCopyrightText = "<year> <author>"
SPDX-License-Identifier = "MIT"

# Include only if CODE_OF_CONDUCT.md exists and is Contributor-Covenant-derived.
[[annotations]]
path = ["CODE_OF_CONDUCT.md"]
precedence = "override"
SPDX-FileCopyrightText = "<year> <author>"
SPDX-License-Identifier = "CC-BY-SA-4.0"

# Include only when the reference collection exceeds the small-collection threshold.
[[annotations]]
path = [
  "references/papers/**",
  "references/extractions/**",
  "references/transcriptions/**",
]
precedence = "override"
SPDX-FileCopyrightText = "Original authors and publishers"
SPDX-License-Identifier = "LicenseRef-Reference-Material"
```

<!-- REUSE-IgnoreEnd -->

Notes on the skeleton:

- Generated-group `SPDX-FileCopyrightText = "NONE"` is the REUSE-blessed way to say "no copyright is asserted." Use it for lock files and tool output. Do not invent a fictional copyright line.
- The config group uses `aggregate`, not `override`, so a genuine per-file SPDX (rare but allowed) still wins.
- Keep path lists alphabetized within each block when practical; they grow and unordered lists drift.

## 6. SPDX Placement by File Type

`REUSE.toml` is the default; inline and sidecar are exceptions. Use `references/file-type-matrix.md` as the single source of truth. Summary:

1. **REUSE.toml coverage** (most files): prose group, config group, generated group, structural group, reference-material group, CoC block. Covered in Section 5. No inline SPDX, no sidecar.
2. **Inline always**: substantive hand-authored source code where the SPDX tag is part of the file's public interface and should travel with the file — `.lean`, `.py` (hand-authored), hand-authored `.tex`, `.lua`, `.js`, `.ts`, `.css`, `.less`, hand-authored `.html`, shebang scripts with substantive logic, `.sh`/`.zsh` beyond trivial wrappers, compiled-language sources (`.go`, `.rs`, `.c`, `.cpp`, `.h`, `.hpp`, `.swift`, `.kt`, `.java`). A consumer lifting one of these files elsewhere should read the SPDX header on it.
3. **Sidecar (narrow residual)**: per-file sidecars only where per-file metadata is substantive and the format blocks inline comments. Examples: individual bundled reference PDFs under the small-collection threshold (author/publisher-specific copyright lines); binary assets the project authors with distinct attribution. Everything else that was historically sidecared (lock files, `lean-toolchain`, `cspell-words.txt`, `.gitignore`, `Makefile`, etc.) now lives in a `REUSE.toml` block.

Governing principle: **inline headers are load-bearing; REUSE.toml is ceremony.** If the SPDX tag on a file does not tell a downstream reader something they can't get from `REUSE.toml`, it should not be inline.

Inline syntax by format (for files that genuinely go inline):

- Lean: `/- ... -/` block at the very top, before imports
- Shebang scripts: keep shebang on line 1; SPDX `#` comments immediately after
- LaTeX (hand-authored): `%` comments at the top. `.bib` stays in the prose group, not inline, because it travels with the bibliography. Generated `.tex` stays in the generated group.
- Lua: `--` comments at the top
- JavaScript, TypeScript, CSS, LESS, HTML: native comment syntax at the top
- Compiled languages: the language's single-line or block comment convention at the top

Every inline block includes both `SPDX-FileCopyrightText` and `SPDX-License-Identifier`. Prefer `reuse annotate` for batch insertion on recognized types and `reuse annotate --force-dot-license` for the narrow sidecar cases.

**Anti-pattern to migrate**: inline SPDX on infrastructure config (`lakefile.toml`, `pyproject.toml`, `Makefile`, `cspell.jsonc`, `.gitignore`, `.editorconfig`, etc.). Strip the inline block; the REUSE.toml config group covers it. Inline SPDX on generated `.tex` or `.ics` outputs is the same anti-pattern — the generator regenerates the file and the header disappears anyway.

## 7. Verification

1. `reuse lint` must report zero errors. Zero, not "only low severity".
2. Run the project's own lint (`make lint`, `npm run lint`, `ruff check`, etc.) if one is present.
3. Run the project's build or proof check if edits touched source-bearing files (for example, `make check-proofs` for this repo's Lean tree).
4. Re-read `README.md`, `NOTICE`, and representative per-file headers together to confirm the summary still matches the coverage.

Details: `references/verification.md`.

## 8. Carve-Outs

Third-party reference materials are **not** carve-outs. They are SPDX-covered via `LicenseRef-Reference-Material` (see `references/reference-material-text.md`).

True carve-outs — files the skill never tags, and that `NOTICE` names explicitly:

1. `LICENSES/` license texts themselves (tool convention).
2. Vendored dependency state: `proofs/.lake/packages/**`, `.git/`, `.venv/`, `.ruff_cache/`, `node_modules/`, `vendor/`, and similar.
3. External shared corpora accessed through symlinks (for example, `corpora/` pointing outside the worktree).
4. Build artifacts and caches that are already gitignored.

## 9. Plan Document Emission (conditional)

Emit a tracked plan document at `docs/plans/todo/YYYY-MM-DD-license-notice-spdx-rollout.md` only when:

1. Bootstrap mode is running against a repo with no existing SPDX coverage, **and**
2. Scope spans more than a handful of subtrees or requires non-trivial policy calls (fork lineage, third-party reference carve-outs, a new license bucket).

Structure it like the existing `2026-04-19-license-*` plans: context, goals, coverage rules, phased execution, verification, done criteria. Commit the plan as its own step before edits begin.

For Maintain mode, New-file drop, or a small Bootstrap against a tiny repo, skip the plan document.

## Common Drift Patterns

When run in Maintain mode, the skill typically surfaces drift in one or more of these categories. The list is an empirical synthesis of patterns observed across the four prior rollouts; treat it as a checklist of *what to look for*, not as an exhaustive enumeration.

- **License-file casing and naming.** `LICENSES/APACHE-2.0.txt` should be `Apache-2.0.txt`; `MIT.txt` should be `MIT.txt` (already correct); etc. SPDX expects the canonical SPDX-License-Identifier capitalization. Use `git mv` so history follows.
- **Missing root `REUSE.toml`.** Repos that started with per-file SPDX headers everywhere often lack a `REUSE.toml`. Adding it lets prose / config / generated / structural groups cover whole subtrees by glob, eliminating most sidecar files.
- **Sidecar proliferation.** `*.md.license`, `*.json.license`, `*.toml.license`, `.gitkeep.license`, `lock-file.license` sidecars accumulate when SPDX is added file-by-file. Fold them into the relevant `REUSE.toml` group (prose, config, generated, structural).
- **Inline SPDX in prose.** `<!-- SPDX-FileCopyrightText: ... -->` blocks at the top of Markdown files are noise once the prose group covers them. Strip them in the same commit that introduces the group.
- **Generated artifacts not separated.** Lock files (`lake-manifest.json`, `package-lock.json`, `Cargo.lock`, `uv.lock`), toolchain pins (`lean-toolchain`, `rust-toolchain.toml`), and Pandoc-generated `.tex` should land in a CC0-licensed generated group, not in the same bucket as hand-authored config.
- **Reference material left under default license.** Bundled third-party material under `references/`, `papers/shared/`, or similar should carry `LicenseRef-Reference-Material` (or a more specific `LicenseRef-*`), not the project's default license.
- **Forks without fork-aware policy.** Repos forked from a permissively-licensed upstream need (a) per-file sidecars on byte-identical upstream files, (b) dual-copyright on fork-derived lockfiles, (c) compound license notation on the README if it predates the fork. These are **not drift**; they are intentional and must not be flattened.

For the specific drift state of any given repo at a given time, write the audit findings into a `docs/plans/todo/YYYY-MM-DD-license-*` plan document (per the rollout commit ladder in `references/commit-sequence.md`).

## Reference Files

- `references/file-type-matrix.md` — the placement decision table by file type
- `references/license-split.yaml` — default three- or four-way split
- `references/NOTICE.template.md` — fill-in-the-blanks NOTICE body
- `references/reference-material-text.md` — canonical `LicenseRef-Reference-Material.txt` text and scope
- `references/commit-sequence.md` — the rollout commit ladder
- `references/verification.md` — `reuse lint` + repo-lint + build invariants
- `references/example-flows.md` — end-to-end Bootstrap and single-file Maintain transcripts
