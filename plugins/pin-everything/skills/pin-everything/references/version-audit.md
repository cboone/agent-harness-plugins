# Version-Audit Script

How to install and tailor the bundled `version-audit-template` script. Covers the surfaces Dependabot does not touch.

## Surfaces Audited

The script audits the four surfaces Dependabot misses:

1. **Node.js LTS** — drift in whichever Node version file the repo uses (`.tool-versions` with a `nodejs` line, `.nvmrc`, or `.node-version`), mirroring the priority order in skill step 4.
2. **`packageManager`** — Yarn or pnpm release drift (Corepack stays at the pinned version until the field is bumped). npm has no equivalent integrity surface, so npm-managed projects produce no row here.
3. **Action SHAs in scanned files** — third-party action refs found anywhere in the configured `SCAN_PATHS` (defaults: `.github/` and `plugins/`, which together cover both real workflows and the action refs embedded in skill templates and other Markdown). Only release-tagged refs (those whose comment is a numeric `# vX.Y.Z` tag) are audited; channel/branch pins like `# stable` or `# main` are intentionally out of scope, since they have no upstream "latest version" to compare against and would require a different "pinned SHA vs. branch HEAD" check.
4. **Install-command pins inside scripts** — `go install`, `cargo install`, every Python install verb (`pip install`, `uv pip install`, `uv add`, `uv tool install`, `uvx`), and `npx` pins in shell scripts, Makefiles, and skill prose. The single `audit_python_install_pins` function covers all five Python verbs with one regex.

Each surface has an upstream-of-record API the script queries. If the script finds a pinned version older than the upstream's current latest, it records a row in the drift report.

## Per-Surface Upstream APIs

| Surface         | Upstream                                                                                                                                                          |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Node.js LTS     | `https://nodejs.org/dist/index.json`                                                                                                                              |
| Yarn stable     | `https://repo.yarnpkg.com/tags`                                                                                                                                   |
| pnpm stable     | `https://registry.npmjs.org/pnpm/latest`                                                                                                                          |
| GitHub releases | `gh api repos/<r>/releases/latest`, with `gh api repos/<r>/tags` (highest semver entry) as a fallback for repos that publish version tags without GitHub Releases |
| crates.io       | `https://crates.io/api/v1/crates/<crate>`                                                                                                                         |
| PyPI            | `https://pypi.org/pypi/<pkg>/json`                                                                                                                                |
| npm registry    | `https://registry.npmjs.org/<pkg>/latest` (scoped packages require the `/` between scope and name to be URL-encoded as `%2f`, e.g. `@taplo/cli` → `@taplo%2fcli`) |

Each surface's jq filter (extracted from `./scripts/version-audit-template`):

```text
Node.js LTS      first(.[] | select(.lts != false)) | .version    (then strip leading "v")
Yarn stable      .latest.stable
pnpm stable      .version
GitHub releases  .tag_name (releases/latest); .[].name filtered to ^v?[0-9]+(\.[0-9]+)+$ then sort -V (tags fallback)
crates.io        .crate.max_stable_version
PyPI             .info.version
npm registry     .version
```

The script wraps each query in error-tolerant boilerplate (`curl -fsSL ... 2>/dev/null || true`); a transient network failure produces no row, not a script failure.

## Issue-Management Workflow

The companion GitHub Actions workflow (`version-audit.yml`) runs the script weekly and manages exactly one labeled issue per repo:

- The "Find existing audit issue" step searches across **both open and closed** issues for the label+title pair. This is what preserves the single-issue invariant across drift→clear→drift cycles: if a previous cycle closed the issue when drift cleared, the next drift detection finds and reopens that same issue rather than stacking a new one alongside it.
- If the script's stdout is non-empty (drift detected), the workflow opens an issue titled "Version audit: drift detected" with the labeled list of drifted surfaces. If an existing issue with that label is found, the workflow updates its body in place; if that issue is currently closed, it is reopened first with a "drift detected again" comment.
- If stdout is empty (no drift) and the existing issue is currently open, the workflow closes it with a "drift cleared" comment. Already-closed issues are left alone.

The single-issue invariant prevents the audit from spamming the issue tracker. Reviewers see exactly one issue per repo (open during drift, closed when the surfaces are current again), with the current state of every surface in its body.

## Tailoring the Template

Read `./scripts/version-audit-template`. It contains seven `audit_*` functions plus a `print_report` driver. Tailor before writing the user's `bin/version-audit`:

1. **Drop unused surface functions.** If the target repo has no Python install pins of any kind (no `pip install`, `uv pip install`, `uv add`, `uv tool install`, or `uvx` calls with `==`), delete `audit_python_install_pins` and remove its call from the bottom of the script. The function name covers all five Python install verbs together because they share an upstream (PyPI) and a single grep handles them all; deleting it on the basis of "no plain `pip install` pins" alone would drop drift coverage for the `uv`-only repos. Apply the same all-or-nothing rule to `audit_npx_pins`, `audit_go_install_pins`, and `audit_cargo_install_pins`.
2. **Adjust grep paths.** The template greps `plugins/` and `.github/` because that's where the canonical example repo keeps its surfaces. For a different layout, change the path arguments to `grep -rH ... <paths>` (the `-H` flag preserves filenames so drift rows can report the actual file).
3. **Add new surface functions** if the target repo has surfaces the template doesn't cover (e.g. a custom version file format).

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
