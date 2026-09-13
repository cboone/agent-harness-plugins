# Checklist

Every check the review runs against the default-branch `dependabot.yml`, grouped by area. Each gives the default severity, what to look at, and the fix. Raise or lower a severity when the repository's own policy says so, and record why.

Dependabot's options change. Where a check depends on current GitHub behavior, confirm it against the [Dependabot options reference](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference) before reporting it, and cite what the documentation says.

## Coverage

| Check                                                   | Severity | Look at                                                                                                                                 | Fix                                                                                         |
| ------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| An ecosystem present has no entry                       | Error    | The inventory against `updates[].package-ecosystem`, using `./ecosystems.md`                                                            | Add an entry for it                                                                         |
| A manifest directory is not covered                     | Error    | Directories with manifests against each entry's `directory` or `directories` (globs such as `/apps/*` count as covering their matches)  | Switch to `directories` and add it, or a glob that matches it                               |
| A composite action with external `uses:` is not covered | Error    | `action.yml` files outside `.github/workflows/` that reference other actions, against the `github-actions` entry                        | Add its directory to the `github-actions` entry's `directories`                             |
| An entry has nothing to update                          | Warning  | Entries whose directory holds no manifest for that ecosystem, such as `pip` after a move to `uv`, or `github-actions` with no workflows | Remove the entry, or replace it with the ecosystem now in use                               |
| An entry covers a directory another repository manages  | Warning  | Subtrees and vendored copies                                                                                                            | Remove the directory. For version updates, `exclude-paths` also works (see Update behavior) |
| A separate install tree is folded into a workspace root | Warning  | Nested lockfiles next to a workspace root                                                                                               | List the nested directory on its own                                                        |

## Validity

| Check                                                            | Severity | Look at                                                                                          | Fix                                                                                          |
| ---------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| The file does not parse                                          | Error    | The YAML parser's line and column                                                                | Fix the syntax before reviewing anything else                                                |
| Schema errors                                                    | Error    | `uvx check-jsonschema --builtin-schema vendor.dependabot .github/dependabot.yml`                 | Fix the reported path, after confirming it is not schema lag on a documented option          |
| `version` is not `2`                                             | Error    | The top-level `version` key                                                                      | Set `version: 2`                                                                             |
| `directory` and `directories` in one entry                       | Error    | Each entry                                                                                       | Keep one. Only `directories` accepts globs                                                   |
| Two entries for the same ecosystem, directory, and target branch | Error    | Entries sharing all three                                                                        | Merge them into one entry                                                                    |
| `reviewers` is set                                               | Warning  | Each entry. GitHub removed the option from `dependabot.yml` in 2025 in favor of code owners      | Remove it, and add the reviewers to `.github/CODEOWNERS` for the manifest and lockfile paths |
| A label does not exist                                           | Warning  | Each entry's `labels` against `gh label list`; Dependabot comments on each PR it could not label | Create the label, or remove it from the config                                               |
| A milestone does not exist                                       | Warning  | Each entry's `milestone` against `gh api repos/OWNER/REPO/milestones`                            | Correct the number, or remove it                                                             |
| `target-branch` names a branch that does not exist               | Error    | `gh api repos/OWNER/REPO/branches/BRANCH`                                                        | Correct or remove it                                                                         |
| A `registries` entry references a missing secret                 | Error    | `${{secrets.NAME}}` in `registries` against the Dependabot secrets list                          | The user adds the Dependabot secret                                                          |

## Grouping and volume

| Check                                        | Severity   | Look at                                                                                                                    | Fix                                                                                                                  |
| -------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| No groups in an ecosystem with many open PRs | Suggestion | Open Dependabot PR count per ecosystem                                                                                     | Add `ECOSYSTEM-minor-patch` and `ECOSYSTEM-major` groups, the house baseline `pin-everything` writes                 |
| One catch-all group that includes majors     | Suggestion | Groups with `patterns: ["*"]` and no `update-types`                                                                        | Split by `update-types`, so a breaking major does not hold back every patch                                          |
| Group patterns overlap                       | Warning    | Two groups whose `patterns` match the same dependency. A dependency joins the first group that matches                     | Narrow the patterns, or reorder the groups so the intended one comes first                                           |
| `open-pull-requests-limit: 0`                | Warning    | Entries with a zero limit. That disables version updates for the entry; security updates are not subject to the limit      | Confirm it is intended, and say so in a comment. Otherwise remove it                                                 |
| A limit too low for SHA-pinned actions       | Suggestion | `github-actions` entries with a limit at or below the default of 5 in a repository that pins actions to SHAs               | Raise it, or group the updates                                                                                       |
| Inconsistent schedules                       | Suggestion | `schedule.interval`, `day`, `time`, and `timezone` across entries                                                          | Align them, so update PRs arrive together                                                                            |
| No `cooldown` beyond the default             | Suggestion | Version updates already wait 3 days after a release by default. A longer cooldown trades freshness for supply-chain safety | Consider `cooldown.default-days`, with `semver-major-days` longer than patch. Cooldown never delays security updates |
| Update volume against CI cost                | Suggestion | Daily schedules, ungrouped ecosystems, and heavy workflows running on every Dependabot PR                                  | Weekly schedules and groups; for the workflows, the `optimize-runner-usage` skill                                    |

## Update behavior

| Check                                                    | Severity   | Look at                                                                                                                                                                                    | Fix                                                                                           |
| -------------------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| `versioning-strategy` widens exact pins                  | Warning    | An application that pins exact versions in `package.json` without `versioning-strategy: increase`                                                                                          | Add `versioning-strategy: increase`                                                           |
| `versioning-strategy` narrows a library's ranges         | Warning    | A published library with `increase`, which forces consumers onto the newest minimum                                                                                                        | Use the ecosystem default, or `widen` where supported                                         |
| Commit messages do not match the repository's convention | Warning    | `commit-message.prefix` and `include` against recent commit subjects, any commitlint config, and any PR-title check workflow. With no prefix, titles read `Bump ...` or `build(deps): ...` | Set `prefix` (and `include: scope` for `chore(deps):`) to match                               |
| A PR-title check fails every Dependabot PR               | Error      | A workflow that validates PR titles, against recent Dependabot PR titles                                                                                                                   | Align `commit-message`, or exempt `dependabot[bot]` in the check                              |
| Stale `ignore` rules                                     | Warning    | `ignore[].dependency-name` entries that match nothing in the manifests any more                                                                                                            | Remove them                                                                                   |
| Broad `ignore` rules                                     | Warning    | `dependency-name: "*"`, or `update-types` that ignore all majors, without a comment explaining the policy                                                                                  | Narrow them, or document the intent in a comment                                              |
| `exclude-paths` expected to stop security updates        | Warning    | Excluded paths that still receive security update PRs. `exclude-paths` applies to version updates only                                                                                     | Explain the limit, and address the vulnerable dependency, or dismiss the alerts with a reason |
| `rebase-strategy: disabled`                              | Suggestion | Entries that disable rebasing, which leaves conflicted PRs for a person to refresh                                                                                                         | Confirm it is intended                                                                        |
| `insecure-external-code-execution: allow`                | Warning    | Entries that let Dependabot run code from manifests                                                                                                                                        | Remove it unless the build genuinely needs it, and record why                                 |

## Untracked surfaces

These are not config defects. They are version pins Dependabot cannot see, reported so nobody assumes they are covered:

- `.tool-versions`, `.nvmrc`, `.node-version`, `.python-version`, `.ruby-version`, `rust-toolchain.toml` (runtime pins outside a supported manifest)
- `packageManager` in `package.json`
- tool versions set in workflow `env:` or action inputs, such as a linter version passed to a setup action
- install commands with a version in scripts, Dockerfiles, and docs
- action references inside Markdown templates
- checksums pinned beside a download

The `pin-everything` skill's version-audit step generates a script and workflow that watch these. The `upgrade-everything` skill checks them on demand.
