---
applyTo: "plugins/publish-report-board/skills/publish-report-board/references/progress-model.md,plugins/suggest-next-issue/skills/suggest-next-issue/references/progress-model.md,bin/build-shared-references"
---

# Shared References

For repo-wide conventions, see [copilot-instructions.md](../copilot-instructions.md) and `AGENTS.md` at the repository root. The mechanism is described in the "Shared references" section of `docs/plugin-development.md`.

- **Copies are generated**: `plugins/suggest-next-issue/skills/suggest-next-issue/references/progress-model.md` is a byte-identical copy of `publish-report-board`'s `references/progress-model.md`, written by `bin/build-shared-references`. Review the source, not the copy, and do not flag the duplication; rule 22 of `bin/validate-plugins` fails when they differ.
- **The model serves two skills**: A rule in the source applies to both report boards and `suggest-next-issue`. Flag wording that only one consumer can follow, such as a board-only scheduling rule, which belongs in a board-type reference instead.
- **Two version bumps**: A changed source also changes `suggest-next-issue`, so both plugins need a forward version bump.
