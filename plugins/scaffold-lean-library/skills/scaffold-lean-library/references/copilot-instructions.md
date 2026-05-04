# Copilot Instructions Template

Use this template for `.github/copilot-instructions.md`.

```markdown
# Copilot Instructions

## PR Review

- **Lean entrypoint manifests are explicit**: `LEAN-NAMESPACE.lean` and `LEAN-TEST-NAMESPACE.lean` intentionally list public imports even when they are transitively available. Do not suggest removing manifest imports as redundant.
- **Mathlib cache bootstrap is required**: In a fresh clone or worktree, run `bin/bootstrap-worktree` before any direct `lake build`, `lake test`, or `lake lint`.
- **Lean comments and docstrings are not hardwrapped**: This project lets editors handle visual wrapping. Do not request line breaks solely to fit a column limit.
- **Tests mirror public Lean modules**: Public modules under `LEAN-NAMESPACE/` should have matching compile-time API regression modules under `LEAN-TEST-NAMESPACE/`.
```

## Notes

- Keep this file focused on review instructions that automated reviewers often get wrong.
- Add project-specific conventions as they emerge.
