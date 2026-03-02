---
name: use-git
description: >-
  Git and GitHub CLI conventions for Claude Code. Use when:
  (1) running git commands (commit, push, merge, rebase),
  (2) running gh CLI commands (pr create, issue create, pr review),
  (3) passing long content to git or gh (PR bodies, issue bodies, review replies),
  (4) reviewing code that uses git or gh CLI patterns.
  Covers tmpfile patterns, HEREDOC commits, GPG signing, safe push practices,
  and permission-prompt avoidance.
---

# Use Git

Conventions for running git and GitHub CLI (`gh`) commands in Claude Code. These rules keep Bash commands short, avoid unnecessary permission prompts, and prevent destructive operations.

## Core Principles

1. **Tmpfiles for long content**: Write long strings (PR bodies, issue bodies, review replies) to a tmpfile via the Write tool, then pass `--body-file`. Keeps Bash commands short and avoids permission prompts.
1. **HEREDOCs for short content**: Commit messages use `$(cat << 'EOF' ... EOF)`. Single-quoted `'EOF'` prevents variable expansion.
1. **GPG sign every commit**: Always `git commit -S`. The sandbox cannot access GPG keys, so resort immediately to the unsandboxed command.
1. **Never amend**: Always create new commits. Pre-commit hook failures mean the commit did not happen, so `--amend` would modify the wrong commit.
1. **Never use force or override flags**: Never use `git push --force`, `git push -f`, `--no-verify`, or similar override flags without explicit user instruction. If the user explicitly requests a force push, use `--force-with-lease --force-if-includes` instead. Investigate root causes rather than forcing through.
1. **Parallel tool calls over chained commands**: Use separate Bash tool calls for independent commands instead of chaining with `;` or `&&`, which trigger permission prompts.
1. **Exclude secret files from staging**: Never stage `.env`, `credentials.json`, `*.pem`, `*.key`, or similar secret files.

## Quick Decision Table

| Scenario                        | Pattern                  | Reason                                     |
| ------------------------------- | ------------------------ | ------------------------------------------ |
| Commit messages                 | HEREDOC                  | Short, predictable length                  |
| PR bodies (`gh pr create`)      | Tmpfile + `--body-file`  | Can be long; HEREDOC triggers prompts      |
| Issue bodies (`gh issue create`)| Tmpfile + `--body-file`  | Can be long                                |
| Review replies                  | Tmpfile + `--body-file`  | Variable length                            |
| Worktree prompts                | Write tool to `/tmp/`    | Avoids shell escaping                      |
| Tag messages                    | Inline `-m`              | Typically one line                         |

## Workflow

1. **Quick reference:** Check the decision table above
1. **Tmpfile details:** Read `references/tmpfile-pattern.md`
1. **HEREDOC details:** Read `references/heredoc-pattern.md`
1. **Safety rules:** Read `references/safety-rules.md`
1. **Common operations:** Read `references/common-operations.md`

## Reference Navigation

**Quick reviews (default):**

- The decision table above and the core principles cover most situations

**Deep dives by topic:**

- `references/tmpfile-pattern.md` - When and how to use tmpfiles for long content
- `references/heredoc-pattern.md` - When and how to use HEREDOCs for commit messages
- `references/safety-rules.md` - GPG signing, never amend, never force, secret exclusion, parallel calls
- `references/common-operations.md` - Base branch detection, push with upstream fallback, conventional commits, branch naming
