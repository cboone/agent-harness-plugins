# Conventional Commits Parsing

Rules for parsing [Conventional Commits](https://www.conventionalcommits.org/) and determining the version bump level.

## Commit Pattern

```text
^(\w+)(\(.+\))?(!)?:\s(.+)$
```

Components:

- **Type**: `feat`, `fix`, `chore`, `docs`, `refactor`, `perf`, `test`, `style`, `ci`, `build`, `revert`
- **Scope** (optional): parenthesized context, e.g., `feat(auth):`
- **Breaking indicator** (optional): `!` suffix on the type, e.g., `feat!:`
- **Description**: the rest of the first line

## Breaking Change Detection

A commit is a breaking change if either:

- The type has a `!` suffix (e.g., `feat!: remove legacy API`)
- The commit body or footer contains `BREAKING CHANGE:` or `BREAKING-CHANGE:` (note: requires reading the full commit message, not just the subject)

## Bump Classification

| Condition                                                                                              | Bump level |
| ------------------------------------------------------------------------------------------------------ | ---------- |
| Any breaking change                                                                                    | Major      |
| `feat` type                                                                                            | Minor      |
| Everything else (`fix`, `chore`, `docs`, `refactor`, `perf`, `test`, `style`, `ci`, `build`, `revert`) | Patch      |

The overall bump is the highest individual level found across all commits since the last release. Priority: major > minor > patch.

## Type-to-Changelog Mapping

Map commit types to Keep a Changelog categories:

| Commit type | Changelog category |
| ----------- | ------------------ |
| `feat`      | Added              |
| `fix`       | Fixed              |
| `refactor`  | Changed            |
| `perf`      | Changed            |
| `revert`    | Removed            |
| `docs`      | Changed            |
| `style`     | Changed            |
| `chore`     | Changed            |
| `ci`        | Changed            |
| `build`     | Changed            |
| `test`      | Changed            |

Breaking changes get a `**BREAKING:**` prefix in their changelog entry regardless of their type, and appear first in their respective category.

## Non-Conventional Commits

Commits that do not match the conventional commits pattern:

- Classify as **patch** level for bump calculation
- Place under the **Changed** category in the changelog
- Use the full commit subject as the entry text

## Merge Commits

Exclude merge commits from analysis. Use `--no-merges` when running `git log`.

## Commit Analysis Command

To get the commit list for analysis:

<!-- prettier-ignore -->
```bash
git log <LAST-TAG>..HEAD --format='%H %s' --no-merges
```

For commits with bodies (needed for `BREAKING CHANGE:` footer detection):

<!-- prettier-ignore -->
```bash
git log <LAST-TAG>..HEAD --format='%H%n%s%n%b%n---END---' --no-merges
```

## Presenting the Summary

Group commits by their changelog category and present them to the user:

```text
Commits since vX.Y.Z (N total):

  Added (M):
    - feat: description (#PR)
    - feat(scope): description

  Fixed (N):
    - fix: description

  Changed (P):
    - refactor: description

Recommended bump: minor (vX.Y.Z -> vX.Y+1.0)
```
