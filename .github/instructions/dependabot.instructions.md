---
applyTo: "plugins/triage-dependabot-prs/**,plugins/review-dependabot-config/**,plugins/monitor-pr/**,plugins/upgrade-everything/**,tests/scrut/dependabot-prs.md,tests/data/dependabot-prs/**"
---

# Dependabot Facts for Review

These were checked against live GitHub data and the GitHub documentation. Do not flag code or instructions that follow them.

- **One Dependabot identity, spelled per API.** The `gh` CLI's JSON output (`gh pr view --json author`, `gh pr list --json author`) and the `author:app/dependabot` search qualifier use `app/dependabot`. REST responses (`user.login` on comments and reviews, `author.login` in the compare API) and `github.actor` in Actions use `dependabot[bot]`. `gh pr list --author app/dependabot` returns every Dependabot PR. Each command matches the form its own API returns, so do not ask for both forms in a comparison that reads from one API.
- **The "disable automated security fix PRs" footer line appears only on security update PRs.** Version update PRs, grouped or single, do not carry it, so it is a valid security marker. A body without the footer (after a rebase, or when truncated) is reported as `kind: unknown`, never as `version`.
- **Dependabot alert `manifest_path` is repository-relative** (`go.mod`, `web/package-lock.json`), with no leading `/`.
- **Default labels.** With `labels` unset, Dependabot applies `dependencies`, and adds an ecosystem label only when more than one package ecosystem is configured.
- **`jq` on empty or whitespace-only input emits nothing and exits 0**, so `dependabot-prs summarize < /dev/null` reaches the "input is empty" check. `tests/scrut/dependabot-prs.md` covers that case.
