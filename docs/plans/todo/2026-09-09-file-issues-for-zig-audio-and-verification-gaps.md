# File issues for Zig, audio-plugin, verification and documentation gaps

## Context

Two projects, [fosforo](https://github.com/cboone/fosforo) (a Zig 0.16 CLAP phosphor oscilloscope rendered with Metal) and [springer](https://github.com/cboone/springer) (a Zig 0.16 CLAP diatonic chord generator for Logic's MIDI FX slot), have between them built a large body of infrastructure by hand that no plugin in this catalog produces. Springer is currently re-deriving fosforo's build from scratch: its own Phase 0 plan records that `scripts/`, `build.zig`, `src/canary.zig`, `src/build_info.zig`, `macos/Info.plist` and `packaging/distribution.xml` "start as adaptations rather than new work," and its `.gitleaks.toml`, `typos.toml`, `.editorconfig`, `.markdownlint-cli2.jsonc` and secret-scanning workflows are near-verbatim copies of fosforo's.

That copying is the signal. Everything copied is generalizable, and everything hand-written is a gap.

Issue [#223](https://github.com/cboone/agent-harness-plugins/issues/223) added Zig to the detection tables of `scaffold-new-repo`, `set-up-ci`, `set-up-linters` and `set-up-installers`, but it stopped short of a Zig scaffolder or a Zig style guide, and it left `lint-and-fix`, `refresh-project-scaffolding` and `bootstrap-project` untouched. A search across all issue states for `audio`, `clap`, `vst` or `dsp` returns nothing: the audio-plugin domain is entirely greenfield here.

Mining the Claude Code transcripts for both projects (260 typed human turns across fosforo's 53 worktrees, plus springer's three) surfaced a second class of gap that has nothing to do with either language or domain: recurring session-continuity friction, and a verification discipline that fosforo developed the hard way and that nothing in this catalog teaches.

The outcome of this plan is a set of GitHub issues, twenty in `cboone/agent-harness-plugins` and four in `cboone/gh-actions`, each carrying enough measured detail lifted from the two source repositories that an implementer can build the skill without rediscovering what fosforo already paid for.

### Filed

All twenty-four were filed on 2026-09-09. This section is the record; the group sections below are the reasoning behind each.

| Group | Plan ref | Issue                                                              | Title                                                                                       |
| ----- | -------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| A     | A1       | [#338](https://github.com/cboone/agent-harness-plugins/issues/338) | New skill: write-zig-code                                                                   |
| A     | A2       | [#339](https://github.com/cboone/agent-harness-plugins/issues/339) | New skill: scaffold-zig-cli                                                                 |
| B     | B3       | [#340](https://github.com/cboone/agent-harness-plugins/issues/340) | New skill: set-up-macos-signing                                                             |
| B     | B4       | [#341](https://github.com/cboone/agent-harness-plugins/issues/341) | New skill: stamp-build-provenance                                                           |
| B     | B2       | [#342](https://github.com/cboone/agent-harness-plugins/issues/342) | New skill: set-up-clap-validation                                                           |
| B     | B5       | [#343](https://github.com/cboone/agent-harness-plugins/issues/343) | New skill: write-realtime-audio-code                                                        |
| B     | B1       | [#344](https://github.com/cboone/agent-harness-plugins/issues/344) | New skill: scaffold-clap-audio-plugin                                                       |
| C     | C1       | [#345](https://github.com/cboone/agent-harness-plugins/issues/345) | New skill: plant-defects                                                                    |
| C     | C2       | [#346](https://github.com/cboone/agent-harness-plugins/issues/346) | New skill: check-ci-workflows                                                               |
| E     | E2       | [#347](https://github.com/cboone/agent-harness-plugins/issues/347) | New skill: write-phased-build-plan                                                          |
| E     | E1       | [#348](https://github.com/cboone/agent-harness-plugins/issues/348) | New skill: write-adr                                                                        |
| D     | D1       | [#349](https://github.com/cboone/agent-harness-plugins/issues/349) | New skill: review-project-status                                                            |
| D     | D2       | [#350](https://github.com/cboone/agent-harness-plugins/issues/350) | New skill: create-deferred-issues                                                           |
| D     | D3       | [#351](https://github.com/cboone/agent-harness-plugins/issues/351) | New skill: write-manual-verification-plan                                                   |
| F     | F1       | [#352](https://github.com/cboone/agent-harness-plugins/issues/352) | feat: close the Zig gaps left by #223 across the plugin ecosystem                           |
| F     | F2       | [#353](https://github.com/cboone/agent-harness-plugins/issues/353) | set-up-linters: make typos a cross-language option instead of Rust-only                     |
| F     | F3       | [#354](https://github.com/cboone/agent-harness-plugins/issues/354) | write-bash-scripts: add verification-aware script conventions                               |
| F     | F4       | [#355](https://github.com/cboone/agent-harness-plugins/issues/355) | optimize-runner-usage: derive timeout-minutes from measured run history                     |
| F     | F5       | [#356](https://github.com/cboone/agent-harness-plugins/issues/356) | chore: validate skill and path cross-references in bin/validate-plugins                     |
| F     | F6       | [#357](https://github.com/cboone/agent-harness-plugins/issues/357) | create-worktree: record and respect an exclusive-resource claim                             |
| G     | G1       | [gh-actions#85](https://github.com/cboone/gh-actions/issues/85)    | fix: shellcheck is unpinned and actionlint fails open without it                            |
| G     | G2       | [gh-actions#86](https://github.com/cboone/gh-actions/issues/86)    | fix: lint-shell.yml discovery misses extension-less scripts outside bin, scripts and script |
| G     | G3       | [gh-actions#87](https://github.com/cboone/gh-actions/issues/87)    | feat: extract the pinned-tool install into one composite action                             |
| G     | G4       | [gh-actions#88](https://github.com/cboone/gh-actions/issues/88)    | feat: add a shared clap-validator install action                                            |

One correction made during filing. G1 was planned as "`lint-github-actions.yml` never installs shellcheck, so actionlint skips every `run:` block". That overstated it: `ubuntu-latest` ships ShellCheck, which `lint-shell.yml` running a bare `shellcheck` with no install step confirms. The filed issue is the accurate narrower one, that `shellcheck` is the only unpinned tool in two otherwise checksum-pinned workflows and that `actionlint` fails open if it is ever absent.

### Decisions taken

- **Split by generality.** Audio-specific skills are filed alongside Go, Rust, Lean and Zig support, but the genuinely general parts (macOS signing and notarization, build provenance, planted-defect verification) are extracted as standalone skills rather than buried inside a CLAP scaffolder.
- **Mixed granularity, matching precedent.** `New skill: <name>` issues with the `new skill` label for each new plugin (following [#60](https://github.com/cboone/agent-harness-plugins/issues/60)), plus umbrella `feat:` issues with per-plugin sections for cross-plugin edits (following [#223](https://github.com/cboone/agent-harness-plugins/issues/223)). The [#313](https://github.com/cboone/agent-harness-plugins/issues/313)-[#316](https://github.com/cboone/agent-harness-plugins/issues/316) Swift cluster and the newer [#334](https://github.com/cboone/agent-harness-plugins/issues/334)-[#336](https://github.com/cboone/agent-harness-plugins/issues/336) MD060 cluster are both one-issue-per-plugin; that shape is used here only inside the umbrella issues, as sections.
- **Names follow the catalog's convention.** Every existing plugin is a verb-first imperative in kebab-case that joins an existing family (`write-*`, `scaffold-*`, `set-up-*`, `add-*`, `check-*`, `create-*`, `review-*`) where one exists. The only bare nouns are the four that double as their own slash command (`commit`, `pr`, `release`, `notify`). Eight working names were corrected to fit; see [Naming](#naming).
- **ADRs are one skill.** `write-adr` covers both authoring and directory maintenance, the way `write-formalization-roadmap` covers a whole document class.

### Naming

Corrected from the working names used during research:

| Working name                      | Filed as                         | Why                                                                         |
| --------------------------------- | -------------------------------- | --------------------------------------------------------------------------- |
| `scaffold-clap-plugin`            | `scaffold-clap-audio-plugin`     | "plugin" means a Claude Code plugin everywhere else in this repository      |
| `set-up-audio-plugin-validation`  | `set-up-clap-validation`         | Same collision, and shorter                                                 |
| `sign-and-notarize-macos-bundles` | `set-up-macos-signing`           | `lint-and-fix` is the only `X-and-Y` precedent; this configures a subsystem |
| `audit-ci-instruments`            | `check-ci-workflows`             | No `audit-*` family; "instruments" is fosforo's private jargon              |
| `plant-defects-to-verify-tests`   | `plant-defects`                  | No `<verb>-to-<verb>` precedent anywhere in the catalog                     |
| `capture-deferrals`               | `create-deferred-issues`         | Joins the `create-*` family; the original noun was vague                    |
| `project-status`                  | `review-project-status`          | Not verb-first; `review-branch` is the family                               |
| `manual-verification`             | `write-manual-verification-plan` | Not verb-first; `write-formalization-roadmap` is the precedent              |

## Source material

Every issue body should cite concrete artifacts. The richest are:

| Artifact                                                           | Repository | What it carries                                                              |
| ------------------------------------------------------------------ | ---------- | ---------------------------------------------------------------------------- |
| `build.zig` (867 lines)                                            | fosforo    | Provenance stamping, translate-c pipeline, optimize-mode fan-out, TSan steps |
| `.github/workflows/ci.yml` (1,106 lines)                           | fosforo    | Ten jobs, pinned tool installs with committed SHA256, measured timeouts      |
| `.github/actions/clap-validator/action.yml`                        | both       | Cached, rev-pinned clap-validator composite action                           |
| `scripts/assert-adhoc-signature`, `assert-distributable-signature` | fosforo    | The two halves of a signing assertion no `codesign --verify` can express     |
| `scripts/build-installer`, `notarize-installer`                    | fosforo    | `pkgbuild`/`productbuild`, `notarytool`, `stapler`, `spctl`                  |
| `scripts/read-provenance`, `install-plugins`                       | fosforo    | Prove which build landed in a shared plug-in folder                          |
| `scripts/race-check`, `smoke-leak-check`                           | fosforo    | Ordered assertions; control arm before absence                               |
| `src/canary.zig` (257 lines)                                       | fosforo    | Comptime source canaries over ordering-critical declarations                 |
| `AGENTS.md` (168 KB, ~60 gotchas)                                  | fosforo    | The measured-fact record; the theory-of-instruments table at lines 388-399   |
| `docs/adr/` (19 ADRs + README index)                               | fosforo    | The ADR house style, including amendment-by-issue sections                   |
| `docs/adr/0014-auval-enumerates-no-third-party-*.md`               | springer   | `auval` is not a signal on this machine, with five hypotheses ruled out      |
| `docs/plans/todo/2026-07-25-repo-foundation-and-phased-*.md`       | fosforo    | Six phases, exit criteria, the exclusive-resource table                      |
| `docs/plans/todo/2026-09-08-build-springer-*.md`                   | springer   | Eight phases, the verification-program table, tooling it says it will need   |
| `docs/plans/todo/2026-09-04-close-the-verification-gaps-*.md`      | fosforo    | The planted-defect program, stated as a principle                            |
| `cmake/CMakeLists.txt`, `cmake/entry.cpp`                          | both       | clap-wrapper consumer requirements; POST_BUILD ordering                      |

## Group A: Zig language support

### A1. `New skill: write-zig-code`

Label `new skill`, `zig`. Model on `plugins/write-go-code/` (SKILL.md plus `references/essential/checklist.md` and `references/comprehensive/*.md`), the right profile for a compiled language with a built-in formatter and official style guidance.

Comprehensive topics: naming (the upstream Zig Style Guide), error unions and `try`/`errdefer`, allocators and memory ownership, `comptime`, slices, optionals and sentinels, testing with `std.testing`, C interop via `translate-c`, and `build.zig` conventions.

Measured rules to embed, from fosforo's `.github/zig.instructions.md` and `AGENTS.md`:

- `testing.refAllDecls(@This())` per module plus one call per public container type declared at file scope; `refAllDeclsRecursive` was removed in Zig 0.16. Keep a checked list of the modules a test build compiles, so adding one to a source list and not the other fails the test step.
- Never `refAllDecls` a `translate-c` module: it leaves `@compileError` stubs and the sweep detonates on `__nonnull`.
- `b.runAllowFail` with `catch return null`, never `b.run`, for anything optional at configure time. `b.run` calls `process.fatal`, and a tarball with no `.git` must still build.
- `std.debug.assert` is an ordinary function, so its argument is evaluated in every optimize mode. The C "work inside an assert" bug class does not exist in Zig.
- `sanitize_thread` requires `.use_llvm = true` and `.link_libc = true`. Without the former, Zig 0.16's self-hosted x86_64 backend links the TSan runtime and emits no instrumentation, silently.
- Three optimize modes are three different programs: `strings -a` finds `reached unreachable code` in Debug and ReleaseSafe only, and a Debug-only assertion passes vacuously outside Debug.
- `@divFloor`/`@mod` rather than `/` and `%` wherever a negative operand is possible. Springer's degree arithmetic came from JavaScript, which floors; Zig truncates, and the refactor would compile and pass any test that only plays above the root.

Sources: the Zig Language Reference, the Zig Style Guide, std library conventions.

### A2. `New skill: scaffold-zig-cli`

Label `new skill`, `zig`. Model directly on `plugins/scaffold-rust-cli/` (275-line SKILL.md, 16 reference files). `scaffold-new-repo`'s existing `zig-cli` project type supplies only a `.gitignore` stanza and a README install snippet; it generates no Zig.

Reference files: `build-zig.md`, `build-zig-zon.md`, `main-zig.md`, `root-zig.md`, `makefile.md`, `gitignore.md`, `editorconfig.md`, `typos.md`, `ci-workflow.md`, `release-workflow.md`, `license.md`, `readme.md`.

Working templates already exist at `~/Development/seine/`: `build.zig.zon`, `Makefile`, `.github/workflows/{ci,release}.yml`. `set-up-ci`'s `references/ci-zig.md` and `references/makefile-zig.md` are the CI and Makefile halves and should be reused rather than duplicated.

Must-haves the transcripts justify:

- **Let Zig emit the fingerprint.** `error: invalid fingerprint: 0x…; if this is a new or forked package, use this value` appears in six separate project directories, because the value gets guessed instead of copied from the compiler's own output.
- **`minimum_zig_version` is mandatory**, because `set-up-ci`'s Zig template passes `zig-version-file: build.zig.zon` and `mlugg/setup-zig` resolves the toolchain by _omitting_ its `version:` input entirely.
- **Seed `.claude/settings.json`** with `Bash(zig build *)` and `Bash(zig fmt *)`. Fosforo eventually added exactly these to `settings.local.json`; springer's allowlist is still empty, so every build prompts.
- **An aggregate local gate.** Roughly 200 hand-spelled variants of `zig fmt --check build.zig src/ && echo …` appear across the corpus, no two alike. One `make check` target ends that.
- Homebrew's Zig is unpinned and floats to 0.17 on upgrade; `mlugg/setup-zig` or a pinned install is the only reliable source.

## Group B: audio-plugin support

### B1. `New skill: scaffold-clap-audio-plugin`

Label `new skill`, `audio`. The highest-value, most-repeated technical knowledge in the corpus: a macOS CLAP plugin authored once in Zig and projected outward to AUv2 by clap-wrapper.

Generates `build.zig` and `build.zig.zon` (with `clap` pinned), `src/clap/` bindings, `cmake/CMakeLists.txt`, `cmake/entry.cpp` and `entry.h`, `macos/Info.plist`, `scripts/build-audio-unit`, `scripts/install-plugins`, and a permanent-identifiers table.

The expensive knowledge to encode:

- **`translate-c` over a `zig cc -E -P` step, not over the headers directly.** Zig `translate-c` mishandles `#pragma once` under path aliasing: `clap/factory/../version.h` against `clap/version.h` yields 161 redefinition errors while plain clang is clean. The corpus holds 66 `expected unqualified-id` and 48 `unknown type name` errors from rediscovering this. Cost: object-like macros are consumed, so `CLAP_PLUGIN_FEATURE_*` must be restated and tested in `src/clap/c.zig`.
- **Comptime `@sizeOf`/`@offsetOf` assertions over every struct crossing the ABI.** A binding that compiles is not a binding whose layout is right, and the failure mode is a silent misread on the audio thread.
- **`features[0]` decides the AU type.** clap-wrapper derives `aumi` from `note-effect`; anything unrecognized falls back to `aumu` with a warning, so it fails by working wrongly rather than by failing.
- **Zig 0.16 writes static archives Apple's linker refuses** (`ld: 64-bit mach-o member … not 8-byte aligned`). Hand CMake an object file, obtained via `getEmittedBin()` rather than by depending on the Compile step, which writes no file.
- **A pass-through must not forward every event it is handed.** `clap-validator`'s `transport-fuzz-sample-accurate` catches echoing `CLAP_EVENT_TRANSPORT`; use an allowlist.
- **clap-wrapper still emits untrue sandbox claims** at v0.16.0 (`network.client` and `temporary-exception.files.all.read-write` beside `sandboxSafe = true`). A POST_BUILD script strips them, and **anything that rewrites the AU plist must run before signing**, which seals `Contents/Info.plist` into `_CodeSignature/CodeResources`.
- **The identifiers are permanent.** CLAP id, bundle id, and AU type/subtype/manufacturer codes get written into host project files; changing one after release makes the plugin read as missing in every project that used it.
- Draft CLAP extensions live in `clap/all.h`, not `clap/clap.h`. `clap_version_is_compatible` is only `major >= 1`, which is narrower than "compatible" suggests.

Depends on A2, B3 and B4.

### B2. `New skill: set-up-clap-validation`

Label `new skill`, `audio`. Wires `clap-validator` into CI and records what the other validators are actually worth.

- The composite action at `fosforo/.github/actions/clap-validator/action.yml`: `actions/cache/restore` keyed on `runner.os`, `runner.arch`, the validator rev and the Rust version, with **no `restore-keys`** (a partial match would silently run a validator built from a different commit), then `cargo install --git … --rev … --locked --root "$RUNNER_TEMP/clap-validator"`, then `cache/save` reusing the primary key. Neither input is defaulted, so a caller that forgets fails loudly.
- Pin by commit, not by tag: `clap-validator` reporting version `0.4.1` does not mean two binaries are the same.
- The `if: failure()` step that turns `--json --only-failed` into a `$GITHUB_STEP_SUMMARY` table.
- Bundle assertions that run _before_ validation: `codesign --verify --strict`, the ad-hoc signature assertion, and a provenance check.
- **`auval` is very likely not a signal.** Springer's ADR 0014 records that `auval -a` lists 58 components, every one Apple's, and that `AudioComponentFindNext` returns the same Apple-only set, with five hypotheses ruled out one at a time. Carry this so nobody re-runs that investigation. Related traps: `AudioComponentCache.plist` staleness, `killall -9 AudioComponentRegistrar`, and Logic hiding an effect because the track is mono.
- Validate **both** bundles, the `zig build` CLAP and the clap-wrapper-built one. They are different binaries.

Cross-reference G4, which moves the composite action upstream.

### B3. `New skill: set-up-macos-signing`

Label `new skill`. General-purpose macOS work extracted from fosforo, useful to any project shipping a signed artifact, not only audio plugins.

- `assert-adhoc-signature`: asserts a bundle is signed ad-hoc **and nothing more**, refusing a `runtime` flag, a `Timestamp=` or an `Authority=`. This is a negative that `codesign --verify` cannot express, and it is what keeps a development default from quietly acquiring a real identity.
- `assert-distributable-signature`: the exact inverse, requiring `Developer ID Application:`, hardened runtime and a secure timestamp. Catches the Apple _Development_ certificate trap that `security find-identity -v -p codesigning` will not show you.
- `build-installer`: `pkgbuild` plus `productbuild`, a `packaging/distribution.xml` carrying `hostArchitectures`, `allowed-os-versions` and both `enable_currentUserHome` and `enable_localSystem` domains, and a version cross-check across every file that restates the version.
- `notarize-installer`: `xcrun notarytool submit --keychain-profile`, `stapler staple`, `spctl --assess`, requiring `Developer ID Installer:`.
- Signing identity comes from an environment variable, never from `argv`, and has no default.
- `.gitignore` must carry `*.p8`: App Store Connect API keys are downloadable exactly once.
- The deployment target must stay in step across `build.zig`, `cmake/CMakeLists.txt`, `macos/Info.plist` and `packaging/distribution.xml`.

### B4. `New skill: stamp-build-provenance`

Label `new skill`. General-purpose. Solves the multi-worktree, one-install-folder hazard, which produced eight separate confused turns in the fosforo transcripts and voided two verification runs before it was built.

- Stamp branch, short commit and dirty flag at configure time. Two _separate_ `git rev-parse` calls, because `--abbrev-ref` is sticky and a combined call silently prints the branch twice. `git status --porcelain` for dirty. Use the allow-fail runner so a tarball with no `.git` degrades to an "unknown" value rather than failing the build.
- A `read-provenance` script with a `--check` mode, reading with `grep -a` rather than `strings` (which is an `xcrun` shim). The marker appears twice in Debug and once in ReleaseFast, so take the longest match, not the first.
- The marker survives only because something logs it; otherwise it is dead-stripped. Say so.
- An install step that copies, then compares hashes after the copy, reports the provenance of the bundle it is about to replace, and refuses to be confused by a hand-made symlink.
- A CI assertion that the marker exists and matches its shape, with a positive control run before any "this string is absent" assertion.

### B5. `New skill: write-realtime-audio-code`

Label `new skill`, `audio`. A style guide for the audio thread, in the shape of `write-go-code`.

Both projects state the same non-negotiable: nothing reachable from the audio thread allocates, locks, or makes a syscall. Beyond that: lock-free ring buffers rather than queues, release/acquire pairing and what a relaxed load actually costs you, sample-accurate event handling, parameters identified by stable ids rather than by index or name, versioned state save and restore, and a pure DSP core behind a seam that names no host type. Springer enforces that seam with a comptime assertion, and it is what makes most of the plugin testable without a host.

Pairs with C1: fosforo verified its ring's memory ordering under Thread Sanitizer specifically because a single-threaded test suite cannot see an ordering at all.

## Group C: verification methodology

### C1. `New skill: plant-defects`

Label `new skill`. The single most transferable idea in either repository, stated in both build plans:

> A test asserts a property of the code. Planting a defect asserts a property of the test, and the second does not follow from the first.

Content:

- **Plant tables** as a first-class artifact: planted defect, instrument, result, and a column naming the test that covers each row, which is what makes plants regress rather than being prose about a check nobody re-runs.
- **Ordered assertions.** An absence has to be told apart from an instrument that was not running: control arm first, then progress or parse, then the absence. Both `race-check` and `smoke-leak-check` are built this way.
- **Vacuous passes.** A blank readback passed fosforo's decay checks outright because `nan` compares false. A `ruff format --check` that reports zero files passes. An `actionlint` run without `shellcheck` on PATH silently skips every `run:` block and exits 0.
- **Structural uncoverability**, the third failure class beside false negative and false positive: code that no test binary compiles. Fosforo's shader watcher was gated behind `if (shader.live) struct {…} else struct {…}` where `live` folds in `!builtin.is_test`, so the real `poll` was not merely untested but not compiled, and no test written in the suite could have reached it.
- **Instrument-blindness tables.** Fosforo's runs six planted defects against six instruments and marks one row as covered by nothing, deliberately. Working that table out is what led it to _refuse_ a proposed peak-RSS instrument rather than build it.
- **Encoding a plant is not the same as covering it.** Two of fosforo's tests encoded a plant while being caught by something else entirely, because the planted value sat far outside a different bound.
- Optional but worth a section: comptime source canaries (`src/canary.zig`) for orderings a single-threaded suite cannot see, and TSan arms with a deliberately weakened control. TSan discriminates only an ordering that guards _non-atomic_ memory, so a payload has to be stood up or both arms come back clean.

### C2. `New skill: check-ci-workflows`

Label `new skill`. Fosforo names this failure class explicitly: **configured, believed to be running, silently not**. It hit four times, in its issues #28, #85, #87 and #99.

Checks the skill should run against a repository's workflows:

- `actionlint` without `shellcheck` installed skips every `run:` block and exits 0. See G1: the shared reusable workflow has this defect today.
- `pull_request:` carrying `branches: [main]` reads the _base_ ref, so a stacked PR gets no CI at all and nothing anywhere says so.
- `paths-ignore` that excludes the very files a check exists to examine. A spell checker whose workflow ignores `docs/**` and `*.md` runs on nothing; fosforo's `typos.yml` is a separate workflow for exactly this reason, and `.editorconfig` is deliberately absent from `ci.yml`'s ignore list. State the rule: a check must not be able to skip the change that governs it.
- `shfmt -d .` passes on a fresh CI checkout and fails locally, because `shfmt` does not read `.gitignore` and walks into vendored build trees. The correct selection is `git ls-files -z | xargs -0 shfmt -f | xargs -r <tool>`.
- `shfmt` must run with no formatting flags when checking; `shfmt -i 2 -d` silently ignores the file entirely.
- A tool whose config fails to parse should fail loudly, not quietly.
- Positive controls: does the format check report a non-zero file count, does `actionlint` print a `shellcheck` version line, does a "this string is absent" assertion have a matching "this string is present" run first.
- A `--fix`-mode trap: `markdownlint-cli2 --fix` ignores file arguments and rewrites everything matching its `globs`, including historical done-plans.

## Group D: session continuity

### D1. `New skill: review-project-status`

Label `new skill`. Twenty-two of 260 human turns (8.5%) are some form of "where are we?": _"I've lost track of where we are in the process, please summarize"_, _"Remind me why we paused part way through this work? … I forget how we set the plan up"_, _"Where does this project stand? Review docs, plans, commits, tests, PRs, etc."_

Reads the master plan, `gh issue list`, milestones, the worktree list, branch state and recent commits, and emits a "you are here" board: which phase, which of its exit criteria are met, what is in flight where, and what is unblocked.

Distinct from `suggest-next-issue`, which ranks issues but does not reconstruct plan position. Cross-reference open issues [#11](https://github.com/cboone/agent-harness-plugins/issues/11) and [#23](https://github.com/cboone/agent-harness-plugins/issues/23), which cover plan _lifecycle_; this covers plan _position_. Pairs with E2, which defines the phase structure it reads.

### D2. `New skill: create-deferred-issues`

Label `new skill`. Twenty-seven of 260 turns (10.4%) are the user saying "file that" about something the agent had already surfaced in prose: _"Create an issue to take care of shfmt"_, _"File an issue for the typos drift please"_, _"Create an issue for that last concern regarding fosforo_all. Then /pr"_.

Scans the session, the branch diff and the PR description for concerns the agent named and set aside, proposes the set as a batch, and files the approved ones through `create-issue` in one pass rather than one round trip each.

### D3. `New skill: write-manual-verification-plan`

Label `new skill`. Twelve turns ask some variant of _"What can I verify manually?"_, and the answers repeatedly fail on the same point: _"Arm 2: I'm not sure exactly what I'm looking for"_, _"5: I'm not sure what count you mean"_.

Emits a numbered, resumable checklist where every step states the action, the exact expected observation, and how to tell a null result from a broken instrument. Persists it to the plan or issue so it survives the session, and accepts partial results (_"That's a lot of testing. Let's save it for later in the phases. I did check 1 and 2, nothing happened (as desired)"_) without losing state.

Named for the general case rather than for a DAW: it covers a simulator, a browser, or a physical device equally.

## Group E: documentation conventions

Both repositories independently converged on the same two document classes, and nothing in the catalog produces either.

### E1. `New skill: write-adr`

Label `new skill`. Fosforo has 19 ADRs plus a README index; springer has 14. The format is identical in both, because springer copied it.

The skill covers authoring and directory maintenance together:

- The document shape: `# NNNN. Title`, `**Status:**`, `## Context`, `## Decision`, `## Consequences`.
- **ADRs are superseded, not edited.** A decision that changes gets a new ADR; the old one records what was believed and why. Refusals are recorded on purpose, so the argument does not get relitigated in code review.
- **Amendment sections**: `## Amended by issue #NN: <title>`, appended over time. Fosforo's ADR 0013 has ten.
- The `docs/adr/README.md` index table, kept in step with the directory.
- The **non-negotiables list** in `AGENTS.md` as the ADRs' index of record for agents: one bullet per ADR, each linking to it, under a heading that says plainly "do not relitigate these in code review; supersede them with a new ADR instead." Both repositories carry this verbatim, and it is what makes the ADR directory load-bearing rather than decorative.
- Springer's ADR 0014 is the model for an ADR that settles a question by measurement: a five-row hypothesis/test/result table of ruled-out causes, and an explicit "What this does not establish" section.
- Documentation rules that go with the format, from `.github/docs.instructions.md` in both repositories: point-in-time measured facts must not be hedged or future-proofed; when correcting a measured figure, grep the old value repository-wide; done plans are historical records whose `path:line` citations are pre-change by construction.

Note in the body that `scaffold-new-repo` should gain a `docs/adr/` stub with the index README, as a small follow-up once this lands.

### E2. `New skill: write-phased-build-plan`

Label `new skill`. The direct analog of `write-formalization-roadmap`, which the catalog already carries for proof-assistant projects.

Both repositories run from a master plan that stays in `docs/plans/todo/` permanently rather than moving to `done/`. Fosforo's has six phases, springer's eight. The shared structure:

- A phase table with scope and status, mirrored into the README so the public status and the working status cannot drift.
- **Per-phase exit criteria**, and the rule that a milestone is its exit criteria rather than a list of steps.
- **Issues filed one phase at a time**, so a phase marked planned deliberately has none yet.
- A **verification program** table: layer, command, and whether it runs in CI. Springer's has thirteen rows, including three marked "not in CI, by hand" with the reason.
- **Sequencing that puts the largest unknown first.** Springer proves the Audio Unit path in Phase 1 against an empty pass-through plugin, explicitly because discovering a wrapper limitation after the musical engine is written is far more expensive.
- An **exclusive-resource table** naming what can run beside what. Fosforo's records that only one workstream at a time may need the DAW, which is the constraint F6 makes machine-readable.
- A risks section, and an identifiers-permanence table where the project ships identifiers a host will persist.

Pairs with D1, which reads this structure to report position.

## Group F: cross-plugin edits

### F1. `feat: close the Zig gaps left by #223 across the plugin ecosystem`

Umbrella issue with per-plugin sections, following the shape of #223 itself. Labels `enhancement`, `zig`.

| Plugin                        | Work                                                                                                                                                                                                     |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `set-up-linters`              | Add `references/languages/zig.md`; the `languages/` directory has nine files and no Zig. Add a `build.zig` → `zig fmt` row to the existing-linter detection table. Add `zig` to the marketplace keywords |
| `lint-and-fix`                | Add Zig detection. Its config-to-tool table has no `build.zig` row, so a Zig repository's formatter is invisible to it; Zig appears only as a "skip this reusable workflow" note                         |
| `refresh-project-scaffolding` | Add a Zig row to the detection table and Zig entries to the `.editorconfig`, `.gitignore`, Makefile-target and release-workflow expectation sections                                                     |
| `bootstrap-project`           | Add Zig to `references/overlap-rules.md` and the key-overlap bullets, once A2 lands                                                                                                                      |
| `set-up-secret-scanning`      | Document the gitleaks allowlist for `build.zig.zon`: Zig multihashes read as credentials. Both repositories carry the identical stanza                                                                   |
| `set-up-ci`                   | Add a `check` aggregate target to `references/makefile-zig.md`; document the `run-scrut` wiring in `references/ci-zig.md`                                                                                |
| `scaffold-new-repo`           | Point the "pairs with" list at `scaffold-zig-cli` once A2 lands                                                                                                                                          |

Depends on A2 for the last two rows.

### F2. `feat: make typos a cross-language linter option in set-up-linters`

Label `enhancement`. `typos` appears in `set-up-linters` only inside `references/languages/rust.md` and the Rust row of `references/checklist.md`. There is no cross-language option; `cspell` is what it recommends for everything else. Springer's Phase 0 plan records the consequence plainly: "`typos.toml` was written by hand. No skill offers typos outside its Rust path."

Add `typos` as a language-independent choice with a starting `typos.toml`. Both source repositories converged on the same two `extend-ignore-re` entries, and the reasons should carry across: a backtick-anchored `[0-9a-f]{7,40}` pattern, because a pinned short SHA like `91f9abd` otherwise reads as a misspelling of "and"; and a `<!-- spellchecker:off -->` … `<!-- spellchecker:on -->` block, because `typos` has no inline directive.

Note that `extend-words` and `extend-identifiers` are not interchangeable: `typos` splits identifiers into words, so which one you need depends on where the token appears. Note also that running both `cspell` and `typos` means two dictionaries to maintain, so this is an either/or, not an addition.

### F3. `feat: add verification-aware conventions to write-bash-scripts`

Label `enhancement`. `write-bash-scripts` already covers `set -euo pipefail`, sysexits codes and `TRACE` tracing. Missing, all of it earned:

- **A `--check` mode on any script that rewrites a file.** A rewriting step cannot detect its own absence, so CI has to assert the result independently. Both of fosforo's plist-correcting scripts carry one.
- **Assert the control fired before believing an absence**, the ordered-assertion discipline from C1 in its shell form.
- **File selection**: `git ls-files -z | xargs -0 <tool> -f | xargs -r <tool>` rather than walking the tree, because these tools do not read `.gitignore`.
- **Shell discovery is by shebang; shell styling is by name**, which is why an `.editorconfig` section for extension-less scripts is a hand-maintained list.
- **A pipe swallows the exit code you care about.** `set -o pipefail` is already recommended, but the failure mode deserves naming: a `cargo install … | tail` reported success while the install had failed.
- Two-tier return codes: helper functions return distinct small integers that `main` maps to sysexits values.

### F4. `feat: derive timeout-minutes from measured run history in optimize-runner-usage`

Label `enhancement`. `optimize-runner-usage` adds `timeout-minutes` but does not read the Actions API, so the value is guessed. Fosforo's rule is that every timeout is measured, not copied: roughly 4x the slowest observed run, with the figure and the sample size recorded in a comment beside it, plus documented exceptions. The consequence of guessing is visible in springer, which inherited fosforo's numbers under the comment "Carried from fosforo, which measured 24s max over 29 runs on a repository of comparable size. Not yet measured here."

Add a step that queries `gh api` for completed runs per workflow, reports observed maximum and sample size, and writes both into the comment. Cross-reference `cboone/gh-actions#81`.

### F5. `chore: validate cross-references between skills in bin/validate-plugins`

Label `maintenance`. During springer's Phase 0, `bootstrap-project` sent the agent to read `plugins/set-up-ci/commands/set-up-ci.md`, a path that no longer exists, and invoked skills under their pre-rename hyphen-less names (`setup-ci`, `setup-linters`). The source had already been fixed; the broken instructions were still what the agent loaded. The hand-work that followed is recorded in springer's Phase 0 plan.

Add a check to `bin/validate-plugins` that every skill name and repository-relative path referenced inside a `SKILL.md` body resolves. This catches the whole class at merge time rather than in a downstream project.

### F6. `feat: record an exclusive-resource claim in create-worktree`

Label `enhancement`. Lower priority, but it recurs. Fosforo can only run one workstream at a time that needs the DAW, and the constraint had to be restated repeatedly: _"in this project we only ever run one work stream that requires host usage at a time"_ was sent three times, growing each time. Related: _"Are there any open issues that can be done in parallel with the other work? That don't need exclusive host access, in other words"_ and _"Does that sequence include consideration of which issues might involve verification that conflicts with other worktrees?"_

Let a worktree declare and hold a named exclusive resource, so `create-worktree`, `suggest-next-issue` and `review-project-status` can all see who currently owns it. E2's exclusive-resource table is the human-readable half of the same idea.

## Group G: issues for `cboone/gh-actions`

Filed against the actions repository, not this one. Its label set is the standard GitHub default plus `in progress`, `dependencies` and `javascript`, so use `bug` and `enhancement`.

### G1. `fix: lint-github-actions.yml never installs shellcheck, so actionlint skips every run block`

Label `bug`. Confirmed by reading `.github/workflows/lint-github-actions.yml`: it installs `actionlint` and runs it, and nothing on the runner provides `shellcheck`. `actionlint` shells out to `shellcheck` for `run:` blocks and, when it is absent, skips them silently and exits 0. Every caller of this reusable workflow currently believes its `run:` blocks are linted and they are not.

Fosforo's own `actionlint` job installs shellcheck alongside actionlint for exactly this reason, with a "Report tool versions" step whose purpose is to make the shellcheck version line visible as a positive control. Fix: install a pinned `shellcheck` in the workflow and print both versions before running.

### G2. `fix: lint-shell.yml discovery misses cmake/ and extension-less scripts outside bin, scripts and script`

Label `bug`. `lint-shell.yml` finds files two ways: `find . \( -name '*.sh' -o -name '*.bash' \)`, and a `file --mime-type` sweep restricted to `bin/`, `scripts/` and `script/`. Fosforo has thirteen extension-less shell scripts, two of which live in `cmake/`, and springer recorded the same gap. Neither is linted today, and springer's Phase 0 plan notes the related trap that the job "passes by finding nothing. It is wired, not exercised."

Fix: replace the discovery with `git ls-files -z | xargs -0 shfmt -f`, which reads shebangs across the whole tracked tree and needs no directory allowlist. Add a step that fails, or at minimum annotates, when the discovered set is empty, so a wired-but-unexercised job is visible.

Note that this is not `#83`, which is the `lint-text.yml` / `github.job_workflow_sha` bug.

### G3. `feat: extract a pinned-tool install into one composite action`

Label `enhancement`. `lint-github-actions.yml` and `lint-shell.yml` each hand-roll roughly forty lines of the same thing: `uname` os and arch mapping, a download, a checksum comparison with a `sha256sum`/`shasum` fallback, an extract, and a `$GITHUB_PATH` append. `shfmt`'s copy additionally hard-codes four checksums and refuses any version but `3.13.1`, because upstream stopped publishing `sha256sums.txt` after v3.13.0.

Fosforo repeats the same shape five more times, for `shfmt`, `shellcheck`, `ruff`, `typos` and `actionlint`, each with a committed SHA256. One composite action taking tool, version, checksum and archive-member would collapse all of it and give one place to fix the `shfmt` version pin. Cross-reference `#61`, which is about the pinned versions themselves going stale.

### G4. `feat: add a reusable clap-validator workflow`

Label `enhancement`. Fosforo and springer carry byte-similar copies of `.github/actions/clap-validator/action.yml`, and springer's is a copy of fosforo's. The shape is settled: cache keyed on os, arch, validator rev and Rust version with **no `restore-keys`**, `cargo install --git --rev --locked --root "$RUNNER_TEMP/clap-validator"`, `cache/save` reusing the primary key, and no defaults on either input.

Deliberately keep the `validate` step in the calling job rather than in the action, which is fosforo's own choice: the gate should be readable in the job that runs it. Pairs with B2, which will point at this once it exists.

## Definition of done, per new-plugin issue

Every `New skill:` issue body should close with the repository's own checklist, from `AGENTS.md`:

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json` at version `1.0.0`.
1. Register in `.claude-plugin/marketplace.json`, alphabetically, with a category from the nine valid values.
1. Write a per-plugin `README.md`.
1. Add a row to the matching category table in the root `README.md`, using the marketplace `description` verbatim.
1. Regenerate with `bin/build-codex-marketplace` and `bin/build-opencode-mirror` and commit both generated trees; CI fails on drift.
1. Recompute `metadata.version` with `bin/compute-catalog-state`.

Fourteen new plugins are proposed. The catalog state as of this branch's rebase onto main is `catalog-M63-m80-p146-n51`; if all fourteen land at `1.0.0` it becomes `catalog-M77-m80-p146-n65`. Recompute rather than trusting that figure, since main moves.

Category assignments: `code-quality` for A1, B5, C1, C2; `scaffolding` for A2, B1; `ci-and-release` for B2, B3, B4; `issues-and-worktrees` for D1, D2; `writing` for D3, E1, E2.

## Labels

Two new labels in `cboone/agent-harness-plugins`, following the `javascript` precedent:

- `zig` for A1, A2, F1
- `audio` for B1, B2, B5

`new skill` applies to A1, A2, B1-B5, C1, C2, D1-D3, E1, E2. `enhancement` applies to F1-F4 and F6; `maintenance` to F5.

## Execution

1. Create the `zig` and `audio` labels with `gh label create`.
1. Draft each issue body to a tmpfile and file it with `gh issue create --title … --body-file …`, per the `create-issue` skill's tmpfile pattern. Do not pass long bodies as inline Bash arguments, and `rm` the tmpfile in a separate Bash call.
1. File Groups A through F against `cboone/agent-harness-plugins` in the order above, so dependent issues can reference the numbers of the ones they depend on: A2 before F1's `bootstrap-project` and `scaffold-new-repo` rows; A2, B3 and B4 before B1; E2 before D1.
1. File Group G against `cboone/gh-actions`.
1. After filing, add the cross-reference lines: F1 points at A2; B1 points at A2, B3 and B4; C1 and B5 point at each other; C2 points at G1; B2 points at G4; D1 points at E2, #11 and #23; F4 points at `cboone/gh-actions#81`; G3 points at `cboone/gh-actions#61`.
1. Add the transcript evidence to the existing [#334](https://github.com/cboone/agent-harness-plugins/issues/334) as a comment rather than as a new issue; see below.

## Already addressed on main, so not filed

The rebase onto main brought in 24 commits, three of which overlap this research.

**Markdown table alignment is solved.** [#325](https://github.com/cboone/agent-harness-plugins/pull/325) set `MD060: false`, dropped `markdownlint-rule-force-align-table-columns`, and handed alignment to Prettier, which has a fixer where markdownlint has none at any version. [#334](https://github.com/cboone/agent-harness-plugins/issues/334), [#335](https://github.com/cboone/agent-harness-plugins/issues/335) and [#336](https://github.com/cboone/agent-harness-plugins/issues/336) are already open to propagate that through `write-markdown`, `set-up-linters` and `refresh-project-scaffolding`.

The transcript mining produced hard numbers that belong on #334 as a comment, since they quantify the cost the fix removes: **1,940 `MD060` violations across 48 of roughly 65 transcript files**, 16x the next-most-common rule, and a throwaway `align_tables.py` written from scratch **25 times** to do the padding by hand. That comment is [posted](https://github.com/cboone/agent-harness-plugins/issues/334#issuecomment-5606377130).

The same mining supports #334's stated constraint that the manual procedure cannot simply be deleted, because it still serves repos with markdownlint and no Prettier. **Fosforo and springer are both exactly that case**: fosforo has no Prettier at all, and springer's `.prettierignore` excludes `*.md` outright with the recorded reason that "markdownlint owns Markdown, uncontested … Two formatters with opinions about the same file is one more than can be satisfied." Both still carry `"MD060": { "style": "aligned" }`. They are the concrete instances of the seven repos #334 counts, and migrating them is downstream repository work rather than a plugin issue.

Two further exclusions, unchanged:

- **Copilot review-comment shapes.** The "Suppressed comments" and nested-comment cases the transcripts flag are already open as [#324](https://github.com/cboone/agent-harness-plugins/issues/324).
- **`AGENTS.md` size management.** Fosforo's is 168 KB against a 150 KB limit. `clean-up-agent-config` already proposes splitting a large instruction file into a core plus scoped files, and both repositories have partly adopted the `.github/*.instructions.md` pattern it describes, so this is covered.

## Verification

This plan produced issues, not code, so verification is that the filed set is complete, correct and non-duplicative. All of the following were run after filing.

1. **Done.** `gh issue list --repo cboone/agent-harness-plugins --state open --limit 100` returns 38: the twenty new ones (#338-#357) plus eighteen previously open. The plan predicted twenty previously open; #323 and #326 were closed by other work at 17:29Z, mid-filing, which accounts for the difference.
1. **Done.** `gh issue list --repo cboone/gh-actions --state open` returns 10: the four new ones (#85-#88) plus the six that were already open. None duplicates `#83` (which is `lint-text.yml`, not shell discovery), `#81` or `#61`; #87 and #85 both cite #61 rather than restating it.
1. **Done.** No duplicates of `#223`, `#248`, `#249` or `#271`; #352 supersedes none of them and cites #223 as the work it continues.
1. **Done.** All fourteen new-plugin issues carry `new skill`. `gh label list` shows `zig` and `audio`, both created for this batch.
1. **Done.** Every proposed name is verb-first kebab-case inside an existing family; see [Naming](#naming) for the eight corrected during planning.
1. **Done.** Cross-reference comments posted where a body said "filed separately": #338, #339, #340, #341, #342, #343, #345, #346, #347, #348, #349, #351 and #354.
1. **Done.** #334 carries the transcript-evidence comment and no duplicate MD060 issue was filed.
1. **Done.** `npx --no-install prettier --check` and `npx --no-install markdownlint-cli2` both pass on this file.

Remaining, for whoever picks up the work rather than for this plan:

- Recompute the catalog state with `bin/compute-catalog-state` at implementation time rather than trusting the projected `catalog-M77-m80-p146-n65`, since main moves.
