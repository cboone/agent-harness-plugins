# Version-Audit Script

How to install and tailor the bundled `version-audit-template` script. Covers the surfaces Dependabot does not touch.

## Surfaces Audited

The script audits the four surfaces Dependabot misses:

1. **`.tool-versions`** — Node.js LTS drift (and other languages with similar version-file conventions).
2. **`packageManager`** — Yarn release drift (Corepack stays at the pinned version until the file is bumped).
3. **Action SHAs in `.md` templates** — third-party action refs embedded in skill template documentation.
4. **Install-command pins inside scripts** — `go install`, `cargo install`, `pip install`, `npx` pins in shell scripts, Makefiles, and skill prose.

Each surface has an upstream-of-record API the script queries. If the script finds a pinned version older than the upstream's current latest, it records a row in the drift report.

## Per-Surface Upstream APIs

| Surface         | Upstream                                  |
| --------------- | ----------------------------------------- |
| Node.js LTS     | `https://nodejs.org/dist/index.json`      |
| Yarn stable     | `https://repo.yarnpkg.com/tags`           |
| GitHub releases | `gh api repos/<r>/releases/latest`        |
| crates.io       | `https://crates.io/api/v1/crates/<crate>` |
| PyPI            | `https://pypi.org/pypi/<pkg>/json`        |
| npm registry    | `https://registry.npmjs.org/<pkg>/latest` |

Each surface's jq filter (extracted from `./scripts/version-audit-template`):

```text
Node.js LTS      first(.[] | select(.lts != false)) | .version    (then strip leading "v")
Yarn stable      .latest.stable
GitHub releases  .tag_name
crates.io        .crate.max_stable_version
PyPI             .info.version
npm registry     .version
```

The script wraps each query in error-tolerant boilerplate (`curl -fsSL ... 2>/dev/null || true`); a transient network failure produces no row, not a script failure.

## Issue-Management Workflow

The companion GitHub Actions workflow (`version-audit.yml`) runs the script weekly and manages exactly one labeled issue per repo:

- If the script's stdout is non-empty (drift detected), the workflow opens an issue titled "Version audit: drift detected" with the labeled list of drifted surfaces. If an issue with that label already exists, it updates the existing issue's body in place.
- If stdout is empty (no drift), and an issue with that label is open, the workflow closes it with a "drift cleared" comment.

The single-issue invariant prevents the audit from spamming the issue tracker. Reviewers see exactly one issue at a time, with the current state of every surface in its body.

## Tailoring the Template

Read `./scripts/version-audit-template`. It contains seven `audit_*` functions plus a `print_report` driver. Tailor before writing the user's `bin/version-audit`:

1. **Drop unused surface functions.** If the target repo has no `pip install` pins, delete `audit_pip_install_pins` and remove its call from the bottom of the script. Similarly drop `audit_npx_pins` if there are no `npx` pins, etc.
2. **Adjust grep paths.** The template greps `plugins/` and `.github/` because that's where the canonical example repo keeps its surfaces. For a different layout, change the path arguments to `grep -rh ... <paths>`.
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
  latest=$(curl -fsSL https://api.github.com/repos/oven-sh/bun/releases/latest \
    | jq -r '.tag_name' \
    | sed 's/^bun-v//')
  if [[ -n "${latest}" && "${current}" != "${latest}" ]]; then
    record_drift "Bun" "bun runtime" "${current}" "${latest}" "bun.lock"
  fi
}
```

Then add `audit_bun` to the call list at the bottom of the script. The `record_drift` helper handles the row formatting.

## Operational Notes

- The script requires `gh` (authenticated), `jq`, and `curl`. CI runners on `ubuntu-latest` have all three preinstalled. Locally, install via `brew install gh jq curl`.
- The script reads no secrets and writes no files; it's safe to run from any working directory in the repo.
- Empty stdout is the success signal. If the script errors out (a syntax error, a missing tool), the workflow's `Run audit` step fails before the issue-management steps run.

## Verifying Locally

Before committing the tailored script:

```bash
shellcheck -S warning bin/version-audit
shfmt -d bin/version-audit
bash bin/version-audit
```

The first two should produce no output. The third should produce the drift report (or no output if everything is current).
