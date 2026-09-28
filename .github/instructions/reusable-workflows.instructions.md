---
applyTo: ".github/workflows/**"
---

# Reusable Workflow Calls

For repo-wide conventions, see [copilot-instructions.md](../copilot-instructions.md) and `AGENTS.md` at the repository root.

- **Read the indentation before reporting a key as misplaced.** A job that calls a reusable workflow has exactly three keys here: `name`, `uses` and `with`. Anything indented under `with:` is an input to the called workflow, however much its name resembles a job-level key. `timeout-minutes` under `with:` is the documented way to override `run-scrut-tests.yml`'s ceiling, not a job-level key that silently does nothing.
- **A key GitHub rejects on a `uses:` job cannot be in a run that succeeded.** Before reporting one, check whether the workflow ran. An unsupported key on a `uses:` job fails the run outright, so a green run is evidence against that reading.
- **`cboone/gh-actions` reusable workflows are readable.** Check the `workflow_call` inputs there before inferring a contract from the caller alone.
- Remote `uses:` references are pinned to full commit SHAs with a trailing version comment, including workflows in this owner's own repositories. That is deliberate; do not suggest a tag instead.
