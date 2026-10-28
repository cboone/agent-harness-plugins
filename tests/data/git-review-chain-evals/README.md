# Git and review chain evaluations

This opt-in local procedure extends the repository's evaluation-data convention. It is not called by `make test-all` and does not evaluate live GitHub workflows.

- `inputs.json` holds frozen requests and skill selections.
- `assessment-criteria.md` holds expectations separately from the requests.
- `run.mjs` prepares one throwaway fixture and captures one model invocation.
- `assessment.md` records actual coverage and limitations.
- `before-evidence.json` preserves redacted baseline excerpts.
- `comparison-evidence.json` preserves all remaining before/after records and host probes.

The recorded Tier B evaluation is complete at its expanded cap of 32 calls. Additional model calls require a new go-ahead. The initial shell/stub defect was corrected with fixture-only zsh startup files and a non-model login/non-login preflight; its four invalid attempts remain in the evidence. The runner refuses to overwrite them; its optional final argument names a replacement attempt.

Before an authorized run, create a new external scratch directory, freeze canonical plugins under its `before-source/plugins/`, and prepare per-command overrides disabling unrelated advertised skill paths, plugins and MCP servers. Verify the rendered skill inventory for the intended case without making a model call. Do not copy credentials or edit user configuration. The existing Codex login supplies authentication. Every model must use only the local fixture's `gh` stub; an executable mismatch stops the case before a call. Synthetic Git origin and signing configuration must remain local.

Run one case with Node, supplying stage (`before` or `after`), the absolute recorded scratch directory, an overrides JSON file holding CLI arguments, and a case ID from `inputs.json`. The driver refuses an existing result directory. Preserve failures rather than overwriting them. Review exit status, final reply, actual commands, stub logs, signed commits and tree state before judging the case. Record retries and nested model invocations separately. Never classify an empty or failed reviewer result as clean.
