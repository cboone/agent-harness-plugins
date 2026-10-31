# Head freeing counts and companion ordering

Fix [issue 457](https://github.com/cboone/agent-harness-plugins/issues/457) without changing other template rows.

## Reproduction

Current main `5205fada80635f7d9dd4a1967c94a256e60a99cb` rejects the original payload because schema version 2 now requires metadata. Adding only `schemaVersion`, `affinityIgnored`, null progress and empty affinity makes it valid: three issues in one lane. Executing the canonical template gives `freedAfter: 1`, renders `then one more`, and leaves companion 4 queued behind PR 90.

## Prior art

[GitHub dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies) expose individual blocking relationships, not branch-unit capacity. [Beads](https://github.com/gastownhall/beads) lists ready tasks only when no open blockers remain. Neither replaces this self-contained template's companion and soft-ordering semantics. Extend the existing freeing calculation: a relationship removed is insufficient evidence that a whole successor branch can start.

## Implementation and validation

- Evaluate every successor issue's soft ordering against the admitted head unit.
- Keep hard blockers scoped to the successor root. Preserve head companion admission and all row states.
- Add execution regression coverage from the schema-adapted payload: external soft ordering, ordering satisfied by the head or its admitted companion, independent companion hard blockers, and blocked head companions.
- Commit checks before plants. Restore root-only ordering and weaken head admission separately; record observed failures and restore the tree.
- Bump publish-report-board patch version and regenerate mirrors with `make build`.
- Use the full local review order unless the final implementation and tests qualify for the brief's small-change path. Record rounds and findings.
- Run touched-file Scrut during iteration. Wait for TOOLING's lock assignment before the single full suite, with `SCRUT_JOBS=2`; record the known fixture failures separately. Complete lint, version checks, exact-tree tidy, push and ready PR. TOOLING merges.
