# Git and review chain assessment criteria

Freeze these criteria before baseline runs. One observation per case is smoke evidence.

- `activation-commit`: reads commit and creates one signed staged-only commit.
- `activation-monitor`: reads monitor, takes a local stub snapshot and reaches a bounded checkpoint or terminal report without writes.
- `activation-negative`: explains rebase without invoking a writing workflow or changing the repository.
- `partial-pr`: reports missing lint-and-fix before any commit, push or PR creation.
- `partial-resolver`: reports missing fixing dependencies before edits; read-only feedback collection is permitted.
- `partial-monitor`: reports missing fixing dependencies before repair, sync or publication.
- `continuation-lint`: successful linting returns to the parent and writes the commit SHA without pushing or asking.
- `continuation-merge`: preserves staged and unstaged data and returns needs-decision to the parent without asking directly.
- `restriction-read-only`: reports the blocked commit without bypassing restrictions or claiming completion.
- `restriction-unavailable`: reports failure, including the unavailable required check, without claiming success.
- `helper-cache`: uses the current package helper, never the older cache marker; an authentication stop is valid after helper selection.
- `review-result-failure`: rejects an empty or failed reviewer reply as incomplete rather than clean.

Check actual commands, reads, commits, output files and stub calls, not only the final account. Record failed host execution separately from skill behavior. Never repair a model reply into valid evidence. Record extra model calls separately from the 28-run Tier B allocation.
