---
applyTo: "plugins/*/skills/*/references/review-checklist.md,plugins/set-up-review-config/**,bin/build-review-checklists"
---

# Review Checklists

For repo-wide conventions, see [copilot-instructions.md](../copilot-instructions.md) and `AGENTS.md` at the repository root. The format is defined in the "Review checklists" section of `docs/plugin-development.md`.

- **Copies are generated**: `plugins/set-up-review-config/skills/set-up-review-config/references/checklists/` holds byte-identical copies of each style guide's `references/review-checklist.md`, written by `bin/build-review-checklists`. Review the source checklist, not the copy, and do not flag the duplication; rule 20 of `bin/validate-plugins` fails when they differ.
- **Checklists stand alone**: A checklist is installed into other repositories, so it has no relative links, no `./references/` paths and no tables or code fences. Do not suggest linking to the guide's own reference files; the installed copy links to the full guide separately.
- **Rules come from the guide**: Flag a checklist rule that the style guide beside it does not state or imply, and a changed guide rule whose checklist entry was left behind.
- **Rule names are citations**: Reviewers cite `<guide>: Rule name`, so a renamed bold rule name changes review comments downstream. Flag renames that look accidental.
- **Two version bumps**: A changed source checklist also changes `set-up-review-config`, so both plugins need a forward version bump.
- **Managed markers are exact strings**: `<!-- BEGIN set-up-review-config -->`, `<!-- END set-up-review-config -->` and the `<!-- Managed by set-up-review-config` prefix are matched literally by the skill, `refresh-project-scaffolding` and `clean-up-agent-config`. Flag any edit that changes one without the others.
