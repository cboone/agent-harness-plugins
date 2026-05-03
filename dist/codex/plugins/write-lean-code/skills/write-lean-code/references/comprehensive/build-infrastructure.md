
# Build Infrastructure

Repeating patterns for Mathlib-downstream Lean 4 projects: the bootstrap script, Makefile target set, `lakefile.toml` options, entrypoint manifest, and test-library wiring. The guidance here is generic; project-local specifics (actual library names, additional dependencies, vendored packages to exclude) live in the invoking project's CLAUDE.md or AGENTS.md.

## Table of Contents

- [Why a bootstrap script](#why-a-bootstrap-script)
- [Bootstrap script pattern](#bootstrap-script-pattern)
- [Makefile standard target set](#makefile-standard-target-set)
- [`lintDriver` and `batteries/runLinter`](#lintdriver-and-batteriesrunlinter)
- [Entrypoint manifest](#entrypoint-manifest)
- [`testDriver` vs `defaultTargets`](#testdriver-vs-defaulttargets)
- [Test library naming, layout, and discipline](#test-library-naming-layout-and-discipline)

## Why a Bootstrap Script

Running `lake build` in a fresh clone or worktree downloads the Mathlib source but does not download its prebuilt artifacts. Lake will then happily spend an hour or more compiling Mathlib from source on your machine, which is almost never what anyone wants. The supported path is to run `lake exe cache get` (which pulls Mathlib's prebuilt `.olean` files from the Mathlib cache server) before any `lake build`.

A `bin/bootstrap-worktree` script bakes that invariant into the workflow: it runs `lake update`, runs `lake exe cache get`, verifies the prebuilt Mathlib artifacts landed on disk, and only then runs `lake build` on the project's own libraries. Every fresh clone, every new git worktree, every CI cold start calls the same script, so nobody ever re-learns the "why is Mathlib compiling from source" lesson by accident.

## Bootstrap Script Pattern

Canonical `bin/bootstrap-worktree` shape, written in zsh to take advantage of glob qualifiers and local-option blocks. Replace `<PrimaryLib>` with the project's main library name (e.g. `Shannon`, `ZhangYeung`, `StrengthModel`). Projects with multiple top-level libraries (a library plus a companion book, site, or auxiliary library) list them all in the final `lake build`.

```zsh
#!/usr/bin/env zsh

setopt ERR_EXIT NO_UNSET PIPE_FAIL

readonly script_dir="${0:A:h}"
readonly repo_root="${script_dir:h}"
readonly mathlib_build_dir="${repo_root}/.lake/packages/mathlib/.lake/build/lib/lean"

function ensure_mathlib_cache_present() {
  setopt local_options NULL_GLOB

  local build_dir="${1}"
  local -a mathlib_oleans
  mathlib_oleans=(
    "${build_dir}"/Mathlib.olean(N)
    "${build_dir}"/Mathlib/**/*.olean(N)
  )

  if (( ${#mathlib_oleans} == 0 )); then
    print -u2 "Mathlib prebuilt artifacts are missing under ${build_dir}"
    print -u2 "Refusing to run 'lake build' because that would compile Mathlib from source."
    print -u2 "Rerun 'bin/bootstrap-worktree' and make sure 'lake exe cache get' succeeds."
    exit 1
  fi
}

function main() {
  print "Bootstrapping worktree in ${repo_root}"

  cd "${repo_root}"
  print "[1/4] Running lake update"
  lake update
  print "[2/4] Downloading prebuilt dependency artifacts with lake exe cache get"
  lake exe cache get
  print "[3/4] Verifying Mathlib prebuilt artifacts"
  ensure_mathlib_cache_present "${mathlib_build_dir}"
  print "[4/4] Building <PrimaryLib>"
  lake build <PrimaryLib>
}

main "${@}"
```

Key design points:

- `setopt ERR_EXIT NO_UNSET PIPE_FAIL` (or `set -euo pipefail` equivalently) turns silent failures into loud ones.
- `${0:A:h}` resolves the script's directory even through symlinks; `${script_dir:h}` walks up to the repo root.
- The `ensure_mathlib_cache_present` check uses zsh's `(N)` glob qualifier, which returns an empty array for no-match instead of erroring. The guard bails with a clear message rather than proceeding into a multi-hour source compilation.
- When the Lean project is nested (e.g. `proofs/` inside a larger repo), the script `cd`s into that subdirectory and the `mathlib_build_dir` path is adjusted accordingly.
- The final `lake build` targets the specific library (or libraries) rather than running bare `lake build`, which keeps build output focused and prevents accidental compilation of unused dependencies.

The script must stay fast on re-runs. `lake update` and `lake exe cache get` are both idempotent; running the script twice in a row does nothing expensive the second time. That keeps it safe to call from both onboarding docs and automation.

## Makefile Standard Target Set

Every Mathlib-downstream project in this family ships the same Makefile target set, keyed off a `_check-mathlib-cache` private target that guards build and test commands against the "Mathlib artifacts missing" failure mode.

```makefile
MATHLIB_BUILD_DIR := .lake/packages/mathlib/.lake/build/lib/lean

build: _check-mathlib-cache ## Build the <PrimaryLib> library
	lake build <PrimaryLib>

bootstrap: ## Bootstrap worktree (lake update, cache get, build)
	bin/bootstrap-worktree

_check-mathlib-cache:
	@if [ ! -d "$(MATHLIB_BUILD_DIR)" ] || { [ ! -f "$(MATHLIB_BUILD_DIR)/Mathlib.olean" ] && [ -z "$$(find $(MATHLIB_BUILD_DIR)/Mathlib -name '*.olean' -print -quit 2>/dev/null)" ]; }; then \
		echo "Error: Mathlib prebuilt artifacts not found." >&2; \
		echo "Run 'make bootstrap' or 'bin/bootstrap-worktree' first." >&2; \
		exit 1; \
	fi

test: _check-mathlib-cache ## Run Lean tests
	lake test

lean-lint: _check-mathlib-cache ## Run Lean linter (batteries)
	lake lint

lint: lint-markdown lint-spelling ## Run all text linters

lint-markdown: ## Lint Markdown files
	markdownlint-cli2 "**/*.md"

lint-spelling: ## Check spelling with cspell
	cspell --no-progress .

check: lint lean-lint build test ## Lint, build, and test

clean: ## Remove Lake build artifacts
	lake clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | \
		awk -F ':.*## ' '{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: build bootstrap clean lint lint-markdown lint-spelling lean-lint test check help _check-mathlib-cache
```

Conventions baked in:

- `##` comments on each target are the canonical docstring source. The `help` target auto-extracts them with `grep | awk` so `make help` stays in sync with the actual targets.
- `_check-mathlib-cache` is a prerequisite of every target that invokes `lake build`, `lake test`, or `lake lint`. The leading underscore marks it as private by convention (there is no enforcement at the Make level).
- `check` is the authoritative local pre-commit command. Any additional project-specific checks (proof-boundary enforcement, figure regeneration) become prerequisites of `check` rather than replacing it.
- `bootstrap` is the only target that does not depend on `_check-mathlib-cache`; it is the target that creates the cache.
- When the project has only a text (Markdown, BibTeX) lint stack and no Lean code yet, `lint` stays as a meta-target depending on `lint-markdown` + `lint-spelling` and `lean-lint` is added when the Lean project gains enough surface to benefit from it.

Projects with additional artifacts (a companion book rendered via Verso, figure-generation scripts, an ICS calendar) add more targets in the same `target: deps ## docstring` style and list them in `.PHONY`. The rule of thumb: if a developer would type it as a shell command, give it a Make target so the help system discovers it and so the target can be a dependency of `check` when appropriate.

## `lintDriver` and `batteries/runLinter`

Every Mathlib-downstream project in this family sets `lintDriver = "batteries/runLinter"` in its `lakefile.toml`:

```toml
lintDriver = "batteries/runLinter"
```

That wires `lake lint` to the Batteries-supplied linter driver. Mathlib itself already depends on Batteries (so the dependency is free), and the driver handles the set of linters the Mathlib community runs in CI (`unusedArguments`, `unusedHypotheses`, `docBlame`, etc.). Without the `lintDriver` setting, `lake lint` is a no-op; with it, `lake lint` is a real pre-commit gate that catches the same issues Mathlib reviewers would flag.

If the project uses a `lakefile.lean` instead of a `lakefile.toml`, the same line goes in the `package` block:

```lean
package "MyProject" where
  lintDriver := "batteries/runLinter"
```

Either form drives `lake lint` identically.

## Entrypoint Manifest

A Lean library named `<Name>` has a root file `<Name>.lean` at the project root. Mathlib's convention is that this root file is an explicit manifest re-exporting every public submodule, mirroring `Mathlib.lean`:

```lean
/- Brief library description. -/
import <Name>.Prelude
import <Name>.Foo
import <Name>.Bar
import <Name>.Baz
```

The repetition is intentional: listing every submodule explicitly makes the public surface discoverable in one place, makes `import <Name>` pull in the whole library transitively, and gives the linter a fixed list against which "this module is unreachable from the entrypoint" can be detected.

PR review tooling (including GitHub Copilot's suggestions) sometimes flags imports in an entrypoint manifest as "redundant transitive imports" and suggests removing them. That advice is wrong for the manifest file; state the convention in the project's agent-config instructions (`.github/lean.instructions.md` for Copilot, project CLAUDE.md for Claude Code) so reviewers do not churn on it.

## `testDriver` vs `defaultTargets`

This section covers only the Lake wiring; for the test-module style itself (import discipline, 1:1 naming mirror, composition per milestone, anti-patterns), use the companion `write-lean-tests` skill.

Lake exposes two ways to wire up a test library of the compile-time `example`-based form (where each test is an `example` that restates a public definition or lemma and thus type-checks iff the public surface still matches):

1. **`testDriver = "<Name>Test"` with `defaultTargets = ["<Name>"]`.** Mathlib convention. `lake test` runs the test library; `lake build` builds only the main library. The build-vs-test signal stays distinct.
2. **`defaultTargets = ["<Name>", "<Name>Test"]` with no `testDriver`.** Simpler config. `lake build` compiles both libraries together; there is no separate `lake test` invocation because the test library is just another default target.

Both work for compile-time example-based tests. Option 1 is the recommendation, for three reasons:

- It matches the Mathlib convention, so newcomers recognize the wiring immediately and tooling that keys off `testDriver` (`make test` conventions, CI matrices) just works.
- The `lake test` output is separable from `lake build` output, which keeps logs and CI stages readable.
- It future-proofs the project if runtime (`IO`-side, `#eval`-side) tests ever get added later; option 2 would need a rewrite to accommodate them.

Option 2 is defensible for trivial projects or during initial scaffolding, when `testDriver` machinery feels like premature ceremony. Flipping from option 2 to option 1 later is a one-commit change: move `<Name>Test` out of `defaultTargets`, add `testDriver = "<Name>Test"`, update the Makefile's `test` target to call `lake test`, and the test files themselves do not change.

Canonical `lakefile.toml` shape under option 1:

```toml
name = "<name>"
version = "0.1.0"
defaultTargets = ["<Name>"]
lintDriver = "batteries/runLinter"
testDriver = "<Name>Test"

[[lean_lib]]
name = "<Name>"

[[lean_lib]]
name = "<Name>Test"
```

Under a `lakefile.lean`, the equivalent is:

```lean
package "<Name>" where
  testDriver := "<Name>Test"

lean_lib «<Name>Test» where
  globs := #[.submodules `<Name>Test]
```

Use the `globs := #[.submodules ·]` form when the test tree has subdirectories (so that `<Name>Test/X/Y.lean` is picked up without being listed by name).

## Test Library Naming, Layout, and Discipline

### Naming

Test library name mirrors the main library with a `Test` suffix: `Shannon` + `ShannonTest`, `ZhangYeung` + `ZhangYeungTest`, `StrengthModel` + `StrengthModelTest`. Avoid alternate spellings (`Shannon.Tests`, `shannon_test`); the mirrored form is what the convention recognizes.

### Directory layout

Directory structure mirrors the main library one-to-one:

```text
<Name>/
├── <Name>.lean         -- entrypoint manifest for main library
├── <Name>/
│   ├── Foo.lean
│   ├── Foo/
│   │   └── Bar.lean
│   └── Baz.lean
├── <Name>Test.lean     -- entrypoint manifest for test library
└── <Name>Test/
    ├── Foo.lean
    ├── Foo/
    │   └── Bar.lean
    └── Baz.lean
```

Every public module at `<Name>/X/Y.lean` has a matching module at `<Name>Test/X/Y.lean`. The `<Name>Test.lean` entrypoint re-exports every test submodule, same pattern as the main manifest.

### Discipline rule

Every public module added to `<Name>/` lands in the same commit as a matching module under `<Name>Test/` that:

- Imports only the public surface (`import <Name>` or the specific submodule). Never reaches into internal helpers or `.Internal` namespaces.
- Restates each exported definition or lemma as an `example` with the public signature. The file type-checks iff the public surface still matches what downstream code would see.
- Includes at least one composed-downstream-use `example` for any milestone that produces derivable consequences (e.g. "Corollary X follows by combining `foo` and `bar`"), not just the base signatures.

When a public definition is renamed, restated, or removed, the corresponding test module is updated in the same change. This keeps `lake test` a reliable gate against accidental API breakage: the build either catches the drift immediately in the test module, or it catches it at the next downstream consumer (which is much worse, because consumers are often in a different repo).

### Why compile-time tests and not a runtime test runner

The `example`-based style has a specific property that runtime tests (`#eval`, `IO`-side assertion libraries) lack: it runs for free as part of `lake build`. Every change to the main library surface forces a rebuild of the test library, and signature drift shows up as a type error at the exact `example` that references the renamed symbol. No test runner to invoke, no flake, no "forgot to run the tests" failure mode. The only cost is authoring discipline: each new public declaration needs a matching `example`.

For random-variable libraries or probability libraries where `#eval` is impractical anyway (most interesting definitions are `noncomputable`), compile-time tests are often the only option that is not aspirational.
