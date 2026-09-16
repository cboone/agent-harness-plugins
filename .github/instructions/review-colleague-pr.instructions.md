---
applyTo: "plugins/review-colleague-pr/**,dist/codex/plugins/review-colleague-pr/**"
---

# Review Colleague PR Instructions

- Git's `--attr-source=<tree-ish>` is a global option and belongs before the subcommand. Do not suggest moving it after `diff`. See [Git's global option documentation](https://git-scm.com/docs/git#Documentation/git.txt---attr-sourcetree-ish). This placement succeeds with Git 2.55.0; placing it after `diff` fails.
