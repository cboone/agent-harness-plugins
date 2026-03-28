# Prohibit Floating Major Version Tags in Release Skill

Issue: #232

## Context

The `/release` skill's SKILL.md instructs the LLM to create only the exact version tag (`vVERSION`, e.g., `v2.2.0`). However, it never explicitly prohibits creating floating major tags (`v2`), a convention common in GitHub Actions repositories. Without an explicit prohibition, the LLM may add floating major tags during execution. The `gh-actions` repository has moved away from this pattern (cboone/gh-actions#26), and the skill should explicitly prevent it.

## Changes

### 1. `plugins/release/skills/release/SKILL.md`

**Step 10 (line 229-230):** After the `git tag` code block, before "After tagging, confirm:", add:

```markdown
Do NOT create floating major version tags (e.g., `v2`). Create only the exact version tag shown above.
```

**Step 11b (line 296-298):** After the `git push` code block, before "If the push is rejected", add:

```markdown
Do NOT push any floating major version tags (e.g., `v2`). Push only the exact version tag.
```

The manual command sections (shown when user declines to publish) do not need changes because those are commands the user runs manually, not commands the LLM executes.

### 2. Version bump (patch: 1.3.0 -> 1.3.1)

- `plugins/release/.claude-plugin/plugin.json` line 12
- `.claude-plugin/marketplace.json` line 304

The marketplace `metadata.version` does NOT change (no plugins added or removed).

## Verification

- Run `/check-versions` to confirm plugin.json and marketplace.json versions match
- Read the modified SKILL.md sections to verify correct placement
