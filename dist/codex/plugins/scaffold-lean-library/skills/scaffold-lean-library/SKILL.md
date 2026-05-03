---
name: scaffold-lean-library
description: >-
  Scaffold a Lean 4 library project with Mathlib or PFR dependencies, Lake
  test/lint wiring, GitHub Actions CI, text linting, and agent instructions.
---

# Scaffold Lean Library

Generate a Lean 4 library repository with Lake, Mathlib or PFR dependencies, compile-time API regression tests, local Makefile targets, GitHub Actions CI, text linting, and agent instructions.

## Workflow

### 1. Gather Project Information

If the user provided values in the request, use them and do not ask again. Derive safe defaults from context only when they are unambiguous.

Ask for any missing values:

- **Project name**: kebab-case repository and Lake package name, for example `entropy-inequalities`.
- **Short description**: one sentence for README, marketplace-style summaries, and agent instructions.
- **Top-level Lean namespace**: `UpperCamelCase`, for example `EntropyInequalities`. Derive from the project name when the result is readable; ask if acronyms or domain terms make the derivation ambiguous.
- **Lean toolchain version**: the exact `lean-toolchain` content, for example `leanprover/lean4:v4.25.0`.
- **Dependency family**: `Mathlib` or `PFR`.
- **Dependency git ref**: a Mathlib tag/ref or a PFR git ref.
- **Paper-backed mode**: whether to add `references/` stubs and Pandoc-academic lint ignores for formalizations tied to papers or transcriptions.
- **GitHub username**: for repository URLs.
- **Copyright holder**: for `LICENSE` and source headers.

Detect the GitHub username and full name when possible:

```bash
gh api user -q .login
```

```bash
git config user.name
```

If either command fails or returns an empty value, ask the user.

### 2. Resolve Dependency Ref

For **Mathlib** projects:

1. If the user supplied a dependency ref, use it.
1. Otherwise, if the Lean toolchain is exactly `leanprover/lean4:vX.Y.Z` or `vX.Y.Z`, derive the Mathlib ref `vX.Y.Z`.
1. Verify the derived ref exists before using it:

   ```bash
   git ls-remote --tags https://github.com/leanprover-community/mathlib4.git refs/tags/vX.Y.Z
   ```

1. If the tag does not exist, or if the Lean toolchain is nightly, a branch, or otherwise not a clean stable version, ask the user for the Mathlib ref.

For **PFR** projects:

1. Ask for the `teorth/pfr` ref explicitly. Do not derive it from the Lean toolchain.
1. Use the PFR dependency block from `./references/dependency-blocks.md`.
1. Import `PFR.ForMathlib.Entropy.Basic` in the main prelude.

Always allow the user to override a derived dependency ref.

### 3. Refresh Workflow Pins

Before emitting workflow templates, refresh every pinned action or reusable workflow SHA and its version comment.

For `leanprover/lean-action`:

```bash
TAG="$(gh release view --repo leanprover/lean-action --json tagName --jq '.tagName')"
SHA="$(gh api "repos/leanprover/lean-action/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

For `cboone/gh-actions`:

```bash
TAG="$(gh release view --repo cboone/gh-actions --json tagName --jq '.tagName')"
SHA="$(gh api "repos/cboone/gh-actions/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

For `actions/checkout`, refresh the latest release in the same way when the Lean workflow template includes a checkout step:

```bash
TAG="$(gh release view --repo actions/checkout --json tagName --jq '.tagName')"
SHA="$(gh api "repos/actions/checkout/commits/${TAG}" --jq '.sha')"
echo "${SHA} # ${TAG}"
```

Replace the `LEAN-ACTION-SHA`, `LEAN-ACTION-TAG`, `CBOONE-GH-ACTIONS-SHA`, `CBOONE-GH-ACTIONS-TAG`, `CHECKOUT-SHA`, and `CHECKOUT-TAG` placeholders in emitted workflows. If `gh` is unavailable or unauthenticated, use `git ls-remote --tags` as a fallback and clearly report any pins that could not be refreshed.

### 4. Verify the Target Directory

The project should be scaffolded in a directory named after the project. If the current directory is already named after the project and is empty or contains only initial repository metadata, use it. Otherwise, create a subdirectory named after the project.

If the target directory already contains Lean project files (`lakefile.toml`, `lakefile.lean`, `lean-toolchain`, or `*.lean` files), warn the user before writing files.

### 5. Initialize Git

Skip if already inside a git repository.

```bash
git init
```

### 6. Generate Project Files

Read the reference templates listed below and create the files in the target repository. Replace placeholders consistently:

- `PROJECT-NAME`: kebab-case project name.
- `PROJECT-TITLE`: title-cased project name for prose.
- `PROJECT-DESCRIPTION`: short description.
- `LEAN-NAMESPACE`: top-level Lean namespace and main library name.
- `LEAN-TEST-NAMESPACE`: `LEAN-NAMESPACETest`.
- `LEAN-TOOLCHAIN`: exact `lean-toolchain` content.
- `DEPENDENCY-FAMILY`: `Mathlib` or `PFR`.
- `DEPENDENCY-REQUIRE-BLOCK`: dependency block from `./references/dependency-blocks.md`.
- `DEPENDENCY-IMPORT`: `Mathlib` for Mathlib projects, `PFR.ForMathlib.Entropy.Basic` for PFR projects.
- `DEPENDENCY-REF`: explicit Mathlib or PFR ref.
- `GITHUB-USERNAME`: detected or supplied GitHub username.
- `COPYRIGHT-HOLDER`: detected or supplied copyright holder.
- `YEAR`: current year from `date +%Y`.
- Workflow pin placeholders from step 3.

Create these files:

- `lean-toolchain` from `./references/lean-toolchain.md`.
- `lakefile.toml` from `./references/lakefile-toml.md`.
- `LEAN-NAMESPACE.lean` from `./references/root-lean.md`.
- `LEAN-NAMESPACE/Prelude.lean` from `./references/prelude-lean.md`.
- `LEAN-TEST-NAMESPACE.lean` from `./references/test-root-lean.md`.
- `LEAN-TEST-NAMESPACE/Prelude.lean` from `./references/test-prelude-lean.md`.
- `bin/bootstrap-worktree` from `./references/bootstrap-worktree.md`.
- `Makefile` from `./references/makefile.md`.
- `.github/workflows/ci.yml` from `./references/ci-workflow.md`.
- `.github/workflows/text-lint.yml` from `./references/text-lint-workflow.md`.
- `.markdownlint-cli2.jsonc` from `./references/markdownlint-cli2-jsonc.md`.
- `cspell.jsonc` from `./references/cspell-jsonc.md`.
- `cspell-words.txt` from `./references/cspell-words.md`.
- `.editorconfig` from `./references/editorconfig.md`.
- `.gitignore` from `./references/gitignore.md`.
- `.github/copilot-instructions.md` from `./references/copilot-instructions.md`.
- `AGENTS.md` from `./references/agents-md.md`.
- `README.md` from `./references/readme.md`.
- `LICENSE` from `./references/license.md`.
- `CHANGELOG.md` from `./references/changelog.md`.

If paper-backed mode is enabled, also create the files and directories in `./references/paper-backed-stubs.md`.

### 7. Set Executable Bits and Safe Symlink

Mark the bootstrap script executable:

```bash
chmod +x bin/bootstrap-worktree
```

Create `CLAUDE.md` as a symlink only when safe:

```bash
if [[ ! -e CLAUDE.md ]]; then
  ln -s AGENTS.md CLAUDE.md
elif [[ -L CLAUDE.md ]] && [[ "$(readlink CLAUDE.md)" == "AGENTS.md" ]]; then
  :
else
  echo "CLAUDE.md already exists and was left unchanged." >&2
fi
```

Do not use `ln -f`, `ln -sfn`, or any override flag. If `CLAUDE.md` exists and is not already the intended symlink, leave it untouched and report that decision.

### 8. Verify Generated Files

Run syntax and dry-run checks before attempting a full Lean build:

```bash
zsh -n bin/bootstrap-worktree
```

```bash
make -n build test lean-lint check
```

Then bootstrap the worktree and run the local check:

```bash
bin/bootstrap-worktree
```

```bash
make check
```

If the Lean dependency cache is unavailable, report the failing command and the generated files still produced. Do not replace `bin/bootstrap-worktree` with a bare `lake build`; the bootstrap script is the supported path for Mathlib-downstream projects.

### 9. Create Initial Commit

Stage the generated project files and create a signed commit:

```bash
git add -A
git commit -S -m "feat: scaffold Lean library project"
```

### 10. Summary

Print a summary listing the generated files, dependency family and ref, whether paper-backed stubs were created, workflow pins used, and the verification commands that passed or failed.

## Error Handling

- If `lake update` fails, check the dependency ref and repository URL first.
- If `lake exe cache get` fails, report the cache failure and do not proceed to a bare `lake build`.
- If `_check-mathlib-cache` fails, run `make bootstrap` or `bin/bootstrap-worktree` before retrying `make build`, `make test`, or `make lean-lint`.
- If `CLAUDE.md` exists and is not the intended symlink, leave it unchanged and tell the user.
- If workflow pin refresh fails, ask before emitting unrefreshed pins.

## Reference Templates

- `./references/dependency-blocks.md`: Mathlib and PFR Lake dependency blocks.
- `./references/lean-toolchain.md`: `lean-toolchain` template.
- `./references/lakefile-toml.md`: Lake package configuration.
- `./references/root-lean.md`: main entrypoint manifest.
- `./references/prelude-lean.md`: main prelude module.
- `./references/test-root-lean.md`: test entrypoint manifest.
- `./references/test-prelude-lean.md`: test prelude module.
- `./references/bootstrap-worktree.md`: zsh bootstrap script.
- `./references/makefile.md`: Makefile target set.
- `./references/ci-workflow.md`: Lean build, lint, and test workflow.
- `./references/text-lint-workflow.md`: Markdown, spelling, and formatting workflow.
- `./references/markdownlint-cli2-jsonc.md`: markdownlint config.
- `./references/cspell-jsonc.md`: cspell config.
- `./references/cspell-words.md`: initial cspell vocabulary.
- `./references/editorconfig.md`: EditorConfig template.
- `./references/gitignore.md`: `.gitignore` template.
- `./references/copilot-instructions.md`: Copilot review instructions.
- `./references/agents-md.md`: agent instruction template.
- `./references/readme.md`: README template.
- `./references/license.md`: Apache-2.0 license template.
- `./references/changelog.md`: changelog template.
- `./references/paper-backed-stubs.md`: optional paper-backed reference files.
