# Plugin source instructions

Read [plugin development](../docs/plugin-development.md) before changing a plugin. Paths in that guide are relative to the repository root.

- Each plugin has `.claude-plugin/plugin.json`, a README, and a skill, command or hook entry point. Canonical metadata lives in `../.claude-plugin/marketplace.json`; update registration and descriptions together. Each Claude manifest is its sole version source. When a plugin also has `.codex-plugin/plugin.json`, mirror the version there because validation requires both manifests to agree.
- Bundled helpers belong to the plugin that invokes them. Use `${CLAUDE_PLUGIN_ROOT}/scripts/NAME`, not version-blind locator globs. Script references must resolve to shipped executable files.
- The `review-scope` copies in `review-until-clean/scripts/` and `review-pr-with-codex/scripts/` must stay byte-identical. Update both copies and their scrut coverage together.
- Cross-harness hooks need compatible manifests and entry points. Follow `notify/` for separate Claude and Codex surfaces; unsupported Codex events invalidate its entire hook manifest.
- Reference files and skill names are checked by `../bin/check-cross-references`. The guide describes repository-path declarations and file-scoped exemptions; an unused exemption also fails validation.
- Add bundled-script coverage to `../tests/scrut/` and register needed paths in both the Makefile's `SCRUT_ENV` and CI's `scrut-env` list.
- A style guide's `references/review-checklist.md` follows the review checklist format in the plugin development guide. `make build` copies it into `set-up-review-config`, so a checklist change needs forward version bumps in both plugins.
- `publish-report-board`'s `references/progress-model.md` is copied into `suggest-next-issue` by `make build`, so a change to it needs forward version bumps in both plugins. Never edit the copy. Both gather scripts apply the model from `publish-report-board/scripts/progress.jq`; change a rule there and in the model together.
- `review-anti-patterns`'s `references/codex-exec.md` is copied into `trim-comments` and `trim-text` by `make build`, so a change to it needs forward version bumps in all three plugins. Never edit the copies.
- Rebuild the Codex mirror with `make build` and run relevant validation after source changes. Never edit generated mirrors directly.
