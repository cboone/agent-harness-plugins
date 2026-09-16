---
applyTo: ".claude-plugin/marketplace.json,.agents/plugins/marketplace.json,plugins/pr/**,dist/codex/plugins/pr/**"
---

# Catalog and PR Issue Review

- Claude plugin manifests are the sole version source. Verify each changed plugin has a forward SemVer bump, mirror that version into a Codex manifest when present, and ensure marketplace entries and metadata contain no `version` fields.
- A feature branch may increment a plugin's patch component while addressing review feedback after its minor capability bump. A forward version such as `1.9.3` over base `1.8.5` is valid; intervening versions do not need published releases. Do not request a version reduction solely because those releases are absent from the base branch.
- In the PR skill, a closing candidate means an identity matching the PR target after follow-up removal. Other connected identities are related issues and do not satisfy the closing-candidate condition. Evaluate the Strategy 3 fallback against the closing list.
- The PR skill defaults its target to the validated fetch repository. Parent traversal checks the fork network; it does not select or authorize an upstream PR destination. Respect explicit user repository and upstream-write instructions rather than requiring automatic fork-to-parent PR creation.
