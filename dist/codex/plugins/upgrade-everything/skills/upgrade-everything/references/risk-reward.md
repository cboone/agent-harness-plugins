# Risk and Reward

Use this model to make upgrade recommendations without hiding any candidate. Risk affects ordering, validation, and recommendation; it never removes a candidate from the plan.

## Reward Dimensions

| Dimension                | Higher reward when                                                                 |
| ------------------------ | ---------------------------------------------------------------------------------- |
| Security                 | The upgrade fixes a known vulnerability, unsafe default, or exposed CI dependency. |
| Bug fixes                | Release notes mention correctness, stability, or crash fixes relevant to the repo. |
| Compatibility            | The upgrade restores support for current platforms, package managers, or APIs.     |
| Template alignment       | The repo should match current project templates, workflows, or generated files.    |
| Stale transitive cleanup | The upgrade refreshes old transitive dependencies or lockfile resolution.          |
| Ecosystem support        | The current version is near end-of-support or unsupported by upstream tooling.     |
| Maintainer policy        | The repo's policy expects current minor or patch releases.                         |

## Risk Dimensions

| Dimension                   | Higher risk when                                                                               |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| SemVer major changes        | The upgrade crosses a major boundary or the ecosystem does not follow SemVer reliably.         |
| Runtime or toolchain jumps  | The upgrade changes compiler, interpreter, package manager, or build image behavior.           |
| Lockfile churn              | The upgrade changes many transitive dependencies or multiple ecosystem lockfiles.              |
| Deprecated packages         | The current or target package is deprecated, renamed, archived, or superseded.                 |
| Migration notes             | Upstream requires config changes, code changes, data migrations, or manual intervention.       |
| Changelog warnings          | Release notes mention breaking changes, removals, changed defaults, or security model changes. |
| Public library constraints  | Tightening a manifest range could constrain downstream users.                                  |
| CI blast radius             | The dependency is used across many jobs, publish paths, release automation, or templates.      |
| Repo-specific test coverage | The repo lacks tests or checks that exercise the upgraded dependency.                          |

## Ratings

| Rating  | Reward meaning                                                  | Risk meaning                                                          |
| ------- | --------------------------------------------------------------- | --------------------------------------------------------------------- |
| High    | Strong repo-specific benefit or security relevance.             | Requires migration review, broad validation, or explicit user choice. |
| Medium  | Clear maintenance value with limited direct feature impact.     | Behavior could change, but validation is available and bounded.       |
| Low     | Mostly currency, tidy-up, or alignment value.                   | Narrow impact, patch-level change, or strong automated validation.    |
| Unknown | Reward cannot be evaluated from available upstream information. | Risk cannot be evaluated from available upstream information.         |

## Recommendation Labels

| Label       | Meaning                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------ |
| Recommended | Reward is clear and risk is low or manageable with available validation.                   |
| Optional    | Upgrade is valid, but reward is mostly maintenance or repo policy alignment.               |
| Review      | Upgrade should be considered, but migration notes, major changes, or blast radius matter.  |
| Blocked     | Upstream data, ownership, package manager state, or validation prerequisites are missing.  |
| Hold        | The repo appears to have an intentional hold policy, but the candidate remains selectable. |

## Candidate Matrix Fields

| Field        | Required content                                                              |
| ------------ | ----------------------------------------------------------------------------- |
| `#`          | Stable candidate number used for user selection.                              |
| `Ecosystem`  | Package manager, runtime, CI, container, schema, marketplace, or other owner. |
| `Surface`    | File path and version surface, concise enough to scan.                        |
| `Current`    | Current version, tag, SHA, digest, range, channel, or unknown value.          |
| `Latest`     | Latest resolved upstream value, or `Unknown` / `Blocked`.                     |
| `Type`       | Patch, minor, major, digest, SHA, runtime, schema, channel, or unknown.       |
| `Reward`     | Rating plus the most important reason.                                        |
| `Risk`       | Rating plus the most important reason.                                        |
| `Confidence` | High, medium, low, or unknown based on upstream source quality.               |
| `Validation` | Commands or checks required before calling the upgrade complete.              |

## Validation Guidance

- Package dependencies: run the ecosystem's resolver, tests, and lockfile consistency checks.
- Runtime or toolchain upgrades: run build, test, lint, and any smoke tests that execute the produced artifact.
- GitHub Actions and reusable workflows: validate workflow syntax and run local checks that mirror the changed CI behavior where possible.
- Container images: rebuild affected images and run the repo's container smoke tests or entrypoint checks.
- Release tooling: run dry-run or config validation commands before claiming success.
- Schema URLs and config versions: run the tool that consumes the config.
- Marketplace and plugin versions: run manifest validation and recompute derived catalog metadata.
