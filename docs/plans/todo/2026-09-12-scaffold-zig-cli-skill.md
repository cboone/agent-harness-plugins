# Add a `scaffold-zig-cli` skill plugin

Closes [#339](https://github.com/cboone/agent-harness-plugins/issues/339).

## Context

The catalog scaffolds Go CLIs, Go libraries, Rust CLIs and Lean libraries, but not Zig. [#223](https://github.com/cboone/agent-harness-plugins/issues/223) added a `zig-cli` _project type_ to `scaffold-new-repo`, and that type reaches exactly three things: the `.gitignore` template, the README installation snippet, and the `.gitignore` detection heuristic. It emits no `build.zig`, no `build.zig.zon`, no sources, no Makefile and no workflows. Bootstrapping [springer](https://github.com/cboone/springer) hit that gap and its plan records the hand-work as a deliberate deviation.

Four failures recur across the transcript corpus and across seine, strength, fosforo and springer. Each one is a requirement here:

- The `build.zig.zon` fingerprint gets guessed instead of copied from the compiler's own diagnostic, in six separate project directories.
- `minimum_zig_version` goes missing, so `zig-version-file: build.zig.zon` has nothing to resolve and CI cannot pick a toolchain.
- `.claude/settings.json` ships with an empty allowlist, so every `zig build` prompts. springer is still in that state; fosforo worked around it in the untracked `settings.local.json`.
- There is no aggregate local gate, so the corpus holds roughly 200 hand-spelled variants of `zig fmt --check … && echo "fmt clean"`, no two alike.

The outcome: `/scaffold-zig-cli` produces a Zig CLI that builds, tests, formats and releases on the first try, with the toolchain version single-sourced from `build.zig.zon`.

## Scope boundaries

Out of scope, by the issue's own words and by [#352](https://github.com/cboone/agent-harness-plugins/issues/352)'s split:

- `bootstrap-project`'s `references/overlap-rules.md`, applicability table and ordering list.
- `scaffold-new-repo`'s "pairs with" list.
- `set-up-ci`'s `references/makefile-zig.md` and `references/ci-zig.md` (the `check` target and the `run-scrut` worked example belong to #352).
- A `write-zig-code` skill ([#338](https://github.com/cboone/agent-harness-plugins/issues/338)).

"Reuse, not duplicate" cannot mean cross-plugin file reads: a skill resolves `./references/…` only inside its own plugin, and plugins install independently. Every scaffolder already carries its own copy of the CI workflow and Makefile that `set-up-ci` also ships. So reuse here means the emitted content agrees with the canonical template, not that the file is shared.

## Decisions

**Zig 0.16 only.** 0.16 removed `std.io` and `std.fs.File` and changed `main`'s shape, so 0.15-era source does not compile. strength, fosforo and springer are all pinned to 0.16.0 and the installed toolchain is 0.16.0. One template set, plus an `## Error Handling` entry for older toolchains.

**seine is not the ancestor of the source templates.** Its `src/main.zig` uses `std.io.fixedBufferStream` and `std.fs.File.stdout()`, both gone in 0.16. Its Makefile and CI also omit `build.zig.zon` from the format check and restate the Zig version in four jobs. Use it for repository shape, not for Zig source.

**Release workflow calls the reusable workflow.** `cboone/gh-actions/.github/workflows/release-zig-binaries.yml`, SHA-pinned, with `binary-name` and `zig-version-file: build.zig.zon`. This matches `scaffold-rust-cli`'s `release-workflow.md` structurally and keeps the version single-sourced. It supersedes the inline `mlugg/setup-zig` workflow the issue named from `set-up-installers`. Current pin: `17f94b08428565213e70ae19c37a7be894a172d2 # v3.1.1`, for both this and `run-zig-ci.yml`. The `ci-zig.md` copy in `set-up-ci` still pins `v3.0.0`; do not update it here.

**The fingerprint diagnostic in the issue is the wrong one.** `missing top-level 'fingerprint' field; suggested value: 0x…` is what an omitted field produces. `invalid fingerprint: 0x…; if this is a new or forked package, use this value: 0x…` fires only when the field is present and wrong. Both strings are in the 0.16.0 binary. The skill must accept either and take the **last** `0x[0-9a-f]{16}` on the line, or it will grep for a message that never appears and stall. Never copy a fingerprint from another project.

**No argument-parsing dependency.** Hand-rolled `--help` / `--version`, `.dependencies = .{}` left empty. A dependency means a multihash in `build.zig.zon`, which needs `zig fetch --save` at scaffold time and reads as a credential to gitleaks. All four reference repos hand-roll. No `-with-clap`-style variant, matching the issue's single `main-zig.md`.

**`--version` reads the manifest.** `const manifest = @import("build.zig.zon");` in `build.zig`, fed through `b.addOptions()`, so the version has one home. Proven at `/Users/ctm/Development/fosforo/build.zig:5,383`.

## Files to create

`plugins/scaffold-zig-cli/`, modeled on `plugins/scaffold-rust-cli/`:

- `.claude-plugin/plugin.json`: nine alphabetical keys, `"version": "1.0.0"`, `"skills": "./skills"`, keywords `["cli", "scaffolding", "zig"]`. No `.codex-plugin/` (skill-only plugins do not get one).
- `README.md`: `scaffold-rust-cli`'s shape. Opening paragraph is the marketplace `description` verbatim, then `**Type:**` / `**Trigger:**`, `## Installation`, `## What It Does`, `## Usage`, `## Examples`, `## Recommended Permissions`, `## See Also`. Link only to plugins that exist; mention `write-zig-code` as plain prose without a link, since `markdownlint-rule-relative-links` fails on a missing target.
- `skills/scaffold-zig-cli/SKILL.md`: `## Workflow` with numbered steps in `scaffold-rust-cli`'s order (gather project information, detect user identity, verify the target directory, initialize git, one step per generated file, seed `.claude/settings.json`, create directory stubs, verify the build, create the initial commit, update Copilot instructions, summary), then `## Error Handling`, `## Reference Templates`, and the `## Refresh cboone/gh-actions SHAs before scaffolding` block reproduced verbatim from `scaffold-rust-cli`.

Reference templates under `skills/scaffold-zig-cli/references/`, in generation order: `build-zig-zon.md`, `build-zig.md`, `root-zig.md`, `main-zig.md`, `typos.md`, `makefile.md`, `gitignore.md`, `editorconfig.md`, `ci-workflow.md`, `release-workflow.md`, `license.md`, `readme.md`. Each follows the house shape: `# … Template` H1, an instruction paragraph, one fenced template, `## Notes`.

### What the templates must get right

- **`build.zig.zon`**: `.name` is an enum literal, so a hyphenated project needs `.name = .@"PROJECT-NAME"`; recommend a snake_case identifier. Emitted without `.fingerprint`, filled in from the diagnostic, and written back with the `// Changing this has security and trust implications.` comment. `minimum_zig_version` normalized from `zig version` to `MAJOR.MINOR.PATCH`, since a dev toolchain prints `0.16.0-dev.164+bc7955306` and CI would then install a dev build. `.paths` lists `build.zig`, `build.zig.zon`, `src`, `LICENSE`.
- **`build.zig`**: `b.addModule` over `src/root.zig` carrying **both** `target` and `optimize`. `optimize` is optional there and the `zig init` template omits it, which silently pins library tests to Debug even under `zig build test -Doptimize=ReleaseFast`. A root module without a resolved `target` panics outright.
- **`src/main.zig`**: `pub fn main(init: std.process.Init) !u8`. Argv via `init.minimal.args.toSlice(arena)`, never `args.iterate()`, whose iterator is a `@compileError` on Windows and WASI and would fail the cross-compile job on the first push. Return `u8` rather than calling `std.process.exit`, which skips the buffered writer's flush. Stdout through `Io.File.stdout().writer(io, &buf)` and its `.interface`.
- **`src/root.zig`**: the library module, one public function taking an `*Io.Writer`, one `test` block capturing into `Io.Writer.fixed`. A test must never write to real stdout: under `zig build test` stdout is the build runner's IPC channel and printing to it corrupts the protocol.
- **`makefile.md`**: a superset of `set-up-ci`'s `makefile-zig.md`, the way `scaffold-rust-cli`'s Makefile is a superset of `makefile-rust.md`. Keep that file's `fmt` = check / `format` = write convention rather than seine's inverted pair. Add the `check` aggregate gate the issue requires, plus scrut and cross-language targets. Format targets name `build.zig.zon` explicitly: `.zon` is formatted by `zig fmt` in 0.16, and both seine's Makefile and the reusable CI workflow's `zig fmt --check src/ build.zig` silently skip the manifest.
- **`ci-workflow.md`**: byte-aligned with `set-up-ci`'s `ci-zig.md` yaml except for the refreshed SHA. Keep `zig-version-file: build.zig.zon` and `run-cross-compile: true`.
- **`editorconfig.md`**: `[*.zig]`, `[build.zig]`, `[build.zig.zon]` at `indent_size = 4`, matching `set-up-linters`' `references/tools/editorconfig.md`.
- **`.claude/settings.json` seeding**: merge `Bash(zig build*)`, `Bash(zig fmt*)` and `Bash(zig version)` into `permissions.allow`, preserving any existing entries, and create the file with the `$schema` line if absent. `scaffold-new-repo` writes the empty-allowlist version, so this step usually merges rather than creates. No space before the `*`, so bare `zig build` matches too.

## Files to modify

- `.claude-plugin/marketplace.json`: insert the entry between `scaffold-rust-cli` and `set-up-ci`, `"category": "scaffolding"`, `"source": "./plugins/scaffold-zig-cli"`, `"version": "1.0.0"`. Keep `description` at or under 155 characters so the root README table does not need re-padding.
- `README.md`: a `Scaffold Zig CLI` row as the new last row of the Scaffolding table, description verbatim from the catalog; and add the plugin plus the Zig toolchain to the Scaffolding `**External tools:**` bullet. Leave `## Contents` alone.
- `.claude-plugin/marketplace.json` `metadata.version`: recompute with `bin/compute-catalog-state`.
- Regenerate `dist/codex/`, `.agents/plugins/marketplace.json` and `dist/opencode/` with `make build`. `git add` the new `dist/opencode/skills/scaffold-zig-cli` symlink explicitly: `bin/validate-plugins` never checks the OpenCode mirror, and only CI's `git status --porcelain` step catches an untracked one.

No `tests/scrut/` or `Makefile` change: the plugin ships no scripts, and no test enumerates plugins or asserts a count.

## Verification

1. **The templates actually build.** Scaffold a throwaway project from the finished templates into the scratchpad and run `zig build`, `zig build test`, `zig fmt --check build.zig build.zig.zon src`, then exercise `--help`, `--version`, an unknown flag (expect a non-zero exit) and a positional argument. This is the step that catches a 0.16 API slip, and it doubles as a rehearsal of the skill's own "Verify the Build" step. Confirm the fingerprint round trip end to end: omit the field, capture the real diagnostic text, paste, rebuild clean.
2. **Repository gates.** `make build` then `make test-all` (lint, validate, scrut). `bin/check-cross-references` on its own while editing, since rule 19 resolves `./references/…` and any backticked name next to the word "skill" against `plugins/`.
3. **Placeholder hygiene.** Keep angle-bracket placeholders unpadded: `tests/scrut/repo-tooling.md` greps the whole tree for `< foo >` and fails on it. Use the house `PROJECT-NAME` form.
4. **Versions before the PR.** Run the `check-versions` skill. PR #391 also adds a plugin, so the catalog state tag has to be recomputed if that merges first.

## Notes for follow-up, not for this branch

- `cboone/gh-actions`' `run-zig-ci.yml` runs `zig fmt --check src/ build.zig` and never checks `build.zig.zon`, so a malformed manifest passes CI. That belongs in the gh-actions repo.
- `AGENTS.md`'s "53 plugin READMEs … accounts for 51" counts are stale against the current 52.
