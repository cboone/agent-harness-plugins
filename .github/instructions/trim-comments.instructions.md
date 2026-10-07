---
applyTo: "plugins/trim-comments/**,dist/codex/plugins/trim-comments/**"
---

# Trim comments review instructions

For repository-wide conventions, see [the general Copilot instructions](../copilot-instructions.md).

- **Leaving the edits uncommitted is deliberate.** The skill can activate implicitly, so it edits and reports, and the user reviews the diff and commits it, optionally with the `commit` skill. Do not flag the absence of a commit or push step, and do not propose adding one or a flag that enables one.
- **User-given paths are relative to the working directory on purpose.** Like any command-line argument, a path the user passes is resolved from the current directory, and `git ls-files --full-name` turns the matches into root-relative paths for the rest of the workflow. Do not propose treating user arguments as root-relative; a path that matches nothing is reported, not skipped.
- **The `realpath` equality check already rejects any symlinked component.** The skill compares `realpath "./$path"` with the literal string `<resolved root>/$path`, not with a resolved form of it. A symlink in any component, including one pointing at an ancestor such as `alias -> .`, resolves to a different string, so the path is dropped. Do not report that the check misses ancestor or self-referencing links.
