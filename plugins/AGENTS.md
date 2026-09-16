# Plugin source instructions

Read [plugin development](../docs/plugin-development.md) before changing a plugin. Paths in that guide are relative to the repository root.

- Each plugin has `.claude-plugin/plugin.json`, a README, and a skill, command or hook entry point. Canonical metadata lives in `../.claude-plugin/marketplace.json`; update registration, version and descriptions together.
- Bundled helpers belong to the plugin that invokes them. Use `${CLAUDE_PLUGIN_ROOT}/scripts/NAME`, not version-blind locator globs. Script references must resolve to shipped executable files.
- The three helpers in `create-worktree/scripts/` and `address-issue-in-worktree/scripts/` must stay byte-identical. Update both copies and their scrut coverage together.
- Cross-harness hooks need compatible manifests and entry points. Follow `notify/` for separate Claude, Codex and OpenCode surfaces; unsupported Codex events invalidate its entire hook manifest.
- Reference files and skill names are checked by `../bin/check-cross-references`. The guide describes repository-path declarations and file-scoped exemptions; an unused exemption also fails validation.
- Add bundled-script coverage to `../tests/scrut/` and register needed paths in both the Makefile's `SCRUT_ENV` and CI's `scrut-env` list.
- Recompute catalog state, rebuild both mirrors and run relevant validation after source changes. Never edit generated mirrors directly.
