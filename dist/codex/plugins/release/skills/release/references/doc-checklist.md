# Documentation Checklist

Map commit types to documentation that may need manual review. Present relevant items as part of the pre-tag review gate (Step 8) so the user can evaluate documentation needs before approving the release commit and tag.

## Commit-Type-to-Documentation Mapping

| Change type        | Docs to review                                               |
| ------------------ | ------------------------------------------------------------ |
| Breaking changes   | Migration guide, upgrade instructions, API notes             |
| `feat:`            | README features section, API docs, usage examples, man pages |
| Removed features   | README, deprecation notices                                  |
| Dependency changes | Install instructions, compatibility matrix                   |
| Security fixes     | Security policy, advisories                                  |
| CLI changes        | README usage section, `--help` text in docs, man pages       |
| Config changes     | Config reference, example configs                            |
| `perf:`            | Benchmarks, performance docs                                 |

## Skip Conditions

Skip the checklist entirely if the release contains only these commit types:

- `chore:`
- `test:`
- `style:`
- `ci:`
- `build:`

These types rarely require documentation updates.

## Presentation

Present the checklist as a list of documentation areas to review, filtered to only the categories relevant to the commits in this release:

```text
Documentation review checklist:

- [ ] README features section (new feat: commits detected)
- [ ] API docs and usage examples (new feat: commits detected)
- [ ] Migration guide (breaking changes detected)
```

The user must explicitly approve before the release commit and tag are created.
