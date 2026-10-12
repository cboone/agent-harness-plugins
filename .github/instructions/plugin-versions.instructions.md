---
applyTo: "plugins/*/.claude-plugin/plugin.json,plugins/*/.codex-plugin/plugin.json"
---

# Plugin Version Review

- A plugin needs a version bump when any file under `plugins/<name>/` changes, references and READMEs included. Check the whole plugin directory against the base branch before calling a bump unrelated; a one-line reference edit justifies a patch bump.
- Renaming a plugin's skill changes how users invoke it, for example `/monitor-pr` becoming `/monitor-pr:monitor`, so it is a breaking change and takes a major bump even when the plugin also gains a skill.
