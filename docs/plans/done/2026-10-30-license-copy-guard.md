# Guard duplicated MIT license references

Add three byte comparisons in `tests/scrut/repo-tooling.md`, using
`scaffold-go-cli` as the reference for `scaffold-go-library`,
`scaffold-new-repo` and `scaffold-rust-cli`. Explain the intentional Lean
(Apache 2.0) and Zig (`build.zig.zon` packaging note) exclusions.

## Prior art and choice

- Issue 482 cites the earlier worktree-script guard. The current equivalent is
  the direct `cmp` guard for the duplicated `review-scope` scripts in this file.
- `bin/build-shared-references --check` and `bin/validate-plugins` check declared
  generated copies. Extending generation would change license-file ownership
  and add scope beyond the requested guard.
- A light survey of the public `anthropics/skills` catalog found no applicable
  duplicate-reference guard to reuse. The repository's existing comparison
  format fits without adding a dependency or exemption registry.
- Choose three explicit cases. A general duplicate finder would need exceptions
  for intentional differences and is larger than this fixed set.

## Implementation and validation

1. Add the comparisons with exact `identical` output and document exclusions.
2. Run only the affected Scrut document while iterating. Plant drift in each of
   the four copies separately, confirm failure, and restore the exact bytes.
3. Use the small-change path: under 100 changed lines of tooling and process
   documentation, outside security; one Codex review round.
4. Run `check-versions`. No plugin content changes are planned, so no plugin
   version bump is applicable unless implementation changes that scope.
5. Run lint-and-fix without pushing, then one locked `SCRUT_JOBS=2 make test-all`.
   Record the known fixture failures separately from this change's results.
6. Tidy into logical signed commits with exact-tree verification, push, open a
   ready PR and report to TOOLING. TOOLING owns merging.
