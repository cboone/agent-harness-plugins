# Documentation instructions

Follow the root writing conventions. [Plugin development](plugin-development.md) owns specialized plugin layouts, catalog procedures and version rules; update it in place.

- Name plans `YYYY-MM-DD-meaningful-description.md` and use `plans/todo/` and `plans/done/`.
- Completed plans are historical records and excluded from Prettier. Do not rewrite them while formatting current documentation.
- [Review case corpus](review-case-corpus.md) owns the frozen corpus conventions: the `CASE.md` and `defects.yaml` schema, the closed sets, and the freezing procedure. Update it in place.
- Save branch reviews in `reviews/` using `review-branch`; address their items with `address-review`.
- Keep root instructions focused on operation, critical constraints and navigation. Every directory-scoped `AGENTS.md` has a sibling `CLAUDE.md` symlink.
