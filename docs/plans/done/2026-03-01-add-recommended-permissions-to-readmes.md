# Add Recommended Permissions to Plugin READMEs

## Context

Plugin `settings.json` files can now ship with plugins, but currently only the `agent` key is supported. Permission rules (`allow`/`deny`/`ask`) in plugin `settings.json` are silently ignored. Since the broader `settings.json` schema does support `permissions.allow` with patterns like `Bash(npx eslint *)`, we can document the recommended permission rules in each plugin's README so users can add them to their own `.claude/settings.json`.

This gives users an immediately useful, copy-paste solution for eliminating permission prompts when using plugins that run Bash commands.

## Plugins to Update (10 total)

### Tier 1: High priority (frequent use, many Bash commands)

1. **lint-and-fix** (1.1.0): linters, formatters, git commit, git push
1. **commit** (1.2.0): git status, diff, log, add, commit, push
1. **pr** (1.3.1): git commands, gh pr create, mktemp, rm

### Tier 2: Medium priority (less frequent, targeted commands)

1. **merge-main** (1.1.1): git fetch, merge, commit, push, gh repo view
1. **release** (1.0.0): git tag, log, commit, date
1. **create-worktree** (1.0.6): launch-workmux script, git worktree list
1. **create-worktree-from-issue** (1.2.3): gh issue commands, launch-workmux script
1. **resolve-copilot-pr-feedback** (1.1.7): resolve-copilot-threads script, git push
1. **create-issue** (1.0.0): gh issue create, mktemp, rm
1. **suggest-next-issue** (1.1.1): gh issue list, gh label list, gh repo view

## Permission Rules Per Plugin

### lint-and-fix

```json
"Bash(npx eslint *)",
"Bash(npx prettier *)",
"Bash(npx markdownlint-cli2 *)",
"Bash(shellcheck *)",
"Bash(shfmt *)",
"Bash(npx knip*)",
"Bash(npm run lint*)",
"Bash(npm run format*)",
"Bash(npm run check*)",
"Bash(bin/lint*)",
"Bash(scripts/lint*)",
"Bash(script/lint*)",
"Bash(git status --porcelain)",
"Bash(git add *)",
"Bash(git commit *)",
"Bash(git push*)"
```

### commit

```json
"Bash(git status*)",
"Bash(git diff*)",
"Bash(git log *)",
"Bash(git add *)",
"Bash(git commit *)",
"Bash(git push*)",
"Bash(git branch *)",
"Bash(git mv *)"
```

### pr

```json
"Bash(git status*)",
"Bash(git diff*)",
"Bash(git log *)",
"Bash(git add *)",
"Bash(git commit *)",
"Bash(git push*)",
"Bash(git branch *)",
"Bash(git rev-parse *)",
"Bash(git remote *)",
"Bash(git mv *)",
"Bash(gh repo view *)",
"Bash(gh issue view *)",
"Bash(gh issue list *)",
"Bash(gh pr create *)",
"Bash(gh pr view *)",
"Bash(mktemp /tmp/pr-body-*)",
"Bash(rm -f /tmp/pr-body-*)"
```

### merge-main

```json
"Bash(git status*)",
"Bash(git branch *)",
"Bash(git fetch *)",
"Bash(git merge *)",
"Bash(git commit *)",
"Bash(git push*)",
"Bash(git stash*)",
"Bash(git log *)",
"Bash(git diff*)",
"Bash(git add *)",
"Bash(git remote *)",
"Bash(gh repo view *)"
```

### release

```json
"Bash(git status --porcelain)",
"Bash(git branch --show-current)",
"Bash(git tag *)",
"Bash(git log *)",
"Bash(git add *)",
"Bash(git commit *)",
"Bash(git remote get-url *)",
"Bash(date *)"
```

### create-worktree

```json
"Bash(bash */launch-workmux *)",
"Bash(git worktree list*)",
"Bash(rm -f /tmp/workmux-prompt-*)"
```

### create-worktree-from-issue

```json
"Bash(gh issue view *)",
"Bash(gh issue list *)",
"Bash(gh issue edit *)",
"Bash(gh label create *)",
"Bash(bash */launch-workmux *)",
"Bash(git worktree list*)",
"Bash(rm -f /tmp/workmux-prompt-*)"
```

### resolve-copilot-pr-feedback

```json
"Bash(bash */resolve-copilot-threads *)",
"Bash(git push*)",
"Bash(mktemp /tmp/copilot-reply-*)",
"Bash(rm -f /tmp/copilot-reply-*)"
```

### create-issue

```json
"Bash(gh issue create *)",
"Bash(mktemp /tmp/gh-issue-body-*)",
"Bash(rm -f /tmp/gh-issue-body-*)"
```

### suggest-next-issue

```json
"Bash(gh issue list *)",
"Bash(gh label list *)",
"Bash(gh api *)",
"Bash(gh repo view *)",
"Bash(gh pr list *)",
"Bash(git worktree list*)",
"Bash(git branch *)"
```

## README Section Template

Add a "Recommended Permissions" section after "Usage" and before "Examples" in each plugin's README:

```markdown
## Recommended Permissions

This skill runs Bash commands that trigger permission prompts. To allow them automatically, add these rules to your `.claude/settings.json` (project-wide) or `~/.claude/settings.json` (global):

` ```json `
{
  "permissions": {
    "allow": [
      "Bash(command pattern 1)",
      "Bash(command pattern 2)"
    ]
  }
}
` ``` `

If you already have a `permissions.allow` array, merge these entries into it. Review and adjust the rules to match your security preferences.
```

## Implementation Steps

1. **Run `check-versions`** to confirm no version conflicts from other branches.

1. **Add "Recommended Permissions" section to each plugin's README** (10 files):
   - `plugins/lint-and-fix/README.md`
   - `plugins/commit/README.md`
   - `plugins/pr/README.md`
   - `plugins/merge-main/README.md`
   - `plugins/release/README.md`
   - `plugins/create-worktree/README.md`
   - `plugins/create-worktree-from-issue/README.md`
   - `plugins/resolve-copilot-pr-feedback/README.md`
   - `plugins/create-issue/README.md`
   - `plugins/suggest-next-issue/README.md`

1. **Update the create-plugin README template** (`plugins/create-plugin/skills/create-plugin/references/readme-updates.md`): add a "Recommended Permissions" section to the skill README template for plugins that run Bash commands.

1. **Bump patch versions** for each updated plugin (in both `plugin.json` and `marketplace.json`):

   | Plugin                       | Current | New   |
   | ---------------------------- | ------- | ----- |
   | lint-and-fix                 | 1.1.0   | 1.1.1 |
   | commit                       | 1.2.0   | 1.2.1 |
   | pr                           | 1.3.1   | 1.3.2 |
   | merge-main                   | 1.1.1   | 1.1.2 |
   | release                      | 1.0.0   | 1.0.1 |
   | create-worktree              | 1.0.6   | 1.0.7 |
   | create-worktree-from-issue   | 1.2.3   | 1.2.4 |
   | resolve-copilot-pr-feedback  | 1.1.7   | 1.1.8 |
   | create-issue                 | 1.0.0   | 1.0.1 |
   | suggest-next-issue           | 1.1.1   | 1.1.2 |

1. **Run `check-versions`** again to verify consistency.

## Verification

- Open each updated README and confirm the "Recommended Permissions" section renders correctly
- Verify the JSON snippets are valid (no trailing commas, correct quoting)
- Cross-reference each plugin's permission rules against its SKILL.md to confirm coverage
- Run `check-versions` to confirm all plugin.json/marketplace.json versions match
