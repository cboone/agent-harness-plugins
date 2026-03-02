# Plan: Create `use-git` Skill

## Context

When Claude Code runs git/gh CLI commands with long string arguments (commit messages, PR bodies, issue bodies, review replies), it triggers unnecessary permission prompts because the Bash command appears complex. Multiple skills have independently discovered and implemented solutions (tmpfile pattern in `create-issue` and `resolve-copilot-pr-feedback`, HEREDOC pattern in `commit` and `pr`), but the patterns are scattered and inconsistent. For example, the `pr` skill uses HEREDOC for PR bodies, while the `create-issue` skill correctly identified that long content should use tmpfiles with `--body-file` instead.

This skill centralizes git/gh CLI conventions into a single auto-activating style guide, similar to `write-go-code` or `handle-secrets`.

## Files to Create

### 1. `plugins/use-git/.claude-plugin/plugin.json`

Standard plugin metadata. Version `1.0.0`, category `code-quality`, keywords covering git, gh, cli, conventions, permissions.

### 2. `plugins/use-git/skills/use-git/SKILL.md`

Auto-activating style guide. Structure follows `handle-secrets` pattern:

- **Frontmatter**: Triggers on git commands, gh CLI commands, passing long content to either, reviewing git/gh code
- **Core Principles**: Numbered list covering the seven key rules
- **Quick Decision Table**: When to use tmpfile vs HEREDOC vs inline flag
- **Reference Navigation**: Pointers to detailed reference files

Core principles to cover:

1. **Tmpfiles for long content**: Write long strings (PR bodies, issue bodies, review replies) to a tmpfile via the Write tool, then pass `--body-file`. Keeps Bash commands short.
2. **HEREDOCs for short content**: Commit messages use `$(cat << 'EOF' ... EOF)`.
3. **GPG sign every commit**: Always `git commit -S`. Sandbox cannot access GPG keys, so resort immediately to unsandboxed command.
4. **Never amend**: Always create new commits. Pre-commit hook failures mean the commit did not happen, so `--amend` would modify the wrong commit.
5. **Never use `--force`**: Never use `git push --force` or `git push -f`. If the user explicitly requests a force push, use `--force-with-lease --force-if-includes` instead, which protects against overwriting others' work. Never use `--no-verify` or other override flags without explicit user instruction.
6. **Parallel tool calls over chained commands**: Separate Bash tool calls for independent commands instead of `;` or `&&`, which trigger permission prompts.
7. **Exclude secret files from staging**: Never stage `.env`, `credentials.json`, `*.pem`, `*.key`.

Decision table:

| Scenario | Pattern | Reason |
|----------|---------|--------|
| Commit messages | HEREDOC | Short, predictable length |
| PR bodies (`gh pr create`) | Tmpfile + `--body-file` | Can be long; HEREDOC triggers prompts |
| Issue bodies (`gh issue create`) | Tmpfile + `--body-file` | Can be long |
| Review replies | Tmpfile + `--body-file` | Variable length |
| Worktree prompts | Write tool to `/tmp/` | Avoids shell escaping |
| Tag messages | Inline `-m` | Typically one line |

### 3. `plugins/use-git/skills/use-git/references/tmpfile-pattern.md`

Detailed tmpfile pattern guide:

- Why the pattern exists (permission prompts from long Bash arguments)
- Three-step workflow: (1) `mktemp /tmp/purpose-XXXXXX.md`, (2) Write tool to write content, (3) pass `--body-file` to command
- Cleanup: always `rm -f` after command completes, even on failure
- Concrete examples for `gh issue create`, `gh pr create`, review replies, and custom scripts
- Anti-patterns: never `echo "..." | gh`, never inline `--body` with long content, never HEREDOC for long `gh` arguments

### 4. `plugins/use-git/skills/use-git/references/heredoc-pattern.md`

Detailed HEREDOC guide:

- When to use (commit messages, short inline content)
- The exact pattern with GPG signing
- Why single-quoted `'EOF'` (prevents variable expansion)
- When HEREDOC is not appropriate (long content that triggers prompts)

### 5. `plugins/use-git/skills/use-git/references/safety-rules.md`

Detailed safety conventions:

- GPG signing: always `-S` for commits, sandbox limitation
- Never amend: rationale about pre-commit hooks
- Never `--force`: always use `--force-with-lease --force-if-includes` when user explicitly requests force push; suggest `git pull --rebase` as default alternative
- Never use override flags (`--no-verify`, `-f`): investigate root causes instead
- Secret file exclusion: patterns to watch for
- Parallel tool calls: rationale about chained commands and prompts

### 6. `plugins/use-git/skills/use-git/references/common-operations.md`

Reusable git/gh patterns:

- Base branch detection: `gh repo view` primary, `git remote show origin` fallback
- Push with upstream fallback: `git push`, then `git push -u origin HEAD`
- Checking remote tracking status
- Conventional commit types and format
- Branch naming: `TYPE/SLUG` format

### 7. `plugins/use-git/README.md`

Per-plugin README following the standard template. Trigger: `/use-git` (also activates automatically). Links to commit, pr, create-issue skills in See Also.

## Files to Modify

### 8. `.claude-plugin/marketplace.json`

- Add `use-git` entry in alphabetical order (between `suggest-next-issue` and `write-go-code`)
- Bump `metadata.version` from `1.16.0` to `1.17.0` (adding a plugin)

### 9. `README.md`

- Add `Use Git` to the Git subcategory in the ToC (after Review Branch): `∙ [Use Git](#use-git)`
- Add H4 description section under Git (after Review Branch, alphabetically)
- Mark as auto-activating: `(also activates automatically)`

### 10. `CLAUDE.md`

- Add `use-git` directory entry to the Structure tree in alphabetical position

## Existing Patterns to Reuse

- **Skill structure**: Follow `handle-secrets` SKILL.md layout (core principles, decision table, workflow, reference navigation)
- **Reference structure**: Flat `references/` directory (like `handle-secrets`)
- **Plugin registration**: Follow existing `marketplace.json` entry format exactly
- **README ToC**: One entry per line, `∙` prefix for continuation links
- **Tmpfile pattern**: Documented in `plugins/create-issue/skills/create-issue/SKILL.md` (lines 40-78)
- **HEREDOC pattern**: Documented in `plugins/commit/skills/commit/SKILL.md` (lines 136-142)
- **Body-file pattern**: Documented in `plugins/resolve-copilot-pr-feedback/skills/resolve-copilot-pr-feedback/SKILL.md` (lines 188-199)

## Out of Scope

- **Updating existing skills** to reference `use-git` instead of duplicating patterns (separate follow-up)
- **Updating the PR skill** to use tmpfile pattern for PR bodies (separate patch, `pr` v1.3.0 to v1.3.1)
- **Moving rules from CLAUDE.md**: The skill complements CLAUDE.md; both can coexist

## Verification

1. Check that `plugin.json` version matches `marketplace.json` version (`1.0.0`)
2. Check that `marketplace.json` metadata version bumped to `1.17.0`
3. Check that README ToC entry follows one-per-line format
4. Check that CLAUDE.md structure tree is alphabetically correct
5. Run `/check-versions` to verify version consistency
6. Install the plugin and verify `/use-git` loads the skill correctly
7. Verify auto-activation triggers when running git commands
