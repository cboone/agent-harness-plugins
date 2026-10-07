---
applyTo: ".github/workflows/**"
---

# Git Commands in Workflows

For repo-wide conventions, see [copilot-instructions.md](../copilot-instructions.md) and `AGENTS.md` at the repository root.

- **`git worktree add --orphan -b <branch> <path>` is correct.** Since Git 2.42, `--orphan` is a flag that makes the new branch named by `-b` or `-B` an unborn branch; it takes no argument of its own. `git worktree add -h` prints the synopsis `[--orphan] [(-b | -B) <new-branch>] <path> [<commit-ish>]`. Do not suggest dropping `-b` or moving the branch name after `--orphan`.
- **A push from the main checkout can publish a branch committed in a linked worktree.** Worktrees share the repository's refs, so `git push origin refs/heads/<branch>:refs/heads/<branch>` from the checkout that holds the persisted credentials is deliberate, not a mismatch.
