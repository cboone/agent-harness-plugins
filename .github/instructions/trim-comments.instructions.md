---
applyTo: "plugins/trim-comments/**,dist/codex/plugins/trim-comments/**"
---

# Trim comments review instructions

For repository-wide conventions, see [the general Copilot instructions](../copilot-instructions.md).

- **Committing by default, never pushing, is deliberate.** The skill can activate implicitly, so it stops at a local commit the user can inspect and undo; `--no-commit` leaves the edits uncommitted. It commits only files that were clean before the run, directly with `git commit -- <paths>` rather than through the `commit` skill, whose hook, plan, and issue-reference rules would override these. Do not propose a push step, staging whole dirty files, or delegating the commit.
- **Committing from the working tree, then checking hashes, is deliberate.** Step 6 confirms each file holds only comment edits, records its hash, commits with `git commit -- <paths>`, and reports any committed content whose hash differs. A change made in the moment between the check and the commit is reported in a local, unpushed commit the user can inspect. Committing from a separate index would leave the user's index out of step with `HEAD` for those paths, so do not propose it.
- **`git hash-object -- "./$path"` already applies clean filters.** For a file argument, Git hashes the content after the path's clean filters and line-ending conversion, so it matches the blob `git commit` stores; only `--no-filters` hashes raw bytes. Do not propose adding `--path`.
- **User-given paths are relative to the working directory on purpose.** Like any command-line argument, a path the user passes is resolved from the current directory, and `git ls-files --full-name` turns the matches into root-relative paths for the rest of the workflow. Do not propose treating user arguments as root-relative; a path that matches nothing is reported, not skipped.
- **The `realpath` equality check already rejects any symlinked component.** The skill compares `realpath "./$path"` with the literal string `<resolved root>/$path`, not with a resolved form of it. A symlink in any component, including one pointing at an ancestor such as `alias -> .`, resolves to a different string, so the path is dropped. Do not report that the check misses ancestor or self-referencing links.
