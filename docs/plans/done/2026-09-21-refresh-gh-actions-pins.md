# Refresh the cboone/gh-actions pins across plugin templates

Closes #399. Supersedes #383.

## Context

Every `cboone/gh-actions` reference in the plugin templates was pinned to `91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0`, except the two `scaffold-zig-cli` templates added by #339, which were pinned to `v3.1.1` when they were authored. The repository therefore emits inconsistent pins: a Zig project scaffolded today gets one release, a Rust project another.

The 11 skills carrying the `## Refresh cboone/gh-actions SHAs before scaffolding` block tell the agent to resolve the current tag before emitting a workflow, so emitted workflows are not necessarily stale. That block is an instruction rather than a guarantee: it depends on the agent following it and on `gh` being authenticated, and a stale template is what ships when either fails. Reviewing a template diff also means reading a pin that has been wrong for several releases, which trains the reader to skip the line.

Both issues predate the current upstream state. #383 targets v3.1.0 and #399 targets v3.1.1. Current latest is **v4.1.0** (`bbe15187a1a8c60caded9295d1d2d90338a0bb93`), released 2026-09-21, four releases past #383's target. v4.0.0 is a major release, so this is a deliberate upgrade rather than a hash swap, and the sections below record what was checked.

`bin/version-audit` already covers these pins. Issue #419 lists `cboone/gh-actions` drift in both `plugins/` and `.github/workflows/ci.yml`, so the recurrence concern raised in #399 needs no code change. That finding is reported rather than acted on.

## What v4 changes, and why the templates still need no input edits

The [v4 migration guide](https://github.com/cboone/gh-actions/blob/v4.1.0/docs/migrations/v4.md) lists the inputs whose handling changed. Every ordinary input now reaches its shell step through an `env:` mapping instead of being interpolated into `run:` source, so values arrive literally and multi-line values are rejected rather than silently truncated.

| Workflow                    | Inputs the guide flags                                          | Passed by our templates |
| --------------------------- | --------------------------------------------------------------- | ----------------------- |
| `run-go-ci.yml`             | `test-flags`, `codecov-files`                                   | none                    |
| `release-go-binaries.yml`   | `goreleaser-args`                                               | none                    |
| `run-rust-ci.yml`           | `test-args`, `clippy-args`, `extra-components`, `codecov-files` | none                    |
| `release-rust-binaries.yml` | `build-args`                                                    | none                    |
| `run-zig-ci.yml`            | `fmt-paths`, `cross-targets`                                    | none                    |
| `release-zig-binaries.yml`  | `targets`                                                       | two, both safe          |

The two `targets` values are `"x86_64-apple-darwin aarch64-apple-darwin"` in `scaffold-rust-cli/references/release-workflow-macos-only.md` and `${{ matrix.target }}` in `set-up-installers/SKILL.md`. Both are plain, non-empty and space-separated, which the guide states behaves exactly as before. No template pins `audit-version` or `llvm-cov-version`, so the Rust checksum change does not apply. `cross-targets` and `fmt-paths` are left at their defaults, and both defaults are non-empty at v4.1.0.

So no template needs an input edit. Three v4 changes are nonetheless visible to a scaffolded repository on its first CI run, and each gets a note (see Change 2).

## Changes

### 1. Repoint every SHA-pinned ref to v4.1.0

Replace `91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5 # v3.0.0` and `17f94b08428565213e70ae19c37a7be894a172d2 # v3.1.1` with `bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0`. This is a uniform substitution across 41 references in 25 canonical files:

| Plugin                    | Refs | Files |
| ------------------------- | ---- | ----- |
| `set-up-ci`               | 9    | 6     |
| `set-up-linters`          | 9    | 2     |
| `set-up-installers`       | 5    | 1     |
| `scaffold-rust-cli`       | 4    | 4     |
| `add-goreleaser-homebrew` | 3    | 2     |
| `scaffold-go-library`     | 3    | 2     |
| `scaffold-go-cli`         | 2    | 2     |
| `scaffold-zig-cli`        | 2    | 2     |
| `set-up-secret-scanning`  | 2    | 2     |
| `add-scrut-cli-tests`     | 1    | 1     |
| `manage-repo-licensing`   | 1    | 1     |

Leave untouched: the placeholder SHA `1234567890abcdef1234567890abcdef12345678` in `pin-everything`, which is a deliberate illustration, and the `CBOONE-GH-ACTIONS-SHA` / `CBOONE-GH-ACTIONS-TAG` tokens in `scaffold-lean-library`, which that skill resolves at scaffold time.

### 2. Add targeted notes where v4 changes what a scaffolded repo sees

Short notes only, placed in the Notes section each template already has.

- `manage-repo-licensing/skills/manage-repo-licensing/references/verification.md`: `run-reuse` installs reuse 6.2.0, up from 5.0.2. `reuse lint` now reads whole files rather than stopping after the first 4 KiB, so copyright or license text deep in a file is found and may need `REUSE-IgnoreStart` and `REUSE-IgnoreEnd`; a new Invalid SPDX License Expressions criterion can fail a repository that previously passed; and Bad licenses now considers only `LICENSES/`. There is no opt-out, because the action installs from a hash-pinned requirements file.
- `set-up-ci/skills/set-up-ci/references/ci-shell.md` and `set-up-linters/skills/set-up-linters/references/tools/github-actions-ci.md`: `lint-shell.yml` and `lint-github-actions.yml` install a pinned, checksum-verified ShellCheck 0.11.0 instead of using the runner image's 0.9.0. A first run can report findings from checks added in 0.10.0 and 0.11.0, SC2327 to SC2332 among them. Both workflows now depend on the `job.workflow_repository` and `job.workflow_sha` context properties, which GitHub Enterprise Server does not populate.
- `set-up-ci/skills/set-up-ci/references/ci-zig.md` and `scaffold-zig-cli/skills/scaffold-zig-cli/references/ci-workflow.md`: `run-zig-ci.yml` now format-checks `build.zig.zon` alongside `build.zig` and `src`, so an unformatted or missing manifest fails the default formatting job. Run `zig fmt build.zig.zon`, or set `fmt-paths`.

### 3. Fold in the two findings from #383

Verified against the v4.1.0 workflow listing before planning.

- **`lint-go.yml` does not exist.** `pin-everything/skills/pin-everything/references/github-actions.md` uses it at lines 63 and 76. The real Go workflow is `run-go-ci.yml`. Pairing a real repository with a fictional workflow name in a skill about pinning is the kind of thing a reader copies. Rename both occurrences, and the `commits/v3.0.0` lookup between them, keeping the placeholder SHA and the unpinned-then-pinned structure intact. That structure is the lesson: line 63 is deliberately a bare tag because it is the "before" half.
- **Seven bare `@v3.0.0` tags in prose.** Six in `lint-and-fix/skills/lint-and-fix/SKILL.md` at lines 97 and 367, one in `pin-everything`'s line 63. Bump the version string to `v4.1.0` and keep the bare, unpinned form: in `lint-and-fix` these illustrate the shape of a reusable-workflow call the skill should skip, and in `pin-everything` the bare tag is the unpinned starting state. After this, no `v3.0.0` string remains anywhere under `plugins/`.

### 4. Bump this repository's own CI

`.github/workflows/ci.yml` carries four refs: `set-up-shellcheck`, `set-up-shfmt` and `set-up-actionlint` at `0d53592f40b487f01b26b374e539c517fa9c570f # v3.2.0`, and `run-scrut-tests.yml` at `17f94b08428565213e70ae19c37a7be894a172d2 # v3.1.1`. Move all four to v4.1.0.

The risk here is shfmt, whose default moves from 3.13.1 to 3.14.1 and could reformat tracked scripts. This was checked before planning rather than after: the local toolchain is already shfmt 3.14.1 and ShellCheck 0.11.0, exactly what v4.1.0 pins, and `make lint-shell` exits 0 against all 30 tracked scripts. The bump is therefore verifiable locally and expected to be inert.

`run-scrut-tests.yml` receives only `scrut-env` and `scrut-test-dir`, neither of which is an affected input. v4's scrut change builds from source on Linux arm64 and macOS x86-64; this job runs on ubuntu-latest amd64, so it is unaffected.

### 5. Patch version bumps

Each touched plugin's `.claude-plugin/plugin.json` is its sole version source, and a pin refresh with wording notes is a patch change. None of these plugins has a `.codex-plugin/plugin.json`, and `.claude-plugin/marketplace.json` carries no version field, so no catalog edit is needed.

| Plugin                    | From  | To    |
| ------------------------- | ----- | ----- |
| `add-goreleaser-homebrew` | 2.3.6 | 2.3.7 |
| `add-scrut-cli-tests`     | 1.6.6 | 1.6.7 |
| `lint-and-fix`            | 1.4.0 | 1.4.1 |
| `manage-repo-licensing`   | 1.0.6 | 1.0.7 |
| `pin-everything`          | 1.2.1 | 1.2.2 |
| `scaffold-go-cli`         | 2.8.3 | 2.8.4 |
| `scaffold-go-library`     | 1.8.6 | 1.8.7 |
| `scaffold-rust-cli`       | 1.2.6 | 1.2.7 |
| `scaffold-zig-cli`        | 1.0.1 | 1.0.2 |
| `set-up-ci`               | 2.1.1 | 2.1.2 |
| `set-up-installers`       | 3.1.2 | 3.1.3 |
| `set-up-linters`          | 2.2.2 | 2.2.3 |
| `set-up-secret-scanning`  | 3.0.3 | 3.0.4 |

### 6. Regenerate the mirrors

`make build` runs `bin/build-review-checklists`, `bin/build-codex-marketplace` and `bin/build-opencode-mirror`. Only `dist/codex` mirrors these references, in 23 files. Commit `plugins/` and `dist/` together so CI's generated-mirror drift check stays green.

## Out of scope

- **Replacing literal SHAs with placeholder tokens.** `scaffold-lean-library` already uses `CBOONE-GH-ACTIONS-SHA`, which cannot rot, and unifying every template on that pattern would end this class of drift. It also stops the templates being valid copy-pasteable YAML, removes the pins from `bin/version-audit`'s view, and diverges from the roughly 60 third-party SHA pins in the same files. Worth its own issue, not this one.
- **Extending `bin/version-audit`.** Line 127 already greps `plugins/` for `uses: …@<40 hex>`, and #419 proves it fires on these pins. Nothing to change.

## Verification

Run from the worktree root, in order.

```bash
# 1. No stale refs anywhere in the canonical tree or the mirrors.
grep -rn '91f9abd25d4f82354c0f950dfc8b6d7525b0f5b5\|17f94b08428565213e70ae19c37a7be894a172d2' plugins/ dist/ .github/
grep -rn 'v3\.0\.0\|lint-go\.yml' plugins/

# 2. Exactly one gh-actions version remains, plus the deliberate placeholder.
grep -rhoE 'cboone/gh-actions[^@ `")]*@[A-Za-z0-9.-]+( # v[0-9.]+)?' plugins/ | sort | uniq -c

# 3. The canonical tree and the mirror agree.
diff <(grep -rhoE 'cboone/gh-actions/[^@ `")]+@[A-Za-z0-9._-]+' plugins/ | sort) \
     <(grep -rhoE 'cboone/gh-actions/[^@ `")]+@[A-Za-z0-9._-]+' dist/ | sort)

# 4. The pinned SHA really is v4.1.0.
gh api repos/cboone/gh-actions/commits/v4.1.0 --jq '.sha'

# 5. Mirrors regenerate to exactly what is committed.
make build && git status --porcelain dist/ .agents/

# 6. Full gate.
make test-all
```

Steps 1 and 2 are the substantive checks: step 1 should print nothing, and step 2 should show only `@bbe15187a1a8c60caded9295d1d2d90338a0bb93 # v4.1.0`, the `@v4.1.0` bare tags, the `1234567890abcdef…` placeholder and the `CBOONE-GH-ACTIONS-SHA` token.

Then run the repository's `check-versions` skill to confirm every touched plugin was bumped and nothing untouched was.

`make test-all` covers markdownlint, Prettier, ShellCheck, shfmt, actionlint, the JSON and manifest validators, the generated-mirror drift check and scrut. Prettier formats `docs/plans/todo/` and `plugins/**/*.md` with `embeddedLanguageFormatting: "off"`, so the YAML inside fenced blocks is not reformatted. Observe the final result rather than reporting from a partial run.

CI itself is the last check on Change 4, since the v4 composite actions only run there. The local `make lint-shell` pass against the same tool versions is the evidence that it should be inert.

## Follow-up

Close #383 as superseded once this merges, with a comment recording that the refs went to v4.1.0 rather than v3.1.0, that both of its extra findings were folded in here, and that its 39-ref core is subsumed. Confirm the comment text before posting.
