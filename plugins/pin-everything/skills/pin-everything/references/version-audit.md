# Version-Audit Script

How to install and tailor the bundled `version-audit-template` script. Covers the surfaces Dependabot does not touch.

## Surfaces Audited

The script audits the surfaces Dependabot does not cover:

1. **Language runtime version files**: drift in whichever version file the repo uses for each language pinned by skill step 4. Six languages are covered:
   - **Node.js** in `.tool-versions` (with a `nodejs` line), `.nvmrc`, or `.node-version`. Drift is checked within the **same major series** so repos intentionally pinning a Current (odd-numbered, non-LTS) major like Node 23 are not told to "downgrade" to the latest LTS major every cycle.
   - **Ruby** in `.tool-versions` (with a `ruby` line), `.ruby-version`, or a `Gemfile` `ruby 'X.Y.Z'` directive — matching the priority order step 4 uses to wire `ruby/setup-ruby`. Constraint forms (`ruby '~> 3.4'`, `ruby '>= 3.4'`) and engine delegations (`ruby file: '.ruby-version'`) are silently skipped because they're either not pins or are handled by the prior file in priority order. Drift is checked within the same X.Y feature-release series (Ruby's release boundary is at the minor — 3.4.x is one line, 3.5.x the next). Tags in `ruby/ruby` use underscores (`v3_4_2`); the audit normalizes them to dots before comparing. Pre-releases are filtered out so a freshly-cut `v3.5.0-preview1` is not reported as drift against a stable `v3.4.2` pin.
   - **Python** in `.python-version`. Drift is checked within the same X.Y series, mirroring Ruby. `pyproject.toml`'s `requires-python` is intentionally **not** audited — it uses `>=` semantics, so it's a floor, not a pin.
   - **Go** in `go.mod`'s `go X.Y.Z` directive. The `go X.Y` form (no patch) is a module-spec floor — `actions/setup-go` resolves it to the highest patch in the X.Y line at install time — so the audit silently skips it. Drift is checked within the same X.Y release line, matching Ruby and Python.
   - **Rust** in `rust-toolchain.toml`'s `channel = "X.Y.Z"`. Moving channels (`stable`, `beta`, `nightly`) are silently skipped because they have no fixed upstream to compare against. Drift is checked against absolute latest stable; Rust does not maintain parallel patch lines the way Ruby and Python do.
   - **Zig** in `build.zig.zon`'s `.minimum_zig_version = "X.Y.Z"`. Although the field's name reads "minimum", `mlugg/setup-zig` (the action step 4 wires up) installs exactly that value, so it functions as a pin for CI. Dev-snapshot pins (`0.X.Y-dev.NNNN+abcdef`) are silently skipped — they track master rather than a release line. Drift is checked against absolute latest tagged release.

   Non-numeric values (`.nvmrc` aliases like `lts/*`, `node`, `latest`; major-only pins like `22` or `3.4`) are silently skipped — they're not pins, so there's nothing to compare against.

2. **`packageManager`**: Yarn or pnpm release drift (Corepack stays at the pinned version until the field is bumped). Both the version and the `+sha512.<hash>` integrity suffix are audited: a bare `<mgr>@<X.Y.Z>` (no integrity hash) defeats the Corepack tarball-pinning contract from skill step 5 and is itself reported as drift even when the version is current. The integrity-hash row takes precedence over the version-drift row when both apply, since regenerating the pin closes both at once. npm has no equivalent integrity surface, so npm-managed projects produce no row here.
3. **Action SHAs in scanned files**: third-party action refs found anywhere in the configured `SCAN_PATHS` (defaults: `.github/` and `plugins/`, which together cover both real workflows and the action refs embedded in skill templates and other Markdown). Only release-tagged refs (those whose comment is a numeric `# vX.Y.Z` tag) are audited; channel/branch pins like `# stable` or `# main` are intentionally out of scope, since they have no upstream "latest version" to compare against and would require a different "pinned SHA vs. branch HEAD" check. Drift is checked **within the same major series** as the pinned version, matching the held-major pattern documented in `references/github-actions.md`. A `# v2.3.4, held at v2 pending v3 migration` pin is flagged when a newer v2.x lands but never told to "upgrade" to v3, so the audit doesn't emit a permanent false-positive row for the held-major lifetime. Major bumps are a separate concern (Dependabot already proposes them for workflow files); the audit's role is the same-major patch backstop for SHA pins inside scanned Markdown templates and other surfaces Dependabot does not see.
4. **Install-command pins inside scripts**: `go install`, `cargo install`, every Python install verb (`pip install`, `uv pip install`, `uv add`, `uv tool install`, `uvx`), and `npx` pins in shell scripts, Makefiles, and skill prose. The single `audit_python_install_pins` function covers all five Python verbs with one regex. For `go install`, `github.com/<owner>/<repo>[/...]` paths are auto-derived (the upstream-of-record is the GitHub repo named by the first two path segments); vanity domains like `golang.org/x/...` and `mvdan.cc/...` redirect to repos whose names do not match the import path, so they require an explicit entry in the `vanity_path_to_repo` map inside `audit_go_install_pins`. Unmapped vanity paths are skipped silently; extending that map for the consuming repo's vanity-domain Go tools is a required tailoring step.

Each surface has an upstream-of-record API the script queries. If the script finds a pinned version older than the upstream's current latest within the relevant series, it records a row in the drift report.

## Per-Surface Upstream APIs

| Surface              | Upstream                                                                                                                                                                                                                                                                                                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Node.js (same major) | `https://nodejs.org/dist/index.json`                                                                                                                                                                                                                                                                                                                                 |
| Ruby (same X.Y)      | `gh api repos/ruby/ruby/releases` (paginated, `select(.prerelease == false)`); tag names are normalized from `v3_4_2` → `3.4.2`                                                                                                                                                                                                                                      |
| Python (same X.Y)    | `gh api repos/python/cpython/releases` (paginated, `select(.prerelease == false)`)                                                                                                                                                                                                                                                                                   |
| Go (same X.Y)        | `gh api repos/golang/go/tags` (paginated); tag names are normalized from `go1.23.5` → `1.23.5`                                                                                                                                                                                                                                                                       |
| Rust stable          | `gh api repos/rust-lang/rust/releases` (`.[0].tag_name`)                                                                                                                                                                                                                                                                                                             |
| Zig stable           | `gh api repos/ziglang/zig/releases` (`.[0].tag_name`)                                                                                                                                                                                                                                                                                                                |
| Yarn stable          | `https://repo.yarnpkg.com/tags`                                                                                                                                                                                                                                                                                                                                      |
| pnpm stable          | `https://registry.npmjs.org/pnpm/latest`                                                                                                                                                                                                                                                                                                                             |
| GitHub releases      | `gh api repos/<r>/releases/latest`, with `gh api repos/<r>/tags` (highest semver entry) as a fallback for repos that publish version tags without GitHub Releases                                                                                                                                                                                                    |
| GitHub same-major    | `gh api repos/<r>/releases` (paginated, filtered to the major and sorted by version), with `gh api repos/<r>/tags` (same filter+sort) as a fallback. Used by `audit_actions` so pinned `# vN.x.y` comments are compared only within the same vN.* line, which avoids false-positive drift rows for held-major pins like `# v2.3.4, held at v2 pending v3 migration`. |
| crates.io            | `https://crates.io/api/v1/crates/<crate>`                                                                                                                                                                                                                                                                                                                            |
| PyPI                 | `https://pypi.org/pypi/<pkg>/json`                                                                                                                                                                                                                                                                                                                                   |
| npm registry         | `https://registry.npmjs.org/<pkg>/latest` (scoped packages require the `/` between scope and name to be URL-encoded as `%2f`, e.g. `@taplo/cli` → `@taplo%2fcli`)                                                                                                                                                                                                    |

Each surface's jq filter (extracted from `./scripts/version-audit-template`):

```text
Node.js            first(.[] | select(.version | startswith($prefix))) | .version
                   with $prefix = "v<major>." derived from the current pinned version
                   (then strip leading "v")
Ruby               .[] | select(.prerelease == false) | .tag_name
                   then sed 's/^v//; s/_/./g' and grep ^<X.Y>\.[0-9]+$
                   then semver_max (jq-based, portable replacement for sort -V | tail -n 1)
Python             .[] | select(.prerelease == false) | .tag_name
                   then sed 's/^v//' and grep ^<X.Y>\.[0-9]+$
                   then semver_max
Go                 .[].name (tags, paginated) filtered to ^go<X.Y>\.[0-9]+$
                   then sed 's/^go//' and semver_max
Rust stable        .[0].tag_name (then strip leading "v")
Zig stable         .[0].tag_name
Yarn stable        .latest.stable
pnpm stable        .version
GitHub releases    .tag_name (releases/latest); .[].name filtered to ^v?[0-9]+(\.[0-9]+)+$ then semver_max (tags fallback)
GitHub same-major  .[] | select(.prerelease == false) | .tag_name (releases, paginated)
                   filtered to ^v?<major>(\.[0-9]+)+$ then semver_max
                   (tags fallback uses the same filter)
crates.io          .crate.max_stable_version
PyPI               .info.version
npm registry       .version
```

The `semver_max` helper is defined once near the top of the script and reused by every surface that needs to pick the highest version-aware match from a stream of release tags. It uses `jq` (already a hard dependency) instead of GNU `sort -V`, so the script runs on stock macOS BSD `sort` without an extra coreutils install.

The script wraps each query in error-tolerant boilerplate (`curl -fsSL ... 2>/dev/null || true`); a transient network failure produces no row, not a script failure.

## Issue-Management Workflow

The companion GitHub Actions workflow (`version-audit.yml`) runs the script weekly and manages exactly one labeled issue per repo:

- The "Find existing audit issue" step searches across **both open and closed** issues for the label+title pair. This is what preserves the single-issue invariant across drift→clear→drift cycles: if a previous cycle closed the issue when drift cleared, the next drift detection finds and reopens that same issue rather than stacking a new one alongside it.
- If the script's stdout is non-empty (drift detected), the workflow opens an issue titled "Version audit: drift detected" with the labeled list of drifted surfaces. If an existing issue with that label is found, the workflow updates its body in place; if that issue is currently closed, it is reopened first with a "drift detected again" comment.
- If stdout is empty (no drift) and the existing issue is currently open, the workflow closes it with a "drift cleared" comment. Already-closed issues are left alone.

The single-issue invariant prevents the audit from spamming the issue tracker. Reviewers see exactly one issue per repo (open during drift, closed when the surfaces are current again), with the current state of every surface in its body.

## Tailoring the Template

Read `./scripts/version-audit-template`. It contains twelve `audit_*` functions plus a `print_report` driver. Tailor before writing the user's `bin/version-audit`:

1. **Drop unused surface functions.** If the target repo has no Python install pins of any kind (no `pip install`, `uv pip install`, `uv add`, `uv tool install`, or `uvx` calls with `==`), delete `audit_python_install_pins` and remove its call from the bottom of the script. The function name covers all five Python install verbs together because they share an upstream (PyPI) and a single grep handles them all; deleting it on the basis of "no plain `pip install` pins" alone would drop drift coverage for the `uv`-only repos. Apply the same all-or-nothing rule to `audit_npx_pins`, `audit_go_install_pins`, and `audit_cargo_install_pins`. For runtime functions: drop `audit_node` if no Node version file is present (no `.tool-versions` with a `nodejs` line, no `.nvmrc`, no `.node-version`); drop `audit_ruby` if no Ruby version file is present (no `.tool-versions` with a `ruby` line, no `.ruby-version`, no `Gemfile` `ruby 'X.Y.Z'` directive); drop `audit_python_runtime` if no `.python-version` is present; drop `audit_go_runtime` if no `go.mod` is present; drop `audit_rust_runtime` if no `rust-toolchain.toml` is present; drop `audit_zig_runtime` if no `build.zig.zon` is present. The runtime functions self-skip when the file is missing or carries a non-pin form (constraint, alias, moving channel), so leaving them in for repos that don't currently use the language is harmless; dropping is purely a noise-reduction choice.
2. **Adjust grep paths.** The template greps `plugins/` and `.github/` because that's where the canonical example repo keeps its surfaces. For a different layout, change the path arguments to `grep -rH ... <paths>` (the `-H` flag preserves filenames so drift rows can report the actual file).
3. **Extend the vanity-domain map for `go install`.** `audit_go_install_pins` auto-derives `OWNER/REPO` for any `github.com/<owner>/<repo>[/...]` import path, so most consuming repos need no change there. But vanity domains (`golang.org/x/...`, `mvdan.cc/...`, `gotest.tools/...`, `sigs.k8s.io/...`, `oras.land/...`, etc.) redirect to repos whose names do not match the import path, so each one needs a manual entry in the `vanity_path_to_repo` associative array inside `go_install_path_to_repo`. Audit-time silence on a vanity-domain pin is a tailoring gap, not a feature — extend the map for every vanity-domain `go install` line in the consuming repo before writing `bin/version-audit`.
4. **Add new surface functions** if the target repo has surfaces the template doesn't cover (e.g. a custom version file format, a different language runtime).

Write the result to `bin/version-audit` and `chmod +x` it.

## Tailoring the Workflow

Read `./scripts/version-audit-workflow-template.yml`. The template is mostly substitution-free (the main repo-specific element is the `actions/checkout` SHA, which the skill should refresh per the "Refresh own SHAs" section). Confirm:

- The cron schedule (`0 12 * * 1`, weekly Monday at noon UTC) matches the team's preference.
- The `ISSUE_LABEL` (`version-audit`) doesn't collide with an existing label.
- The `permissions:` block has `issues: write` (required to open / edit / close issues).

Write the result to `.github/workflows/version-audit.yml`.

## Extending the Script

When new surfaces appear in the repo (e.g. the team adds a Bun-based subproject), add a corresponding `audit_*` function:

```bash
function audit_bun() {
  if [[ ! -f "bun.lock" ]]; then
    return
  fi
  local current latest
  current=$(jq -r '.bunVersion // empty' bun.lock)
  if [[ -z "${current}" ]]; then
    return
  fi
  latest=$(curl -fsSL https://api.github.com/repos/oven-sh/bun/releases/latest 2> /dev/null \
    | jq -r '.tag_name' \
    | sed 's/^bun-v//' || true)
  if [[ -n "${latest}" && "${current}" != "${latest}" ]]; then
    record_drift "Bun" "bun runtime" "${current}" "${latest}" "bun.lock"
  fi
}
```

For grep-based surface functions, follow the existing audit_* pattern: use `grep -rHE` so each match line is prefixed with its filename, then split with `file="${line%%:*}"; content="${line#*:}"` and pass `${file}` as the location argument to `record_drift`.

Then add `audit_bun` to the call list at the bottom of the script. The `record_drift` helper handles the row formatting.

## Operational Notes

- The script requires `gh` (authenticated), `jq`, `curl`, and **Bash 4+** (it uses associative arrays via `declare -A`). CI runners on `ubuntu-latest` have all four preinstalled. macOS ships `/bin/bash` 3.2, which fails on the first `declare -A`; install a newer Bash via `brew install bash gh jq curl` and invoke the script through its shebang (`./bin/version-audit`) so `/usr/bin/env bash` picks up the Homebrew-installed Bash from `PATH`. The script's first action is a Bash version check that exits cleanly with an actionable error if Bash 4+ is unavailable.
- The script reads no secrets and writes no files. It `cd`s to `git rev-parse --show-toplevel` on entry, so it's safe to invoke from any working directory inside the repo (it errors out cleanly if invoked outside a git checkout).
- Empty stdout is the success signal. If the script errors out (a syntax error, a missing tool), the workflow's `Run audit` step fails before the issue-management steps run.

## Verifying Locally

Before committing the tailored script:

```bash
shellcheck -S warning bin/version-audit
shfmt -d bin/version-audit
./bin/version-audit
```

The third command invokes the script via its shebang (`#!/usr/bin/env bash`), which picks up the Bash from `PATH` rather than forcing `/bin/bash`. This matters on macOS, where `/bin/bash` is 3.2 and lacks the associative-array support the script requires.

The first two should produce no output. The third should produce the drift report (or no output if everything is current).
